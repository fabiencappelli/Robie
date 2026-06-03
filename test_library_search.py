import json
from pathlib import Path

from classes import Library
from library_search import search_books


def load_library(path: str = "library.json") -> Library:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return Library.model_validate(data)


if __name__ == "__main__":
    library = load_library()

    queries = [
        "lis les royaumes de feu tome quatre",
        "lis royaume de feu tome cat",
        "lis l ile au secret",
        "reprends le tome quatre des royaumes de feu",
        "mets la guerre des clans tome deux",
        "lis ewilan tome un",
        "mets eragon deux",
    ]

    for query in queries:
        print("\nQUERY:", query)

        candidates = search_books(query, library)

        for candidate in candidates:
            print(
                candidate.book_id,
                candidate.score,
                "=>",
                candidate.series,
                candidate.volume,
                "-",
                candidate.title,
                "| matched:",
                candidate.matched_text,
            )
