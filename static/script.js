let cart = JSON.parse(localStorage.getItem('cart')) || [];

document.addEventListener('DOMContentLoaded', () => {
  updateCartCount();
});

function addToCart(itemName, itemImage) {
  const existingItem = cart.find(item => item.name === itemName);
  const itemPrice = getPrice(itemName);

  if (existingItem) {
    existingItem.quantity++;
  } else {
    cart.push({
      name: itemName,
      image: itemImage,
      quantity: 1,
      price: itemPrice
    });
  }

  localStorage.setItem("cart", JSON.stringify(cart));
  updateCartCount();
  showToast(`${itemName} added to cart`);

  // Add bounce animation to cart icon
  const cartIcon = document.querySelector('.fa-shopping-cart');
  if (cartIcon) {
    cartIcon.classList.add('cart-icon-bounce');
    setTimeout(() => {
      cartIcon.classList.remove('cart-icon-bounce');
    }, 500); // Match animation duration
  }
}

function getPrice(itemName) {
  switch (itemName) {
    case "Milk":
      return 90;
    case "Curd":
      return 70;
    case "Ghee":
      return 500;
    case "Monthly Milk Package":
      return 3000; // Fixed price with no tax
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

function showToast(message) {
  const toast = document.getElementById("toast");
  if (!toast) return;

  toast.textContent = message;
  toast.classList.add("show");
  toast.classList.remove("hidden");

  setTimeout(() => {
    toast.classList.remove("show");
    toast.classList.add("hidden");
  }, 2000);
}
