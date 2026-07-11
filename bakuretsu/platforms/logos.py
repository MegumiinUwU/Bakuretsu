"""Programmatic platform logos.

If ``assets/logos/<key>.png`` exists it always wins; these drawings are
the guaranteed fallback so cards never ship with a blank circle.
Each drawer returns an RGBA image of the requested square size.
"""

from __future__ import annotations

from PIL import Image, ImageDraw

from bakuretsu.utils.fonts import load_font


def _canvas(size: int, oversample: int = 4) -> tuple[Image.Image, ImageDraw.ImageDraw, int]:
    """Big canvas we draw on, later downscaled for smooth edges."""
    big = size * oversample
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img), big


def _finish(img: Image.Image, size: int) -> Image.Image:
    return img.resize((size, size), Image.Resampling.LANCZOS)


def draw_letterboxd(size: int) -> Image.Image:
    """Three overlapping circles: orange, green, blue."""
    img, draw, big = _canvas(size)
    r = int(big * 0.30)
    cy = big // 2
    centers = [
        (int(big * 0.28), cy, (255, 128, 0, 255)),   # orange
        (int(big * 0.50), cy, (0, 224, 84, 255)),    # green
        (int(big * 0.72), cy, (64, 188, 244, 255)),  # blue
    ]
    for cx, cyy, color in centers:
        draw.ellipse([(cx - r, cyy - r), (cx + r, cyy + r)], fill=color)
    return _finish(img, size)


def draw_backloggd(size: int) -> Image.Image:
    """Dark rounded tile with a purple 'B'."""
    img, draw, big = _canvas(size)
    draw.rounded_rectangle(
        [(0, 0), (big - 1, big - 1)], radius=big // 5, fill=(28, 24, 38, 255)
    )
    font = load_font(int(big * 0.72), bold=True)
    draw.text(
        (big // 2, int(big * 0.46)),
        "B",
        font=font,
        fill=(163, 140, 255, 255),
        anchor="mm",
    )
    return _finish(img, size)


def draw_myanimelist(size: int) -> Image.Image:
    """MAL blue rounded tile with white 'MAL'."""
    img, draw, big = _canvas(size)
    draw.rounded_rectangle(
        [(0, 0), (big - 1, big - 1)], radius=big // 5, fill=(46, 81, 162, 255)
    )
    font = load_font(int(big * 0.40), bold=True)
    draw.text(
        (big // 2, int(big * 0.48)),
        "MAL",
        font=font,
        fill=(255, 255, 255, 255),
        anchor="mm",
    )
    return _finish(img, size)
