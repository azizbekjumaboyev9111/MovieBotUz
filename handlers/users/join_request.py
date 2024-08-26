from aiogram.types import ChatJoinRequest
from loader import Database, bot, dp

@dp.chat_join_request_handler()
async def Tasdiqlash (message: ChatJoinRequest):
    chat = message.chat
    user = message.from_user
    try:
        await bot.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        await bot.send_message(chat_id=user.id, text="Tasdiqlash so'rovingiz qabul qilinish uchun botga /start bosing!\n\n/start /start /start")
        check_user = await Database.check_user_exists(message.from_user.id)
        if not check_user:
            await Database.new_user(message.from_user.id)
    except:
        pass