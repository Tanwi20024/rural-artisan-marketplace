from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(db.Model, UserMixin):
    """
    Shared table for both Customers and Artisans.
    The 'role' field determines which type of user this is.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15))
    address = db.Column(db.String(255))
    role = db.Column(db.String(20), nullable=False)  # 'customer' or 'artisan'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    artisan_profile = db.relationship(
        'ArtisanProfile', backref='user', uselist=False, cascade='all, delete-orphan'
    )
    products = db.relationship('Product', backref='artisan', lazy=True)
    cart_items = db.relationship('Cart', backref='customer', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='customer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_artisan(self):
        return self.role == 'artisan'

    def is_customer(self):
        return self.role == 'customer'

    def __repr__(self):
        return f'<User {self.name} ({self.role})>'


class ArtisanProfile(db.Model):
    """
    Extra profile details specific to artisans only.
    One-to-one relationship with User.
    """
    __tablename__ = 'artisan_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    shop_name = db.Column(db.String(150))
    bio = db.Column(db.Text)
    village = db.Column(db.String(100))
    district = db.Column(db.String(100))
    state = db.Column(db.String(100))
    experience_years = db.Column(db.Integer)
    specialization = db.Column(db.String(150))
    profile_photo = db.Column(db.String(255))

    def __repr__(self):
        return f'<ArtisanProfile {self.shop_name}>'


class Product(db.Model):
    """Products listed by artisans."""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    artisan_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Story / cultural storytelling fields
    story = db.Column(db.Text)
    artisan_message = db.Column(db.Text)
    origin_region = db.Column(db.String(150))
    video_url = db.Column(db.String(255))

    # Relationships
    cart_entries = db.relationship('Cart', backref='product', cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    def __repr__(self):
        return f'<Product {self.name}>'


class Cart(db.Model):
    """Items a customer has added to their cart (not yet ordered)."""
    __tablename__ = 'cart'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Cart customer={self.customer_id} product={self.product_id}>'


class Order(db.Model):
    """
    A placed order. Can contain products from multiple artisans,
    which is why delivery status lives on OrderItem, not here.
    """
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    shipping_address = db.Column(db.String(255), nullable=False)
    payment_method = db.Column(db.String(20), default='Cash on Delivery')
    placed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order #{self.id} by customer={self.customer_id}>'


class OrderItem(db.Model):
    """
    A single product within an order, with its own delivery status.
    Status lives here (not on Order) because each artisan only
    controls the status of their own items within a mixed order.
    """
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    artisan_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Shipped, Out for Delivery, Delivered
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<OrderItem product={self.product_id} status={self.status}>'


class ReturnRequest(db.Model):
    """A customer's request to return a delivered order item."""
    __tablename__ = 'return_requests'

    id = db.Column(db.Integer, primary_key=True)
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_items.id'), nullable=False, unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='Requested')  # Requested, Approved, Rejected
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)

    order_item = db.relationship('OrderItem', backref=db.backref('return_request', uselist=False))

    def __repr__(self):
        return f'<ReturnRequest order_item={self.order_item_id} status={self.status}>'


class Review(db.Model):
    """A customer's rating and review of a product they've purchased."""
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    comment = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref='reviews')
    customer = db.relationship('User', backref='reviews')

    __table_args__ = (
        db.UniqueConstraint('product_id', 'customer_id', name='unique_review_per_customer_product'),
    )

    def __repr__(self):
        return f'<Review product={self.product_id} rating={self.rating}>'

class Wishlist(db.Model):
    """Products a customer has saved to their wishlist."""
    __tablename__ = 'wishlist'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship('User', backref='wishlist_items')
    product = db.relationship('Product', backref=db.backref('wishlisted_by', cascade='all, delete-orphan'))

    __table_args__ = (
        db.UniqueConstraint('customer_id', 'product_id', name='unique_wishlist_item'),
    )

    def __repr__(self):
        return f'<Wishlist customer={self.customer_id} product={self.product_id}>'

class NewsletterSubscriber(db.Model):
    """Email addresses collected from the newsletter signup form."""
    __tablename__ = 'newsletter_subscribers'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<NewsletterSubscriber {self.email}>'

class Notification(db.Model):
    """In-app notifications for a user (order updates, etc.)."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')

    def __repr__(self):
        return f'<Notification user={self.user_id} read={self.is_read}>'