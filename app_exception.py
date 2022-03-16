from flask import Flask, request, abort

app = Flask(__name__)


# errorhandler 装饰器
# 参数 code_or_exception – HTTP的错误状态码或指定异常
@app.errorhandler(500)
def handle_500_exception(e):   # 自定义异常处理，参数e为捕获的异常对象
    print(e)
    return 'Server Error'     # 给浏览器返回状态码200

@app.errorhandler(ZeroDivisionError)
def handle_zero_division_exception(e):
    print(e)    # 参数e为异常对象 division by zero
    return 'ZeroDivision Error'



@app.route('/abort_exception')
def abort_exception():               # 抛出异常响应
    channel_id = request.args.get('channel_id')
    if channel_id is None:
        # 未传参数，直接错误返回

        # abort抛出一个给定状态代码的HTTPException或者指定响应
        abort(400)  # bad request 400

    return 'request OK'


@app.route('/capture_exception')
def capture_exception():

    # a = 1 / 0     # 捕获到ZeroDivisionError异常， 会执行自定义异常处理函数handle_zero_division_exception

    abort(500)      # 捕获到500异常， 会执行自定义异常处理函数handle_500_exception

    return 'capture exception and handle'










