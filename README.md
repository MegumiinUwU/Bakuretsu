# Bakuretsu

A personal toolkit for managing and enhancing my game, movie, and anime reviews.

> **Note:** This project is currently in demo/development stage. It's a collection of tools I use during my reviews process. More details about each tool will be added soon as development progresses.

---

## Tools

### 1. Review Card Generator

Generate beautiful, branded review card images instantly for your games, movies, and anime. Perfect for sharing on social media alongside your Letterboxd or Backloggd reviews.

<img src="Readme%20images/1.gif" alt="Bakuretsu Review Card Generator UI Demo - showing the interface with title input, score slider, review text area, platform selection, and live card preview" width="700">

#### Features

- **Three Generator Modes** — Review Card, Star Review (Textless), and Score Card
- **Star Ratings** — Half-star precision (0.5–5.0) with filled, half, and empty star rendering
- **Score Cards** — Minimal cover + score layout with glow borders, corner brackets & dot-grid accents
- **Platform Branding** — Add your Backloggd or Letterboxd username with platform logo (Rest of sites soon)
- **Cover Images** — Load covers from URLs or upload local files
- **Score Color Coding** — Automatic color based on score (green for high, red for low)
- **Themed Palettes** — Seasonal/themed styles like Ramadan with pixel-art decorations
- **Customizable Dimensions** — Adjust card size and corner radius
- **Modern UI** — Clean, dark-themed interface with live preview and mode selector

#### Generator Modes

The tool includes three generator modes, selectable from the UI:

##### Review Card

The original full review card — title, cover, numeric score, review text, and platform branding. Landscape format (1200×675 default).

<img src="Readme%20images/reviewcard.png" alt="Multiple review card examples showing different color palette styles - Bakuretsu Dark, Midnight Blue, Ocean, and more" width="650">

##### Star Review Card (Textless Review)

A visual-only card with a star rating instead of text. Shows the title, cover image, and a ★ rating (0.5–5.0 in half-star steps). Square format (1080×1080 default). Great for quick ratings on social media.

<img src="Readme%20images/Planet_of_Lana_textless_review.png" alt="example" width="650">

##### Score Card

A minimal, stylized card focused on the score. Features the cover image framed with an accent-colored glow border, decorative corner brackets, a large numeric score out of 10, and platform branding. Square format (1080×1080 default).

<img src="Readme%20images/Planet_of_Lana_score_card.png" alt="example" width="650">

#### Style Palettes

Choose from 9 built-in color palettes or create your own custom colors:

| Palette | Vibe |
|---------|------|
| **Bakuretsu Dark** | Default dark theme with pink accent |
| **Midnight Blue** | Deep navy with cyan highlights |
| **Deep Purple** | Rich purple aesthetic |
| **Ocean** | Cool blues with sky accents |
| **Forest** | Dark greens, nature-inspired |
| **Sunset** | Warm oranges and reds |
| **Monochrome** | Clean black and white |
| **Retrowave** | Synthwave purple and cyan |
| **Ramadan** | Deep navy with gold accents, pixel-art crescent moon, stars & mosque silhouette |

or any custom colors/dimensions

<img src="Readme%20images/Styles.png" alt="Multiple review card examples showing different color palette styles - Bakuretsu Dark, Midnight Blue, Ocean, and more" width="650">

#### Example

Here's a review card generated for **OMORI**:

<img src="Readme%20images/Omori.png" alt="Example review card for OMORI game showing cover art, 9.0 score, review text, and Backloggd branding" width="550">

#### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the UI
python ui_app.py
```

Or use it programmatically:

```python
from review_card_generator import create_review_card, create_textless_review_card, create_score_card

# Full review card
card = create_review_card(
    title="OMORI",
    score=9.0,
    review_text="A hauntingly beautiful RPG that explores themes of grief and friendship...",
    content_type="game",
    platform="backloggd",
    platform_username="YourUsername",
    output_path="output/omori_review.png"
)

# Star review card (textless)
star_card = create_textless_review_card(
    title="OMORI",
    stars=4.5,
    content_type="game",
    cover_image="https://example.com/omori-cover.jpg",
    platform="backloggd",
    platform_username="YourUsername",
    output_path="output/omori_star_review.png"
)

# Score card
score_card = create_score_card(
    title="OMORI",
    score=9.0,
    content_type="game",
    cover_image="https://example.com/omori-cover.jpg",
    platform="backloggd",
    platform_username="YourUsername",
    output_path="output/omori_score_card.png"
)
```

---

## Coming Soon

More tools are in development to complete the review workflow:

- **The "Cross-Platform" Text Formatter**   Format your reviews for multiple platforms at once
- **The "Can I Beat It?" Calculator**   Estimate completion time based on your gaming habits
- **The "Deal Sniper"**  Track prices and find the best deals for your wishlist
- *...and more*

---

## License

See [LICENSE](LICENSE) for details.
