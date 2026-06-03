import re
import unicodedata

from rapidfuzz import fuzz

from classes import BookCandidate, Library, SearchIndexEntry

# filtre tout ce qui n'est ni un caractère de mot, ni un espace
PUNCTUATION_RE = re.compile(r"[^\w\s]", flags=re.UNICODE)
# filtre les espaces, y compris longs
WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    text = text.lower()
    # décomposition canonique
    text = unicodedata.normalize("NFD", text)
    # ne garde pas les diacritiques
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    # remplace les ponctuations par des espaces
    text = PUNCTUATION_RE.sub(" ", text)
    # écrase les longs espaces
    text = WHITESPACE_RE.sub(" ", text)
    # strip enlève les espaces au début et à la fin
    return text.strip()


def build_search_index(library: Library) -> list[SearchIndexEntry]:
    index = []

    for book in library.books:
        texts = [
            book.title,
            *book.aliases,
        ]

        if book.series:
            texts.append(book.series)
            texts.append(f"{book.series} {book.title}")

        seen = set()

        for text in texts:
            normalized = normalize_text(text)

            if not normalized or normalized in seen:
                continue

            seen.add(normalized)

            index.append(
                SearchIndexEntry(
                    text=text,
                    normalized_text=normalized,
                    book_id=book.id,
                    source="library",
                    weight=1.0,
                )
            )

    return index


def search_books(
    query: str,
    library: Library,
    limit: int = 5,
    min_score: float = 55.0,
) -> list[BookCandidate]:
    normalized_query = normalize_text(query)

    if not normalized_query:
        return []

    index = build_search_index(library)
    books_by_id = {book.id: book for book in library.books}

    best_by_book = {}

    for entry in index:
        score = fuzz.WRatio(normalized_query, entry.normalized_text)

        if score < min_score:
            continue

        previous = best_by_book.get(entry.book_id)

        if previous is None or score > previous[0]:
            best_by_book[entry.book_id] = (score, entry)

    ranked = sorted(
        best_by_book.items(),
        key=lambda item: item[1][0],
        reverse=True,
    )

    candidates = []

    for book_id, (score, entry) in ranked[:limit]:
        book = books_by_id[book_id]

        candidates.append(
            BookCandidate(
                book_id=book.id,
                title=book.title,
                series=book.series,
                volume=book.volume,
                score=round(score, 2),
                matched_text=entry.text,
            )
        )

    return candidates
