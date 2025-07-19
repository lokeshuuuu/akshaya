let cart = JSON.parse(localStorage.getItem('cart')) || [];

document.addEventListener('DOMContentLoaded', () => {
  // Dark mode toggle functionality
  const themeToggle = document.getElementById('theme-toggle');
  const body = document.body;

  // Check for saved theme in localStorage
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    body.classList.add(savedTheme);
  }

  // Toggle theme on button click
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      body.classList.toggle('dark-mode');
      localStorage.setItem('theme', body.classList.contains('dark-mode') ? 'dark-mode' : '');
    });
  }
  updateCartCount();

  // --- Existing payment page logic (modify to integrate Cashfree) ---
  const cartItems = JSON.parse(localStorage.getItem('cart')) || [];
  const cartList = document.getElementById('cart-items-payment');
  const priceSummary = document.getElementById('price-summary');
  const cashfreePayBtn = document.getElementById('cashfree-pay-btn'); // Get the new button

  if (cartItems.length === 0) {
    cartList.innerHTML = '<p>Your cart is empty. Please add items from the <a href="{{ url_for("home") }}">store</a>.</p>';
    if (cashfreePayBtn) {
      cashfreePayBtn.disabled = true; // Disable button if cart is empty
    }
    return;
  }

  let subtotal = 0;

  cartItems.forEach((item, index) => {
    const itemTotal = item.price * item.quantity;
    subtotal += itemTotal;

    const li = document.createElement('li');
    li.className = 'cart-item-payment';
    li.innerHTML = `
      <img src="${item.image}" alt="${item.name}" style="width: 70px; height: 70px;">
      <span>${item.name} × ${item.quantity} = ₹${itemTotal}</span>
      <button onclick="removeItem(${index})">Delete</button>
    `;
    cartList.appendChild(li);
  });

  const gst = subtotal * 0.12;
  const delivery = subtotal * 0.08;
  const total = subtotal + gst + delivery;

  priceSummary.innerHTML = `
    <div class="price-summary-row"><span>Subtotal:</span><span>₹${subtotal.toFixed(2)}</span></div>
    <div class="price-summary-row"><span>GST (12%):</span><span>₹${gst.toFixed(2)}</span></div>
    <div class="price-summary-row"><span>Delivery (8%):</span><span>₹${delivery.toFixed(2)}</span></div>
    <div class="price-summary-row total"><span>Total:</span><span>₹${total.toFixed(2)}</span></div>
  `;

  // --- Cashfree Payment Integration ---
  if (cashfreePayBtn) {
    cashfreePayBtn.addEventListener('click', async () => {
      const name = document.getElementById('customer-name').value;
      const phone = document.getElementById('customer-phone').value;
      const address = document.getElementById('delivery-address').value;

      if (!name || !phone || !address) {
        showToast('Please fill in all customer details.', 'error');
        return;
      }

      // Prepare data for backend
      const orderData = {
        order_amount: total.toFixed(2), // Use the calculated total amount
        customer_details: {
          customer_name: name,
          customer_phone: phone,
          customer_email: "" // You might want to add an email input
        },
        // You can add more details here if needed in the backend
      };

      try {
        // Call backend to create Cashfree order
        const response = await fetch('/create_cashfree_order', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(orderData)
        });

        const result = await response.json();

        if (response.ok && result.payment_session_id) {
          // Initiate Cashfree payment
          const cashfree = new Cashfree();
          const checkoutOptions = {
            paymentSessionId: result.payment_session_id,
            redirectTarget: "_blank" // Recommended for mobile or new tab
          };

          cashfree.checkout(checkoutOptions);

          // Handle the payment response in a callback (optional but recommended)
          // cashfree.then(res => {
          //   if (res.redirectAction === "webview") {
          //     // Handle webview redirection
          //   }
          // });

        } else {
          showToast(result.message || 'Failed to create Cashfree order.', 'error');
        }
      } catch (error) {
        console.error("Error initiating Cashfree payment:", error);
        showToast('An error occurred while initiating payment. Please try again.', 'error');
      }
    });
  }

  // --- Existing helper functions ---
  function showToast(message, type) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.className = `show ${type || ''}`;
    setTimeout(() => toast.className = toast.className.replace('show', ''), 3000);
  }
});

function removeItem(index) {
  const cart = JSON.parse(localStorage.getItem('cart')) || [];
  cart.splice(index, 1);
  localStorage.setItem('cart', JSON.stringify(cart));
  window.location.reload();
}

// Keep your existing getPrice and updateCartCount functions
function getPrice(itemName) {
  switch (itemName) {
    case "Milk":
      return 90;
    case "Curd":
      return 70;
    case "Ghee":
      return 500;
    case "Monthly Milk Package":
      return 2900;
    default:
      return 0;
  }
}

function updateCartCount() {
  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
  const cartCountElem = document.getElementById("cart-count");
  if (cartCountElem) {
    cartCountElem.textContent = totalItems;
  }
}
