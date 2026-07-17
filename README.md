# 🧺 Rural Artisan Marketplace

Live Link = https://rural-artisan-marketplace.onrender.com

A full-stack web application connecting rural artisans across India directly with customers, eliminating middlemen and promoting traditional handicrafts.

Built as a B.Tech final-year portfolio project.

## Features

**Customers can:**
- Register and log in
- Browse, search, and filter products by category
- View detailed product pages
- Add products to cart and manage quantities
- Checkout with Cash on Delivery
- View order history and track delivery status
- Manage their profile

**Artisans can:**
- Register and log in
- Add, edit, and delete their products with image uploads
- View and manage received orders
- Mark orders as delivered
- Manage their profile and shop details

## Tech Stack

- **Backend:** Python, Flask, Flask-Login, Flask-WTF
- **Database:** MySQL with SQLAlchemy ORM, Flask-Migrate for schema migrations
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Image Uploads:** Local file storage

## Project Structure

rural-artisan-marketplace/
├── app.py                  # Application factory
├── config.py                # Configuration
├── extensions.py            # Flask extensions (db, login_manager, migrate)
├── models.py                 # SQLAlchemy models
├── forms.py                  # Flask-WTF forms
├── utils.py                  # Image upload helpers
├── blueprints/                # Feature modules (auth, products, cart, orders, profile)
├── templates/                 # Jinja2 templates
├── static/                    # CSS, JS, images, uploads
└── migrations/                 # Database migration history

## Database Schema

- **User** — shared table for customers and artisans (role-based)
- **ArtisanProfile** — extended profile info for artisans
- **Product** — items listed by artisans
- **Cart** — items a customer has added but not yet ordered
- **Order** — placed orders (Cash on Delivery)
- **OrderItem** — individual products within an order, with per-artisan delivery status

## Setup Instructions

1. Clone the repository
2. Create a virtual environment: `python3 -m venv venv`
3. Activate it: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a MySQL database: `CREATE DATABASE rural_artisan_db;`
6. Create a `.env` file with your database credentials (see `.env.example` if provided)
7. Run migrations: `flask db upgrade`
8. Start the app: `python app.py`
9. Visit `http://127.0.0.1:5000`

## Author

Built by Tanwi Srivastava as a B.Tech final-year project.
