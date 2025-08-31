import sqlite3

conn = sqlite3.connect("rental.db")
cur = conn.cursor()

# Customers Table
cur.execute("""
CREATE TABLE IF NOT EXISTS Customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    email TEXT,
    aadhaar_no TEXT UNIQUE,
    dl_no TEXT UNIQUE NOT NULL,
    address TEXT
);
""")

# Vehicles Table
cur.execute("""
CREATE TABLE IF NOT EXISTS Vehicles (
    vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_type TEXT CHECK(vehicle_type IN ('Bike', 'Car')),
    brand TEXT,
    model TEXT,
    reg_no TEXT UNIQUE NOT NULL,
    rent_per_day REAL NOT NULL,
    available BOOLEAN DEFAULT 1
);
""")

# Rentals Table
cur.execute("""
CREATE TABLE IF NOT EXISTS Rentals (
    rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    vehicle_id INTEGER,
    start_date DATE,
    end_date DATE,
    actual_return DATE,
    total_amount REAL,
    fine_amount REAL DEFAULT 0,
    payment_status TEXT CHECK(payment_status IN ('Pending','Paid')) DEFAULT 'Pending',
    FOREIGN KEY(customer_id) REFERENCES Customers(customer_id),
    FOREIGN KEY(vehicle_id) REFERENCES Vehicles(vehicle_id)
);
""")

# Payments Table
cur.execute("""
CREATE TABLE IF NOT EXISTS Payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rental_id INTEGER,
    amount REAL,
    payment_date DATE DEFAULT CURRENT_DATE,
    method TEXT CHECK(method IN ('Cash','UPI','PayTM','Card')),
    FOREIGN KEY(rental_id) REFERENCES Rentals(rental_id)
);
""")

# Insert sample vehicles
cur.executemany("""
INSERT OR IGNORE INTO Vehicles (vehicle_type, brand, model, reg_no, rent_per_day)
VALUES (?, ?, ?, ?, ?)
""", [
    ("Bike", "Hero", "Splendor Plus", "OD-33-AB-1234", 400),
    ("Bike", "Honda", "Activa 6G", "OD-33-AC-5678", 500),
    ("Car", "Maruti Suzuki", "Swift", "OD-33-CA-1111", 1500),
    ("Car", "Hyundai", "i20", "OD-33-CB-2222", 2000)
])

conn.commit()
conn.close()
print("Database initialized!")
