from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import smtplib
from email.message import EmailMessage
import os
import uuid
from cashfree_sdk.api_utility import APIUtility
from cashfree_sdk.exceptions.cashfree_api_exception import CashfreeApiException
from cashfree_sdk.exceptions.api_exception import APIException

app = Flask(__name__)
CORS(app)  # Enable CORS

# Email configuration
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'lokesh154721@gmail.com')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD', 'honw bbzy eqxc cfin ')  # Use Gmail App Password
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL', 'lokesh154721@gmail.com')

# Cashfree Configuration (use environment variables for production)
# Replace with your actual API keys and endpoint
CASHFREE_APP_ID = os.environ.get('CASHFREE_APP_ID')
CASHFREE_SECRET_KEY = os.environ.get('CASHFREE_SECRET_KEY')
CASHFREE_ENDPOINT = "https://sandbox.cashfree.com/pg" # Use production endpoint for production

# Initialize Cashfree API Utility
APIUtility.initialize(CASHFREE_ENDPOINT, CASHFREE_APP_ID, CASHFREE_SECRET_KEY)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/create_cashfree_order', methods=['POST'])
def create_cashfree_order():
    data = request.json
    # Extract necessary data from the request (e.g., order_amount, customer_details)
    order_amount = data.get('order_amount')
    customer_details = data.get('customer_details') # Assuming you send customer details from frontend
    order_id = str(uuid.uuid4()) # Generate a unique order ID

    if not all([order_amount, customer_details]):
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        # Create order payload
        order_payload = {
            "order_amount": order_amount,
            "order_id": order_id,
            "order_currency": "INR", # Or your desired currency
            "customer_details": customer_details,
            # Add more details as needed (e.g., order_meta, order_expiry_time)
        }

        # Call Cashfree API to create order
        response = APIUtility.create_order(order_payload)
        payment_session_id = response.get('payment_session_id')

        if payment_session_id:
            return jsonify({'payment_session_id': payment_session_id}), 200
        else:
            return jsonify({'message': 'Failed to create Cashfree order'}), 500

    except (CashfreeApiException, APIException) as e:
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

    if not all([name, phone, address, cart_items]):
        return jsonify({'message': 'Missing required fields'}), 400

    email_body = f"""
    New Order Received!

    Customer Details:
    Name: {name}
    Phone: {phone}
    Address: {address}

    Cart Items:
    """

    total_price = 0
    for item in cart_items:
        price = 0
        if item['name'] == 'Milk':
            price = 90
        elif item['name'] == 'Curd':
            price = 70
        elif item['name'] == 'Ghee':
            price = 500
        elif item['name'] == 'Monthly Milk Package':
            price = 2900

        item_total = price * item.get('quantity', 1)
        total_price += item_total
        email_body += f"- {item['name']} (Quantity: {item.get('quantity', 1)}) = ₹{item_total}
"

    email_body += f"
Total Amount: ₹{total_price}
"

    # Send email
    msg = EmailMessage()
    msg.set_content(email_body)
    msg['Subject'] = 'New Order - Akshaya'
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        return jsonify({'message': 'Order submitted successfully and email sent!'}), 200
    except Exception as e:
        print(f"Email sending failed: {e}")
        return jsonify({'message': 'Failed to send order email'}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
