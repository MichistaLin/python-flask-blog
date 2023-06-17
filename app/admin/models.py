from datetime import datetime,timedelta
from RealProject import db
from sqlalchemy.dialects.mysql import TEXT


class BaseModel(db.Model):
    # 基类模型
    __abstract__ = True

    add_date = db.Column(db.DateTime,nullable=False,default=datetime.now) # 创建时间
    pub_date = db.Column(db.DateTime,default=datetime.now,onupdate=datetime.now,nullable=False) # 更新时间

class Collection(BaseModel):
    # 收藏
    collection_id = db.Column(db.Integer, primary_key=True, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id', ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete="CASCADE"), nullable=False)

    user = db.relationship("User", back_populates="collection")
    post = db.relationship("Post", back_populates="collection")

class Comment(BaseModel):
    # 评论
    comment_id = db.Column(db.Integer, primary_key=True, nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.answer_id', ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete="CASCADE"), nullable=False)
    content = db.Column(TEXT,nullable=False)

    user = db.relationship("User", back_populates="comment")
    answer = db.relationship("Answer", back_populates="comment")
