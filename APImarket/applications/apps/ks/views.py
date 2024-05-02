from sanic import HTTPResponse, Request
from sanic.views import HTTPMethodView

from app_conf import ks_default
from applications.apps.ks.utils import get_aweme_detail, ks_web_request
from core.message import CodeDict
from core.response import json_success_response, json_fail_response


class AwemeDetailView(HTTPMethodView):
    """
    作品详情
    """

    @staticmethod
    async def get(request: Request) -> HTTPResponse:
        aweme_id = request.args.get("video_id", None)
        cookie = request.headers.get('cookie', None)
        if not aweme_id:
            return json_fail_response(CodeDict.field_val_err)
        if cookie:
            cookie = cookie
        else:
            cookie = ks_default
        data = await get_aweme_detail(aweme_id, cookie)
        return json_success_response(data)


class UserPostDataView(HTTPMethodView):
    """
    主页作品数据
    """
    query = {
        "operationName":"visionProfilePhotoList",
        "query":"fragment photoContent on PhotoEntity {\n  __typename\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  commentCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n}\n\nfragment recoPhotoFragment on recoPhotoEntity {\n  __typename\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  commentCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n}\n\nfragment feedContent on Feed {\n  type\n  author {\n    id\n    name\n    headerUrl\n    following\n    headerUrls {\n      url\n      __typename\n    }\n    __typename\n  }\n  photo {\n    ...photoContent\n    ...recoPhotoFragment\n    __typename\n  }\n  canAddComment\n  llsid\n  status\n  currentPcursor\n  tags {\n    type\n    name\n    __typename\n  }\n  __typename\n}\n\nquery visionProfilePhotoList($pcursor: String, $userId: String, $page: String, $webPageArea: String) {\n  visionProfilePhotoList(pcursor: $pcursor, userId: $userId, page: $page, webPageArea: $webPageArea) {\n    result\n    llsid\n    webPageArea\n    feeds {\n      ...feedContent\n      __typename\n    }\n    hostName\n    pcursor\n    __typename\n  }\n}\n",
        "variables":{
            "page":"profile",
            "pcursor":"",
            "userId":""
        }
    }
    async def get(self, request:Request) -> HTTPResponse:
        user_id = request.args.get("user_id", None)
        pcursor = request.args.get("cursor", "")
        cookie = request.headers.get('cookie', None)
        if cookie:
            cookie = cookie
        else:
            cookie = ks_default
        if not user_id:
            return json_fail_response(CodeDict.field_val_err)

        self.query['variables']['pcursor'] = pcursor
        self.query['variables']['userId'] = user_id

        try:
            data = await ks_web_request(self.query, cookie)
        except:
            return json_fail_response(CodeDict.fail, message="网络请求失败")
        return json_success_response(data)


class UserDataView(HTTPMethodView):
    """
    用户数据
    """
    query = {
        "operationName":"visionProfile",
        "query":"query visionProfile($userId: String) {\n  visionProfile(userId: $userId) {\n    result\n    hostName\n    userProfile {\n      ownerCount {\n        fan\n        photo\n        follow\n        photo_public\n        __typename\n      }\n      profile {\n        gender\n        user_name\n        user_id\n        headurl\n        user_text\n        user_profile_bg_url\n        __typename\n      }\n      isFollowing\n      __typename\n    }\n    __typename\n  }\n}\n",
        "variables":{
            "userId":""
        }
    }
    async def get(self, request:Request) -> HTTPResponse:
        user_id = request.args.get("user_id", None)
        cookie = request.headers.get('cookie', None)
        if cookie:
            cookie = cookie
        else:
            cookie = ks_default
        if not user_id:
            return json_fail_response(CodeDict.field_val_err)

        self.query['variables']['userId'] = user_id

        try:
            data = await ks_web_request(self.query, cookie)
        except:
            return json_fail_response(CodeDict.fail, message="网络请求失败")
        return json_success_response(data)


class AwemeCommentView(HTTPMethodView):
    """
    评论数据
    """
    query = {
        "operationName":"commentListQuery",
        "query":"query commentListQuery($photoId: String, $pcursor: String) {\n  visionCommentList(photoId: $photoId, pcursor: $pcursor) {\n    commentCount\n    pcursor\n    rootComments {\n      commentId\n      authorId\n      authorName\n      content\n      headurl\n      timestamp\n      likedCount\n      realLikedCount\n      liked\n      status\n      authorLiked\n      subCommentCount\n      subCommentsPcursor\n      subComments {\n        commentId\n        authorId\n        authorName\n        content\n        headurl\n        timestamp\n        likedCount\n        realLikedCount\n        liked\n        status\n        authorLiked\n        replyToUserName\n        replyTo\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
        "variables":{
            "photoId":"",
            "pcursor":""
        }
    }
    async def get(self, request:Request) -> HTTPResponse:
        photoId = request.args.get("video_id", None)
        pcursor = request.args.get("pcursor", None)
        cookie = request.headers.get('cookie', None)
        if cookie:
            cookie = cookie
        else:
            cookie = ks_default
        if not photoId:
            return json_fail_response(CodeDict.field_val_err)

        self.query['variables']['photoId'] = photoId
        self.query['variables']['pcursor'] = pcursor

        try:
            data = await ks_web_request(self.query, cookie)
        except:
            return json_fail_response(CodeDict.fail, message="网络请求失败")
        return json_success_response(data)


