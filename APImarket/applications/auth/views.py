# coding: utf-8

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, time

from redis.asyncio import Redis
from sanic import Request, HTTPResponse
from sanic.views import HTTPMethodView

from applications.models import User, RequestCard, VIPCard
from core.message import CodeDict
from core.response import json_success_response, json_fail_response

from libs.logger import LoggerProxy
from utils.ali_sms import send_sms
from utils.string_utils import is_valid_mobile, generate_code, generate_random_string

logger: LoggerProxy = LoggerProxy(__name__)


class UserRegisterView(HTTPMethodView):
    """
    注册视图
    """

    @staticmethod
    async def post(request: Request) -> HTTPResponse:
        mobile = request.json.get("mobile", None)
        password = request.json.get("password", None)
        password2 = request.json.get("password2", None)
        # 数据校验
        if not mobile:
            return json_fail_response(CodeDict.no_field, message="缺少mobile参数")
        if not password:
            return json_fail_response(CodeDict.no_field, message="缺少password参数")
        if not password == password2:
            return json_fail_response(CodeDict.field_val_err, message="密码校验错误")
        if not is_valid_mobile(mobile):
            return json_fail_response(CodeDict.field_val_err, message="手机号不合法")
        # 校验是否已注册
        user_exists = await User.filter(mobile=mobile)
        if user_exists:
            user = await User.get(mobile=mobile)
            if user.is_active:
                return json_fail_response(CodeDict.data_repeat, message='已注册')
            user = await user.update_user_info(new_password=password)
        else:
            user = await User.create_user(mobile=mobile, password=password)
        # 发送验证码
        redis_client: Redis = request.ctx.redis_client
        is_send_sms = await redis_client.get(f"flag_{mobile}")
        if is_send_sms:
            return json_fail_response(CodeDict.data_repeat, message="请不要频繁发送")
        code = await generate_code()
        sms_status = await send_sms(phone_numbers=mobile, template_param={"code": f'{code}'})
        sms_status_str = sms_status.decode()
        sms_status_json = json.loads(sms_status)
        if 'Code' in sms_status_str:  # 判断返回内容是否存在code的key，错误时不返回code
            if sms_status_json["Code"] == 'OK':
                # 存储短信验证码到redis
                # 存储一个标记，表示此手机号已发送过短信，标记有效期为60s
                await redis_client.set(f"flag_{mobile}", 1, 60)
                await redis_client.set(f"{mobile}_code", str(code), 300)
                return json_success_response('注册成功，请先激活账号！验证码已发送至该手机号！')
            else:
                return json_fail_response(CodeDict.fail, "验证码发送失败")
        return json_fail_response(CodeDict.fail, '验证码发送失败')


class UserLoginView(HTTPMethodView):
    """
    用户登录
    """

    @staticmethod
    async def post(request: Request) -> HTTPResponse:
        mobile = request.json.get('mobile', None)
        password = request.json.get('password', None)
        if not mobile or not password:
            return json_fail_response(CodeDict.field_val_err)
        user = await User.filter(mobile=mobile)
        if not user:
            return json_fail_response(CodeDict.fail, message="账号或密码错误")
        user = user[0]
        p_verify = await user.verify_password(password)
        if not p_verify:
            return json_fail_response(CodeDict.fail, message="账号或密码错误")
        if not user.is_active:
            return json_fail_response(CodeDict.fail, message="未激活")
        if not user.status:
            return json_fail_response(CodeDict.fail, message="已封禁")
        data = {
            "mobile": user.mobile,
            "status": user.status,
            "is_active": user.is_active,
            "requests_remain": user.requests_remain,
            "is_vip": user.is_vip,
            "vip_exp": user.vip_exp,
            # "create_datetime": user.create_datetime,
            "authorization_token": {
                "token": user.authorization_token
            }
        }
        return json_success_response(data)


