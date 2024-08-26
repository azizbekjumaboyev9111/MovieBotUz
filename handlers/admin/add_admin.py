from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
import math
from handlers.admin.adminpanel import adminkeyboard
from loader import dp, bot,Database
from data.config import ADMINS, channel_id
from aiogram.dispatcher.filters.state import State, StatesGroup
import json

class AddAdminState(StatesGroup):
    id = State()
    name = State()


@dp.callback_query_handler(text='admin_add')
async def addkino(call: types.CallbackQuery):
    await call.message.edit_text("Admin idni kiriting:", reply_markup=adminkeyboard.back())
    await AddAdminState.id.set()

@dp.message_handler(state=AddAdminState.id)
async def addkinoname(message: types.Message, state: FSMContext):
    await state.update_data({'id': message.text})
    await message.answer("Admin ismini kirting!")
    await AddAdminState.name.set()

@dp.message_handler(state=AddAdminState.name)
async def addkinoname(message: types.Message, state: FSMContext):
    info = await state.get_data()
    id = info['id']
    sql = "INSERT INTO `admins`(`user_id`, `name`) VALUES (%s, %s)"
    await Database.apply(sql, (id, message.text))
    await message.answer("Admin qo'shildi!", reply_markup=adminkeyboard.admin_panel())
    await state.finish()



@dp.callback_query_handler(lambda c: c.data == 'admin_remove', user_id=ADMINS)
async def add_channel(callback_query: types.CallbackQuery):
    res = await Database.get_all_admins()
    keyboard = types.InlineKeyboardMarkup()
    r = []
    if res:
        for x in res:
            r.append(types.InlineKeyboardButton(text=x['user_id'], callback_data=f"rmv_admin:{x['id']}")
                 )
        keyboard.add(*r)
    keyboard.add(types.InlineKeyboardButton(text='➕ Admin qo\'shish', callback_data='admin_add'))
    keyboard.add(types.InlineKeyboardButton(text='⬅️ Ortga', callback_data='panel'))
    await callback_query.message.edit_text("O'chirmoqchi bo'lgan tugamngiz ustig bir marta bosangiz ochadi", reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data.startswith('rmv_admin:'), user_id=ADMINS)
async def delete_channel_id(callback_query: types.CallbackQuery):
    url_id = callback_query.data.split(':')[1]
    await Database.delete_admins(url_id)
    res = await Database.get_all_admins()
    keyboard = types.InlineKeyboardMarkup()
    r = []
    if res:
        for x in res:
            r.append(types.InlineKeyboardButton(text=x['user_id'], callback_data=f"rmv_admin:{x['id']}")
                     )
        keyboard.add(*r)
    keyboard.add(types.InlineKeyboardButton(text='➕ Admin qo\'shish', callback_data='admin_add'))
    keyboard.add(types.InlineKeyboardButton(text='⬅️ Ortga', callback_data='panel'))
    await callback_query.message.edit_text("O'chirildi yana ochirmoqchi bosangiz kerakli tugma ustiga bosing",
                                           reply_markup=keyboard)



