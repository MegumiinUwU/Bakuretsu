"""Text shaping and wrapping with full Arabic (RTL) support.

The rules that make Arabic come out correctly:

1. Wrap on the *logical* (unshaped) text, word by word.
2. Shape each wrapped line individually with ``arabic_reshaper`` (joins
   the letterforms) and then run the bidi algorithm (fixes visual order).
   Shaping before wrapping would break letter joins at line boundaries;
   running bidi on the whole paragraph would reverse the line order.
3. Measure widths on the *shaped* text, since joined Arabic glyphs are
   narrower than isolated ones.
4. Right-align lines whose base direction is RTL.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import ImageFont

_ARABIC_RE = re.compile(
    "["
    "؀-ۿ"  # Arabic
    "ݐ-ݿ"  # Arabic Supplement
    "ࢠ-ࣿ"  # Arabic Extended-A
    "ﭐ-﷿"  # Arabic Presentation Forms-A
    "ﹰ-﻿"  # Arabic Presentation Forms-B
    "]"
)

_reshaper = arabic_reshaper.ArabicReshaper(
    configuration={"delete_harakat": False, "support_ligatures": True}
)


def contains_arabic(text: str) -> bool:
    return bool(_ARABIC_RE.search(text))


def is_rtl(text: str) -> bool:
    """True when the first strong-directional character is Arabic."""
    for ch in text:
        if _ARABIC_RE.match(ch):
            return True
        if ch.isalpha():  # first strong char is Latin -> LTR paragraph
            return False
    return False


def shape(text: str) -> str:
    """Return display-ready text (reshaped + bidi) for a single line."""
    if not contains_arabic(text):
        return text
    return get_display(_reshaper.reshape(text))


@dataclass(frozen=True)
class Line:
    """One wrapped, display-ready line of text."""

    display: str  # what to hand to PIL's draw.text
    rtl: bool  # right-align when True
    width: int  # measured pixel width of the shaped text


def measure(text: str, font: ImageFont.ImageFont) -> int:
    bbox = font.getbbox(text)
    return int(bbox[2] - bbox[0])


def wrap(text: str, font: ImageFont.ImageFont, max_width: int) -> list[Line]:
    """Wrap logical text into shaped lines that fit within ``max_width``.

    Handles explicit newlines, mixed Arabic/English input and words longer
    than the line (kept on their own line as a last resort).
    """
    lines: list[Line] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            continue
        current: list[str] = []
        for word in words:
            candidate = " ".join(current + [word])
            if measure(shape(candidate), font) <= max_width or not current:
                current.append(word)
            else:
                lines.append(_make_line(" ".join(current), font))
                current = [word]
        if current:
            lines.append(_make_line(" ".join(current), font))
    return lines


def _make_line(logical: str, font: ImageFont.ImageFont) -> Line:
    display = shape(logical)
    return Line(display=display, rtl=is_rtl(logical), width=measure(display, font))


def ellipsize(line: Line, font: ImageFont.ImageFont, max_width: int) -> Line:
    """Trim a line until it fits, appending an ellipsis on the correct side."""
    display = "…" + line.display if line.rtl else line.display + "…"
    while measure(display, font) > max_width and len(display) > 4:
        display = "…" + display[2:] if line.rtl else display[:-2] + "…"
    return Line(display=display, rtl=line.rtl, width=measure(display, font))
