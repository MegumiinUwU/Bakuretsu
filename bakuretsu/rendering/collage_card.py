"""Top List / Year in Review collage renderer.

A ranked grid of covers. Each cell shows the cover with a rank badge
(gold / silver / bronze for the top three), a color-coded score chip,
and the item's title underneath. The grid automatically picks the
column count that gives the biggest covers for the card's aspect ratio.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Optional, Union

from PIL import Image, ImageDraw

from bakuretsu.models import CollageData
from bakuretsu.rendering.base import BaseCardRenderer
from bakuretsu.utils import text as textutil
from bakuretsu.utils.colors import score_color

RANK_COLORS = {
    1: (245, 197, 66),   # gold
    2: (184, 192, 204),  # silver
    3: (205, 127, 50),   # bronze
}
COVER_RATIO = 1.45  # cover height / width


class CollageCardRenderer(BaseCardRenderer):
    # ---------- grid math ----------

    def _best_grid(
        self, n: int, grid_w: int, grid_h: int, gap: int, label_h: int
    ) -> tuple[int, int, int]:
        """Pick (cols, cell_w, cell_h) maximizing cover size that fits."""
        best = (1, 0, 0)
        for cols in range(1, min(n, 5) + 1):
            rows = math.ceil(n / cols)
            by_width = (grid_w - gap * (cols - 1)) / cols
            by_height = ((grid_h - gap * (rows - 1)) / rows - label_h) / COVER_RATIO
            cell_w = int(min(by_width, by_height))
            if cell_w > best[1]:
                best = (cols, cell_w, int(cell_w * COVER_RATIO) + label_h)
        return best

    # ---------- cell pieces ----------

    def _rank_badge(self, draw: ImageDraw.ImageDraw, x: int, y: int, r: int, rank: int) -> None:
        color = RANK_COLORS.get(rank)
        if color:
            fill, text_color = (*color, 245), (20, 16, 8)
        else:
            fill, text_color = (12, 14, 28, 235), (255, 255, 255)
        draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=fill,
                     outline=(*self.style.accent_color, 200) if not color else None, width=2)
        font = self.fonts.sized(int(r * 1.15), bold=True)
        draw.text((x, y), str(rank), font=font, fill=text_color, anchor="mm")

    def _score_chip(self, draw: ImageDraw.ImageDraw, right: int, bottom: int, height: int, score: float) -> None:
        text = f"{score:g}"
        font = self.fonts.sized(int(height * 0.62), bold=True)
        text_w = textutil.measure(text, font)
        pad = height // 3
        # never narrower than a circle, otherwise the corner radius exceeds
        # half the width and Pillow draws a line artifact through the pill
        pill_w = max(text_w + pad * 2, height)
        left = right - pill_w
        top = bottom - height
        draw.rounded_rectangle(
            [(left, top), (right, bottom)],
            radius=min(pill_w, height) // 2,
            fill=(*score_color(score), 235),
        )
        draw.text(((left + right) // 2, (top + bottom) // 2), text,
                  font=font, fill=(255, 255, 255), anchor="mm")

    # ---------- render ----------

    def render(
        self,
        data: CollageData,
        output_path: Optional[Union[str, Path]] = None,
    ) -> Image.Image:
        data.validate()
        card, draw = self.new_canvas()
        style = self.style
        w, h = style.width, style.height
        pad = style.padding
        attribution_h = self.attribution_height(data.platform)

        # header: main title + optional subtitle, centered
        y = pad
        title_lh = style.scaled(style.base_title_size) + 6
        title_lines = textutil.wrap(data.title, self.fonts.title, w - pad * 2)
        y = self.draw_lines(
            draw, title_lines, pad, y, w - pad * 2,
            self.fonts.title, style.primary_color, title_lh, max_lines=2, center=True,
        )
        if data.subtitle.strip():
            sub_font = self.fonts.sized(style.scaled(style.base_platform_size + 4))
            sub_lines = textutil.wrap(data.subtitle, sub_font, w - pad * 2)
            y = self.draw_lines(
                draw, sub_lines, pad, y + style.scaled(4), w - pad * 2,
                sub_font, style.secondary_color, style.scaled(style.base_platform_size + 10),
                max_lines=1, center=True,
            )
        # accent divider under the header
        y += style.scaled(10)
        divider_half = min(w // 6, 160)
        draw.line([(w // 2 - divider_half, y), (w // 2 + divider_half, y)],
                  fill=(*style.accent_color, 170), width=3)
        y += style.scaled(16)

        # grid area
        n = len(data.entries)
        gap = max(14, style.scaled(18))
        label_font = self.fonts.sized(max(13, style.scaled(15)))
        label_h = int(max(13, style.scaled(15)) * 1.9)
        grid_w = w - pad * 2
        grid_h = h - y - attribution_h - pad
        cols, cell_w, cell_h = self._best_grid(n, grid_w, grid_h, gap, label_h)
        if cell_w < 40:
            raise ValueError("Card too small for this many items, pick a bigger size")
        cover_h = int(cell_w * COVER_RATIO)
        rows = math.ceil(n / cols)

        total_grid_h = rows * cell_h + gap * (rows - 1)
        grid_top = y + max(0, (grid_h - total_grid_h) // 2)

        badge_r = max(13, cell_w // 7)
        chip_h = max(20, cell_w // 5)

        for index, entry in enumerate(data.entries):
            row, col = divmod(index, cols)
            in_row = min(cols, n - row * cols)  # center a short last row
            row_w = in_row * cell_w + (in_row - 1) * gap
            x0 = pad + (grid_w - row_w) // 2 + col * (cell_w + gap)
            y0 = grid_top + row * (cell_h + gap)

            self.paste_cover(card, draw, entry.cover_image, x0, y0, cell_w, cover_h,
                             radius=max(8, cell_w // 16))
            self._rank_badge(draw, x0 + badge_r // 2 + 4, y0 + badge_r // 2 + 4, badge_r, index + 1)
            self._score_chip(draw, x0 + cell_w - 6, y0 + cover_h - 6, chip_h, entry.score)

            # item title, one ellipsized line under the cover
            lines = textutil.wrap(entry.title, label_font, cell_w)
            if lines:
                line = lines[0]
                if len(lines) > 1:
                    line = textutil.ellipsize(line, label_font, cell_w)
                draw.text(
                    (x0 + cell_w // 2, y0 + cover_h + label_h // 2),
                    line.display, font=label_font,
                    fill=style.secondary_color, anchor="mm",
                )

        self.draw_attribution(
            card, draw, data.platform, data.platform_username, data.attribution_style,
            h - pad - style.scaled(30), align="center",
        )

        if output_path:
            self.save(card, output_path)
        return card
