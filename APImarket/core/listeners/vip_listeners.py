#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

"""
@Project : MoreAPI_V3
@File    : vip_listeners.py
@Author  : MoreCoding多点部落
@Time    : 2023/9/15 5:15 PM
"""
import asyncio
import time
from asyncio.base_events import BaseEventLoop
from datetime import datetime, timedelta

from sanic import Sanic

from applications.models import User
from .base import BaseListener
from libs.logger import LoggerProxy

logger = LoggerProxy(__name__)


async def check_user_vip():
    while True:
        # 获取当前时间的时间戳
        current_timestamp = int(time.time())
        # 查询模型中是否有过期数据
        expired_data = await User.filter(vip_exp__lte=current_timestamp).all()
        # 处理过期数据，这里可以根据需求进行操作
        for data in expired_data:
            data.is_vip = False
            data.vip_exp = 0
            await data.save()
        # 等待到第二天的0点10分
        now = datetime.now()
        tomorrow = datetime(now.year, now.month, now.day) + timedelta(days=1)
        next_run_time = tomorrow.replace(hour=0, minute=30)
        # 计算等待时间
        wait_seconds = (next_run_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)

class VIPListener(BaseListener):
    """VIP过期监听"""



    async def after_server_start(self, app: Sanic, loop: BaseEventLoop) -> None:
        """
        创建定时任务，检查是否有用户的VIP过期，然后取消该用户的VIP
        """
        asyncio.create_task(check_user_vip())


    async def before_server_stop(self, app: Sanic, loop: BaseEventLoop) -> None:
        """释放连接"""

