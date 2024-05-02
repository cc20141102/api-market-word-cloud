from sanic import Blueprint

from applications.apps.videos.views import VideoView

router: Blueprint = Blueprint('video', url_prefix='video')


router.add_route(VideoView.as_view(), "/", name="video_parse")