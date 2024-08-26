from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
import math
from handlers.admin.adminpanel import adminkeyboard
from loader import dp, bot,Database
from data.config import ADMINS, channel_id
from aiogram.dispatcher.filters.state import State, StatesGroup
import json

class AddMovieState(StatesGroup):
    name = State()
    quality = State()
    movie = State()



from filters.admins import IsSuperAdmin
@dp.message_handler(IsSuperAdmin(), commands=['del'])
async def addkinoname(message: types.Message, state: FSMContext):
    if message.get_args():
        sql = """DELETE FROM `movies` WHERE `id`=%s"""
        await Database.apply(sql, message.get_args())
        await message.answer("Kino ochirildi!")
    else:
        pass


@dp.callback_query_handler(text='add_kino')
async def addkino(call: types.CallbackQuery):
    await call.message.edit_text("Kino nomini kiriting:", reply_markup=adminkeyboard.back())
    await AddMovieState.name.set()

@dp.message_handler(state=AddMovieState.name)
async def addkinoname(message: types.Message, state: FSMContext):
    await state.update_data({'name': message.text.lower()})
    keyboad = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboad.add(types.KeyboardButton(text="2160p"), types.KeyboardButton(text="1140p"))
    keyboad.add(types.KeyboardButton(text="1080p"), types.KeyboardButton(text="720p"))
    keyboad.add(types.KeyboardButton(text="480p"), types.KeyboardButton(text="360p"))
    keyboad.add(types.KeyboardButton(text="240p"), types.KeyboardButton(text="144p"))
    keyboad.add(types.KeyboardButton(text="Bekor qilish"))
    await message.answer("Kino formatini kirting!",reply_markup=keyboad)
    await AddMovieState.quality.set()

@dp.message_handler(state=AddMovieState.quality)
async def addkinoquality(message: types.Message, state: FSMContext):
    if message.text == "Bekor qilish":
        await state.finish()
        await message.answer("Kino qo'shish bekor qilindi!", reply_markup=types.ReplyKeyboardRemove())
    else:
        await state.update_data({'quality': message.text})
        await message.answer("Kinoni yuboring!", reply_markup=types.ReplyKeyboardRemove())
        await AddMovieState.movie.set()


@dp.message_handler(state=AddMovieState.movie, content_types=['video', 'document'])
async def addkinomovie(message: types.Message, state: FSMContext):
    info = await state.get_data()
    bot_ = await bot.get_me()
    name = info['name']
    quality = info['quality']
    if message.content_type == 'video':
        file_size = message.video.file_size // 1048576
        msg = (await bot.send_video(chat_id=channel_id, video=message.video.file_id)).message_id
        sql = "INSERT INTO `movies`(`name`,`quality`,`file_id`, `file_size`, `views`) VALUES (%s, %s, %s, %s, %s)"
        await Database.apply(sql, (name, quality, msg, f"{math.floor(file_size)} MB", 0))
        sql = "SELECT * FROM `movies` WHERE `file_id` = %s"

        res = await Database.get(sql, msg)
        text = f"""<b>✅ Botga yangi film yuklandi:

🎞 {name.capitalize()}</b>

🖥 <a href='https://t.me/{bot_.username}?start={res["id"]}'>{quality}</a>"""
        await message.answer(text)
        await state.finish()
    elif message.content_type == 'document':
        file_size = message.document.file_size // 1048576
        msg = (await bot.send_video(chat_id=channel_id, video=message.document.file_id)).message_id
        sql = "INSERT INTO `movies`(`name`,`quality`,`file_id`, `file_size`, `views`) VALUES (%s, %s, %s, %s, %s)"
        await Database.apply(sql, (name, quality, msg, f"{math.floor(file_size)} MB", 0))
        sql = "SELECT * FROM `movies` WHERE `file_id` = %s"
        res = await Database.get(sql, msg)
        text = f"""<b>✅ Botga yangi film yuklandi:

🎞 {name.capitalize()}</b>

🖥 <a href='https://t.me/{bot_.username}?start={res["id"]}'>{quality}</a>"""
        await message.answer(text)
        await state.finish()
    else:pass
