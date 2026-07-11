"""Loading and preparing cover images."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Union

import requests
from PIL import Image, ImageDraw

from bakuretsu.models import CoverSource

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def load_image(source: CoverSource) -> Image.Image:
    """Load an image from a URL, file path, or pass through a PIL Image."""
    if isinstance(source, Image.Image):
        return source.convert("RGBA")

    source_str = str(source)
    if source_str.startswith(("http://", "https://")):
        try:
            response = requests.get(source_str, headers={"User-Agent": _UA}, timeout=15)
            response.raise_for_status()
            return Image.open(BytesIO(response.content)).convert("RGBA")
        except requests.RequestException as exc:
            raise ValueError(f"Failed to load image from URL: {exc}") from exc

    path = Path(source_str)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")
    return Image.open(path).convert("RGBA")


def cover_fit(
    image: Image.Image,
    width: int,
    height: int,
    radius: int = 0,
) -> Image.Image:
    """Scale-and-crop an image to exactly width x height, rounded corners optional."""
    src_ratio = image.width / image.height
    dst_ratio = width / height

    if src_ratio > dst_ratio:
        new_h = height
        new_w = int(new_h * src_ratio)
    else:
        new_w = width
        new_h = int(new_w / src_ratio)

    image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - width) // 2
    top = (new_h - height) // 2
    image = image.crop((left, top, left + width, top + height))

    if radius > 0:
        mask = Image.new("L", (width, height), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [(0, 0), (width - 1, height - 1)], radius=radius, fill=255
        )
        image.putalpha(mask)
    return image
