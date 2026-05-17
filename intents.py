from typing import Literal, Optional
from pydantic import BaseModel, Field


class Intent(BaseModel):
    intent: Literal[
        "play_audiobook",
        "resume_audiobook",
        "stop",
        "pause",
        "resume_playback",
        "volume_up",
        "volume_down",
        "unknown",
    ]

    title: Optional[str] = None
    start_mode: Optional[Literal["beginning", "last_position"]] = None

    confidence: float = Field(ge=0.0, le=1.0)
    confirmation_question: Optional[str] = None
