import json
import re

import httpx
from sanic import Request, HTTPResponse
from sanic.views import HTTPMethodView

from app_conf import douyin_default
from applications.apps.douyin.utils import Utils, ua, get_data
from core.message import CodeDict
from core.response import json_success_response, json_fail_response


async def reset_douyin_cookie(cookie: str):
    """
    删除cookie中的msToken和ttwid
    """
    # 删除msToken及其对应值
    input_string = re.sub(r'msToken=[^;]*;', '', cookie)
    # 删除ttwid及其对应值
    input_string = re.sub(r'ttwid=[^;]*;', '', input_string)
    return f"msToken={Utils().generate_random_str(107)}; ttwid={Utils().getttwid()};" + input_string


headers = {
    'User-Agent': ua,
    'referer': 'https://www.douyin.com/',
}


class AwemeDetailView(HTTPMethodView):
    """
    作品详情
    """
    request_domain = 'https://www.douyin.com/aweme/v1/web/aweme/detail/?'

    async def get(self, request: Request) -> HTTPResponse:
        aweme_id = request.args.get('aweme_id', None)
        cookie = request.headers.get('cookie', None)
        if cookie:
            headers['Cookie'] = await reset_douyin_cookie(cookie)
        else:
            headers['Cookie'] = await reset_douyin_cookie(douyin_default)
        if not aweme_id:
            return json_fail_response(CodeDict.field_val_err)
        url = self.request_domain + Utils().getXbogus(f'aweme_id={aweme_id}&device_platform=webapp&aid=6383')
        data = await get_data(url, headers)
        return json_success_response(data)

class UserDataView(HTTPMethodView):
    """
    用户详情
    """
    request_domain = 'https://www.douyin.com/aweme/v1/web/user/profile/other/?'

    async def get(self, request: Request) -> HTTPResponse:
        sec_uid = request.args.get('sec_user_id', None)
        cookie = request.headers.get('cookie', None)
        if cookie:
            headers['Cookie'] = await reset_douyin_cookie(cookie)
        else:
            headers['Cookie'] = await reset_douyin_cookie(douyin_default)
        if not sec_uid:
            return json_fail_response(CodeDict.field_val_err)
        url = self.request_domain + Utils().getXbogus(f'sec_user_id={sec_uid}&device_platform=webapp&aid=6383')
        data = await get_data(url, headers)
        return json_success_response(data)


class UserVideoDataView(HTTPMethodView):
    """
    用户作品列表
    """
    request_domain = 'https://www.douyin.com/aweme/v1/web/aweme/post/?'

    async def get(self, request: Request) -> HTTPResponse:
        sec_uid = request.args.get('sec_user_id', None)
        count = request.args.get('count', 20)
        max_cursor = request.args.get('max_cursor', 0)
        cookie = request.headers.get('cookie', None)
        if cookie:
            headers['Cookie'] = await reset_douyin_cookie(cookie)
        else:
            headers['Cookie'] = await reset_douyin_cookie(douyin_default)
        if not sec_uid:
            return json_fail_response(CodeDict.field_val_err)
        url = self.request_domain + Utils().getXbogus(f'sec_user_id={sec_uid}&count={count}&max_cursor={max_cursor}&device_platform=webapp&aid=6383')
        data = await get_data(url, headers)
        return json_success_response(data)


class LiveRoomDataView(HTTPMethodView):
    """
    直播间信息
    """
    request_domain = 'https://live.douyin.com/webcast/room/web/enter/?'

    async def get(self, request: Request) -> HTTPResponse:
        web_rid = request.args.get('web_rid', None)
        cookie = request.headers.get('cookie', None)
        if cookie:
            headers['Cookie'] = await reset_douyin_cookie(cookie)
        else:
            headers['Cookie'] = await reset_douyin_cookie(douyin_default)
        if not web_rid:
            return json_fail_response(CodeDict.field_val_err)
        url = self.request_domain + Utils().getXbogus(f'aid=6383&device_platform=web&web_rid={web_rid}')
        data = await get_data(url, headers)
        return json_success_response(data)


class AwemeCommentDataView(HTTPMethodView):
    """
    作品评论数据
    """
    request_domain = 'https://www.douyin.com/aweme/v1/web/comment/list/?'

    async def get(self, request: Request) -> HTTPResponse:
        aweme_id = request.args.get('aweme_id', None)
        count = request.args.get('count', 20)
        cursor = request.args.get('cursor', 0)
        cookie = request.headers.get('cookie', None)
        if cookie:
            headers['Cookie'] = await reset_douyin_cookie(cookie)
        else:
            headers['Cookie'] = await reset_douyin_cookie(douyin_default)
        if not aweme_id:
            return json_fail_response(CodeDict.field_val_err)
        url = self.request_domain + Utils().getXbogus(f'aweme_id={aweme_id}&count={count}&cursor={cursor}&item_type=0&device_platform=webapp&aid=6383')
        data = await get_data(url, headers)
        return json_success_response(data)


class SearchDataView(HTTPMethodView):
    """
    搜索数据
    """
    search_data = 'https://www.douyin.com/aweme/v1/web/general/search/single/?'
    search_video = 'https://www.douyin.com/aweme/v1/web/search/item/?'
    search_user = 'https://www.douyin.com/aweme/v1/web/discover/search/?'
    search_live = 'https://www.douyin.com/aweme/v1/web/live/search/?'

    async def get(self, request: Request) -> HTTPResponse:
        keyword = request.args.get('keyword', None)
        search_type = request.args.get('search_type', "general")
        sort_type = request.args.get("sort_type", 0)
        publish_time = request.args.get("publish_time", 0)
        offset = request.args.get("offset", 0)
        count = request.args.get("count", 10)
        cookie = request.headers.get('cookie', None)
        if cookie:
            headers['Cookie'] = await reset_douyin_cookie(cookie)
        else:
            headers['Cookie'] = await reset_douyin_cookie(douyin_default)
        if not keyword:
            return json_fail_response(CodeDict.field_val_err)
        if search_type == 'video':
            search_channel = "aweme_video_web"
            SEARCH_URL = self.search_video
        elif search_type == 'user':
            search_channel = "aweme_user_web"
            SEARCH_URL = self.search_user
            sort_type = 0
            publish_time = 0
        elif search_type == 'live':
            search_channel = "aweme_live"
            SEARCH_URL = self.search_live
            sort_type = 0
            publish_time = 0
        else:
            search_channel = "aweme_general"
            SEARCH_URL = self.search_data

        if sort_type == 0 and publish_time == 0:
            is_filter_search = 0
        else:
            is_filter_search = 1

        url = SEARCH_URL + Utils().getXbogus(f'keyword={keyword}&search_channel={search_channel}&sort_type={sort_type}&publish_time={publish_time}&is_filter_search={is_filter_search}&search_source=switch_tab&offset={offset}&count={count}&device_platform=webapp&aid=6383')
        data = await get_data(url, headers)
        return json_success_response(data)