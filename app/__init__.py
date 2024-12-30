import os
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
from app.services.neo4j_service import Neo4jService

# Initialize Flask extensions
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='templates')
    print(f"Template folder path: {os.path.abspath(app.template_folder)}")
    
    # Load configurations
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change to a secure key
    # You can load other configurations here or from a config file
    # For example:
    # app.config.from_object('config.Config')

    # Initialize Neo4jService
    neo4j_service = Neo4jService()
    neo4j_service.init_app(app)
    
    # Initialize other extensions
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Adjust as per your blueprint

    # Register blueprints
    from app.blueprints.auth.routes import auth as auth_blueprint
    from app.blueprints.community.routes import community as community_blueprint
    from app.blueprints.content.routes import content as content_blueprint

    print("Registering blueprints...")
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(community_blueprint, url_prefix='/community')
    app.register_blueprint(content_blueprint, url_prefix='/content')

    return app

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from .models.user_models import User
    return User.get_user_by_id(current_app.neo4j_service, user_id)  # Adjusted to use Neo4j
