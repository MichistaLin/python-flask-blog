from datetime import datetime
from RealProject import db
from sqlalchemy.dialects.mysql import LONGTEXT
from enum import IntEnum


class BaseModel(db.Model):
    # 基类模型
    __abstract__ = True

    add_date = db.Column(db.DateTime, nullable=False, default=datetime.now)  # 创建时间
    pub_date = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)  # 更新时间


class PostPublishType(IntEnum):
    # 文章发布类型
    draft = 1  # 草稿
    show = 2  # 发布


class Category(BaseModel):
    # 文章分类模型
    cate_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    icon = db.Column(db.String(128), nullable=True)
    post = db.relationship('Post', back_populates='category', cascade="all,delete", passive_deletes=True)

    # post = db.relationship('Post',backref='category',lazy=True)

    def __repr__(self):
        return '<Category %r>' % self.name


# 多对多关系帮助器表
tags = db.Table('tags',
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.tag_id'), primary_key=True),
                db.Column('post_id', db.Integer, db.ForeignKey('post.post_id'), primary_key=True)
                )


class Post(BaseModel):
    # 文章
    post_id = db.Column(db.Integer, primary_key=True)  # 文章id
    user_id = db.Column(db.Integer,db.ForeignKey('user.user_id', ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(128), nullable=False)  # 文章标题
    desc = db.Column(db.String(200), nullable=True)  # 文章描述
    content = db.Column(LONGTEXT, nullable=True)
    has_type = db.Column(db.Enum(PostPublishType), server_default='show', nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.cate_id', ondelete="CASCADE"), nullable=False)  # 文章分类id
    # 多对多关系
    tags = db.relationship('Tag', secondary=tags, lazy='subquery', backref=db.backref('post', lazy=True))

    category = db.relationship("Category", back_populates="post")
    user = db.relationship('User',back_populates="post")
    answer = db.relationship('Answer', back_populates='post', cascade="all,delete", passive_deletes=True)
    collection = db.relationship('Collection', back_populates='post', cascade="all,delete", passive_deletes=True)
    
    def __repr__(self):
        return '<Post %r>' % self.title


class Tag(BaseModel):
    # 文章标签模型
    tag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)

    def __repr__(self):
        return self.name

class Answer(BaseModel):
    # 回答模型
    answer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.user_id', ondelete="CASCADE"),nullable=False)
    content = db.Column(LONGTEXT, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id', ondelete="CASCADE"), nullable=False)
    c_number = db.Column(db.Integer, nullable=False,server_default='0') #评论数
    z_number = db.Column(db.Integer, nullable=False,server_default='0') #点赞数

    user = db.relationship("User", back_populates="answer")
    post = db.relationship("Post", back_populates="answer")
    comment = db.relationship('Comment', back_populates='answer', cascade="all,delete", passive_deletes=True)

    def __repr__(self):
        return '<Answer %r>' % self.answer_id
