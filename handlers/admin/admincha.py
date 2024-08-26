from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from filters.admins import IsAdmin
from loader import dp, bot,Database
from data.config import ADMINS
from aiogram.dispatcher.filters.state import State, StatesGroup
import json

class AdminKeyboard:
    def admin_panel(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='📊 Statistika', callback_data='stat'),types.InlineKeyboardButton(text='📢 Kanallar', callback_data='channels'))
        keyboard.add(types.InlineKeyboardButton(text='📝 Xabar yuborish', callback_data='location_all'),types.InlineKeyboardButton(text='📝 Guruhlarga Xabar yuborish', callback_data='mail_group'))
        keyboard.add(types.InlineKeyboardButton(text='🎞 Kino qo\'shish', callback_data='add_kino'))
        keyboard.add(types.InlineKeyboardButton(text='➕ Reklama qo\'shish', callback_data='ads_add'),types.InlineKeyboardButton(text='➖ Reklama o\'chirish', callback_data='ads_remove'))
#        keyboard.add(types.InlineKeyboardButton(text='➕ Admin qo\'shish', callback_data='admin_add'),types.InlineKeyboardButton(text='➖ Admin o\'chirish', callback_data='admin_remove'))
        keyboard.add(types.InlineKeyboardButton(text='🔼', callback_data='close'))

        return keyboard
    def back(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='⬅️ Ortga', callback_data='panel'))
        return keyboard

    def mail_sending(self,status=None):
        keyboard = types.InlineKeyboardMarkup()
        if status=='True':
            pause_or_resume = "To'xtatish ⏸"
        else:
            pause_or_resume = 'Davom etish ▶️'
        if status != None:
            keyboard.add(types.InlineKeyboardButton(text=pause_or_resume, callback_data='pause_or_resume'))
        keyboard.add(types.InlineKeyboardButton(text="🔄 Yangilash", callback_data='update_mail'))
        keyboard.add(types.InlineKeyboardButton(text="🗑 O'chirish", callback_data='delete_mail'))
        keyboard.add(types.InlineKeyboardButton(text='⬅️ Ortga', callback_data='panel'))
        return keyboard


    async def channels_keyboard(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='📢 Kanallar', callback_data='channels_list'))
        keyboard.add(types.InlineKeyboardButton(text='➕ Kanal qo\'shish', callback_data='add_channel'),
                     types.InlineKeyboardButton(text='➖ Kanal o\'chirish', callback_data='delete_channel'))
        check = await Database.get_settings('channels')
        name, value = check['name'], check['value']
        if value == 'True':
            text = '✅ Majburiy a\'zolik | Yoqilgan'
        else:
            text = '❌ Majburiy a\'zolik | O\'chirilgan'
        keyboard.add(types.InlineKeyboardButton(text=text, callback_data='channels_on_off'))
        keyboard.add(types.InlineKeyboardButton(text='🔙 Orqaga', callback_data='panel'))
        return keyboard

    async def channels_list(self):
        keyboard = types.InlineKeyboardMarkup()
        channels = await Database.get_all_channels()
        if len(channels) > 0:
            for channel in channels:
                try:
                    channel = await bot.get_chat(channel['channel_id'])
                    count = (await bot.get_chat_member_count(channel.id))
                    if count > 1000:
                        count = f'{round(count / 1000, 1)}K'
                except:
                    continue
                keyboard.add(
                    types.InlineKeyboardButton(text=f'{channel.title} [{count}]', callback_data=f'channel_{channel.id}'))
            keyboard.add(types.InlineKeyboardButton(text='🔙 Orqaga', callback_data='channels'))
            return keyboard
        else:
            return False

    async def delete_channel(self):
        keyboard = types.InlineKeyboardMarkup()
        channels = await Database.get_all_channels()
        for channel in channels:
            try:
                channel = await bot.get_chat(channel['channel_id'])
                count = (await bot.get_chat_member_count(channel.id))
                if count > 1000:
                    count = f'{round(count / 1000, 1)}K'

            except:
                continue
            keyboard.add(types.InlineKeyboardButton(text=f'{channel.title} [{count}]',
                                                    callback_data=f'delete_channel_{channel.id}'))
        keyboard.add(types.InlineKeyboardButton(text='🔙 Orqaga', callback_data='channels'))
        return keyboard

    def back_to(self, step):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='🔙 Orqaga', callback_data=f'back_to_{step}'))
        return keyboard