class AwemeSubCommentView(HTTPMethodView):
    """
    子评论数据
    """
    query = {
        "operationName":"visionSubCommentList",
        "query":"mutation visionSubCommentList($photoId: String, $rootCommentId: String, $pcursor: String) {\n  visionSubCommentList(photoId: $photoId, rootCommentId: $rootCommentId, pcursor: $pcursor) {\n    pcursor\n    subComments {\n      commentId\n      authorId\n      authorName\n      content\n      headurl\n      timestamp\n      likedCount\n      realLikedCount\n      liked\n      status\n      authorLiked\n      replyToUserName\n      replyTo\n      __typename\n    }\n    __typename\n  }\n}\n",
        "variables":{
            "photoId":"",
            "pcursor":"",
            "rootCommentId":""
        }
    }
    async def get(self, request:Request) -> HTTPResponse:
        photoId = request.args.get("video_id", None)
        root_id = request.args.get("root_id", None)
        pcursor = request.args.get("pcursor", '')
        cookie = request.headers.get('cookie', None)
        if cookie:
            cookie = cookie
        else:
            cookie = ks_default
        if not photoId:
            return json_fail_response(CodeDict.field_val_err)
        if not root_id:
            return json_fail_response(CodeDict.field_val_err)

        self.query['variables']['photoId'] = photoId
        self.query['variables']['pcursor'] = pcursor
        self.query['variables']['rootCommentId'] = root_id

        try:
            data = await ks_web_request(self.query, cookie)
        except:
            return json_fail_response(CodeDict.fail, message="网络请求失败")
        return json_success_response(data)


class SearchDataView(HTTPMethodView):
    """
    搜索数据
    """
    data_query = {
        "operationName":"visionSearchPhoto",
        "query":"fragment photoContent on PhotoEntity {\n  __typename\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  commentCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n}\n\nfragment recoPhotoFragment on recoPhotoEntity {\n  __typename\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  commentCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n}\n\nfragment feedContent on Feed {\n  type\n  author {\n    id\n    name\n    headerUrl\n    following\n    headerUrls {\n      url\n      __typename\n    }\n    __typename\n  }\n  photo {\n    ...photoContent\n    ...recoPhotoFragment\n    __typename\n  }\n  canAddComment\n  llsid\n  status\n  currentPcursor\n  tags {\n    type\n    name\n    __typename\n  }\n  __typename\n}\n\nquery visionSearchPhoto($keyword: String, $pcursor: String, $searchSessionId: String, $page: String, $webPageArea: String) {\n  visionSearchPhoto(keyword: $keyword, pcursor: $pcursor, searchSessionId: $searchSessionId, page: $page, webPageArea: $webPageArea) {\n    result\n    llsid\n    webPageArea\n    feeds {\n      ...feedContent\n      __typename\n    }\n    searchSessionId\n    pcursor\n    aladdinBanner {\n      imgUrl\n      link\n      __typename\n    }\n    __typename\n  }\n}\n",
        "variables":{
            "keyword":"",
            "page":"search",
            "pcursor":""
        }
    }
    user_query = {
        "operationName": "graphqlSearchUser",
        "query": "query graphqlSearchUser($keyword: String, $pcursor: String, $searchSessionId: String) {\n  visionSearchUser(keyword: $keyword, pcursor: $pcursor, searchSessionId: $searchSessionId) {\n    result\n    users {\n      fansCount\n      photoCount\n      isFollowing\n      user_id\n      headurl\n      user_text\n      user_name\n      verified\n      verifiedDetail {\n        description\n        iconType\n        newVerified\n        musicCompany\n        type\n        __typename\n      }\n      __typename\n    }\n    searchSessionId\n    pcursor\n    __typename\n  }\n}\n",
        "variables": {
            "keyword": "",
            "pcursor": ""
        }
    }
    async def get(self, request:Request) -> HTTPResponse:
        keyword = request.args.get("keyword", None)
        type = request.args.get("type", 'video')
        pcursor = request.args.get("pcursor", '1')
        cookie = request.headers.get('cookie', None)
        if cookie:
            cookie = cookie
        else:
            cookie = ks_default
        if not keyword:
            return json_fail_response(CodeDict.field_val_err)

        if type == 'user':
            self.user_query['variables']['keyword'] = keyword
            self.user_query['variables']['pcursor'] = pcursor
            try:
                data = await ks_web_request(self.user_query, cookie)
            except:
                return json_fail_response(CodeDict.fail, message="网络请求失败")
        else:
            self.data_query['variables']['keyword'] = keyword
            self.data_query['variables']['pcursor'] = pcursor
            try:
                data = await ks_web_request(self.data_query, cookie)
            except:
                return json_fail_response(CodeDict.fail, message="网络请求失败")
        return json_success_response(data)