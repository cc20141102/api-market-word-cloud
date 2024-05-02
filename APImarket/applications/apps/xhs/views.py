from sanic import Request, HTTPResponse
from sanic.views import HTTPMethodView
from xhs import XhsClient, SearchSortType, SearchNoteType

from app_conf import xhs_default
from applications.apps.xhs.utils import sign
from core.message import CodeDict
from core.response import json_success_response, json_fail_response


class NoteDetailView(HTTPMethodView):
    """
    笔记详情
    """

    @staticmethod
    def get(request: Request) -> HTTPResponse:
        note_id = request.args.get("note_id", None)
        cookie = request.headers.get('cookie', None)
        if not cookie:
            cookie = xhs_default
        if not note_id:
            return json_fail_response(CodeDict.field_val_err)

        try:
            xhs_client = XhsClient(cookie, sign=sign)
        except Exception:
            return json_fail_response(CodeDict.fail, message='处理失败了')
        try:
            data = xhs_client.get_note_by_id(note_id)
        except Exception:
            return json_fail_response(CodeDict.fail, message="数据处理失败")
        return json_success_response(data)


class UserDetailView(HTTPMethodView):
    """
    作者详情
    """

    @staticmethod
    async def get(request: Request) -> HTTPResponse:
        user_id = request.args.get("user_id", None)
        cookie = request.headers.get('cookie', None)
        if not cookie:
            cookie = xhs_default

        if not user_id:
            return json_fail_response(CodeDict.field_val_err)
        try:
            xhs_client = XhsClient(cookie, sign=sign)
        except Exception:
            return json_fail_response(CodeDict.fail)
        try:
            data = xhs_client.get_user_info(user_id)
        except Exception:
            return json_fail_response(CodeDict.fail)
        return json_success_response(data)


class UserNotesView(HTTPMethodView):
    """
    用户笔记
    """

    @staticmethod
    async def get(request: Request) -> HTTPResponse:
        user_id = request.args.get("user_id", None)
        cursor = request.args.get("cursor", "")
        type = request.args.get("type", "")
        cookie = request.headers.get('cookie', None)
        if not cookie:
            cookie = xhs_default

        if not user_id:
            return json_fail_response(message="缺少user_id参数")
        try:
            xhs_client = XhsClient(cookie, sign=sign)
        except:
            return json_fail_response(message="解析失败!请检查cookie状态！")
        try:
            if type == 'collect':
                data = xhs_client.get_user_collect_notes(user_id=user_id, cursor=cursor)
            elif type == "like":
                data = xhs_client.get_user_like_notes(user_id=user_id, cursor=cursor)
            else:
                data = xhs_client.get_user_notes(user_id, cursor)
        except:
            return json_fail_response(message="解析失败")
        return json_success_response(data)


class NoteCommentView(HTTPMethodView):
    """
    笔记评论
    """

    @staticmethod
    async def get(request: Request) -> HTTPResponse:
        note_id = request.args.get("note_id", None)
        cursor = request.args.get("cursor", "")
        cookie = request.headers.get('cookie', None)
        if not cookie:
            cookie = xhs_default

        if not note_id:
            return json_fail_response(message="缺少note_id参数")
        try:
            xhs_client = XhsClient(cookie, sign=sign)
        except:
            return json_fail_response(message="解析失败!请检查cookie状态！")
        try:
            data = xhs_client.get_note_comments(note_id, cursor)
        except:
            return json_fail_response(message="解析失败")
        return json_success_response(data)


class UserNotesSubCommentView(HTTPMethodView):
    """
    笔记子评论
    """

    @staticmethod
    async def get(request: Request) -> HTTPResponse:
        note_id = request.args.get("note_id", None)
        root_comment_id = request.args.get("root_comment_id", None)
        cursor = request.args.get("cursor", "")
        num = request.args.get("num", 30)
        cookie = request.headers.get('cookie', None)
        if not cookie:
            cookie = xhs_default
        if not note_id:
            return json_fail_response(message="缺少note_id参数")
        if not root_comment_id:
            return json_fail_response(message="缺少root_comment_id参数")
        try:
            xhs_client = XhsClient(cookie, sign=sign)
        except:
            return json_fail_response(message="解析失败!请检查cookie状态！")
        try:
            data = xhs_client.get_note_sub_comments(note_id, root_comment_id=root_comment_id, cursor=cursor, num=num)
        except:
            return json_fail_response(message="解析失败")
        return json_success_response(data)


class SearchNotesView(HTTPMethodView):
    """
    搜索笔记
    """

    @staticmethod
    async def get(request: Request) -> HTTPResponse:
        keyword = request.args.get("keyword", None)
        page = request.args.get("page", 1)
        page_size = request.args.get("page_size", 20)
        sort = request.args.get("sort", "general")  # general：默认  hot:最热  new:最新
        note_type = request.args.get("note_type", "all")  # all:全部  video:视频  image: 图集

        cookie = request.headers.get('cookie', None)
        if not cookie:
            cookie = xhs_default

        if not keyword:
            return json_fail_response(message="缺少keyword参数")
        if not sort:
            sort = "general"
        if not note_type:
            note_type = "all"

        if sort == "hot":
            sort = SearchSortType.MOST_POPULAR
        elif sort == "new":
            sort = SearchSortType.LATEST
        else:
            sort = SearchSortType.GENERAL

        if note_type == "video":
            note_type = SearchNoteType.VIDEO
        elif note_type == "image":
            note_type = SearchNoteType.IMAGE
        else:
            note_type = SearchNoteType.ALL
        try:
            xhs_client = XhsClient(cookie, sign=sign)
        except:
            return json_fail_response(message="解析失败!请检查cookie状态！")
        try:
            data = xhs_client.get_note_by_keyword(keyword=keyword, page=page, page_size=page_size, sort=sort,
                                                  note_type=note_type)
        except:
            return json_fail_response(message="解析失败")
        return json_success_response(data)
