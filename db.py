import sqlite3

def connect_db():
    conn = sqlite3.connect('rental_system.db')
    return conn

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')
    
    # Create Vehicles table
    cursor.execute('''CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        name TEXT NOT NULL,
        deposit REAL NOT NULL,
        available INTEGER NOT NULL,
        city TEXT NOT NULL,
        image TEXT NOT NULL
    )''')

    # Create Bookings table
    cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        booking_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        city TEXT NOT NULL,
        FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
    )''')


    

    conn.commit()
    conn.close()

def add_vehicle(type, name, deposit, available, city, image):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('''INSERT INTO vehicles (type, name, deposit, available, city, image)
                      VALUES (?, ?, ?, ?, ?, ?)''', (type, name, deposit, available, city, image))
    
    conn.commit()
    conn.close()

def add_booking(vehicle_id, amount, city):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('''INSERT INTO bookings (vehicle_id, amount, city)
                      VALUES (?, ?, ?)''', (vehicle_id, amount, city))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
    print("Database setup complete.")
