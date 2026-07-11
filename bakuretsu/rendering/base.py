"""Shared canvas/drawing machinery for all card renderers."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from PIL import Image, ImageDraw

from bakuretsu.models import CardStyle, CoverSource
from bakuretsu.platforms import get_platform
from bakuretsu.themes import get_theme
from bakuretsu.utils import text as textutil
from bakuretsu.utils.fonts import FontSet
from bakuretsu.utils.images import cover_fit, load_image


class BaseCardRenderer:
    """Common behavior: canvas, theme decoration, cover, attribution, save."""

    def __init__(self, style: Optional[CardStyle] = None) -> None:
        self.style = style or CardStyle()
        self.fonts = FontSet(self.style)

    # ---------- canvas ----------

    def new_canvas(self) -> tuple[Image.Image, ImageDraw.ImageDraw]:
        """Rounded-rectangle card base with theme decorations applied."""
        style = self.style
        card = Image.new("RGBA", (style.width, style.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(card)
        draw.rounded_rectangle(
            [(0, 0), (style.width - 1, style.height - 1)],
            radius=style.corner_radius,
            fill=style.background_color,
        )
        if style.theme:
            theme = get_theme(style.theme)
            if theme and theme.decorator:
                theme.decorator(card, style)
                self._clip_corners(card)
                draw = ImageDraw.Draw(card)
        return card, draw

    def _clip_corners(self, card: Image.Image) -> None:
        """Re-apply the rounded-corner mask after decorations drew over it."""
        mask = Image.new("L", card.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [(0, 0), (card.width - 1, card.height - 1)],
            radius=self.style.corner_radius,
            fill=255,
        )
        card.putalpha(mask)

    # ---------- cover ----------

    def paste_cover(
        self,
        card: Image.Image,
        draw: ImageDraw.ImageDraw,
        source: Optional[CoverSource],
        x: int,
        y: int,
        width: int,
        height: int,
        radius: int = 15,
    ) -> None:
        """Paste the cover image, or a labeled placeholder when unavailable."""
        if source:
            try:
                cover = cover_fit(load_image(source), width, height, radius)
                card.alpha_composite(cover, (x, y))
                return
            except Exception:
                pass  # fall through to placeholder
        draw.rounded_rectangle(
            [(x, y), (x + width, y + height)], radius=radius, fill=(40, 40, 50, 255)
        )
        draw.text(
            (x + width // 2, y + height // 2),
            "No Cover",
            font=self.fonts.review,
            fill=self.style.secondary_color,
            anchor="mm",
        )

    # ---------- platform attribution ----------

    def attribution_height(self, platform_key: str) -> int:
        return self.style.scaled(34) if get_platform(platform_key) else 0

    def draw_attribution(
        self,
        card: Image.Image,
        draw: ImageDraw.ImageDraw,
        platform_key: str,
        username: str,
        attribution_style: str,
        y: int,
        align: str = "left",
    ) -> None:
        """Platform logo + credit line at height y.

        align: 'left', 'center' or 'right' within the padded card width.
        """
        platform = get_platform(platform_key)
        if platform is None:
            return

        style = self.style
        logo_size = style.scaled(30)
        gap = max(6, logo_size // 3)
        credit = platform.attribution_text(username, attribution_style)
        credit_display = textutil.shape(credit)
        text_w = textutil.measure(credit_display, self.fonts.platform)
        total_w = logo_size + gap + text_w

        if align == "center":
            x = (style.width - total_w) // 2
        elif align == "right":
            x = style.width - style.padding - total_w
        else:
            x = style.padding

        text_fill = style.secondary_color
        theme = get_theme(style.theme) if style.theme else None
        if theme and theme.attribution_pill:
            pad_x = max(10, logo_size // 2)
            pad_y = max(5, logo_size // 5)
            pill_h = logo_size + pad_y * 2
            draw.rounded_rectangle(
                [(x - pad_x, y - pad_y), (x + total_w + pad_x, y - pad_y + pill_h)],
                radius=pill_h // 2,
                fill=(8, 10, 22, 200),
            )
            text_fill = (255, 255, 255)

        logo = platform.logo(logo_size)
        card.alpha_composite(logo, (x, y))
        draw.text(
            (x + logo_size + gap, y + logo_size // 2),
            credit_display,
            font=self.fonts.platform,
            fill=text_fill,
            anchor="lm",
        )

    # ---------- text ----------

    def draw_lines(
        self,
        draw: ImageDraw.ImageDraw,
        lines: list[textutil.Line],
        x: int,
        y: int,
        block_width: int,
        font,
        fill,
        line_height: int,
        max_lines: Optional[int] = None,
        center: bool = False,
    ) -> int:
        """Draw wrapped lines; RTL lines right-align inside the block.

        Returns the y coordinate below the last drawn line.
        """
        shown = lines if max_lines is None else lines[:max_lines]
        truncated = max_lines is not None and len(lines) > max_lines
        for i, line in enumerate(shown):
            if truncated and i == len(shown) - 1:
                line = textutil.ellipsize(line, font, block_width)
            if center:
                lx = x + (block_width - line.width) // 2
            elif line.rtl:
                lx = x + block_width - line.width
            else:
                lx = x
            draw.text((lx, y), line.display, font=font, fill=fill)
            y += line_height
        return y

    # ---------- output ----------

    @staticmethod
    def save(card: Image.Image, output_path: Union[str, Path]) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() in (".jpg", ".jpeg"):
            card.convert("RGB").save(path, quality=95)
        else:
            card.save(path, "PNG")
        return path
