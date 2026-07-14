import os
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from blueprints.products import products_bp
from extensions import db
from models import Product
from forms import ProductForm
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
    """View details of a single product."""
    product = Product.query.get_or_404(product_id)
    return render_template('products/product_detail.html', product=product)


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
            image_filename=image_filename
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