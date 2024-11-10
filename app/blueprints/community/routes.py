from flask import Blueprint

community = Blueprint('community', __name__)

@community.route('/login')
def login():
    return 'Login Page'

@community.route('/signup')
def signup():
    return 'Sign-up Page'
