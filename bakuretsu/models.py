"""Data models shared across the toolkit."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Union

from PIL import Image

RGB = tuple[int, int, int]
RGBA = tuple[int, int, int, int]

CoverSource = Union[str, Path, Image.Image]


class ContentType(Enum):
    """Type of content being reviewed."""

    GAME = "game"
    MOVIE = "movie"
    ANIME = "anime"


@dataclass
class CardStyle:
    """Visual configuration for a card.

    Font sizes given here are *base* sizes tuned for a 1200x675 card;
    renderers scale them relative to the actual card dimensions so every
    size preset (square, story, ...) keeps readable proportions.
    """

    width: int = 1200
    height: int = 675
    background_color: RGBA = (18, 18, 26, 255)
    primary_color: RGB = (255, 255, 255)
    secondary_color: RGB = (156, 163, 175)
    accent_color: RGB = (236, 72, 153)
    corner_radius: int = 20
    padding: int = 40
    theme: Optional[str] = None  # key of a decorated theme, e.g. "ramadan"

    base_title_size: int = 48
    base_score_size: int = 72
    base_review_size: int = 28
    base_platform_size: int = 20

    font_path: Optional[str] = None
    bold_font_path: Optional[str] = None

    @property
    def scale(self) -> float:
        """Scale factor relative to the 1200x675 reference card."""
        s = (self.width + self.height) / (1200 + 675)
        return max(0.6, min(2.5, s))

    @property
    def is_landscape(self) -> bool:
        return self.width / self.height >= 1.15

    def scaled(self, base: int) -> int:
        return max(10, int(round(base * self.scale)))


@dataclass
class ReviewData:
    """Full review: title, score out of 10, and review text."""

    title: str
    score: float
    review_text: str
    content_type: ContentType = ContentType.GAME
    cover_image: Optional[CoverSource] = None
    platform: str = "none"
    platform_username: str = ""
    attribution_style: str = "handle"

    def validate(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not 0 <= self.score <= 10:
            raise ValueError("Score must be between 0 and 10")
        if not self.review_text or not self.review_text.strip():
            raise ValueError("Review text cannot be empty")


@dataclass
class StarReviewData:
    """Textless review: title, cover and a star rating (0.5-5.0)."""

    title: str
    stars: float
    content_type: ContentType = ContentType.GAME
    cover_image: Optional[CoverSource] = None
    platform: str = "none"
    platform_username: str = ""
    attribution_style: str = "handle"

    def validate(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not 0.5 <= self.stars <= 5.0:
            raise ValueError("Stars must be between 0.5 and 5.0")


@dataclass
class ScoreCardData:
    """Minimal score card: cover framed with glow + big numeric score."""

    title: str
    score: float
    content_type: ContentType = ContentType.GAME
    cover_image: Optional[CoverSource] = None
    platform: str = "none"
    platform_username: str = ""
    attribution_style: str = "handle"

    def validate(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not 0 <= self.score <= 10:
            raise ValueError("Score must be between 0 and 10")
