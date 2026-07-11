"""Small reusable UI widgets."""

from __future__ import annotations

import customtkinter as ctk
from tkinter import colorchooser

from bakuretsu.utils.colors import hex_to_rgb


class ColorButton(ctk.CTkButton):
    """A button that displays and lets the user pick a color."""

    def __init__(self, master, color: str, label: str, **kwargs):
        self.current_color = color
        super().__init__(
            master,
            text=label,
            fg_color=color,
            hover_color=color,
            width=105,
            height=36,
            command=self._pick_color,
            **kwargs,
        )
        self._update_text_color()

    def _pick_color(self):
        color = colorchooser.askcolor(color=self.current_color, title="Choose Color")
        if color[1]:
            self.set_color(color[1])

    def _update_text_color(self):
        r, g, b = hex_to_rgb(self.current_color)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        self.configure(text_color="#000000" if brightness > 128 else "#ffffff")

    def set_color(self, color: str):
        self.current_color = color
        self.configure(fg_color=color, hover_color=color)
        self._update_text_color()

    def get_color(self) -> str:
        return self.current_color


def section_label(master, text: str, size: int = 14) -> ctk.CTkLabel:
    return ctk.CTkLabel(master, text=text, font=ctk.CTkFont(size=size, weight="bold"))
