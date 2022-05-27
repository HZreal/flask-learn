import typing

from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit, close_room, join_room

app = Flask(__name__)


# 基于flask app 创建socketIO对象的两种方式
socketio = SocketIO(app)
# socketio = SocketIO()
# socketio.init_app(app, cors_allowed_origins='*')



# 监听ws连接时的回调
@socketio.on('connect', namespace='namespace')
def ws_connect():
    print('a client connected --------')

# 监听ws断开连接时的回调
@socketio.on('disconnect')
def ws_disconnect():
    print('a client disconnected --------')


# 未定义事件，接收msg
@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)

# 未定义事件，接收JSON
@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))

# 定义事件rec_msg_event，接收msg
@socketio.on('my event')
def handle_my_custom_event(data):
    print('type ----', type(data))
    print('on my custom event, received json: ' + data)

@socketio.on('my_event')
def handle_my_custom_event(arg1, arg2, arg3):
    print('on my_event, received args: ' + arg1 + arg2 + arg3)




def hhh(event_name: str, data: dict, namespace: str='', broadcast: bool=False, callback: typing.Callable=None, to: str='', include_self: bool=True):
    """

    :param event_name:        事件名
    :param data:              待发数据，字典
    :param namespace:         命名空间
    :param broadcast:         是否广播，默认否，发给原事件客户
    :param callback:          回调函数
    :param to:                发送至，
    :param include_self:      广播时是否发给自己，默认是
    :return:
    """

@socketio.on('message')
def handle_message(message):
    print('message ----', message)
    send(message)

@socketio.on('json')
def handle_json(json):
    print('json ----', json)
    send(json, json=True)

@socketio.on('news', namespace='/namespace')
def handle_my_custom_event(json):
    print('on my event ---->>', json)
    emit('news', json)


@app.route('/index')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    socketio.run(app)

