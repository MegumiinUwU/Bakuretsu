"""Shared drawing helpers for theme decorations."""

from __future__ import annotations

import random
from typing import Iterator

from PIL import Image, ImageDraw, ImageFilter


def overlay_for(card: Image.Image) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    """Transparent layer matching the card, to be alpha-composited on top."""
    layer = Image.new("RGBA", card.size, (0, 0, 0, 0))
    return layer, ImageDraw.Draw(layer)


def composite(card: Image.Image, layer: Image.Image, blur: float = 0.0) -> None:
    if blur > 0:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    card.alpha_composite(layer)


def glow_paste(
    layer: Image.Image,
    sprite: Image.Image,
    x: int,
    y: int,
    blur: float,
) -> None:
    """Paste a sprite with a soft halo. The halo is blurred on a padded
    canvas so it fades out instead of being clipped into a square."""
    pad = int(blur * 3)
    padded = Image.new("RGBA", (sprite.width + pad * 2, sprite.height + pad * 2), (0, 0, 0, 0))
    padded.alpha_composite(sprite, (pad, pad))
    halo = padded.filter(ImageFilter.GaussianBlur(blur))
    layer.alpha_composite(halo, (x - pad, y - pad))
    layer.alpha_composite(sprite, (x, y))


def rng_for(card: Image.Image, seed: int) -> random.Random:
    """Deterministic randomness — same card size, same decoration layout."""
    return random.Random((card.width, card.height, seed).__hash__())


def scatter_stars(
    draw: ImageDraw.ImageDraw,
    rng: random.Random,
    width: int,
    height: int,
    count: int,
    color: tuple[int, int, int],
    max_alpha: int = 140,
) -> None:
    """Small dot stars with occasional 4-point sparkles."""
    for _ in range(count):
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        alpha = rng.randint(max_alpha // 3, max_alpha)
        r = rng.choice((1, 1, 1, 2, 2, 3))
        draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=(*color, alpha))
        if r >= 2 and rng.random() < 0.4:  # sparkle cross
            arm = r * 3
            draw.line([(x - arm, y), (x + arm, y)], fill=(*color, alpha // 2), width=1)
            draw.line([(x, y - arm), (x, y + arm)], fill=(*color, alpha // 2), width=1)


def blit_bitmap(
    draw: ImageDraw.ImageDraw,
    bitmap: list[str],
    x: int,
    y: int,
    px: int,
    color: tuple[int, int, int, int],
) -> None:
    """Draw a pixel-art bitmap ('#' = filled) at (x, y) with pixel size px."""
    for row_i, row in enumerate(bitmap):
        for col_i, ch in enumerate(row):
            if ch == "#":
                x0 = x + col_i * px
                y0 = y + row_i * px
                draw.rectangle([(x0, y0), (x0 + px - 1, y0 + px - 1)], fill=color)


def bitmap_size(bitmap: list[str], px: int) -> tuple[int, int]:
    return max(len(r) for r in bitmap) * px, len(bitmap) * px
