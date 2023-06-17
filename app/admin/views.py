from flask import Blueprint,render_template,request,flash,redirect,url_for,g
from app.auth.views.auth import login_required
from app.blog.models import Category,Post,Tag
from RealProject  import db
from .forms import CategoryCreateForm,PostForm,TagForm,CreateUserForm,AnswerForm
from app.auth.models import User
from werkzeug.security import check_password_hash, generate_password_hash
from app.admin.utils import upload_file_path
from app.admin.models import Comment
from app.blog.models import Answer

bp = Blueprint('admin', __name__,url_prefix='/admin',static_folder='static',template_folder='templates')

@bp.route('/')
@login_required
def index():
    # 主页视图
    posts_num = len(Post.query.all())
    users_num = len(User.query.all())
    comments_num = len(Comment.query.all())
    return render_template('admin/index.html',posts_num=posts_num,users_num=users_num,comments_num=comments_num)


@bp.route('/category')
@login_required
def category():
    # 查看分类
    page = request.args.get('page', 1, type=int)
    pagination = Category.query.order_by(-Category.add_date).paginate(page=page, per_page=10, error_out=False)
    category_list = pagination.items
    return render_template('admin/category.html', category_list=category_list, pagination=pagination)

@bp.route('/category/add', methods=['GET', 'POST'])
@login_required
def category_add():
    # 增加分类
    form = CategoryCreateForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, icon=form.icon.data)
        db.session.add(category)
        db.session.commit()
        flash(f'{form.name.data}分类添加成功')
        return redirect(url_for('admin.category'))
    return render_template('admin/category_form.html', form=form)


@bp.route('/category/edit/<int:cate_id>', methods=['GET', 'POST'])
@login_required
def category_edit(cate_id):
    # 编辑分类
    category = Category.query.get(cate_id)
    form = CategoryCreateForm(name=category.name, icon=category.icon)
    if form.validate_on_submit():
        category.name = form.name.data
        category.icon = form.icon.data
        db.session.add(category)
        db.session.commit()
        flash(f'{form.name.data}分类修改成功')
        return redirect(url_for('admin.category'))
    return render_template('admin/category_form.html', form=form)

@bp.route('/category/delete/<int:cate_id>', methods=['GET', 'POST'])
@login_required
def category_del(cate_id):
    # 删除分类
    category = Category.query.get(cate_id)
    if category: 
        # 级联删除 
        Post.query.filter(Post.post_id==category.cate_id).delete()
        db.session.delete(category)
        db.session.commit()
        flash(f'{category.name}分类删除成功')
        return redirect(url_for('admin.category'))

@bp.route('/article')
@login_required
def article():
    # 查看文章列表
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(-Post.add_date).paginate(page=page, per_page=10, error_out=False)
    post_list = pagination.items
    return render_template('admin/article.html', post_list=post_list, pagination=pagination)

@bp.route('/article/add', methods=['GET', 'POST'])
@login_required
def article_add():
    # 增加文章
    form = PostForm()
    # 分类
    form.category_id.choices = [(v.cate_id,v.name) for v in Category.query.all()]
    # 标签
    form.tags.choices = [(v.tag_id,v.name) for v in Tag.query.all()]

    if form.validate_on_submit():
        post = Post(
            user_id=g.user.user_id,
            title=form.title.data, 
            desc=form.desc.data, 
            has_type=form.has_type.data, 
            category_id=int(form.category_id.data), # 1对多保存
            content=form.content.data,
        )
        post.tags = [Tag.query.get(tag_id) for tag_id in form.tags.data]
        db.session.add(post)
        db.session.commit()
        flash(f'{form.title.data}文章添加成功')
        if g.user.is_super_user:
            return redirect(url_for('admin.article'))
        else:
            return redirect(url_for('auth.mypost'))
    return render_template('admin/article_form.html', form=form)

