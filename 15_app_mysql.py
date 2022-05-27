from datetime import datetime
from flask import Flask
# from flask_restful import marshal, fields
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy import and_, or_, not_, func
from sqlalchemy.orm import load_only, contains_eager

# mysql驱动
# import MySQLdb     # TODO with problem
import pymysql
pymysql.install_as_MySQLdb()


app = Flask(__name__)


class FlaskConfig:
    """连接mysql数据库配置"""
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root123456@127.0.0.1:3306/toutiao'   # URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False            # 在Flask中是否追踪数据修改
    SQLALCHEMY_ECHO = True                            # 显示生成的SQL语句，可用于调试

app.config.from_object(FlaskConfig)

# 创建SQLAlchemy对象，读取app中的数据库连接信息
# 方式一、
db: SQLAlchemy = SQLAlchemy(app)
# 方式二、
# db = SQLAlchemy()
# db.init_app(app)
# 注意此方式在 单独运行调试(独立于视图外) 时，对数据库操作需要在Flask的应用上下文中进行，在视图中操作则无需设置上下文环境
# with app.app_context(environ):
#     User.query.all()


# 定义模型类
class User(db.Model):
    """User模型类"""
    __tablename__ = 'user_basic'

    class STATUS:    # 枚举
        DISABLE = 0
        ENABLE = 1

    id = db.Column('user_id', db.Integer, primary_key=True, doc='用户ID')
    mobile = db.Column(db.String, doc='手机号')
    password = db.Column(db.String, doc='密码')
    name = db.Column('user_name', db.String, doc='昵称')
    profile_photo = db.Column(db.String, doc='头像')
    last_login = db.Column(db.DateTime, doc='最后登录时间')
    is_media = db.Column(db.Boolean, default=False, doc='是否是自媒体')
    is_verified = db.Column(db.Boolean, default=False, doc='是否实名认证')
    introduction = db.Column(db.String, doc='简介')
    certificate = db.Column(db.String, doc='认证')
    article_count = db.Column(db.Integer, default=0, doc='发帖数')
    following_count = db.Column(db.Integer, default=0, doc='关注的人数')
    fans_count = db.Column(db.Integer, default=0, doc='被关注的人数（粉丝数）')
    like_count = db.Column(db.Integer, default=0, doc='累计点赞人数')
    read_count = db.Column(db.Integer, default=0, doc='累计阅读人数')

    account = db.Column(db.String, doc='账号')
    email = db.Column(db.String, doc='邮箱')
    status = db.Column(db.Integer, default=STATUS.ENABLE, doc='状态，是否可用')

    # 额外声明的类属性，不映射数据库的字段；默认是惰性执行
    # 方式一、主模型类中声明关联表的连接属性，通过此属性查询获取从表信息(默认是对象列表)，此方式需要从模型类对应字段设置外键约束
    # profile = db.relationship('UserProfile', uselist=False)           # uselist表示主表调用profile返回时是否以列表返回，这里是一对一关系，返回从表对象即可，故不需要以列表返回
    # followings = db.relationship('Relation')                          # 多对多，以列表形式返回(默认)

    # 方式二、仅在主模型类中声明关联字段及关联条件，此时从模型类对应字段不需要设置外键约束
    profile = db.relationship('UserProfile', primaryjoin='User.id==foreign(UserProfile.id)', uselist=False)
    followings = db.relationship('Relation', primaryjoin='User.id==foreign(Relation.user_id)')

