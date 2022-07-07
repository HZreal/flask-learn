# Flask Resource Code Parse

## 核心之werkzeug模块

Flask自身并没有实现WSGI，而是依赖werkzeug来实现WSGI程序。

在开发时，我们使用flask run命令启动Flask，其中服务端程序就是由Werkzeug提供的，应用程序就是Flask中程序实例app。

在生产环境中，通常不在使用Werkzeug提供的WSGI程序，而是需要用一个更强健，性能更高的WSGI服务器。这些 WSGI 服务器也被称为 WSGI 容器（Standalone WSGI Container），因为它们可以高效的处理HTTP请求，调用我们编写的应用程序。

这些WSGI服务器有很多选择，比如:
* gunicorn(http://gunicorn.org/）
* uWSGI(http://uwsgi-docs.readthedocs.io/en/atest/）
* Gevet(http://www.gevent.org/)
* Waitress(https://docs.pylonsproject.org/projects/waitress/en/latest/)

werkzeug不是一个web服务器，也不是一个web框架，而是一个工具包。官方的介绍说是一个WSGI工具包，它可以作为一个Web框架的服务端库， 因为它封装好了很多Web框架的东西，例如 Request，Response等等。安装flask时会依赖的安装好werkzeug。
