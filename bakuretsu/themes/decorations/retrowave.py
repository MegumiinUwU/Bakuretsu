"""Retrowave decoration: banded sun on the horizon and a perspective grid."""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter

from bakuretsu.themes.decorations.common import (
    composite,
    glow_paste,
    overlay_for,
    rng_for,
    scatter_stars,
)

SUN_TOP = (255, 94, 158)
SUN_BOTTOM = (255, 179, 71)
GRID = (0, 217, 255)


def _sun(size: int) -> Image.Image:
    """Gradient sun with the classic horizontal cuts near the bottom."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # vertical gradient bands inside a circle mask
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([(0, 0), (size - 1, size - 1)], fill=255)
    for y in range(size):
        t = y / size
        color = tuple(int(a + (b - a) * t) for a, b in zip(SUN_TOP, SUN_BOTTOM))
        d.line([(0, y), (size, y)], fill=(*color, 220))
    img.putalpha(mask)
    # carve horizontal slits, wider toward the bottom
    carve = ImageDraw.Draw(img)
    slit_y = int(size * 0.55)
    gap = max(2, size // 40)
    while slit_y < size:
        carve.rectangle([(0, slit_y), (size, slit_y + gap)], fill=(0, 0, 0, 0))
        slit_y += gap * 3
        gap = int(gap * 1.35) + 1
    return img


def draw(card: Image.Image, style) -> None:
    w, h = card.size
    rng = rng_for(card, seed=88)
    layer, d = overlay_for(card)

    scatter_stars(d, rng, w, int(h * 0.5), count=max(20, (w * h) // 40000), color=(255, 255, 255), max_alpha=110)

    horizon = int(h * 0.72)

    # sun sitting on the horizon, centered right of middle
    sun_size = max(80, min(w, h) // 3)
    sun = _sun(sun_size)
    sx = int(w * 0.68) - sun_size // 2
    sy = horizon - sun_size + int(sun_size * 0.12)
    glow_paste(layer, sun, sx, sy, blur=sun_size / 10)

    # perspective grid below the horizon
    grid_alpha = 70
    # horizontal lines, spacing grows toward the bottom edge
    y = horizon
    step = max(3, h // 90)
    while y < h:
        d.line([(0, y), (w, y)], fill=(*GRID, grid_alpha), width=1)
        y += step
        step = int(step * 1.35) + 1
    # radial verticals from a vanishing point on the horizon
    vp_x = w // 2
    for i in range(-12, 13):
        x_bottom = vp_x + i * (w // 10)
        d.line([(vp_x, horizon), (x_bottom, h)], fill=(*GRID, grid_alpha), width=1)
    # horizon glow line
    d.line([(0, horizon), (w, horizon)], fill=(*GRID, 160), width=2)

    composite(card, layer)
