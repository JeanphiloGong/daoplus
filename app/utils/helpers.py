from app.models.notification_models import Notification
from app import db

# Function to create notifications for likes and follows
def create_notification(user_id, action, target_id, target_type):
    notification = Notification(
        user_id=user_id,
        action=action,
        target_id=target_id,
        target_type=target_type
    )
    db.session.add(notification)
    db.session.commit()

# Notify user when they get a like
def notify_like(user_id, post_id):
    create_notification(user_id, 'liked', post_id, 'post')

# Notify user when they get a new follower
def notify_follow(user_id, follower_id):
    create_notification(user_id, 'followed', follower_id, 'user')
