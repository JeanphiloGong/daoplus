# Import flask package
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user

# Import app models
from app.models.user_models import   User
from app.models.like_models import Like
from app.models.follow_models import  Follow
from app.models.post_models import Post
from app.models.comment_models import  Comment
from app.models.notification_models import Notification
from app.blueprints.community.forms import PostForm, CommentForm
from app.services.reward_service import add_reward_points, get_user_rewards

community = Blueprint('community', __name__)

# Home route to display all posts
@community.route('/')
def home():
    print("Rendering index.html")
    # Fetch posts from Neo4j
    posts = Post.get_all_posts(current_app.neo4j_service)
    return render_template('community/index.html', posts=posts)

# Route for login (placeholder)
@community.route('/login')
def login():
    return 'Login Page'

# Route for signup (placeholder)
@community.route('/signup')
def signup():
    return 'Sign-up Page'

# Route for displaying user profile
@community.route('/profile')
@login_required
def profile():
    # Get rewards for the current user
    rewards = get_user_rewards(current_user)  
    # Fetch notifications for the user
    notifications = Notification.get_notifications_for_user(current_app.neo4j_service, current_user.user_id)
    return render_template('community/profile.html', rewards=rewards, notifications=notifications)

# Route for displaying all posts
@community.route('/posts')
def post_list():
    # Fetch posts from Neo4j
    posts = Post.get_all_posts(current_app.neo4j_service)
    return render_template('community/post_list.html', posts=posts)

# Route for displaying a single post and its comments
@community.route('/posts/<int:post_id>')
def post_detail(post_id):
    # Get a specific post from Neo4j
    post = Post.get_post_by_id(current_app.neo4j_service, post_id)
    if not post:
        flash('Post not found.', 'danger')
        return redirect(url_for('community.post_list'))
    
    comments = Comment.get_comments_by_post_id(current_app.neo4j_service, post_id)
    form = CommentForm()
    return render_template('community/post_detail.html', post=post, comments=comments, form=form)

# Route for creating a new post
@community.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        # Create a new post in Neo4j
        post = Post.create_post(current_app.neo4j_service, title=form.title.data, content=form.content.data, user_id=current_user.user_id)
        if post:
            # Add reward points after the post is created
            add_reward_points(current_user, 10)
            flash('Your post has been created!', 'success')
            return redirect(url_for('community.post_list'))
        else:
            flash('Failed to create post.', 'danger')
    return render_template('community/new_post.html', form=form)

# Route for editing an existing post
@community.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.get_post_by_id(current_app.neo4j_service, post_id)
    if not post:
        flash('Post not found.', 'danger')
        return redirect(url_for('community.post_list'))
    
    # Check if the current user is the author of the post
    if post.user_id != current_user.user_id:
        flash('You are not authorized to edit this post.', 'danger')
        return redirect(url_for('community.post_list'))
    
    form = PostForm(obj=post)
    
    if form.validate_on_submit():
        # Update the post in Neo4j
        Post.update_post(current_app.neo4j_service, post_id, title=form.title.data, content=form.content.data)
        flash('Your post has been updated!', 'success')
        return redirect(url_for('community.post_detail', post_id=post.post_id))
    
    return render_template('community/edit_post.html', post=post, form=form)

# Route for deleting a post
@community.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.get_post_by_id(current_app.neo4j_service, post_id)
    if not post:
        flash('Post not found.', 'danger')
        return redirect(url_for('community.post_list'))
    
    # Check if the current user is the author of the post
    if post.user_id != current_user.user_id:
        flash('You are not authorized to delete this post.', 'danger')
        return redirect(url_for('community.post_list'))
    
    # Delete the post from Neo4j
    Post.delete_post(current_app.neo4j_service, post_id)
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('community.post_list'))

# Like Post Route
@community.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.get_post_by_id(current_app.neo4j_service, post_id)
    if not post:
        flash('Post not found.', 'danger')
        return redirect(url_for('community.post_list'))
    
    # Check if the user already liked the post
    if not Like.is_liked(current_app.neo4j_service, current_user.user_id, post_id):
        # Create a new like relationship in Neo4j
        Like.like_post(current_app.neo4j_service, current_user.user_id, post_id)
        # Add reward points for liking the post
        add_reward_points(current_user, 5)
        flash('Post liked!', 'success')
    else:
        flash('You have already liked this post.', 'warning')
    
    return redirect(url_for('community.post_detail', post_id=post.post_id))

