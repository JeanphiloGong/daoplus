# app/blueprints/community/__init__.py
from flask import Blueprint

community = Blueprint('community', __name__)

from . import routes  # Import routes for the blueprint
