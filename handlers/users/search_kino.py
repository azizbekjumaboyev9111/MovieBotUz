from aiogram import types
from loader import dp, Database, bot
import uuid

@dp.inline_handler()
async def inline_search(query: types.InlineQuery):
    bot_ = await bot.get_me()
    user = bot_.username
    language_code = query.from_user.language_code
    user_id = query.from_user.id
    q = query.query
    n = 0
    results = []
    try:
        if not q:
            res = await Database.get_random_movies()
            for x in res:
                sss = uuid.uuid4().hex[:11]
                results.append(
                    types.InlineQueryResultArticle(
                        id=sss,
                        title=f"{x['quality']}, {x['name'].capitalize()}",
                        description=f"📀 Hajmi: {x['file_size']}\n👁: {x['views']}",
                        input_message_content=types.InputTextMessageContent(f"cinema_id:{x['id']}", disable_web_page_preview=True),
                        thumb_url="https://img1.teletype.in/files/45/df/45df13dc-2b53-4d42-b22c-30f5187e4e55.jpeg",
                                                 )
                )
            await query.answer(results, cache_time=5, switch_pm_parameter='start', switch_pm_text="Botdan foydanalish!...")
        elif q == 'saved':
            sql = "SELECT * FROM `saved` WHERE user_id = %s"
            saved_res = await Database.get(sql, (user_id), fetch_all=True)
            for x in saved_res:
                res = await Database.get_movies2(x['kino_id'])
                for x in res:
                    sss = uuid.uuid4().hex[:11]
                    results.append(
                        types.InlineQueryResultArticle(
                            id=sss,
                            title=f"{x['quality']}, {x['name'].capitalize()}",
                            description=f"📀 Hajmi: {x['file_size']}\n👁: {x['views']}",
                            input_message_content=types.InputTextMessageContent(f"cinema_id:{x['id']}",
                                                                                disable_web_page_preview=True),
                            thumb_url="https://img1.teletype.in/files/45/df/45df13dc-2b53-4d42-b22c-30f5187e4e55.jpeg",
                        )
                    )
            await query.answer(results, cache_time=5, switch_pm_parameter='start',
                                   switch_pm_text="Botdan foydanalish!...")

        else:
            sql = "SELECT * FROM movies WHERE name LIKE %s"
            dbsearch = await Database.get(sql, (f'%{q.lower()}%',), fetch_all=True)
            for x in dbsearch:
                sss = uuid.uuid4().hex[:11]
                results.append(
                    types.InlineQueryResultArticle(
                        id=sss,
                        title=f"{x['quality']}, {x['name'].capitalize()}",
                        description=f"📀 Hajmi: {x['file_size']}\n👁: {x['views']}",
                        input_message_content=types.InputTextMessageContent(f"cinema_id:{x['id']}",
                                                                            disable_web_page_preview=True),
                        thumb_url="https://img1.teletype.in/files/45/df/45df13dc-2b53-4d42-b22c-30f5187e4e55.jpeg",
                    )
                )
            await query.answer(results, cache_time=5, switch_pm_parameter='start',
                               switch_pm_text="Botdan foydanalish!...")

    except Exception as e:
        print(f'Error: {e}')
        await query.answer([], cache_time=5, switch_pm_parameter='start', switch_pm_text='Botdan foydanalish!...')
