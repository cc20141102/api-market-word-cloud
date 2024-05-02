#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

"""
@Project : MoreAPI_V3
@File    : router.py
@Author  : MoreCoding多点部落
@Time    : 2023/9/8 4:28 PM
"""


from sanic import Blueprint

from applications.apps.youtube.views import VideoData, VideoCommentsData, SearchDataView

router: Blueprint = Blueprint('youtube', url_prefix='youtube')

router.add_route(VideoData.as_view(), "/video_data", name="youtube_video_data")
router.add_route(VideoCommentsData.as_view(), "/video_comments", name="youtube_video_comments")
router.add_route(SearchDataView.as_view(), "/search", name="youtube_search")