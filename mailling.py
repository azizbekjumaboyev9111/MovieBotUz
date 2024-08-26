import asyncio
from datetime import datetime
from loader import Database, bot
from data import config
from aiogram import exceptions
import json, logging


# bot = Bot(config.BOT_TOKEN)


async def send_post(chat_id, message_id, user_id, reply_markup=None, mail_type='Oddiy'):
    try:
        if mail_type == 'forward':
            await bot.forward_message(chat_id=user_id, from_chat_id=chat_id, message_id=message_id)
        elif mail_type == 'Oddiy':
            if reply_markup:
                await bot.copy_message(chat_id=user_id, from_chat_id=chat_id, message_id=message_id,
                                       reply_markup=reply_markup)
            else:
                await bot.copy_message(chat_id=user_id, from_chat_id=chat_id, message_id=message_id)

    except exceptions.BotBlocked:
        sql = "UPDATE users SET `status` = 'passive' WHERE user_id =%s"
        await Database.apply(sql, (user_id))
        logging.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        sql = "UPDATE users SET `status` = 'passive' WHERE user_id =%s"
        await Database.apply(sql, (user_id))
        logging.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        logging.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. "
            f"Sleep {e.timeout} seconds."
        )
        await asyncio.sleep(e.timeout)
        return await send_post(chat_id, message_id, user_id, reply_markup, mail_type)
    except exceptions.UserDeactivated:
        sql = "UPDATE users SET `status` = 'passive' WHERE user_id =%s"
        await Database.apply(sql, (user_id))
        logging.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        sql = "UPDATE users SET `status` = 'passive' WHERE user_id =%s"
        await Database.apply(sql, (user_id))
        logging.exception(f"Target [ID:{user_id}]: failed")
    else:
        logging.info(f"Target [ID:{user_id}]: success")
        return True
    return False


async def mailing():
    print('Mailing started ' + str(datetime.now()))
    run = True
    while run:
        sql = "SELECT `status`, `chat_id`, `message_id`, `reply_markup`, `mail_type`, `offset`, `send`, `not_send`,`type`,`location` FROM `mailing` WHERE `status` = %s"
        mailing = await Database.get(sql, 'True')

        if not mailing:
            await asyncio.sleep(2)
            continue
        # reply_markup = None
        status, chat_id, message_id, reply_markup, mail_type, offset, send, not_send, type, location = mailing.values()
        not_send, send = int(not_send), int(send)
        if reply_markup:
            reply_markup = json.loads(reply_markup)
        if type == 'mail_group':
            table = 'groups'
        if type == 'mail_user':
            table = 'users'
        if type == 'mail_group':
            sql = f"SELECT * FROM `{table}` where `id` > %s"
            users = await Database.get(sql, (offset), fetch_all=True)
        elif type == 'mail_user':
            if location == 'all':
                sql = f"SELECT * FROM `{table}` where `id` > %s and `status`='active'"
                users = await Database.get(sql, (offset), fetch_all=True)
            else:
                sql = f"SELECT * FROM `{table}` where `id` > %s and `lang` = %s and `status`='active'"
                users = await Database.get(sql, (offset, location), fetch_all=True)
        if not users:
            await Database.get("UPDATE `mailing` SET `status` = %s", 'False')
            for admin in config.ADMINS:
                try:
                    date = datetime.now().strftime("%d-%m-%Y %H:%M")

                    await bot.send_message(admin,
                                           f"Habar yuborish tugadi\n\n✅ Yuborilgan: {send}\n❌ Yuborilmagan: {not_send} \n\n📅 {date}")

                except:
                    pass
            run = False
            continue
        for user in users:
            await asyncio.sleep(0.05)
            send_post_result = await send_post(chat_id, message_id, user['user_id'], mail_type=mail_type,
                                               reply_markup=reply_markup)
            if send_post_result:
                send += 1
            else:
                not_send += 1
                await Database.update_user(user['user_id'], status='passive', table=table)

            sql = "UPDATE `mailing` SET `offset` = %s, `send` = %s, `not_send` = %s WHERE `status` = %s"
            await Database.apply(sql, (str(user['id']), str(send), str(not_send), 'True'))
            if str((send + not_send >= 1000))[:3] == str(000):
                for admin in config.ADMINS:
                    try:
                        date = datetime.now().strftime("%d-%m-%Y %H:%M")
                        await bot.send_message(admin,
                                               f"Habar yuborish bajarilmoqda\n\n✅ Yuborilgan: {send}\n❌ Yuborilmagan: {not_send} \n\n📅 {date}")
                    except:
                        pass


if __name__ == '__main__':
    print("Run")
    # asyncio.run(mailing())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(mailing())
