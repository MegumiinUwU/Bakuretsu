"""Persistent app settings (usernames, defaults, attribution style).

Stored as ``settings.json`` next to the project (gitignored, since it
holds personal handles). Missing keys fall back to defaults, so the file
survives upgrades.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path

SETTINGS_FILE = Path("settings.json")

# How the platform credit line is written on the card.
ATTRIBUTION_STYLES: dict[str, str] = {
    "handle": "@username only",
    "follow": "Follow me on <platform>",
    "posted": "Posted on <platform> by @username",
}


@dataclass
class AppSettings:
    """User preferences that persist between sessions."""

    usernames: dict[str, str] = field(default_factory=dict)  # platform key -> handle
    default_platform: str = "none"
    attribution_style: str = "handle"  # key of ATTRIBUTION_STYLES
    default_theme: str = "Bakuretsu Dark"
    default_size: str = "Landscape (Default)"
    default_content_type: str = "game"
    output_dir: str = "output"

    def username_for(self, platform_key: str) -> str:
        return self.usernames.get(platform_key, "")

    @classmethod
    def load(cls, path: Path = SETTINGS_FILE) -> "AppSettings":
        settings = cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return settings
        for key, value in data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        if settings.attribution_style not in ATTRIBUTION_STYLES:
            settings.attribution_style = "handle"
        return settings

    def save(self, path: Path = SETTINGS_FILE) -> None:
        path.write_text(
            json.dumps(asdict(self), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
