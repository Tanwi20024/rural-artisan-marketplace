import os
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
    """Check if the uploaded file has an allowed image extension."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']


def save_product_image(file):
    """
    Save an uploaded product image to static/uploads with a safe filename.
    Returns the filename to store in the database, or None if invalid.
    """
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # Prefix with a timestamp-like unique value to avoid filename clashes
        import uuid
        unique_filename = f"{uuid.uuid4().hex}_{filename}"

        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        return unique_filename

    return None

def create_notification(user_id, message, link=None):
    """Helper to create an in-app notification for a user."""
    from extensions import db
    from models import Notification

    notification = Notification(user_id=user_id, message=message, link=link)
    db.session.add(notification)
    db.session.commit()