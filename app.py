from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)
CORS(app)  # Enable CORS

# Email configuration
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'lokesh154721@gmail.com')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD', 'honw bbzy eqxc cfin ')  # Use Gmail App Password
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL', 'lokesh154721@gmail.com')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/payment')
def payment():
    return render_template('payment.html')

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
        email_body += f"- {item['name']} (Quantity: {item.get('quantity', 1)}) = ₹{item_total}\n"

    email_body += f"\nTotal Amount: ₹{total_price}\n"

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
