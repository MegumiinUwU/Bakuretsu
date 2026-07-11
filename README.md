# Bakuretsu

My personal toolkit for the reviews I post on social media. I review games, movies, and anime on places like Backloggd and Letterboxd, and this app turns those reviews into clean, branded card images that are ready to share.

<div align="center">
<img src="Readme%20images/full_app.gif" alt="Bakuretsu full app demo: writing a review, picking a theme, and generating a card" width="850">
</div>

---

## What it does

You type your review, pick a theme and a size, and Bakuretsu renders a polished card image with your cover art, score, and platform username on it. Three card modes are included:

| Mode | What you get |
|------|--------------|
| **Review Card** | Title, cover, numeric score, and your full review text |
| **Star Review** | Textless card with the cover and a star rating (0.5 to 5.0, half stars supported) |
| **Score Card** | Minimal card: glowing framed cover, big score, corner brackets |

Some example cards:

<img src="Readme%20images/Omori.png" alt="Example review card for OMORI" width="550">

<img src="Readme%20images/Planet_of_Lana_textless_review.png" alt="Star review card example" width="420"> <img src="Readme%20images/Planet_of_Lana_score_card.png" alt="Score card example" width="420">

## Themes

20 themes ship with the app: 12 clean color palettes (Bakuretsu Dark, Midnight Blue, Deep Purple, Ocean, Forest, Sunset, Monochrome, Crimson, Gold Luxe, Coffee, Paper Light, Mint Light) plus 8 decorated themes with hand-drawn artwork:

- **Ramadan** golden crescent, hanging lanterns, starfield, mosque skyline
- **Exams Time** chalk formulas, F-graded papers, coffee mug, pencil
- **Retrowave** banded sunset sun and a perspective neon grid
- **Sakura** blossom branch and drifting petals
- **Halloween** glowing moon, bats, jack-o'-lanterns, spiderweb
- **Winter** snowflakes, falling snow, layered drifts
- **Arcade** marching pixel invaders, hearts, coins, CRT scanlines
- **Cinema** film strips and spotlight beams

<div align="center">
<img src="Readme%20images/themes.gif" alt="Browsing the theme dropdown and previewing different themes" width="850">
</div>

Every theme's colors can still be tweaked with the custom color pickers, and more palette examples are here:

<img src="Readme%20images/Styles.png" alt="Review cards in different color palettes" width="650">

## Free preview navigation

The preview area works like an infinite canvas, so what you see is exactly what gets saved:

- **Drag** with the mouse to move around the card freely
- **Scroll** to zoom in and out, anchored right where your cursor points
- **Double-click** (or the Fit button) to fit the whole card back in view
- **1:1** shows the card at its true export size, pixel for pixel

## Sizes for every platform

One dropdown switches the card dimensions to presets for X/Twitter, Instagram (square, portrait, story), TikTok, Facebook, Reddit, Discord, YouTube thumbnails, and Pinterest, or you can type any custom width and height. The layout adapts on its own: landscape cards put the cover on the left, portrait and story cards stack it on top, and fonts scale with the card size.

## Arabic support

I write reviews in Arabic too, so the text engine handles it properly: letters come out connected and in the right direction (not reversed), lines align to the right, and mixing Arabic with English words in the same sentence just works.

## Platforms and settings

Cards can carry your identity on Backloggd, Letterboxd, or MyAnimeList with a logo and a credit line in one of three styles: just `@username`, `Follow me on <platform>`, or `Posted on <platform> by @username`.

Open the Settings dialog once, save your usernames and preferred defaults (platform, theme, size, output folder), and the app fills everything in automatically every time you make a card.

<div align="center">
<img src="Readme%20images/settings.gif" alt="Settings dialog with usernames, credit line styles, and defaults" width="500">
</div>

## For tinkerers

The code is organized so adding things is easy:

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
├── ui/                     # customtkinter app + pan/zoom preview
└── utils/                  # fonts, colors, images, Arabic text shaping
```

A new palette is one dict entry, a new decorated theme is one `draw(card, style)` module, a new platform is one `PlatformSpec`, and a new size preset is one line. The UI picks all of them up automatically.

It also works from code:

```python
from bakuretsu import create_review_card

create_review_card(
    title="OMORI",
    score=9.0,
    review_text="A hauntingly beautiful RPG...",
    cover_image="https://example.com/omori.jpg",
    platform="backloggd",
    platform_username="YourUsername",
    attribution_style="follow",
    theme="Ramadan",
    size="Instagram Square",
    output_path="output/omori.png",
)
```

## Coming soon

- **The "Cross-Platform" Text Formatter**: format your reviews for multiple platforms at once
- **The "Can I Beat It?" Calculator**: estimate completion time based on your gaming habits
- **The "Deal Sniper"**: track prices and find the best deals for your wishlist
- *...and more*

## Download and start

You need Python 3.10+ installed, then:

```bash
# 1. Grab the code
git clone https://github.com/MegumiinUwU/Bakuretsu.git
cd Bakuretsu

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the app
python main.py
```

Generated cards are saved wherever you choose, with the `output/` folder as the default.

## License

See [LICENSE](LICENSE) for details.

---

<div align="center">
<img src="https://count.getloli.com/@auto-pipeline-ai?theme=rule34" alt="visitor counter">
</div>
