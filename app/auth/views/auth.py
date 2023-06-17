from flask import Blueprint,render_template,request,redirect,url_for,session,flash,g
from ..models import User
from werkzeug.security import check_password_hash, generate_password_hash
from RealProject import db
import functools
from ..forms import LoginForm,RegisterForm,UserinfoForm
from app.blog.models import Answer,Post
from app.admin.models import Collection,Comment
from app.admin.utils import upload_file_path

bp = Blueprint('auth', __name__,url_prefix='/auth',static_folder='../static',template_folder='../templates')

# 在模板中获取用户信息
@bp.before_app_request
def load_logged_in_user():
    # 每个请求之前都回去session中查看user_id来获取用户
    user_id = session.get('user_id')
    # 注册用户即非管理员用户允许登录后查看的url
    # urls = ['/auth/']
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(int(user_id))
         # 权限判断
        # if g.user.is_super_user and g.user.is_active:
        #     g.user.has_perm = 1
        # elif not g.user.is_super_user and g.user.is_active and not g.user.is_staff and request.path in urls:
        #     g.user.has_perm = 1
        # else:
        #     g.user.has_perm = 0

# 实现login_required装饰器
def login_required(view):
    # 限制必须登录才能访问的页面装饰器
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            redirect_to = f"{url_for('auth.login')}?redirect_to={request.path}"
            return redirect(redirect_to)

        # 登录成功后对权限进行判断处理
        # if not g.user.has_perm:
        #     return '<h1>无权限查看！</h1>'
        return view(**kwargs)
    return wrapped_view

@bp.route('/login',methods=['GET','POST'])
def login():
    # 登录视图
    redirect_to = request.args.get('redirect_to')
    # form = LoginForm(meta={'csrf': False}) # 禁用csrf
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        session.clear()
        session['user_id'] = user.user_id
        if redirect_to is not None:
            return redirect(redirect_to)
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


@bp.route('/register',methods=['GET','POST'])
def register():
    # 注册视图
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=generate_password_hash(form.password.data))
        db.session.add(user)
        db.session.commit()
        session.clear()
        session['user_id'] = user.user_id
        return redirect(url_for('index'))
    return render_template('register.html', form=form)
    

# 实现用户退出登录功能
@bp.route('/logout')
def logout():
    # 注销
    session.clear()
    return redirect(url_for('index'))

@bp.route('/')
@login_required
def userinfo():
    # 用户中心

    return render_template('userinfo.html')

@bp.route('/userinfo_edit/<int:user_id>',methods=['GET','POST'])
@login_required
def userinfo_edit(user_id):
    user = User.query.get(user_id)
    # print(user)

    form = UserinfoForm(
        username=user.username, 
        password=user.password,
        avatar=user.avatar,
        gender=user.gender,
        email=user.email,
        sign=user.sign,
        introduce=user.introduce
    )
    form.password.default = f'{user.password}'
    # print(form.validate_on_submit(),user.username,user.gender)

    if form.validate_on_submit():
        user.username = form.username.data
        if not form.password.data:
            user.password = user.password
        else:
            user.password = generate_password_hash(form.password.data)
        f = form.avatar.data
        if user.avatar == f:
            user.avatar = user.avatar
        else:
            avatar_path, filename = upload_file_path('avatar', f)
            f.save(avatar_path)
            user.avatar = f'avatar/{filename}'
        if form.gender.data:
            user.gender = form.gender.data
        else:
            user.gender = user.gender
        if form.email.data:
            user.email = form.email.data
        else:
            user.email = user.email
        if form.sign.data:
            user.sign = form.sign.data
        else:
            user.sign = user.sign
        if form.introduce.data:
            user.introduce = form.introduce.data
        else:
            user.introduce = user.introduce
        db.session.add(user)
        db.session.commit()
        # flash(f'{user.username}修改成功')
        return redirect(url_for('auth.userinfo'))
    return render_template('userinfo_form.html',form=form)


@bp.route('/collection')
@login_required
def collection():
    #我的收藏
    # collection = Collection.query.filter(Collection.user_id==g.user.user_id).all()
    page = request.args.get('page', 1, type=int)
    pagination = Collection.query.filter(Collection.user_id==g.user.user_id).order_by(-Collection.add_date).paginate(page=page, per_page=10, error_out=False)
    collection_list = pagination.items

    return render_template('collection.html',collection_list=collection_list,pagination=pagination)

@bp.route('/collection/add', methods=['GET', 'POST'])
@login_required
def collection_add():
    post_id = request.args['post_id']
    user_id = request.args['user_id']
    cate_id = request.args['cate_id']
    collection = Collection(post_id=post_id,user_id=user_id)
    db.session.add(collection)
    db.session.commit()
    return redirect(url_for('blog.detail',cate_id=cate_id ,post_id=post_id))

@bp.route('/collection/del', methods=['GET', 'POST'])
@login_required
def collection_del():
    # 取消收藏
    post_id = request.args['post_id']
    user_id = request.args['user_id']
    cate_id = request.args['cate_id']
    collection = Collection.query.filter(Collection.post_id==post_id and Collection.user_id==user_id).first()
    db.session.delete(collection)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('blog.detail',cate_id=cate_id ,post_id=post_id))

@bp.route('/collection/del_1', methods=['GET', 'POST'])
@login_required
def collection_del_1():
    # 删除收藏
    collection_id = request.args['collection_id']
    collection = Collection.query.get(collection_id)
    db.session.delete(collection)
    db.session.commit()
    flash(f'已取消收藏')
    return redirect(url_for('auth.collection'))


@bp.route('/mycomment')
@login_required
def mycomment():
    #我的评论
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.filter(Comment.user_id==g.user.user_id).order_by(-Comment.add_date).paginate(page=page, per_page=10, error_out=False)
    comments = pagination.items
    if comments:
        comment_list = [comment for comment in comments]
    else:
        comment_list = []
    
    return render_template('mycomment.html',comment_list=comment_list,pagination=pagination)

@bp.route('/mycomment/<int:comment_id>',methods=['GET','POST'])
@login_required
def comment_del(comment_id):
    # 删除评论
    comment = Comment.query.get(comment_id)
    answer = Answer.query.filter(Answer.answer_id == comment.answer_id).first()
    if comment:
        answer.c_number = answer.c_number - 1
        db.session.delete(comment)
        db.session.commit()
        flash('成功删除一条评论')
        return redirect(url_for('auth.mycomment'))

@bp.route('/myanswer')
@login_required
def myanswer():
    # 我的回答
    page = request.args.get('page', 1, type=int)
    pagination = Answer.query.filter(Answer.user_id==g.user.user_id).order_by(-Answer.add_date).paginate(page=page, per_page=10, error_out=False)
    answers = pagination.items
    if answers:
        answer_list = [answer for answer in answers]
    else:
        answer_list = []

    return render_template('myanswer.html',answer_list=answer_list,pagination=pagination)

@bp.route('/mypost')
@login_required
def mypost():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter(Post.user_id==g.user.user_id).order_by(-Post.add_date).paginate(page=page, per_page=10, error_out=False)
    posts = pagination.items
    # print(posts)
    if posts:
        post_list = [post for post in posts]
    else:
        post_list = [] 

    return render_template('mypost.html',post_list=post_list,pagination=pagination)