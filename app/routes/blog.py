from flask import (Blueprint, render_template,
                   redirect, url_for, flash,
                   request, abort, current_app,
                   jsonify, )
from flask_login import login_required, current_user
from app.models import BlogPost, User, Like, Comment, CommentVote
from app import db
from sqlalchemy import or_
import os
from werkzeug.utils import secure_filename
import bleach
from app.forms import (PostForm, AvatarUploadForm,
                       ChangeEmailForm, ChangePasswordForm,
                       CommentForm, ReplyForm)
from werkzeug.security import check_password_hash

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'recent')

    query = BlogPost.query

    if search:
        query = query.filter(or_(BlogPost.title.contains(search), BlogPost.content.contains(search)))

    if sort == 'likes':
        query = query.outerjoin(Like).group_by(BlogPost.id).order_by(db.func.count(Like.id).desc())
    else:  # default to recent
        query = query.order_by(BlogPost.timestamp.desc())

    posts = query.paginate(page=page, per_page=10, error_out=False)
    return render_template('index.html', title='Home', posts=posts, search=search, sort=sort)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        content = bleach.clean(form.content.data, tags=['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'em', 'u', 'a', 'img'], attributes={'a': ['href'], 'img': ['src', 'alt']})
        post = BlogPost(title=form.title.data, content=content, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created.', 'success')
        return redirect(url_for('blog.index'))
    return render_template('create_post.html', title='Create Post', form=form)

@bp.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = BlogPost.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=post, user=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.', 'success')
        return redirect(url_for('blog.post', id=post.id))
    page = request.args.get('page', 1, type=int)
    comments = post.comments.filter_by(parent=None).order_by(Comment.timestamp.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('post.html', title=post.title, post=post, form=form, comments=comments)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = BlogPost.query.get_or_404(id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = bleach.clean(form.content.data, tags=['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'em', 'u', 'a', 'img'], attributes={'a': ['href'], 'img': ['src', 'alt']})
        db.session.commit()
        flash('Your post has been updated.', 'success')
        return redirect(url_for('blog.post', id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('edit_post.html', title='Edit Post', form=form, post=post)

@bp.route('/user/<username>')
@login_required
def user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.filter_by(author=user).order_by(BlogPost.timestamp.desc()).paginate(page=page, per_page=10,
                                                                                               error_out=False)
    return render_template('user_posts.html', user=user, posts=posts)


@bp.route('/like/<int:post_id>/<action>')
@login_required
def like_action(post_id, action):
    post = BlogPost.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.likes.append(Like(post=post))
        db.session.commit()
    if action == 'unlike':
        like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
        db.session.delete(like)
        db.session.commit()
    return redirect(request.referrer)

@bp.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return {'location': url_for('static', filename='uploads/' + filename)}
    return 'File type not allowed', 400

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile/profile.html', user=current_user)

@bp.route('/profile/avatar', methods=['GET', 'POST'])
@login_required
def change_avatar():
    form = AvatarUploadForm()
    if form.validate_on_submit():
        if form.avatar.data:
            filename = secure_filename(form.avatar.data.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.avatar.data.save(file_path)
            current_user.avatar = filename
            db.session.commit()
            flash('Your avatar has been updated!', 'success')
        return redirect(url_for('blog.profile'))
    return render_template('profile/change_avatar.html', form=form)

@bp.route('/profile/password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('blog.profile'))
        else:
            flash('Invalid old password.', 'danger')
    return render_template('profile/change_password.html', form=form)

@bp.route('/profile/email', methods=['GET', 'POST'])
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.check_password(form.password.data):
            current_user.email = form.new_email.data
            db.session.commit()
            flash('Your email has been updated!', 'success')
            return redirect(url_for('blog.profile'))
        else:
            flash('Invalid password.', 'danger')
    return render_template('profile/change_email.html', form=form)

@bp.route('/comment/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_comment(id):
    comment = Comment.query.get_or_404(id)
    if comment.user != current_user:
        abort(403)
    form = CommentForm()
    if form.validate_on_submit():
        comment.body = form.body.data
        db.session.commit()
        flash('Your comment has been updated.', 'success')
        return redirect(url_for('blog.post', id=comment.post_id))
    elif request.method == 'GET':
        form.body.data = comment.body
    return render_template('edit_comment.html', title='Edit Comment', form=form, comment=comment)

@bp.route('/comment/<int:id>/reply', methods=['GET', 'POST'])
@login_required
def reply_comment(id):
    parent = Comment.query.get_or_404(id)
    form = ReplyForm()
    if form.validate_on_submit():
        reply = Comment(body=form.body.data, user=current_user, post=parent.post, parent=parent)
        db.session.add(reply)
        db.session.commit()
        flash('Your reply has been posted.', 'success')
        return redirect(url_for('blog.post', id=parent.post_id))
    return render_template('reply_comment.html', title='Reply to Comment', form=form, parent=parent)


@bp.route('/comment/<int:id>/vote/<action>', methods=['POST'])
@login_required
def vote_comment(id, action):
    comment = Comment.query.get_or_404(id)
    vote = CommentVote.query.filter_by(user_id=current_user.id, comment_id=comment.id).first()

    if vote:
        if vote.vote_type == action:
            db.session.delete(vote)
        else:
            vote.vote_type = action
    else:
        vote = CommentVote(user_id=current_user.id, comment_id=comment.id, vote_type=action)
        db.session.add(vote)

    db.session.commit()
    return jsonify({
        'likes': comment.like_count(),
        'dislikes': comment.dislike_count(),
        'user_vote': comment.user_vote(current_user)
    })

@bp.route('/comment/<int:id>/delete', methods=['POST'])
@login_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    if comment.user != current_user:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('Your comment has been deleted.', 'success')
    return redirect(url_for('blog.post', id=comment.post_id))
