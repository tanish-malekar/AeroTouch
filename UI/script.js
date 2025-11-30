// Menu Data
const menuData = {
    burgers: [
        { id: 'b1', name: 'Classic Burger', description: 'Juicy beef patty with fresh lettuce, tomato, and our special sauce', price: 8.99, emoji: '🍔' },
        { id: 'b2', name: 'Cheese Burger', description: 'Double cheese, caramelized onions, and crispy bacon', price: 10.99, emoji: '🍔' },
        { id: 'b3', name: 'Veggie Burger', description: 'Grilled veggie patty with avocado and sprouts', price: 9.49, emoji: '🥬' },
        { id: 'b4', name: 'BBQ Burger', description: 'Smoky BBQ sauce, onion rings, and cheddar cheese', price: 11.99, emoji: '🍔' },
        { id: 'b5', name: 'Spicy Burger', description: 'Jalapeños, pepper jack cheese, and sriracha mayo', price: 10.49, emoji: '🌶️' },
        { id: 'b6', name: 'Mushroom Swiss', description: 'Sautéed mushrooms and melted Swiss cheese', price: 11.49, emoji: '🍄' }
    ],
    pizzas: [
        { id: 'p1', name: 'Margherita', description: 'Fresh tomatoes, mozzarella, and basil on thin crust', price: 12.99, emoji: '🍕' },
        { id: 'p2', name: 'Pepperoni', description: 'Classic pepperoni with extra cheese', price: 14.99, emoji: '🍕' },
        { id: 'p3', name: 'Hawaiian', description: 'Ham, pineapple, and mozzarella cheese', price: 13.99, emoji: '🍍' },
        { id: 'p4', name: 'Veggie Supreme', description: 'Bell peppers, olives, mushrooms, and onions', price: 13.49, emoji: '🥗' },
        { id: 'p5', name: 'Meat Lovers', description: 'Pepperoni, sausage, bacon, and ham', price: 16.99, emoji: '🥓' },
        { id: 'p6', name: 'BBQ Chicken', description: 'Grilled chicken, BBQ sauce, and red onions', price: 15.49, emoji: '🍗' }
    ],
    drinks: [
        { id: 'd1', name: 'Cola', description: 'Ice-cold classic cola drink', price: 2.49, emoji: '🥤' },
        { id: 'd2', name: 'Lemonade', description: 'Fresh squeezed lemonade with mint', price: 3.49, emoji: '🍋' },
        { id: 'd3', name: 'Iced Tea', description: 'Refreshing iced tea with lemon', price: 2.99, emoji: '🧊' },
        { id: 'd4', name: 'Milkshake', description: 'Creamy vanilla milkshake with whipped cream', price: 4.99, emoji: '🥛' },
        { id: 'd5', name: 'Orange Juice', description: 'Freshly squeezed orange juice', price: 3.99, emoji: '🍊' },
        { id: 'd6', name: 'Coffee', description: 'Premium roasted coffee, hot or iced', price: 3.49, emoji: '☕' }
    ]
};

// Cart State
let cart = {};
let currentCategory = 'burgers';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    showCategory('burgers');
});

// Show Category
function showCategory(category) {
    currentCategory = category;
    
    // Update active button
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Render items
    renderMenu(category);
}

