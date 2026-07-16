// Wishlist heart icon toggle (AJAX)
function toggleWishlist(button, productId) {
    fetch(`/wishlist/toggle/${productId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'added') {
                button.textContent = '♥';
                button.classList.add('wishlist-active');
            } else if (data.status === 'removed') {
                button.textContent = '♡';
                button.classList.remove('wishlist-active');
            } else if (data.error) {
                alert(data.error);
            }
        })
        .catch(() => {
            alert('Something went wrong. Please try again.');
        });
}