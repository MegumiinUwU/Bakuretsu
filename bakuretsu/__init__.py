"""
Bakuretsu — Review card generator toolkit.

Public API:
    create_review_card(...)   Full review card (title, cover, score, text)
    create_star_card(...)     Textless star-rating card
    create_score_card(...)    Minimal cover + big score card
"""

from bakuretsu.api import (
    create_collage_card,
    create_review_card,
    create_score_card,
    create_star_card,
)
from bakuretsu.models import (
    CardStyle,
    CollageData,
    CollageEntry,
    ContentType,
    ReviewData,
    ScoreCardData,
    StarReviewData,
)
from bakuretsu.settings import AppSettings

__version__ = "2.1.0"

__all__ = [
    "create_review_card",
    "create_star_card",
    "create_score_card",
    "create_collage_card",
    "CardStyle",
    "ContentType",
    "ReviewData",
    "StarReviewData",
    "ScoreCardData",
    "CollageData",
    "CollageEntry",
    "AppSettings",
]
