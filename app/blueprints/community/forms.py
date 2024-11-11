# app/blueprints/community/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
