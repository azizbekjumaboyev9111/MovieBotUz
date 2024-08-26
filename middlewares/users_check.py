import asyncio
from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from loader import bot, Database
from keyboards.inline.key import userkeyboard


async def check_channel(user_id):
    check = await Database.get_settings('channels')
    name, value = check['name'], check['value']
    if value == 'True':
        keyboard = types.InlineKeyboardMarkup()
        channels = await Database.get_all_channels()
        checking = False
        for channel in channels:
            try:
                channel = await bot.get_chat(channel['channel_id'])
                _ = ['creator', 'administrator', 'member']
                status = await bot.get_chat_member(channel.id, user_id)

            except Exception as e:
                continue
            if not status.status in _:
                keyboard.add(types.InlineKeyboardButton(text=f'{channel.title}', url=f'{channel.invite_link}'))
                checking = True
        if checking:
            button = "A'zolikni tasdiqlash 🔅"
            keyboard.add(types.InlineKeyboardButton(text=button, callback_data=f'check_channel'))
            text = "<b>Assalomu alekum {fullname} ko'rsatilgan kanallarga obuna bo'lib tasdiqlash tugmasini bosing</b>"
            return text, keyboard
        else:
            return False



class User_checkMiddleware(BaseMiddleware):
    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(User_checkMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        type = message.chat.type
        if type == 'private':
            check_user = await Database.check_user_exists(message.from_user.id)
            if check_user:
                user_status = check_user['status']
                if user_status == 'passive':
                    await Database.update_user(user_id=message.from_user.id, status='active')
            if not check_user:
                # if message.get_args():
                #     id = message.get_args().replace('member_', '')
                #     sql = "SELECT * FROM `joined` WHERE `type` = %s"
                #     res = await Database.get(sql, id)
                #     if res:
                #         son = int(res['status']) + 1
                #         sql = f"UPDATE joined SET `status` = {str(son)} WHERE type =%s"
                #         await Database.apply(sql, (id))
                #     else:
                #         pass
                await Database.new_user(message.from_user.id)
                check = await Database.get_settings('channels')
                name, value = check['name'], check['value']
                if value == 'True':
                    keyboard = types.InlineKeyboardMarkup()
                    if message.chat.type == 'private':
                        check = await check_channel(message.from_user.id)
                        if check:
                            text, keyboard = check
                            await message.answer(text=text.format(fullname=message.from_user.full_name),
                                                 reply_markup=keyboard)
                            raise CancelHandler()

                text = """Tanlang:"""
                await bot.send_message(message.from_user.id, text=text,
                                       reply_markup=await userkeyboard.signals())
                raise CancelHandler()
            check = await Database.get_settings('channels')
            name, value = check['name'], check['value']
            if value == 'True':
                keyboard = types.InlineKeyboardMarkup()
                if message.chat.type == 'private':
                    check = await check_channel(message.from_user.id)
                    if check:
                        text, keyboard = check
                        await message.answer(text=text.format(fullname=message.from_user.full_name),
                                             reply_markup=keyboard)
                        raise CancelHandler()

        elif type == 'supergroup' or type == 'group':
            check_group = await Database.check_group_exists(message.chat.id)
            if not check_group:
                await Database.new_group(message.chat.id)


    async def on_process_callback_query(self, call: types.CallbackQuery, data: dict):
        type = call.message.chat.type
        if type == 'private':
            check = await Database.get_settings('channels')
            name, value = check['name'], check['value']
            if value == 'True':
                keyboard = types.InlineKeyboardMarkup()
                if call.message.chat.type == 'private':
                    check = await check_channel(call.from_user.id)
                    if check:
                        text, keyboard = check
                        await call.message.answer(text=text.format(fullname=call.from_user.full_name),
                                                  reply_markup=keyboard)
                        raise CancelHandler()