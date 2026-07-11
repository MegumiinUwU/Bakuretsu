"""Color palettes (hex strings).

Every palette defines the same four roles:
    background  card background
    primary     title text
    secondary   review/body text
    accent      stars, borders, decorative elements

Add a palette here and it appears in the UI automatically. Decorated
themes (see registry.py) reference these by name or define their own.
"""

Palette = dict[str, str]

PALETTES: dict[str, Palette] = {
    "Bakuretsu Dark": {
        "background": "#12121a",
        "primary": "#ffffff",
        "secondary": "#9ca3af",
        "accent": "#ec4899",
    },
    "Midnight Blue": {
        "background": "#0a192f",
        "primary": "#e6f1ff",
        "secondary": "#8892b0",
        "accent": "#64ffda",
    },
    "Deep Purple": {
        "background": "#1a1025",
        "primary": "#ffffff",
        "secondary": "#a78bfa",
        "accent": "#c084fc",
    },
    "Ocean": {
        "background": "#0c1821",
        "primary": "#ffffff",
        "secondary": "#94a3b8",
        "accent": "#38bdf8",
    },
    "Forest": {
        "background": "#14201a",
        "primary": "#ffffff",
        "secondary": "#86efac",
        "accent": "#22c55e",
    },
    "Sunset": {
        "background": "#1c1412",
        "primary": "#ffffff",
        "secondary": "#fca5a5",
        "accent": "#f97316",
    },
    "Monochrome": {
        "background": "#171717",
        "primary": "#ffffff",
        "secondary": "#a3a3a3",
        "accent": "#ffffff",
    },
    "Crimson": {
        "background": "#160b0e",
        "primary": "#fff1f2",
        "secondary": "#b08a90",
        "accent": "#e11d48",
    },
    "Gold Luxe": {
        "background": "#0f0d08",
        "primary": "#fdf6e3",
        "secondary": "#a89968",
        "accent": "#d4af37",
    },
    "Coffee": {
        "background": "#1b1310",
        "primary": "#f5ebe0",
        "secondary": "#b08968",
        "accent": "#e6a15c",
    },
    "Paper Light": {
        "background": "#f7f3ec",
        "primary": "#1f2937",
        "secondary": "#6b7280",
        "accent": "#d97706",
    },
    "Mint Light": {
        "background": "#f0faf5",
        "primary": "#134e4a",
        "secondary": "#5f8f87",
        "accent": "#0d9488",
    },
    # Palettes used by decorated themes
    "Retrowave": {
        "background": "#16122b",
        "primary": "#edf2f4",
        "secondary": "#e056fd",
        "accent": "#00d9ff",
    },
    "Ramadan": {
        "background": "#0a0e2a",
        "primary": "#ffffff",
        "secondary": "#c9a961",
        "accent": "#ffd700",
    },
    "Exams Time": {
        "background": "#1a2e1a",
        "primary": "#e8e4d4",
        "secondary": "#8faa8b",
        "accent": "#e63946",
    },
    "Sakura": {
        "background": "#1c1220",
        "primary": "#fff5f7",
        "secondary": "#d8a7b1",
        "accent": "#f9a8c4",
    },
    "Halloween": {
        "background": "#120a18",
        "primary": "#fff7ed",
        "secondary": "#a78bfa",
        "accent": "#f97316",
    },
    "Winter": {
        "background": "#0b1420",
        "primary": "#f0f9ff",
        "secondary": "#94b8d0",
        "accent": "#7dd3fc",
    },
    "Arcade": {
        "background": "#0d0d12",
        "primary": "#f8fafc",
        "secondary": "#94a3b8",
        "accent": "#22d3ee",
    },
    "Cinema": {
        "background": "#141210",
        "primary": "#faf5eb",
        "secondary": "#a89f91",
        "accent": "#e0b64f",
    },
    "Youssef Mohamed": {
        "background": "#0d1b45",
        "primary": "#ffffff",
        "secondary": "#9db4e8",
        "accent": "#ffd23f",
    },
}
