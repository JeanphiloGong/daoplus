# Importing necessary modules from the app and werkzeug
from app import db  # Importing the database instance from the app module
from werkzeug.security import generate_password_hash, check_password_hash  # Functions for password hashing

# Define the User class as a model for the 'users' table in the database
class User(db.Model):
    # Defining the columns in the 'users' table
    id = db.Column(db.Integer, primary_key=True)  # Primary key column to uniquely identify each user
    username = db.Column(db.String(120), unique=True, nullable=False)  # Username must be unique and cannot be null
    email = db.Column(db.String(120), unique=True, nullable=False)  # Email must be unique and cannot be null
    password_hash = db.Column(db.String(128))  # Stores the hashed password, not the plain password

    # Method to set the user's password (by hashing it before storing)
    def set_password(self, password):
        # Use werkzeug's generate_password_hash function to securely hash the password
        self.password_hash = generate_password_hash(password)

    # Method to check if a provided password matches the stored hash
    def check_password(self, password):
        # Use werkzeug's check_password_hash function to compare the provided password with the stored hash
        return check_password_hash(self.password_hash, password)

    # Represent the user object as a string (optional but helpful for debugging)
    def __repr__(self):
        return f"<User {self.username}>"