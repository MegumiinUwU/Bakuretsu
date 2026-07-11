"""Convenience functions — the stable programmatic API.

Example:
    from bakuretsu import create_review_card

    create_review_card(
        title="OMORI",
        score=9.0,
        review_text="A hauntingly beautiful RPG...",
        cover_image="https://example.com/omori.jpg",
        platform="backloggd",
        platform_username="YourUser",
        theme="Ramadan",
        size="Instagram Square",
        output_path="output/omori.png",
    )
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from PIL import Image

from bakuretsu.models import (
    CardStyle,
    CollageData,
    CollageEntry,
    ContentType,
    ReviewData,
    ScoreCardData,
    StarReviewData,
)
from bakuretsu.rendering import (
    CollageCardRenderer,
    ReviewCardRenderer,
    ScoreCardRenderer,
    StarCardRenderer,
)
from bakuretsu.sizes import get_preset
from bakuretsu.themes import get_theme
from bakuretsu.utils.colors import hex_to_rgb


def build_style(
    theme: Optional[str] = None,
    size: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    corner_radius: int = 0,
    **overrides,
) -> CardStyle:
    """Assemble a CardStyle from a theme name and/or size preset name."""
    kwargs: dict = {"corner_radius": corner_radius}

    if theme:
        theme_obj = get_theme(theme)
        if theme_obj is None:
            raise ValueError(f"Unknown theme: {theme!r}")
        palette = theme_obj.palette
        kwargs.update(
            background_color=(*hex_to_rgb(palette["background"]), 255),
            primary_color=hex_to_rgb(palette["primary"]),
            secondary_color=hex_to_rgb(palette["secondary"]),
            accent_color=hex_to_rgb(palette["accent"]),
            theme=theme if theme_obj.decorated else None,
        )

    if size:
        preset = get_preset(size)
        if preset is None:
            raise ValueError(f"Unknown size preset: {size!r}")
        kwargs.update(width=preset.width, height=preset.height)
    if width:
        kwargs["width"] = width
    if height:
        kwargs["height"] = height

    kwargs.update(overrides)
    return CardStyle(**kwargs)


def _style_or_build(style, theme, size, width, height) -> CardStyle:
    if style is not None:
        return style
    return build_style(theme=theme, size=size, width=width, height=height)


def create_review_card(
    title: str,
    score: float,
    review_text: str,
    content_type: str = "game",
    cover_image=None,
    platform: str = "none",
    platform_username: str = "",
    attribution_style: str = "handle",
    theme: Optional[str] = None,
    size: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    style: Optional[CardStyle] = None,
    output_path: Optional[Union[str, Path]] = None,
) -> Image.Image:
    """Generate a full review card (title, cover, score, review text)."""
    data = ReviewData(
        title=title,
        score=score,
        review_text=review_text,
        content_type=ContentType(content_type.lower()),
        cover_image=cover_image,
        platform=platform,
        platform_username=platform_username,
        attribution_style=attribution_style,
    )
    renderer = ReviewCardRenderer(_style_or_build(style, theme, size, width, height))
    return renderer.render(data, output_path)


def create_star_card(
    title: str,
    stars: float,
    content_type: str = "game",
    cover_image=None,
    platform: str = "none",
    platform_username: str = "",
    attribution_style: str = "handle",
    theme: Optional[str] = None,
    size: Optional[str] = "Instagram Square",
    width: Optional[int] = None,
    height: Optional[int] = None,
    style: Optional[CardStyle] = None,
    output_path: Optional[Union[str, Path]] = None,
) -> Image.Image:
    """Generate a textless star-rating card (0.5-5.0 stars)."""
    data = StarReviewData(
        title=title,
        stars=stars,
        content_type=ContentType(content_type.lower()),
        cover_image=cover_image,
        platform=platform,
        platform_username=platform_username,
        attribution_style=attribution_style,
    )
    renderer = StarCardRenderer(_style_or_build(style, theme, size, width, height))
    return renderer.render(data, output_path)


# Backwards-compatible alias for the old function name.
create_textless_review_card = create_star_card


def create_collage_card(
    title: str,
    entries: list,
    subtitle: str = "",
    content_type: str = "game",
    platform: str = "none",
    platform_username: str = "",
    attribution_style: str = "handle",
    theme: Optional[str] = None,
    size: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    style: Optional[CardStyle] = None,
    output_path: Optional[Union[str, Path]] = None,
) -> Image.Image:
    """Generate a Top List / Year in Review collage card.

    ``entries`` is an ordered list (rank 1 first) of CollageEntry objects
    or dicts with keys: title, score, and optional cover_image.
    """
    normalized = [
        entry if isinstance(entry, CollageEntry) else CollageEntry(
            title=entry["title"],
            score=float(entry["score"]),
            cover_image=entry.get("cover_image"),
        )
        for entry in entries
    ]
    data = CollageData(
        title=title,
        entries=normalized,
        subtitle=subtitle,
        content_type=ContentType(content_type.lower()),
        platform=platform,
        platform_username=platform_username,
        attribution_style=attribution_style,
    )
    renderer = CollageCardRenderer(_style_or_build(style, theme, size, width, height))
    return renderer.render(data, output_path)


def create_score_card(
    title: str,
    score: float,
    content_type: str = "game",
    cover_image=None,
    platform: str = "none",
    platform_username: str = "",
    attribution_style: str = "handle",
    theme: Optional[str] = None,
    size: Optional[str] = "Instagram Square",
    width: Optional[int] = None,
    height: Optional[int] = None,
    style: Optional[CardStyle] = None,
    output_path: Optional[Union[str, Path]] = None,
) -> Image.Image:
    """Generate a minimal score card (framed cover + big score)."""
    data = ScoreCardData(
        title=title,
        score=score,
        content_type=ContentType(content_type.lower()),
        cover_image=cover_image,
        platform=platform,
        platform_username=platform_username,
        attribution_style=attribution_style,
    )
    renderer = ScoreCardRenderer(_style_or_build(style, theme, size, width, height))
    return renderer.render(data, output_path)
