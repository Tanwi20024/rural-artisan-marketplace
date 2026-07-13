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
    login_manager.login_view = 'auth.login'  # we'll create this blueprint in Step 3
    login_manager.login_message_category = 'info'

    # Import models so Flask-Migrate can detect them
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def home():
        return render_template('base.html')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)