class AdminForm(StatesGroup):
    mail_type = State()
    mail = State()
    mail_location = State()
    mailling = State()
    gr_mailling = State()
    add_music = State()


adminkeyboard = AdminKeyboard()

@dp.message_handler(IsAdmin(), commands=['admin'], state='*')
async def admin_panel(message: types.Message,state: FSMContext):
    await state.finish()
    await message.delete()
    await message.answer('Admin panel', reply_markup=adminkeyboard.admin_panel())

@dp.callback_query_handler(IsAdmin(), text='close', state='*')
async def close_(call: types.CallbackQuery,state: FSMContext):
    await state.finish()
    await call.message.delete()



@dp.callback_query_handler(IsAdmin(), text='pause_or_resume', state='*')
async def pause_or_resume(callback_query: types.CallbackQuery,state: FSMContext):
    res = await Database.get("SELECT `send`,`not_send`,`status`,`type`,`location` FROM `mailing`")
    if res:
        await callback_query.answer()
        send,not_send,status,type,location = res['send'],res['not_send'],res['status'],res['type'],res['location']
        all_user = (await Database.all_user_count())['all']
        no_send = (send + not_send)
        if status =='True':
            status = 'False'
            status_ = 'To\'xtatilgan'
        else:
            status = 'True'
            status_ = 'Davom etmoqda'


        text = f"📨 Xabar yuborish\n\nYuborilmoqda: Userlarga\n✅ Yuborilgan: {send}\n❌ Yuborilmagan: {not_send}\n👥 Umumiy:{no_send}/{all_user} \n\n📊 Status: {status_}"
        await Database.apply("UPDATE `mailing` SET `status` = %s",(status,))
        if send >= all_user:
            text+=f"\n\n<b>📧 Xabar yuborish tugadi</b>"
            status = None
        try:
            await callback_query.message.edit_text(text=text,reply_markup=adminkeyboard.mail_sending(status))
        except:
            pass
        return
    await callback_query.answer('Xabar yuborish boshlanmagan')

@dp.callback_query_handler(IsAdmin(), text='delete_mail', state='*')
async def delete_mail(callback_query: types.CallbackQuery,state: FSMContext):
    res = await Database.get("SELECT `send`,`not_send`,`status` FROM `mailing`")
    if res:
        await callback_query.answer("Xabar o'chirildi 🗑")
        await Database.apply("DELETE FROM `mailing`")
        await callback_query.message.edit_text(text='Xabar yuborish o\'chirildi',reply_markup=adminkeyboard.admin_panel())
        return
    await callback_query.answer('Xabar yuborish boshlanmagan')

@dp.callback_query_handler(IsAdmin(), lambda callback_query: callback_query.data.startswith('update_mail'), state='*')
async def mail_location_(callback_query: types.CallbackQuery,state: FSMContext):
    res = await Database.get("SELECT `send`,`not_send`,`status`,`type`,`location` FROM `mailing`")
    if res:
        send, not_send, status, type, location = res['send'], res['not_send'], res['status'], res['type'], res[
            'location']
        if type == 'mail_user':
            type = '👤 Userlarga'
            all_user = (await Database.all_user_count())['all']
        if type == 'mail_group':
            type = '👤 Guruhlarga'
            all_user = (await Database.all_group_count())['all']
        no_send = (send + not_send)
        if status == 'True':
            status = 'Davom etmoqda'
        if status == 'False':
            status = 'To\'xtatilgan'
        text = f"📨 Xabar yuborish\n\n Yuborilmoqda: {type}\n✅ Yuborilgan: {send}\n❌ Yuborilmagan: {not_send}\n👥 Umumiy: {no_send}/{all_user} \n\n📊 Status: {status}"
        if no_send == all_user:
            text += f"\n\n<b>📧 Xabar yuborish tugadi</b>"
            status = None
        try:
            await callback_query.message.edit_text(text=text, reply_markup=AdminKeyboard().mail_sending(status))
        except:
            await callback_query.answer()
        return
    else:
        pass


