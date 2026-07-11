"""Exams Time decoration: chalkboard formulas, F-graded papers,
coffee mug and a pencil. (No more baked-in captions.)"""

from __future__ import annotations

from PIL import Image, ImageDraw

from bakuretsu.themes.decorations.common import composite, overlay_for, rng_for
from bakuretsu.utils.fonts import load_font

CHALK = (232, 228, 212)
RED_PEN = (230, 57, 70)

_FORMULAS = ["E=mc²", "x² + y²", "∑ n!", "sin(θ)", "lim→∞", "∫ f(x)dx", "π≈3.14", "a²+b²=c²", "?!"]


def _paper(size: int, angle: float) -> Image.Image:
    """A ruled exam sheet with a big red F."""
    w, h = size, int(size * 1.3)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([(0, 0), (w - 1, h - 1)], radius=max(2, size // 20), fill=(245, 242, 230, 210))
    # ruled lines
    for ly in range(h // 5, h, h // 6):
        d.line([(int(w * 0.08), ly), (int(w * 0.92), ly)], fill=(120, 140, 200, 120), width=1)
    # big red F, slightly tilted look via offset strokes
    f_font = load_font(int(h * 0.42), bold=True)
    d.text((int(w * 0.30), int(h * 0.16)), "F", font=f_font, fill=(*RED_PEN, 235))
    # red circle around the F
    d.ellipse(
        [(int(w * 0.14), int(h * 0.08)), (int(w * 0.72), int(h * 0.62))],
        outline=(*RED_PEN, 200),
        width=max(2, size // 30),
    )
    return img.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)


def _mug(size: int) -> Image.Image:
    """Coffee mug with steam."""
    img = Image.new("RGBA", (int(size * 1.3), int(size * 1.5)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0, y0 = int(size * 0.05), int(size * 0.5)
    body_w, body_h = size, int(size * 0.8)
    d.rounded_rectangle(
        [(x0, y0), (x0 + body_w, y0 + body_h)], radius=size // 8, fill=(150, 100, 60, 220)
    )
    d.ellipse([(x0 + 4, y0 - size // 12), (x0 + body_w - 4, y0 + size // 8)], fill=(70, 45, 25, 235))
    # handle
    d.arc(
        [(x0 + body_w - size // 8, y0 + size // 8), (x0 + body_w + size // 3, y0 + body_h - size // 8)],
        300, 60 + 360, fill=(150, 100, 60, 220), width=max(3, size // 12),
    )
    # steam curls
    for sx in (x0 + body_w // 3, x0 + 2 * body_w // 3):
        d.arc([(sx - 8, y0 - size // 2), (sx + 8, y0 - size // 6)], 90, 270, fill=(*CHALK, 110), width=2)
        d.arc([(sx - 8, y0 - size * 3 // 4), (sx + 8, y0 - size * 5 // 12)], 270, 90, fill=(*CHALK, 80), width=2)
    return img


def _pencil(length: int, angle: float) -> Image.Image:
    img = Image.new("RGBA", (length, length // 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    h = length // 4
    body_left = h  # room for the tip
    # tip
    d.polygon([(0, h // 2), (body_left, h // 6), (body_left, h * 5 // 6)], fill=(230, 200, 150, 230))
    d.polygon([(0, h // 2), (h // 3, h // 3), (h // 3, h * 2 // 3)], fill=(40, 40, 40, 235))
    # body + eraser
    d.rectangle([(body_left, h // 6), (length - h // 2, h * 5 // 6)], fill=(250, 180, 40, 230))
    d.rectangle([(length - h // 2, h // 6), (length - 1, h * 5 // 6)], fill=(240, 120, 130, 230))
    return img.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)


def draw(card: Image.Image, style) -> None:
    w, h = card.size
    rng = rng_for(card, seed=77)
    layer, d = overlay_for(card)

    # chalk formulas scattered around the edges
    formula_font = load_font(max(16, min(w, h) // 30))
    spots = [
        (0.03, 0.05), (0.75, 0.04), (0.42, 0.03), (0.05, 0.55),
        (0.88, 0.40), (0.68, 0.90), (0.04, 0.90), (0.90, 0.72), (0.35, 0.93),
    ]
    for i, (fx, fy) in enumerate(spots):
        formula = _FORMULAS[i % len(_FORMULAS)]
        alpha = rng.randint(45, 95)
        d.text((int(w * fx), int(h * fy)), formula, font=formula_font, fill=(*CHALK, alpha))

    # F-graded papers tucked in two corners
    paper_size = max(50, min(w, h) // 7)
    layer.alpha_composite(_paper(paper_size, -14), (int(w * 0.80), int(h * 0.62)))
    layer.alpha_composite(_paper(int(paper_size * 0.8), 18), (int(w * 0.02), int(h * 0.12)))

    # coffee mug bottom-center-left (clear of the attribution line), pencil top-right
    mug = _mug(max(30, min(w, h) // 11))
    layer.alpha_composite(mug, (int(w * 0.34), h - mug.height - int(h * 0.05)))
    pencil = _pencil(max(60, min(w, h) // 5), -30)
    layer.alpha_composite(pencil, (int(w * 0.60), int(h * 0.05)))

    composite(card, layer)
