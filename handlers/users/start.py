import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from data.config import channel_id
from keyboards.inline.key import userkeyboard
from loader import dp, Database, bot
from aiogram.dispatcher.filters import BoundFilter

class Shaxsiy(BoundFilter):
    async def check(self, message: types.Message):
        return message.chat.type == types.ChatType.PRIVATE

@dp.callback_query_handler(text='check_channel')
async def bot_start(message: types.CallbackQuery, state: FSMContext):
    await message.message.edit_text("<b>Tanlang:</b>", reply_markup=await userkeyboard.signals())

@dp.message_handler(Shaxsiy(),CommandStart(), state='*')
async def bot_start(message: types.Message, state: FSMContext):
    bt_use = await bot.get_me()
    if message.get_args():
        try:
            res = await Database.get_movies(code=message.get_args())
            print(res)
            views = int(res['views']) + 1
            await bot.copy_message(chat_id=message.from_user.id, from_chat_id=channel_id, message_id=res['file_id'], caption=f"""{res['name'].capitalize()} | {res['quality']}
📀 Hajmi: {res['file_size']}
👁: {views}
🔡 Kino kodi: {res['id']}
👉 @{bt_use.username}""", reply_markup=await userkeyboard.signals_res(message.from_user.id, res['id']))
            sql = "UPDATE movies SET `views` = {} WHERE id =%s".format(str(views))
            await Database.apply(sql, (res['id']))
        except Exception as e:
            print(e)
            return await message.answer("<b>Error movie code!</b>")
    else:
        await message.answer("<b>Tanlang:</b>", reply_markup=await userkeyboard.signals())

@dp.message_handler(Shaxsiy(), text_contains='cinema_id:')
async def bot_start(message: types.Message, state: FSMContext):
    data = message.text.split(':')[1]
    await message.delete()
    bt_use = await bot.get_me()
    try:
        res = await Database.get_movies(code=data)
        views = int(res['views']) + 1
        await bot.copy_message(chat_id=message.from_user.id, from_chat_id=channel_id, message_id=res['file_id'],
                               caption=f"""{res['name'].capitalize()} | {res['quality']}
📀 Hajmi: {res['file_size']}
👁: {views}
🔡 Kino kodi: {res['id']}
👉 @{bt_use.username}""", reply_markup=await userkeyboard.signals_res(message.from_user.id, res['id']))
        sql = "UPDATE movies SET `views` = {} WHERE id =%s".format(str(views))
        await Database.apply(sql, (res['id']))
    except Exception as e:
        pass

@dp.callback_query_handler( text_contains='save:')
async def bot_start(message: types.CallbackQuery, state: FSMContext):
    data = message.data.split(':')[1]
    await Database.new_saved_user(user_id=message.from_user.id, kino_id=data)
    await message.answer("✅ Muvaffaqiyatli saqlandi")
    await message.message.edit_reply_markup(await userkeyboard.signals_res(message.from_user.id, data))

@dp.callback_query_handler( text_contains='deletesa:')
async def bot_start(message: types.CallbackQuery, state: FSMContext):
    data = message.data.split(':')[1]
    await Database.delete_saved(message.from_user.id, data)
    await message.answer("✅ Muvaffaqiyatli o'chirildi")
    await message.message.edit_reply_markup(await userkeyboard.signals_res(message.from_user.id, data))


@dp.message_handler()
async def bot_start(message: types.Message, state: FSMContext):
    data = message.text
    if data.isdigit():
        bt_use = await bot.get_me()
        try:
            res = await Database.get_movies(code=data)
            await message.delete()
            views = int(res['views']) + 1
            await bot.copy_message(chat_id=message.from_user.id, from_chat_id=channel_id, message_id=res['file_id'],
                               caption=f"""{res['name'].capitalize()} | {res['quality']}
📀 Hajmi: {res['file_size']}
👁: {views}
🔡 Kino kodi: {res['id']}
👉 @{bt_use.username}""", reply_markup=await userkeyboard.signals_res(message.from_user.id, res['id']))
            sql = "UPDATE movies SET `views` = {} WHERE id =%s".format(str(views))
            await Database.apply(sql, (res['id']))
        except Exception as e:
            pass
    else:
        pass
