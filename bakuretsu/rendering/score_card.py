"""Minimal score card: glowing framed cover, big score, corner brackets."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from PIL import Image, ImageDraw, ImageFilter

from bakuretsu.models import ScoreCardData
from bakuretsu.rendering.base import BaseCardRenderer
from bakuretsu.utils import text as textutil
from bakuretsu.utils.colors import format_score, score_color


class ScoreCardRenderer(BaseCardRenderer):
    def _corner_brackets(self, draw, x, y, w, h, color, length, thickness) -> None:
        for cx, cy, dx, dy in ((x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
            draw.line([(cx, cy), (cx + dx * length, cy)], fill=color, width=thickness)
            draw.line([(cx, cy), (cx, cy + dy * length)], fill=color, width=thickness)

    def _border_glow(self, card, x, y, w, h, radius, color, layers=5) -> None:
        for i in range(layers, 0, -1):
            glow = Image.new("RGBA", card.size, (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow)
            expand = i * 3
            alpha = max(10, 55 - i * 10)
            gd.rounded_rectangle(
                [(x - expand, y - expand), (x + w + expand, y + h + expand)],
                radius=radius + expand,
                outline=(*color, alpha),
                width=2,
            )
            card.alpha_composite(glow.filter(ImageFilter.GaussianBlur(i * 2)))

    def _dot_grid(self, draw, x0, y0, x1, y1, spacing, color) -> None:
        for gx in range(x0, x1, spacing):
            for gy in range(y0, y1, spacing):
                draw.ellipse([(gx, gy), (gx + 2, gy + 2)], fill=color)

    def render(
        self,
        data: ScoreCardData,
        output_path: Optional[Union[str, Path]] = None,
    ) -> Image.Image:
        data.validate()
        card, draw = self.new_canvas()
        style = self.style
        w, h = style.width, style.height
        pad = style.padding
        center_x = w // 2
        card_min = min(w, h)
        accent = style.accent_color
        attribution_h = self.attribution_height(data.platform)

        # background accents (skip when a decorated theme already fills the card)
        if not style.theme:
            dot_spacing = max(18, card_min // 50)
            self._dot_grid(draw, pad, pad, pad + card_min // 4, pad + card_min // 4, dot_spacing, (*accent, 25))
            self._dot_grid(
                draw, w - pad - card_min // 4, h - pad - card_min // 4, w - pad, h - pad,
                dot_spacing, (*accent, 25),
            )
            line_len = card_min // 6
            for (x0, y0), (x1, y1) in (
                (((w - pad), pad), ((w - pad - line_len), pad)),
                (((w - pad), pad), ((w - pad), pad + line_len)),
                ((pad, h - pad), (pad + line_len, h - pad)),
                ((pad, h - pad), (pad, h - pad - line_len)),
            ):
                draw.line([(x0, y0), (x1, y1)], fill=(*accent, 40), width=1)

        # layout: title, framed cover, score, brackets — vertically centered
        title_lh = style.scaled(style.base_title_size - 6) + 8
        title_font = self.fonts.sized(style.scaled(style.base_title_size - 6), bold=True)
        title_lines = textutil.wrap(data.title, title_font, w - pad * 2)
        title_h = min(2, len(title_lines)) * title_lh

        border_pad = max(7, card_min // 120)
        cover_w = int(card_min * 0.52)
        cover_h = cover_w  # square crop, like the original design
        frame_w = cover_w + border_pad * 2
        frame_h = cover_h + border_pad * 2

        score_size = max(56, int(card_min * 0.085))
        denom_size = max(30, int(score_size * 0.5))
        score_font = self.fonts.sized(score_size, bold=True)
        denom_font = self.fonts.sized(denom_size, bold=True)
        score_h = score_size + style.scaled(8)

        gap = int(card_min * 0.04)
        usable_h = h - pad * 2 - attribution_h
        total_h = title_h + gap + frame_h + gap + score_h
        y = pad + max(0, (usable_h - total_h) // 2)

        # title
        y = self.draw_lines(
            draw, title_lines, pad, y, w - pad * 2,
            title_font, style.primary_color, title_lh, max_lines=2, center=True,
        )
        y += gap

        # glowing frame + cover
        frame_x = center_x - frame_w // 2
        frame_y = y
        self._border_glow(card, frame_x, frame_y, frame_w, frame_h, 15, accent)
        draw = ImageDraw.Draw(card)
        draw.rounded_rectangle(
            [(frame_x, frame_y), (frame_x + frame_w, frame_y + frame_h)],
            radius=15,
            outline=(*accent, 210),
            width=max(3, card_min // 270),
        )
        self.paste_cover(
            card, draw, data.cover_image,
            frame_x + border_pad, frame_y + border_pad, cover_w, cover_h, radius=12,
        )

        # corner brackets around the frame
        margin = max(10, card_min // 70)
        self._corner_brackets(
            draw,
            frame_x - margin, frame_y - margin,
            frame_w + margin * 2, frame_h + margin * 2,
            (*accent, 130),
            length=max(20, card_min // 25),
            thickness=max(2, card_min // 360),
        )
        y = frame_y + frame_h + gap

        # score: number + smaller "/10", baseline-aligned via anchors
        num_text = format_score(data.score, with_denominator=False)
        denom_text = "/10"
        num_w = textutil.measure(num_text, score_font)
        denom_w = textutil.measure(denom_text, denom_font)
        space = max(4, score_size // 16)
        start_x = center_x - (num_w + space + denom_w) // 2
        baseline_y = y + score_size

        draw.text((start_x, baseline_y), num_text, font=score_font, fill=score_color(data.score), anchor="ls")
        draw.text(
            (start_x + num_w + space, baseline_y),
            denom_text,
            font=denom_font,
            fill=(*style.secondary_color, 190),
            anchor="ls",
        )

        # separator line under the score
        sep_y = baseline_y + int(gap * 0.7)
        sep_half = card_min // 8
        draw.line([(center_x - sep_half, sep_y), (center_x + sep_half, sep_y)], fill=(*accent, 70), width=2)

        self.draw_attribution(
            card, draw, data.platform, data.platform_username,
            data.attribution_style,
            h - pad - style.scaled(30),
            align="right",
        )

        if output_path:
            self.save(card, output_path)
        return card
