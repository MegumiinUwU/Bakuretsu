"""Theme registry: every entry the UI shows in the theme dropdown.

A theme = a palette + an optional decoration drawer.

To add a plain palette theme: add the palette in ``palettes.py``, then a
``Theme(palette_name)`` entry here. To add a decorated theme: also write
a ``draw(card, style)`` module under ``decorations/`` and reference it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from PIL import Image

from bakuretsu.themes.decorations import (
    arcade,
    cinema,
    exams,
    halloween,
    ramadan,
    retrowave,
    sakura,
    winter,
)
from bakuretsu.themes.palettes import PALETTES, Palette

Decorator = Callable[[Image.Image, object], None]  # (card, style) -> None


@dataclass(frozen=True)
class Theme:
    palette_name: str
    decorator: Optional[Decorator] = None

    @property
    def palette(self) -> Palette:
        return PALETTES[self.palette_name]

    @property
    def decorated(self) -> bool:
        return self.decorator is not None


THEMES: dict[str, Theme] = {
    # Plain palettes
    "Bakuretsu Dark": Theme("Bakuretsu Dark"),
    "Midnight Blue": Theme("Midnight Blue"),
    "Deep Purple": Theme("Deep Purple"),
    "Ocean": Theme("Ocean"),
    "Forest": Theme("Forest"),
    "Sunset": Theme("Sunset"),
    "Monochrome": Theme("Monochrome"),
    "Crimson": Theme("Crimson"),
    "Gold Luxe": Theme("Gold Luxe"),
    "Coffee": Theme("Coffee"),
    "Paper Light": Theme("Paper Light"),
    "Mint Light": Theme("Mint Light"),
    # Decorated themes
    "Retrowave": Theme("Retrowave", retrowave.draw),
    "Ramadan": Theme("Ramadan", ramadan.draw),
    "Exams Time": Theme("Exams Time", exams.draw),
    "Sakura": Theme("Sakura", sakura.draw),
    "Halloween": Theme("Halloween", halloween.draw),
    "Winter": Theme("Winter", winter.draw),
    "Arcade": Theme("Arcade", arcade.draw),
    "Cinema": Theme("Cinema", cinema.draw),
}


def theme_names() -> list[str]:
    return list(THEMES.keys())


def get_theme(name: str) -> Optional[Theme]:
    if name in THEMES:
        return THEMES[name]
    # tolerate lowercase keys coming from the API / old scripts
    for theme_name, theme in THEMES.items():
        if theme_name.lower() == (name or "").lower():
            return theme
    return None
