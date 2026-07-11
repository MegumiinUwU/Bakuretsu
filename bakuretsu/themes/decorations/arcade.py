"""Arcade decoration: pixel invaders, hearts, coins and CRT scanlines."""

from __future__ import annotations

from PIL import Image, ImageDraw

from bakuretsu.themes.decorations.common import (
    bitmap_size,
    blit_bitmap,
    composite,
    overlay_for,
    rng_for,
)

INVADER_A = [
    "..#.....#..",
    "...#...#...",
    "..#######..",
    ".##.###.##.",
    "###########",
    "#.#######.#",
    "#.#.....#.#",
    "...##.##...",
]
INVADER_B = [
    "...##..##...",
    "..########..",
    ".##.####.##.",
    "############",
    ".#........#.",
    "..#..##..#..",
    ".#..#..#..#.",
]
HEART = [
    ".##..##.",
    "########",
    "########",
    ".######.",
    "..####..",
    "...##...",
]
COIN = [
    "..####..",
    ".#....#.",
    "#..##..#",
    "#..#...#",
    "#..##..#",
    ".#....#.",
    "..####..",
]


def draw(card: Image.Image, style) -> None:
    w, h = card.size
    rng = rng_for(card, seed=99)
    layer, d = overlay_for(card)

    accent = style.accent_color
    secondary = style.secondary_color

    px = max(3, min(w, h) // 140)

    # marching invader rows near the top
    inv_w, _ = bitmap_size(INVADER_A, px)
    gap = inv_w // 2
    x = style.corner_radius + gap
    row_y = int(h * 0.04)
    i = 0
    while x + inv_w < w - style.corner_radius:
        bitmap = INVADER_A if i % 2 == 0 else INVADER_B
        alpha = 70 if i % 2 == 0 else 55
        blit_bitmap(d, bitmap, x, row_y + (0 if i % 2 == 0 else px * 2), px, (*accent, alpha))
        x += inv_w + gap
        i += 1

    # a lone bigger invader bottom-right
    big_px = px * 2
    inv2_w, inv2_h = bitmap_size(INVADER_B, big_px)
    blit_bitmap(
        d, INVADER_B,
        w - inv2_w - style.corner_radius - big_px * 2,
        h - inv2_h - style.corner_radius - big_px * 2,
        big_px, (*accent, 90),
    )

    # hearts (lives) bottom-left
    heart_px = max(2, px)
    hw, _ = bitmap_size(HEART, heart_px)
    for i in range(3):
        alpha = 110 if i < 2 else 40  # last life fading
        blit_bitmap(
            d, HEART,
            style.corner_radius + 8 + i * (hw + heart_px * 2),
            h - style.corner_radius - heart_px * 8 - int(min(w, h) * 0.075),
            heart_px, (239, 68, 68, alpha),
        )

    # scattered coins
    for _ in range(5):
        cx = rng.randint(style.corner_radius, w - style.corner_radius - px * 8)
        cy = rng.randint(int(h * 0.15), int(h * 0.85))
        blit_bitmap(d, COIN, cx, cy, max(2, px - 1), (250, 204, 21, rng.randint(35, 70)))

    # CRT scanlines, very subtle
    for y in range(0, h, 4):
        d.line([(0, y), (w, y)], fill=(0, 0, 0, 26), width=1)

    composite(card, layer)
