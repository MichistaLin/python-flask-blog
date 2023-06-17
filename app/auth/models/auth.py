from datetime import datetime
from RealProject import db

class BaseModel(db.Model):
    """基类模型
    """
    __abstract__ = True

    add_date = db.Column(db.DateTime, nullable=False, default=datetime.now) # 创建时间
    pub_date = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False) # 更新时间


class User(BaseModel):
    """用户模型
    """
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(320), nullable=False)
    gender = db.Column(db.String(6), nullable=True)                        # 性别
    avatar = db.Column(db.String(200), nullable=True)                       # 头像
    email = db.Column(db.String(45), nullable=True)                         # 邮箱
    sign = db.Column(db.String(30), nullable=True)                          # 个性签名
    introduce = db.Column(db.String(200), nullable=True)                    # 个人介绍
    is_super_user = db.Column(db.Boolean, nullable=True, default=False)     # 超级管理员标识
    is_active = db.Column(db.Boolean, nullable=True, default=True)          # 是否为活跃用户
    is_staff = db.Column(db.Boolean, nullable=True, default=False)          # 是否允许登录后台

    post = db.relationship('Post', back_populates='user', cascade="all,delete", passive_deletes=True)
    answer = db.relationship('Answer', back_populates='user', cascade="all,delete", passive_deletes=True)
    collection = db.relationship('Collection', back_populates='user', cascade="all,delete", passive_deletes=True)
    comment = db.relationship('Comment', back_populates='user', cascade="all,delete", passive_deletes=True)
    def __repr__(self):
        return '<User %r>' % self.username