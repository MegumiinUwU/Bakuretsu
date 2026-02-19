"""
Bakuretsu Review Card Generator - UI Application
A modern GUI for generating branded review cards.
"""

import customtkinter as ctk
from tkinter import filedialog, colorchooser, messagebox
from PIL import Image, ImageTk
import os
from pathlib import Path
from typing import Optional
import threading

from review_card_generator import (
    create_review_card,
    CardStyle,
    ReviewCardGenerator,
    ReviewData,
    Platform,
    ContentType,
    ImageLoader
)


# Color Palettes
COLOR_PALETTES = {
    "Bakuretsu Dark": {
        "background": "#12121a",
        "primary": "#ffffff",
        "secondary": "#9ca3af",
        "accent": "#ec4899"
    },
    "Midnight Blue": {
        "background": "#0a192f",
        "primary": "#e6f1ff",
        "secondary": "#8892b0",
        "accent": "#64ffda"
    },
    "Deep Purple": {
        "background": "#1a1025",
        "primary": "#ffffff",
        "secondary": "#a78bfa",
        "accent": "#c084fc"
    },
    "Ocean": {
        "background": "#0c1821",
        "primary": "#ffffff",
        "secondary": "#94a3b8",
        "accent": "#38bdf8"
    },
    "Forest": {
        "background": "#14201a",
        "primary": "#ffffff",
        "secondary": "#86efac",
        "accent": "#22c55e"
    },
    "Sunset": {
        "background": "#1c1412",
        "primary": "#ffffff",
        "secondary": "#fca5a5",
        "accent": "#f97316"
    },
    "Monochrome": {
        "background": "#171717",
        "primary": "#ffffff",
        "secondary": "#a3a3a3",
        "accent": "#ffffff"
    },
    "Retrowave": {
        "background": "#1a1a2e",
        "primary": "#edf2f4",
        "secondary": "#e056fd",
        "accent": "#00d9ff"
    },
    "Ramadan": {
        "background": "#0a0e2a",
        "primary": "#ffffff",
        "secondary": "#c9a961",
        "accent": "#ffd700"
    }
}

THEMED_PALETTES = {"Ramadan"}


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color."""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


class ColorButton(ctk.CTkButton):
    """A button that displays and allows picking a color."""
    
    def __init__(self, master, color: str, label: str, **kwargs):
        self.current_color = color
        super().__init__(
            master,
            text=label,
            fg_color=color,
            hover_color=color,
            width=120,
            height=40,
            command=self._pick_color,
            **kwargs
        )
        self._update_text_color()
    
    def _pick_color(self):
        """Open color picker dialog."""
        color = colorchooser.askcolor(color=self.current_color, title="Choose Color")
        if color[1]:
            self.current_color = color[1]
            self.configure(fg_color=self.current_color, hover_color=self.current_color)
            self._update_text_color()
    
    def _update_text_color(self):
        """Update text color based on background brightness."""
        rgb = hex_to_rgb(self.current_color)
        brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
        text_color = "#000000" if brightness > 128 else "#ffffff"
        self.configure(text_color=text_color)
    
    def set_color(self, color: str):
        """Set the button's color."""
        self.current_color = color
        self.configure(fg_color=color, hover_color=color)
        self._update_text_color()
    
    def get_color(self) -> str:
        """Get the current color."""
        return self.current_color


