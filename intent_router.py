from robie.intents import Intent


def simple_intent(transcript: str) -> Intent | None:
    text = transcript.lower().strip()

    stop_words = ["stop", "arrête", "arrete", "tais-toi", "coupe"]
    pause_words = ["pause", "mets en pause"]
    resume_words = ["reprends", "continue", "relance"]
    louder_words = ["plus fort", "augmente le son", "monte le son"]
    quieter_words = ["moins fort", "baisse le son", "moins de son"]

    if any(w in text for w in stop_words):
        return Intent(intent="stop", confidence=0.95)from robie.classes import Library, StartMode
from robie.intents import Intent
from robie.library_search import search_books


def simple_intent(transcript: str) -> Intent | None:
    text = transcript.lower().strip()
    word_count = len(text.split())

    stop_words = ["stop", "arrête", "arrete", "tais-toi", "coupe"]
    pause_words = ["pause", "mets en pause"]
    resume_words = ["reprends", "continue", "relance"]
    louder_words = ["plus fort", "augmente le son", "monte le son"]
    quieter_words = ["moins fort", "baisse le son", "moins de son"]

    if any(w in text for w in stop_words):
        return Intent(intent="stop", confidence=0.95)

    if any(w in text for w in pause_words):
        return Intent(intent="pause", confidence=0.95)

    # Important :
    # "reprends" tout seul = reprendre la lecture en cours
    # "reprends Ewilan tome deux" = demande d'audiobook avec reprise
    if any(w in text for w in resume_words) and word_count <= 3:
        return Intent(intent="resume_playback", confidence=0.90)

    if any(w in text for w in louder_words):
        return Intent(intent="volume_up", confidence=0.95)

    if any(w in text for w in quieter_words):
        return Intent(intent="volume_down", confidence=0.95)

    return None


def detect_start_mode(transcript: str) -> StartMode:
    text = transcript.lower().strip()

    resume_markers = [
        "reprends",
        "reprendre",
        "continue",
        "continuons",
        "relance",
        "où on en était",
        "ou on en etait",
        "là où on en était",
        "la ou on en etait",
        "là où on était",
        "la ou on etait",
        "dernière fois",
        "derniere fois",
    ]

    if any(marker in text for marker in resume_markers):
        return StartMode.LAST_POSITION

    return StartMode.BEGINNING


def audiobook_intent(transcript: str, library: Library) -> Intent | None:
    candidates = search_books(
        transcript,
        library,
        limit=3,
        min_score=60.0,
    )

    if not candidates:
        return None

    best = candidates[0]

    return Intent(
        intent="play_audiobook",
        book_id=best.book_id,
        start_mode=detect_start_mode(transcript),
        confidence=best.score / 100,
        raw_text=transcript,
    )


def route_intent(transcript: str, library: Library) -> Intent:
    intent = simple_intent(transcript)

    if intent is not None:
        return intent

    intent = audiobook_intent(transcript, library)

    if intent is not None:
        return intent

    return Intent(
        intent="unknown",
        confidence=0.0,
        raw_text=transcript,
    )

    if any(w in text for w in pause_words):
        return Intent(intent="pause", confidence=0.95)

    if any(w in text for w in resume_words):
        return Intent(intent="resume_playback", confidence=0.90)

    if any(w in text for w in louder_words):
        return Intent(intent="volume_up", confidence=0.95)

    if any(w in text for w in quieter_words):
        return Intent(intent="volume_down", confidence=0.95)

    return None
