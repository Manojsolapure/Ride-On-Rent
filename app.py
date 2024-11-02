import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from db import connect_db
from werkzeug.security import generate_password_hash, check_password_hash
from contextlib import closing

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Function to add a vehicle to the database
def add_vehicle(vehicle_type, vehicle_name, deposit, available, city):
    with closing(connect_db()) as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO vehicles (type, name, deposit, available, city) VALUES (?, ?, ?, ?, ?)''', 
                       (vehicle_type, vehicle_name, deposit, available, city))
        conn.commit()

# Function to add a booking to the database
def add_booking(vehicle_id, amount, city):
    with closing(connect_db()) as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO bookings (vehicle_id, amount, city) VALUES (?, ?, ?)''', 
                       (vehicle_id, amount, city))
        conn.commit()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        with closing(connect_db()) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                               (username, email, password))
                conn.commit()
                flash('Sign up successful! Please log in.', 'success')
            except Exception as e:
                print(f"Error: {e}")
                flash('An error occurred. Please try again.', 'error')

        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        with closing(connect_db()) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        city = request.form['city']
        from_date = request.form['from_date']
        to_date = request.form['to_date']
        
        session['city'] = city
        session['from_date'] = from_date
        session['to_date'] = to_date
        
        return redirect(url_for('available_vehicles'))

    return render_template('dashboard.html')

@app.route('/available_vehicles', methods=['GET'])  # Only GET method allowed
def available_vehicles():
    city = session.get('city')
    
    if not city:
        flash('Please select a city first.', 'error')
        return redirect(url_for('dashboard'))

    with closing(connect_db()) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vehicles WHERE city = ? AND available = 1', (city,))
        vehicles = cursor.fetchall()

    return render_template('available_vehicles.html', vehicles=vehicles)

@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    vehicle_id = request.form.get('vehicle_id')
    # Logic to store the booking in the database goes here
    return "Booking confirmed!", 200

def connect_db():
    conn = sqlite3.connect('rental_system.db')
    return conn

def get_vehicle(vehicle_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM vehicles WHERE id = ?', (vehicle_id,))
    vehicle = cursor.fetchone()  # Fetch one vehicle based on the ID
    conn.close()
    return vehicle

@app.route('/booking/<int:vehicle_id>')
def booking(vehicle_id):
    vehicle = get_vehicle(vehicle_id)
    if vehicle is None:
        return "Vehicle not found", 404
    return render_template('booking.html', vehicle=vehicle)

# Add initial vehicles if not already present
def initialize_vehicles():
    try:
        add_vehicle('Bike', 'Bike 1', 100.0, 1, 'City A')
        add_vehicle('Bike', 'Bike 2', 150.0, 1, 'City B')
        add_vehicle('Bike', 'Bike 3', 120.0, 1, 'City C')
    except Exception as e:
        print(f"Error adding vehicles: {e}")

@app.route('/pay', methods=['POST'])
def pay():
    vehicle_id = request.json.get('vehicle_id')
    amount = request.json.get('amount')
    city = request.json.get('city')

    # Save booking to database
    add_booking(vehicle_id, amount, city)

    return jsonify({"message": "Booking successful", "vehicle_id": vehicle_id, "amount": amount})

if __name__ == '__main__':
    with closing(connect_db()) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM vehicles')
        vehicle_count = cursor.fetchone()[0]

    if vehicle_count == 0:  # Only add vehicles if the table is empty
        initialize_vehicles()

    app.run(debug=True)
