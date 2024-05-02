from __future__ import annotations

from sanic import Blueprint

from .douyin.router import router as douyin_router
from .videos.router import router as video_router
from .xhs.router import router as xhs_router
from .ks.router import router as ks_router
from .bilibili.router import router as bilibili_router
from .youtube.router import router as youtube_router

ROUTER_GROUP = Blueprint.group(douyin_router, video_router, xhs_router, ks_router, bilibili_router,youtube_router, url_prefix="/api")
