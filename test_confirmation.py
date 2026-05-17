import json
from pathlib import Path

from classes import Library, Intent, StartMode


def load_library(path: str = "library.json") -> Library:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return Library.model_validate(data)


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
        start_label = "maintenant"

    return f"Tu veux écouter {book_label}, {start_label} ?"


if __name__ == "__main__":
    library = load_library()

    intent = Intent(
        intent="play_audiobook",
        book_id="lrdf_04",
        start_mode=StartMode.BEGINNING,
        confidence=0.92,
        raw_text="lis les royaumes de feu tome 4 depuis le début",
    )

    question = build_confirmation_question(intent, library)
    print(question)
