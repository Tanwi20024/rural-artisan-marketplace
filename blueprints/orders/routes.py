from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from blueprints.orders import orders_bp
from extensions import db
from models import Order, OrderItem


@orders_bp.route('/my-orders')
@login_required
def my_orders():
    """Customer's order history."""
    if not current_user.is_customer():
        abort(403)

    orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.placed_at.desc()).all()

    return render_template('orders/my_orders.html', orders=orders)


@orders_bp.route('/artisan/orders')
@login_required
def artisan_orders():
    """Artisan's view of order items belonging to their products."""
    if not current_user.is_artisan():
        abort(403)

    order_items = OrderItem.query.filter_by(artisan_id=current_user.id).order_by(OrderItem.id.desc()).all()

    return render_template('orders/artisan_orders.html', order_items=order_items)


@orders_bp.route('/artisan/orders/<int:item_id>/deliver', methods=['POST'])
@login_required
def mark_delivered(item_id):
    """Artisan marks their own order item as delivered."""
    order_item = OrderItem.query.get_or_404(item_id)

    if order_item.artisan_id != current_user.id:
        abort(403)

    order_item.status = 'Delivered'
    db.session.commit()

    flash('Order item marked as delivered.', 'success')
    return redirect(url_for('orders.artisan_orders'))