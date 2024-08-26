from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Botni ishga tushurish"),
            # types.BotCommand("login", "Loginni o'zgartirish"),
            # types.BotCommand("premium", "Premium hizmat"),
#            types.BotCommand("coder", "Dasturchi"),
        ]
    )
