from flask import Flask, render_template, flash, redirect, url_for, request
from config import Config
from extensions import db, login_manager, migrate
from sqlalchemy import func


def create_app():
    """Application factory - creates and configures the Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Flask-Login configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Import models so Flask-Migrate can detect them
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    # Register blueprints
    from blueprints.auth import auth_bp
    from blueprints.products import products_bp
    from blueprints.cart import cart_bp
    from blueprints.orders import orders_bp
    from blueprints.profile import profile_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(profile_bp)

    @app.route('/')
    def home():
        from flask import session
        from flask_login import current_user
        from models import Product, Order, OrderItem, Review, User, ArtisanProfile
        recently_viewed_ids = session.get('recently_viewed', [])
        recently_viewed_products = []
        if recently_viewed_ids:
            products_by_id = {p.id: p for p in Product.query.filter(Product.id.in_(recently_viewed_ids)).all()}
            recently_viewed_products = [products_by_id[pid] for pid in recently_viewed_ids if pid in products_by_id]

        recommended_products = []
        if current_user.is_authenticated and current_user.is_customer():
            purchased_product_ids = [
                item.product_id for item in
                OrderItem.query.join(Order).filter(Order.customer_id == current_user.id).all()
            ]

            if purchased_product_ids:
                purchased_categories = {
                    p.category for p in Product.query.filter(Product.id.in_(purchased_product_ids)).all()
                }
                recommended_products = Product.query.filter(
                    Product.category.in_(purchased_categories),
                    ~Product.id.in_(purchased_product_ids)
                ).order_by(Product.created_at.desc()).limit(6).all()

        if not recommended_products:
            recommended_products = Product.query.order_by(Product.created_at.desc()).limit(6).all()

            new_arrivals = Product.query.order_by(Product.created_at.desc()).limit(6).all()

        from sqlalchemy import func
        trending_products = (
            Product.query.outerjoin(Review)
            .group_by(Product.id)
            .order_by(func.count(Review.id).desc())
            .limit(6)
            .all()
        )

        from models import User
        featured_artisans = (
            User.query.filter_by(role='artisan')
            .join(Product, Product.artisan_id == User.id)
            .group_by(User.id)
            .order_by(func.count(Product.id).desc())
            .limit(4)
            .all()
        )

        artisans_count = User.query.filter_by(role='artisan').count()
        products_count = Product.query.count()
        orders_count = Order.query.count()

        villages_count = (
            db.session.query(func.count(func.distinct(ArtisanProfile.village)))
            .filter(ArtisanProfile.village.isnot(None), ArtisanProfile.village != '')
            .scalar()
        )
        states_count = (
            db.session.query(func.count(func.distinct(ArtisanProfile.state)))
            .filter(ArtisanProfile.state.isnot(None), ArtisanProfile.state != '')
            .scalar()
        )

        impact_stats = {
            'artisans': artisans_count,
            'products': products_count,
            'villages': villages_count or 0,
            'orders': orders_count,
            'states': states_count or 0,
            'families': artisans_count
        }

        testimonials = (
            Review.query.filter(Review.comment.isnot(None), Review.comment != '')
            .order_by(Review.rating.desc(), Review.created_at.desc())
            .limit(6)
            .all()
        )

        return render_template(
            'home.html',
            recently_viewed_products=recently_viewed_products,
            recommended_products=recommended_products,
            new_arrivals=new_arrivals,
            trending_products=trending_products,
            featured_artisans=featured_artisans,
            impact_stats=impact_stats,
            testimonials=testimonials
        )

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/contact')
    def contact():
        return render_template('contact.html')

    @app.route('/privacy')
    def privacy():
        return render_template('privacy.html')

    @app.route('/terms')
    def terms():
        return render_template('terms.html')
    
    @app.route('/newsletter/subscribe', methods=['POST'])
    def newsletter_subscribe():
        from models import NewsletterSubscriber
        from flask import request

        email = request.form.get('email', '').strip()

        if not email:
            flash('Please enter a valid email address.', 'warning')
            return redirect(request.referrer or url_for('home'))

        existing = NewsletterSubscriber.query.filter_by(email=email).first()
        if existing:
            flash('You are already subscribed!', 'info')
        else:
            new_subscriber = NewsletterSubscriber(email=email)
            db.session.add(new_subscriber)
            db.session.commit()
            flash('Thanks for subscribing! You will hear from us soon.', 'success')

        return redirect(request.referrer or url_for('home'))

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)