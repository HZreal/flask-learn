# Supervisor

## 简介

doc：http://supervisord.org

Supervisor是 Python 开发的一个 C/S 服务。是 Linux/Unix 系统下的进程管理工具。它可以很方便的监听、启动、停止、重启一个或多个进程。用Supervisor管理的进程，当一个进程意外被杀死，supervisort监听到进程死后，会自动将它重新拉起，很方便的做到进程自动恢复的功能，不再需要自己写shell脚本来控制。

当执行一些需要以守护进程方式执行的程序，比如一个后台任务，常用它来做进程管理。
Supervisor 还能友好的管理程序在命令行上输出的日志，可以将日志重定向到自定义的日志文件中

gunicorn是一个进程，很有可能因为一些原因被关闭或者阻塞，为了保证gunicorn进程正常运行，需要使用看护进程插件。于是supervisor可以解决这个问题。

Supervisor将一个普通的命令行进程变为后台 daemon 进程，并监控其状态，异常退出时能自动重启。它是通过 fork/exec 的方式把这些被管理的进程当作 supervisor 的子进程来启动。当子进程挂掉的时候，主进程可以准确获取子进程挂掉的信息，可以选择是否启动和报警。supervisor 还提供了一个功能，可以为 supervisord 或者每个子进程，设置一个非 root 的用户，这个普通用户也可以管理它对应的进程。


**服务端进程supervisord**

supervisor 的服务器端称为 supervisord，主要负责启动自身及其监控的子进程，响应客户端命令，重启异常退出的子进程，记录子进程stdout和stderr输出，生成和处理子进程生命周期中的事件。可以在配置文件中配置相关参数，包括supervisor自身的状态，其管理的各个子进程的相关属性等。

**客户端supervisorctl**

提供了一个类shell的接口（即命令行）来操作supervisor服务端。通过supervisorctl，可以连接到supervisord服务进程，获得服务进程监控的子进程状态，可以执行 stop、start、restart 等命令，来对这些子进程进行管理。

## 安装

ubuntu下，

```bash
apt install supervisor
```

```python
pip install supervisor
```

创建配置文件

运行**echo_supervisord_conf**命令输出默认的配置项

```bash
sudo echo_supervisord_conf > /etc/supervisor/supervisord.conf
```

配置文件中，include选项（与nginx中的一样）指明包含的其他配置文件，设置为files =/etc/supervisor/conf.d/*.conf表示加载当前目录下所有的.conf配置文件。

注意：centOS下配置文件为.ini

## 启动并查看

```bash
supervisord -c /etc/supervisord.conf
```

查看 supervisord 是否在运行：

```bash
ps aux | grep supervisord
```

用supervisorctl来管理supervisor

```bash
supervisorctl
若配置inet_http_server中设置了用户名密码，则supervisorctl执行以下操作时需要参数-u, -p认证

> status                          # 查看程序状态
> reload                          # 重新加载
> update                          # 重启配置文件修改过的程序
> supervisorctl start all / aa    # 启动所有/指定的程序进程

> start apscheduler               # 启动 apscheduler 单一程序
> stop process:*                  # 关闭 process组 程序
> start process:*                 # 启动 process组 程序
> restart process:*               # 重启 process组 程序

```
