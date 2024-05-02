# coding: utf-8

"""用户蓝图"""

from sanic import Blueprint

from .views import UserRegisterView, UserLoginView, UserActiveView, DailyCheckIn, ForgetPassword, \
    ResetAuthorizationView, ActiveRemainView, ActiveVIPView

router: Blueprint = Blueprint('user', url_prefix='auth')


router.add_route(UserRegisterView.as_view(), "/register", name="user_register")  # 用户列表
router.add_route(UserLoginView.as_view(), "/login", name="user_login")
router.add_route(UserActiveView.as_view(), "/active", name="user_active")
router.add_route(DailyCheckIn.as_view(), "/daily_check_in", name="user_daily_check_in")
router.add_route(ForgetPassword.as_view(), "/reset_password", name="user_reset_password")
router.add_route(ResetAuthorizationView.as_view(), "/reset_token", name="user_reset_token")
router.add_route(ActiveRemainView.as_view(), "/active_remain", name="user_active_remain")
router.add_route(ActiveVIPView.as_view(), "/active_vip", name="user_active_vip")
