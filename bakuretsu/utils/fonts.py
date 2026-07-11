"""Font resolution with caching.

Prefers fonts that ship with Windows and have full Arabic coverage
(Segoe UI / Tahoma / Arial) so mixed English + Arabic text renders with
connected letterforms. Custom fonts can be dropped into ``assets/fonts``
or passed explicitly through ``CardStyle.font_path``.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from PIL import ImageFont

ASSETS_FONT_DIR = Path("assets/fonts")

# Ordered candidates: all of these support Arabic script.
_REGULAR_CANDIDATES = [
    "C:/Windows/Fonts/segoeui.ttf",
    "segoeui.ttf",
    "C:/Windows/Fonts/tahoma.ttf",
    "tahoma.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "DejaVuSans.ttf",
]
_BOLD_CANDIDATES = [
    "C:/Windows/Fonts/segoeuib.ttf",
    "segoeuib.ttf",
    "C:/Windows/Fonts/tahomabd.ttf",
    "tahomabd.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "DejaVuSans-Bold.ttf",
]


def _asset_fonts(bold: bool) -> list[str]:
    """User-supplied fonts in assets/fonts, bold ones matched by name."""
    if not ASSETS_FONT_DIR.is_dir():
        return []
    fonts = sorted(str(p) for p in ASSETS_FONT_DIR.glob("*.[to]tf"))
    bolds = [f for f in fonts if "bold" in Path(f).stem.lower()]
    regulars = [f for f in fonts if f not in bolds]
    return bolds + regulars if bold else regulars + bolds


@lru_cache(maxsize=128)
def _load(path: str, size: int) -> Optional[ImageFont.FreeTypeFont]:
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        return None


def load_font(
    size: int,
    bold: bool = False,
    custom_path: Optional[str] = None,
) -> ImageFont.ImageFont:
    """Return the best available font at the given pixel size."""
    candidates: list[str] = []
    if custom_path:
        candidates.append(custom_path)
    candidates += _asset_fonts(bold)
    candidates += _BOLD_CANDIDATES if bold else _REGULAR_CANDIDATES
    for path in candidates:
        font = _load(path, size)
        if font is not None:
            return font
    return ImageFont.load_default(size=size)


def load_emoji_font(size: int) -> Optional[ImageFont.FreeTypeFont]:
    """Color-emoji capable font, if the system has one."""
    for path in (
        "C:/Windows/Fonts/seguiemj.ttf",
        "seguiemj.ttf",
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    ):
        font = _load(path, size)
        if font is not None:
            return font
    return None


class FontSet:
    """The four fonts a card renderer needs, scaled to the card size."""

    def __init__(self, style) -> None:  # style: CardStyle
        regular = style.font_path
        bold = style.bold_font_path or style.font_path
        self.title = load_font(style.scaled(style.base_title_size), bold=True, custom_path=bold)
        self.score = load_font(style.scaled(style.base_score_size), bold=True, custom_path=bold)
        self.review = load_font(style.scaled(style.base_review_size), custom_path=regular)
        self.platform = load_font(style.scaled(style.base_platform_size), custom_path=regular)

    def sized(self, size: int, bold: bool = False) -> ImageFont.ImageFont:
        return load_font(size, bold=bold)
