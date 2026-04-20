#!/usr/bin/env python3
"""Generate favicons for Transity Logistics Services.

Output directory: same as this script.
Logo: rounded dark square with amber 'T' serif glyph and underline accent.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

INK = (14, 14, 13, 255)
AMBER = (232, 165, 59, 255)
HERE = Path(__file__).parent

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    "/Library/Fonts/Georgia.ttf",
    "/System/Library/Fonts/Times.ttc",
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size, index=0)
            except Exception:
                continue
    return ImageFont.load_default()


def make_icon(size: int, *, transparent_bg: bool = False, padding_ratio: float = 0.0) -> Image.Image:
    """Draw the T mark at the given size."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    pad = int(size * padding_ratio)
    inner = size - 2 * pad

    # rounded-square background
    if not transparent_bg:
        radius = max(2, int(inner * 0.18))
        d.rounded_rectangle(
            [pad, pad, pad + inner - 1, pad + inner - 1],
            radius=radius,
            fill=INK,
        )

    # T glyph
    glyph_size = int(inner * 0.72)
    font = load_font(glyph_size)
    bbox = d.textbbox((0, 0), "T", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = pad + (inner - tw) / 2 - bbox[0]
    ty = pad + (inner - th) / 2 - bbox[1] - inner * 0.04
    d.text((tx, ty), "T", font=font, fill=AMBER)

    # amber underline accent
    bar_h = max(1, int(inner * 0.06))
    bar_w = int(inner * 0.36)
    bar_x = pad + (inner - bar_w) / 2
    bar_y = pad + inner - int(inner * 0.16)
    d.rounded_rectangle(
        [bar_x, bar_y, bar_x + bar_w, bar_y + bar_h],
        radius=bar_h // 2,
        fill=AMBER,
    )
    return img


def make_maskable(size: int) -> Image.Image:
    """Android maskable icon: edge-to-edge ink, centered T with safe padding."""
    img = Image.new("RGBA", (size, size), INK)
    d = ImageDraw.Draw(img)
    inner = int(size * 0.64)
    pad = (size - inner) // 2

    glyph_size = int(inner * 0.88)
    font = load_font(glyph_size)
    bbox = d.textbbox((0, 0), "T", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = pad + (inner - tw) / 2 - bbox[0]
    ty = pad + (inner - th) / 2 - bbox[1] - inner * 0.04
    d.text((tx, ty), "T", font=font, fill=AMBER)

    bar_h = max(2, int(inner * 0.07))
    bar_w = int(inner * 0.4)
    bar_x = pad + (inner - bar_w) / 2
    bar_y = pad + inner - int(inner * 0.1)
    d.rounded_rectangle(
        [bar_x, bar_y, bar_x + bar_w, bar_y + bar_h],
        radius=bar_h // 2,
        fill=AMBER,
    )
    return img


def main() -> None:
    # Render PNGs at 2x then downscale (supersampling) for cleaner edges
    def rendered(sz):
        return make_icon(sz * 2).resize((sz, sz), Image.LANCZOS)

    sizes = {
        "favicon-16x16.png": 16,
        "favicon-32x32.png": 32,
        "favicon-48x48.png": 48,
        "favicon-96x96.png": 96,
        "apple-touch-icon.png": 180,
        "android-chrome-192x192.png": 192,
        "android-chrome-512x512.png": 512,
        "og-cover-mark.png": 512,
    }
    for name, sz in sizes.items():
        rendered(sz).save(HERE / name, optimize=True)
        print(f"wrote {name} ({sz}×{sz})")

    # ICO with multiple embedded sizes
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
    ico_base = make_icon(256)
    ico_base.save(HERE / "favicon.ico", sizes=ico_sizes)
    print("wrote favicon.ico (multi-size)")

    # Maskable for PWA
    make_maskable(512).save(HERE / "maskable-512.png", optimize=True)
    print("wrote maskable-512.png")


if __name__ == "__main__":
    main()
