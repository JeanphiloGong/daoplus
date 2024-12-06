from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy.orm import aliased
from app import db
from app.models.user_models import Like, Follow, User
from app.models.post_models import Post, Comment
from app.blueprints.community.forms import PostForm, CommentForm  # Assuming you have WTForms for validation
from app.services.reward_service import add_reward_points, get_user_rewards


community = Blueprint('community', __name__)


# Home route to display all posts
@community.route('/')
def home():
    print("Rendering index.html")
    # try:
    #    return render_template('community/index.html')
    # except TemplateNotFound as e:
    #    return f"Template not found: {str(e)}"
    posts = Post.query.all()  # Retrieve all posts from the database
    return render_template('community/index.html', posts=posts)


# Route for login (just a placeholder for now)
@community.route('/login')
def login():
    return 'Login Page'

# Route for signup (just a placeholder for now)
@community.route('/signup')
def signup():
    return 'Sign-up Page'

# Route for displaying user profile
@community.route('/profile')
@login_required
def profile():
    rewards = get_user_rewards(current_user)  # Get the total reward points for the user
    return render_template('community/profile.html', rewards=rewards)

# Route for displaying all posts
@community.route('/posts')
def post_list():
    posts = Post.query.all()  # Get all posts from the database
    return render_template('community/post_list.html', posts=posts)

# Route for displaying a single post and its comments
@community.route('/posts/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)  # Get a specific post by ID
    comments = Comment.query.filter_by(post_id=post.id).all()  # Get comments for that post
    form = CommentForm()
    return render_template('community/post_detail.html', post=post, comments=comments,form=form)

# Route for creating a new post
@community.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()  # Use the PostForm here

    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()

        # Add reward points after the post is created
        add_reward_points(current_user, 10)  # Award 10 points for creating a post

        flash('Your post has been created!', 'success')
        return redirect(url_for('community.post_list'))
    
    return render_template('community/new_post.html', form=form)


# Route for editing an existing post
@community.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    comment_form = CommentForm()
    post_form = PostForm()
    
    # Check if the current user is the author of the post
    if post.user_id != current_user.id:
        flash('You are not authorized to edit this post.', 'danger')
        return redirect(url_for('community.post_list'))
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('community.post_detail', post_id=post.id, form=comment_form))
    
    # For GET request, populate the form with the existing post data
    post_form.title.data = post.title
    post_form.content.data = post.content
    return render_template('community/edit_post.html', post=post, form=post_form)

# Route for deleting a post
@community.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Check if the current user is the author of the post
    if post.user_id != current_user.id:
        flash('You are not authorized to delete this post.', 'danger')
        return redirect(url_for('community.post_list'))
    
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('community.post_list'))

# Like Post Route
@community.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Check if the user already liked the post
    existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if not existing_like:
        # Create a new like
        like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(like)
        db.session.commit()

        # Add reward points for liking the post
        add_reward_points(current_user, 5)  # Award 5 points for liking a post

        flash('Post liked!', 'success')
    else:
        flash('You have already liked this post.', 'warning')
    
    return redirect(url_for('community.view_post', post_id=post.id))


# Route for creating a new comment on a post
@community.route('/posts/<int:post_id>/comment', methods=['POST'])
@login_required
def new_comment(post_id):
    form = CommentForm()  # Use the CommentForm here
    
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, user_id=current_user.id, post_id=post_id)
        db.session.add(comment)
        db.session.commit()

        # Add reward points for commenting on a post
        add_reward_points(current_user, 3)  # Award 3 points for posting a comment

        flash('Your comment has been added!', 'success')
        return redirect(url_for('community.post_detail', post_id=post_id))
    
    return render_template('community/post_detail.html', post=Post.query.get(post_id), form=form)



# Route for deleting a comment
@community.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if the current user is the author of the comment
    if comment.user_id != current_user.id:
        flash('You are not authorized to delete this comment.', 'danger')
        return redirect(url_for('community.post_detail', post_id=comment.post_id))
    
    db.session.delete(comment)
    db.session.commit()
    flash('Your comment has been deleted!', 'success')
    return redirect(url_for('community.post_detail', post_id=comment.post_id))

# Route for flagging a post
@community.route('/posts/<int:post_id>/flag', methods=['POST'])
@login_required
def flag_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Flag the post if it has not been flagged already
    if post.is_flagged:
        flash('This post has already been flagged.', 'warning')
        return redirect(url_for('community.post_detail', post_id=post.id))
    
    post.is_flagged = True
    db.session.commit()
    
    flash('The post has been flagged for review.', 'success')
    return redirect(url_for('community.post_detail', post_id=post.id))

# Route for admin to view all flagged posts
@community.route('/admin/flagged_posts', methods=['GET'])
@login_required
def view_flagged_posts():
    if not current_user.is_admin:
        flash('You are not authorized to view flagged posts.', 'danger')
        return redirect(url_for('community.post_list'))
    
    flagged_posts = Post.query.filter_by(is_flagged=True).all()
    return render_template('community/flagged_posts.html', posts=flagged_posts)

# Route for admin to moderate a flagged post (approve or delete)
@community.route('/admin/moderate_post/<int:post_id>', methods=['POST'])
@login_required
def moderate_flagged_post(post_id):
    if not current_user.is_admin:
        flash('You are not authorized to moderate flagged posts.', 'danger')
        return redirect(url_for('community.post_list'))
    
    post = Post.query.get_or_404(post_id)
    
    action = request.form.get('action')  # "approve" or "delete"
    
    if action == 'approve':
        post.is_flagged = False
        db.session.commit()
        flash('The post has been approved and unflagged.', 'success')
    elif action == 'delete':
        db.session.delete(post)
        db.session.commit()
        flash('The flagged post has been deleted.', 'danger')
    
    return redirect(url_for('community.view_flagged_posts'))


# Follow User Route
@community.route('/follow_user/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    user_to_follow = User.query.get_or_404(user_id)
    
    # Check if the user is already following the target user
    existing_follow = Follow.query.filter_by(follower_id=current_user.id, followed_id=user_id).first()
    
    if not existing_follow:
        # Create a new follow
        follow = Follow(follower_id=current_user.id, followed_id=user_to_follow.id)
        db.session.add(follow)
        db.session.commit()

        # Add reward points for following a user
        add_reward_points(current_user, 2)  # Award 2 points for following a user

        flash(f'You are now following {user_to_follow.username}!', 'success')
    else:
        flash(f'You are already following {user_to_follow.username}.', 'warning')
    
    return redirect(url_for('community.profile', user_id=user_to_follow.id))

@community.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('q', '')  # Get the search query from the URL parameter

    if query:
        # Perform search by title or content
        posts = Post.query.filter(
            (Post.title.ilike(f'%{query}%')) | (Post.content.ilike(f'%{query}%'))
        ).all()
    else:
        posts = []  # No query, return an empty list or you could return all posts

    return render_template('community/search.html', posts=posts, query=query)
