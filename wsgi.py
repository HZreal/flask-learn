#  WSGI容器
# wsgi容器调用flask App

# Gunicorn doc: https://docs.gunicorn.org/en/stable/
# Flask deployment doc: https://flask.palletsprojects.com/en/2.1.x/deploying/

from app_deployment import app





# 1. 开发模式启动
# app.run()

# 2. 生产模式启动
# gunicorn简单启动:    wsgi为主程序名称，即wsgi.py文件的名称，app为主程序里的Flask App实例
# gunicorn -b 0.0.0.0:5000 wsgi:app
# 指定4个worker:
# gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app   模式默认为同步模式
# 指定worker类型:
# gunicorn --worker-class=gevent --worker-connections=100 -w 4 -b 0.0.0.0:5000 wsgi:app   模式设置为gevent协程
# 了解更多参数启动可查看命令参数: gunicorn -h

# 如果使用应用程序工厂模式，则启动如下，
# gunicorn -w 4 -b 0.0.0.0:5000 "wsgi:create_app()"


# 指定配置文件启动，所有的指令参数都放入配置文件中，配置文件必须是python文件:
# gunicorn -c deploy/gunicorn_conf.py wsgi:app


# 查看gunicorn进程，一个master进程，其余为worker子进程
# ps -ef | grep gunicorn
# 通常这些进程id都是顺序递增的，且id最小的那个就是最初创建的master进程。关闭gunicorn只需kill掉master进程id即可









