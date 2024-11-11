# app/services/reward_service.py

from app.models.user_models import Reward
from app import db

def add_reward_points(user, points):
    """Add reward points to a user."""
    reward = Reward.query.filter_by(user_id=user.id).first()
    if reward:
        reward.points += points
    else:
        reward = Reward(user_id=user.id, points=points)
        db.session.add(reward)
    db.session.commit()

def deduct_reward_points(user, points):
    """Deduct reward points from a user."""
    reward = Reward.query.filter_by(user_id=user.id).first()
    if reward and reward.points >= points:
        reward.points -= points
        db.session.commit()
    else:
        return False  # Insufficient points
    return True

def get_user_rewards(user):
    """Retrieve the user's total reward points."""
    reward = Reward.query.filter_by(user_id=user.id).first()
    return reward.points if reward else 0
