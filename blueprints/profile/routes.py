from flask import render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from blueprints.profile import profile_bp
from extensions import db
from models import ArtisanProfile, Product, OrderItem, Order
from sqlalchemy import func, extract
from forms import ProfileForm
from utils import save_product_image

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required


def view_profile():
    """View and edit the logged-in user's profile."""
    form = ProfileForm()

    # For artisans, load their existing ArtisanProfile (create one if it doesn't exist yet)
    artisan_profile = None
    if current_user.is_artisan():
        artisan_profile = current_user.artisan_profile
        if artisan_profile is None:
            artisan_profile = ArtisanProfile(user_id=current_user.id)
            db.session.add(artisan_profile)
            db.session.commit()

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data

        if current_user.is_artisan():
            artisan_profile.shop_name = form.shop_name.data
            artisan_profile.bio = form.bio.data
            artisan_profile.village = form.village.data
            artisan_profile.district = form.district.data
            artisan_profile.state = form.state.data

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.view_profile'))

    # Pre-fill the form with existing data on GET request
    if not form.is_submitted():
        form.name.data = current_user.name
        form.phone.data = current_user.phone
        form.address.data = current_user.address

        if current_user.is_artisan():
            form.shop_name.data = artisan_profile.shop_name
            form.bio.data = artisan_profile.bio
            form.village.data = artisan_profile.village
            form.district.data = artisan_profile.district
            form.state.data = artisan_profile.state

    return render_template('profile/profile.html', form=form)

@profile_bp.route('/artisan/<int:artisan_id>')
def artisan_public_profile(artisan_id):
    """Public-facing artisan profile page — 'Know Your Artisan'."""
    from models import User, Product

    artisan = User.query.filter_by(id=artisan_id, role='artisan').first_or_404()
    products = Product.query.filter_by(artisan_id=artisan.id).order_by(Product.created_at.desc()).all()

    return render_template('profile/artisan_public.html', artisan=artisan, products=products)

@profile_bp.route('/notifications')
@login_required
def view_notifications():
    """Show all notifications for the logged-in user, mark as read."""
    from models import Notification

    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(20).all()

    for n in notifications:
        n.is_read = True
    db.session.commit()

    return render_template('profile/notifications.html', notifications=notifications)
    

@profile_bp.route("/analytics")
@login_required
def analytics_dashboard():
    """Artisan Analytics Dashboard."""

    if not current_user.is_artisan():
        flash("Access denied.", "danger")
        return redirect(url_for("main.home"))

    products = Product.query.filter_by(artisan_id=current_user.id).all()
    order_items = OrderItem.query.filter_by(artisan_id=current_user.id).all()

    total_products = len(products)
    total_orders = len(order_items)

    total_revenue = sum(
        item.price_at_purchase * item.quantity
        for item in order_items
    )

    pending_orders = sum(
        1 for item in order_items
        if item.status == "Pending"
    )

    shipped_orders = sum(
        1 for item in order_items
        if item.status == "Shipped"
    )

    out_for_delivery_orders = sum(
        1 for item in order_items
        if item.status == "Out for Delivery"
    )

    delivered_orders = sum(
        1 for item in order_items
        if item.status == "Delivered"
    )

    return render_template(
        "profile/analytics_dashboard.html",
        total_products=total_products,
        total_orders=total_orders,
        total_revenue=total_revenue,
        pending_orders=pending_orders,
        shipped_orders=shipped_orders,
        out_for_delivery_orders=out_for_delivery_orders,
        delivered_orders=delivered_orders,
    )
@profile_bp.route("/analytics-data")
@login_required
def analytics_data():
    """Return analytics data as JSON."""

    if not current_user.is_artisan():
        return jsonify({"error": "Access denied"}), 403

    order_items = OrderItem.query.filter_by(
        artisan_id=current_user.id
    ).all()

    month_labels = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    monthly_revenue = [0] * 12

    pending = 0
    shipped = 0
    out_for_delivery = 0
    delivered = 0

    for item in order_items:

        revenue = float(item.price_at_purchase) * item.quantity

        if item.order and item.order.placed_at:
            month = item.order.placed_at.month - 1
            monthly_revenue[month] += revenue

        if item.status == "Pending":
            pending += 1
        elif item.status == "Shipped":
            shipped += 1
        elif item.status == "Out for Delivery":
            out_for_delivery += 1
        elif item.status == "Delivered":
            delivered += 1

    return jsonify({
        "month_labels": month_labels,
        "monthly_revenue": monthly_revenue,
        "status": {
            "pending": pending,
            "shipped": shipped,
            "out_for_delivery": out_for_delivery,
            "delivered": delivered
        }
    })