@dp.callback_query_handler(IsAdmin(), lambda callback_query: callback_query.data.startswith('location_'), state='*')
async def mail_location_(callback_query: types.CallbackQuery,state: FSMContext):
    res = await Database.get("SELECT `send`,`not_send`,`status`,`type`,`location` FROM `mailing`")
    if res:
        send, not_send, status, type, location = res['send'], res['not_send'], res['status'], res['type'], res[
            'location']
        if type == 'mail_user':
            type = '👤 Userlarga'
            all_user = (await Database.all_user_count())['all']
        if type == 'mail_group':
            type = '👤 Guruhlarga'
            all_user = (await Database.all_group_count())['all']
        no_send = (send + not_send)
        if status == 'True':
            status = 'Davom etmoqda'
        if status == 'False':
            status = 'To\'xtatilgan'
        text = f"📨 Xabar yuborish\n\n Yuborilmoqda: {type}\n✅ Yuborilgan: {send}\n❌ Yuborilmagan: {not_send}\n👥 Umumiy: {no_send}/{all_user} \n\n📊 Status: {status}"
        if no_send == all_user:
            text += f"\n\n<b>📧 Xabar yuborish tugadi</b>"
            status = None
        await callback_query.message.edit_text(text=text, reply_markup=AdminKeyboard().mail_sending(status))
        return
    await state.finish()
    location = callback_query.data.split('_')[1]
    await state.update_data(mail_location=location)
    text = '<b>Xabar yuborish uchun xabarni yuboring</b>'
    await callback_query.message.edit_text(text=text, reply_markup=adminkeyboard.back())
    await AdminForm.mailling.set()

@dp.callback_query_handler(IsAdmin(), text=['mail_group'])
async def mail_type(callback_query: types.CallbackQuery,state: FSMContext):
    res = await Database.get("SELECT `send`,`not_send`,`status`,`type`,`location` FROM `mailing`")
    if res:
        send, not_send, status, type, location = res['send'], res['not_send'], res['status'], res['type'], res[
            'location']
        if type == 'mail_user':
            type = '👤 Userlarga'
            all_user = (await Database.all_user_count())['all']
        if type == 'mail_group':
            type = '👤 Guruhlarga'
            all_user = (await Database.all_group_count())['all']
        no_send = (send + not_send)
        if status == 'True':
            status = 'Davom etmoqda'
        if status == 'False':
            status = 'To\'xtatilgan'
        text = f"📨 Xabar yuborish\n\n Yuborilmoqda: {type}\n✅ Yuborilgan: {send}\n❌ Yuborilmagan: {not_send}\n👥 Umumiy: {no_send}/{all_user} \n\n📊 Status: {status}"
        if no_send == all_user:
            text += f"\n\n<b>📧 Xabar yuborish tugadi</b>"
            status = None
        await callback_query.message.edit_text(text=text, reply_markup=AdminKeyboard().mail_sending(status))
        return
    if callback_query.data == 'mail_group':
        await state.update_data(mail_location='group')
        text = '<b>Xabar yuborish uchun xabarni yuboring</b>'
        await callback_query.message.edit_text(text=text, reply_markup=adminkeyboard.back())
        await AdminForm.gr_mailling.set()

