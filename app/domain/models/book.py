class Book(object):
    @classmethod
    def book_id(cls, book):
        return book.get('id')

    @classmethod
    def name(cls, book):
        return book.get('payload', {}).get('name')

    @classmethod
    def isbn(cls, book):
        return book.get('payload', {}).get('isbn')

    @classmethod
    def author(cls, book):
        return book.get('payload', {}).get('author')
