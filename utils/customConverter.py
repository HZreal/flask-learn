from werkzeug.routing import BaseConverter


# BaseConverter 为转换器基类


class MobileNumberConverter(BaseConverter):
    """
    自定义手机号格式转换器
    """
    regex = r'1[3-9]\d{9}'


class CodeConverter(BaseConverter):
    pass