@dp.message_handler(IsAdmin(), state=AdminForm.gr_mailling, content_types=types.ContentTypes.ANY)
async def mailling(message: types.Message,state: FSMContext):
    message_id = message.message_id
    chat_id = message.chat.id
    reply_markup = ''
    if message.reply_markup:
        reply_markup = json.dumps(message.reply_markup.as_json(), ensure_ascii=False)
    data = await state.get_data()
    # mail_type, mail,location = data['mail_type'], data['mail'],data['mail_location']
    sql = "INSERT INTO `mailing`(`status`, `chat_id`, `message_id`, `reply_markup`, `mail_type`, `offset`, `send`, `not_send`,`type`,`location`) VALUES ('True',%s,%s,%s,%s,0,0,0,%s,%s)"
    res = await Database.apply(sql,(chat_id,message_id,reply_markup, 'Oddiy', 'mail_group', 'all'))
    if res:
        await message.answer('Xabar yuborish boshlandi',reply_markup=adminkeyboard.admin_panel())
        await state.finish()
    else:
        await message.answer('Xatolik yuz berdi',reply_markup=adminkeyboard.admin_panel())
        await state.finish()



@dp.message_handler(IsAdmin(), state=AdminForm.mailling, content_types=types.ContentTypes.ANY)
async def mailling(message: types.Message,state: FSMContext):
    message_id = message.message_id
    chat_id = message.chat.id
    reply_markup = ''
    if message.reply_markup:
        reply_markup = json.dumps(message.reply_markup.as_json(), ensure_ascii=False)
    data = await state.get_data()
    # mail_type, mail,location = data['mail_type'], data['mail'],data['mail_location']
    sql = "INSERT INTO `mailing`(`status`, `chat_id`, `message_id`, `reply_markup`, `mail_type`, `offset`, `send`, `not_send`,`type`,`location`) VALUES ('True',%s,%s,%s,%s,0,0,0,%s,%s)"
    res = await Database.apply(sql,(chat_id,message_id,reply_markup, 'Oddiy', 'mail_user', 'all'))
    if res:
        await message.answer('Xabar yuborish boshlandi',reply_markup=adminkeyboard.admin_panel())
        await state.finish()
    else:
        await message.answer('Xatolik yuz berdi',reply_markup=adminkeyboard.admin_panel())
        await state.finish()

@dp.callback_query_handler(IsAdmin(), text='stat',state='*')
async def stat_(call: types.CallbackQuery,state: FSMContext):
    stat = await Database.all_user_count()
    stat_2 = await Database.all_group_count()
    stat_kino = await Database.all_kino_count()
    stat_views = await Database.all_views_count()
    print(stat_views)
    all,active,passive = stat['all'],stat['active'],stat['passive']
    all_group, active_group, passive_group = stat_2['all'], stat_2['active'], stat_2['passive']
    date_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    text = f'📊 Statistika\n\n👥 Umumiy foydalanuvchilar soni: <b>{all}</b>\n👤 Aktiv foydalanuvchilar soni: <b>{active}</b>\n👤 Aktiv guruhlar soni: <b>{active_group}</b>\n🎞 Barcha kinolar: <b>{stat_kino["COUNT(`id`)"]}</b>\n📥 Jami yuklab olingan kinolar: <b>{sum([int(x["views"]) for x in stat_views])}</b>\n\n'
    text+=f'\n📅 {date_time}'
    await call.answer()
    await call.message.edit_text(text, reply_markup=adminkeyboard.back())

@dp.callback_query_handler(IsAdmin(), text='panel', state='*')
async def panel_(call: types.CallbackQuery,state: FSMContext):
    await state.finish()
    await call.answer()
    await call.message.edit_text('Admin panel', reply_markup=adminkeyboard.admin_panel())