class ReviewCardApp(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("Bakuretsu - Review Card Generator")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Variables
        self.cover_image_path: Optional[str] = None
        self.generated_card: Optional[Image.Image] = None
        self.preview_photo: Optional[ImageTk.PhotoImage] = None
        
        # Build UI
        self._create_layout()
        self._create_input_panel()
        self._create_style_panel()
        self._create_preview_panel()
        
        # Apply default palette
        self._apply_palette("Bakuretsu Dark")
    
    def _create_layout(self):
        """Create the main layout structure."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        # Left panel (inputs + style)
        self.left_panel = ctk.CTkScrollableFrame(self, width=450)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Right panel (preview)
        self.right_panel = ctk.CTkFrame(self)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_panel.grid_rowconfigure(1, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)
    
    def _create_input_panel(self):
        """Create the review input section."""
        # Header
        header = ctk.CTkLabel(
            self.left_panel,
            text="Review Details",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=(10, 20), anchor="w")
        
        # Title
        ctk.CTkLabel(self.left_panel, text="Title", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.title_entry = ctk.CTkEntry(
            self.left_panel,
            placeholder_text="Game or Movie name...",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.title_entry.pack(fill="x", pady=(5, 15))
        
        # Score
        ctk.CTkLabel(self.left_panel, text="Score (0-10)", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        
        score_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        score_frame.pack(fill="x", pady=(5, 15))
        
        self.score_var = ctk.DoubleVar(value=7.0)
        self.score_slider = ctk.CTkSlider(
            score_frame,
            from_=0,
            to=10,
            number_of_steps=20,
            variable=self.score_var,
            command=self._update_score_label
        )
        self.score_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.score_label = ctk.CTkLabel(
            score_frame,
            text="7.0",
            font=ctk.CTkFont(size=18, weight="bold"),
            width=50
        )
        self.score_label.pack(side="right")
        
        # Review Text
        ctk.CTkLabel(self.left_panel, text="Review", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.review_text = ctk.CTkTextbox(
            self.left_panel,
            height=150,
            font=ctk.CTkFont(size=13)
        )
        self.review_text.pack(fill="x", pady=(5, 15))
        
        # Content Type
        ctk.CTkLabel(self.left_panel, text="Content Type", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.content_type_var = ctk.StringVar(value="game")
        content_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        content_frame.pack(fill="x", pady=(5, 15))
        
        ctk.CTkRadioButton(
            content_frame,
            text="Game",
            variable=self.content_type_var,
            value="game"
        ).pack(side="left", padx=(0, 20))
        
        ctk.CTkRadioButton(
            content_frame,
            text="Movie",
            variable=self.content_type_var,
            value="movie"
        ).pack(side="left")
        
        # Platform
        ctk.CTkLabel(self.left_panel, text="Platform", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.platform_var = ctk.StringVar(value="none")
        self.platform_menu = ctk.CTkOptionMenu(
            self.left_panel,
            variable=self.platform_var,
            values=["None", "Backloggd", "Letterboxd"],
            command=self._on_platform_change,
            height=40
        )
        self.platform_menu.pack(fill="x", pady=(5, 10))
        
        # Username (initially hidden)
        self.username_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.username_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(self.username_frame, text="Username", font=ctk.CTkFont(size=14)).pack(anchor="w")
        self.username_entry = ctk.CTkEntry(
            self.username_frame,
            placeholder_text="@yourusername",
            height=35
        )
        self.username_entry.pack(fill="x", pady=(5, 0))
        self.username_frame.pack_forget()  # Hide initially
        
        # Cover Image
        ctk.CTkLabel(self.left_panel, text="Cover Image", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        
        cover_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        cover_frame.pack(fill="x", pady=(5, 10))
        
        self.cover_entry = ctk.CTkEntry(
            cover_frame,
            placeholder_text="Image URL or click Browse...",
            height=40
        )
        self.cover_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            cover_frame,
            text="Browse",
            width=80,
            height=40,
            command=self._browse_cover
        ).pack(side="right")
        
        self.cover_status = ctk.CTkLabel(
            self.left_panel,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.cover_status.pack(anchor="w", pady=(0, 15))
    
    def _create_style_panel(self):
        """Create the styling section."""
        # Divider
        ctk.CTkFrame(self.left_panel, height=2, fg_color="gray30").pack(fill="x", pady=20)
        
        # Style Header
        header = ctk.CTkLabel(
            self.left_panel,
            text="Card Style",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=(0, 20), anchor="w")
        
        # Palette Selection
        ctk.CTkLabel(self.left_panel, text="Color Palette", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.palette_var = ctk.StringVar(value="Bakuretsu Dark")
        self.palette_menu = ctk.CTkOptionMenu(
            self.left_panel,
            variable=self.palette_var,
            values=list(COLOR_PALETTES.keys()),
            command=self._apply_palette,
            height=40
        )
        self.palette_menu.pack(fill="x", pady=(5, 15))
        
        # Individual Color Buttons
        ctk.CTkLabel(self.left_panel, text="Custom Colors (click to change)", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        colors_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        colors_frame.pack(fill="x", pady=(5, 15))
        
        self.bg_color_btn = ColorButton(colors_frame, "#12121a", "Background")
        self.bg_color_btn.pack(side="left", padx=(0, 10))
        
        self.primary_color_btn = ColorButton(colors_frame, "#ffffff", "Title")
        self.primary_color_btn.pack(side="left", padx=(0, 10))
        
        colors_frame2 = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        colors_frame2.pack(fill="x", pady=(0, 15))
        
        self.secondary_color_btn = ColorButton(colors_frame2, "#9ca3af", "Review")
        self.secondary_color_btn.pack(side="left", padx=(0, 10))
        
        self.accent_color_btn = ColorButton(colors_frame2, "#ec4899", "Accent")
        self.accent_color_btn.pack(side="left", padx=(0, 10))
        
        # Card Dimensions
        ctk.CTkLabel(self.left_panel, text="Card Size", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        size_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        size_frame.pack(fill="x", pady=(5, 15))
        
        ctk.CTkLabel(size_frame, text="Width:").pack(side="left")
        self.width_entry = ctk.CTkEntry(size_frame, width=70, height=30)
        self.width_entry.insert(0, "1200")
        self.width_entry.pack(side="left", padx=(5, 15))
        
        ctk.CTkLabel(size_frame, text="Height:").pack(side="left")
        self.height_entry = ctk.CTkEntry(size_frame, width=70, height=30)
        self.height_entry.insert(0, "675")
        self.height_entry.pack(side="left", padx=5)
        
        # Corner Radius
        radius_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        radius_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(radius_frame, text="Corner Radius:").pack(side="left")
        self.radius_entry = ctk.CTkEntry(radius_frame, width=70, height=30)
        self.radius_entry.insert(0, "20")
        self.radius_entry.pack(side="left", padx=5)
    
    def _create_preview_panel(self):
        """Create the preview section."""
        # Header with buttons
        header_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="Preview",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        # Action buttons
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")
        
        self.generate_btn = ctk.CTkButton(
            btn_frame,
            text="Generate Card",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=140,
            command=self._generate_card
        )
        self.generate_btn.pack(side="left", padx=(0, 10))
        
        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="Save Image",
            font=ctk.CTkFont(size=14),
            height=40,
            width=120,
            fg_color="gray30",
            hover_color="gray40",
            command=self._save_card,
            state="disabled"
        )
        self.save_btn.pack(side="left")
        
        # Preview canvas
        self.preview_frame = ctk.CTkFrame(self.right_panel, fg_color="gray17")
        self.preview_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.preview_frame.grid_rowconfigure(0, weight=1)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        
        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Click 'Generate Card' to preview",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        self.preview_label.grid(row=0, column=0)
        
        # Status bar
        self.status_label = ctk.CTkLabel(
            self.right_panel,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 10))
    
    def _update_score_label(self, value):
        """Update the score display label."""
        score = round(value * 2) / 2  # Round to nearest 0.5
        self.score_var.set(score)
        self.score_label.configure(text=f"{score:.1f}" if score != int(score) else f"{int(score)}.0")
        
        # Update color based on score
        if score >= 8:
            color = "#22c55e"
        elif score >= 6:
            color = "#eab308"
        elif score >= 4:
            color = "#f97316"
        else:
            color = "#ef4444"
        self.score_label.configure(text_color=color)
    
    def _on_platform_change(self, value):
        """Handle platform selection change."""
        if value.lower() == "none":
            self.username_frame.pack_forget()
        else:
            self.username_frame.pack(fill="x", pady=(0, 15), after=self.platform_menu)
    
    def _browse_cover(self):
        """Open file browser for cover image."""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.webp *.bmp"),
            ("All files", "*.*")
        ]
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            self.cover_entry.delete(0, "end")
            self.cover_entry.insert(0, filepath)
            self.cover_status.configure(text=f"Selected: {Path(filepath).name}", text_color="green")
    
    def _apply_palette(self, palette_name: str):
        """Apply a color palette to the color buttons."""
        if palette_name in COLOR_PALETTES:
            palette = COLOR_PALETTES[palette_name]
            self.bg_color_btn.set_color(palette["background"])
            self.primary_color_btn.set_color(palette["primary"])
            self.secondary_color_btn.set_color(palette["secondary"])
            self.accent_color_btn.set_color(palette["accent"])
    
    def _get_style(self) -> CardStyle:
        """Build CardStyle from current UI settings."""
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            radius = int(self.radius_entry.get())
        except ValueError:
            width, height, radius = 1200, 675, 20
        
        bg_rgb = hex_to_rgb(self.bg_color_btn.get_color())
        
        palette_name = self.palette_var.get()
        theme = palette_name.lower() if palette_name in THEMED_PALETTES else None
        
        return CardStyle(
            width=width,
            height=height,
            background_color=(*bg_rgb, 255),
            primary_color=hex_to_rgb(self.primary_color_btn.get_color()),
            secondary_color=hex_to_rgb(self.secondary_color_btn.get_color()),
            accent_color=hex_to_rgb(self.accent_color_btn.get_color()),
            corner_radius=radius,
            theme=theme
        )
    
    def _validate_inputs(self) -> bool:
        """Validate user inputs."""
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror("Validation Error", "Please enter a title.")
            return False
        
        review = self.review_text.get("1.0", "end").strip()
        if not review:
            messagebox.showerror("Validation Error", "Please enter a review.")
            return False
        
        return True
    
    def _generate_card(self):
        """Generate the review card."""
        if not self._validate_inputs():
            return
        
        self.status_label.configure(text="Generating...", text_color="yellow")
        self.generate_btn.configure(state="disabled")
        self.update()
        
        try:
            # Get values
            title = self.title_entry.get().strip()
            score = self.score_var.get()
            review = self.review_text.get("1.0", "end").strip()
            content_type = self.content_type_var.get()
            
            platform = self.platform_var.get().lower()
            username = self.username_entry.get().strip()
            
            cover = self.cover_entry.get().strip() or None
            
            style = self._get_style()
            
            # Generate card
            self.generated_card = create_review_card(
                title=title,
                score=score,
                review_text=review,
                content_type=content_type,
                cover_image=cover,
                platform=platform,
                platform_username=username,
                style=style
            )
            
            # Update preview
            self._update_preview()
            
            self.status_label.configure(text="Card generated successfully!", text_color="green")
            self.save_btn.configure(state="normal")
            
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")
            messagebox.showerror("Generation Error", str(e))
        finally:
            self.generate_btn.configure(state="normal")
    
    def _update_preview(self):
        """Update the preview display with the generated card."""
        if not self.generated_card:
            return
        
        # Get available space
        self.preview_frame.update()
        max_width = self.preview_frame.winfo_width() - 40
        max_height = self.preview_frame.winfo_height() - 40
        
        if max_width <= 0 or max_height <= 0:
            max_width, max_height = 800, 450
        
        # Calculate scaled size
        card_ratio = self.generated_card.width / self.generated_card.height
        frame_ratio = max_width / max_height
        
        if card_ratio > frame_ratio:
            new_width = max_width
            new_height = int(max_width / card_ratio)
        else:
            new_height = max_height
            new_width = int(max_height * card_ratio)
        
        # Resize for preview
        preview_image = self.generated_card.copy()
        preview_image = preview_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        self.preview_photo = ImageTk.PhotoImage(preview_image)
        
        # Update label
        self.preview_label.configure(image=self.preview_photo, text="")
    
    def _save_card(self):
        """Save the generated card to file."""
        if not self.generated_card:
            messagebox.showwarning("No Card", "Please generate a card first.")
            return
        
        # Default filename from title
        title = self.title_entry.get().strip()
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        default_name = f"{safe_title.replace(' ', '_')}_review.png" if safe_title else "review_card.png"
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_name,
            initialdir="output",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                self.generated_card.save(filepath)
                self.status_label.configure(text=f"Saved: {Path(filepath).name}", text_color="green")
                messagebox.showinfo("Success", f"Card saved to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))


def main():
    """Run the application."""
    app = ReviewCardApp()
    app.mainloop()


if __name__ == "__main__":
    main()
