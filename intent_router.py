from robie.intents import Intent


def simple_intent(transcript: str) -> Intent | None:
    text = transcript.lower().strip()

    stop_words = ["stop", "arrête", "arrete", "tais-toi", "coupe"]
    pause_words = ["pause", "mets en pause"]
    resume_words = ["reprends", "continue", "relance"]
    louder_words = ["plus fort", "augmente le son", "monte le son"]
    quieter_words = ["moins fort", "baisse le son", "moins de son"]

    if any(w in text for w in stop_words):
        return Intent(intent="stop", confidence=0.95)

    if any(w in text for w in pause_words):
        return Intent(intent="pause", confidence=0.95)

    if any(w in text for w in resume_words):
        return Intent(intent="resume_playback", confidence=0.90)

    if any(w in text for w in louder_words):
        return Intent(intent="volume_up", confidence=0.95)

    if any(w in text for w in quieter_words):
        return Intent(intent="volume_down", confidence=0.95)

    return None
