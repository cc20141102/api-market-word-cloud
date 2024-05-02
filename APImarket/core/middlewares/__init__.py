# coding: utf-8

from __future__ import annotations

from .authorization import AuthorizationMiddleware
from .base import BaseMiddleware
from .logger import LoggerMiddleware
from .timer import TimerMiddleware
from .redis import RedisMiddleware


MIDDLEWARE_TUPLE: tuple[type[BaseMiddleware], ...] = (
    TimerMiddleware,
    RedisMiddleware,
    AuthorizationMiddleware,
    LoggerMiddleware,
)
