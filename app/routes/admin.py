# 在 admin.py 中
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, db
from app.forms import UserForm

admin = Blueprint('admin', __name__)

@admin.route('/admin')
@login_required
def admin_index():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
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