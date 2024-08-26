from aiogram import Dispatcher

from loader import dp
from .users_check import User_checkMiddleware

if __name__ == "middlewares":
    dp.middleware.setup(User_checkMiddleware())