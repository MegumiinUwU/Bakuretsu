"""Full review card renderer.

Layout adapts to the card's aspect ratio:
- landscape: cover on the left, title/score/review on the right
- square & portrait (Instagram, stories): cover on top, text below
"""

from __future__ import annotations

from typing import Optional, Union
from pathlib import Path

from PIL import Image

from bakuretsu.models import CardStyle, ReviewData
from bakuretsu.rendering.base import BaseCardRenderer
from bakuretsu.utils import text as textutil
from bakuretsu.utils.colors import format_score, score_color


class ReviewCardRenderer(BaseCardRenderer):
    def render(
        self,
        data: ReviewData,
        output_path: Optional[Union[str, Path]] = None,
    ) -> Image.Image:
        data.validate()
        card, draw = self.new_canvas()

        if self.style.is_landscape:
            self._render_landscape(card, draw, data)
        else:
            self._render_portrait(card, draw, data)

        if output_path:
            self.save(card, output_path)
        return card

    # ---------- landscape: cover left, text right ----------

    def _render_landscape(self, card, draw, data: ReviewData) -> None:
        style = self.style
        pad = style.padding
        attribution_h = self.attribution_height(data.platform)

        cover_w = int(style.width * 0.25)
        cover_h = min(int(cover_w * 1.5), style.height - pad * 2 - attribution_h)
        self.paste_cover(card, draw, data.cover_image, pad, pad, cover_w, cover_h)

        text_x = pad + cover_w + pad
        text_w = style.width - text_x - pad

        # title (max 2 lines)
        title_lh = style.scaled(style.base_title_size) + 6
        title_lines = textutil.wrap(data.title, self.fonts.title, text_w)
        y = self.draw_lines(
            draw, title_lines, text_x, pad, text_w,
            self.fonts.title, style.primary_color, title_lh, max_lines=2,
        )

        # score
        y += style.scaled(12)
        draw.text(
            (text_x if not title_lines or not title_lines[0].rtl else text_x + text_w,
             y),
            format_score(data.score),
            font=self.fonts.score,
            fill=score_color(data.score),
            anchor="la" if not title_lines or not title_lines[0].rtl else "ra",
        )
        y += style.scaled(style.base_score_size) + style.scaled(20)

        # review text, as many lines as fit
        review_lh = style.scaled(style.base_review_size) + style.scaled(8)
        available = style.height - pad - attribution_h - y
        max_lines = max(1, available // review_lh)
        review_lines = textutil.wrap(data.review_text, self.fonts.review, text_w)
        self.draw_lines(
            draw, review_lines, text_x, y, text_w,
            self.fonts.review, style.secondary_color, review_lh, max_lines=max_lines,
        )

        self.draw_attribution(
            card, draw, data.platform, data.platform_username,
            data.attribution_style,
            style.height - pad - style.scaled(30),
            align="left",
        )

    # ---------- portrait / square: cover top, text below ----------

    def _render_portrait(self, card, draw, data: ReviewData) -> None:
        style = self.style
        pad = style.padding
        attribution_h = self.attribution_height(data.platform)
        center_x = style.width // 2
        text_w = style.width - pad * 2

        # title first, centered
        title_lh = style.scaled(style.base_title_size) + 6
        title_lines = textutil.wrap(data.title, self.fonts.title, text_w)
        y = self.draw_lines(
            draw, title_lines, pad, pad, text_w,
            self.fonts.title, style.primary_color, title_lh, max_lines=2, center=True,
        )
        y += style.scaled(14)

        # cover centered, sized to leave room for score + a few review lines
        review_lh = style.scaled(style.base_review_size) + style.scaled(8)
        reserved_below = (
            style.scaled(style.base_score_size) + style.scaled(40)
            + review_lh * 4 + attribution_h + pad
        )
        cover_h = max(120, style.height - y - reserved_below)
        cover_w = min(int(cover_h / 1.4), text_w)
        cover_h = int(cover_w * 1.4)
        self.paste_cover(
            card, draw, data.cover_image,
            center_x - cover_w // 2, y, cover_w, cover_h,
        )
        y += cover_h + style.scaled(20)

        # score centered
        draw.text(
            (center_x, y),
            format_score(data.score),
            font=self.fonts.score,
            fill=score_color(data.score),
            anchor="ma",
        )
        y += style.scaled(style.base_score_size) + style.scaled(20)

        # review text fills the rest
        available = style.height - pad - attribution_h - y
        max_lines = max(1, available // review_lh)
        review_lines = textutil.wrap(data.review_text, self.fonts.review, text_w)
        self.draw_lines(
            draw, review_lines, pad, y, text_w,
            self.fonts.review, style.secondary_color, review_lh,
            max_lines=max_lines, center=True,
        )

        self.draw_attribution(
            card, draw, data.platform, data.platform_username,
            data.attribution_style,
            style.height - pad - style.scaled(30),
            align="center",
        )
