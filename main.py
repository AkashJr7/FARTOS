
from flask_mail import Mail, Message
from flask import Flask, render_template, Response, redirect, request, session
from camera import VideoCamera
import sqlite3
import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.secret_key = "your_secret_key"
CART = []

# OpenRouter API Configuration
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = "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"  # Replace with your OpenRouter API key

# Chatbot route
@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json.get('message')
    print(f"User message: {user_message}")  # Debugging: Print user's input

    # Prepare the payload for the OpenRouter API
    payload = {
        "model": "deepseek/deepseek-r1:free",  # Use the DeepSeek-R1 model
        "messages": [
            {"role": "system", "content": "You are a fashion assistant. Help users with fashion-related queries."},
            {"role": "user", "content": user_message}
        ]
    }

    # Set the headers for the API request
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Debugging: Print the payload and headers
    print("Payload:", payload)
    print("Headers:", headers)

    try:
        # Send the request to the OpenRouter API
        response = requests.post(OPENROUTER_API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

        # Extract the chatbot's response
        chatbot_response = response.json()['choices'][0]['message']['content']
        print(f"Chatbot response: {chatbot_response}")  # Debugging: Print chatbot's response

        return jsonify({"response": chatbot_response})
    except requests.exceptions.RequestException as e:
        print(f"Error calling OpenRouter API: {e}")  # Debugging: Print API error
        print(f"Response content: {e.response.text}")  # Debugging: Print the response content
        return jsonify({"response": "Sorry, I couldn't process your request. Please try again later."}), 500
    

# Define available goggles
goggles_men = [
    {"id": 1, "name": "Aviator", "image": "static/goggles/men_aviator.png"},
    {"id": 2, "name": "Sporty", "image": "static/goggles/men_sporty.png"},
]

goggles_women = [
    {"id": 3, "name": "Cat Eye", "image": "static/goggles/women_cateye.png"},
    {"id": 4, "name": "Round", "image": "static/goggles/women_round.png"},
]


@app.route('/goggles/men')
def goggles_men_page():
    return render_template("goggles.html", goggles=goggles_men, category="Men")

@app.route('/goggles/women')
def goggles_women_page():
    return render_template("goggles.html", goggles=goggles_women, category="Women")

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_id = request.form.get("item_id")
    category = request.form.get("category")
    
    item = next((g for g in (goggles_men + goggles_women) if str(g["id"]) == item_id), None)
    if item:
        CART.append(item)
    
    return redirect(f'/goggles/{category.lower()}')



# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'akashjoshi9278@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'akshaycr72325'         # Replace with your password
mail = Mail(app)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()

        if user:
            # Generate reset link
            reset_link = f"http://127.0.0.1:5000/reset_password/{user[0]}"
            msg = Message('Password Reset Request',
                          sender='akashjoshi9278@gmail.com',
                          recipients=[email])
            msg.body = f"Click the link to reset your password: {reset_link}"
            mail.send(msg)
            return "Reset password link sent to your email."
        else:
            return "No account found with this email."

    return '''
     <form action="/forgot_password" method="POST">
         <label for="email">Enter your email:</label>
         <input type="email" id="email" name="email" required>
         <button type="submit">Send Reset Link</button> 
     </form>
    '''
@app.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
def reset_password(user_id):
    if request.method == 'POST':
        new_password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, user_id))
        conn.commit()
        conn.close()
        return redirect('/login')

    return '''
    <form action="/reset_password/{}" method="POST">
        <label for="password">Enter new password:</label>
         <input type="password" id="password" name="password" required>
        <button type="submit">Reset Password</button>
    </form>
    '''.format(user_id)


# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_or_phone TEXT UNIQUE,
        password TEXT,
         gender TEXT,
        height REAL,
         weight REAL
    )''')
    conn.commit()
    conn.close()

init_db()

PRODUCTS = {
    'modal-1': {'name': 'White T-Shirt for Man', 'price': 235.64, 'category': 'men'},
    'modal-2': {'name': 'Pink T-shirt for Woman', 'price': 125.31, 'category': 'women'},
    'modal-3': {'name': 'Red T-Shirt for Man', 'price': 125.50, 'category': 'men'},
    'modal-4': {'name': 'Purple T-shirt for Woman', 'price': 175.00, 'category': 'women'},
    'modal-5': {'name': 'Orange T-shirt for Men', 'price': 134.75, 'category': 'men'},
    'modal-6': {'name': 'Golden One Piece', 'price': 2193.20, 'category': 'women'},
    'modal-7': {'name': 'Light Pink Sport T-shirt for Woman', 'price': 252.66, 'category': 'women'},
    'modal-8': {'name': 'Grey T-shirt', 'price': 418.96, 'category': 'women'},
    'modal-9': {'name': 'Pink T-shirt for Woman', 'price': 375.00, 'category': 'women'},
    'modal-10': {'name': 'Red One Piece', 'price': 3525.85, 'category': 'women'},
    'modal-11': {'name': 'One Piece', 'price': 4563.16, 'category': 'women'},
    'modal-12': {'name': 'Red T-Shirt for Woman', 'price': 263.15, 'category': 'women'}
}

# Consolidated cart routes
@app.route('/api/add_to_cart', methods=['POST'])
def api_add_to_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    product_id = request.form.get('product_id')
    size = request.form.get('size')
    
    if not product_id or not size:
        return jsonify({'success': False, 'message': 'Product ID and size are required'})
    
    # Get product details
    product = PRODUCTS.get(product_id)
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'})
    
    # Add to cart
    cart_item = {
        'product_id': product_id,
        'name': product['name'],
        'image': f"static/images/t-shirts/{product_id}.png",
        'price': product['price'],
        'size': size,
        'quantity': 1
    }
    
    # Check if item already exists in cart
    existing_item = next((item for item in CART['items'] if 
                         item['product_id'] == product_id and item['size'] == size), None)
    
    if existing_item:
        existing_item['quantity'] += 1
    else:
        CART['items'].append(cart_item)
    
    # Update total
    CART['total'] = sum(item['price'] * item['quantity'] for item in CART['items'])
    
    return jsonify({
        'success': True,
        'message': 'Item added to cart',
        'cart_count': len(CART['items']),
        'cart_total': CART['total']
    })

@app.route('/api/update_cart', methods=['POST'])
def api_update_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    product_id = request.form.get('product_id')
    size = request.form.get('size')
    action = request.form.get('action')  # 'increase' or 'decrease'
    
    if not product_id or not size or not action:
        return jsonify({'success': False, 'message': 'Invalid request'})
    
    # Find the item in cart
    item = next((item for item in CART['items'] if 
                item['product_id'] == product_id and item['size'] == size), None)
    
    if not item:
        return jsonify({'success': False, 'message': 'Item not found in cart'})
    
    if action == 'increase':
        item['quantity'] += 1
    elif action == 'decrease':
        if item['quantity'] > 1:
            item['quantity'] -= 1
        else:
            CART['items'].remove(item)
    
    # Update total
    CART['total'] = sum(item['price'] * item['quantity'] for item in CART['items'])
    
    return jsonify({
        'success': True,
        'cart_count': len(CART['items']),
        'cart_total': CART['total']
    })

@app.route('/api/remove_from_cart', methods=['POST'])
def api_remove_from_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    product_id = request.form.get('product_id')
    size = request.form.get('size')
    
    if not product_id or not size:
        return jsonify({'success': False, 'message': 'Invalid request'})
    
    # Remove item from cart
    CART['items'] = [item for item in CART['items'] 
                     if not (item['product_id'] == product_id and item['size'] == size)]
    
    # Update total
    CART['total'] = sum(item['price'] * item['quantity'] for item in CART['items'])
    
    return jsonify({
        'success': True,
        'cart_count': len(CART['items']),
        'cart_total': CART['total']
    })

@app.route('/checkOut')
def checkOut():
    if 'user_id' not in session:
        return redirect('/login')
    
    return render_template('checkout.html', 
                         cart_items=CART['items'], 
                         cart_total=CART['total'])


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email_or_phone = request.form['email_or_phone']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (email_or_phone, password) VALUES (?, ?)',
                      (email_or_phone, password))
            conn.commit()
            session['user_id'] = c.lastrowid  # Automatically log in the user
            conn.close()
            return redirect('/complete_profile')
        except sqlite3.IntegrityError:
            conn.close()
            return "User already exists."
    return render_template('signup.html')

@app.route('/complete_profile', methods=['GET', 'POST'])
def complete_profile():
    if 'user_id' not in session:
        return redirect('/signup')
    
    if request.method == 'POST':
        gender = request.form['gender']
        height = request.form['height']
        weight = request.form['weight']
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('UPDATE users SET gender = ?, height = ?, weight = ? WHERE id = ?',
                  (gender, height, weight, session['user_id']))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('complete_profile.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_phone = request.form['email_or_phone']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE (email_or_phone=? OR email_or_phone=?) AND password = ?',
                  (email_or_phone, email_or_phone, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect('/')
        else:
            return "Invalid credentials."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')
'''
@app.route('/')
def indexx():
    if 'user_id' not in session:
        return redirect('/signup')
    return render_template('index.html')