class UserProfile(db.Model):
    """
    用户资料表
    """
    __tablename__ = 'user_profile'

    class GENDER:
        MALE = 0
        FEMALE = 1

    id = db.Column('user_id', db.Integer, primary_key=True, doc='用户ID')
    # id = db.Column('user_id', db.Integer, db.ForeignKey('user_basic.user_id'), primary_key=True, doc='用户ID')   # 模型类声明外键时，传的是数据库中真实表名及字段名，用于关联查询时生成的SQL语句的传入，而非模型类名和属性名；实际数据库中并没有外键关系
    gender = db.Column(db.Integer, default=0, doc='性别')
    birthday = db.Column(db.Date, doc='生日')
    real_name = db.Column(db.String, doc='真实姓名')
    id_number = db.Column(db.String, doc='身份证号')
    id_card_front = db.Column(db.String, doc='身份证正面')
    id_card_back = db.Column(db.String, doc='身份证背面')
    id_card_handheld = db.Column(db.String, doc='手持身份证')
    ctime = db.Column('create_time', db.DateTime, default=datetime.now, doc='创建时间')     # default值为一个函数，模型类创建时会自动调用now()函数
    utime = db.Column('update_time', db.DateTime, default=datetime.now, onupdate=datetime.now, doc='更新时间')   # onupdate指定修改时的调用
    register_media_time = db.Column(db.DateTime, doc='注册自媒体时间')

    area = db.Column(db.String, doc='地区')
    company = db.Column(db.String, doc='公司')
    career = db.Column(db.String, doc='职业')


class Relation(db.Model):
    """
    用户关系表
    """
    __tablename__ = 'user_relation'

    class RELATION:
        DELETE = 0
        FOLLOW = 1
        BLACKLIST = 2

    id = db.Column('relation_id', db.Integer, primary_key=True, doc='主键ID')
    user_id = db.Column(db.Integer, doc='用户ID')
    # user_id = db.Column(db.Integer, db.ForeignKey('user_basic.user_id'), doc='用户ID')
    target_user_id = db.Column(db.Integer, doc='目标用户ID')
    relation = db.Column(db.Integer, doc='关系')
    ctime = db.Column('create_time', db.DateTime, default=datetime.now, doc='创建时间')
    utime = db.Column('update_time', db.DateTime, default=datetime.now, onupdate=datetime.now, doc='更新时间')

    user = db.relationship('User', primaryjoin='Relation.target_user_id==foreign(User.id)', uselist=False)

# field = {
#     'mobile': fields.String,
#     'name': fields.String
# }

