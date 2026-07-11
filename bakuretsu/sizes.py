"""Card size presets tuned for social media platforms.

Add a new preset by appending a ``SizePreset`` to ``SIZE_PRESETS`` —
the UI dropdown and the API pick it up automatically.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SizePreset:
    name: str
    width: int
    height: int
    note: str = ""


SIZE_PRESETS: list[SizePreset] = [
    SizePreset("Landscape (Default)", 1200, 675, "16:9, good everywhere"),
    SizePreset("X / Twitter Post", 1600, 900, "16:9 timeline image"),
    SizePreset("Instagram Square", 1080, 1080, "1:1 feed post"),
    SizePreset("Instagram Portrait", 1080, 1350, "4:5 feed post"),
    SizePreset("Instagram / TikTok Story", 1080, 1920, "9:16 full screen"),
    SizePreset("Facebook Post", 1200, 630, "link/feed image"),
    SizePreset("Reddit Post", 1200, 628, "feed preview"),
    SizePreset("Discord Embed", 1280, 720, "16:9 embed"),
    SizePreset("YouTube Thumbnail", 1280, 720, "16:9"),
    SizePreset("Pinterest Pin", 1000, 1500, "2:3 pin"),
]


def preset_names() -> list[str]:
    return [p.name for p in SIZE_PRESETS] + ["Custom"]


def get_preset(name: str) -> Optional[SizePreset]:
    for preset in SIZE_PRESETS:
        if preset.name == name:
            return preset
    return None
