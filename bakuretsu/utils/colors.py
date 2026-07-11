"""Color helpers."""

from __future__ import annotations

from bakuretsu.models import RGB


def hex_to_rgb(hex_color: str) -> RGB:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def rgb_to_hex(rgb: RGB) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def score_color(score: float) -> RGB:
    """Traffic-light color for a 0-10 score."""
    if score >= 8:
        return (34, 197, 94)  # green
    if score >= 6:
        return (234, 179, 8)  # yellow
    if score >= 4:
        return (249, 115, 22)  # orange
    return (239, 68, 68)  # red


def format_score(score: float, with_denominator: bool = True) -> str:
    text = str(int(score)) if score == int(score) else f"{score:.1f}"
    return f"{text}/10" if with_denominator else text
