from sanic import Blueprint

from applications.apps.xhs.views import NoteDetailView, UserDetailView, UserNotesView, NoteCommentView, \
    UserNotesSubCommentView, SearchNotesView

router: Blueprint = Blueprint('xhs', url_prefix='xhs')


router.add_route(NoteDetailView.as_view(), "/get_note_by_id", name="xhs_note_detail")
router.add_route(UserDetailView.as_view(), "/get_user_info", name="xhs_user_detail")
router.add_route(UserNotesView.as_view(), "/get_user_notes", name="xhs_user_notes")
router.add_route(NoteCommentView.as_view(), "/get_note_comments", name="xhs_note_comments")
router.add_route(UserNotesSubCommentView.as_view(), "/get_note_sub_comments", name="xhs_note_sub_comments")
router.add_route(SearchNotesView.as_view(), "/search_note_by_keyword", name="xhs_search_note_by_keyword")