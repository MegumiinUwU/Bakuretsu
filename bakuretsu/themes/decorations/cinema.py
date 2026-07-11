"""Cinema decoration: film strips along the top and bottom edges,
a spotlight sweep and small star sparkles."""

from __future__ import annotations

from PIL import Image, ImageDraw

from bakuretsu.themes.decorations.common import composite, overlay_for, rng_for, scatter_stars

FILM = (8, 7, 6)
HOLE = (250, 245, 235)


def _film_strip(width: int, height: int) -> Image.Image:
    """Horizontal film strip: dark band, sprocket holes, frame separators."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([(0, 0), (width, height)], fill=(*FILM, 210))

    hole_h = max(4, height // 6)
    hole_w = int(hole_h * 1.4)
    step = hole_w * 2
    margin = hole_h
    for x in range(margin, width - hole_w, step):
        for y in (margin, height - margin - hole_h):
            d.rounded_rectangle(
                [(x, y), (x + hole_w, y + hole_h)],
                radius=max(1, hole_h // 3),
                fill=(*HOLE, 150),
            )
    # frame separators across the middle band
    frame_w = height * 2
    top = margin * 2 + hole_h
    bottom = height - margin * 2 - hole_h
    for x in range(0, width, frame_w):
        d.line([(x, top), (x, bottom)], fill=(*HOLE, 60), width=2)
    return img


def draw(card: Image.Image, style) -> None:
    w, h = card.size
    rng = rng_for(card, seed=55)
    layer, d = overlay_for(card)

    strip_h = max(30, h // 12)
    strip = _film_strip(w, strip_h)
    layer.alpha_composite(strip, (0, 0))
    layer.alpha_composite(strip, (0, h - strip_h))

    # spotlight beams from the bottom corners
    beam = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    accent = style.accent_color
    bd.polygon([(0, h), (int(w * 0.35), 0), (int(w * 0.55), 0)], fill=(*accent, 16))
    bd.polygon([(w, h), (int(w * 0.45), 0), (int(w * 0.65), 0)], fill=(*accent, 16))
    layer.alpha_composite(beam)

    scatter_stars(d, rng, w, h, count=max(12, (w * h) // 70000), color=accent, max_alpha=90)

    composite(card, layer)
