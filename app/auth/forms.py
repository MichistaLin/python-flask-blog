# 表单验证
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from flask_wtf.file import FileField, FileRequired, FileSize, FileAllowed
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from werkzeug.security import check_password_hash
from .models import User

class LoginForm(FlaskForm):
    # 登录表单
    def qs_username(username):
        # 对该字段进行在传递之前处理
        u = f'{username}123456'
        return username

    username = StringField('username', validators=[
        DataRequired(message="不能为空"), 
        Length(max=32, message="不符合字数要求！")
        ], filters=(qs_username,))
    password = PasswordField('password', validators=[
        DataRequired(message="不能为空"),
        Length(max=32, message="不符合字数要求！")
        ])

    def validate_username(form, field):
        user = User.query.filter_by(username=field.data).first()
        if user is None:
            error = '该用户不存在！'
            raise ValidationError(error)
        elif not check_password_hash(user.password, form.password.data):
            raise ValidationError('密码不正确')


class RegisterForm(FlaskForm):
    # 注册表单
    username = StringField('username', validators=[
        DataRequired(message="不能为空"), 
        Length(min=2, max=32, message="超过限制字数！")
        ])
    password = PasswordField('password', validators=[
        DataRequired(message="不能为空"),
        Length(min=2, max=32, message="超过限制字数！"),
        EqualTo('password1', message='两次密码输入不一致！')
        ])
    password1 = PasswordField('password1')

    def validate_username(form, field):
        user = User.query.filter_by(username=field.data).first()
        if user is not None:
            error = '该用户名称已存在！'
            raise ValidationError(error)

class UserinfoForm(FlaskForm):
    # 修改个人用户信息表单
    username = StringField('username', validators=[
        DataRequired(message="不能为空"), 
        Length(max=32, message="不符合字数要求！")
        ])
    password = PasswordField('password', validators=[
        # DataRequired(message="不能为空"),
        Length(max=32, message="不符合字数要求！")
        ], description="修改用户信息时，留空则代表不修改！")
    avatar = FileField("avatar", validators=[
        FileAllowed(['jpg', 'png', 'gif'], message="仅支持jpg/png/gif格式"),
        FileSize(max_size=2048000, message="不能大于2M")],
        description="大小不超过2M，仅支持jpg/png/gif格式，不选择则代表不修改")
    gender = StringField('gender',validators=[DataRequired(message="不能为空"),Length(max=6, message="不符合字数要求！")], description="修改用户信息时，留空则代表不修改！")
    email = StringField('email',validators=[DataRequired(message="不能为空"),Length(max=45, message="不符合字数要求！")], description="修改用户信息时，留空则代表不修改！")
    sign = StringField('sign',validators=[DataRequired(message="不能为空"),Length(max=30, message="不符合字数要求！")], description="修改用户信息时，留空则代表不修改！")
    introduce = StringField('introduce',validators=[DataRequired(message="不能为空"),Length(max=200, message="不符合字数要求！")], description="修改用户信息时，留空则代表不修改！")