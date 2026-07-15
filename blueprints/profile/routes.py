from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from blueprints.profile import profile_bp
from extensions import db
from models import ArtisanProfile
from forms import ProfileForm
from utils import save_product_image

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def view_profile():
    """View and edit the logged-in user's profile."""
    form = ProfileForm()

    # For artisans, load their existing ArtisanProfile (create one if it doesn't exist yet)
    artisan_profile = None
    if current_user.is_artisan():
        artisan_profile = current_user.artisan_profile
        if artisan_profile is None:
            artisan_profile = ArtisanProfile(user_id=current_user.id)
            db.session.add(artisan_profile)
            db.session.commit()

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data

        if current_user.is_artisan():
            artisan_profile.shop_name = form.shop_name.data
            artisan_profile.bio = form.bio.data
            artisan_profile.village = form.village.data
            artisan_profile.district = form.district.data
            artisan_profile.state = form.state.data

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.view_profile'))

    # Pre-fill the form with existing data on GET request
    if not form.is_submitted():
        form.name.data = current_user.name
        form.phone.data = current_user.phone
        form.address.data = current_user.address

        if current_user.is_artisan():
            form.shop_name.data = artisan_profile.shop_name
            form.bio.data = artisan_profile.bio
            form.village.data = artisan_profile.village
            form.district.data = artisan_profile.district
            form.state.data = artisan_profile.state

    return render_template('profile/profile.html', form=form)