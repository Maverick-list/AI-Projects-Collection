import os
import sqlite3
import datetime
from flask import Flask, request, jsonify, session, send_file
from flask_session import Session
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

DB_PATH = 'cashier.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER NOT NULL
    )
    ''')
    
    # Transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id TEXT UNIQUE NOT NULL,
        total_amount REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Transaction Items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transaction_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id TEXT NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (transaction_id) REFERENCES transactions (transaction_id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')
    
    # Expenses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Default user if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed_pw = generate_password_hash('admin123')
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', hashed_pw))
    
    conn.commit()
    conn.close()

# API Endpoints

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'status': 'success', 'message': 'Logged in successfully'})
    
    return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'status': 'success', 'message': 'Logged out successfully'})

@app.route('/api/auth/me', methods=['GET'])
def get_me():
    if 'user_id' in session:
        return jsonify({'status': 'success', 'username': session['username']})
    return jsonify({'status': 'error', 'message': 'Not authenticated'}), 401

# Products CRUD
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return jsonify([dict(row) for row in products])

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    conn = get_db_connection()
    conn.execute('INSERT INTO products (name, price, stock) VALUES (?, ?, ?)',
                 (data['name'], data['price'], data['stock']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.json
    conn = get_db_connection()
    conn.execute('UPDATE products SET name = ?, price = ?, stock = ? WHERE id = ?',
                 (data['name'], data['price'], data['stock'], id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

# Transactions
@app.route('/api/transactions', methods=['POST'])
def process_transaction():
    data = request.json # {items: [{id, quantity, price, name}], total}
    items = data.get('items')
    total = data.get('total')
    
    if not items:
        return jsonify({'status': 'error', 'message': 'No items in transaction'}), 400
    
    transaction_id = f"TRX-{int(datetime.datetime.now().timestamp())}"
    
    conn = get_db_connection()
    try:
        # Create transaction record
        conn.execute('INSERT INTO transactions (transaction_id, total_amount) VALUES (?, ?)',
                     (transaction_id, total))
        
        for item in items:
            # Add transaction item
            conn.execute('''
            INSERT INTO transaction_items (transaction_id, product_id, product_name, quantity, price)
            VALUES (?, ?, ?, ?, ?)
            ''', (transaction_id, item['id'], item['name'], item['quantity'], item['price']))
            
            # Update stock
            conn.execute('UPDATE products SET stock = stock - ? WHERE id = ?',
                         (item['quantity'], item['id']))
        
        conn.commit()
        return jsonify({'status': 'success', 'transaction_id': transaction_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

# Reports
@app.route('/api/reports/summary', methods=['GET'])
def get_summary():
    conn = get_db_connection()
    
    # Daily income
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    daily_income = conn.execute('SELECT SUM(total_amount) FROM transactions WHERE date(timestamp) = ?', (today,)).fetchone()[0] or 0
    
    # Total stock
    total_stock = conn.execute('SELECT SUM(stock) FROM products').fetchone()[0] or 0
    
    # Recent transactions
    recent_tx = conn.execute('SELECT * FROM transactions ORDER BY timestamp DESC LIMIT 10').fetchall()
    
    # Daily charts (last 7 days)
    chart_data = []
    for i in range(6, -1, -1):
        day = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        income = conn.execute('SELECT SUM(total_amount) FROM transactions WHERE date(timestamp) = ?', (day,)).fetchone()[0] or 0
        chart_data.append({'date': day, 'income': income})
        
    conn.close()
    return jsonify({
        'daily_income': daily_income,
        'total_stock': total_stock,
        'recent_transactions': [dict(row) for row in recent_tx],
        'chart_data': chart_data
    })

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    conn = get_db_connection()
    df = pd.read_sql_query('SELECT * FROM transactions', conn)
    conn.close()
    
    csv_path = 'transactions_export.csv'
    df.to_csv(csv_path, index=False)
    return send_file(csv_path, as_attachment=True)

# Dashboard & Frontend
@app.route('/')
def index():
    return send_file('templates/index.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
