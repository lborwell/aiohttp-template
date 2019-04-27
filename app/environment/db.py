import logging
import uuid

import aiopg


class DBFacade:

    BOOK_KEYS = ['id', 'payload', 'created_at', 'updated_at']
    BOOK_TABLE = 'books'

    def __init__(self, proxy):
        self.__proxy = proxy

    async def create_book(self, id, payload, timestamp):
        keys = ['id', 'payload', 'created_at', 'updated_at']
        values = (id, payload, timestamp, timestamp)
        sql = 'INSERT INTO {} ({}) VALUES ({});'.format(
            self.BOOK_TABLE,
            ','.join(keys),
            ','.join(['%s'] * len(keys)))
        await self.__proxy.insert(sql, values)
        return id

    async def lookup_book(self, id):
        sql = 'SELECT {} FROM {} WHERE id = %s;'.format(','.join(self.BOOK_KEYS), self.BOOK_TABLE)
        books = await self.__proxy.query(sql, (id,))
        if books:
            return self._deserialize(self.BOOK_KEYS, books[0])
        return None

    async def list_books(self):
        sql = 'SELECT {} FROM {}'.format(','.join(self.BOOK_KEYS), self.BOOK_TABLE)
        books = await self.__proxy.query(sql, ())
        return [self._deserialize(self.BOOK_KEYS, b) for b in books]

    async def list_books_by_author(self, author):
        sql = 'SELECT {} FROM {} WHERE payload->>\'author\' = %s;'.format(','.join(self.BOOK_KEYS), self.BOOK_TABLE)
        books = await self.__proxy.query(sql, (author,))
        return [self._deserialize(self.BOOK_KEYS, b) for b in books]

    async def migrate(self, migration):
        await self.__proxy.insert(migration, ())

    @classmethod
    def _deserialize(cls, keys, account):
        def coerce_uuids(item):
            if isinstance(item, uuid.UUID):
                return str(item)
            return item
        return dict(zip(keys, map(coerce_uuids, account)))


class PostgresProxy:

    _connection_pool = None

    def __init__(self, database, user, password, host, sslmode):
        self._dsn = 'dbname=%s user=%s password=%s host=%s sslmode=%s' % (database, user, password, host, sslmode)
        self._connection_pool = None

    async def query(self, query, args):
        await self.init()
        with await self._connection_pool.cursor() as cursor:
            await cursor.execute(query, args)
            return await cursor.fetchall()

    async def insert(self, query, args):
        await self.init()
        with await self._connection_pool.cursor() as cursor:
            return await cursor.execute(query, args)

    async def update(self, query, args):
        await self.init()
        with await self._connection_pool.cursor() as cursor:
            return await cursor.execute(query, args)

    async def delete(self, query, args):
        await self.init()
        with await self._connection_pool.cursor() as cursor:
            return await cursor.execute(query, args)

    async def init(self):
        if not self._connection_pool:
            self._connection_pool = await aiopg.create_pool(self._dsn)


class Cursor:

    def __init__(self, connection):
        self._connection = connection

    def __enter__(self):
        return self._connection.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if all((exc_type, exc_val, exc_tb)):
            self._connection.rollback()
            logging.exception('Failed to perform query {}\n\nTraceback:\n{}'.format(exc_val, exc_tb))
        else:
            self._connection.commit()


class Connection:

    def __init__(self, pool):
        self._pool = pool
        self._pool_connection = pool.getconn()

    def __enter__(self):
        return self._pool_connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._pool.putconn(self._pool_connection)
