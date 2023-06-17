from flask import Blueprint, render_template, request,redirect,url_for,g,current_app
from .models import Category, Post, Tag,Answer
import random
from app.auth.models.auth import User
from app.admin.models import Collection,Comment
from RealProject import db
from sqlalchemy import or_

bp = Blueprint('blog', __name__, url_prefix='/blog', static_folder='static', template_folder='templates')

def changedatabaseuser():
    if g.user:
        if g.user.is_super_user:
            current_app['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:lyd123@127.0.0.1:3306/myblog'
        else:
            current_app['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:lyd123@127.0.0.1:3306/myblog'
    else:
        pass
    
@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(-Post.add_date).paginate(page=page, per_page=6, error_out=False)
    post_list = pagination.items

    imgs = ['https://p.qqan.com/up/2022-12/16711702984635618.jpg',
            'https://p.qqan.com/up/2022-12/16706610649807158.jpg',
            'https://p.qqan.com/up/2022-12/16705644186295927.jpg',
            'https://p.qqan.com/up/2022-12/16700473522915296.jpg',
            'https://p.qqan.com/up/2022-12/16700473529619154.jpg',
            'https://img.vm.laomishuo.com/image/2022/09/2022090710385913.jpg',
            'https://img.vm.laomishuo.com/image/2022/03/2022032917383354.jpeg',
            'https://img.vm.laomishuo.com/image/2022/09/202209071029311.jpg',
            'https://img.vm.laomishuo.com/image/2022/09/2022090710261865.jpg'
            ]

    for post in post_list:
        post.img = random.choice(imgs)
    
    return render_template('index.html', posts=post_list, pagination=pagination)


@bp.route('/category/<int:cate_id>')
def cates(cate_id):
    # 分类页
    cate = Category.query.get(cate_id)
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter(Post.category_id == cate_id).paginate(page=page, per_page=10, error_out=False)
    post_list = pagination.items
    return render_template('cate_list.html', cate=cate, post_list=post_list, cate_id=cate_id, pagination=pagination)


@bp.route('/category/<int:cate_id>/<int:post_id>',methods=['GET','POST'])
def detail(cate_id, post_id):
    # 详情页
    cate = Category.query.get(cate_id)
    post = Post.query.get_or_404(post_id)
    collection_list = Collection.query.filter(Collection.post_id==post_id).all()
    if collection_list:
        collections = [collection.user_id for collection in collection_list]
    else:
        collections = []
    
    page = request.args.get('page', 1, type=int)
    pagination = Answer.query.filter(Answer.post_id==post_id).order_by(-Answer.add_date).paginate(page=page, per_page=9, error_out=False)
    obj_answers = pagination.items
    if obj_answers:
        answers = [answer for answer in obj_answers]
    else:
        answers = []

    # 上一篇
    prev_post = Post.query.filter(Post.post_id < post_id).order_by(-Post.post_id).first()
    # 下一篇
    next_post = Post.query.filter(Post.post_id > post_id).order_by(Post.post_id).first()

    return render_template('detail.html', cate=cate,collections=collections, post=post,answers=answers, prev_post=prev_post, next_post=next_post,pagination=pagination)

@bp.route('/like/', methods=['POST'])
def giveLike():
    cate_id = request.args['cate_id']
    post_id = request.form.get('post_id')
    answer_id = request.form.get('answer_id')
    answer = Answer.query.get(answer_id)
    answer.z_number = answer.z_number + 1
    db.session.commit()
    return redirect(url_for('blog.detail',cate_id=cate_id, post_id=post_id))

@bp.route('/comment/<int:cate_id>/<int:post_id>/<int:answer_id>',methods=['GET','POST'])
def comment(cate_id,post_id,answer_id):
    comments = Comment.query.filter(Comment.answer_id==answer_id).all()
    answer = Answer.query.get(answer_id)
    cate = Category.query.get(cate_id)
    post = Post.query.get(post_id)
    if comments:
        comment_list = [comment for comment in comments]
    else:
        comment_list = []

    return render_template('comment.html',comment_list=comment_list,cate=cate,post=post,answer=answer)


@bp.context_processor
def inject_archive():
    # 文章归档日期注入上下文
    posts = Post.query.order_by(Post.add_date)
    dates = set([post.add_date.strftime("%Y年%m月") for post in posts])

    # 标签
    tags = Tag.query.all()
    for tag in tags:
        tag.style = ['is-success', 'is-danger', 'is-black', 'is-light', 'is-primary', 'is-link', 'is-info',
                     'is-warning']

    return dict(dates=dates, tags=tags)


@bp.route('/category/<string:date>')
def archive(date):
    # 归档页
    import re
    # 正则匹配年月
    regex = re.compile(r'\d{4}|\d{2}')
    dates = regex.findall(date)

    from sqlalchemy import extract, and_, or_
    page = request.args.get('page', 1, type=int)
    # 根据年月获取数据
    archive_posts = Post.query.filter(
        and_(extract('year', Post.add_date) == int(dates[0]), extract('month', Post.add_date) == int(dates[1])))
    # 对数据进行分页
    pagination = archive_posts.paginate(page=page, per_page=10, error_out=False)
    return render_template('archive.html', post_list=pagination.items, pagination=pagination, date=date)


@bp.route('/tags/<int:tag_id>')
def tags(tag_id):
    # 标签页
    tag = Tag.query.get(tag_id)
    return render_template('tags.html', post_list=tag.post, tag=tag)


@bp.context_processor
def inject_archive():
    # 文章归档日期注入上下文
    posts = Post.query.order_by(-Post.add_date)
    dates = set([post.add_date.strftime("%Y年%m月") for post in posts])

    # 标签
    tags = Tag.query.all()
    for tag in tags:
        tag.style = ['is-success', 'is-danger', 'is-black', 'is-light', 'is-primary', 'is-link', 'is-info',
                     'is-warning']

    # 最新文章
    new_posts = posts.limit(6)
    return dict(dates=dates, tags=tags, new_posts=new_posts)


@bp.route('/search')
def search():
    # 搜索视图
    words = request.args.get('words', '', type=str)
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter(or_(Post.title.like("%" + words + "%"),Post.desc.like("%" + words + "%"),Post.content.like("%" + words + "%"))).paginate(page=page, per_page=10, error_out=False)
    post_list = pagination.items
    return render_template('search.html', post_list=post_list, words=words, pagination=pagination)
