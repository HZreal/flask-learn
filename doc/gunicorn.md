# Gunicorn

## 简介

doc：https://docs.gunicorn.org/en/stable/

Gunicorn是基于unix系统，一种高性能的Python WSGI HTTP Server。用来解析HTTP请求的网关服务。

通常是在进行反向代理（如nginx），或者进行负载均衡（如 AWS ELB）和一个web 应用（比如 Django 或者 Flask）之间。
运行模型基于pre-fork worker 模型，即就是支持eventlet，也支持greenlet。

gunicorn是WSGI的实现，同时也自带web server，能直接对外提供web服务。

大部分的web app框架如Flask和Django也都带有web server。这些web应用框架专注于写app，开发时使用自带的web server，生产环境会使用如uWSGI、Gunicorn这样的高性能服务器。

## 特点

1、简单易使用；
2、能和大多数的Python Web框架兼容；
3、轻量级的资源消耗；
4、目前，gunicorn只能运行在Linux环境中，不支持windows平台。

### WSGI 与 uWSGI

WSGI即Web Server Gateway Interface。是一种协议。而不是web server，也不是web app；是为了将web和app解耦、再连接起来的一道桥梁。因为它是一种通用的接口规范，规定了web server（如Apache、Nginx）和web app（或web app框架）之间的标准规范。

uWSGI即基于WSGI、HTTP等实现的web应用服务器。

## pre-fork worker 模型

Nginx, Gunicorn, uWSGI都是这种模型的实现。(也可以说是perfork模型)


区别于 CGI 采用的fork-and-exec模式。


**worker model**

意味着这个模型有一个master进程，来管理一组worker进程；

**fork**

意味着worker进程是由master进程fork（复刻）出来的；

**pre-**

意味着在任何客户端请求到来之前，就已从master进程fork出了多个worker进程，坐等请求到来；

**执行流程**

在worker进程创建时，就被实例化了Python web app；并由worker进程监听端口、处理请求。当请求到来时，worker进程就能解析HTTP请求、调用Python web app处理、得到处理结果后，再整理成HTTP Response，通过TCP返回给客户端。

注：

- master进程不是处理请求的，只负责管理worker进程，比如对worker进程的创建、销毁、以及根据负载情况增减。

- 启动时设置的–workers参数只是worker数，而gunicorn还会自动创建一个master进程。所以，即使配置workers为1，你的app也至少有两个进程：master负责管理，worker负责处理请求。



## Gunicorn使用

启动后，gunicorn的所有worker共用一组listener（Gunicorn支持绑定多个[socket](https://so.csdn.net/so/search?q=socket&spm=1001.2101.3001.7020)，所以说是一组）。在启动worker时，worker内为每个listener创建一个WSGI server，接收HTTP请求，并调用app对象去处理请求。

### gunicorn的工作模式

一般分为同步worker使用和异步worker使用。

- **Sync Worker**

  - 同步模式，是默认的，最简单的worker模式。

  - 每个worker进程，一次只处理一个请求；如果此时又有其他请求被分配到了这个worker进程中，那只能被堵塞了，只能等待第一个请求完成。

  - 一个请求一个进程，并发时，是非常消耗CPU和内存的。
  - 适合在访问量不大、CPU密集而非I/O的情形。
  - 优点在于，即使某个worker的进程crash了，也只会影响到当前这一个请求，不会影响其他的请求。

- **Async Worker**
  - 异步worker有Gevent和Eventlet两种，都是基于Greenlet实现的。
  - 当使用了异步worker，就能同时处理多个请求，不会出现上面同步worker那样，当一个请求进行时会把后续请求都block堵塞住了。
  - 

gunicorn**支持使用不同的worker进程类型**来使用这些异步Python库（sync/gevent/eventlet/tornado等），可通过worker-class参数设置。

如单核机器上运行的gevent：

```bash
gunicorn --worker-class=gevent --worker-connections=1000 --workers=3 main:app
```

ps：

- 参数worker-connection 是对于 gevent worker 类的特殊设置，指的是单个worker线程的最大连接数，即协程数。
- （2*CPU数）+1 仍然是建议的worker数量。因为这里是单核，所以设置的是3个worker。在这种情况下，最大的并发请求数是3000（3个worker进程(共3个线程)，每个worker线程最大可达1000个连接数）

### 搭配supervisor、nginx

生产环境中，进程的启停和状态的监控最好应用supervisor之类的监控工具。然后在gunicorn的前端防止一个http proxy server，比如nginx。

### gunicorn命令参数

1)-c CONFIG,–config=CONFIG
指定一个配置文件（py文件）
2)-b BIND,–bind=BIND
与指定socket进行绑定
3)-D,–daemon
后台进程方式运行gunicorn进程
4)-w WORKERS,–workers=WORKERS
工作进程的数量
5)-k WORKERCLASS,–worker-class=WORKERCLASS
工作进程类型，包括sync（默认）,eventlet,gevent,tornado,gthread,gaiohttp
6)–backlog INT
最大挂起的连接数
7)–log-level LEVEL
日志输出等级
8)–access-logfile FILE
访问日志输出文件
9)–error-logfile FILE
错误日志输出文件

