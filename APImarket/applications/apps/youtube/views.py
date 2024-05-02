#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

"""
@Project : MoreAPI_V3
@File    : views.py
@Author  : MoreCoding多点部落
@Time    : 2023/9/8 4:28 PM
"""
import json

import requests
from sanic import Request, HTTPResponse
from sanic.views import HTTPMethodView

from core.message import CodeDict
from core.response import json_success_response, json_fail_response


async def get_youtube_video_data(video_id: str):
    """
    获取视频下载链接的方法
    """
    try:
        response = requests.get("http://8.210.17.91:8596", params={"video_id": video_id})
        if response.status_code == 200:
            return json.loads(response.text)
        return None
    except:
        return None


async def get_youtube_video_comments_data(video_id: str, max_results: int, order: str, page_token: str):
    """
    获取视频下载链接的方法
    """
    try:
        response = requests.get("http://8.210.17.91:8596/video_comments",
                                params={"video_id": video_id, "max_results": max_results, "order": order,
                                        "page_token": page_token})
        if response.status_code == 200:
            return json.loads(response.text)
        return None
    except:
        return None


async def get_youtube_search_data(keywords: str, max_results: int, order: str, page_token: str, video_type: str="any", region_code:str='US'):
    """
    获取视频下载链接的方法
    """
    try:
        response = requests.get("http://8.210.17.91:8596/search",params={"keywords": keywords, "max_results":max_results, "order":order, "page_token":page_token, "video_type":video_type, "region_code":region_code})
        if response.status_code == 200:
            return json.loads(response.text)
        return None
    except:
        return None


class VideoData(HTTPMethodView):
    """
    获取视频信息
    """

    @staticmethod
    async def get(request: Request) -> HTTPResponse:
        video_id = request.args.get("video_id", None)

        if not video_id:
            return json_fail_response(CodeDict.field_val_err)
        data = await get_youtube_video_data(video_id)
        if data:
            return json_success_response(data)
        return json_fail_response(CodeDict.fail)


class VideoCommentsData(HTTPMethodView):
    """
    获取视频评论信息
    """

    @staticmethod
    async def get(request: Request) -> HTTPResponse:
        video_id = request.args.get("video_id", None)
        max_results = request.args.get("max_results", 20)
        order = request.args.get("order", "time")
        page_token = request.args.get("page_token", "")

        if not video_id:
            return json_fail_response(CodeDict.field_val_err)
        if order == 'time':
            order = 'time'
        else:
            order = 'relevance'

        data = await get_youtube_video_comments_data(video_id, max_results=max_results, order=order,
                                                     page_token=page_token)
        if data:
            return json_success_response(data)
        return json_fail_response(CodeDict.fail)


class SearchDataView(HTTPMethodView):
    """
    搜索
    """

    @staticmethod
    async def get(request: Request) -> HTTPResponse:
        keywords = request.args.get("keywords", None)
        max_results = request.args.get("max_results", 20)
        order = request.args.get("order", "relevance")
        page_token = request.args.get("page_token", "")
        video_type = request.args.get("video_type", "any")
        region_code = request.args.get("region_code", "US")

        if not keywords:
            return json_fail_response(CodeDict.field_val_err)
        if region_code not in ['US', 'TW', 'HK', 'SG', 'JP', 'IE', 'IN', 'FR', 'CA']:
            return json_fail_response(CodeDict.field_val_err, message="暂不支持此国家序号")
        if order == 'date':
            order = 'date'
        elif order == 'rating':
            order = 'rating'
        elif order == 'viewCount':
            order = 'viewCount'
        elif order == 'title':
            order = 'title'
        elif order == 'videoCount':
            order = 'videoCount'
        else:
            order = 'relevance'

        if video_type == 'any':
            video_type = 'any'
        elif video_type == 'episode':
            video_type = 'episode'
        else:
            video_type = 'movie'

        data = await get_youtube_search_data(keywords=keywords, max_results=max_results, order=order,
                                             page_token=page_token, video_type=video_type, region_code=region_code)
        if data:
            return json_success_response(data)
        return json_fail_response(CodeDict.fail)
