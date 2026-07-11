"""Bakuretsu main window: inputs on the left, live preview on the right."""

from __future__ import annotations

import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

import customtkinter as ctk
from PIL import Image

import webbrowser
from urllib.parse import quote

from bakuretsu.api import (
    build_style,
    create_collage_card,
    create_review_card,
    create_score_card,
    create_star_card,
)
from bakuretsu.utils import clipboard
from bakuretsu.platforms import PLATFORMS
from bakuretsu.settings import ATTRIBUTION_STYLES, AppSettings
from bakuretsu.sizes import get_preset, preset_names
from bakuretsu.themes import THEMES, get_theme, theme_names
from bakuretsu.ui.preview import PanZoomPreview
from bakuretsu.ui.settings_dialog import SettingsDialog
from bakuretsu.ui.widgets import ColorButton, section_label
from bakuretsu.utils.colors import hex_to_rgb

MODES = ["Review Card", "Star Review", "Score Card", "Top List"]

SCORE_COLORS = ((8, "#22c55e"), (6, "#eab308"), (4, "#f97316"), (0, "#ef4444"))


def _score_hex(score: float) -> str:
    for threshold, color in SCORE_COLORS:
        if score >= threshold:
            return color
    return SCORE_COLORS[-1][1]


class BakuretsuApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bakuretsu — Review Card Generator")
        self.geometry("1420x920")
        self.minsize(1150, 780)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.settings = AppSettings.load()
        self.generated_card: Optional[Image.Image] = None
        self.preview_photo = None
        self._generating = False

        self._build_layout()
        self._build_inputs()
        self._build_style_panel()
        self._build_preview()
        self._apply_settings_defaults()

    # ---------- layout ----------

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.left = ctk.CTkScrollableFrame(self, width=430)
        self.left.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        self.right = ctk.CTkFrame(self)
        self.right.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.right.grid_rowconfigure(1, weight=1)
        self.right.grid_columnconfigure(0, weight=1)

    # ---------- input panel ----------

    def _build_inputs(self):
        top_row = ctk.CTkFrame(self.left, fg_color="transparent")
        top_row.pack(fill="x", pady=(6, 4))
        section_label(top_row, "Generator", 14).pack(side="left")
        ctk.CTkButton(
            top_row, text="⚙  Settings", width=110, height=30,
            fg_color="gray25", hover_color="gray35", command=self._open_settings,
        ).pack(side="right")

        self.mode_var = ctk.StringVar(value=MODES[0])
        ctk.CTkSegmentedButton(
            self.left, values=MODES, variable=self.mode_var, command=self._on_mode_change
        ).pack(fill="x", pady=(0, 16))

        section_label(self.left, "Title").pack(anchor="w")
        self.title_entry = ctk.CTkEntry(
            self.left, placeholder_text="Game / movie / anime name...", height=40,
            font=ctk.CTkFont(size=14),
        )
        self.title_entry.pack(fill="x", pady=(4, 14))

        # --- mode specific frames ---
        self.mode_frame = ctk.CTkFrame(self.left, fg_color="transparent")
        self.mode_frame.pack(fill="x")

        # review mode: score + text
        self.review_frame = ctk.CTkFrame(self.mode_frame, fg_color="transparent")
        self.review_frame.pack(fill="x")
        self._build_score_slider(self.review_frame, "score")
        section_label(self.review_frame, "Review").pack(anchor="w")
        self.review_text = ctk.CTkTextbox(self.review_frame, height=150, font=ctk.CTkFont(size=13))
        self.review_text.pack(fill="x", pady=(4, 14))

        # star mode
        self.star_frame = ctk.CTkFrame(self.mode_frame, fg_color="transparent")
        section_label(self.star_frame, "Star Rating").pack(anchor="w")
        star_row = ctk.CTkFrame(self.star_frame, fg_color="transparent")
        star_row.pack(fill="x", pady=(4, 14))
        self.stars_var = ctk.DoubleVar(value=4.0)
        ctk.CTkSlider(
            star_row, from_=0.5, to=5.0, number_of_steps=9,
            variable=self.stars_var, command=self._update_stars_label,
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.stars_label = ctk.CTkLabel(
            star_row, text="★★★★☆  4.0",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffd700", width=130,
        )
        self.stars_label.pack(side="right")

        # score card mode
        self.score_card_frame = ctk.CTkFrame(self.mode_frame, fg_color="transparent")
        self._build_score_slider(self.score_card_frame, "sc_score")

        # top list (collage) mode
        self.collage_items: list[dict] = []
        self.collage_frame = ctk.CTkFrame(self.mode_frame, fg_color="transparent")

        ctk.CTkLabel(self.collage_frame, text="Subtitle (optional)").pack(anchor="w")
        self.subtitle_entry = ctk.CTkEntry(self.collage_frame, placeholder_text="e.g. ranked by pure vibes", height=32)
        self.subtitle_entry.pack(fill="x", pady=(2, 10))

        section_label(self.collage_frame, "List Items (2-10, rank order)").pack(anchor="w")
        add_box = ctk.CTkFrame(self.collage_frame, fg_color="gray17")
        add_box.pack(fill="x", pady=(4, 8))

        row1 = ctk.CTkFrame(add_box, fg_color="transparent")
        row1.pack(fill="x", padx=8, pady=(8, 4))
        self.item_title_entry = ctk.CTkEntry(row1, placeholder_text="Item title...", height=32)
        self.item_title_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.item_score_entry = ctk.CTkEntry(row1, placeholder_text="0-10", width=58, height=32)
        self.item_score_entry.pack(side="right")

        row2 = ctk.CTkFrame(add_box, fg_color="transparent")
        row2.pack(fill="x", padx=8, pady=(0, 4))
        self.item_cover_entry = ctk.CTkEntry(row2, placeholder_text="Cover URL or Browse...", height=32)
        self.item_cover_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(row2, text="Browse", width=70, height=32, command=self._browse_item_cover).pack(side="right")

        ctk.CTkButton(add_box, text="+ Add Item", height=32, command=self._add_collage_item).pack(
            fill="x", padx=8, pady=(2, 8)
        )

        self.items_list_frame = ctk.CTkFrame(self.collage_frame, fg_color="transparent")
        self.items_list_frame.pack(fill="x", pady=(0, 12))

        # --- common ---
        section_label(self.left, "Content Type").pack(anchor="w")
        self.content_var = ctk.StringVar(value="game")
        content_row = ctk.CTkFrame(self.left, fg_color="transparent")
        content_row.pack(fill="x", pady=(4, 14))
        for value, label in (("game", "Game"), ("movie", "Movie"), ("anime", "Anime")):
            ctk.CTkRadioButton(content_row, text=label, variable=self.content_var, value=value).pack(
                side="left", padx=(0, 16)
            )

        section_label(self.left, "Platform").pack(anchor="w")
        self.platform_var = ctk.StringVar(value="None")
        ctk.CTkOptionMenu(
            self.left, variable=self.platform_var,
            values=["None"] + [p.name for p in PLATFORMS.values()],
            command=self._on_platform_change, height=38,
        ).pack(fill="x", pady=(4, 8))

        self.username_frame = ctk.CTkFrame(self.left, fg_color="transparent")
        ctk.CTkLabel(self.username_frame, text="Username").pack(anchor="w")
        self.username_entry = ctk.CTkEntry(self.username_frame, placeholder_text="@yourusername", height=34)
        self.username_entry.pack(fill="x", pady=(2, 4))
        self.attribution_var = ctk.StringVar(value=self.settings.attribution_style)
        ctk.CTkLabel(self.username_frame, text="Credit line").pack(anchor="w", pady=(4, 0))
        ctk.CTkOptionMenu(
            self.username_frame, variable=self.attribution_var,
            values=list(ATTRIBUTION_STYLES.keys()), height=30,
        ).pack(fill="x", pady=(2, 4))

        section_label(self.left, "Cover Image").pack(anchor="w", pady=(10, 0))
        cover_row = ctk.CTkFrame(self.left, fg_color="transparent")
        cover_row.pack(fill="x", pady=(4, 4))
        self.cover_entry = ctk.CTkEntry(cover_row, placeholder_text="Image URL or Browse...", height=38)
        self.cover_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(cover_row, text="Browse", width=80, height=38, command=self._browse_cover).pack(side="right")
        self.cover_status = ctk.CTkLabel(self.left, text="", font=ctk.CTkFont(size=12), text_color="gray")
        self.cover_status.pack(anchor="w", pady=(0, 10))

    def _build_score_slider(self, parent, kind: str):
        section_label(parent, "Score (0-10)").pack(anchor="w")
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(4, 14))
        var = ctk.DoubleVar(value=7.0)
        label = ctk.CTkLabel(row, text="7.0", font=ctk.CTkFont(size=18, weight="bold"), width=48)

        def update(value, v=var, lbl=label):
            score = round(float(value) * 2) / 2
            v.set(score)
            lbl.configure(text=f"{score:.1f}", text_color=_score_hex(score))

        ctk.CTkSlider(row, from_=0, to=10, number_of_steps=20, variable=var, command=update).pack(
            side="left", fill="x", expand=True, padx=(0, 10)
        )
        label.pack(side="right")
        setattr(self, f"{kind}_var", var)
        setattr(self, f"{kind}_label", label)

    # ---------- style panel ----------

    def _build_style_panel(self):
        ctk.CTkFrame(self.left, height=2, fg_color="gray30").pack(fill="x", pady=16)
        section_label(self.left, "Card Style", 20).pack(anchor="w", pady=(0, 10))

        section_label(self.left, "Theme").pack(anchor="w")
        self.theme_var = ctk.StringVar(value=self.settings.default_theme)
        ctk.CTkOptionMenu(
            self.left, variable=self.theme_var, values=theme_names(),
            command=self._apply_theme, height=38,
        ).pack(fill="x", pady=(4, 12))

        section_label(self.left, "Custom Colors").pack(anchor="w", pady=(2, 4))
        row1 = ctk.CTkFrame(self.left, fg_color="transparent")
        row1.pack(fill="x", pady=(2, 6))
        self.bg_btn = ColorButton(row1, "#12121a", "Background")
        self.bg_btn.pack(side="left", padx=(0, 8))
        self.primary_btn = ColorButton(row1, "#ffffff", "Title")
        self.primary_btn.pack(side="left", padx=(0, 8))
        row2 = ctk.CTkFrame(self.left, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 12))
        self.secondary_btn = ColorButton(row2, "#9ca3af", "Body")
        self.secondary_btn.pack(side="left", padx=(0, 8))
        self.accent_btn = ColorButton(row2, "#ec4899", "Accent")
        self.accent_btn.pack(side="left", padx=(0, 8))

        section_label(self.left, "Card Size").pack(anchor="w", pady=(4, 0))
        self.size_var = ctk.StringVar(value=self.settings.default_size)
        ctk.CTkOptionMenu(
            self.left, variable=self.size_var, values=preset_names(),
            command=self._on_size_change, height=38,
        ).pack(fill="x", pady=(4, 6))

        size_row = ctk.CTkFrame(self.left, fg_color="transparent")
        size_row.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(size_row, text="W:").pack(side="left")
        self.width_entry = ctk.CTkEntry(size_row, width=70, height=30)
        self.width_entry.pack(side="left", padx=(4, 12))
        ctk.CTkLabel(size_row, text="H:").pack(side="left")
        self.height_entry = ctk.CTkEntry(size_row, width=70, height=30)
        self.height_entry.pack(side="left", padx=(4, 12))
        ctk.CTkLabel(size_row, text="Radius:").pack(side="left")
        self.radius_entry = ctk.CTkEntry(size_row, width=56, height=30)
        self.radius_entry.pack(side="left", padx=4)
        self.radius_entry.insert(0, "0")
        self._set_size_fields(1200, 675)

    # ---------- preview panel ----------

    def _build_preview(self):
        header = ctk.CTkFrame(self.right, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 8))
        section_label(header, "Preview", 20).pack(side="left")

        buttons = ctk.CTkFrame(header, fg_color="transparent")
        buttons.pack(side="right")
        self.generate_btn = ctk.CTkButton(
            buttons, text="Generate Card", font=ctk.CTkFont(size=14, weight="bold"),
            height=40, width=140, command=self._generate,
        )
        self.generate_btn.pack(side="left", padx=(0, 8))
        self.save_btn = ctk.CTkButton(
            buttons, text="Save Image", height=40, width=110,
            fg_color="gray30", hover_color="gray40", command=self._save, state="disabled",
        )
        self.save_btn.pack(side="left")

        self.preview_frame = ctk.CTkFrame(self.right, fg_color="gray14")
        self.preview_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 16))
        self.preview_frame.grid_rowconfigure(0, weight=1)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview = PanZoomPreview(self.preview_frame)
        self.preview.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        # share bar: appears active once a card is generated
        share_bar = ctk.CTkFrame(self.right, fg_color="transparent")
        share_bar.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 4))
        self.copy_btn = ctk.CTkButton(
            share_bar, text="📋 Copy Image", height=32, width=130,
            fg_color="gray25", hover_color="gray35", state="disabled",
            command=self._copy_card,
        )
        self.copy_btn.pack(side="left", padx=(0, 8))
        self.x_share_btn = ctk.CTkButton(
            share_bar, text="Post on X", height=32, width=100,
            fg_color="gray25", hover_color="gray35", state="disabled",
            command=self._share_on_x,
        )
        self.x_share_btn.pack(side="left", padx=(0, 8))
        self.platform_share_btn = ctk.CTkButton(
            share_bar, text="Open Platform", height=32, width=150,
            fg_color="gray25", hover_color="gray35", state="disabled",
            command=self._share_on_platform,
        )
        self.platform_share_btn.pack(side="left")

        self.status = ctk.CTkLabel(
            self.right,
            text="Ready  |  drag to pan, scroll to zoom, double-click to fit",
            font=ctk.CTkFont(size=12), text_color="gray",
        )
        self.status.grid(row=3, column=0, sticky="w", padx=20, pady=(0, 8))

    # ---------- events ----------

    def _apply_settings_defaults(self):
        self._apply_theme(self.settings.default_theme)
        self.theme_var.set(self.settings.default_theme)
        self.size_var.set(self.settings.default_size)
        self._on_size_change(self.settings.default_size)
        default = self.settings.default_platform
        if default != "none" and default in PLATFORMS:
            self.platform_var.set(PLATFORMS[default].name)
            self._on_platform_change(PLATFORMS[default].name)

    def _open_settings(self):
        SettingsDialog(self, self.settings, on_save=self._apply_settings_defaults)

    def _on_mode_change(self, mode: str):
        for frame in (self.review_frame, self.star_frame, self.score_card_frame, self.collage_frame):
            frame.pack_forget()
        if mode == "Review Card":
            self.review_frame.pack(fill="x")
        elif mode == "Star Review":
            self.star_frame.pack(fill="x")
        elif mode == "Score Card":
            self.score_card_frame.pack(fill="x")
        else:
            self.collage_frame.pack(fill="x")
        # square presets suit the star/score cards better
        if mode in ("Star Review", "Score Card") and self.size_var.get() == "Landscape (Default)":
            self.size_var.set("Instagram Square")
            self._on_size_change("Instagram Square")

    # ---------- top list items ----------

    def _browse_item_cover(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.webp *.bmp"), ("All files", "*.*")]
        )
        if filepath:
            self.item_cover_entry.delete(0, "end")
            self.item_cover_entry.insert(0, filepath)

    def _add_collage_item(self):
        title = self.item_title_entry.get().strip()
        if not title:
            messagebox.showerror("Top List", "Please enter an item title.")
            return
        try:
            score = float(self.item_score_entry.get().strip())
            if not 0 <= score <= 10:
                raise ValueError
        except ValueError:
            messagebox.showerror("Top List", "Score must be a number between 0 and 10.")
            return
        if len(self.collage_items) >= 10:
            messagebox.showerror("Top List", "Maximum 10 items.")
            return
        self.collage_items.append({
            "title": title,
            "score": score,
            "cover_image": self.item_cover_entry.get().strip() or None,
        })
        self.item_title_entry.delete(0, "end")
        self.item_score_entry.delete(0, "end")
        self.item_cover_entry.delete(0, "end")
        self._refresh_items_list()

    def _move_collage_item(self, index: int, delta: int):
        new_index = index + delta
        if 0 <= new_index < len(self.collage_items):
            items = self.collage_items
            items[index], items[new_index] = items[new_index], items[index]
            self._refresh_items_list()

    def _remove_collage_item(self, index: int):
        del self.collage_items[index]
        self._refresh_items_list()

    def _refresh_items_list(self):
        for child in self.items_list_frame.winfo_children():
            child.destroy()
        for i, item in enumerate(self.collage_items):
            row = ctk.CTkFrame(self.items_list_frame, fg_color="gray17")
            row.pack(fill="x", pady=2)
            label = f"{i + 1}.  {item['title']}   ({item['score']:g})"
            ctk.CTkLabel(row, text=label, anchor="w").pack(
                side="left", fill="x", expand=True, padx=8
            )
            ctk.CTkButton(row, text="✕", width=28, height=24, fg_color="gray25",
                          hover_color="#7f1d1d", command=lambda i=i: self._remove_collage_item(i)).pack(
                side="right", padx=(2, 6), pady=3)
            ctk.CTkButton(row, text="↓", width=28, height=24, fg_color="gray25", hover_color="gray35",
                          command=lambda i=i: self._move_collage_item(i, 1)).pack(side="right", padx=2, pady=3)
            ctk.CTkButton(row, text="↑", width=28, height=24, fg_color="gray25", hover_color="gray35",
                          command=lambda i=i: self._move_collage_item(i, -1)).pack(side="right", padx=2, pady=3)

    def _update_stars_label(self, value):
        stars = round(float(value) * 2) / 2
        self.stars_var.set(stars)
        full = int(stars)
        half = (stars - full) >= 0.25
        display = "★" * full + ("½" if half else "") + "☆" * (5 - full - (1 if half else 0))
        self.stars_label.configure(text=f"{display}  {stars:.1f}")

    def _on_platform_change(self, platform_name: str):
        if platform_name == "None":
            self.username_frame.pack_forget()
            self.platform_share_btn.configure(text="Open Platform", state="disabled")
            return
        self.username_frame.pack(fill="x", pady=(0, 10))
        for platform in PLATFORMS.values():
            if platform.name == platform_name:
                saved = self.settings.username_for(platform.key)
                self.username_entry.delete(0, "end")
                if saved:
                    self.username_entry.insert(0, saved)
                self.platform_share_btn.configure(
                    text=f"Open {platform.name}",
                    state="normal" if self.generated_card else "disabled",
                )

    def _on_size_change(self, preset_name: str):
        preset = get_preset(preset_name)
        if preset:
            self._set_size_fields(preset.width, preset.height)

    def _set_size_fields(self, width: int, height: int):
        self.width_entry.delete(0, "end")
        self.width_entry.insert(0, str(width))
        self.height_entry.delete(0, "end")
        self.height_entry.insert(0, str(height))

    def _apply_theme(self, theme_name: str):
        theme = get_theme(theme_name)
        if theme:
            palette = theme.palette
            self.bg_btn.set_color(palette["background"])
            self.primary_btn.set_color(palette["primary"])
            self.secondary_btn.set_color(palette["secondary"])
            self.accent_btn.set_color(palette["accent"])

    def _browse_cover(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.webp *.bmp"), ("All files", "*.*")]
        )
        if filepath:
            self.cover_entry.delete(0, "end")
            self.cover_entry.insert(0, filepath)
            self.cover_status.configure(text=f"Selected: {Path(filepath).name}", text_color="green")

    # ---------- generation ----------

    def _current_style(self):
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            radius = int(self.radius_entry.get())
        except ValueError:
            width, height, radius = 1200, 675, 0

        theme_name = self.theme_var.get()
        theme = get_theme(theme_name)
        style = build_style(width=width, height=height, corner_radius=radius)
        style.background_color = (*hex_to_rgb(self.bg_btn.get_color()), 255)
        style.primary_color = hex_to_rgb(self.primary_btn.get_color())
        style.secondary_color = hex_to_rgb(self.secondary_btn.get_color())
        style.accent_color = hex_to_rgb(self.accent_btn.get_color())
        style.theme = theme_name if (theme and theme.decorated) else None
        return style

    def _platform_key(self) -> str:
        name = self.platform_var.get()
        for platform in PLATFORMS.values():
            if platform.name == name:
                return platform.key
        return "none"

    def _validate(self) -> bool:
        if not self.title_entry.get().strip():
            messagebox.showerror("Validation Error", "Please enter a title.")
            return False
        if self.mode_var.get() == "Review Card" and not self.review_text.get("1.0", "end").strip():
            messagebox.showerror("Validation Error", "Please enter a review.")
            return False
        if self.mode_var.get() == "Top List" and len(self.collage_items) < 2:
            messagebox.showerror("Validation Error", "Add at least 2 items to the list.")
            return False
        return True

    def _generate(self):
        if self._generating or not self._validate():
            return
        self._generating = True
        self.status.configure(text="Generating...", text_color="#eab308")
        self.generate_btn.configure(state="disabled")

        mode = self.mode_var.get()
        kwargs = dict(
            title=self.title_entry.get().strip(),
            content_type=self.content_var.get(),
            cover_image=self.cover_entry.get().strip() or None,
            platform=self._platform_key(),
            platform_username=self.username_entry.get().strip().lstrip("@"),
            attribution_style=self.attribution_var.get(),
            style=self._current_style(),
        )
        if mode == "Review Card":
            kwargs.update(score=self.score_var.get(), review_text=self.review_text.get("1.0", "end").strip())
            fn = create_review_card
        elif mode == "Star Review":
            kwargs.update(stars=self.stars_var.get())
            fn = create_star_card
        elif mode == "Score Card":
            kwargs.update(score=self.sc_score_var.get())
            fn = create_score_card
        else:
            kwargs.pop("cover_image", None)
            kwargs.update(
                entries=[dict(item) for item in self.collage_items],
                subtitle=self.subtitle_entry.get().strip(),
            )
            fn = create_collage_card

        def work():
            try:
                card = fn(**kwargs)
                self.after(0, lambda: self._on_generated(card))
            except Exception as exc:  # noqa: BLE001 - surfaced to the user
                self.after(0, lambda exc=exc: self._on_generation_error(exc))

        threading.Thread(target=work, daemon=True).start()

    def _on_generated(self, card: Image.Image):
        self._generating = False
        self.generated_card = card
        self.generate_btn.configure(state="normal")
        self.save_btn.configure(state="normal")
        if clipboard.is_supported():
            self.copy_btn.configure(state="normal")
        self.x_share_btn.configure(state="normal")
        if self._platform_key() != "none":
            self.platform_share_btn.configure(state="normal")
        self.status.configure(text="Card generated!", text_color="#22c55e")
        self._update_preview()

    # ---------- share ----------

    def _copy_card(self) -> bool:
        if not self.generated_card:
            return False
        if clipboard.copy_image(self.generated_card):
            self.status.configure(text="Image copied to clipboard!", text_color="#22c55e")
            return True
        self.status.configure(text="Clipboard copy failed on this system", text_color="#ef4444")
        return False

    def _share_text(self) -> str:
        title = self.title_entry.get().strip()
        mode = self.mode_var.get()
        if mode == "Review Card":
            return f"{title} - {self.score_var.get():g}/10"
        if mode == "Star Review":
            return f"{title} - {self.stars_var.get():g}/5 stars"
        if mode == "Score Card":
            return f"{title} - {self.sc_score_var.get():g}/10"
        return title

    def _share_on_x(self):
        if self._copy_card():
            self.status.configure(
                text="Image copied! Paste it (Ctrl+V) into your post", text_color="#22c55e"
            )
        webbrowser.open(f"https://twitter.com/intent/tweet?text={quote(self._share_text())}")

    def _share_on_platform(self):
        platform_key = self._platform_key()
        for platform in PLATFORMS.values():
            if platform.key == platform_key and platform.search_url:
                if self._copy_card():
                    self.status.configure(
                        text=f"Image copied! Paste it into your {platform.name} review",
                        text_color="#22c55e",
                    )
                webbrowser.open(platform.share_link(self.title_entry.get().strip()))
                return

    def _on_generation_error(self, exc: Exception):
        self._generating = False
        self.generate_btn.configure(state="normal")
        self.status.configure(text=f"Error: {exc}", text_color="#ef4444")
        messagebox.showerror("Generation Error", str(exc))

    def _update_preview(self):
        if self.generated_card:
            self.preview.set_image(self.generated_card)

    def _save(self):
        if not self.generated_card:
            return
        title = self.title_entry.get().strip()
        safe = "".join(c for c in title if c.isalnum() or c in " -_").strip().replace(" ", "_")
        suffix = {
            "Review Card": "_review",
            "Star Review": "_star_review",
            "Score Card": "_score_card",
            "Top List": "_top_list",
        }[self.mode_var.get()]
        out_dir = Path(self.settings.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=f"{safe or 'card'}{suffix}.png",
            initialdir=str(out_dir),
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All files", "*.*")],
        )
        if filepath:
            try:
                if filepath.lower().endswith((".jpg", ".jpeg")):
                    self.generated_card.convert("RGB").save(filepath, quality=95)
                else:
                    self.generated_card.save(filepath)
                self.status.configure(text=f"Saved: {Path(filepath).name}", text_color="#22c55e")
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror("Save Error", str(exc))


def main():
    app = BakuretsuApp()
    app.mainloop()


if __name__ == "__main__":
    main()
