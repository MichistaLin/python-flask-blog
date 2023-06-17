这是我的一个数据库课程设计，实现了登录、注册、管理用户、发布文章、管理文章（可发布图片、富文本）、设置及修改用户信息、评论、点赞以及收藏博客等功能。效果图如下

![博客首页](https://img-blog.csdnimg.cn/dccc471096ac44469eda9d7c5140c47f.png)

![个人中心](https://img-blog.csdnimg.cn/d8b9099634844c50972159cf5ee21c7a.png)

# 使用方法
1. 配置环境
  可以使用我提供的虚拟环境，关于虚拟环境修改的问题，可以参考文章我写的这篇文章[虚拟环境复制](https://blog.csdn.net/m0_57110410/article/details/131266980)，也可以自己根据`requirements.txt`安装。
2. 创建数据库
  在`MySQL`中创建一个数据库，名字自己定，然后修改`RealProject\settings.py`里的`SQLALCHEMY_DATABASE_URI`，格式为`mysql+pymysql://username:password@127.0.0.1:3306/dbname`，其中的`username`是MySQL数据库登录的用户名，`password`是登录密码，`3306`是MySQL默认的端口号，我没有修改过，如果你修改过，就改成你的，`dbname`就是你刚刚创建的数据库的名字。

![在这里插入图片描述](https://img-blog.csdnimg.cn/7393ed8ace5945b9b452ae5ee3e2110d.png)

3. 连接数据库
由于我们使用的是`SQLAlchemy`，所以需要做一些初始化设置。在`vscode`或者`pycharm`的`cmd`终端运行如下命令
```python
# 设置项目的flask环境变量，每次关闭项目之后再次打开，如果要用到flask命令，都需要先设置Flask环境变量
set FLASK_APP=RealProject
set FLASK_ENV=development

```
同步数据库，此时，你可以发现项目目录多了一个migrations的文件夹，下边的versions目录下的文件就是生成的数据库迁移文件！
```python
flask db init
```
然后，运行以下命令生成迁移
```python
flask db migrate
```
做完这两步就完成了第一次的初始迁移操作，我们可以看数据库已经有了我们创建的模型字段！
之后，每次在新增和修改完模型数据之后，只需要执行以下两个命令即可
```python
flask db migrate
flask db upgrade
```
4. 运行flask项目
直接运行manage.py即可

关注博客：<a href="https://blog.csdn.net/m0_57110410">CSDN-再游于北方知寒</a>