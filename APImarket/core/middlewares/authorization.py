# coding: utf-8
import json
import time
from datetime import datetime

from sanic import Request, HTTPResponse

from applications.models import User
from .base import BaseMiddleware
from libs.logger import LoggerProxy
from ..message import CodeDict
from ..response import json_fail_response

logger: LoggerProxy = LoggerProxy(__name__)

exclude_login_apis = ['user_register', 'user_login', 'user_active', 'user_reset_password', 'user_reset_token']  # 排除需要登录的路由名称
exclude_request_remain_apis = ['user']  # 排除需要扣除积分的总路由名称

vip_request_apis = ['youtube']

class AuthorizationMiddleware(BaseMiddleware):
    """验证登录和扣除积分中间件"""

    async def before_request(self, request: Request) -> None:
        """
        请求前验证是否登录
        """
        # 获取请求链接的路由名称
        if not request.name:
            return json_fail_response(CodeDict.dont_request)
        # 获取路由名称
        last_dot_index = request.name.rfind('.')
        if not last_dot_index != -1:
            return json_fail_response(CodeDict.dont_request)
        extracted_part = request.name[last_dot_index + 1:]
        # 判断是否需要登录
        if extracted_part in exclude_login_apis:
            print("无需登录")
            pass
        else:
            # 需要获取用户的请求头的authorization
            if not request.token:
                return json_fail_response(CodeDict.no_authorization)
            # 获取用户
            user = await User.filter(authorization_token=request.token)
            if not user:
                return json_fail_response(CodeDict.authorization_fail)
            user = user[0]
            # 获取总路由名称  判断是否需要验证剩余请求次数
            first_dot_index = request.name.find('.')
            second_dot_index = request.name.find('.', first_dot_index + 1)
            if not first_dot_index != -1 and not second_dot_index != -1:
                pass
            else:
                app_name = request.name[first_dot_index + 1:second_dot_index]
                if app_name not in exclude_request_remain_apis:
                    if not user.status:
                        return json_fail_response(message="已封禁")
                    if not user.is_active:
                        return json_fail_response(message="未激活")
                    if user.requests_remain <= 0:
                        return json_fail_response(message="请求次数不足")
                    # 判断是否vip解析的app
                    if app_name in vip_request_apis:
                        if not user.is_vip:
                            return json_fail_response(message="此接口需充值VIP方可使用")

    async def before_response(self, request: Request, response: HTTPResponse) -> None:
        # 扣除相应积分
        # 获取请求链接的路由名称
        if not request.name:
            return json_fail_response(CodeDict.dont_request)
        # 获取总路由名称  判断是否需要进行扣除请求次数
        first_dot_index = request.name.find('.')
        second_dot_index = request.name.find('.', first_dot_index + 1)
        if not first_dot_index != -1 and not second_dot_index != -1:
            pass
        app_name = request.name[first_dot_index + 1:second_dot_index]
        if app_name in exclude_request_remain_apis:
            pass
        else:
            # 判断返回数据
            if not response.status == 200:
                pass
            else:
                result = json.loads(response.body)
                if result['code'] == 200 and not result['data'] == {}:
                    user = await User.get(authorization_token=request.token)
                    user.requests_remain -= 1
                    await user.save()
                else:
                    pass