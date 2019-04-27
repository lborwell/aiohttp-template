import datetime

from app.handlers.rest.base_handler import json_endpoint
from app.services.books_controller import BookService


@json_endpoint
async def index(request):
    author_query = request.query.get('author')
    if author_query:
        books = await BookService.list_by_author_name(author_query)
    else:
        books = await BookService.list()
    return {'books': {k: v for k, v in map(lambda x: (x['id'], _present(x)), books)}}


@json_endpoint
async def show(request):
    book_id = request.match_info['book_id']
    book = await BookService.lookup(book_id)
    if book:
        return _present(book)
    raise FileNotFoundError


@json_endpoint
async def create(request):
    body = await request.json()
    book_id = await BookService.create(payload=body)
    return _present(await BookService.lookup(book_id))


def _present(book):
    if book:
        return {
            'id': book['id'],
            'created_at': datetime.datetime.strftime(book['created_at'], '%H:%M:%S %a %d %b %y'),
            'updated_at': datetime.datetime.strftime(book['updated_at'], '%H:%M:%S %a %d %b %y'),
            **book['payload']
        }
    return {}
