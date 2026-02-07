"""
Bakuretsu Review Card Generator
Generates branded review card images for games and movies.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union
import requests
from io import BytesIO
import textwrap
import os


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
        review_font_size: int = 24,
        platform_font_size: int = 20,
        font_path: Optional[str] = None,
        bold_font_path: Optional[str] = None,
        padding: int = 40,
        cover_width: int = 300,
        corner_radius: int = 20,
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
        
        # Load fonts
        self._load_fonts()
    
    def _load_fonts(self):
        """Load fonts with fallback to default."""
        try:
            if self.font_path and Path(self.font_path).exists():
                self.title_font = ImageFont.truetype(self.font_path, self.title_font_size)
                self.score_font = ImageFont.truetype(self.bold_font_path or self.font_path, self.score_font_size)
                self.review_font = ImageFont.truetype(self.font_path, self.review_font_size)
                self.platform_font = ImageFont.truetype(self.font_path, self.platform_font_size)
            else:
                # Try common system fonts
                system_fonts = [
                    "arial.ttf", "Arial.ttf",
                    "segoeui.ttf", "Segoe UI.ttf",
                    "Helvetica.ttf", "DejaVuSans.ttf",
                    "C:/Windows/Fonts/segoeui.ttf",
                    "C:/Windows/Fonts/arial.ttf",
                ]
                font_loaded = False
                for font_name in system_fonts:
                    try:
                        self.title_font = ImageFont.truetype(font_name, self.title_font_size)
                        self.score_font = ImageFont.truetype(font_name, self.score_font_size)
                        self.review_font = ImageFont.truetype(font_name, self.review_font_size)
                        self.platform_font = ImageFont.truetype(font_name, self.platform_font_size)
                        font_loaded = True
                        break
                    except (OSError, IOError):
                        continue
                
                if not font_loaded:
                    # Use default bitmap font as last resort
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
