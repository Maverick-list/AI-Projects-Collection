# Simple Cashier App

A modern, responsive full-stack POS application built with Flask, SQLite, and Tailwind CSS.

## Features
- **Dashboard**: Real-time sales summary and trend chart.
- **Inventory**: CRUD operations for products with searchable table.
- **Point of Sale**: Search products, manage cart, and process transactions.
- **Reports**: Transaction history and CSV export.
- **Authentication**: Session-based login.

## Setup & Run

1. **Install Python 3.13+** (if not already installed).
2. **Setup Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Run Application**:
   ```bash
   python app.py
   ```
4. **Access**:
   Open `http://127.0.0.1:5000` in your browser.
   - **Username**: `admin`
   - **Password**: `admin123`

## Directory Structure
- `app.py`: Backend logic and API.
- `requirements.txt`: Dependencies.
- `templates/index.html`: Main frontend file.
- `cashier.db`: SQLite database (auto-generated).
