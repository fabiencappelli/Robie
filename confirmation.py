from classes import Intent, Library, StartMode


def find_book(library: Library, book_id: str):
    for book in library.books:
        if book.id == book_id:
            return book

    raise ValueError(f"Livre introuvable: {book_id}")


def build_confirmation_question(intent: Intent, library: Library) -> str:
    book = find_book(library, intent.book_id)

    if book.series and book.volume:
        book_label = f"{book.series}, tome {book.volume}, {book.title}"
    elif book.series:
        book_label = f"{book.series}, {book.title}"
    else:
        book_label = book.title

    if intent.start_mode == StartMode.BEGINNING:
        start_label = "depuis le début"
    elif intent.start_mode == StartMode.LAST_POSITION:
        start_label = "là où tu t'étais arrêté"
    else:
        start_label = "depuis le début"

    return f"Tu veux écouter {book_label}, {start_label} ?"
