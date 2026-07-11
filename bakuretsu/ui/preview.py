"""Pan & zoom preview canvas (Canva-style free navigation).

- drag with the left mouse button to pan
- scroll wheel zooms in/out anchored at the cursor
- double-click or the Fit button re-fits the card to the window
- 1:1 button shows the true exported pixel size

Only the visible viewport is cropped and resized on each redraw, so
zooming into large story-size cards stays fast and memory-safe.
"""

from __future__ import annotations

import tkinter as tk
from typing import Optional

import customtkinter as ctk
from PIL import Image, ImageTk

MIN_SCALE = 0.02
MAX_SCALE = 8.0
WHEEL_FACTOR = 1.15


class PanZoomPreview(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._image: Optional[Image.Image] = None
        self._photo: Optional[ImageTk.PhotoImage] = None
        self._scale = 1.0
        self._offset_x = 0.0  # image origin in canvas coords
        self._offset_y = 0.0
        self._drag_start: Optional[tuple[int, int, float, float]] = None
        self._fitted = True  # auto-refit on resize until the user navigates
        self._quality_job: Optional[str] = None

        self.canvas = tk.Canvas(self, highlightthickness=0, bg="#101014", cursor="crosshair")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Double-Button-1>", lambda e: self.fit())
        self.canvas.bind("<MouseWheel>", self._on_wheel)  # Windows / macOS
        self.canvas.bind("<Button-4>", lambda e: self._zoom_at(e.x, e.y, WHEEL_FACTOR))  # Linux
        self.canvas.bind("<Button-5>", lambda e: self._zoom_at(e.x, e.y, 1 / WHEEL_FACTOR))
        self.canvas.bind("<Configure>", self._on_resize)

        # floating controls, bottom-right
        controls = ctk.CTkFrame(self.canvas, fg_color="#1c1c24", corner_radius=8)
        controls.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")

        def btn(text, command, width=34):
            return ctk.CTkButton(
                controls, text=text, width=width, height=28,
                fg_color="gray25", hover_color="gray35",
                font=ctk.CTkFont(size=13), command=command,
            )

        btn("−", lambda: self._zoom_center(1 / 1.25)).pack(side="left", padx=(6, 2), pady=5)
        self.zoom_label = ctk.CTkLabel(controls, text="100%", width=52, font=ctk.CTkFont(size=12))
        self.zoom_label.pack(side="left", padx=2, pady=5)
        btn("+", lambda: self._zoom_center(1.25)).pack(side="left", padx=2, pady=5)
        btn("Fit", self.fit, width=44).pack(side="left", padx=2, pady=5)
        btn("1:1", self.actual_size, width=44).pack(side="left", padx=(2, 6), pady=5)

        self._placeholder = self.canvas.create_text(
            0, 0, text="Click 'Generate Card' to preview",
            fill="#808080", font=("Segoe UI", 14),
        )
        self._image_item: Optional[int] = None

    # ---------- public API ----------

    def set_image(self, image: Image.Image) -> None:
        """Show a new card; keeps the current view if the size is unchanged."""
        same_size = self._image is not None and self._image.size == image.size
        self._image = image
        if same_size and not self._fitted:
            self._redraw()
        else:
            self.fit()

    def fit(self) -> None:
        """Scale to fit the whole card in the window, centered."""
        if self._image is None:
            return
        cw, ch = self._canvas_size()
        iw, ih = self._image.size
        self._scale = max(MIN_SCALE, min((cw - 30) / iw, (ch - 30) / ih, MAX_SCALE))
        self._center()
        self._fitted = True
        self._redraw()

    def actual_size(self) -> None:
        """Zoom to 100% (one card pixel = one screen pixel), centered."""
        if self._image is None:
            return
        self._scale = 1.0
        self._center()
        self._fitted = False
        self._redraw()

    # ---------- events ----------

    def _on_resize(self, _event) -> None:
        if self._image is None:
            cw, ch = self._canvas_size()
            self.canvas.coords(self._placeholder, cw // 2, ch // 2)
            return
        if self._fitted:
            self.fit()
        else:
            self._redraw()

    def _on_press(self, event) -> None:
        self._drag_start = (event.x, event.y, self._offset_x, self._offset_y)
        self.canvas.configure(cursor="fleur")

    def _on_drag(self, event) -> None:
        if self._drag_start is None or self._image is None:
            return
        sx, sy, ox, oy = self._drag_start
        self._offset_x = ox + (event.x - sx)
        self._offset_y = oy + (event.y - sy)
        self._fitted = False
        self._redraw(fast=True)

    def _on_release(self, _event) -> None:
        self._drag_start = None
        self.canvas.configure(cursor="crosshair")
        self._redraw()

    def _on_wheel(self, event) -> None:
        factor = WHEEL_FACTOR if event.delta > 0 else 1 / WHEEL_FACTOR
        self._zoom_at(event.x, event.y, factor)

    # ---------- zoom / pan math ----------

    def _zoom_center(self, factor: float) -> None:
        cw, ch = self._canvas_size()
        self._zoom_at(cw // 2, ch // 2, factor)

    def _zoom_at(self, mx: int, my: int, factor: float) -> None:
        if self._image is None:
            return
        new_scale = max(MIN_SCALE, min(self._scale * factor, MAX_SCALE))
        if new_scale == self._scale:
            return
        # keep the image point under the cursor fixed
        ratio = new_scale / self._scale
        self._offset_x = mx - (mx - self._offset_x) * ratio
        self._offset_y = my - (my - self._offset_y) * ratio
        self._scale = new_scale
        self._fitted = False
        self._redraw(fast=True)
        self._schedule_quality_pass()

    def _center(self) -> None:
        cw, ch = self._canvas_size()
        iw, ih = self._image.size
        self._offset_x = (cw - iw * self._scale) / 2
        self._offset_y = (ch - ih * self._scale) / 2

    def _canvas_size(self) -> tuple[int, int]:
        return max(self.canvas.winfo_width(), 50), max(self.canvas.winfo_height(), 50)

    # ---------- drawing ----------

    def _schedule_quality_pass(self) -> None:
        """After rapid zooming stops, redraw once with high-quality resampling."""
        if self._quality_job is not None:
            self.after_cancel(self._quality_job)
        self._quality_job = self.after(150, lambda: self._redraw(fast=False))

    def _redraw(self, fast: bool = False) -> None:
        if self._image is None:
            return
        self.canvas.itemconfigure(self._placeholder, state="hidden")

        cw, ch = self._canvas_size()
        iw, ih = self._image.size
        s = self._scale

        # visible part of the image, in image coordinates
        x0 = max(0.0, -self._offset_x / s)
        y0 = max(0.0, -self._offset_y / s)
        x1 = min(float(iw), (cw - self._offset_x) / s)
        y1 = min(float(ih), (ch - self._offset_y) / s)

        if self._image_item is not None:
            self.canvas.delete(self._image_item)
            self._image_item = None
        if x1 <= x0 or y1 <= y0:
            return  # card fully panned out of view

        crop = self._image.crop((int(x0), int(y0), int(x1 + 0.5) + 1, int(y1 + 0.5) + 1))
        target_w = max(1, round(crop.width * s))
        target_h = max(1, round(crop.height * s))
        resample = Image.Resampling.NEAREST if fast else (
            Image.Resampling.BILINEAR if s < 1 else Image.Resampling.LANCZOS
        )
        view = crop.resize((target_w, target_h), resample)

        self._photo = ImageTk.PhotoImage(view)
        self._image_item = self.canvas.create_image(
            round(self._offset_x + int(x0) * s),
            round(self._offset_y + int(y0) * s),
            image=self._photo,
            anchor="nw",
        )
        self.canvas.tag_lower(self._image_item)
        self.zoom_label.configure(text=f"{self._scale * 100:.0f}%")
