"""Textless star-review card: title, cover, star rating."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Optional, Union

from PIL import Image, ImageChops, ImageDraw

from bakuretsu.models import StarReviewData
from bakuretsu.rendering.base import BaseCardRenderer
from bakuretsu.utils import text as textutil


class StarCardRenderer(BaseCardRenderer):
    MAX_STARS = 5

    # ---------- star drawing ----------

    @staticmethod
    def _star_points(cx: float, cy: float, outer_r: float) -> list[tuple[float, float]]:
        inner_r = outer_r * 0.42
        points = []
        for i in range(10):
            angle = math.radians(-90 + i * 36)
            r = outer_r if i % 2 == 0 else inner_r
            points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        return points

    def _star_image(self, outer_r: int, color: tuple, half_of: Optional[tuple] = None) -> Image.Image:
        """Anti-aliased star; if half_of is given, left half uses `color`
        over an empty star of color `half_of`."""
        os = 4
        big = int(outer_r * 2.4) * os
        img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        points = self._star_points(big / 2, big / 2, outer_r * os)

        if half_of is None:
            d.polygon(points, fill=color)
        else:
            d.polygon(points, fill=half_of)  # empty base
            filled = Image.new("RGBA", (big, big), (0, 0, 0, 0))
            fd = ImageDraw.Draw(filled)
            fd.polygon(points, fill=color)
            _, _, _, alpha = filled.split()
            mask = Image.new("L", (big, big), 0)
            ImageDraw.Draw(mask).rectangle([(0, 0), (big // 2, big)], fill=255)
            filled.putalpha(ImageChops.multiply(alpha, mask))
            img.alpha_composite(filled)

        small = big // os
        return img.resize((small, small), Image.Resampling.LANCZOS)

    def _draw_rating(self, card: Image.Image, stars: float, center_x: int, center_y: int, outer_r: int) -> None:
        fill = (*self.style.accent_color, 255)
        empty = (*self.style.secondary_color, 70)

        spacing = int(outer_r * 2.7)
        start_x = center_x - ((self.MAX_STARS - 1) * spacing) // 2
        full = int(stars)
        has_half = (stars - full) >= 0.25

        for i in range(self.MAX_STARS):
            if i < full:
                img = self._star_image(outer_r, fill)
            elif i == full and has_half:
                img = self._star_image(outer_r, fill, half_of=empty)
            else:
                img = self._star_image(outer_r, empty)
            card.alpha_composite(
                img,
                (start_x + i * spacing - img.width // 2, center_y - img.height // 2),
            )

    # ---------- render ----------

    def render(
        self,
        data: StarReviewData,
        output_path: Optional[Union[str, Path]] = None,
    ) -> Image.Image:
        data.validate()
        card, draw = self.new_canvas()
        style = self.style
        pad = style.padding
        center_x = style.width // 2
        attribution_h = self.attribution_height(data.platform)
        text_w = style.width - pad * 2

        # measure the stack: title + cover + stars, vertically centered
        title_lh = style.scaled(style.base_title_size) + 8
        title_lines = textutil.wrap(data.title, self.fonts.title, text_w)
        title_h = min(2, len(title_lines)) * title_lh

        star_r = max(15, int(min(style.width, style.height) * 0.03))
        star_area = int(star_r * 2.6)
        gap = style.scaled(22)

        usable_h = style.height - pad * 2 - attribution_h
        cover_h = usable_h - title_h - star_area - gap * 2
        cover_w = min(int(cover_h / 1.4), text_w)
        cover_h = int(cover_w * 1.4)

        total_h = title_h + gap + cover_h + gap + star_area
        y = pad + max(0, (usable_h - total_h) // 2)

        y = self.draw_lines(
            draw, title_lines, pad, y, text_w,
            self.fonts.title, style.primary_color, title_lh, max_lines=2, center=True,
        )
        y += gap

        self.paste_cover(
            card, draw, data.cover_image,
            center_x - cover_w // 2, y, cover_w, cover_h,
        )
        y += cover_h + gap

        self._draw_rating(card, data.stars, center_x, y + star_area // 2, star_r)

        self.draw_attribution(
            card, draw, data.platform, data.platform_username,
            data.attribution_style,
            style.height - pad - style.scaled(30),
            align="center",
        )

        if output_path:
            self.save(card, output_path)
        return card
