from sanic import Blueprint

from applications.apps.ks.views import AwemeDetailView, UserPostDataView, UserDataView, AwemeCommentView, \
    AwemeSubCommentView, SearchDataView

router: Blueprint = Blueprint('kuaishou', url_prefix='ks')


router.add_route(AwemeDetailView.as_view(), "/video_data", name="ks_aweme_detail")
router.add_route(UserPostDataView.as_view(), "/user_video_data", name="ks_user_video_data")
router.add_route(UserDataView.as_view(), "/user_data", name="ks_user_data")
router.add_route(AwemeCommentView.as_view(), "/comments_list", name="ks_comments_list")
router.add_route(AwemeSubCommentView.as_view(), "/sub_comments_list", name="ks_sub_comments_list")
router.add_route(SearchDataView.as_view(), "/search", name="ks_search")