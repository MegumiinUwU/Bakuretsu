"""Sakura decoration: blossom branch in the top corner and drifting petals."""

from __future__ import annotations

import math

from PIL import Image, ImageDraw

from bakuretsu.themes.decorations.common import composite, overlay_for, rng_for

PETAL = (249, 168, 196)
PETAL_DEEP = (236, 120, 165)
BRANCH = (74, 48, 42)


def _petal(size: int, angle: float, alpha: int) -> Image.Image:
    """Single teardrop petal with a notched tip."""
    os = 3
    big = size * os
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([(big // 4, 0), (big * 3 // 4, big - 1)], fill=(*PETAL, alpha))
    # notch at the top to suggest the sakura petal cleft
    d.polygon(
        [(big // 2, 0), (big // 2 - big // 10, big // 6), (big // 2 + big // 10, big // 6)],
        fill=(0, 0, 0, 0),
    )
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)


def _blossom(size: int, alpha: int = 220) -> Image.Image:
    """Five-petal flower."""
    img = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = size
    pr = size // 2
    for i in range(5):
        ang = math.radians(i * 72 - 90)
        px = cx + int(size * 0.55 * math.cos(ang))
        py = cy + int(size * 0.55 * math.sin(ang))
        d.ellipse([(px - pr, py - pr), (px + pr, py + pr)], fill=(*PETAL, alpha))
    core = size // 4
    d.ellipse([(cx - core, cy - core), (cx + core, cy + core)], fill=(*PETAL_DEEP, alpha))
    return img


def draw(card: Image.Image, style) -> None:
    w, h = card.size
    rng = rng_for(card, seed=33)
    layer, d = overlay_for(card)

    # branch sweeping in from the top-right corner
    unit = max(30, min(w, h) // 9)
    thick = max(4, unit // 8)
    points = [
        (w + 10, int(h * 0.02)),
        (w - unit * 2, int(h * 0.10)),
        (w - unit * 3.6, int(h * 0.14)),
        (w - unit * 5.0, int(h * 0.24)),
    ]
    for a, b in zip(points, points[1:]):
        d.line([a, b], fill=(*BRANCH, 230), width=thick)
    # twigs
    d.line([points[1], (w - unit * 2.8, int(h * 0.02))], fill=(*BRANCH, 220), width=max(2, thick // 2))
    d.line([points[2], (w - unit * 4.2, int(h * 0.06))], fill=(*BRANCH, 220), width=max(2, thick // 2))

    # blossom clusters along the branch
    blossom_spots = [points[1], points[2], points[3], (w - unit * 2.8, int(h * 0.02)), (w - unit * 4.2, int(h * 0.06))]
    for bx, by in blossom_spots:
        for _ in range(3):
            size = rng.randint(unit // 4, unit // 2)
            flower = _blossom(size, alpha=rng.randint(190, 240))
            ox = int(bx) - flower.width // 2 + rng.randint(-unit // 3, unit // 3)
            oy = int(by) - flower.height // 2 + rng.randint(-unit // 4, unit // 4)
            layer.alpha_composite(flower, (ox, oy))

    # drifting petals everywhere (denser on the right)
    for _ in range(max(14, (w * h) // 60000)):
        size = rng.randint(max(6, unit // 6), max(10, unit // 3))
        x = rng.randint(0, w - size * 2)
        y = rng.randint(0, h - size * 2)
        petal = _petal(size, rng.uniform(0, 360), rng.randint(70, 170))
        layer.alpha_composite(petal, (x, y))

    composite(card, layer)
