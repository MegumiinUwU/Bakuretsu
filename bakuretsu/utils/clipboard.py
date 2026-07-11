"""Copy rendered cards to the system clipboard (Windows).

Puts both a CF_DIB bitmap (understood by nearly every app) and a
registered "PNG" format (used by Discord, browsers, and modern apps,
keeps transparency) on the clipboard in one shot.
"""

from __future__ import annotations

import io
import sys

from PIL import Image


def is_supported() -> bool:
    return sys.platform == "win32"


def copy_image(image: Image.Image) -> bool:
    """Copy a PIL image to the clipboard. Returns True on success."""
    if not is_supported():
        return False

    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
    kernel32.GlobalAlloc.argtypes = (wintypes.UINT, ctypes.c_size_t)
    kernel32.GlobalLock.restype = wintypes.LPVOID
    kernel32.GlobalLock.argtypes = (wintypes.HGLOBAL,)
    kernel32.GlobalUnlock.argtypes = (wintypes.HGLOBAL,)
    user32.SetClipboardData.restype = wintypes.HANDLE
    user32.SetClipboardData.argtypes = (wintypes.UINT, wintypes.HANDLE)

    # CF_DIB: BMP file minus its 14-byte header
    with io.BytesIO() as buffer:
        image.convert("RGB").save(buffer, "BMP")
        dib_data = buffer.getvalue()[14:]
    # PNG: full file, keeps alpha
    with io.BytesIO() as buffer:
        image.save(buffer, "PNG")
        png_data = buffer.getvalue()

    CF_DIB = 8
    GMEM_MOVEABLE = 0x0002
    png_format = user32.RegisterClipboardFormatW("PNG")

    if not user32.OpenClipboard(None):
        return False
    try:
        user32.EmptyClipboard()
        for clip_format, data in ((CF_DIB, dib_data), (png_format, png_data)):
            if not clip_format:
                continue
            handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
            if not handle:
                return False
            pointer = kernel32.GlobalLock(handle)
            ctypes.memmove(pointer, data, len(data))
            kernel32.GlobalUnlock(handle)
            user32.SetClipboardData(clip_format, handle)
        return True
    finally:
        user32.CloseClipboard()