# Route for creating a new comment on a post
@community.route('/posts/<int:post_id>/comment', methods=['POST'])
@login_required
def new_comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        # Create a new comment in Neo4j
        comment = Comment.create_comment(current_app.neo4j_service, content=form.content.data, user_id=current_user.user_id, post_id=post_id)
        if comment:
            # Add reward points for commenting on a post
            add_reward_points(current_user, 3)
            flash('Your comment has been added!', 'success')
            return redirect(url_for('community.post_detail', post_id=post_id))
        else:
            flash('Failed to add comment.', 'danger')
    return render_template('community/post_detail.html', post=Post.get_post_by_id(current_app.neo4j_service, post_id), form=form)

# Route for deleting a comment
@community.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.get_comment_by_id(current_app.neo4j_service, comment_id)
    if not comment:
        flash('Comment not found.', 'danger')
        return redirect(url_for('community.post_list'))
    
    # Check if the current user is the author of the comment
    if comment.user_id != current_user.user_id:
        flash('You are not authorized to delete this comment.', 'danger')
        return redirect(url_for('community.post_detail', post_id=comment.post_id))
    
    # Delete the comment from Neo4j
    Comment.delete_comment(current_app.neo4j_service, comment_id)
    flash('Your comment has been deleted!', 'success')
    return redirect(url_for('community.post_detail', post_id=comment.post_id))

# Route for flagging a post
@community.route('/posts/<int:post_id>/flag', methods=['POST'])
@login_required
def flag_post(post_id):
    post = Post.get_post_by_id(current_app.neo4j_service, post_id)
    if not post:
        flash('Post not found.', 'danger')
        return redirect(url_for('community.post_list'))
    
    if post.is_flagged:
        flash('This post has already been flagged.', 'warning')
        return redirect(url_for('community.post_detail', post_id=post.post_id))
    
    # Flag the post
    Post.flag_post(current_app.neo4j_service, post_id)
    flash('The post has been flagged for review.', 'success')
    return redirect(url_for('community.post_detail', post_id=post.post_id))

# Route for admin to view all flagged posts
@community.route('/admin/flagged_posts', methods=['GET'])
@login_required
def view_flagged_posts():
    if not current_user.is_admin:
        flash('You are not authorized to view flagged posts.', 'danger')
        return redirect(url_for('community.post_list'))
    
    flagged_posts = Post.get_flagged_posts(current_app.neo4j_service)
    return render_template('community/flagged_posts.html', posts=flagged_posts)

# Route for admin to moderate a flagged post (approve or delete)
@community.route('/admin/moderate_post/<int:post_id>', methods=['POST'])
@login_required
def moderate_flagged_post(post_id):
    if not current_user.is_admin:
        flash('You are not authorized to moderate flagged posts.', 'danger')
        return redirect(url_for('community.post_list'))
    
    action = request.form.get('action')  # "approve" or "delete"
    
    if action == 'approve':
        Post.unflag_post(current_app.neo4j_service, post_id)
        flash('The post has been approved and unflagged.', 'success')
    elif action == 'delete':
        Post.delete_post(current_app.neo4j_service, post_id)
        flash('The flagged post has been deleted.', 'danger')
    else:
        flash('Invalid action.', 'danger')
    
    return redirect(url_for('community.view_flagged_posts'))

# Follow User Route
@community.route('/follow_user/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    user_to_follow = User.get_user_by_id(current_app.neo4j_service, user_id)
    if not user_to_follow:
        flash('User not found.', 'danger')
        return redirect(url_for('community.profile'))
    
    # Check if the user is already following the target user
    if not Follow.is_following(current_app.neo4j_service, current_user.user_id, user_id):
        # Create a new follow relationship in Neo4j
        Follow.follow_user(current_app.neo4j_service, current_user.user_id, user_id)
        # Add reward points for following a user
        add_reward_points(current_user, 2)
        flash(f'You are now following {user_to_follow.username}!', 'success')
    else:
        flash(f'You are already following {user_to_follow.username}.', 'warning')
    
    return redirect(url_for('community.profile'))

# Search Route
@community.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('q', '')  # Get the search query from the URL parameter
    if query:
        # Perform search by title or content using Neo4j's Cypher query
        posts = Post.search_posts(current_app.neo4j_service, query)
    else:
        posts = []  # Return empty if no query
    
    return render_template('community/search.html', posts=posts, query=query)
