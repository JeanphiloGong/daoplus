# Importing necessary modules from the app and werkzeug
from app import db  # Importing the database instance from the app module
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash  # Functions for password hashing

# Define the User class as a model for the 'users' table in the database
class User(db.Model):
    # Defining the columns in the 'users' table
    id = db.Column(db.Integer, primary_key=True)  # Primary key column to uniquely identify each user
    username = db.Column(db.String(120), unique=True, nullable=False)  # Username must be unique and cannot be null
    email = db.Column(db.String(120), unique=True, nullable=False)  # Email must be unique and cannot be null
    password_hash = db.Column(db.String(128))  # Stores the hashed password, not the plain password

    # Relationship with Reward model
    rewards = db.relationship('Reward', backref='reward_owner', lazy=True)

    # Method to set the user's password (by hashing it before storing)
    def set_password(self, password):
        # Use werkzeug's generate_password_hash function to securely hash the password
        self.password_hash = generate_password_hash(password)

    # Method to check if a provided password matches the stored hash
    def check_password(self, password):
        # Use werkzeug's check_password_hash function to compare the provided password with the stored hash
        return check_password_hash(self.password_hash, password)

    # Flask-Login required methods
    def is_authenticated(self):
        # This is required by Flask-Login, it should return True if the user is authenticated
        return True  # You can implement your own logic here if needed

    def is_active(self):
        # This is required by Flask-Login, it should return True if the user is active
        return True  # You can implement your own logic here if needed

    def is_anonymous(self):
        # Return False, as this is a typical non-anonymous user
        return False

    def get_id(self):
        # This returns the user's ID for Flask-Login to manage sessions
        return str(self.id)  # Flask-Login expects this to be a string
    
    # Represent the user object as a string (optional but helpful for debugging)
    def __repr__(self):
        return f"<User {self.username}>"
    

# Like Model (User liking a post)
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='likes', lazy=True)
    post = db.relationship('Post', backref='likes', lazy=True)

# Follow Model (User following another user)
class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    follower = db.relationship('User', foreign_keys=[follower_id], backref='following', lazy=True)
    followed = db.relationship('User', foreign_keys=[followed_id], backref='followers', lazy=True)

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points = db.Column(db.Integer, default=0)

    user = db.relationship('User', backref=db.backref('user_rewards', lazy=True))

    def __repr__(self):
        return f"<Reward(user_id={self.user_id}, points={self.points})>"


