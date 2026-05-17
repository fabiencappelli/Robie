# robie/classes.py

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class IntentName(str, Enum):
    PLAY_AUDIOBOOK = "play_audiobook"
    RESUME_AUDIOBOOK = "resume_audiobook"
    STOP = "stop"
    PAUSE = "pause"
    RESUME_PLAYBACK = "resume_playback"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    UNKNOWN = "unknown"


class StartMode(str, Enum):
    BEGINNING = "beginning"
    LAST_POSITION = "last_position"


class ConfirmationResponseType(str, Enum):
    CONFIRM = "confirm"
    REJECT = "reject"
    CORRECT_BOOK = "correct_book"
    CORRECT_START_MODE = "correct_start_mode"
    UNCLEAR = "unclear"


class PlaybackStatus(str, Enum):
    IDLE = "idle"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class RobieMode(str, Enum):
    IDLE = "idle"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    PLAYING = "playing"
    PAUSED = "paused"
    ERROR = "error"


class Book(BaseModel):
    id: str
    title: str
    series: Optional[str] = None
    volume: Optional[int] = None
    path: Path
    aliases: list[str] = Field(default_factory=list)
    language: str = "fr"


class Library(BaseModel):
    version: int = 1
    books: list[Book]


class SearchIndexEntry(BaseModel):
    text: str
    normalized_text: str
    book_id: str
    source: str
    weight: float = 1.0


class BookCandidate(BaseModel):
    book_id: str
    title: str
    series: Optional[str] = None
    volume: Optional[int] = None
    score: float
    matched_text: str


class BookPosition(BaseModel):
    position_seconds: float = Field(default=0.0, ge=0.0)
    updated_at: Optional[datetime] = None
    completed: bool = False


class PositionsStore(BaseModel):
    version: int = 1
    positions: dict[str, BookPosition] = Field(default_factory=dict)


class Intent(BaseModel):
    intent: IntentName
    book_id: Optional[str] = None
    start_mode: Optional[StartMode] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    confirmation_question: Optional[str] = None
    raw_text: Optional[str] = None


class ConfirmationResponse(BaseModel):
    response_type: ConfirmationResponseType
    book_id: Optional[str] = None
    start_mode: Optional[StartMode] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    raw_text: Optional[str] = None


class PlayerState(BaseModel):
    status: PlaybackStatus = PlaybackStatus.IDLE
    current_book_id: Optional[str] = None
    position_seconds: float = Field(default=0.0, ge=0.0)
    volume: Optional[int] = None
    error_message: Optional[str] = None


class RobieSessionState(BaseModel):
    mode: RobieMode = RobieMode.IDLE
    pending_intent: Optional[Intent] = None
    player: PlayerState = Field(default_factory=PlayerState)
    last_transcription: Optional[str] = None
