# coding: utf-8
from datetime import datetime

from tortoise import fields

from passlib.context import CryptContext

from utils.models import BaseModel
from utils.string_utils import generate_random_string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    """用户表"""

    class Meta:
        table = "t_user"
        table_description = "用户表"

    mobile = fields.CharField(max_length=11, unique=True, description="用户名")
    password = fields.CharField(max_length=256, description="密码")
    status = fields.BooleanField(default=False, description="用户状态")
    is_active = fields.BooleanField(default=False, description="是否激活")
    requests_remain = fields.IntField(default=0, description="剩余请求次数")
    authorization_token = fields.CharField(max_length=64, unique=True, description="用户唯一凭证")
    is_vip = fields.BooleanField(default=False, description="是否VIP")
    vip_exp = fields.IntField(default=0, description="VIP过期时间")

    @classmethod
    async def create_user(cls, mobile: str, password: str):
        """
        创建新用户
        :param mobile:
        :param password:
        :return:
        """
        hashed_password = pwd_context.hash(password)
        user = await cls.create(mobile=mobile, password=hashed_password,
                                authorization_token=generate_random_string(64))
        return user

    async def verify_password(self, plain_password: str) -> bool:
        """
        验证用户密码
        :param plain_password: 输入的密码
        :return:
        """
        return pwd_context.verify(plain_password, self.password)

    # async def update_last_login(self):
    #     """
    #     更新上次登录时间
    #     :return:
    #     """
    #     self.last_login = datetime.now()
    #     await self.save()

    async def update_user_info(self, new_mobile: str = None, new_password: str = None, new_status: bool = None,
                               new_active: bool = None):
        """
        更新用户
        :param new_mobile: 新手机号
        :param new_password: 新密码
        :param new_status:  状态
        :return:
        """
        if new_mobile:
            self.mobile = new_mobile
        if new_password:
            self.password = pwd_context.hash(new_password)
        if new_status:
            self.status = new_status
        if new_active:
            self.is_active = new_active
        self.update_datetime = datetime.now()  # 更新日期
        await self.save()


class RequestCard(BaseModel):
    """
    解析卡
    """

    class Meta:
        table = "t_request_card"
        table_description = "解析卡表"

    card_num = fields.CharField(max_length=32, description="卡号", unique=True)
    status = fields.BooleanField(default=True, description='状态')
    user = fields.IntField(description="关联用户", null=True)
    card_type = fields.IntField(default=0, description="卡片类型")



class VIPCard(BaseModel):
    """
    VIP卡
    """

    class Meta:
        table = "t_vip_card"
        table_description = "VIP卡"

    card_num = fields.CharField(max_length=48, description="卡号", unique=True)
    status = fields.BooleanField(default=True, description='状态')
    user = fields.IntField(description="关联用户", null=True)
    card_type = fields.IntField(default=0, description="卡片类型")