@app.route('/get_user')
def get_user():
    # 原生sqlalchemy用法
    # print(db.session.query(User).all())
    # print(db.session.query(User).first())
    # print(db.session.query(User).get(2))


    # flask_sqlalchemy用法，是对原生sqlalchemy的封装
    # user_list = User.query.all()   # 模型类列表
    # print('user_list-----------', user_list)
    # u1 = User.query.first()      # limit 1
    # print('u1---------', u1)
    # u2 = User.query.get(2)       # 指定pk
    # print('u2---------', u2.name)

    # 过滤
    # filter_by 传的是条件的 key value 形式，且只能exact、逻辑and查询
    # uu21: BaseQuery = User.query.filter_by(mobile='15212345678')           # exact查询
    # uu22 = User.query.filter_by(mobile='15212345678', id=3).first()        # and查询
    # print('uu21--------\n', uu21.first())
    # print('uu22--------\n', uu22)

    # filter 传的是比较条件，双等于号；所有情况的查询
    # uu23: BaseQuery = User.query.filter(User.mobile == '15212345678')
    # uu24 = User.query.filter(and_(User.mobile != '15112345678', User.id > 3)).all()
    # uu25 = User.query.filter(or_(User.mobile == '15112345678', User.id > 3)).all()
    # uu26 = User.query.filter(not_(User.mobile != '15112345678')).all()
    # print(uu23.first(), uu24, uu25, uu26, sep='\n')

    # offset偏移 limit限制记录条数
    # uu27 = User.query.offset(2).limit(3).all()
    # print(uu27)

    # order_by排序
    # uu28 = User.query.order_by(User.id).all()                # 正序
    # uu29 = User.query.order_by(User.id.desc()).all()         # 倒序
    # print(uu28, uu29, sep='\n')

    # 复合查询
    # uu30 = User.query.filter(User.mobile.startswith('15')).order_by(User.id.desc()).offset(1).limit(5).all()
    # print(uu30)

    # 优化查询  load_only函数指定查询的字段；只能加载当前query的表中的某些字段，若要加载关联表的某些字段，需要使用contains_eager函数
    # uu31 = User.query.options(load_only(User.name, User.mobile)).order_by(User.id).all()
    # print(uu31)

    # 分组聚合：只能使用原生sqlalchemy写法，因为聚合的结果(中间表)无法映射到已有的模型类
    # uu32 = db.session.query(Relation.user_id, func.count(Relation.target_user_id)).group_by(Relation.user_id).all()   # 查询某user_id关注的target_user_id数量
    # print(uu32)       # 返回元祖列表，每个元素为元祖，包含查询结果表的每个字段

    # !!!关联查询!!!
    # a. 主模型类字段为relationship，从模型类字段写ForeignKey约束
    # user1 = User.query.get(1)
    # userprofile = user1.profile          # Model Object
    # print(userprofile)
    # userfollowings = user1.followings    # Model Object List
    # print(userfollowings, userfollowings[0].target_user_id)

    # b. 主模型类字段为relationship，并使用primaryjoin
    # 仅在主模型类中设置primaryjoin(User.id==foreign(UserProfile.id))

    # c. 通过sql orm 指定字段关联查询
    """
    原生SQL
    select a.relation_id, a.user_id, a.relation, b.user_id, b.user_name
    from user_relation as a inner join user_basic as b
    on a.target_user_id=b.user_id
    where b.user_id=2;
    """
    # 此时将Relation作为主表，User为从表，返回Relation对象列表
    relation_obj_list = Relation.query.join(Relation.user).options(load_only(Relation.user_id, Relation.relation), contains_eager(Relation.user).load_only(User.id, User.name)).filter(User.id == 2)
    for item in relation_obj_list:
        print(item.__dict__)
        print(item.id, item.user_id, item.relation)
        # 获取从表User的数据需要用到主表Relation中的关联属性user
        print(item.user)                    # 默认返回列表，取对象需要索引
        # print(item.user[0].name)          # uselist=True
        print(item.user.name)               # uselist=False


    return 'OK'


@app.route('/add_user')
def add_user():
    # user = User(mobile='15912345678', name='huang')
    # db.session.add(user)

    user1 = User(mobile='15112345678', name='huang1')
    user2 = User(mobile='15212345678', name='huang2')
    user3 = User(mobile='15312345678', name='huang3')
    # add_all 进行批量增添
    db.session.add_all([user1, user2, user3])
    db.session.commit()
    return 'OK'

@app.route('/update_user')
def update_user():
    # 更新   update user set is_verified=1 where id=1;
    # 方式一、
    # u = User.query.get(1)
    # u.is_verified = True
    # db.session.add(u)
    # db.session.commit()
    # 方式二、
    User.query.filter_by(id=2).update({'is_verified': True})
    db.session.commit()

    return 'OK'

@app.route('/delete_user')
def delete_user():
    # 删除   delete from user where id=1;
    # 方式一、
    # u = User.query.order_by(User.id.desc()).first()
    # db.session.delete(u)
    # db.session.commit()
    # 方式二、
    User.query.filter(User.id == 6).delete()
    db.session.commit()

    return 'OK'

@app.route('/use_transaction')
def use_transaction():
    """
    在视图中本身就是在上下午管理器环境中中，进行数据库操作时默认开启了事务
    但是独立运行时需要设置管理器环境with app.request_context(environ):
    """
    try:
        user = User(mobile='13912345678', name='hhhh1234')
        db.session.add(user)                 # 将操作生成SQL语句保存在session会话中，但并不提交执行
        db.session.flush()                   # 将当前session会话中已有sql发送给数据库执行，目的是获取执行结果，得到自增主键user.id的值
        profile = UserProfile(id=user.id)    # UserProfile表数据的新增是依赖于UserBasic表新增完成后的自增user.id的
        db.session.add(profile)
        db.session.commit()
    except Exception as e:
        print('sql operation failed--------------\n', e)
        db.session.rollback()
        return 'sql server operation failed'

    return 'OK'