@bp.route('/article/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def article_edit(post_id):
    # 修改文章
    post = Post.query.get(post_id)
    tags = [tag.tag_id for tag in post.tags]
    form = PostForm(
        title=post.title, desc=post.desc, 
        category_id=post.category.cate_id, has_type=post.has_type.value,
        content=post.content, tags=tags
    )

    form.category_id.choices = [(v.cate_id,v.name) for v in Category.query.all()]
    form.tags.choices = [(v.tag_id,v.name) for v in Tag.query.all()]

    if form.validate_on_submit():
        post.title = form.title.data
        post.desc = form.desc.data
        post.has_type = form.has_type.data
        post.category_id=int(form.category_id.data)
        post.content = form.content.data
        post.tags = [Tag.query.get(tag_id) for tag_id in form.tags.data]
        db.session.add(post)
        db.session.commit()
        flash(f'{form.title.data}文章修改成功')
        if g.user.is_super_user:
            return redirect(url_for('admin.article'))
        else:
            return redirect(url_for('auth.mypost'))
    return render_template('admin/article_form.html', form=form)

@bp.route('/article/delete/<int:post_id>', methods=['GET', 'POST'])
@login_required
def article_del(post_id):
    # 删除文章
    post = Post.query.get(post_id)
    if post:  
        db.session.delete(post)
        db.session.commit()
        flash(f'{post.title}文章删除成功')
        if g.user.is_super_user:
            return redirect(url_for('admin.article'))
        else:
            return redirect(url_for('auth.mypost'))


@bp.route('/tag')
@login_required
def tag():
    # 查看标签列表
    page = request.args.get('page', 1, type=int)
    pagination = Tag.query.order_by(-Tag.add_date).paginate(page=page, per_page=10, error_out=False)
    tag_list = pagination.items
    return render_template('admin/tag.html', tag_list=tag_list, pagination=pagination)


@bp.route('/tag/add', methods=['GET', 'POST'])
@login_required
def tag_add():
    # 增加标签
    form = TagForm()
    if form.validate_on_submit():
        tag = Tag(name=form.name.data)
        db.session.add(tag)
        db.session.commit()
        flash(f'{form.name.data}添加成功')
        return redirect(url_for('admin.tag'))
    return render_template('admin/tag_form.html', form=form)


@bp.route('/tag/edit/<int:tag_id>', methods=['GET', 'POST'])
@login_required
def tag_edit(tag_id):
    # 修改标签
    tag = Tag.query.get(tag_id)
    form = TagForm(name=tag.name)
    if form.validate_on_submit():
        tag.name = form.name.data
        db.session.add(tag)
        db.session.commit()
        flash(f'{form.name.data}添加成功')
        return redirect(url_for('admin.tag'))
    return render_template('admin/tag_form.html', form=form)


@bp.route('/tag/del/<int:tag_id>', methods=['GET', 'POST'])
@login_required
def tag_del(tag_id):
    # 删除标签
    tag = Tag.query.get(tag_id)
    if tag:
        db.session.delete(tag)
        db.session.commit()
        flash(f'{tag.name}删除成功')
        return redirect(url_for('admin.tag'))


@bp.route('/user')
@login_required
def user():
    # 查看文章列表
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(-User.add_date).paginate(page=page, per_page=10, error_out=False)
    user_list = pagination.items
    return render_template('admin/user.html', user_list=user_list, pagination=pagination)

@bp.route('/user/add', methods=['GET', 'POST'])
@login_required
def user_add():
    # 添加用户
    # https://flask-wtf.readthedocs.io/en/1.0.x/form/#file-uploads  
    form = CreateUserForm()
    if form.validate_on_submit():      
        f = form.avatar.data
        # 判断是否有头像（因为定义数据库时头像可为空）
        if f:
            avatar_path, filename = upload_file_path('avatar', f)
            f.save(avatar_path)
            user = User(
                username=form.username.data, 
                password=generate_password_hash(form.password.data),
                avatar=f'avatar/{filename}',
                is_super_user=form.is_super_user.data,
                is_active=form.is_active.data,
                is_staff=form.is_staff.data
                )
        else:
            user = User(
                username=form.username.data, 
                password=generate_password_hash(form.password.data),
                avatar=None,
                is_super_user=form.is_super_user.data,
                is_active=form.is_active.data,
                is_staff=form.is_staff.data
                )
        db.session.add(user)
        db.session.commit()
        flash(f'{form.username.data}用户添加成功')
        return redirect(url_for('admin.user'))
    return render_template('admin/user_form.html', form=form)

@bp.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
    # 修改用户信息
    user = User.query.get(user_id)

    from .utils import upload_file_path
    form = CreateUserForm(
        username=user.username, 
        password=user.password,
        avatar=user.avatar,
        is_super_user=user.is_super_user,
        is_active=user.is_active,
        is_staff=user.is_staff 
    )
    form.password.default = f'{user.password}'
    print(form.validate_on_submit())
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
        user.is_super_user = form.is_super_user.data
        user.is_active = form.is_active.data
        user.is_staff = form.is_staff.data
        db.session.add(user)
        db.session.commit()
        flash(f'{user.username}修改成功')
        return redirect(url_for('admin.user'))
    return render_template('admin/user_form.html', form=form, user=user)

@bp.route('/user/del/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_del(user_id):
    # 删除用户
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f'{user.username}删除成功')
        return redirect(url_for('admin.user'))

@bp.route('/upload', methods=['POST'])
@login_required
def upload():
    # 上传图片
    if request.method == 'POST':
        f = request.files.get('upload')
        file_size = len(f.read())
        f.seek(0)  # reset cursor position to beginning of file

        if file_size > 2048000:  # 限制上传大小为2M
            return {
                'code':'err',
                'message': '文件超过限制2048000字节',
            }
        upload_path, filename = upload_file_path('upload', f)
        f.save(upload_path)
        return {
            'code':'ok',
            'url':f'/admin/static/upload/{filename}'
        }


@bp.route('/answer',methods=['GET','POST'])
@login_required
def answer():
    # 回答的文章视图
    page = request.args.get('page', 1, type=int)
    pagination = Answer.query.order_by(-Answer.add_date).paginate(page=page, per_page=10, error_out=False)
    answers = pagination.items
    if answers:
        answer_list = [answer for answer in answers]
    else:
        answer_list = []
    return render_template('admin/answer.html', answer_list=answer_list, pagination=pagination)

@bp.route('/answer/add', methods=['GET', 'POST'])
@login_required
def answer_add():
    user_id = request.args['user_id']
    post_id = request.args['post_id']
    cate_id = request.args['cate_id']
    form = AnswerForm()
    if form.validate_on_submit():
        answer = Answer(user_id=user_id,content=form.content.data,post_id=post_id)
        db.session.add(answer)
        db.session.commit()
        return redirect(url_for('blog.detail',cate_id=cate_id,post_id=post_id))
    return render_template('admin/answer_form.html',form=form)

@bp.route('/answer/edit/<int:answer_id>', methods=['GET', 'POST'])
@login_required
def answer_edit(answer_id):
    answer = Answer.query.get(answer_id)
    form = AnswerForm(content=answer.content)

    if form.validate_on_submit():
        answer.content = form.content.data
        db.session.add(answer)
        db.session.commit()
        flash('回答修改成功')
        return redirect(url_for('admin.answer'))
    return render_template('admin/answer_form.html',form=form)

@bp.route('/answer/del/<int:answer_id>', methods=['GET', 'POST'])
@login_required
def answer_del(answer_id):
    # 删除回答
    answer = Answer.query.get(answer_id)
    if answer:
        db.session.delete(answer)
        db.session.commit()
        flash('回答删除成功')
        return redirect(url_for('admin.answer'))

@bp.route('/comments',methods=['GET', 'POST'])
@login_required
def comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(-Comment.add_date).paginate(page=page, per_page=10, error_out=False)
    comments = pagination.items
    if comments:
        comment_list = [comment for comment in comments]
    else:
        comment_list = []
    return render_template('admin/comments.html',comment_list=comment_list, pagination=pagination)


@bp.route('/comments/add/<int:cate_id>/<int:post_id>/<int:answer_id>',methods=['GET', 'POST'])
@login_required
def comment_add(cate_id,post_id,answer_id):
    content = request.form.get('content')
    comment = Comment(user_id=g.user.user_id,content=content,answer_id=answer_id)
    answer = Answer.query.get(answer_id)
    answer.c_number = answer.c_number + 1
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('blog.comment',cate_id=cate_id,post_id=post_id,answer_id=answer_id))

@bp.route('/comments/<int:comment_id>',methods=['GET','POST'])
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