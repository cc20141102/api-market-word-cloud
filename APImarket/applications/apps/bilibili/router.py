from sanic import Blueprint

from applications.apps.bilibili.views import AwemeDetailView, AwemeDownloadView, UserALLPostView, SearchView, \
    CommentsDataView

router: Blueprint = Blueprint('bilibili', url_prefix='bilibili')


router.add_route(AwemeDetailView.as_view(), "/video_data", name="bilibili_aweme_detail")
router.add_route(AwemeDownloadView.as_view(), "/video_download", name="bilibili_aweme_download")
router.add_route(UserALLPostView.as_view(), "/user_post", name="bilibili_user_post")
router.add_route(SearchView.as_view(), "/search", name="bilibili_search")
router.add_route(CommentsDataView.as_view(), "/comments", name="bilibili_comments")