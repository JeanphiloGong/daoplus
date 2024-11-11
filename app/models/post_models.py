# app/models/post_models.py
from app import db  # Import db from the app module

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_flagged = db.Column(db.Boolean, default=False)  # Flag for moderation

    user = db.relationship('User', backref='posts', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    user = db.relationship('User', backref='comments', lazy=True)
    post = db.relationship('Post', backref='comments', lazy=True)
