"""Platform registry.

To add a platform: write (or reuse) a logo drawer in ``logos.py`` and
append one ``PlatformSpec`` to ``PLATFORMS``. The UI dropdown, settings
dialog and attribution rendering all read from this registry.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from PIL import Image

from bakuretsu.models import RGB
from bakuretsu.platforms import logos

LOGO_DIR = Path("assets/logos")


@dataclass(frozen=True)
class PlatformSpec:
    key: str  # stable id used in settings.json and the API
    name: str  # display name written on cards
    accent: RGB
    draw_logo: Callable[[int], Image.Image]
    search_url: str = ""  # {query} is replaced with the URL-encoded title

    def share_link(self, title: str) -> str:
        from urllib.parse import quote

        return self.search_url.format(query=quote(title)) if self.search_url else ""

    def logo(self, size: int) -> Image.Image:
        """User-provided PNG override if present, else the drawn logo."""
        override = LOGO_DIR / f"{self.key}.png"
        if override.exists():
            try:
                img = Image.open(override).convert("RGBA")
                return img.resize((size, size), Image.Resampling.LANCZOS)
            except OSError:
                pass
        return self.draw_logo(size)

    def attribution_text(self, username: str, style: str) -> str:
        """Compose the credit line according to the attribution style."""
        handle = f"@{username}" if username else ""
        if style == "follow":
            return f"Follow me on {self.name}" + (f"  {handle}" if handle else "")
        if style == "posted":
            return f"Posted on {self.name}" + (f" by {handle}" if handle else "")
        return handle or self.name


PLATFORMS: dict[str, PlatformSpec] = {
    "backloggd": PlatformSpec(
        key="backloggd",
        name="Backloggd",
        accent=(139, 92, 246),
        draw_logo=logos.draw_backloggd,
        search_url="https://backloggd.com/search/games/{query}/",
    ),
    "letterboxd": PlatformSpec(
        key="letterboxd",
        name="Letterboxd",
        accent=(255, 128, 0),
        draw_logo=logos.draw_letterboxd,
        search_url="https://letterboxd.com/search/{query}/",
    ),
    "myanimelist": PlatformSpec(
        key="myanimelist",
        name="MyAnimeList",
        accent=(46, 81, 162),
        draw_logo=logos.draw_myanimelist,
        search_url="https://myanimelist.net/search/all?q={query}",
    ),
}

# Accepted aliases -> canonical keys (keeps old scripts working).
_ALIASES = {"mal": "myanimelist"}


def get_platform(key: str) -> Optional[PlatformSpec]:
    """Look up a platform; returns None for 'none'/'' or unknown keys."""
    key = (key or "none").strip().lower()
    key = _ALIASES.get(key, key)
    return PLATFORMS.get(key)
