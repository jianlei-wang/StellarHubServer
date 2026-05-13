"""
自定义异常处理模块
"""

class APIException(Exception):
    """
    基础 API 异常类
    """
    def __init__(self, msg: str, code: int = 400):
        self.msg = msg
        self.code = code
        super().__init__(msg)
