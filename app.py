# app.py (Final working version with Cashfree Integration)

from flask import Flask, render_template, request, redirect, url_for, session
import requests
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import uuid
from cashfree_pg.api_client import Cashfree

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this in production

# Replace these with your actual Cashfree Sandbox credentials
import os

CASHFREE_APP_ID = os.environ.get('CASHFREE_APP_ID', 'your_sandbox_app_id')
CASHFREE_SECRET_KEY = os.environ.get('CASHFREE_SECRET_KEY', 'your_sandbox_secret_key')
CASHFREE_BASE_URL = 'https://sandbox.cashfree.com/pg/orders'

# Sample product catalog
PRODUCTS = [
    {"id": 1, "name": "Milk", "price": 30, "image": "milk.jpg"},
    {"id": 2, "name": "Curd", "price": 40, "image": "curd.jpg"},
    {"id": 3, "name": "Ghee", "price": 120, "image": "ghee.jpg"},
    {"id": 4, "name": "Paneer", "price": 150, "image": "paneer.jpg"}
]

# Cashfree Configuration (use environment variables for production)
# Replace with your actual API keys and endpoint
CASHFREE_APP_ID = os.environ.get('CASHFREE_APP_ID')
CASHFREE_SECRET_KEY = os.environ.get('CASHFREE_SECRET_KEY')
CASHFREE_ENDPOINT = "https://sandbox.cashfree.com/pg" # Use production endpoint for production

Cashfree.XClientId = CASHFREE_APP_ID
Cashfree.XClientSecret = CASHFREE_SECRET_KEY
Cashfree.XEnvironment = Cashfree.SANDBOX # Use Cashfree.PRODUCTION for production


@app.route('/')
def index():
    return render_template('index.html', products=PRODUCTS)

@app.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        return "Product not found", 404

    cart = session.get('cart', [])
    cart.append(product)
    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    subtotal = sum(item['price'] for item in cart)
    gst = subtotal * 0.12
    delivery = subtotal * 0.08
    total = subtotal + gst + delivery
    return render_template('cart.html', cart=cart, subtotal=subtotal, gst=gst, delivery=delivery, total=total)

@app.route('/remove-from-cart/<int:index>')
def remove_from_cart(index):
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        cart.pop(index)
        session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/payment', methods=['GET'])
def payment():
    return render_template('payment.html')

@app.route('/checkout', methods=['GET'])
def checkout():
    return render_template('checkout.html')

@app.route('/create_cashfree_order', methods=['POST'])
def create_cashfree_order():
    data = request.json
    order_amount = data.get('order_amount')
    customer_details = data.get('customer_details')
    order_id = str(uuid.uuid4())

    if not all([order_amount, customer_details]):
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        order_payload = {
            "order_amount": order_amount,
            "order_id": order_id,
            "order_currency": "INR",
            "customer_details": customer_details,
        }

        api_response = Cashfree().PGCreateOrder("2023-08-01", order_payload, None, None)
        payment_session_id = api_response.data.payment_session_id

        if payment_session_id:
            return jsonify({'payment_session_id': payment_session_id}), 200
        else:
            return jsonify({'message': 'Failed to create Cashfree order'}), 500

    except CashfreeApiException as e:
        print(f"Cashfree API error: {e}")
        return jsonify({'message': 'Cashfree API error', 'error': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'message': 'An unexpected error occurred'}), 500

@app.route('/submit_order', methods=['POST'])
def submit_order():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    address = data.get('address')
    cart_items = data.get('cartItems', [])

@app.route('/create-order', methods=['POST'])
def create_order():
    cart = session.get('cart', [])
    if not cart:
        return redirect(url_for('index'))

    email = request.form.get('email')
    phone = request.form.get('phone')

    subtotal = sum(item['price'] for item in cart)
    gst = subtotal * 0.12
    delivery = subtotal * 0.08
    total_amount = round(subtotal + gst + delivery, 2)

    headers = {
        "accept": "application/json",
        "x-api-version": "2022-09-01",
        "content-type": "application/json",
        "x-client-id": CASHFREE_APP_ID,
        "x-client-secret": CASHFREE_SECRET_KEY,
    }

    order_id = f"order_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    data = {
        "customer_details": {
            "customer_id": f"{email}-{datetime.now().timestamp()}",
            "customer_email": email,
            "customer_phone": phone
        },
        "order_amount": total_amount,
        "order_currency": "INR",
        "order_id": order_id,
        "order_meta": {
            "return_url": f"{request.url_root}payment_response?order_id={order_id}"
        }
    }

    response = requests.post(CASHFREE_BASE_URL, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        result = response.json()
        payment_link = result.get("payment_link")
        return render_template("payment.html", payment_link=payment_link)
    else:
        return f"Payment failed: {response.text}", 500

@app.route('/payment_response')
def payment_response():
    return "Thank you for your payment! You will receive confirmation shortly."

if __name__ == '__main__':
    app.run(debug=True)