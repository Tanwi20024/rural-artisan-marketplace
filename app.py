from flask import Flask, render_template
from config import Config


def create_app():
    """Application factory - creates and configures the Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.route('/')
    def home():
        return render_template('base.html')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)