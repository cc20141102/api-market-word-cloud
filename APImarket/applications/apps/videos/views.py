from sanic import Request, HTTPResponse
from sanic.views import HTTPMethodView

from applications.apps.videos.utils import video_parse_main
from core.message import CodeDict
from core.response import json_fail_response, json_success_response
from libs.logger import LoggerProxy

logger: LoggerProxy = LoggerProxy(__name__)


class VideoView(HTTPMethodView):
    """
    短视频解析
    """

    @staticmethod
    async def get(request: Request) -> HTTPResponse:
        share_text = request.args.get('share_text', None)
        if not share_text:
            return json_fail_response(CodeDict.no_field)
        try:
            data = await video_parse_main(share_text)
        except:
            return json_fail_response(message="解析失败")
        if not data:
            return json_fail_response(message="解析失败")
        return json_success_response(data)
