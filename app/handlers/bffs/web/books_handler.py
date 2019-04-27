import datetime
import json

from aiohttp_jinja2 import template

from app.domain.models.book import Book
from app.services.books_controller import BookService


@template('books/index.html.jinja2')
async def index(request):
    books = await BookService.list()
    return {'books': [_present(b) for b in books]}


@template('books/show.html.jinja2')
async def show(request):
    book_id = request.match_info['book_id']
    book = await BookService.lookup(book_id)
    return {'book': _present(book)}


def _present(book):
    if book:
        return {
            'id': book['id'],
            'created_at': datetime.datetime.strftime(book['created_at'], '%H:%M:%S %a %d %b %y'),
            'updated_at': datetime.datetime.strftime(book['updated_at'], '%H:%M:%S %a %d %b %y'),
            'name': Book.name(book),
            'author': Book.author(book),
            'isbn': Book.isbn(book),
            'payload': book['payload'],
            'pretty_payload': json.dumps(book['payload'], indent=2),
        }
    return {}
