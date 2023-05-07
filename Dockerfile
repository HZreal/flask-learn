# 基于 Ubuntu 20.04 和 Python 3.8
FROM ubuntu:20.04

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.8 \
        python3-pip \
        && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# 复制代码到容器中
COPY . /app
WORKDIR /app

# 环境变量
FLASK_APP = docker_app.py
FLASK_ENV = development
FLASK_DEBUG = 0

# 暴露服务端口
EXPOSE 5000

# 启动 Flask 服务
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
