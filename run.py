from app import create_app
from flask_migrate import Migrate
from app import db
# At the start of your run.py
from jinja2 import TemplateNotFound

# Initialize the app
app = create_app()

# Set up database migration
migrate = Migrate(app, db)
  
if __name__ == '__main__':
    app.run(debug=True, port=5002)
