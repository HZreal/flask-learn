import typing
from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit, Namespace, leave_room, join_room, close_room


# TODO
# flask_socketio包所依赖的异步服务可以从三个选项中选择：
#     1. eventlet 性能最佳，支持长轮询和WebSocket传输  (首选)
#     2. gevent 高性能，略低于eventlet ，支持长轮询传输，但没有原生WebSocket支持，若添加对WebSocket的支持，有两种方式:
#             a. 使用带有WebSocket功能的uWSGI Web服务器  (次选)
#             b. 安装gevent-websocket包为gevent添加了WebSocket支持  (次次选)
#     3. 基于Werkzeug的Flask开发服务器，但仅供开发使用，只能用于简化开发工作流程，而不是用于生产  (后选)

# 如果使用多个进程，则必须配置消息队列服务以允许服务器协调广播等操作。支持的队列是Redis、RabbitMQ、 Kafka以及Kombu包支持的任何其他消息队列

#  TODO
#  部署 https://flask-socketio.readthedocs.io/en/latest/deployment.html#
#     Embedded Server
#     Gunicorn Web Server
#     uWSGI Web Server
#     Using nginx as a WebSocket Reverse Proxy
#     Using Multiple Workers
#     Emitting from an External Process


app = Flask(__name__, template_folder='templates/')


# 基于flask app 创建socketIO对象的两种方式
socketio = SocketIO(app)
# socketio = SocketIO()
# socketio.init_app(app, cors_allowed_origins='*')


# 建立连接是有3个请求:  默认请求路径是`/socket.io`，注意命名空间并不会在路径中，而是在参数中传递。
#   第1个请求是polling，GET方式携带EIO、transport、随机串t，服务端确认建立连接，返回sid、pingInterval、pingTimeout、upgrades
#   请求时有提供namespace，则POST请求，服务器接收到请求后会将该客户端再加入到对应命名空间中
#   第3个请求是websocket握手请求，握手成功
# ws连接时的回调
@socketio.on('connect')          # ws://127.0.0.1:5000
def ws_connect():
    print('a client connected in main namespace --------')

@socketio.on('connect', namespace='/chat')       # ws://127.0.0.1:5000/chat ， namespace 实现 websocket 的多路复用，连接过程不会受之影响
def ws_connect():
    print('a client connected in chat namespace--------')

# ws断开连接时的回调
@socketio.on('disconnect')
def ws_disconnect():
    print('a client disconnected --------')

# ws连接异常时的回调
@socketio.on_error(namespace='chat')
def error_handler(e):
    print('chat event error ---- ', e)
    raise RuntimeError()

@socketio.on_error_default       # handles all namespaces without an explicit error handler
def default_error_handler(e):
    print(e)
    # 可以使用request.event变量检查当前请求的消息和数据参数，这对于事件处理程序外部的错误记录和调试很有用
    print(request.event["message"])       # "my error event"
    print(request.event["args"])          # (data, )



# 未命名事件，也可以说事件名为message，仅处理客户端没有指定事件名、或者事件名为message的请求
@socketio.on('message', namespace='/chat')
def handle_message(message):
    print('message ---->  ', type(message), message)

    # send方法，不指定事件名，将数据发送给此请求的原事件
    if isinstance(message, dict):
        send(message, json=True)         # 若是json数据，可说明
    else:
        send(message)

@socketio.on('json', namespace='/chat')
def handle_json(json):
    print('type ----', type(json))
    print('on json event, received data is ', json)

# 注册事件custom_event，仅处理事件custom_event
@socketio.on('custom_event', namespace='/chat')
def handle_custom_event(data):
    print('type ----', type(data))
    print('on custom_event event, received data is ', data)


# emit函数解析
def _emit(event_name: str, data: dict, namespace: str='', broadcast: bool=False, callback: typing.Callable=None, to: str='', include_self: bool=True):
    """

    :param event_name:        事件名
    :param data:              待发数据，字典
    :param namespace:         命名空间
    :param broadcast:         是否广播，默认是，发给本命名空间，且包括发送者
    :param callback:          回调函数，服务端emit后，当客户端确认收到后，服务端的调用
    :param to:                发送至某个room内的所有人，
    :param include_self:      广播时是否发给自己，默认是
    :return:
    """

def ack():
    print('emited data has been received by client')
    # print(ack_msg)

# 注册news事件
@socketio.on('news', namespace='/chat')
def handle_news(data):
    print('on news event, received data is ---->  ', type(data), data)
    emit('news', data, callback=ack())        # callback确认回调，确认客户端收到了消息

# 注册news1事件，处理函数return，使客户端可以成功回调
# 处理函数返回的任何值都将作为回调函数中的参数传递给客户端
@socketio.on('news1', namespace='/chat')
def handle_news1(data):
    print('on news1 event, received data: ', data)
    if data is not None:
        return 'ACK for client, notice client that server received', True        # return返回值被客户端emit的回调函数接收，  emit(event, data, (res) => {})中res接收，即server端告知client端我已接收
    else:
        return 'ACK for client, notice client that data error or server not received', False

# 注册news2事件，接收多个数据
@socketio.on('news2', namespace='/chat')
def handle_news2(arg1, arg2, arg3):
    print('on news2 event, received three args: ', arg1, arg2, arg3)
    emit("news2", (arg1, arg2, arg3))       # 发送具有多个数据的事件

# 注册news3事件，进行广播
@socketio.on('news3', namespace='/chat')
def handle_news3(data):
    print('on news3 event, received data is ---->  ', type(data), data)
    emit('news3', data, broadcast=True, include_self=True)        # broadcast进行广播，连接到命名空间的所有客户端都会接收，默认包括发件人




# 对于装饰器语法不方便时，可以使用on_event替用
def my_function_handler(data):
    pass
socketio.on_event('_event', my_function_handler, namespace='/test')


# 类的方式处理一个namespace下的操作
class RoomNamespace(Namespace):
    room_users = {'chat': []}

    def on_connect(self):
        print('a client connected in room namespace ----!!!!!!!----')
        print('connect SessionID -->  ', request.sid)

    def on_disconnect(self):
        print('a client disconnected --------')

    # 事件名必须以on_开头
    def on_my_event(self, data):
        emit('my_response', data)

    def on_join(self, data):
        print('on join event, received data is ---->  ', type(data), data)

        username = data['username']
        room = 'chat'
        self.room_users[room].append(username)
        join_room(room)
        emit('join_res', username+'加入房间', to=room)
        return True

    def on_leave(self, data):
        print('on leave event, received data is ---->  ', type(data), data)

        username = data['username']
        room = 'chat'
        self.room_users[room].remove(username)
        leave_room(room)
        emit('leave_res', username + '离开房间', to=room)
        return True

socketio.on_namespace(RoomNamespace('/room'))

@app.route('/index')
def index():
    # 返回页面
    return render_template('index1.html')

if __name__ == "__main__":
    socketio.run(app)