@dp.callback_query_handler(IsAdmin(), text='channels_on_off',  state='*')
async def channels_on_off(call: types.CallbackQuery, state: FSMContext):
    check = await Database.get_settings('channels')
    name, value = check['name'], check['value']
    if value == 'True':
        await Database.update_settings('channels', 'False')
        text = '❌ Majburiy a\'zolik o\'chirildi'
    else:
        await Database.update_settings('channels', 'True')
        text = '✅ Majburiy a\'zolik yoqildi'
    await call.message.edit_reply_markup(reply_markup=await adminkeyboard.channels_keyboard())
    await call.answer(text=text, )


@dp.callback_query_handler(IsAdmin(), lambda c: c.data == 'channels' or c.data == 'back_to_channels',  state='*')
async def channels(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.answer()
    text = 'Kanallar'
    keyboard = await adminkeyboard.channels_keyboard()
    try:
        await callback_query.message.edit_text(text=text, reply_markup=keyboard)
    except:
        await callback_query.message.delete()
        await callback_query.message.answer(text=text, reply_markup=keyboard)


@dp.callback_query_handler(IsAdmin(),lambda c: c.data.startswith('channel_'),  state='*')
async def channel_(callback_query: types.CallbackQuery):
    await callback_query.answer()
    channel_id = callback_query.data.split('_')[1]
    try:
        channel = await bot.get_chat(channel_id)
        count = await bot.get_chat_member_count(channel_id)
        if count > 1000:
            count = f'{round(count / 1000, 1)}K'
    except:
        await callback_query.message.edit_text('Kanal topilmadi', reply_markup=adminkeyboard.back_to('channels'))
        return
    text = '<b>'
    text += f'Kanal: {channel.title}\n'
    text += f'Kanal ID: {channel.id}\n'
    text += f'Kanal linki: {channel.invite_link}\n'
    text += f'Kanalga a\'zo: {count}\n'
    text += '</b>'

    await callback_query.message.edit_text(text=text, reply_markup=adminkeyboard.back_to('channels'),disable_web_page_preview=True)



class FormChannel(StatesGroup):
    channel_id = State()


@dp.callback_query_handler(IsAdmin(),lambda c: c.data == 'add_channel', )
async def add_channel(callback_query: types.CallbackQuery):
    await callback_query.answer()
    text = 'Kanal ID ni yoki username ni kiriting'
    await callback_query.message.delete()
    await callback_query.message.answer(text=text, reply_markup=adminkeyboard.back_to('channels'))
    await FormChannel.channel_id.set()


@dp.message_handler(IsAdmin(),state=FormChannel.channel_id, )
async def add_channel_id(message: types.Message, state: FSMContext):
    channel_id = message.text
    if channel_id.startswith('@'):
        channel_id = channel_id.replace('@', '')
    if channel_id.isdigit():
        if not channel_id.startswith('-100'):
            channel_id = f'-100{channel_id}'
    try:
        channel = await bot.get_chat(channel_id)
        channel_id = channel.id
    except:
        await message.answer('Kanal topilmadi', reply_markup=adminkeyboard.back_to('channels'))
        return

    if channel.type != 'channel':
        await message.answer('Bu kanal emas', reply_markup=adminkeyboard.back_to('channels'))
        return
    await Database.add_channel(channel_id)
    await message.answer('Kanal qo\'shildi: <a href="{}">{}</a>'.format(channel.invite_link, channel.title),
                         parse_mode='html', reply_markup=await adminkeyboard.channels_keyboard())
    await state.finish()


@dp.callback_query_handler(IsAdmin(),lambda c: c.data == 'delete_channel', )
async def delete_channel(callback_query: types.CallbackQuery):
    text = 'O\'chirish uchun kanalni tanlang'
    keyboard = await adminkeyboard.delete_channel()
    if not keyboard:
        await callback_query.answer('Kanal mavjud emas')
        return
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer(text=text, reply_markup=keyboard)


@dp.callback_query_handler(IsAdmin(),lambda c: c.data.startswith('delete_channel_'), )
async def delete_channel_id(callback_query: types.CallbackQuery):
    channel_id = callback_query.data.replace('delete_channel_', '')
    await Database.delete_channel(channel_id)
    await callback_query.answer('Kanal o\'chirildi', show_alert=True)
    keyboard = await adminkeyboard.delete_channel()
    if not keyboard:
        await callback_query.message.edit_text('Kanal mavjud emas', reply_markup=adminkeyboard.back_to('channels'))
    else:
        await callback_query.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query_handler(IsAdmin(),lambda c: c.data == 'channels_list', )
async def channels_list(callback_query: types.CallbackQuery):
    text = 'Kanallar'
    keyboard = await adminkeyboard.channels_list()
    if keyboard:
        await callback_query.answer()
        await callback_query.message.delete()
        await callback_query.message.answer(text=text, reply_markup=keyboard)
        return
    else:
        return await callback_query.answer("Kanallar mavjud emas", show_alert=True)



class FormAds(StatesGroup):
    txt = State()
    link = State()


@dp.callback_query_handler(IsAdmin(),lambda c: c.data == 'ads_add', )
async def add_channel(callback_query: types.CallbackQuery):
    res = await Database.get_all_ads()
    if len(res) >= 10:
        await callback_query.answer("Iltmos reklama tugmalarini kamayting eng ko'pi 10tagacha reklama tugmalarini qoshishiz mumkin!", show_alert=True)
        return

    await callback_query.answer()
    text = 'Text kirting!'
    await callback_query.message.delete()
    await callback_query.message.answer(text=text, reply_markup=adminkeyboard.back())
    await FormAds.txt.set()

@dp.message_handler(IsAdmin(),state=FormAds.txt)
async def adshandl(message: types.message, state: FSMContext):
    await state.update_data({'txt': message.text})
    await message.answer(text="Url kiriting", reply_markup=adminkeyboard.back())
    await FormAds.link.set()

@dp.message_handler(IsAdmin(),state=FormAds.link)
async def adshandl(message: types.message, state: FSMContext):
    info = await state.get_data()
    txt = info['txt']
    await Database.new_ads(text=txt, url=message.text)
    await message.answer("Yangi button qo'shildi", reply_markup=adminkeyboard.admin_panel())
    await state.finish()

@dp.callback_query_handler(IsAdmin(),lambda c: c.data == 'ads_remove', )
async def add_channel(callback_query: types.CallbackQuery):
    res = await Database.get_all_ads()
    keyboard = types.InlineKeyboardMarkup()
    r = []
    if res:
        for x in res:
            r.append(types.InlineKeyboardButton(text=x['text'], callback_data=f"rmv_ads:{x['id']}")
                 )
        keyboard.add(*r)
    keyboard.add(types.InlineKeyboardButton(text='➕ Reklama qo\'shish', callback_data='ads_add'))
    keyboard.add(types.InlineKeyboardButton(text='⬅️ Ortga', callback_data='panel'))
    await callback_query.message.edit_text("O'chirmoqchi bo'lgan tugamngiz ustig bir marta bosangiz ochadi", reply_markup=keyboard)


@dp.callback_query_handler(IsAdmin(),lambda c: c.data.startswith('rmv_ads:'), )
async def delete_channel_id(callback_query: types.CallbackQuery):
    url_id = callback_query.data.split(':')[1]
    await Database.delete_ads(url_id)
    res = await Database.get_all_ads()
    keyboard = types.InlineKeyboardMarkup()
    r = []
    if res:
        for x in res:
            r.append(types.InlineKeyboardButton(text=x['text'], callback_data=f"rmv_ads:{x['id']}")
                     )
        keyboard.add(*r)
    keyboard.add(types.InlineKeyboardButton(text='➕ Reklama qo\'shish', callback_data='ads_add'))
    keyboard.add(types.InlineKeyboardButton(text='⬅️ Ortga', callback_data='panel'))
    await callback_query.message.edit_text("O'chirildi yana ochirmoqchi bosangiz kerakli tugma ustiga bosing",
                                           reply_markup=keyboard)

