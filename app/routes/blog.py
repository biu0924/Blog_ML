from flask import (Blueprint, render_template,
                   redirect, url_for, flash,
                   request, abort, current_app,
                   jsonify, json)
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

# Blueprint 是 Flask 中的一个类，用于组织一组相关的视图、模板、静态文件等
# 它允许你将应用的不同功能组织成独立的模块。
# 在这里，所有与博客相关的路由和视图函数都被组织在这个 'blog' Blueprint 下
bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    '''
    首页功能
    '''
    # 从 URL 中获取 分页、搜索和排序参数
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'recent')
    # 初始化查询，构建对 BlogPost 数据模型的查询
    query = BlogPost.query
    # 搜索功能，搜索标题或内容中包含 search 内容的博客
    if search:
        query = query.filter(or_(BlogPost.title.contains(search), BlogPost.content.contains(search)))
    # 排序功能
    if sort == 'likes':
        query = query.outerjoin(Like).group_by(BlogPost.id).order_by(db.func.count(Like.id).desc())
    else:  # 默认是最近时间的排序
        query = query.order_by(BlogPost.timestamp.desc())
    # 分页，使用 Flask-SQLAlchemy 的 paginate 实现分页，每页最多是个
    posts = query.paginate(page=page, per_page=10, error_out=False)
    # 查看管理员状态
    is_admin = current_user.is_authenticated and current_user.is_admin
    # 渲染模版，传入必要的数据
    return render_template('index.html', title='Home', posts=posts, search=search, sort=sort, is_admin=is_admin)


@bp.route('/create', methods=['GET', 'POST'])
@login_required# 安全措施，确保只有登录用户可以执行某些操作
def create_post():
    '''
    处理创建新博客文章的请求
    支持 GET(显示表单) 和 POST(提交表单) 方法
    '''
    form = PostForm()# 获取表单实例

    if form.validate_on_submit():
        '''
            当表单通过 POST 方法提交并且数据验证通过时。
            Flask-WTF 会使用在 forms.py 中定义的验证器(validators)来验证表单数据
            具体来说，validate_on_submit()执行如下:
            检查请求方法(应为POST)->CSRF保护->字段验证->返回验证结果
        '''
        # 使用 bleach 清理用户输入的 HTML 内容，只允许特定的标签和属性。这是一个安全措施，防止 XSS 攻击
        content = bleach.clean(
            form.content.data,
            tags=['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'em', 'u', 'a', 'img'],
            attributes={'a': ['href'], 'img': ['src', 'alt']})
        # 新的 BlogPost 实例
        post = BlogPost(
            title=form.title.data,  # 文章标题
            content=content,        # 设置清理后的文章内容
            author=current_user)    # 设置当前登陆用户为作者
        db.session.add(post)    # 将新文章添加到数据库会话
        db.session.commit()     # 提交会话，保存更新到数据库
        flash('Your post has been created.', 'success')
        return redirect(url_for('blog.index'))# 重定向到博客首页
    return render_template('create_post.html', title='Create Post', form=form)

@bp.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    '''
    显示单篇文章及其评论，并允许用户提交评论
    '''
    post = BlogPost.query.get_or_404(id)# 从数据库中获取制定 id 的博客，未找到返回 404
    form = CommentForm()
    if form.validate_on_submit():# 如果用户通过 post 提交评论
        comment = Comment(body=form.body.data, post=post, user=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.', 'success')
        return redirect(url_for('blog.post', id=post.id))
    # 默认第一页
    page = request.args.get('page', 1, type=int)
    # 查询当前文章的评论，只显示一级评论（没有父评论的评论），并按时间降序排序
    # 使用分页功能，每页显示 10 条评论，错误时不抛出异常
    comments = post.comments.filter_by(parent=None).order_by(Comment.timestamp.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('post.html', title=post.title, post=post, form=form, comments=comments)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    '''
    允许作者编辑自己的文章
    '''
    post = BlogPost.query.get_or_404(id)
    if post.author != current_user:# 如果不是自己的文章，返回 403
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = bleach.clean(form.content.data, tags=['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'em', 'u', 'a', 'img'], attributes={'a': ['href'], 'img': ['src', 'alt']})
        db.session.commit()
        flash('Your post has been updated.', 'success')
        return redirect(url_for('blog.post', id=post.id))
    elif request.method == 'GET':# 如果是查看表单请求
        form.title.data = post.title
        form.content.data = post.content
    return render_template('edit_post.html', title='Edit Post', form=form, post=post)

@bp.route('/user/<username>')
@login_required
def user_posts(username):
    '''
    显示特定用户的所有文章
    '''
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.filter_by(author=user).order_by(BlogPost.timestamp.desc()).paginate(page=page, per_page=10,
                                                                                               error_out=False)
    return render_template('user_posts.html', user=user, posts=posts)


@bp.route('/like/<int:post_id>/<action>')
@login_required
def like_action(post_id, action):
    '''
    点赞/取消点赞
    '''
    post = BlogPost.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        # 将当前用户对该文章的点赞记录添加到用户的点赞列表中
        current_user.likes.append(Like(post=post))
        # 提交数据库会话，保存点赞记录
        db.session.commit()
    if action == 'unlike':
        like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
        db.session.delete(like)
        db.session.commit()
    # 重定向到之前的页面
    return redirect(request.referrer)

@bp.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    '''
    上传图片
    '''
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

'''
下面 /profile/... 是用户资料相关路由，查看和更新头像、密码、邮箱等
内容和如上类似
'''
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
        if current_user.check_password(form.old_password.data):# 旧密码输入正确则继续
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
    '''编辑评论'''
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
    '''回复评论'''
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
    '''
    这段代码实现了对评论的投票功能（例如点赞和点踩），允许用户对评论进行投票，并返回更新后的投票统计数据
    '''
    comment = Comment.query.get_or_404(id)
    vote = CommentVote.query.filter_by(user_id=current_user.id, comment_id=comment.id).first()

    if vote:
        # 若投票类型相同，删除投票(取消点赞)
        if vote.vote_type == action:
            db.session.delete(vote)
        # 更新投票类型(点赞或点踩)
        else:
            vote.vote_type = action
    # 若没有记录，新建点赞行动
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


