import os
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from blueprints.products import products_bp
from extensions import db
from models import Product, Review, OrderItem
from forms import ProductForm, ReviewForm
from utils import save_product_image


@products_bp.route('/products')
def list_products():
    """Browse all products, with optional search and category filter."""
    query = Product.query

    search_term = request.args.get('q', '').strip()
    if search_term:
        query = query.filter(Product.name.ilike(f'%{search_term}%'))

    category = request.args.get('category', '').strip()
    if category:
        query = query.filter_by(category=category)

    products = query.order_by(Product.created_at.desc()).all()

    categories = ['Pottery', 'Handloom', 'Wooden Crafts', 'Bamboo Crafts', 'Paintings', 'Jewelry']

    return render_template(
        'products/products.html',
        products=products,
        categories=categories,
        search_term=search_term,
        selected_category=category
    )


@products_bp.route('/products/<int:product_id>')
def product_detail(product_id):
    """View details of a single product, with reviews and purchase eligibility."""
    product = Product.query.get_or_404(product_id)

    reviews = Review.query.filter_by(product_id=product.id).order_by(Review.created_at.desc()).all()
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else None

    can_review = False
    already_reviewed = False

    if current_user.is_authenticated and current_user.is_customer():
        has_purchased = OrderItem.query.filter_by(
            product_id=product.id, artisan_id=product.artisan_id
        ).join(OrderItem.order).filter_by(customer_id=current_user.id).first()

        already_reviewed = Review.query.filter_by(product_id=product.id, customer_id=current_user.id).first() is not None
        can_review = bool(has_purchased) and not already_reviewed

    return render_template(
        'products/product_detail.html',
        product=product,
        reviews=reviews,
        avg_rating=avg_rating,
        can_review=can_review,
        already_reviewed=already_reviewed
    )


@products_bp.route('/artisan/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """Artisan adds a new product."""
    if not current_user.is_artisan():
        abort(403)

    form = ProductForm()

    if form.validate_on_submit():
        image_filename = save_product_image(form.image.data)

        new_product = Product(
            artisan_id=current_user.id,
            name=form.name.data,
            category=form.category.data,
            description=form.description.data,
            price=form.price.data,
            image_filename=image_filename,
            story=form.story.data,
            artisan_message=form.artisan_message.data,
            origin_region=form.origin_region.data,
            video_url=form.video_url.data
        )
        db.session.add(new_product)
        db.session.commit()

        flash('Product added successfully!', 'success')
        return redirect(url_for('products.product_detail', product_id=new_product.id))

    return render_template('products/add_edit_product.html', form=form, mode='add')


@products_bp.route('/artisan/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Artisan edits their own product."""
    product = Product.query.get_or_404(product_id)

    if product.artisan_id != current_user.id:
        abort(403)

    form = ProductForm(obj=product)

    if form.validate_on_submit():
        product.name = form.name.data
        product.category = form.category.data
        product.description = form.description.data
        product.price = form.price.data
        product.story = form.story.data
        product.artisan_message = form.artisan_message.data
        product.origin_region = form.origin_region.data
        product.video_url = form.video_url.data

        if form.image.data:
            new_image = save_product_image(form.image.data)
            if new_image:
                product.image_filename = new_image

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products.product_detail', product_id=product.id))

    return render_template('products/add_edit_product.html', form=form, mode='edit', product=product)


@products_bp.route('/artisan/products/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    """Artisan deletes their own product, unless it has existing orders."""
    product = Product.query.get_or_404(product_id)

    if product.artisan_id != current_user.id:
        abort(403)

    if product.order_items:
        flash('This product cannot be deleted because it has existing orders. Consider marking it out of stock instead.', 'warning')
        return redirect(url_for('products.product_detail', product_id=product.id))

    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'info')
    return redirect(url_for('products.list_products'))

@products_bp.route('/products/<int:product_id>/review', methods=['GET', 'POST'])
@login_required
def add_review(product_id):
    """Customer leaves a review for a product they've purchased."""
    product = Product.query.get_or_404(product_id)

    if not current_user.is_customer():
        abort(403)

    has_purchased = OrderItem.query.filter_by(
        product_id=product.id
    ).join(OrderItem.order).filter_by(customer_id=current_user.id).first()

    if not has_purchased:
        flash('You can only review products you have purchased.', 'warning')
        return redirect(url_for('products.product_detail', product_id=product.id))

    existing_review = Review.query.filter_by(product_id=product.id, customer_id=current_user.id).first()
    if existing_review:
        flash('You have already reviewed this product.', 'info')
        return redirect(url_for('products.product_detail', product_id=product.id))

    form = ReviewForm()

    if form.validate_on_submit():
        new_review = Review(
            product_id=product.id,
            customer_id=current_user.id,
            rating=int(form.rating.data),
            comment=form.comment.data
        )
        db.session.add(new_review)
        db.session.commit()

        flash('Review submitted. Thank you!', 'success')
        return redirect(url_for('products.product_detail', product_id=product.id))

    return render_template('products/add_review.html', form=form, product=product)