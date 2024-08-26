from aiogram import types
from loader import Database, bot
from random import choice, choices


class UserKeyboard:
    async def signals(self):
        bot_ = await bot.get_me()
        BOT_USERNAME = bot_.username
        keyboard = types.InlineKeyboardMarkup()
        res = await Database.get_all_ads()
        keyboard.add(types.InlineKeyboardButton(text="🔍 Barcha kinolar", switch_inline_query_current_chat=''),types.InlineKeyboardButton(text="💾 Saqlangan kinolar", switch_inline_query_current_chat='saved'))
        keyboard.add(types.InlineKeyboardButton(text="Guruhga qo'shish ⤴️", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"))
        if res:
            signals = choice(res)
            keyboard.add(types.InlineKeyboardButton(text=signals['text'], url=signals['url']))
            return keyboard

        else:
            return keyboard

    async def signals_res(self, user_id, code):
        bot_ = await bot.get_me()
        BOT_USERNAME = bot_.username
        keyboard = types.InlineKeyboardMarkup()
        signals1 = await Database.get_all_ads()

        keyboard.add(types.InlineKeyboardButton(text="🔍 Barcha kinolar", switch_inline_query_current_chat=''),types.InlineKeyboardButton(text="💾 Saqlangan kinolar", switch_inline_query_current_chat='saved'))
        sql = "SELECT id FROM `saved` WHERE user_id = %s AND kino_id = %s"
        res = await Database.get(sql, (user_id, code))
        if res:
            keyboard.add(types.InlineKeyboardButton(text="✅ Saqlangan", callback_data=f"deletesa:{code}"))
        else:
            keyboard.add(types.InlineKeyboardButton(text="✔️ Saqlash", callback_data=f"save:{code}"))
        keyboard.add(types.InlineKeyboardButton(text="Guruhga qo'shish ⤴️", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"))
        if signals1:
            signals = choice(signals1)
            keyboard.add(types.InlineKeyboardButton(text=signals['text'], url=signals['url']))
            return keyboard

        else:
            return keyboard



userkeyboard = UserKeyboard()