// Function to render cart items
function renderCart() {
    const cartTableBody = document.querySelector('#cart-table tbody');
    const cart = JSON.parse(localStorage.getItem('cart')) || [];

    // Clear the table before rendering
    cartTableBody.innerHTML = '';

    // Render each item in the cart
    cart.forEach((item, index) => {
        const row = document.createElement('tr');

        // Item name
        const itemCell = document.createElement('td');
        itemCell.textContent = item.name;
        row.appendChild(itemCell);

        // Item quantity
        const quantityCell = document.createElement('td');
        quantityCell.textContent = item.quantity;
        row.appendChild(quantityCell);

        // Item price
        const priceCell = document.createElement('td');
        priceCell.textContent = `$${item.price.toFixed(2)}`;
        row.appendChild(priceCell);

        // Item total (Price * Quantity)
        const totalCell = document.createElement('td');
        totalCell.textContent = `$${(item.price * item.quantity).toFixed(2)}`;
        row.appendChild(totalCell);

        // Actions: Remove button
        const actionsCell = document.createElement('td');
        const removeButton = document.createElement('button');
        removeButton.textContent = 'Remove';
        removeButton.classList.add('btn', 'remove-btn');
        removeButton.addEventListener('click', () => removeItemFromCart(index));
        actionsCell.appendChild(removeButton);
        row.appendChild(actionsCell);

        // Append the row to the table body
        cartTableBody.appendChild(row);
    });

    // Update the checkout button with the total price
    updateCheckoutTotal();
}

// Function to update the total price in the checkout section
function updateCheckoutTotal() {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
    const placeOrderButton = document.querySelector('#place-order');
    placeOrderButton.textContent = `Place Order - Total: $${total.toFixed(2)}`;
}

// Function to remove an item from the cart
function removeItemFromCart(index) {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    cart.splice(index, 1); // Remove the item at the specified index
    localStorage.setItem('cart', JSON.stringify(cart)); // Save the updated cart back to localStorage
    renderCart(); // Re-render the cart
}

// Initial render
document.addEventListener('DOMContentLoaded', () => {
    renderCart();
});
