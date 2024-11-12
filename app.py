from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from datetime import datetime
import mysql.connector.pooling

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flash messages

# Database Configuration: Configure MySQL RDS with connection pooling for efficient database access
db_config = {
    'host': 'database-1.c7mkmugqq0z1.eu-north-1.rds.amazonaws.com',  # Your RDS endpoint
    'user': 'admin',  # Your DB username
    'password': 'Sriramecommerce1126',  # Your DB password
    'database': 'fresh'  # Your DB name
}

# Connection Pool: Use MySQL connection pooling to handle multiple database connections
cnxpool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,  # Number of connections in the pool
    **db_config
)

# Function to establish a database connection
def get_db_connection():
    try:
        return cnxpool.get_connection()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Home Route: Renders the home page template
@app.route('/')
def home():
    return render_template('home.html')

# Register Route (GET/POST): Handles user registration, inserts user data into the database
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        password = request.form.get('password')
        default_address = request.form.get('default_address')

        # Check if default address is provided
        if not default_address:
            flash('Default address is required!')
            return redirect(url_for('register'))

        # Insert user data into the database
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    'INSERT INTO users (name, mobile, email, password, address) VALUES (%s, %s, %s, %s, %s)',
                    (name, mobile, email, password, default_address)
                )
                conn.commit()
                flash('Thank you for registering!')
                return redirect(url_for('login'))
            except mysql.connector.Error as err:
                print(f"Database Error: {err}")
                flash("Registration failed due to a database error.")
            finally:
                cursor.close()
                conn.close()
        else:
            flash("Unable to connect to the database.")
    return render_template('register.html')

# Login Route (GET/POST): Authenticates user with email and password
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form['email']
        password = request.form['password']

        # Check user credentials
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                flash('Login successful!')
                return redirect(url_for('shop'))
            else:
                flash('Invalid email or password!')
        else:
            flash("Unable to connect to the database.")
    return render_template('login.html')

# Shop Route: Renders the shop page
@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')
# Add to Cart (POST): Adds selected items to the user's session-based shopping cart
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    # Get item data from the request
    item_data = request.get_json()
    item_name = item_data['name']
    item_price = item_data['price']
    item_quantity = item_data['quantity']
    
    # Retrieve the cart from the session, if it exists
    cart_items = session.get('cart_items', [])
    
    # Check if the item is already in the cart
    item_found = False
    for item in cart_items:
        if item['name'] == item_name:
            item_found = True
            item['quantity'] += item_quantity  # Update the quantity
            break

    # If the item was not found, add it to the cart
    if not item_found:
        cart_items.append({
            'name': item_name,
            'price': item_price,
            'quantity': item_quantity
        })
    
    # Update the cart in the session
    session['cart_items'] = cart_items
    
    # Return a success response
    return jsonify(success=True)

# Items Route (GET/POST): Displays available items and allows adding them to the shopping cart
@app.route('/items', methods=['GET', 'POST'])
def items():
    if request.method == 'POST':
        # Handle adding items to the cart in session
        item_name = request.form.get('name')
        item_price = float(request.form.get('price'))
        item_quantity = int(request.form.get('quantity'))

        # Retrieve current cart items from session
        cart_items = session.get('cart_items', [])

        # Check if item already exists in the cart
        item_found = False
        for item in cart_items:
            if item['name'] == item_name:
                item['quantity'] += item_quantity  # Update quantity if item is already in the cart
                item_found = True
                break

        # If the item does not exist in the cart, add it
        if not item_found:
            cart_items.append({
                'name': item_name,
                'price': item_price,
                'quantity': item_quantity
            })

        # Save the updated cart in session
        session['cart_items'] = cart_items

        # Flash success message and redirect back to items page
        flash(f'{item_name} added to your cart!')
        return redirect(url_for('items'))

    # Fetch items from the database for display
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT item_id, item_name, price FROM items')
        items = cursor.fetchall()
        cursor.close()
        conn.close()
    else:
        items = []
        flash("Unable to retrieve items from the database.")

    # Retrieve cart items from session
    cart_items = session.get('cart_items', [])

    # Render the template with items and cart items
    return render_template('items.html', items=items, cart_items=cart_items)

if __name__ == "__main__":
    app.run(debug=True)
