from aiogram import types

from aiogram.dispatcher.filters import BoundFilter
from data.config import ADMINS
from loader import Database



class IsSuperAdmin(BoundFilter):
    async def check(self, message: types.Message):
        user_id = message.from_user.id

        if str(user_id) in ADMINS:
            return True
        else:
            return False

class IsAdmin(BoundFilter):
    async def check(self, message: types.CallbackQuery):
        user_id = int(message.from_user.id)
        sql = "SELECT * FROM `admins` WHERE `user_id`= %s"
        admin = await Database.get(sql, user_id)
        # id = callback.data.split(':')[1].split('_')[0]
        print(admin)
        if admin:
            return True
        else:
            return False

class IsAdmin2(BoundFilter):
    async def check(self, message: types.Message):
        user_id = int(message.from_user.id)
        sql = "SELECT * FROM `admins` WHERE `user_id`= %s"
        admin = await Database.get(sql, user_id)
        # id = callback.data.split(':')[1].split('_')[0]
        print(admin)
        if admin:
            return True
        else:
            return False
