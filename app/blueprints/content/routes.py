from flask import Blueprint

content = Blueprint('content', __name__)

@content.route('/login')
def login():
    return 'Login Page'

@content.route('/signup')
def signup():
    return 'Sign-up Page'
