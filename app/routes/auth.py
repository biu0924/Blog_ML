from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db
from urllib.parse import urlparse

bp = Blueprint('auth', __name__)

@bp.route("/register", methods=['GET', 'POST'])
def register():# 注册
    # 如果用户已经注册，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    if request.method == 'POST':
        username =request.form['username']
        email = request.form['email']
        password = request.form['password']

        # 检查用户名是否存在
        user = User.query.filter_by(username=username).first()
        if user:
            flash("Please use a different username.")
            return redirect(url_for("auth.register"))

        # 检查邮箱是否存在
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Please use a different email address.")
            return redirect(url_for("auth.register"))

        # 创建新用户并保存到数据库
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Congratulations, you are now a registered user!")
        return redirect(url_for('auth.login'))
    return render_template("register.html", title="Register")

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash("Invalid username or password.")
            return redirect(url_for('auth.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('blog.index')
        return redirect(next_page)
    return render_template('login.html', title="Sign In")

@bp.route('/logout')
def logout():
    logout_user()# 登出用户
    return redirect(url_for('blog.index'))

