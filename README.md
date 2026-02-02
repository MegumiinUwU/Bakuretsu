# Bakuretsu

A personal toolkit for managing and enhancing my game, movie, and anime reviews.

> **Note:** This project is currently in demo/development stage. It's a collection of tools I use during my reviews process. More details about each tool will be added soon as development progresses.

---

## Tools

### 1. Review Card Generator

Generate beautiful, branded review card images instantly for your games, movies, and anime. Perfect for sharing on social media alongside your Letterboxd or Backloggd reviews.

![Demo](Readme%20images/1.gif)

#### Features

- **Instant Generation** — Type the title, score, and review to generate a branded image
- **Platform Branding** — Add your Backloggd or Letterboxd username with platform logo (Rest of sites soon)
- **Cover Images** — Load covers from URLs or upload local files
- **Score Color Coding** — Automatic color based on score (green for high, red for low)
- **Customizable Dimensions** — Adjust card size and corner radius
- **Modern UI** — Clean, dark-themed interface with live preview

#### Style Palettes

Choose from 8 built-in color palettes or create your own custom colors:

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

or any custom colors/dimensions

![Styles](Readme%20images/Styles.png)

#### Example

Here's a review card generated for **OMORI**:

![Omori Example](Readme%20images/Omori.png)

#### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the UI
python ui_app.py
```

Or use it programmatically:

```python
from review_card_generator import create_review_card

card = create_review_card(
    title="OMORI",
    score=9.0,
    review_text="A hauntingly beautiful RPG that explores themes of grief and friendship...",
    content_type="game",
    platform="backloggd",
    platform_username="YourUsername",
    output_path="output/omori_review.png"
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
