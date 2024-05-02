import http.cookies

from bilibili_api import video, ArgsException, Credential, user, search, comment
from sanic import Request, HTTPResponse
from sanic.views import HTTPMethodView

from app_conf import bilibili_default
from core.message import CodeDict
from core.response import json_fail_response, json_success_response


class AwemeDetailView(HTTPMethodView):
    """
    获取视频信息
    """

    @staticmethod
    async def get(request: Request) -> HTTPResponse:
        bvid = request.args.get("bvid", None)
        if not bvid:
            return json_fail_response(CodeDict.field_val_err)
        try:
            v = video.Video(bvid=bvid)
            data = await v.get_info()
        except ArgsException as e:
            return json_fail_response(CodeDict.field_val_err, message="请检查BVID是否正确")
        return json_success_response(data)


class AwemeDownloadView(HTTPMethodView):
    """
    视频下载信息
    """

    @staticmethod
    async def get(request: Request) -> HTTPResponse:
        bvid = request.args.get("bvid", None)
        cookie = request.headers.get('cookie', None)
        if not cookie:
            cookie = bilibili_default
        else:
            cookie = cookie
        if not bvid:
            return json_fail_response(CodeDict.field_val_err)
        # 使用SimpleCookie对象解析Cookie字符串
        cookie = http.cookies.SimpleCookie(cookie)
        cookie_dict = {key: morsel.value for key, morsel in cookie.items()}
        if not cookie_dict['buvid3'] or not cookie_dict['SESSDATA'] or not cookie_dict['bili_jct']:
            return json_fail_response(CodeDict.field_val_err,
                                      message="请检查cookie的完整性，至少包含buvid3、SESSDATA、bili_jct")
        try:
            # 实例化 Credential 类
            credential = Credential(sessdata=cookie_dict['SESSDATA'], bili_jct=cookie_dict['bili_jct'],
                                    buvid3=cookie_dict['buvid3'])
            v = video.Video(bvid=bvid, credential=credential)
            download_url_data = await v.get_download_url(0)
            detecter = video.VideoDownloadURLDataDetecter(data=download_url_data)
            streams = detecter.detect_best_streams()
            if detecter.check_flv_stream() == True:
                # FLV 流下载
                data = {
                    "message": "FLV 流下载,可直接更改格式",
                    "url": streams[0].url
                }
            else:
                data = {
                    "message": "MP4 流下载,可直接更改格式",
                    "video_url": streams[0].url,
                    "audio_url": streams[1].url
                }
        except ArgsException as e:
            return json_fail_response(CodeDict.field_val_err, message="请检查BVID是否正确")
        return json_success_response(data)


class UserALLPostView(HTTPMethodView):
    """
    获取用户所有动态
    """

    @staticmethod
    async def get(request: Request) -> HTTPResponse:
        user_id = request.args.get("user_id", None)
        if not user_id:
            return json_fail_response(CodeDict.field_val_err)
        # 实例化
        u = user.User(user_id)
        # 用于记录下一次起点
        offset = 0
        # 用于存储所有动态
        dynamics = []
        # 无限循环，直到 has_more != 1
        while True:
            # 获取该页动态
            page = await u.get_dynamics(offset)
            if 'cards' in page:
                # 若存在 cards 字段（即动态数据），则将该字段列表扩展到 dynamics
                dynamics.extend(page['cards'])
            if page['has_more'] != 1:
                # 如果没有更多动态，跳出循环
                break
            # 设置 offset，用于下一轮循环
            offset = page['next_offset']

        return json_success_response(dynamics)


class SearchView(HTTPMethodView):
    """
    搜索
    """

    @staticmethod
    async def get(request: Request) -> HTTPResponse:
        keyword = request.args.get("keyword", None)
        search_type = request.args.get("search_type", "VIDEO")
        order_type = request.args.get("order_type", None)
        order_sort = request.args.get("order_sort", 0)
        page = request.args.get("page", 1)
        if not keyword:
            return json_fail_response(CodeDict.field_val_err)

        if search_type == "VIDEO":
            search_type = search.SearchObjectType.VIDEO
            if order_type == "CLICK":
                order_type = search.OrderVideo.CLICK
            elif order_type == "PUBDATE":
                order_type = search.OrderVideo.PUBDATE
            elif order_type == "DM":
                order_type = search.OrderVideo.DM
            elif order_type == "STOW":
                order_type = search.OrderVideo.STOW
            elif order_type == "SCORES":
                order_type = search.OrderVideo.SCORES
            else:
                order_type = search.OrderVideo.TOTALRANK
        elif search_type == "BANGUMI":
            search_type = search.SearchObjectType.BANGUMI
        elif search_type == "FT":
            search_type = search.SearchObjectType.FT
        elif search_type == "LIVE":
            search_type = search.SearchObjectType.LIVE
            if order_type == "NEWLIVE":
                order_type = search.OrderLiveRoom.NEWLIVE
            else:
                order_type = search.OrderLiveRoom.ONLINE
        elif search_type == "ARTICLE":
            search_type = search.SearchObjectType.ARTICLE
            if order_type == 'CLICK':
                order_type = search.OrderArticle.CLICK
            elif order_type == 'PUBDATE':
                order_type = search.OrderArticle.PUBDATE
            elif order_type == 'ATTENTION':
                order_type = search.OrderArticle.ATTENTION
            elif order_type == 'SCORES':
                order_type = search.OrderArticle.SCORES
            else:
                order_type = search.OrderArticle.TOTALRANK
        elif search_type == "TOPIC":
            search_type = search.SearchObjectType.TOPIC
        elif search_type == "USER":
            search_type = search.SearchObjectType.USER
            if order_type != "FANS":
                order_type = search.OrderUser.LEVEL
            else:
                order_type = search.OrderUser.FANS
        elif search_type == "LIVEUSER":
            search_type = search.SearchObjectType.LIVEUSER
        else:
            search_type = search.SearchObjectType.PHOTO

        try:
            data = await search.search_by_type(keyword, search_type=search_type,
                                               order_type=order_type,order_sort=order_sort,
                                               page=page)
        except ArgsException as e:
            return json_fail_response(CodeDict.field_val_err, message="搜索失败")
        return json_success_response(data)


class CommentsDataView(HTTPMethodView):
    """
    获取评论
    """
    @staticmethod
    async def get(request:Request) -> HTTPResponse:
        aid = request.args.get("aid", None)
        if not aid:
            return json_fail_response(CodeDict.field_val_err)
        # 存储评论
        comments = []
        # 页码
        page = 1
        # 当前已获取数量
        count = 0
        try:
            while True:
                # 获取评论
                c = await comment.get_comments(int(aid), comment.CommentResourceType.VIDEO, page)
                if c['replies']:
                    # 存储评论
                    comments.extend(c['replies'])
                    # 增加已获取数量
                    count += c['page']['size']
                    # 增加页码
                    page += 1

                if count >= c['page']['count']:
                    # 当前已获取数量已达到评论总数，跳出循环
                    break
        except:
            return json_fail_response()
        return json_success_response(comments)