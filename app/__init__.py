from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os


# Initialize SQLAlchemy and LoginManager
db = SQLAlchemy()
login_manager = LoginManager()
# Initialize the Migrate extension
migrate = Migrate()



def create_app():
    app = Flask(__name__, template_folder='templates')  # Adjust the path as needed
    # print(f"Template folder set to: {os.path.abspath(app.template_folder)}")  # Log the absolute path to the template folder
    print(f"Template folder path: {os.path.abspath(app.template_folder)}")

    # Configurations
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure, random key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://jeanphilo:Jeanphilo..@localhost/daoplus'  # Replace with your database URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional, to disable modification tracking
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Set the login view (redirect to login page if not authenticated)
    login_manager.login_view = 'auth.login'  # Assuming your blueprint for auth is named 'auth'
    
    # Register blueprints
    from app.blueprints.auth.routes import auth as auth_blueprint
    from app.blueprints.community.routes import community as community_blueprint
    from app.blueprints.content.routes import content as content_blueprint
    print("Registering community blueprint...")
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(community_blueprint, url_prefix='/community')  # No url_prefix, unless needed
    app.register_blueprint(content_blueprint, url_prefix='/content')
    return app

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from .models.user_models import User
    return User.query.get(int(user_id))  # Fetch the user from the database by ID
