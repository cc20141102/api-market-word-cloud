# coding: utf-8
import json
import time
from datetime import datetime

from sanic import Request, HTTPResponse

from .base import BaseMiddleware
from libs.logger import LoggerProxy

logger: LoggerProxy = LoggerProxy(__name__)


class LoggerMiddleware(BaseMiddleware):
    """日志中间件"""

    async def before_request(self, request: Request) -> None:
        now_time = datetime.now()
        host = request.headers.get('X-Forwarded-For', request.ip)
        request_url = request.method + " " + request.url
        logger.info(f"Request  IP为 {host} 的网友请求了 {request_url}")

    async def before_response(self, request: Request, response: HTTPResponse) -> None:
        now_time = datetime.now()
        host = request.headers.get('X-Forwarded-For', request.ip)
        if response.status == 200:
            logger.info(f"Response  IP为 {host} 的网友的请求了  SUCCESS")
        else:
            logger.error(f"Response   IP为 {host} 的网友的请求了  ERROR")