class UserActiveView(HTTPMethodView):
    """
    账号激活
    """

    @staticmethod
    async def get(request: Request) -> HTTPResponse:
        mobile = request.args.get('mobile', None)
        code = request.args.get('code', None)
        if not mobile or not code:
            return json_fail_response(CodeDict.no_field)
        redis_client: Redis = request.ctx.redis_client
        redis_code = await redis_client.get(f"{mobile}_code")

        if not redis_code:
            return json_fail_response(CodeDict.fail, message='验证码错误')
        if redis_code and not code == redis_code.decode():
            return json_fail_response(CodeDict.fail, message="验证码错误")
        user = await User.get(mobile=mobile)
        # 判断是激活还是重置密码
        if user.requests_remain > 0 and not user.is_active:
            user.is_active = True
            await user.save()
        else:
            if user.is_active:
                return json_fail_response(message="该用户已激活，无需重复操作")
            user.is_active = True
            user.status = True
            # 赠送50请求次数
            user.requests_remain = 50
            await user.save()
        data = {
            "mobile": user.mobile,
            "status": user.status,
            "is_active": user.is_active,
            "is_vip": user.is_vip,
            "requests_remain": user.requests_remain,
            "vip_exp": user.vip_exp,
            # "create_datetime": user.create_datetime,
            "authorization_token": {
                "token": user.authorization_token
            }
        }
        return json_success_response(data)


class DailyCheckIn(HTTPMethodView):
    """
    签到
    """

    @staticmethod
    async def get(request: Request) -> HTTPResponse:
        authorization_token = request.headers.get("authorization")
        if not authorization_token:
            return json_fail_response(CodeDict.fail, message="不支持未登录的请求")
        authorization_token = authorization_token.replace("Bearer ", "")
        user = await User.filter(authorization_token=authorization_token)
        if not user:
            return json_fail_response(message="token错误")
        user = user[0]
        if not user.status:
            return json_fail_response(message="已封禁")
        redis_client: Redis = request.ctx.redis_client
        cache_verify_code = await redis_client.get('daily_check_in_%s' % user.id)
        if cache_verify_code:
            return json_fail_response(message="今日已签到")
        # 获取当前时间
        now = datetime.now()
        # 获取第二天的午夜时间（即第三天的 00:00:00）
        next_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        # 计算当前时间到第二天 0:00:00 的时间差
        time_remaining = next_midnight - now
        # 获取时间差的总秒数
        seconds_remaining = int(time_remaining.total_seconds())
        # 用户签到，存储到redis中，第二天0点失效重置
        await redis_client.set("daily_check_in_%s" % user.id, 1, seconds_remaining)
        # 给用户随机赠送一些积分
        num = random.randint(10, 30)
        user.requests_remain += num
        await user.save()
        return json_success_response(f"签到成功,赠送{num}请求次数")


class ForgetPassword(HTTPMethodView):
    """
    忘记密码
    """

    @staticmethod
    async def post(request: Request) -> HTTPResponse:
        mobile = request.json.get("mobile", None)
        password = request.json.get("password", None)
        password2 = request.json.get("password2", None)
        # 数据校验
        if not mobile:
            return json_fail_response(CodeDict.no_field, message="缺少mobile参数")
        if not password:
            return json_fail_response(CodeDict.no_field, message="缺少password参数")
        if not password == password2:
            return json_fail_response(CodeDict.field_val_err, message="密码校验错误")
        if not is_valid_mobile(mobile):
            return json_fail_response(CodeDict.field_val_err, message="手机号不合法")

        # 校验是否注册
        user_exists = await User.filter(mobile=mobile)
        if not user_exists:
            return json_fail_response(CodeDict.no_data, message="未注册")
        user = user_exists[0]
        if not user.is_active:
            return json_fail_response(CodeDict.fail, message="未激活，请先激活或重新注册")
        if not user.status:
            return json_fail_response(CodeDict.fail, message="已封禁")

        # 发送验证码
        redis_client: Redis = request.ctx.redis_client
        is_send_sms = await redis_client.get(f"flag_{mobile}")
        if is_send_sms:
            return json_fail_response(CodeDict.data_repeat, message="请不要频繁发送")
        code = await generate_code()
        sms_status = await send_sms(phone_numbers=mobile, template_param={"code": f'{code}'})
        sms_status_str = sms_status.decode()
        sms_status_json = json.loads(sms_status)
        if 'Code' in sms_status_str:  # 判断返回内容是否存在code的key，错误时不返回code
            if sms_status_json["Code"] == 'OK':
                # 存储短信验证码到redis
                # 存储一个标记，表示此手机号已发送过短信，标记有效期为60s
                await redis_client.set(f"flag_{mobile}", 1, 60)
                await redis_client.set(f"{mobile}_code", str(code), 300)
                user.is_active = False
                await user.save()
                return json_success_response('密码已更改！请重新激活账号，验证码已发送至该手机号！')
            else:
                return json_fail_response(CodeDict.fail, "验证码发送失败")
        return json_fail_response(CodeDict.fail, '验证码发送失败')


