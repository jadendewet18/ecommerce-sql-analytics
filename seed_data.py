import sqlite3
import random
from datetime import datetime, timedelta

# Connect to SQLite database (this automatically creates the file 'ecommerce_analytics.db')
conn = sqlite3.connect('ecommerce_analytics.db')
cursor = conn.cursor()

# 1. Create Tables inside Python so the script is self-contained
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    signup_date TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    price REAL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    status TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price REAL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
)
''')

print("Tables created successfully.")

# 2. Generate Sample Customers (100 customers)
first_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Ethan', 'Fiona', 'George', 'Hannah', 'Ian', 'Julia']
last_names = ['Smith', 'Johnson', 'Brown', 'Taylor', 'Miller', 'Davis', 'Wilson', 'Moore', 'Anderson', 'Thomas']

for i in range(1, 101):
    fname = random.choice(first_names)
    lname = random.choice(last_names)
    email = f"{fname.lower()}.{lname.lower()}{i}@example.com"
    signup = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 300))
    cursor.execute(
        "INSERT OR IGNORE INTO customers VALUES (?, ?, ?, ?, ?)",
        (i, fname, lname, email, signup.strftime('%Y-%m-%d'))
    )

# 3. Generate Sample Products (20 products)
categories = ['Electronics', 'Apparel', 'Home & Kitchen', 'Books']
for i in range(1, 21):
    cursor.execute(
        "INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?)",
        (i, f"Product {i}", random.choice(categories), round(random.uniform(10.0, 250.0), 2))
    )

# 4. Generate Sample Orders & Order Items
order_id_counter = 1
order_item_counter = 1

for customer_id in range(1, 101):
    num_orders = random.randint(1, 6)
    for _ in range(num_orders):
        order_date = datetime(2025, 6, 1) + timedelta(days=random.randint(0, 365))
        cursor.execute(
            "INSERT OR IGNORE INTO orders VALUES (?, ?, ?, ?)",
            (order_id_counter, customer_id, order_date.strftime('%Y-%m-%d'), 'Completed')
        )
        
        # 1 to 4 items per order
        for _ in range(random.randint(1, 4)):
            prod_id = random.randint(1, 20)
            cursor.execute("SELECT price FROM products WHERE product_id = ?", (prod_id,))
            price = cursor.fetchone()[0]
            cursor.execute(
                "INSERT OR IGNORE INTO order_items VALUES (?, ?, ?, ?, ?)",
                (order_item_counter, order_id_counter, prod_id, random.randint(1, 3), price)
            )
            order_item_counter += 1
            
        order_id_counter += 1

# Save (commit) changes and close the connection
conn.commit()
conn.close()
print("Database seeded successfully with realistic e-commerce records!")