// Render Menu Items
function renderMenu(category) {
    const container = document.getElementById('menu-container');
    const items = menuData[category];
    
    let html = '<div class="menu-grid">';
    
    items.forEach(item => {
        const quantity = cart[item.id] || 0;
        html += `
            <div class="menu-item">
                <div class="item-image">${item.emoji}</div>
                <div class="item-details">
                    <h3 class="item-name">${item.name}</h3>
                    <p class="item-description">${item.description}</p>
                    <p class="item-price">$${item.price.toFixed(2)}</p>
                    <div class="quantity-controls">
                        <button class="qty-btn" onclick="updateQuantity('${item.id}', -1)">−</button>
                        <span class="qty-display" id="qty-${item.id}">${quantity}</span>
                        <button class="qty-btn" onclick="updateQuantity('${item.id}', 1)">+</button>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// Update Quantity
function updateQuantity(itemId, change) {
    const currentQty = cart[itemId] || 0;
    const newQty = Math.max(0, currentQty + change);
    
    if (newQty === 0) {
        delete cart[itemId];
    } else {
        cart[itemId] = newQty;
    }
    
    // Update display
    const qtyDisplay = document.getElementById(`qty-${itemId}`);
    if (qtyDisplay) {
        qtyDisplay.textContent = newQty;
    }
    
    updateCartCount();
}

// Update Cart Count
function updateCartCount() {
    const count = Object.values(cart).reduce((sum, qty) => sum + qty, 0);
    document.getElementById('cart-count').textContent = count;
}

// Find Item by ID
function findItemById(itemId) {
    for (const category of Object.values(menuData)) {
        const item = category.find(i => i.id === itemId);
        if (item) return item;
    }
    return null;
}

// Open Cart
function openCart() {
    const modal = document.getElementById('cart-modal');
    modal.classList.add('active');
    renderCart();
}

// Close Cart
function closeCart() {
    const modal = document.getElementById('cart-modal');
    modal.classList.remove('active');
}

// Render Cart
function renderCart() {
    const cartContainer = document.getElementById('cart-items');
    const cartItems = Object.entries(cart);
    
    if (cartItems.length === 0) {
        cartContainer.innerHTML = '<p class="empty-cart">Your cart is empty 🛒</p>';
        document.getElementById('cart-total').textContent = '0.00';
        return;
    }
    
    let html = '';
    let total = 0;
    
    cartItems.forEach(([itemId, quantity]) => {
        const item = findItemById(itemId);
        if (item) {
            const itemTotal = item.price * quantity;
            total += itemTotal;
            
            html += `
                <div class="cart-item">
                    <div class="cart-item-info">
                        <p class="cart-item-name">${item.emoji} ${item.name}</p>
                        <p class="cart-item-price">$${item.price.toFixed(2)} × ${quantity} = $${itemTotal.toFixed(2)}</p>
                    </div>
                    <div class="cart-item-controls">
                        <button class="cart-qty-btn" onclick="updateCartItem('${itemId}', -1)">−</button>
                        <span>${quantity}</span>
                        <button class="cart-qty-btn" onclick="updateCartItem('${itemId}', 1)">+</button>
                    </div>
                </div>
            `;
        }
    });
    
    cartContainer.innerHTML = html;
    document.getElementById('cart-total').textContent = total.toFixed(2);
}

// Update Cart Item
function updateCartItem(itemId, change) {
    updateQuantity(itemId, change);
    renderCart();
    
    // Also update the menu display if the item is visible
    const qtyDisplay = document.getElementById(`qty-${itemId}`);
    if (qtyDisplay) {
        qtyDisplay.textContent = cart[itemId] || 0;
    }
}

// Place Order
function placeOrder() {
    if (Object.keys(cart).length === 0) {
        alert('Your cart is empty!');
        return;
    }
    
    // Generate random 2-digit order number
    const orderNumber = Math.floor(Math.random() * 90) + 10;
    
    // Clear cart
    cart = {};
    updateCartCount();
    
    // Close cart modal and show order confirmation
    closeCart();
    
    document.getElementById('order-number').textContent = orderNumber;
    document.getElementById('order-modal').classList.add('active');
    
    // Re-render menu to reset quantities
    renderMenu(currentCategory);
}

// Close Order Modal
function closeOrderModal() {
    document.getElementById('order-modal').classList.remove('active');
}

// Close modals on outside click
window.onclick = function(event) {
    const cartModal = document.getElementById('cart-modal');
    const orderModal = document.getElementById('order-modal');
    
    if (event.target === cartModal) {
        closeCart();
    }
    if (event.target === orderModal) {
        closeOrderModal();
    }
}