class ResetAuthorizationView(HTTPMethodView):
    """
    重置个人token
    """

    @staticmethod
    async def post(request: Request) -> HTTPResponse:
        mobile = request.json.get("mobile", None)
        password = request.json.get("password", None)

        if not mobile:
            return json_fail_response(CodeDict.field_val_err)
        if not password:
            return json_fail_response(CodeDict.field_val_err)

        user = await User.filter(mobile=mobile)
        if not user:
            return json_fail_response(CodeDict.fail, message="账号或密码错误")
        user = user[0]
        check_password = await user.verify_password(password)
        if not check_password:
            return json_fail_response(CodeDict.fail, message="账号或密码错误")
        if not user.is_active:
            return json_fail_response(CodeDict.fail, message="账号未激活")
        if not user.status:
            return json_fail_response(CodeDict.fail, message="已封禁")
        user.authorization_token = generate_random_string(64)
        await user.save()
        return json_success_response("token重置成功,请重新登陆获取")


class ActiveRemainView(HTTPMethodView):
    """
    激活请求卡
    """

    @staticmethod
    async def post(request: Request) -> HTTPResponse:
        card_num = request.json.get("card_num", None)
        # for i in range(50):
        #     num = generate_random_string(32)
        #     print(num)
        #     add_card = await RequestCard.create(card_num=num, card_type=3)

        if not card_num:
            return json_fail_response(CodeDict.field_val_err)
        card_exists = await RequestCard.filter(card_num=card_num)
        if not card_exists:
            return json_fail_response(CodeDict.fail, message="激活失败!卡号错误或已失效!")
        card = card_exists[0]
        if not card.status:
            return json_fail_response(CodeDict.fail, message="激活失败!卡号错误或已失效!")
        user = await User.get(authorization_token=request.token)
        if not user.is_active or not user.status:
            return json_fail_response(CodeDict.authorization_fail, message="激活失败!账号未激活或已封禁！")
        if card.card_type == 0:
            card.status = False
            card.update_datetime = datetime.now()
            card.user = user.id
            await card.save()
            user.requests_remain += 500
            await user.save()
        elif card.card_type == 1:
            card.status = False
            card.update_datetime = datetime.now()
            card.user = user.id
            await card.save()
            user.requests_remain += 2000
            await user.save()
        elif card.card_type == 2:
            card.status = False
            card.update_datetime = datetime.now()
            card.user = user.id
            await card.save()
            user.requests_remain += 15000
            await user.save()
        elif card.card_type == 3:
            card.status = False
            card.update_datetime = datetime.now()
            card.user = user.id
            await card.save()
            user.requests_remain += 150000
            await user.save()
        else:
            return json_fail_response(CodeDict.fail, message="系统错误")

        return json_success_response(f"激活码使用成功！当前请求次数剩余{user.requests_remain}次！")


