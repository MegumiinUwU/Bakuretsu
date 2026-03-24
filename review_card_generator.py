"""
Bakuretsu Review Card Generator
Generates branded review card images for games and movies.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union
import requests
from io import BytesIO
import textwrap
import os
import math
import random


class Platform(Enum):
    """Supported review platforms."""
    NONE = "none"
    BACKLOGGD = "backloggd"
    LETTERBOXD = "letterboxd"


class ContentType(Enum):
    """Type of content being reviewed."""
    GAME = "game"
    MOVIE = "movie"


@dataclass
class PlatformBranding:
    """Platform-specific branding configuration."""
    name: str
    logo_path: Optional[str]
    accent_color: tuple[int, int, int]
    username: str = ""
    
    @classmethod
    def backloggd(cls, username: str, logo_path: Optional[str] = None) -> "PlatformBranding":
        """Create Backloggd branding configuration."""
        return cls(
            name="Backloggd",
            logo_path=logo_path or "assets/logos/backloggd_logo.png",
            accent_color=(139, 92, 246),  # Purple
            username=username
        )
    
    @classmethod
    def letterboxd(cls, username: str, logo_path: Optional[str] = None) -> "PlatformBranding":
        """Create Letterboxd branding configuration."""
        return cls(
            name="Letterboxd",
            logo_path=logo_path or "assets/logos/letterboxd_logo.png",
            accent_color=(255, 128, 0),  # Orange
            username=username
        )


@dataclass
class ReviewData:
    """Data container for a review."""
    title: str
    score: float
    review_text: str
    content_type: ContentType
    cover_image: Optional[Union[str, Path, Image.Image]] = None
    platform: Platform = Platform.NONE
    platform_username: str = ""
    
    def validate(self) -> bool:
        """Validate review data."""
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not 0 <= self.score <= 10:
            raise ValueError("Score must be between 0 and 10")
        if not self.review_text or not self.review_text.strip():
            raise ValueError("Review text cannot be empty")
        return True


@dataclass
class TextlessReviewData:
    """Data container for a textless (visual-only) review with star rating."""
    title: str
    stars: float
    content_type: ContentType
    cover_image: Optional[Union[str, Path, Image.Image]] = None
    platform: Platform = Platform.NONE
    platform_username: str = ""

    def validate(self) -> bool:
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not 0.5 <= self.stars <= 5.0:
            raise ValueError("Stars must be between 0.5 and 5")
        return True


@dataclass
class ScoreCardData:
    """Data container for a minimal score card (cover + score + platform handle)."""
    title: str
    score: float
    content_type: ContentType
    cover_image: Optional[Union[str, Path, Image.Image]] = None
    platform: Platform = Platform.NONE
    platform_username: str = ""

    def validate(self) -> bool:
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not 0 <= self.score <= 10:
            raise ValueError("Score must be between 0 and 10")
        return True


class ImageLoader:
    """Handles loading images from various sources."""
    
    @staticmethod
    def load_from_url(url: str) -> Image.Image:
        """Load an image from a URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return Image.open(BytesIO(response.content)).convert("RGBA")
        except requests.RequestException as e:
            raise ValueError(f"Failed to load image from URL: {e}")
    
    @staticmethod
    def load_from_file(path: Union[str, Path]) -> Image.Image:
        """Load an image from a file path."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {path}")
        return Image.open(path).convert("RGBA")
    
    @classmethod
    def load(cls, source: Union[str, Path, Image.Image]) -> Image.Image:
        """Load an image from URL, file path, or return if already an Image."""
        if isinstance(source, Image.Image):
            return source.convert("RGBA")
        
        source_str = str(source)
        if source_str.startswith(('http://', 'https://')):
            return cls.load_from_url(source_str)
        else:
            return cls.load_from_file(source)


class CardStyle:
    """Configuration for card visual style."""
    
    def __init__(
        self,
        width: int = 1200,
        height: int = 675,
        background_color: tuple[int, int, int, int] = (18, 18, 24, 255),
        primary_color: tuple[int, int, int] = (255, 255, 255),
        secondary_color: tuple[int, int, int] = (156, 163, 175),
        accent_color: tuple[int, int, int] = (236, 72, 153),
        title_font_size: int = 48,
        score_font_size: int = 72,
        review_font_size: int = 28,
        platform_font_size: int = 20,
        font_path: Optional[str] = None,
        bold_font_path: Optional[str] = None,
        padding: int = 40,
        cover_width: int = 300,
        corner_radius: int = 20,
        theme: Optional[str] = None,
    ):
        self.width = width
        self.height = height
        self.background_color = background_color
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.accent_color = accent_color
        self.title_font_size = title_font_size
        self.score_font_size = score_font_size
        self.review_font_size = review_font_size
        self.platform_font_size = platform_font_size
        self.font_path = font_path
        self.bold_font_path = bold_font_path
        self.padding = padding
        self.cover_width = cover_width
        self.corner_radius = corner_radius
        self.theme = theme
        
        # Load fonts
        self._load_fonts()
    
    def _load_fonts(self):
        """Load fonts with fallback to default."""
        def _try_load(paths, size):
            for p in paths:
                try:
                    return ImageFont.truetype(p, size)
                except (OSError, IOError):
                    continue
            return None

        system_fonts = [
            "arial.ttf", "Arial.ttf",
            "segoeui.ttf", "Segoe UI.ttf",
            "Helvetica.ttf", "DejaVuSans.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
        system_bold_fonts = [
            "arialbd.ttf",
            "segoeuib.ttf",
            "Helvetica-Bold.ttf", "DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ]

        try:
            if self.font_path and Path(self.font_path).exists():
                bold = self.bold_font_path or self.font_path
                self.title_font = ImageFont.truetype(self.font_path, self.title_font_size)
                self.score_font = ImageFont.truetype(bold, self.score_font_size)
                self.review_font = ImageFont.truetype(bold, self.review_font_size)
                self.platform_font = ImageFont.truetype(self.font_path, self.platform_font_size)
            else:
                regular = _try_load(system_fonts, self.title_font_size)
                if regular:
                    self.title_font = regular
                    self.score_font = _try_load(system_bold_fonts, self.score_font_size) or \
                                      _try_load(system_fonts, self.score_font_size) or ImageFont.load_default()
                    self.review_font = _try_load(system_bold_fonts, self.review_font_size) or \
                                       _try_load(system_fonts, self.review_font_size) or ImageFont.load_default()
                    self.platform_font = _try_load(system_fonts, self.platform_font_size) or ImageFont.load_default()
                else:
                    self.title_font = ImageFont.load_default()
                    self.score_font = ImageFont.load_default()
                    self.review_font = ImageFont.load_default()
                    self.platform_font = ImageFont.load_default()
        except Exception:
            self.title_font = ImageFont.load_default()
            self.score_font = ImageFont.load_default()
            self.review_font = ImageFont.load_default()
            self.platform_font = ImageFont.load_default()


class ReviewCardGenerator:
    """Main class for generating review card images."""
    
    def __init__(self, style: Optional[CardStyle] = None):
        """Initialize the generator with optional custom style."""
        self.style = style or CardStyle()
        self.branding_logo_path: Optional[str] = None
    
    def set_branding_logo(self, logo_path: str):
        """Set the Bakuretsu branding logo path."""
        self.branding_logo_path = logo_path
    
    def _create_rounded_rectangle(
        self, 
        size: tuple[int, int], 
        radius: int, 
        fill: tuple[int, int, int, int]
    ) -> Image.Image:
        """Create a rounded rectangle image."""
        rect = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(rect)
        draw.rounded_rectangle(
            [(0, 0), (size[0] - 1, size[1] - 1)],
            radius=radius,
            fill=fill
        )
        return rect
    
    def _create_cover_with_rounded_corners(
        self, 
        cover: Image.Image, 
        target_width: int,
        target_height: int,
        radius: int
    ) -> Image.Image:
        """Resize cover and apply rounded corners."""
        # Resize maintaining aspect ratio and crop to fill
        cover_ratio = cover.width / cover.height
        target_ratio = target_width / target_height
        
        if cover_ratio > target_ratio:
            new_height = target_height
            new_width = int(new_height * cover_ratio)
        else:
            new_width = target_width
            new_height = int(new_width / cover_ratio)
        
        cover = cover.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Center crop
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        cover = cover.crop((left, top, left + target_width, top + target_height))
        
        # Apply rounded corners mask
        mask = Image.new('L', (target_width, target_height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(
            [(0, 0), (target_width - 1, target_height - 1)],
            radius=radius,
            fill=255
        )
        
        result = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))
        result.paste(cover, (0, 0))
        result.putalpha(mask)
        
        return result
    
    def _format_score(self, score: float) -> str:
        """Format the score for display."""
        if score == int(score):
            return f"{int(score)}/10"
        return f"{score:.1f}/10"
    
    def _get_score_color(self, score: float) -> tuple[int, int, int]:
        """Get color based on score value."""
        if score >= 8:
            return (34, 197, 94)   # Green
        elif score >= 6:
            return (234, 179, 8)   # Yellow
        elif score >= 4:
            return (249, 115, 22)  # Orange
        else:
            return (239, 68, 68)   # Red
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            if bbox[2] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _draw_platform_branding(
        self, 
        draw: ImageDraw.Draw, 
        image: Image.Image,
        platform: Platform,
        username: str,
        position: tuple[int, int]
    ):
        """Draw platform logo and username."""
        if platform == Platform.NONE:
            return
        
        branding = None
        if platform == Platform.BACKLOGGD:
            branding = PlatformBranding.backloggd(username)
        elif platform == Platform.LETTERBOXD:
            branding = PlatformBranding.letterboxd(username)
        
        if not branding:
            return
        
        x, y = position
        logo_size = 32
        
        # Try to load platform logo
        try:
            if branding.logo_path and Path(branding.logo_path).exists():
                logo = Image.open(branding.logo_path).convert("RGBA")
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                image.paste(logo, (x, y), logo)
                x += logo_size + 10
        except Exception:
            # Draw a colored circle as fallback
            draw.ellipse(
                [(x, y), (x + logo_size, y + logo_size)],
                fill=branding.accent_color
            )
            x += logo_size + 10
        
        # Draw platform name and username
        platform_text = f"{branding.name}"
        if username:
            platform_text += f" @{username}"
        
        draw.text(
            (x, y + logo_size // 2),
            platform_text,
            font=self.style.platform_font,
            fill=self.style.secondary_color,
            anchor="lm"
        )
    
    def _draw_ramadan_decorations(self, card: Image.Image, draw: ImageDraw.Draw):
        """Draw pixel-art Ramadan decorations: stars, crescent moon, mosque silhouette."""
        w, h = card.size
        rng = random.Random(42)
        px = max(3, min(w, h) // 160)
        gw, gh = w // px, h // px

        overlay = Image.new("RGBA", card.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)

        def block(gx, gy, color):
            if 0 <= gx < gw and 0 <= gy < gh:
                x0, y0 = gx * px, gy * px
                od.rectangle([(x0, y0), (x0 + px - 1, y0 + px - 1)], fill=color)

        # ---- Pixel stars ----
        for _ in range(max(25, gw * gh // 300)):
            sx, sy = rng.randint(0, gw - 1), rng.randint(0, gh - 1)
            b = rng.randint(80, 160)
            block(sx, sy, (b, b, min(255, b + 30), rng.randint(50, 110)))

        # ---- Pixel crescent moon (top-right) ----
        mr = max(5, min(gw, gh) // 14)
        mcx, mcy = gw - 4 - mr, 3 + mr
        cut_dx = int(mr * 0.5)
        cut_dy = int(-mr * 0.2)
        cut_r = mr * 0.78

        gold = (255, 215, 0, 220)
        gold_glow = (255, 215, 0, 50)

        for dy in range(-mr - 2, mr + 3):
            for dx in range(-mr - 2, mr + 3):
                d = (dx * dx + dy * dy) ** 0.5
                cd = ((dx - cut_dx) ** 2 + (dy - cut_dy) ** 2) ** 0.5
                if d <= mr and cd > cut_r:
                    block(mcx + dx, mcy + dy, gold)
                elif mr < d <= mr + 1.5 and cd > cut_r:
                    block(mcx + dx, mcy + dy, gold_glow)

        # Accent stars near the crescent
        for offset_x, offset_y in [(-mr - 3, -2), (-mr - 2, mr - 1),
                                    (2, -mr - 2), (mr, mr - 2)]:
            block(mcx + offset_x, mcy + offset_y, (255, 230, 100, 180))

        # ---- Mosque silhouette along bottom ----
        sil = (8, 10, 28, 200)
        sil_edge = (18, 22, 48, 200)
        corner_margin = max(3, self.style.corner_radius // px + 1)

        base_h = 3
        profile = [base_h] * gw

        dome_specs = [
            (gw // 6, max(3, gw // 22)),
            (gw // 2, max(4, gw // 16)),
            (gw * 5 // 6, max(3, gw // 20)),
        ]
        for dc, dr in dome_specs:
            for dx in range(-dr, dr + 1):
                gx = dc + dx
                if 0 <= gx < gw:
                    dh = base_h + int((dr ** 2 - dx ** 2) ** 0.5)
                    profile[gx] = max(profile[gx], dh)

        min_h = base_h + max(5, gw // 18)
        for mx in [gw // 4, gw * 3 // 4]:
            for off in (-1, 0, 1):
                if 0 <= mx + off < gw:
                    profile[mx + off] = max(profile[mx + off], min_h)
            if 0 <= mx < gw:
                profile[mx] = max(profile[mx], min_h + 2)

        for gx in range(gw):
            if gx < corner_margin or gx >= gw - corner_margin:
                continue
            for gy_off in range(profile[gx]):
                gy = gh - 1 - gy_off
                if gy >= 0:
                    c = sil_edge if gy_off == profile[gx] - 1 else sil
                    block(gx, gy, c)

        card.alpha_composite(overlay)

    def generate(
        self, 
        review: ReviewData,
        output_path: Optional[Union[str, Path]] = None
    ) -> Image.Image:
        """
        Generate a review card image.
        
        Args:
            review: ReviewData object containing all review information
            output_path: Optional path to save the generated image
            
        Returns:
            PIL Image object of the generated card
        """
        # Validate review data
        review.validate()
        
        # Create base card with rounded corners
        card = self._create_rounded_rectangle(
            (self.style.width, self.style.height),
            self.style.corner_radius,
            self.style.background_color
        )
        draw = ImageDraw.Draw(card)
        
        # Apply theme decorations
        if self.style.theme == "ramadan":
            self._draw_ramadan_decorations(card, draw)
            draw = ImageDraw.Draw(card)
        
        # Calculate layout
        padding = self.style.padding
        cover_width = self.style.cover_width
        cover_height = int(cover_width * 1.5)  # Standard poster ratio
        cover_x = padding
        cover_y = padding
        
        # Text area calculations
        text_x = cover_x + cover_width + padding
        text_width = self.style.width - text_x - padding
        
        # Draw cover image if provided
        if review.cover_image:
            try:
                cover = ImageLoader.load(review.cover_image)
                cover_rounded = self._create_cover_with_rounded_corners(
                    cover, cover_width, cover_height, 15
                )
                card.paste(cover_rounded, (cover_x, cover_y), cover_rounded)
            except Exception as e:
                # Draw placeholder
                placeholder_color = (40, 40, 50, 255)
                draw.rounded_rectangle(
                    [(cover_x, cover_y), (cover_x + cover_width, cover_y + cover_height)],
                    radius=15,
                    fill=placeholder_color
                )
                draw.text(
                    (cover_x + cover_width // 2, cover_y + cover_height // 2),
                    "No Cover",
                    font=self.style.review_font,
                    fill=self.style.secondary_color,
                    anchor="mm"
                )
        else:
            # Draw placeholder
            placeholder_color = (40, 40, 50, 255)
            draw.rounded_rectangle(
                [(cover_x, cover_y), (cover_x + cover_width, cover_y + cover_height)],
                radius=15,
                fill=placeholder_color
            )
            draw.text(
                (cover_x + cover_width // 2, cover_y + cover_height // 2),
                "No Cover",
                font=self.style.review_font,
                fill=self.style.secondary_color,
                anchor="mm"
            )
        
        # Draw title
        title_y = padding
        title_lines = self._wrap_text(review.title, self.style.title_font, text_width)
        for line in title_lines[:2]:  # Max 2 lines for title
            draw.text(
                (text_x, title_y),
                line,
                font=self.style.title_font,
                fill=self.style.primary_color
            )
            title_y += self.style.title_font_size + 5
        
        # Draw score
        score_y = title_y + 15
        score_text = self._format_score(review.score)
        score_color = self._get_score_color(review.score)
        draw.text(
            (text_x, score_y),
            score_text,
            font=self.style.score_font,
            fill=score_color
        )
        
        # Draw review text
        review_y = score_y + self.style.score_font_size + 20
        review_lines = self._wrap_text(review.review_text, self.style.review_font, text_width)
        max_review_lines = 8  # Limit review text lines
        for i, line in enumerate(review_lines[:max_review_lines]):
            if i == max_review_lines - 1 and len(review_lines) > max_review_lines:
                line = line[:-3] + "..." if len(line) > 3 else "..."
            draw.text(
                (text_x, review_y),
                line,
                font=self.style.review_font,
                fill=self.style.secondary_color
            )
            review_y += self.style.review_font_size + 8
        
        # Draw platform branding (bottom left)
        if review.platform != Platform.NONE:
            platform_y = self.style.height - padding - 32
            self._draw_platform_branding(
                draw, card, review.platform, 
                review.platform_username, 
                (padding, platform_y)
            )
        
        
        # Save if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            card.save(output_path, "PNG")
        
        return card


class TextlessReviewCardGenerator:
    """Generator for textless review card images with star ratings."""

    def __init__(self, style: Optional[CardStyle] = None):
        self.style = style or CardStyle(width=1080, height=1080)
        self._base = ReviewCardGenerator(self.style)

    @staticmethod
    def _star_polygon(
        cx: float, cy: float, outer_r: float, inner_r: float = None
    ) -> list[tuple[float, float]]:
        """Calculate vertices of a 5-pointed star."""
        if inner_r is None:
            inner_r = outer_r * 0.38
        points = []
        for i in range(10):
            angle = math.radians(-90 + i * 36)
            r = outer_r if i % 2 == 0 else inner_r
            points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        return points

    def _create_star_image(
        self, img_size: int, outer_r: float, color: tuple
    ) -> Image.Image:
        """Create a single filled star image."""
        img = Image.new("RGBA", (img_size, img_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cx, cy = img_size // 2, img_size // 2
        points = self._star_polygon(cx, cy, outer_r)
        draw.polygon(points, fill=color)
        return img

    def _create_half_star_image(
        self, img_size: int, outer_r: float, fill_color: tuple, empty_color: tuple
    ) -> Image.Image:
        """Create a half-filled star (left half filled, right half empty)."""
        cx, cy = img_size // 2, img_size // 2
        points = self._star_polygon(cx, cy, outer_r)

        base = Image.new("RGBA", (img_size, img_size), (0, 0, 0, 0))
        base_draw = ImageDraw.Draw(base)
        base_draw.polygon(points, fill=empty_color)

        filled = Image.new("RGBA", (img_size, img_size), (0, 0, 0, 0))
        filled_draw = ImageDraw.Draw(filled)
        filled_draw.polygon(points, fill=fill_color)

        _, _, _, alpha = filled.split()
        mask = Image.new("L", (img_size, img_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rectangle([(0, 0), (cx, img_size)], fill=255)
        filled.putalpha(ImageChops.multiply(alpha, mask))

        base.alpha_composite(filled)
        return base

    def _draw_star_rating(
        self,
        card: Image.Image,
        stars: float,
        max_stars: int,
        center_x: int,
        center_y: int,
        star_outer_r: int,
    ):
        """Draw a star rating centered at the given position."""
        fill_color = (*self.style.accent_color, 255)
        empty_color = (*self.style.secondary_color, 60)

        img_size = int(star_outer_r * 2.5)
        spacing = int(star_outer_r * 2.8)
        total_width = (max_stars - 1) * spacing
        start_x = center_x - total_width // 2

        full_stars = int(stars)
        has_half = (stars - full_stars) >= 0.25

        for i in range(max_stars):
            sx = start_x + i * spacing
            paste_x = sx - img_size // 2
            paste_y = center_y - img_size // 2

            if i < full_stars:
                star_img = self._create_star_image(img_size, star_outer_r, fill_color)
            elif i == full_stars and has_half:
                star_img = self._create_half_star_image(
                    img_size, star_outer_r, fill_color, empty_color
                )
            else:
                star_img = self._create_star_image(img_size, star_outer_r, empty_color)

            card.alpha_composite(star_img, (paste_x, paste_y))

    def _draw_cover_placeholder(
        self, draw: ImageDraw.Draw, x: int, y: int, w: int, h: int, center_x: int
    ):
        """Draw a placeholder rectangle when no cover image is available."""
        draw.rounded_rectangle(
            [(x, y), (x + w, y + h)], radius=15, fill=(40, 40, 50, 255)
        )
        draw.text(
            (center_x, y + h // 2),
            "No Cover",
            font=self.style.review_font,
            fill=self.style.secondary_color,
            anchor="mm",
        )

    def generate(
        self,
        review: TextlessReviewData,
        output_path: Optional[Union[str, Path]] = None,
    ) -> Image.Image:
        """Generate a textless review card image with star rating."""
        review.validate()

        card = self._base._create_rounded_rectangle(
            (self.style.width, self.style.height),
            self.style.corner_radius,
            self.style.background_color,
        )
        draw = ImageDraw.Draw(card)

        if self.style.theme == "ramadan":
            self._base._draw_ramadan_decorations(card, draw)
            draw = ImageDraw.Draw(card)

        padding = self.style.padding
        center_x = self.style.width // 2
        card_min = min(self.style.width, self.style.height)

        cover_w = int(card_min * 0.48)
        cover_h = int(cover_w * 1.4)

        star_outer_r = max(15, int(card_min * 0.028))
        star_area_h = int(star_outer_r * 2.5)

        title_lines = self._base._wrap_text(
            review.title, self.style.title_font, self.style.width - padding * 2
        )
        title_line_count = min(2, len(title_lines))
        line_spacing = self.style.title_font_size + 8
        title_h = title_line_count * line_spacing

        gap = int(card_min * 0.025)
        total_h = title_h + gap + cover_h + gap + star_area_h
        start_y = max(padding, (self.style.height - total_h) // 2)

        title_y = start_y
        for line in title_lines[:2]:
            draw.text(
                (center_x, title_y),
                line,
                font=self.style.title_font,
                fill=self.style.primary_color,
                anchor="mt",
            )
            title_y += line_spacing

        cover_y = start_y + title_h + gap
        cover_x = center_x - cover_w // 2

        if review.cover_image:
            try:
                cover = ImageLoader.load(review.cover_image)
                cover_rounded = self._base._create_cover_with_rounded_corners(
                    cover, cover_w, cover_h, 15
                )
                card.paste(cover_rounded, (cover_x, cover_y), cover_rounded)
            except Exception:
                self._draw_cover_placeholder(
                    draw, cover_x, cover_y, cover_w, cover_h, center_x
                )
        else:
            self._draw_cover_placeholder(
                draw, cover_x, cover_y, cover_w, cover_h, center_x
            )

        stars_y = cover_y + cover_h + gap + star_area_h // 2
        self._draw_star_rating(card, review.stars, 5, center_x, stars_y, star_outer_r)

        if review.platform != Platform.NONE:
            platform_y = self.style.height - padding - 32
            self._base._draw_platform_branding(
                draw, card, review.platform, review.platform_username, (padding, platform_y)
            )

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            card.save(output_path, "PNG")

        return card


class ScoreCardGenerator:
    """Generator for square score cards: cover image + score + platform handle."""

    def __init__(self, style: Optional[CardStyle] = None):
        self.style = style or CardStyle(width=1080, height=1080)
        self._base = ReviewCardGenerator(self.style)

    def _get_score_color(self, score: float) -> tuple[int, int, int]:
        if score >= 8:
            return (34, 197, 94)
        elif score >= 6:
            return (234, 179, 8)
        elif score >= 4:
            return (249, 115, 22)
        else:
            return (239, 68, 68)

    def _format_score(self, score: float) -> str:
        if score == int(score):
            return str(int(score))
        return f"{score:.1f}"

    def _draw_corner_brackets(
        self, draw: ImageDraw.Draw, x: int, y: int, w: int, h: int,
        color: tuple, length: int, thickness: int,
    ):
        """Draw L-shaped accent brackets at the four corners of a rectangle."""
        corners = [
            (x, y, 1, 1),
            (x + w, y, -1, 1),
            (x, y + h, 1, -1),
            (x + w, y + h, -1, -1),
        ]
        for cx, cy, dx, dy in corners:
            draw.line([(cx, cy), (cx + dx * length, cy)], fill=color, width=thickness)
            draw.line([(cx, cy), (cx, cy + dy * length)], fill=color, width=thickness)

    def _draw_border_glow(
        self, card: Image.Image, x: int, y: int, w: int, h: int,
        radius: int, color: tuple, layers: int = 4,
    ):
        """Draw a soft glow around a rounded rectangle by stacking blurred outlines."""
        for i in range(layers, 0, -1):
            glow = Image.new("RGBA", card.size, (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow)
            expand = i * 3
            alpha = max(10, 55 - i * 12)
            gd.rounded_rectangle(
                [(x - expand, y - expand), (x + w + expand, y + h + expand)],
                radius=radius + expand,
                outline=(*color, alpha),
                width=2,
            )
            glow = glow.filter(ImageFilter.GaussianBlur(radius=i * 2))
            card.alpha_composite(glow)

    def _draw_dot_grid(
        self, draw: ImageDraw.Draw, x0: int, y0: int, x1: int, y1: int,
        spacing: int, color: tuple,
    ):
        """Draw a subtle decorative dot grid pattern in the given region."""
        for gx in range(x0, x1, spacing):
            for gy in range(y0, y1, spacing):
                draw.ellipse([(gx, gy), (gx + 2, gy + 2)], fill=color)

    def generate(
        self,
        review: ScoreCardData,
        output_path: Optional[Union[str, Path]] = None,
    ) -> Image.Image:
        review.validate()

        w, h = self.style.width, self.style.height
        card = self._base._create_rounded_rectangle(
            (w, h), self.style.corner_radius, self.style.background_color,
        )
        draw = ImageDraw.Draw(card)

        if self.style.theme == "ramadan":
            self._base._draw_ramadan_decorations(card, draw)
            draw = ImageDraw.Draw(card)

        padding = self.style.padding
        center_x = w // 2
        card_min = min(w, h)
        accent = self.style.accent_color

        # --- Background dot grid in top-left and bottom-right quadrants ---
        dot_alpha = 25
        dot_color = (*accent, dot_alpha)
        dot_spacing = max(18, card_min // 50)
        self._draw_dot_grid(
            draw, padding, padding,
            padding + card_min // 4, padding + card_min // 4,
            dot_spacing, dot_color,
        )
        self._draw_dot_grid(
            draw, w - padding - card_min // 4, h - padding - card_min // 4,
            w - padding, h - padding,
            dot_spacing, dot_color,
        )

        # --- Thin accent lines in the top-right and bottom-left corners ---
        line_len = card_min // 6
        line_color = (*accent, 40)
        draw.line([(w - padding, padding), (w - padding - line_len, padding)], fill=line_color, width=1)
        draw.line([(w - padding, padding), (w - padding, padding + line_len)], fill=line_color, width=1)
        draw.line([(padding, h - padding), (padding + line_len, h - padding)], fill=line_color, width=1)
        draw.line([(padding, h - padding), (padding, h - padding - line_len)], fill=line_color, width=1)

        # --- Layout calculations ---
        border_thickness = max(3, card_min // 270)
        border_pad = border_thickness + max(4, card_min // 160)
        cover_w = int(card_min * 0.62)
        cover_h = cover_w
        frame_w = cover_w + border_pad * 2
        frame_h = cover_h + border_pad * 2

        score_num_size = max(56, int(card_min * 0.085))
        score_denom_size = max(32, int(card_min * 0.045))
        try:
            bold_path = self.style.bold_font_path or "C:/Windows/Fonts/segoeuib.ttf"
            score_num_font = ImageFont.truetype(bold_path, score_num_size)
            score_denom_font = ImageFont.truetype(bold_path, score_denom_size)
        except (OSError, IOError, AttributeError):
            score_num_font = self.style.score_font
            score_denom_font = self.style.platform_font

        score_text = self._format_score(review.score)
        denom_text = "/10"
        num_bbox = score_num_font.getbbox(score_text)
        denom_bbox = score_denom_font.getbbox(denom_text)
        score_total_w = (num_bbox[2] - num_bbox[0]) + 4 + (denom_bbox[2] - denom_bbox[0])
        score_total_h = num_bbox[3] - num_bbox[1]

        gap = int(card_min * 0.035)
        bracket_margin = max(10, card_min // 70)
        bracket_len = max(20, card_min // 25)
        bracket_thickness = max(2, card_min // 360)
        platform_h = 36 if review.platform != Platform.NONE else 0

        total_h = frame_h + gap + score_total_h
        start_y = max(padding, (h - total_h - platform_h) // 2)

        frame_x = center_x - frame_w // 2
        frame_y = start_y
        cover_x = frame_x + border_pad
        cover_y = frame_y + border_pad

        # --- Glow around border ---
        self._draw_border_glow(card, frame_x, frame_y, frame_w, frame_h, 15, accent, layers=5)
        draw = ImageDraw.Draw(card)

        # --- Border rectangle ---
        draw.rounded_rectangle(
            [(frame_x, frame_y), (frame_x + frame_w, frame_y + frame_h)],
            radius=15,
            outline=(*accent, 200),
            width=border_thickness,
        )

        # --- Cover image ---
        if review.cover_image:
            try:
                cover = ImageLoader.load(review.cover_image)
                cover_rounded = self._base._create_cover_with_rounded_corners(
                    cover, cover_w, cover_h, 12,
                )
                card.paste(cover_rounded, (cover_x, cover_y), cover_rounded)
            except Exception:
                self._draw_placeholder(draw, cover_x, cover_y, cover_w, cover_h, center_x)
        else:
            self._draw_placeholder(draw, cover_x, cover_y, cover_w, cover_h, center_x)

        # --- Corner brackets around the image frame ---
        bx = frame_x - bracket_margin
        by = frame_y - bracket_margin
        bw = frame_w + bracket_margin * 2
        bh = frame_h + bracket_margin * 2
        self._draw_corner_brackets(
            draw, bx, by, bw, bh,
            (*accent, 120), bracket_len, bracket_thickness,
        )

        # --- Score: "X/10" with /10 in smaller dimmer text ---
        score_y = frame_y + frame_h + gap
        score_color = self._get_score_color(review.score)
        score_start_x = center_x - score_total_w // 2

        draw.text(
            (score_start_x, score_y),
            score_text,
            font=score_num_font,
            fill=score_color,
            anchor="lt",
        )

        denom_x = score_start_x + (num_bbox[2] - num_bbox[0]) + 4
        num_baseline = score_y + (num_bbox[3] - num_bbox[1])
        denom_baseline_offset = denom_bbox[3] - denom_bbox[1]
        denom_y = num_baseline - denom_baseline_offset

        draw.text(
            (denom_x, denom_y),
            denom_text,
            font=score_denom_font,
            fill=(*self.style.secondary_color, 180),
            anchor="lt",
        )

        # --- Accent separator line below score ---
        sep_y = score_y + score_total_h + int(gap * 0.6)
        sep_half = card_min // 8
        draw.line(
            [(center_x - sep_half, sep_y), (center_x + sep_half, sep_y)],
            fill=(*accent, 60), width=2,
        )

        # --- Platform branding (bottom-right) ---
        if review.platform != Platform.NONE:
            platform_y = h - padding - 36
            platform_x = w - padding
            branding = None
            if review.platform == Platform.BACKLOGGD:
                branding = PlatformBranding.backloggd(review.platform_username)
            elif review.platform == Platform.LETTERBOXD:
                branding = PlatformBranding.letterboxd(review.platform_username)
            if branding:
                platform_text = branding.name
                if review.platform_username:
                    platform_text += f"  @{review.platform_username}"
                logo_size = 32
                text_bbox = self.style.platform_font.getbbox(platform_text)
                text_w = text_bbox[2] - text_bbox[0]
                total_brand_w = logo_size + 10 + text_w
                brand_x = platform_x - total_brand_w

                try:
                    if branding.logo_path and Path(branding.logo_path).exists():
                        logo = Image.open(branding.logo_path).convert("RGBA")
                        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                        card.paste(logo, (brand_x, platform_y), logo)
                        brand_x += logo_size + 10
                except Exception:
                    draw.ellipse(
                        [(brand_x, platform_y), (brand_x + logo_size, platform_y + logo_size)],
                        fill=branding.accent_color,
                    )
                    brand_x += logo_size + 10

                draw.text(
                    (brand_x, platform_y + logo_size // 2),
                    platform_text,
                    font=self.style.platform_font,
                    fill=self.style.secondary_color,
                    anchor="lm",
                )

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            card.save(output_path, "PNG")

        return card

    def _draw_placeholder(
        self, draw: ImageDraw.Draw, x: int, y: int, w: int, h: int, cx: int,
    ):
        draw.rounded_rectangle(
            [(x, y), (x + w, y + h)], radius=12, fill=(40, 40, 50, 255),
        )
        draw.text(
            (cx, y + h // 2), "No Cover",
            font=self.style.review_font, fill=self.style.secondary_color, anchor="mm",
        )


def create_review_card(
    title: str,
    score: float,
    review_text: str,
    content_type: str = "game",
    cover_image: Optional[str] = None,
    platform: str = "none",
    platform_username: str = "",
    output_path: Optional[str] = None,
    style: Optional[CardStyle] = None
) -> Image.Image:
    """
    Convenience function to create a review card with minimal setup.
    
    Args:
        title: Name of the game or movie
        score: Score out of 10 (0-10, can be decimal like 7.5)
        review_text: The review text content
        content_type: "game" or "movie"
        cover_image: URL or file path to cover image
        platform: "none", "backloggd", or "letterboxd"
        platform_username: Username on the platform
        output_path: Optional path to save the image
        style: Optional CardStyle for customization
        
    Returns:
        PIL Image object of the generated card
    """
    review = ReviewData(
        title=title,
        score=score,
        review_text=review_text,
        content_type=ContentType(content_type.lower()),
        cover_image=cover_image,
        platform=Platform(platform.lower()),
        platform_username=platform_username
    )
    
    generator = ReviewCardGenerator(style)
    return generator.generate(review, output_path)


def create_textless_review_card(
    title: str,
    stars: float,
    content_type: str = "game",
    cover_image: Optional[str] = None,
    platform: str = "none",
    platform_username: str = "",
    output_path: Optional[str] = None,
    style: Optional[CardStyle] = None,
) -> Image.Image:
    """
    Convenience function to create a textless review card with star rating.

    Args:
        title: Name of the game or movie
        stars: Star rating (0.5-5.0 in 0.5 increments)
        content_type: "game" or "movie"
        cover_image: URL or file path to cover image
        platform: "none", "backloggd", or "letterboxd"
        platform_username: Username on the platform
        output_path: Optional path to save the image
        style: Optional CardStyle for customization

    Returns:
        PIL Image object of the generated card
    """
    review = TextlessReviewData(
        title=title,
        stars=stars,
        content_type=ContentType(content_type.lower()),
        cover_image=cover_image,
        platform=Platform(platform.lower()),
        platform_username=platform_username,
    )

    generator = TextlessReviewCardGenerator(style)
    return generator.generate(review, output_path)


def create_score_card(
    title: str,
    score: float,
    content_type: str = "game",
    cover_image: Optional[str] = None,
    platform: str = "none",
    platform_username: str = "",
    output_path: Optional[str] = None,
    style: Optional[CardStyle] = None,
) -> Image.Image:
    """
    Convenience function to create a square score card (cover + score + handle).

    Args:
        title: Name of the game or movie
        score: Score out of 10 (0-10, can be decimal like 7.5)
        content_type: "game" or "movie"
        cover_image: URL or file path to cover image
        platform: "none", "backloggd", or "letterboxd"
        platform_username: Username on the platform
        output_path: Optional path to save the image
        style: Optional CardStyle for customization

    Returns:
        PIL Image object of the generated card
    """
    review = ScoreCardData(
        title=title,
        score=score,
        content_type=ContentType(content_type.lower()),
        cover_image=cover_image,
        platform=Platform(platform.lower()),
        platform_username=platform_username,
    )

    generator = ScoreCardGenerator(style)
    return generator.generate(review, output_path)


# Example usage
if __name__ == "__main__":
    # Example: Create a game review card for Backloggd
    card = create_review_card(
        title="Elden Ring",
        score=9.5,
        review_text="A masterpiece of open-world design. FromSoftware has outdone themselves with this vast, mysterious world filled with challenging encounters and breathtaking vistas. The freedom to explore at your own pace while facing increasingly difficult foes is incredibly satisfying.",
        content_type="game",
        cover_image="https://example.com/elden-ring-cover.jpg",  # Replace with actual URL
        platform="backloggd",
        platform_username="YourUsername",
        output_path="output/elden_ring_review.png"
    )
    print("Review card generated!")
    
    # Example: Create a movie review card for Letterboxd
    movie_card = create_review_card(
        title="Dune: Part Two",
        score=8.5,
        review_text="Denis Villeneuve delivers an epic continuation that expands the scope while maintaining the intimate character moments. The visuals are stunning and Hans Zimmer's score is phenomenal.",
        content_type="movie",
        platform="letterboxd",
        platform_username="YourUsername",
        output_path="output/dune_2_review.png"
    )
    print("Movie review card generated!")
