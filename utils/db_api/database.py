import re
from typing import Optional, Union, Any, AsyncGenerator, List, Dict, Tuple
from asyncio import get_event_loop

from pymysql import err as mysql_errors
from contextlib import suppress

from aiomysql import Pool, create_pool
from aiomysql.cursors import DictCursor


class MySQLStorage:
    def __init__(self, database: str, host: str = 'localhost', port: int = 3306, user: str = 'root',
                 password: Optional[str] = None, create_pool: bool = True):
        """
        Initialize database
        :param database: Database name
        :param host: Database host
        :param port: Database port
        :param user: Database user
        :param password: Database password
        :param create_pool: Set True if you want to obtain a pool immediately
        """

        self.pool: Optional[Pool] = None
        self.host: str = host
        self.port: int = port
        self.user: str = user
        self.password: str = password
        self.database = database

        if create_pool:
            loop = get_event_loop()
            loop.run_until_complete(self.acquire_pool())
        super().__init__()

    def __del__(self):
        self.pool.close()

    async def acquire_pool(self):
        """
        Creates a new MySQL pool
        """
        if isinstance(self.pool, Pool):
            with suppress(Exception):
                self.pool.close()

        self.pool = await create_pool(host=self.host, port=self.port, user=self.user,
                                      password=self.password, db=self.database)

    @staticmethod
    def _verify_args(args: Optional[Union[Tuple[Union[Any, Dict[str, Any]], ...], Any]]):
        if args is None:
            args = tuple()
        if not isinstance(args, (tuple, dict)):
            args = (args,)
        return args

    async def apply(self, query: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any], Any]] = None) -> int:
        """
        Executes SQL query and returns the number of affected rows
        :param query: SQL query to execute
        :param args: Arguments passed to the SQL query
        :return: Number of affected rows
        """
        args = self._verify_args(args)
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cursor:
                try:
                    await cursor.execute(query, args)
                    await conn.commit()
                    return True
                except mysql_errors.Error as e:
                    await conn.rollback()
                    return False

    async def select(self, query: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any], Any]] = None) -> \
            AsyncGenerator[Dict[str, Any], None]:
        """
        Generator that yields rows
        :param query: SQL query to execute
        :param args: Arguments passed to the SQL query
        :return: Yields rows one by one
        """
        args = self._verify_args(args)
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cursor:
                try:
                    await cursor.execute(query, args)
                    await conn.commit()
                    while True:
                        item = await cursor.fetchone()
                        if item:
                            yield item
                        else:
                            break
                except mysql_errors.Error:
                    pass

    async def get(self, query: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any], Any]] = None,
                  fetch_all: bool = False) -> Union[bool, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Get a single row or a list of rows from the database
        :param query: SQL query to execute
        :param args: Arguments passed to the SQL query
        :param fetch_all: Set True if you need a list of rows instead of just a single row
        :return: A row or a list or rows
        """
        args = self._verify_args(args)
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cursor:
                try:
                    await cursor.execute(query, args)
                    await conn.commit()

                    if fetch_all:
                        return await cursor.fetchall()
                    else:
                        result = await cursor.fetchone()
                        return result if result else dict()
                except mysql_errors.Error:
                    return False

    async def check(self, query: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any], Any]] = None) -> int:
        args = self._verify_args(args)
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cursor:
                try:
                    await cursor.execute(query, args)
                    await conn.commit()

                    return cursor.rowcount
                except mysql_errors.Error:
                    return 0




    async def get_random_movies(self, count=30):
    	sql = """SELECT * FROM `movies` ORDER BY RAND() LIMIT %s"""
    	params = (count,)
    	return await self.get(sql, params, fetch_all=True)

    async def update_user(self, user_id, status='passive', table='users'):
        sql = f"""UPDATE `{table}` SET `status`=%s, WHERE `user_id`=%s"""
        return await self.apply(sql, (status, user_id))

    async def check_user_exists(self, user_id: int) -> bool:
        result = await self.get("""SELECT * FROM users WHERE user_id = %s""", user_id)
        if result:
            return result
        else:
            return False

    async def new_user(self, user_id: int):
        await self.apply("""INSERT INTO `users` (`user_id`, `status`) VALUES (%s, 'active')""", (user_id))

    async def check_group_exists(self, group_id) -> bool:
        return bool(await self.check("""SELECT `id` FROM `groups` WHERE `user_id` = %s""", group_id))

    async def new_group(self, group_id):
        await self.apply("""INSERT INTO `groups` (`user_id`,`status`) VALUES (%s,'active')""", (group_id))


    async def get_all_signals(self) -> bool:
        result = await self.get("""SELECT * FROM `ads`""")
        if result:
            return result
        else:
            return False

    async def all_user_count(self):
        all_res = await self.get("""SELECT COUNT(`id`) FROM `users`""")
        res = {}
        if all_res:
            res['all'] = all_res['COUNT(`id`)']
        active = await self.get("""SELECT COUNT(`id`) FROM `users` WHERE `status` = 'active'""")
        if active:
            res['active'] = active['COUNT(`id`)']
        passive = await self.get("""SELECT COUNT(`id`) FROM `users` WHERE `status` = 'passive'""")
        if passive:
            res['passive'] = passive['COUNT(`id`)']
        return res

    async def all_group_count(self):
        all_res = await self.get("""SELECT COUNT(`id`) FROM `groups`""")
        res = {}
        if all_res:
            res['all'] = all_res['COUNT(`id`)']
        active = await self.get("""SELECT COUNT(`id`) FROM `groups` WHERE `status` = 'active'""")
        if active:
            res['active'] = active['COUNT(`id`)']
        passive = await self.get("""SELECT COUNT(`id`) FROM `groups` WHERE `status` = 'passive'""")
        if passive:
            res['passive'] = passive['COUNT(`id`)']
        return res
    async def all_kino_count(self):
        all_res = await self.get("""SELECT COUNT(`id`) FROM `movies`""")
        return all_res

    async def all_views_count(self):
        sql = """SELECT views FROM `movies`"""
        return await self.get(sql, fetch_all=True)


    async def get_settings(self, name):
        sql = """SELECT * FROM `settings` WHERE `name`=%s"""
        return await self.get(sql, (name))


    async def update_settings(self, name, value):
        sql = """UPDATE `settings` SET `value`=%s WHERE `name`=%s"""
        return await self.apply(sql, (value, name))

    async def get_all_channels(self):
        sql = """SELECT * FROM `channels`"""
        return await self.get(sql, fetch_all=True)


    async def add_channel(self, channel_id):
        sql = """INSERT INTO `channels` (`channel_id`) VALUES (%s)"""
        return await self.apply(sql, (channel_id))

    async def delete_channel(self, channel_id):
        sql = """DELETE FROM `channels` WHERE `channel_id`=%s"""
        return await self.apply(sql, (channel_id))


    async def get_all_movies(self):
        sql = """SELECT * FROM `movies`"""
        return await self.get(sql, fetch_all=True)

    async def get_movies(self, code: int):
        return await self.get("""SELECT * FROM `movies` WHERE `id` = %s""", code)

    async def get_movies2(self, code: int):
        return await self.get("""SELECT * FROM `movies` WHERE `id` = %s""", code, fetch_all=True)

    async def new_saved_user(self, user_id: str, kino_id:str):
        await self.apply("""INSERT INTO `saved` (`user_id`, `kino_id`) VALUES (%s, %s)""", (user_id, kino_id))

    async def delete_saved(self,  user_id: str, kino_id:str):
        sql = """DELETE FROM `saved` WHERE `user_id`=%s AND `kino_id`=%s"""
        return await self.apply(sql, (user_id, kino_id))



    async def new_ads(self, text: str, url:str):
        await self.apply("""INSERT INTO `ads` (`text`, `url`) VALUES (%s, %s)""", (text, url))


    async def get_all_ads(self):
        sql = """SELECT * FROM `ads`"""
        return await self.get(sql, fetch_all=True)

    async def get_all_admins(self):
        sql = """SELECT * FROM `admins`"""
        return await self.get(sql, fetch_all=True)
    async def delete_ads(self,  url):
        sql = """DELETE FROM `ads` WHERE `id`=%s"""
        return await self.apply(sql, url)


    async def delete_admins(self,  url):
        sql = """DELETE FROM `admins` WHERE `id`=%s"""
        return await self.apply(sql, url)