class ActiveVIPView(HTTPMethodView):
    """
    激活VIP
    """

    @staticmethod
    async def post(request: Request) -> HTTPResponse:
        card_num = request.json.get("card_num", None)
        if not card_num:
            return json_fail_response(CodeDict.field_val_err)
        # for i in range(1):
        #     num = generate_random_string(48)
        #     print(num)
        #     add_card = await VIPCard.create(card_num=num, card_type=99)
        card_exists = await VIPCard.filter(card_num=card_num)
        if not card_exists:
            return json_fail_response(CodeDict.fail, message="激活失败!卡号错误或已失效!")
        card = card_exists[0]
        if not card.status:
            return json_fail_response(CodeDict.fail, message="激活失败!卡号错误或已失效!")
        user = await User.get(authorization_token=request.token)
        if not user.is_active or not user.status:
            return json_fail_response(CodeDict.authorization_fail, message="激活失败!账号未激活或已封禁！")
        if card.card_type == 0:
            # 30天
            card.status = False
            card.update_datetime = datetime.now()
            card.user = user.id
            await card.save()
            user.is_vip = True
            if user.vip_exp == 0:
                # 如果原始日期为空，则使用今天的日期作为基准
                current_date = datetime.now()
                new_date = current_date + timedelta(days=30)
            else:
                # 如果时间戳不为0，将指定日期增加30天
                date_from_timestamp = datetime.fromtimestamp(user.vip_exp)
                new_date = date_from_timestamp + timedelta(days=30)
            # 将时间调整为23:59:59
            new_date = new_date.replace(hour=23, minute=59, second=59)
            user.vip_exp = int(new_date.timestamp())
            await user.save()
        elif card.card_type == 1:
            # 90天
            card.status = False
            card.update_datetime = datetime.now()
            card.user = user.id
            await card.save()
            user.is_vip = True

            if user.vip_exp == 0:
                # 如果原始日期为空，则使用今天的日期作为基准
                current_date = datetime.now()
                new_date = current_date + timedelta(days=30)
            else:
                # 如果时间戳不为0，将指定日期增加30天
                date_from_timestamp = datetime.fromtimestamp(user.vip_exp)
                new_date = date_from_timestamp + timedelta(days=30)
            # 将时间调整为23:59:59
            new_date = new_date.replace(hour=23, minute=59, second=59)
            user.vip_exp = int(new_date.timestamp())
            await user.save()
        elif card.card_type == 2:
            # 180天
            card.status = False
            card.update_datetime = datetime.now()
            card.user = user.id
            await card.save()
            user.is_vip = True
            if user.vip_exp == 0:
                # 如果原始日期为空，则使用今天的日期作为基准
                current_date = datetime.now()
                new_date = current_date + timedelta(days=30)
            else:
                # 如果时间戳不为0，将指定日期增加30天
                date_from_timestamp = datetime.fromtimestamp(user.vip_exp)
                new_date = date_from_timestamp + timedelta(days=30)
            # 将时间调整为23:59:59
            new_date = new_date.replace(hour=23, minute=59, second=59)
            user.vip_exp = int(new_date.timestamp())
            await user.save()
        elif card.card_type == 3:
            # 365天
            card.status = False
            card.update_datetime = datetime.now()
            card.user = user.id
            await card.save()
            user.is_vip = True
            if user.vip_exp == 0:
                # 如果原始日期为空，则使用今天的日期作为基准
                current_date = datetime.now()
                new_date = current_date + timedelta(days=30)
            else:
                # 如果时间戳不为0，将指定日期增加30天
                date_from_timestamp = datetime.fromtimestamp(user.vip_exp)
                new_date = date_from_timestamp + timedelta(days=30)
            # 将时间调整为23:59:59
            new_date = new_date.replace(hour=23, minute=59, second=59)
            user.vip_exp = int(new_date.timestamp())
            await user.save()
        else:
            # 永久
            return json_fail_response(CodeDict.fail, message="系统错误")

        return json_success_response("恭喜激活成功！可重新登陆账号查看个人信息!")
