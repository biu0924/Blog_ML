# 在 admin.py 中
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, db, BlogPost, Comment
from app.forms import UserForm, PostForm
from sqlalchemy import func
from datetime import datetime, timedelta

admin = Blueprint('admin', __name__)

@admin.route('/admin')
@login_required
def admin_index():
    if not current_user.is_admin:# 检查是否是管理员
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('blog.index'))
    return render_template('admin/index.html')

@admin.route('/admin/users')
@login_required
def user_list():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    users = User.query.all()
    return render_template('admin/user_list.html', users=users)

@admin.route('/admin/user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.user_list'))
    return render_template('admin/edit_user.html', form=form, user=user)

@admin.route('/admin/user/<int:id>/delete', methods=['POST'])
@login_required
def delete_user(id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.user_list'))

@admin.route('/admin/posts')
@login_required
def post_list():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    posts = BlogPost.query.all()
    return render_template('admin/post_list.html', posts=posts)

@admin.route('/admin/post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    post = BlogPost.query.get_or_404(id)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        # 将表单数据更新到博文对象
        form.populate_obj(post)
        db.session.commit()
        flash('Post updated successfully.', 'success')
        return redirect(url_for('admin.post_list'))
    return render_template('admin/edit_post.html', form=form, post=post)

@admin.route('/admin/post/<int:id>/delete', methods=['POST'])
@login_required
def delete_post(id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully.', 'success')
    return redirect(url_for('admin.post_list'))

@admin.route('/admin/comments')
@login_required
def comment_list():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    comments = Comment.query.all()
    return render_template('admin/comment_list.html', comments=comments)

@admin.route('/admin/comment/<int:id>/delete', methods=['POST'])
@login_required
def delete_comment(id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully.', 'success')
    return redirect(url_for('admin.comment_list'))


@admin.route('/admin/stats')
@login_required
def stats():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    # 总用户数
    total_users = User.query.count()

    # 总文章数
    total_posts = BlogPost.query.count()

    # 总评论数
    total_comments = Comment.query.count()

    # 过去7天的新用户数
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_last_week = User.query.filter(User.date_joined > week_ago).count()

    # 过去7天的新文章数
    new_posts_last_week = BlogPost.query.filter(BlogPost.timestamp > week_ago).count()

    # 最活跃的5个用户（根据文章数）
    active_users = db.session.query(
        User, func.count(BlogPost.id).label('post_count')
    ).join(BlogPost).group_by(User).order_by(func.count(BlogPost.id).desc()).limit(5).all()

    # 最受欢迎的5篇文章（根据评论数）
    popular_posts = db.session.query(
        BlogPost, func.count(Comment.id).label('comment_count')
    ).join(Comment).group_by(BlogPost).order_by(func.count(Comment.id).desc()).limit(5).all()

    return render_template('admin/stats.html',
                           total_users=total_users,
                           total_posts=total_posts,
                           total_comments=total_comments,
                           new_users_last_week=new_users_last_week,
                           new_posts_last_week=new_posts_last_week,
                           active_users=active_users,
                           popular_posts=popular_posts)