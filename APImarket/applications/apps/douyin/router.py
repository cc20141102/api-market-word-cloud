# coding: utf-8

from sanic import Blueprint

from applications.apps.douyin.views import AwemeDetailView, UserDataView, UserVideoDataView, LiveRoomDataView, \
    AwemeCommentDataView, SearchDataView

router: Blueprint = Blueprint('douyin', url_prefix='douyin')


router.add_route(AwemeDetailView.as_view(), "/video_data", name="douyin_aweme_detail")
router.add_route(UserDataView.as_view(), "/user_data", name='douyin_user_data')
router.add_route(UserVideoDataView.as_view(), "/user_video_data", name='douyin_user_video_data')
router.add_route(LiveRoomDataView.as_view(), "/live_room", name='douyin_live_room_data')
router.add_route(AwemeCommentDataView.as_view(), "/video_comment", name='douyin_aweme_comment_data')
router.add_route(SearchDataView.as_view(), "/search", name='douyin_search_data')
