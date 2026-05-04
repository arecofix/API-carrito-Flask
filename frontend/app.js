const API_BASE_URL = 'http://127.0.0.1:5000/api';

const servicesGrid = document.getElementById('services-grid');
const cartItemsContainer = document.getElementById('cart-items');
const cartTotalElement = document.getElementById('cart-total');
const checkoutBtn = document.getElementById('checkout-btn');
const clearCartBtn = document.getElementById('clear-cart-btn');

// Formateador de moneda
const formatPrice = (price) => {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(price);
};

// Cargar catálogo de servicios
async function loadServices() {
    try {
        const response = await fetch(`${API_BASE_URL}/services`);
        const services = await response.json();
        
        servicesGrid.innerHTML = '';
        services.forEach(service => {
            const card = document.createElement('div');
            card.className = 'service-card';
            card.innerHTML = `
                <div>
                    <h3 class="service-name">${service.servicio}</h3>
                    <p class="service-price">${formatPrice(service.precio)}</p>
                </div>
                <button class="btn btn-primary" onclick="addToCart(${service.id})">Agregar al Carrito</button>
            `;
            servicesGrid.appendChild(card);
        });
    } catch (error) {
        console.error('Error cargando servicios:', error);
    }
}

// Cargar carrito
async function loadCart() {
    try {
        const response = await fetch(`${API_BASE_URL}/cart`);
        const data = await response.json();
        
        renderCart(data.items, data.total);
    } catch (error) {
        console.error('Error cargando carrito:', error);
    }
}

// Renderizar carrito en la UI
function renderCart(items, total) {
    cartItemsContainer.innerHTML = '';
    
    if (items.length === 0) {
        cartItemsContainer.innerHTML = '<p class="empty-cart-msg">Tu carrito está vacío.</p>';
        checkoutBtn.disabled = true;
    } else {
        items.forEach(item => {
            const cartItem = document.createElement('div');
            cartItem.className = 'cart-item';
            cartItem.innerHTML = `
                <div class="item-info">
                    <h4>${item.servicio}</h4>
                    <p>${formatPrice(item.subtotal)}</p>
                </div>
                <div class="item-actions">
                    <button class="quantity-btn" onclick="updateQuantity(${item.service_id}, ${item.cantidad - 1})">-</button>
                    <span>${item.cantidad}</span>
                    <button class="quantity-btn" onclick="updateQuantity(${item.service_id}, ${item.cantidad + 1})">+</button>
                </div>
            `;
            cartItemsContainer.appendChild(cartItem);
        });
        checkoutBtn.disabled = false;
    }
    
    cartTotalElement.innerText = formatPrice(total);
}

// Agregar al carrito
async function addToCart(serviceId) {
    try {
        await fetch(`${API_BASE_URL}/cart`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ service_id: serviceId, cantidad: 1 })
        });
        loadCart();
    } catch (error) {
        console.error('Error agregando al carrito:', error);
    }
}

// Actualizar cantidad (sumar/restar)
async function updateQuantity(serviceId, newQuantity) {
    try {
        await fetch(`${API_BASE_URL}/cart/${serviceId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cantidad: newQuantity })
        });
        loadCart();
    } catch (error) {
        console.error('Error actualizando cantidad:', error);
    }
}

// Vaciar carrito
clearCartBtn.addEventListener('click', async () => {
    try {
        await fetch(`${API_BASE_URL}/cart`, { method: 'DELETE' });
        loadCart();
    } catch (error) {
        console.error('Error vaciando carrito:', error);
    }
});

// Checkout
checkoutBtn.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/checkout`, { method: 'POST' });
        if (response.ok) {
            alert('¡Compra finalizada con éxito!');
            loadCart();
        }
    } catch (error) {
        console.error('Error en checkout:', error);
    }
});

// Inicializar
loadServices();
loadCart();
