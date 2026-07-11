"""Ramadan decoration: smooth golden crescent, hanging lanterns,
starfield and a proper mosque skyline (domes + minarets)."""

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

GOLD = (255, 215, 0)
WARM = (255, 190, 90)


def _crescent(size: int) -> Image.Image:
    """Anti-aliased crescent via oversampled circle subtraction."""
    os = 4
    big = size * os
    body = Image.new("L", (big, big), 0)
    d = ImageDraw.Draw(body)
    d.ellipse([(0, 0), (big - 1, big - 1)], fill=255)
    # subtract an offset circle to carve the crescent
    cut = Image.new("L", (big, big), 0)
    dc = ImageDraw.Draw(cut)
    off = int(big * 0.28)
    dc.ellipse([(off, -int(big * 0.10)), (big + off, big - int(big * 0.10))], fill=255)
    from PIL import ImageChops

    mask = ImageChops.subtract(body, cut)
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    img.paste(Image.new("RGBA", (big, big), (*GOLD, 235)), mask=mask)
    return img.resize((size, size), Image.Resampling.LANCZOS)


def _lantern(height: int) -> Image.Image:
    """A little fanous: dome cap, glass body with warm core, base."""
    w = int(height * 0.62)
    img = Image.new("RGBA", (w, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = w // 2
    dome_h = int(height * 0.22)
    body_top = dome_h
    body_bottom = int(height * 0.82)

    # dome cap + hook
    d.line([(cx, 0), (cx, int(height * 0.06))], fill=(*GOLD, 220), width=2)
    d.pieslice([(int(w * 0.12), 0), (int(w * 0.88), dome_h * 2)], 180, 360, fill=(*GOLD, 230))
    # glass body
    d.rounded_rectangle(
        [(int(w * 0.06), body_top), (int(w * 0.94), body_bottom)],
        radius=max(2, w // 6),
        fill=(*WARM, 120),
        outline=(*GOLD, 230),
        width=2,
    )
    # warm glowing core
    d.ellipse(
        [(int(w * 0.30), int(height * 0.38)), (int(w * 0.70), int(height * 0.66))],
        fill=(255, 235, 150, 200),
    )
    # base + tassel
    d.rectangle([(int(w * 0.22), body_bottom), (int(w * 0.78), int(height * 0.88))], fill=(*GOLD, 230))
    d.line([(cx, int(height * 0.88)), (cx, height - 1)], fill=(*GOLD, 200), width=2)
    return img


def _mosque_skyline(width: int, height: int) -> Image.Image:
    """Silhouette strip: central dome, side domes, two minarets."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    sil = (6, 8, 24, 215)
    base_y = height  # everything sits on the bottom edge
    wall_h = int(height * 0.30)

    # base wall
    d.rectangle([(0, base_y - wall_h), (width, base_y)], fill=sil)

    def dome(cx: int, r: int, stem_h: int) -> None:
        top = base_y - wall_h - stem_h
        d.rectangle([(cx - r, top), (cx + r, base_y)], fill=sil)
        d.pieslice([(cx - r, top - r * 2), (cx + r, top)], 180, 360, fill=sil)
        # finial
        d.line([(cx, top - r * 2), (cx, top - r * 2 - r)], fill=sil, width=max(2, r // 6))
        fr = max(2, r // 8)
        fy = top - r * 2 - r
        d.ellipse([(cx - fr, fy - fr), (cx + fr, fy + fr)], fill=sil)

    def minaret(cx: int, h: int, w: int) -> None:
        top = base_y - h
        d.rectangle([(cx - w, top), (cx + w, base_y)], fill=sil)
        # balcony
        d.rectangle([(cx - int(w * 1.8), top + int(h * 0.18)), (cx + int(w * 1.8), top + int(h * 0.22))], fill=sil)
        # pointed cap
        d.polygon([(cx - int(w * 1.6), top), (cx + int(w * 1.6), top), (cx, top - int(h * 0.22))], fill=sil)

    dome(width // 2, int(height * 0.26), int(height * 0.12))
    dome(int(width * 0.30), int(height * 0.16), int(height * 0.04))
    dome(int(width * 0.70), int(height * 0.16), int(height * 0.04))
    minaret(int(width * 0.12), int(height * 0.78), max(4, int(height * 0.045)))
    minaret(int(width * 0.88), int(height * 0.78), max(4, int(height * 0.045)))
    return img


def draw(card: Image.Image, style) -> None:
    w, h = card.size
    rng = rng_for(card, seed=42)
    layer, d = overlay_for(card)

    scatter_stars(d, rng, w, int(h * 0.7), count=max(30, (w * h) // 26000), color=(220, 225, 255))

    # crescent with glow, top-right
    size = max(60, min(w, h) // 6)
    crescent = _crescent(size)
    cx = w - size - int(w * 0.05)
    cy = int(h * 0.06)
    glow_paste(layer, crescent, cx, cy, blur=size / 7)

    # hanging lanterns, top-left, staggered heights
    lantern_h = max(36, min(w, h) // 10)
    for i, (fx, drop) in enumerate([(0.06, 0.02), (0.145, 0.09), (0.23, 0.04)]):
        lx = int(w * fx)
        ly = int(h * drop)
        d.line([(lx + lantern_h * 0.31, 0), (lx + lantern_h * 0.31, ly)], fill=(*GOLD, 150), width=2)
        lantern = _lantern(lantern_h if i != 1 else int(lantern_h * 1.25))
        layer.alpha_composite(lantern, (lx, ly))

    # mosque skyline hugging the bottom, inset past the rounded corners
    inset = style.corner_radius + 4
    sky_h = max(50, int(h * 0.16))
    skyline = _mosque_skyline(w - inset * 2, sky_h)
    layer.alpha_composite(skyline, (inset, h - sky_h))

    composite(card, layer)
