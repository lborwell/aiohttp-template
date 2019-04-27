import json
import uuid

import datetime

from app.environment.facade import Environment


class BookService(object):
    @classmethod
    async def create(cls, payload):
        db = Environment.database()
        id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow()
        await db.create_book(id=id, payload=json.dumps(payload), timestamp=timestamp)
        return id

    @classmethod
    async def lookup(cls, id):
        db = Environment.database()
        return await db.lookup_book(id)

    @classmethod
    async def list(cls):
        db = Environment.database()
        return await db.list_books()

    @classmethod
    async def list_by_author_name(cls, author):
        db = Environment.database()
        return await db.list_books_by_author(author)
