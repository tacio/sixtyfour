"""Compiling the UFO into shippable font files."""

from __future__ import annotations

import contextlib
import os
from pathlib import Path

import ufo2ft
import ufoLib2
from fontTools.colorLib.builder import ColorPaletteType, buildCOLR, buildCPAL
from fontTools.ttLib import TTFont

from . import ufobuild
from .spec import TABLE

#: Palette index 0xFFFF means "the text foreground colour" rather than a stored
#: colour. The empty and solid tiers use it, so they follow the surrounding text
#: and stay visible on a dark background instead of being locked to black.
FOREGROUND = 0xFFFF

BLUE = 0
RED = 1

#: (r, g, b, a) in 0..1. Two palettes: the second lightens both hues for dark UI,
#: where the light-background blue and red go muddy.
PALETTES = {
    "light": [(0x1B / 255, 0x4F / 255, 0xD8 / 255, 1.0), (0xD4 / 255, 0x2A / 255, 0x20 / 255, 1.0)],
    "dark": [(0x7F / 255, 0xA8 / 255, 1.0, 1.0), (1.0, 0x7A / 255, 0x6E / 255, 1.0)],
}

FILL_PALETTE_INDEX = {
    "none": FOREGROUND,
    "solid": FOREGROUND,
    "dots": BLUE,
    "lines": RED,
}


@contextlib.contextmanager
def reproducible():
    """Pin the build clock.

    fontTools reads SOURCE_DATE_EPOCH for head.modified and falls back to the
    current time. Since the built fonts are committed, that fallback would show
    every rebuild as a binary change even when no outline moved. An epoch
    already in the environment wins, so reproducible-build systems stay in
    charge.
    """
    key = "SOURCE_DATE_EPOCH"
    if key in os.environ:
        yield
        return
    os.environ[key] = ufobuild.BUILD_EPOCH
    try:
        yield
    finally:
        del os.environ[key]


def _compile(ufo: ufoLib2.Font, *, cff: bool) -> TTFont:
    compile_fn = ufo2ft.compileOTF if cff else ufo2ft.compileTTF
    return compile_fn(ufo, useProductionNames=False, removeOverlaps=False)


def attach_color(font: TTFont, layers: dict[str, str]) -> None:
    """Add COLR v0 and CPAL, leaving the base outlines in place.

    COLR v1 would let us do gradients we do not want, at the cost of dropping
    support for every renderer older than about 2022. v0 is flat colour layers,
    which is exactly the requirement, and has been supported for a decade.

    The base glyphs keep their full hatched outlines, so a renderer with no COLR
    support draws the monochrome artwork rather than nothing.
    """
    color_glyphs = {
        entry.glyph_name: [(layers[entry.glyph_name], FILL_PALETTE_INDEX[entry.fill])]
        for entry in TABLE
    }
    font["COLR"] = buildCOLR(color_glyphs, version=0, glyphMap=font.getReverseGlyphMap())
    font["CPAL"] = buildCPAL(
        [PALETTES["light"], PALETTES["dark"]],
        paletteTypes=[
            ColorPaletteType.USABLE_WITH_LIGHT_BACKGROUND,
            ColorPaletteType.USABLE_WITH_DARK_BACKGROUND,
        ],
    )


def _save(font: TTFont, path: Path, flavor: str | None = None) -> Path:
    font.flavor = flavor
    path.parent.mkdir(parents=True, exist_ok=True)
    font.save(path)
    return path


def build_color(out_dir: Path, stem: str = "SixtyFour-Regular") -> list[Path]:
    """The colour font: COLR v0 + CPAL, with monochrome fallback outlines."""
    # head.modified is stamped when the file is written, not when it is compiled,
    # so the clock has to stay pinned across the saves as well.
    with reproducible():
        ufo = ufobuild.build_ufo(ufobuild.FAMILY_NAME)
        layers = ufobuild.add_color_layers(ufo)
        ttf = _compile(ufo, cff=False)
        attach_color(ttf, layers)
        return [
            _save(ttf, out_dir / f"{stem}.ttf"),
            _save(ttf, out_dir / f"{stem}.woff2", "woff2"),
            _save(ttf, out_dir / f"{stem}.woff", "woff"),
        ]


def build_mono(out_dir: Path, stem: str = "SixtyFourMono-Regular") -> list[Path]:
    """The monochrome font: no COLR, no CPAL, nothing to fall back from.

    Also shipped as CFF. COLR in a CFF font is legal but poorly supported in
    practice, so the .otf is monochrome only and the .ttf carries the colour.
    """
    with reproducible():
        ufo = ufobuild.build_ufo(ufobuild.MONO_FAMILY_NAME)
        ttf = _compile(ufo, cff=False)
        otf = _compile(ufobuild.build_ufo(ufobuild.MONO_FAMILY_NAME), cff=True)
        return [
            _save(ttf, out_dir / f"{stem}.ttf"),
            _save(ttf, out_dir / f"{stem}.woff2", "woff2"),
            _save(otf, out_dir / f"{stem}.otf"),
        ]
