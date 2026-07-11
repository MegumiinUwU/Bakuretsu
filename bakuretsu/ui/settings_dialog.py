"""Settings dialog: platform usernames, attribution style and defaults."""

from __future__ import annotations

import customtkinter as ctk

from bakuretsu.platforms import PLATFORMS
from bakuretsu.settings import ATTRIBUTION_STYLES, AppSettings
from bakuretsu.sizes import preset_names
from bakuretsu.themes import theme_names
from bakuretsu.ui.widgets import section_label


class SettingsDialog(ctk.CTkToplevel):
    """Modal dialog editing the persistent AppSettings."""

    def __init__(self, master, settings: AppSettings, on_save=None):
        super().__init__(master)
        self.settings = settings
        self.on_save = on_save

        self.title("Settings")
        self.geometry("480x640")
        self.resizable(False, True)
        self.transient(master)
        self.grab_set()

        frame = ctk.CTkScrollableFrame(self)
        frame.pack(fill="both", expand=True, padx=14, pady=14)

        # --- usernames per platform ---
        section_label(frame, "Your usernames", 18).pack(anchor="w", pady=(4, 8))
        self.username_entries: dict[str, ctk.CTkEntry] = {}
        for key, platform in PLATFORMS.items():
            ctk.CTkLabel(frame, text=platform.name).pack(anchor="w")
            entry = ctk.CTkEntry(frame, placeholder_text=f"@you on {platform.name}", height=34)
            entry.pack(fill="x", pady=(2, 10))
            entry.insert(0, settings.username_for(key))
            self.username_entries[key] = entry

        # --- attribution style ---
        section_label(frame, "Credit line on cards", 18).pack(anchor="w", pady=(14, 8))
        self.attribution_var = ctk.StringVar(value=settings.attribution_style)
        for key, description in ATTRIBUTION_STYLES.items():
            ctk.CTkRadioButton(
                frame, text=description, variable=self.attribution_var, value=key
            ).pack(anchor="w", pady=3)

        # --- defaults ---
        section_label(frame, "Defaults", 18).pack(anchor="w", pady=(14, 8))

        ctk.CTkLabel(frame, text="Default platform").pack(anchor="w")
        platform_values = ["None"] + [p.name for p in PLATFORMS.values()]
        current_platform = "None"
        for p in PLATFORMS.values():
            if p.key == settings.default_platform:
                current_platform = p.name
        self.platform_var = ctk.StringVar(value=current_platform)
        ctk.CTkOptionMenu(frame, variable=self.platform_var, values=platform_values, height=34).pack(
            fill="x", pady=(2, 10)
        )

        ctk.CTkLabel(frame, text="Default theme").pack(anchor="w")
        self.theme_var = ctk.StringVar(value=settings.default_theme)
        ctk.CTkOptionMenu(frame, variable=self.theme_var, values=theme_names(), height=34).pack(
            fill="x", pady=(2, 10)
        )

        ctk.CTkLabel(frame, text="Default card size").pack(anchor="w")
        self.size_var = ctk.StringVar(value=settings.default_size)
        ctk.CTkOptionMenu(frame, variable=self.size_var, values=preset_names()[:-1], height=34).pack(
            fill="x", pady=(2, 10)
        )

        ctk.CTkLabel(frame, text="Output folder").pack(anchor="w")
        self.output_entry = ctk.CTkEntry(frame, height=34)
        self.output_entry.pack(fill="x", pady=(2, 10))
        self.output_entry.insert(0, settings.output_dir)

        # --- buttons ---
        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", padx=14, pady=(0, 14))
        ctk.CTkButton(buttons, text="Save", height=38, command=self._save).pack(
            side="right", padx=(8, 0)
        )
        ctk.CTkButton(
            buttons, text="Cancel", height=38, fg_color="gray30", hover_color="gray40",
            command=self.destroy,
        ).pack(side="right")

    def _save(self):
        for key, entry in self.username_entries.items():
            username = entry.get().strip().lstrip("@")
            if username:
                self.settings.usernames[key] = username
            else:
                self.settings.usernames.pop(key, None)

        self.settings.attribution_style = self.attribution_var.get()
        platform_name = self.platform_var.get()
        self.settings.default_platform = "none"
        for p in PLATFORMS.values():
            if p.name == platform_name:
                self.settings.default_platform = p.key
        self.settings.default_theme = self.theme_var.get()
        self.settings.default_size = self.size_var.get()
        self.settings.output_dir = self.output_entry.get().strip() or "output"

        self.settings.save()
        if self.on_save:
            self.on_save()
        self.destroy()
