"""Winter decoration: crystalline snowflakes, falling snow and drifts."""

from __future__ import annotations

import math

from PIL import Image, ImageDraw

from bakuretsu.themes.decorations.common import composite, overlay_for, rng_for

SNOW = (240, 249, 255)
ICE = (125, 211, 252)


def _snowflake(size: int, alpha: int) -> Image.Image:
    """Six-armed flake with side branches."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = size // 2
    arm = size // 2 - 1
    color = (*SNOW, alpha)
    for i in range(6):
        ang = math.radians(i * 60)
        ex = cx + arm * math.cos(ang)
        ey = cy + arm * math.sin(ang)
        d.line([(cx, cy), (ex, ey)], fill=color, width=max(1, size // 24))
        # two branches per arm at 60% radius
        bx = cx + arm * 0.6 * math.cos(ang)
        by = cy + arm * 0.6 * math.sin(ang)
        for spread in (-30, 30):
            bang = math.radians(i * 60 + spread)
            d.line(
                [(bx, by), (bx + arm * 0.25 * math.cos(bang), by + arm * 0.25 * math.sin(bang))],
                fill=color,
                width=max(1, size // 30),
            )
    return img


def draw(card: Image.Image, style) -> None:
    w, h = card.size
    rng = rng_for(card, seed=21)
    layer, d = overlay_for(card)

    # a few large detailed flakes
    for _ in range(max(5, (w * h) // 200000)):
        size = rng.randint(max(24, min(w, h) // 20), max(40, min(w, h) // 10))
        flake = _snowflake(size, rng.randint(60, 130))
        layer.alpha_composite(flake, (rng.randint(0, w - size), rng.randint(0, h - size)))

    # falling snow dots
    for _ in range(max(60, (w * h) // 14000)):
        x, y = rng.randint(0, w), rng.randint(0, h)
        r = rng.choice((1, 1, 2, 2, 3))
        d.ellipse([(x - r, y - r), (x + r, y + r)], fill=(*SNOW, rng.randint(50, 150)))

    # layered snow drifts along the bottom
    drift_h = max(24, h // 14)
    for i, (alpha, lift) in enumerate([(50, 0.0), (75, 0.45), (110, 0.9)]):
        band = Image.new("RGBA", (w * 2, drift_h * 4), (0, 0, 0, 0))
        bd = ImageDraw.Draw(band)
        bd.ellipse([(0, 0), (w * 2, drift_h * 4)], fill=(*SNOW, alpha))
        offset_x = -w // 2 + int(i * w / 3) - w // 3
        layer.alpha_composite(band, (offset_x, h - int(drift_h * (1.6 - lift))))

    # icy accent sparkles
    for _ in range(10):
        x, y = rng.randint(0, w), rng.randint(0, int(h * 0.7))
        arm = rng.randint(3, 7)
        d.line([(x - arm, y), (x + arm, y)], fill=(*ICE, 120), width=1)
        d.line([(x, y - arm), (x, y + arm)], fill=(*ICE, 120), width=1)

    composite(card, layer)
