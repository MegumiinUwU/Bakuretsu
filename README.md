# Bakuretsu

A personal toolkit for managing and enhancing game, movie, and anime reviews.

The flagship tool is the **Review Card Generator** — branded review card
images for sharing on social media alongside your Backloggd, Letterboxd, or
MyAnimeList reviews.

<img src="Readme%20images/1.gif" alt="Bakuretsu Review Card Generator UI Demo" width="700">

---

## Features

- **Three card modes** — Review Card (title + cover + score + text), Star Review (textless ★ rating), and Score Card (framed cover + big score)
- **Social media size presets** — one dropdown for X/Twitter, Instagram square/portrait/story, TikTok, Facebook, Reddit, Discord, YouTube thumbnail, Pinterest, or fully custom dimensions
- **Adaptive layouts** — the review card automatically switches between landscape (cover left) and portrait/story (cover top) composition, and fonts scale with card size
- **Full Arabic support** — review text, titles, and mixed Arabic/English render with correct letterform shaping and RTL alignment (not reversed, not disconnected)
- **Platform branding** — Backloggd, Letterboxd, and MyAnimeList, with your username and a configurable credit line: `@username`, `Follow me on <platform>`, or `Posted on <platform> by @username`
- **App settings** — save your usernames per platform, default theme/size/platform, and credit style once; the app fills them in every time (`⚙ Settings` in the top-left)
- **20 themes** — 12 clean palettes + 8 decorated themes, all extensible
- **Score color coding** — green/yellow/orange/red based on the score
- **Covers from anywhere** — URL or local file, with graceful placeholder

## Themes

**Palettes:** Bakuretsu Dark, Midnight Blue, Deep Purple, Ocean, Forest,
Sunset, Monochrome, Crimson, Gold Luxe, Coffee, Paper Light, Mint Light

**Decorated themes:**

| Theme | Artwork |
|-------|---------|
| **Ramadan** | Golden crescent, hanging lanterns, starfield, mosque skyline |
| **Exams Time** | Chalk formulas, F-graded papers, coffee mug, pencil |
| **Retrowave** | Banded sunset sun, perspective neon grid |
| **Sakura** | Blossom branch, drifting petals |
| **Halloween** | Glowing moon, bats, jack-o'-lanterns, spiderweb |
| **Winter** | Snowflakes, falling snow, layered drifts |
| **Arcade** | Marching pixel invaders, hearts, coins, CRT scanlines |
| **Cinema** | Film strips, spotlight beams |

## Examples

Review card, star review, and score card:

<img src="Readme%20images/Omori.png" alt="Example review card for OMORI game showing cover art, 9.0 score, review text, and Backloggd branding" width="550">

<img src="Readme%20images/Planet_of_Lana_textless_review.png" alt="Star review card example" width="450"> <img src="Readme%20images/Planet_of_Lana_score_card.png" alt="Score card example" width="450">

More palette examples:

<img src="Readme%20images/Styles.png" alt="Multiple review card examples showing different color palette styles" width="650">

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

Or programmatically:

```python
from bakuretsu import create_review_card, create_star_card, create_score_card

create_review_card(
    title="OMORI",
    score=9.0,
    review_text="A hauntingly beautiful RPG...",   # Arabic works too
    cover_image="https://example.com/omori.jpg",
    platform="backloggd",                          # backloggd / letterboxd / myanimelist
    platform_username="YourUsername",
    attribution_style="follow",                    # handle / follow / posted
    theme="Ramadan",
    size="Instagram Square",                       # any preset name, or width=/height=
    output_path="output/omori.png",
)

create_star_card(title="OMORI", stars=4.5, output_path="output/omori_stars.png")
create_score_card(title="OMORI", score=9.0, output_path="output/omori_score.png")
```

## Project Structure

```
main.py                     # UI entry point
bakuretsu/
├── api.py                  # public create_* functions
├── models.py               # data models + CardStyle
├── settings.py             # persistent app settings (settings.json)
├── sizes.py                # social media size presets
├── platforms/              # platform registry + drawn logos
├── themes/
│   ├── palettes.py         # color palettes
│   ├── registry.py         # theme registry (palette + decoration)
│   └── decorations/        # one module per decorated theme
├── rendering/              # base renderer + one module per card mode
├── ui/                     # customtkinter app + settings dialog
└── utils/                  # fonts, colors, images, Arabic text shaping
```

**Adding a palette:** add an entry to `themes/palettes.py` and one line to
`themes/registry.py`. **Adding a decorated theme:** also drop a
`draw(card, style)` module in `themes/decorations/`. **Adding a platform:**
one `PlatformSpec` in `platforms/registry.py` (plus an optional logo drawer
or a PNG in `assets/logos/`). **Adding a size preset:** one line in
`sizes.py`. Everything shows up in the UI automatically.

## Settings

`⚙ Settings` stores to `settings.json` (gitignored):

- Your username per platform — auto-filled whenever you pick that platform
- Credit line style — `@username` only, "Follow me on ...", or "Posted on ... by ..."
- Default platform, theme, card size, and output folder

## Coming Soon

- **The "Cross-Platform" Text Formatter** — format your reviews for multiple platforms at once
- **The "Can I Beat It?" Calculator** — estimate completion time based on your gaming habits
- **The "Deal Sniper"** — track prices and find the best deals for your wishlist
- *...and more*

## License

See [LICENSE](LICENSE) for details.
