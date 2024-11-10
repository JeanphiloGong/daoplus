# app/blueprints/content/__init__.py
from flask import Blueprint

content = Blueprint('content', __name__)

from . import routes  # Import routes for the blueprint
