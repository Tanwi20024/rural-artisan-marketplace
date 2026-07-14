from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from blueprints.orders import orders_bp
from extensions import db
from models import Order, OrderItem, ReturnRequest
from forms import ReturnRequestForm

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


# Defines the order status pipeline — used to determine the "next" status
STATUS_FLOW = ['Pending', 'Shipped', 'Out for Delivery', 'Delivered']


@orders_bp.route('/artisan/orders/<int:item_id>/advance', methods=['POST'])
@login_required
def advance_status(item_id):
    """Artisan moves their order item to the next status in the pipeline."""
    order_item = OrderItem.query.get_or_404(item_id)

    if order_item.artisan_id != current_user.id:
        abort(403)

    current_index = STATUS_FLOW.index(order_item.status)

    if current_index < len(STATUS_FLOW) - 1:
        order_item.status = STATUS_FLOW[current_index + 1]
        db.session.commit()
        flash(f'Status updated to "{order_item.status}".', 'success')
    else:
        flash('This order is already delivered.', 'info')

    return redirect(url_for('orders.artisan_orders'))

@orders_bp.route('/orders/<int:item_id>/return', methods=['GET', 'POST'])
@login_required
def request_return(item_id):
    """Customer requests a return for a delivered order item."""
    order_item = OrderItem.query.get_or_404(item_id)

    if order_item.order.customer_id != current_user.id:
        abort(403)

    if order_item.status != 'Delivered':
        flash('Only delivered items can be returned.', 'warning')
        return redirect(url_for('orders.my_orders'))

    if order_item.return_request:
        flash('A return request already exists for this item.', 'info')
        return redirect(url_for('orders.my_orders'))

    form = ReturnRequestForm()

    if form.validate_on_submit():
        new_request = ReturnRequest(
            order_item_id=order_item.id,
            customer_id=current_user.id,
            reason=form.reason.data
        )
        db.session.add(new_request)
        db.session.commit()

        flash('Return request submitted.', 'success')
        return redirect(url_for('orders.my_orders'))

    return render_template('orders/request_return.html', form=form, order_item=order_item)


@orders_bp.route('/artisan/returns/<int:request_id>/<action>', methods=['POST'])
@login_required
def handle_return(request_id, action):
    """Artisan approves or rejects a return request."""
    return_request = ReturnRequest.query.get_or_404(request_id)

    if return_request.order_item.artisan_id != current_user.id:
        abort(403)

    if action == 'approve':
        return_request.status = 'Approved'
        flash('Return request approved.', 'success')
    elif action == 'reject':
        return_request.status = 'Rejected'
        flash('Return request rejected.', 'info')
    else:
        abort(400)

    db.session.commit()
    return redirect(url_for('orders.artisan_orders'))