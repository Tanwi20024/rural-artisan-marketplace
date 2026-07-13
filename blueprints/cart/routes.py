from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from blueprints.cart import cart_bp
from extensions import db
from models import Cart, Product, Order, OrderItem


@cart_bp.route('/cart')
@login_required
def view_cart():
    """Show all items in the customer's cart."""
    if not current_user.is_customer():
        abort(403)

    cart_items = Cart.query.filter_by(customer_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)

    return render_template('cart/cart.html', cart_items=cart_items, total=total)


@cart_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """Add a product to the customer's cart, or increase quantity if already in it."""
    if not current_user.is_customer():
        abort(403)

    product = Product.query.get_or_404(product_id)

    existing_item = Cart.query.filter_by(
        customer_id=current_user.id, product_id=product.id
    ).first()

    if existing_item:
        existing_item.quantity += 1
    else:
        new_item = Cart(customer_id=current_user.id, product_id=product.id, quantity=1)
        db.session.add(new_item)

    db.session.commit()
    flash(f'{product.name} added to cart.', 'success')
    return redirect(url_for('products.product_detail', product_id=product.id))


@cart_bp.route('/cart/update/<int:cart_id>', methods=['POST'])
@login_required
def update_quantity(cart_id):
    """Update the quantity of a cart item."""
    cart_item = Cart.query.get_or_404(cart_id)

    if cart_item.customer_id != current_user.id:
        abort(403)

    new_quantity = request.form.get('quantity', type=int)

    if new_quantity and new_quantity > 0:
        cart_item.quantity = new_quantity
        db.session.commit()
        flash('Cart updated.', 'success')
    else:
        flash('Invalid quantity.', 'danger')

    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/cart/remove/<int:cart_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_id):
    """Remove an item from the cart."""
    cart_item = Cart.query.get_or_404(cart_id)

    if cart_item.customer_id != current_user.id:
        abort(403)

    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Show checkout page and place the order (Cash on Delivery)."""
    if not current_user.is_customer():
        abort(403)

    cart_items = Cart.query.filter_by(customer_id=current_user.id).all()

    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('products.list_products'))

    total = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        shipping_address = request.form.get('shipping_address', '').strip()

        if not shipping_address:
            flash('Please enter a shipping address.', 'danger')
            return render_template('cart/checkout.html', cart_items=cart_items, total=total)

        # Create the order
        new_order = Order(
            customer_id=current_user.id,
            total_amount=total,
            shipping_address=shipping_address,
            payment_method='Cash on Delivery'
        )
        db.session.add(new_order)
        db.session.flush()  # gets new_order.id before commit

        # Create order items from cart, then clear the cart
        for item in cart_items:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item.product.id,
                artisan_id=item.product.artisan_id,
                quantity=item.quantity,
                price_at_purchase=item.product.price,
                status='Pending'
            )
            db.session.add(order_item)
            db.session.delete(item)

        db.session.commit()

        flash('Order placed successfully! Pay on delivery.', 'success')
        return redirect(url_for('products.list_products'))

    return render_template('cart/checkout.html', cart_items=cart_items, total=total)