'''
@app.route('/')
def home():
    return render_template('index.html')  # Make sure this exists in templates/
	
# Global variable to store selected item
CART = {
    'items': [],  # List of cart items
    'total': 0    # Total price
}
@app.route("/cart/<file_path>", methods=['POST', 'GET'])
def cart(file_path):
    global CART
    file_path = file_path.replace(',', '/')
    print("ADDED", file_path)
    CART.append(file_path)
    return redirect('/checkOut')  # Redirect to the checkout page


'''
@app.route('/checkOut')
def checkOut():
    cart_items = request.args.get('cart_items', '')  # Get the cart_items from the query parameter
    cart_items = cart_items.split(',') if cart_items else []  # Convert the string back to a list

    # Prepare cart items for the template
    cart_items_list = []
    for item in cart_items:
        # Extract item details (e.g., name, image, price) from the file path
        item_name = item.split('/')[-1].replace('.png', '')  # Example: Extract name from file path
        item_image = item  # Use the full file path as the image source
        item_price = "Rs 200.00"  # Example: Set a default price (you can fetch this from a database)

        cart_items_list.append({
            "image": item_image,
            "name": item_name,
            "price": item_price
        })

    print("cart_items_list:", cart_items_list)  # Debugging: Print the cart_items list
    return render_template('checkout.html', cart_items=cart_items_list)
'''
@app.route('/tryon/<file_path>',methods = ['POST', 'GET'])
def tryon(file_path):
	file_path = file_path.replace(',','/')
	os.system('python tryOn.py ' + file_path)
	return redirect('http://127.0.0.1:5000/',code=302, Response=None)
'''
@app.route('/tryall',methods = ['POST', 'GET'])
def tryall():
        CART = request.form['mydata'].replace(',', '/')
        os.system('python test.py ' + CART)
        render_template('checkout.html', message='')
        return render_template('checkout.html', message='')
'''

@app.route('/tryall', methods=['POST', 'GET'])
def tryall():
    if request.method == 'POST':
        CART = request.form['mydata'].replace(',', '/')
        os.system('python test.py ' + CART)
        return redirect('/checkOut')  # Redirect to checkout page after try-on
    return render_template('checkout.html', message='')



@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/product')
def product():
    return render_template('product.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/features')
def features():
    return render_template('features.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
'''
@app.route("/cart/<file_path>",methods = ['POST', 'GET'])
def cart(file_path):
    global CART
    file_path = file_path.replace(',','/')
    print("ADDED", file_path)
    CART.append(file_path)
    return render_template("checkout.html")
'''
@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
    
