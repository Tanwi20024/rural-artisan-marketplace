from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, SubmitField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange


class RegisterForm(FlaskForm):
    """Registration form used by both Customers and Artisans."""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Length(max=15)])
    address = StringField('Address', validators=[Length(max=255)])
    role = SelectField(
        'Register as',
        choices=[('customer', 'Customer'), ('artisan', 'Artisan')],
        validators=[DataRequired()]
    )
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """Login form used by both Customers and Artisans."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ProductForm(FlaskForm):
    """Form used by artisans to add or edit a product."""
    name = StringField('Product Name', validators=[DataRequired(), Length(min=2, max=150)])
    category = SelectField(
        'Category',
        choices=[
            ('Pottery', 'Pottery'),
            ('Handloom', 'Handloom'),
            ('Wooden Crafts', 'Wooden Crafts'),
            ('Bamboo Crafts', 'Bamboo Crafts'),
            ('Paintings', 'Paintings'),
            ('Jewelry', 'Jewelry'),
        ],
        validators=[DataRequired()]
    )
    description = TextAreaField('Description', validators=[Length(max=1000)])
    price = DecimalField('Price (₹)', validators=[DataRequired(), NumberRange(min=1)])
    image = FileField('Product Image', validators=[FileAllowed(['png', 'jpg', 'jpeg'], 'Images only!')])

    story = TextAreaField('The Story Behind This Craft', validators=[Length(max=2000)])
    artisan_message = TextAreaField('A Message From You (Optional)', validators=[Length(max=1000)])
    origin_region = StringField('Region of Origin', validators=[Length(max=150)])
    video_url = StringField('YouTube Video URL (Optional)', validators=[Length(max=255)])

    submit = SubmitField('Save Product')
    
class ProfileForm(FlaskForm):
    """Profile form for customers and artisans."""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[Length(max=15)])
    address = StringField('Address', validators=[Length(max=255)])
    shop_name = StringField('Shop Name', validators=[Length(max=150)])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    village = StringField('Village', validators=[Length(max=100)])
    district = StringField('District', validators=[Length(max=100)])
    state = StringField('State', validators=[Length(max=100)])
    submit = SubmitField('Save Changes')
    phone = StringField('Phone Number', validators=[Length(max=15)])
    address = StringField('Address', validators=[Length(max=255)])

    # Artisan-only fields (left blank/unused for customers)
    shop_name = StringField('Shop Name', validators=[Length(max=150)])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    village = StringField('Village', validators=[Length(max=100)])
    district = StringField('District', validators=[Length(max=100)])
    state = StringField('State', validators=[Length(max=100)])

    submit = SubmitField('Save Changes')

class ReturnRequestForm(FlaskForm):
    """Form for a customer to request a return."""
    reason = TextAreaField('Reason for Return', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Submit Return Request')

class ReviewForm(FlaskForm):
    """Form for a customer to leave a product review."""
    rating = SelectField(
        'Rating',
        choices=[('5', '5 - Excellent'), ('4', '4 - Good'), ('3', '3 - Average'), ('2', '2 - Poor'), ('1', '1 - Very Poor')],
        validators=[DataRequired()]
    )
    comment = TextAreaField('Comment', validators=[Length(max=500)])
    submit = SubmitField('Submit Review')