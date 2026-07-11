"""Halloween decoration: glowing moon, bats, pumpkins and a corner spiderweb."""

from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageFilter

from bakuretsu.themes.decorations.common import (
    composite,
    glow_paste,
    overlay_for,
    rng_for,
    scatter_stars,
)

MOON = (250, 245, 220)
BAT = (16, 10, 24)
PUMPKIN = (249, 115, 22)
WEB = (200, 200, 215)


def _bat(size: int, angle: float, alpha: int = 230) -> Image.Image:
    """Silhouette bat: body + two scalloped wings."""
    w, h = size * 2, size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = w // 2, h // 2
    color = (*BAT, alpha)
    # wings as polygons with scalloped bottom edges
    for side in (-1, 1):
        tip_x = cx + side * size
        d.polygon(
            [
                (cx, cy),
                (cx + side * size // 3, cy - h // 3),
                (tip_x, cy - h // 4),
                (cx + side * size * 3 // 4, cy + h // 8),
                (cx + side * size // 2, cy - h // 12),
                (cx + side * size // 4, cy + h // 6),
            ],
            fill=color,
        )
    # body + ears
    body_r = max(2, size // 6)
    d.ellipse([(cx - body_r, cy - body_r), (cx + body_r, cy + body_r * 2)], fill=color)
    d.polygon([(cx - body_r, cy - body_r), (cx - body_r // 3, cy - body_r * 2), (cx, cy - body_r)], fill=color)
    d.polygon([(cx + body_r, cy - body_r), (cx + body_r // 3, cy - body_r * 2), (cx, cy - body_r)], fill=color)
    return img.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)


def _pumpkin(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    body_top = size // 5
    # segmented body: three overlapping ellipses
    for frac, shade in ((1.0, PUMPKIN), (0.62, (255, 140, 50)), (0.28, (255, 165, 80))):
        half = int(size * frac / 2)
        d.ellipse([(size // 2 - half, body_top), (size // 2 + half, size - 1)], outline=None, fill=(*shade, 235))
    # stem
    d.rectangle([(size // 2 - size // 16, 0), (size // 2 + size // 16, body_top + 2)], fill=(90, 60, 30, 235))
    # jack-o-lantern face
    eye = size // 7
    ey = body_top + size // 4
    for ex in (size // 3, size * 2 // 3):
        d.polygon([(ex - eye, ey + eye), (ex + eye, ey + eye), (ex, ey - eye // 2)], fill=(20, 8, 4, 235))
    # jagged grin
    gy = size * 2 // 3
    d.arc([(size // 5, gy - size // 4), (size * 4 // 5, gy + size // 6)], 15, 165, fill=(20, 8, 4, 235), width=max(2, size // 14))
    return img


def _web(size: int) -> Image.Image:
    """Quarter spiderweb anchored to the top-left corner."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    color = (*WEB, 90)
    spokes = 5
    for i in range(spokes + 1):
        ang = math.radians(90 * i / spokes)
        d.line([(0, 0), (int(size * math.cos(ang)), int(size * math.sin(ang)))], fill=color, width=1)
    for ring in (0.3, 0.55, 0.8, 1.0):
        r = size * ring
        d.arc([(-r, -r), (r, r)], 0, 90, fill=color, width=1)
    return img


def draw(card: Image.Image, style) -> None:
    w, h = card.size
    rng = rng_for(card, seed=13)
    layer, d = overlay_for(card)

    scatter_stars(d, rng, w, int(h * 0.6), count=max(18, (w * h) // 45000), color=(230, 220, 255), max_alpha=100)

    # big glowing moon top-right
    moon_size = max(70, min(w, h) // 5)
    moon = Image.new("RGBA", (moon_size, moon_size), (0, 0, 0, 0))
    ImageDraw.Draw(moon).ellipse([(0, 0), (moon_size - 1, moon_size - 1)], fill=(*MOON, 235))
    mx, my = w - moon_size - int(w * 0.06), int(h * 0.07)
    glow_paste(layer, moon, mx, my, blur=moon_size / 6)

    # bats flying across the moon and sky
    for fx, fy, s, ang in [(0.62, 0.10, 0.8, 8), (0.72, 0.22, 1.0, -6), (0.48, 0.16, 0.6, 14), (0.30, 0.08, 0.5, -12)]:
        bat = _bat(max(16, int(min(w, h) * 0.07 * s)), ang)
        layer.alpha_composite(bat, (int(w * fx), int(h * fy)))

    # spiderweb top-left corner
    layer.alpha_composite(_web(max(60, min(w, h) // 5)), (0, 0))

    # pumpkins bottom-right, raised clear of the attribution line
    p_size = max(40, min(w, h) // 9)
    lift = h - p_size - style.corner_radius - int(min(w, h) * 0.075)
    px = w - style.corner_radius - p_size - 8
    layer.alpha_composite(_pumpkin(p_size), (px, lift))
    layer.alpha_composite(
        _pumpkin(int(p_size * 0.7)), (px - int(p_size * 0.8), lift + int(p_size * 0.3))
    )

    composite(card, layer)
