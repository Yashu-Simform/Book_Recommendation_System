class BookNotFoundError(Exception):
    """Exception raised when a book is not found."""

    def __init__(self, book_id: str):
        self.book_id = book_id
        super().__init__(f"Book with id {book_id} not found.")


class BookAlreadyExistsError(Exception):
    """Exception raised when a book already exists."""

    def __init__(self, title: str, author: str):
        super().__init__(
            f'Book with title "{title}" and author "{author}" already exists.'
        )
