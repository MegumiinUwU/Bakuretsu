"""Youssef Mohamed theme: Sonic-inspired artwork.

Golden rings with sparkles, speed streaks across the sky, and a
Green Hill Zone footer: wavy grass over a checkered dirt strip.
"""

from __future__ import annotations

from PIL import Image, ImageDraw

from bakuretsu.themes.decorations.common import composite, overlay_for, rng_for

RING_GOLD = (255, 210, 63)
RING_DEEP = (214, 158, 20)
GRASS = (46, 204, 64)
GRASS_DARK = (30, 150, 48)
DIRT_LIGHT = (205, 122, 52)
DIRT_DARK = (140, 78, 30)
STREAK = (170, 205, 255)


def _ring(size: int, alpha: int = 230) -> Image.Image:
    """Classic gold ring: thick torus with a bright top highlight."""
    os = 4
    big = size * os
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    thickness = max(os * 2, big // 7)
    inset = thickness // 2 + os
    box = [(inset, inset), (big - inset, big - inset)]
    # deep gold base, brighter gold body, light glint on top-left
    d.ellipse(box, outline=(*RING_DEEP, alpha), width=thickness)
    d.ellipse(
        [(inset + os, inset + os), (big - inset - os, big - inset - os)],
        outline=(*RING_GOLD, alpha),
        width=thickness - os * 2,
    )
    d.arc(box, 190, 300, fill=(255, 240, 170, alpha), width=max(os, thickness // 3))
    return img.resize((size, size), Image.Resampling.LANCZOS)


def _sparkle(d: ImageDraw.ImageDraw, x: int, y: int, r: int, alpha: int) -> None:
    """Four-point ring twinkle."""
    color = (255, 250, 210, alpha)
    d.polygon(
        [(x, y - r), (x + r // 3, y - r // 3), (x + r, y), (x + r // 3, y + r // 3),
         (x, y + r), (x - r // 3, y + r // 3), (x - r, y), (x - r // 3, y - r // 3)],
        fill=color,
    )


def _green_hill_strip(width: int, height: int) -> Image.Image:
    """Checkered dirt with a bumpy grass edge on top."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    grass_h = max(8, height // 4)
    dirt_top = grass_h

    # checkered dirt
    square = max(10, height // 3)
    for row in range((height - dirt_top) // square + 1):
        for col in range(width // square + 1):
            shade = DIRT_LIGHT if (row + col) % 2 == 0 else DIRT_DARK
            x0 = col * square
            y0 = dirt_top + row * square
            d.rectangle(
                [(x0, y0), (min(x0 + square, width), min(y0 + square, height))],
                fill=(*shade, 235),
            )

    # grass band with rounded bumps along the top edge
    d.rectangle([(0, grass_h // 2), (width, dirt_top + 2)], fill=(*GRASS, 245))
    bump_r = grass_h
    for x in range(-bump_r, width + bump_r, int(bump_r * 1.4)):
        d.ellipse([(x, 0), (x + bump_r * 2, bump_r * 2)], fill=(*GRASS, 245))
    # darker underline where grass meets dirt
    d.rectangle([(0, dirt_top), (width, dirt_top + max(2, height // 20))], fill=(*GRASS_DARK, 245))
    return img


def draw(card: Image.Image, style) -> None:
    w, h = card.size
    rng = rng_for(card, seed=91)
    layer, d = overlay_for(card)

    # speed streaks: horizontal dashes suggesting a blue blur running past
    for _ in range(max(10, (w * h) // 70000)):
        y = rng.randint(0, int(h * 0.72))
        length = rng.randint(w // 14, w // 4)
        x = rng.randint(-length // 2, w)
        alpha = rng.randint(25, 70)
        thickness = rng.choice((2, 2, 3, 4))
        d.rounded_rectangle(
            [(x, y), (x + length, y + thickness)],
            radius=thickness // 2,
            fill=(*STREAK, alpha),
        )

    # golden rings drifting across the upper card
    ring_base = max(28, min(w, h) // 10)
    spots = [
        (0.80, 0.08, 1.35, 235), (0.90, 0.30, 0.9, 210), (0.68, 0.22, 0.7, 190),
        (0.06, 0.58, 0.8, 200), (0.45, 0.07, 0.6, 170), (0.24, 0.10, 0.45, 150),
    ]
    for fx, fy, scale, alpha in spots:
        size = int(ring_base * scale)
        ring = _ring(size, alpha)
        rx, ry = int(w * fx), int(h * fy)
        layer.alpha_composite(ring, (rx, ry))
        if scale >= 0.7:  # twinkle beside the bigger rings
            _sparkle(
                d, rx + size + rng.randint(2, 10), ry + rng.randint(0, size // 3),
                max(4, size // 7), rng.randint(140, 220),
            )

    # a few loose twinkles in the sky
    for _ in range(6):
        _sparkle(
            d, rng.randint(0, w), rng.randint(0, int(h * 0.5)),
            rng.randint(3, 7), rng.randint(60, 130),
        )

    # Green Hill Zone footer
    strip_h = max(36, int(h * 0.12))
    strip = _green_hill_strip(w, strip_h)
    layer.alpha_composite(strip, (0, h - strip_h + strip_h // 6))

    composite(card, layer)
