from app import create_app
from flask_migrate import Migrate
from app import db

# Initialize the app
app = create_app()

# Set up database migration
migrate = Migrate(app, db)

if __name__ == "__main__":
    # Run the app in debug mode for development
    app.run(debug=True)
