"""Rasterising the built font, for specimens and for the legibility tests."""

from __future__ import annotations

import io
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from .spec import BASE64_ALPHABET, FILLS, SILHOUETTES, TABLE


def load(font_path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(font_path), size)


def glyph_bitmap(font_path: Path, char: str, size: int, color: bool = False) -> Image.Image:
    """One character on a square white ground, at `size` pixels per em."""
    font = load(font_path, size)
    image = Image.new("RGBA" if color else "L", (size, size), (255, 255, 255, 255) if color else 255)
    draw = ImageDraw.Draw(image)
    # Pillow's default anchor puts the ascender at y=0. The design canvas spans
    # y in [-200, 800], i.e. ascender down to descender, so it lands exactly in
    # a size x size cell with no offset.
    draw.text(
        (0, 0),
        char,
        font=font,
        fill=(0, 0, 0, 255) if color else 0,
        embedded_color=color,
    )
    return image


def ink(font_path: Path, char: str, size: int) -> float:
    """Fraction of the cell covered, 0..1. Used to check the hatch ink ramp."""
    bitmap = glyph_bitmap(font_path, char, size).convert("L")
    pixels = list(bitmap.getdata())
    return 1.0 - (sum(pixels) / (255.0 * len(pixels)))


def contact_sheet(
    font_path: Path, cell: int = 96, color: bool = True, pad: int = 10
) -> Image.Image:
    """All 64 symbols as a 16-wide grid: one row per fill, one column per shape."""
    label_w, header_h = 96, 34
    width = label_w + 16 * (cell + pad) + pad
    height = header_h + 4 * (cell + pad + 16) + pad
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    small = ImageFont.load_default(12)

    for col, name in enumerate(SILHOUETTES):
        x = label_w + col * (cell + pad)
        draw.text((x, 12), name[:9], font=small, fill="#555555")

    for row, fill in enumerate(FILLS):
        y = header_h + row * (cell + pad + 16)
        draw.text((8, y + cell // 2), fill, font=small, fill="#555555")
        for col in range(16):
            char = BASE64_ALPHABET[row * 16 + col]
            x = label_w + col * (cell + pad)
            sheet.paste(glyph_bitmap(font_path, char, cell, color).convert("RGB"), (x, y))
            draw.text((x + 2, y + cell + 1), f"{char} {row*16+col}", font=small, fill="#999999")
    return sheet


def sample_line(font_path: Path, text: str, size: int, color: bool = True) -> Image.Image:
    """A run of text set in the font, for eyeballing rhythm and small sizes."""
    font = load(font_path, size)
    width = size * len(text)
    image = Image.new("RGB", (width, int(size * 1.25)), "white")
    ImageDraw.Draw(image).text(
        (0, 0), text, font=font, fill=(0, 0, 0), embedded_color=color
    )
    return image


def _with_palette(font_path: Path, index: int) -> io.BytesIO:
    """A copy of the font with CPAL palette `index` moved to the front.

    FreeType renders palette 0 and offers no way to pick another, so seeing what
    the dark palette actually looks like means promoting it first.
    """
    font = TTFont(font_path)
    palettes = font["CPAL"].palettes
    palettes.insert(0, palettes.pop(index))
    buffer = io.BytesIO()
    font.save(buffer)
    buffer.seek(0)
    return buffer


def grounds_sheet(font_path: Path, size: int = 54, pad: int = 22) -> Image.Image:
    """The same symbols on a light and a dark ground, side by side.

    The empty and solid tiers paint with the text colour, so they invert with
    the ground; the dotted and striped tiers move to the second CPAL palette.
    Showing both at once is the only way a reader in one theme can see the other.
    """
    sample = "".join(BASE64_ALPHABET[FILLS.index(f) * 16 + i] for i in range(4) for f in FILLS)
    grounds = [
        ("Light ground", ImageFont.truetype(str(font_path), size), "#FBFAF7", "#1A1C22"),
        ("Dark ground", ImageFont.truetype(_with_palette(font_path, 1), size), "#121419", "#ECEBE6"),
    ]
    label = ImageFont.load_default(13)
    row_h = size + 40
    width = size * len(sample) + pad * 2
    sheet = Image.new("RGB", (width, row_h * len(grounds)), "#FFFFFF")
    draw = ImageDraw.Draw(sheet)

    y = 0
    for name, font, background, foreground in grounds:
        draw.rectangle([0, y, width, y + row_h], fill=background)
        draw.text((pad, y + 8), name.upper(), font=label, fill=foreground)
        draw.text((pad, y + 26), sample, font=font, fill=foreground, embedded_color=True)
        y += row_h
    return sheet
