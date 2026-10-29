import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_flow():
    session = requests.Session()
    
    # 1. Login
    print("Testing Login...")
    res = session.post(f"{BASE_URL}/api/auth/login", json={"username": "admin", "password": "admin123"})
    print(res.json())
    assert res.status_code == 200
    
    # 2. Add Product
    print("\nAdding Product...")
    res = session.post(f"{BASE_URL}/api/products", json={"name": "Test Item", "price": 15000, "stock": 100})
    print(res.json())
    assert res.status_code == 200
    
    # 3. Get Products
    print("\nGetting Products...")
    res = session.get(f"{BASE_URL}/api/products")
    products = res.json()
    print(f"Products found: {len(products)}")
    test_item = next(p for p in products if p['name'] == "Test Item")
    
    # 4. Process Transaction
    print("\nProcessing Transaction...")
    txn_data = {
        "items": [{"id": test_item['id'], "name": test_item['name'], "quantity": 2, "price": 15000}],
        "total": 30000
    }
    res = session.post(f"{BASE_URL}/api/transactions", json=txn_data)
    print(res.json())
    assert res.status_code == 200
    
    # 5. Check Stock Reduction
    print("\nChecking Stock...")
    res = session.get(f"{BASE_URL}/api/products")
    products = res.json()
    test_item_after = next(p for p in products if p['id'] == test_item['id'])
    print(f"Stock before: 100, Stock after: {test_item_after['stock']}")
    assert test_item_after['stock'] == 98
    
    # 6. Check Reports Summary
    print("\nChecking Reports...")
    res = session.get(f"{BASE_URL}/api/reports/summary")
    summary = res.json()
    print(f"Daily Income: {summary['daily_income']}")
    assert summary['daily_income'] == 30000
    
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    test_flow()