## gunicorn实现高并发

**workers多进程模式：**

启动时，就已经把worker进程预先fork出来了。当多个请求到来的时候，会轮流复用这些worker进程，从而能提高服务器的并发负载能力。

worker数量一般为（2*CPU数）+1。这样在任何时间，大概有一半的worker是在做I/O，剩下一半才是需要CPU的。每个worker都是一个加载python应用程序的UNIX进程，worker之间没有共享内存

**多线程模式：**

在多workers进程的同时，也开多线程（也就是**worker类型为gthread**），每个worker会加载一次，同一个worker生成的每个线程共享相同的内存空间

最大的并发请求数为worker进程数*线程数

workers数仍然建议（2CPU数+1）

**gevent(协程) 伪线程模式：**

worker类型为gevent，worker-connections为协程数

最大的并发请求数为（worker进程数 * 1000连接/worker)

workers数仍然建议是 (2*CPU) + 1

## Gunicorn 与 uWSGI 与 nginx

### Gunicorn

Gunicorn是使用Python实现的WSGI服务器, 直接提供了http服务, 并且在woker上提供了多种选择, gevent, eventlet这些都支持, 在多worker最大化里用CPU的同时, 还可以使用协程来提供并发支撑, 对于网络IO密集的服务比较有利.

同时Gunicorn也很容易就改造成一个TCP的服务, 比如[doge](https://github.com/zhu327/doge/tree/master/doge/gunicorn)重写worker类, 在针对长连接的服务时, 最好开启reuse_port, 避免worker进程负载不均。

### uWSGI

不同于Gunicorn, uWSGI是使用C写的, 它的[socket](https://so.csdn.net/so/search?q=socket&spm=1001.2101.3001.7020) fd创建, worker进程的启动都是使用C语言系统接口来实现的, 在worker进程处理循环中, 解析了http请求后, 使用python的C接口生成environ对象, 再把这个对象作为参数塞到暴露出来的WSGI application函数中调用. 而这一切都是在C程序中进行, 只是在处理请求的时候交给python虚拟机调用application. 完全使用C语言实现的好处是性能会好一些.

除了支持http协议, uWSGI还实现了uwsgi协议, 一般我们会在uWSGI服务器前面使用Nginx作为负载均衡, 如果使用http协议, 请求在转发到uWSGI前已经在Nginx这里解析了一遍, 转发到uWSGI又会重新解析一遍. uWSGI为了追求性能, 设计了uwsgi协议, 在Nginx解析完以后直接把解析好的结果通过uwsgi协议转发到uWSGI服务器, uWSGI拿到请求按格式生成environ对象, 不需要重复解析请求. 如果用Nginx配合uWSGI, 最好使用uwsgi协议来转发请求.

除了是一个WSGI服务器, uWSGI还是一个开发框架, 它提供了缓存, 队列, rpc等等功能, 在github找找就会发现有人用它的缓存写了一个Django cache backend, 用它的队列实现异步任务这些东西, 但是用了这些东西技术栈也就跟uWSGI绑定在一起, 所以一般也只是把uWSGI当作WSGI服务器来用。

### nginx

使用多个进程监听同一端口就绕不开惊群这个话题, fork子进程, 子进程共享listen socket fd, 多个子进程同时accept阻塞, 在请求到达时内核会唤醒所有accept的进程, 然而只有一个进程能accept成功, 其它进程accept失败再次阻塞, 影响系统性能, 这就是惊群. Linux 2.6内核更新以后多个进程accept只有一个进程会被唤醒, 但是如果使用[epoll](https://so.csdn.net/so/search?q=epoll&spm=1001.2101.3001.7020)还是会产生惊群现象.

Nginx为了解决epoll惊群问题, 使用进程间互斥锁, 只有拿到锁的进程才能把listen fd加入到epoll中, 在accept完成后再释放锁.

但是在高并发情况下, 获取锁的开销也会影响性能, 一般会建议把锁配置关掉. 直到Nginx 1.9.1更新支持了socket的`SO_REUSEPORT`选项, 惊群问题才算解决, listen socket fd不再是在master进程中创建, 而是每个worker进程创建一个通过`SO_REUSEPORT` 选项来复用端口, 内核会自行选择一个fd来唤醒, 并且有负载均衡算法.

Gunicorn与uWSGI都支持reuse_port选项, 在使用时可以通过压测来评估一下reuse_port是否能提升性能.

一般我们会在Gunicorn/uWSGI前面再加一层Nginx, 这样做的原因有一下几点：

1. 做负载均衡
2. 静态文件处理能力强
3. 更安全
4. 扛并发
