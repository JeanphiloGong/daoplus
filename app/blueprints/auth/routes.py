from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from app.models.user_models import User
from flask_login import login_user, login_required, logout_user
from app.services.neo4j_service import Neo4jService

auth = Blueprint('auth', __name__)

# Route for the registration page
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        # Check if passwords match
        if password != password_confirm:
            flash('Passwords must match!', 'danger')
            return redirect(url_for('auth.register'))

        # Check if username or email already exists
        existing_user = User.get_user_by_username(current_app.neo4j_service, username)
        if existing_user:
            flash('Username already exists, please choose a different one.', 'danger')
            return redirect(url_for('auth.register'))

        existing_email = User.get_user_by_email(current_app.neo4j_service, email)
        if existing_email:
            flash('Email already registered, please use a different one.', 'danger')
            return redirect(url_for('auth.register'))

        # Create a new user and set the password
        user = User(username=username, email=email)
        user.set_password(password)

        # Add the user to Neo4j and commit
        current_app.neo4j_service.add_user(user)

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# Route for the login page
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Look for the user by username
        user = User.get_user_by_username(current_app.neo4j_service, username)

        # Check if user exists and the password is correct
        if user and user.check_password(password):
            # Log the user in
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('community.home'))  # Redirect to the homepage or dashboard

        # If login fails
        flash('Invalid username or password, please try again.', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('auth/login.html')


# Route for logging out
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
