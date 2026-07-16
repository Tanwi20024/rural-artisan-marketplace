from flask import Flask, render_template
from config import Config
from extensions import db, login_manager, migrate


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
        from models import Product

        recently_viewed_ids = session.get('recently_viewed', [])
        recently_viewed_products = []
        if recently_viewed_ids:
            products_by_id = {p.id: p for p in Product.query.filter(Product.id.in_(recently_viewed_ids)).all()}
            recently_viewed_products = [products_by_id[pid] for pid in recently_viewed_ids if pid in products_by_id]

        return render_template('home.html', recently_viewed_products=recently_viewed_products)

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/contact')
    def contact():
        return render_template('contact.html')

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


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)