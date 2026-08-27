"""Assembling the UFO source that both fonts are compiled from."""

from __future__ import annotations

import ufoLib2

from . import geometry as g
from . import glyphs
from .spec import TABLE, PAD_CHAR, URLSAFE_ALIASES

FAMILY_NAME = "Sixty Four"
MONO_FAMILY_NAME = "Sixty Four Mono"
STYLE_NAME = "Regular"
VERSION_MAJOR = 1
VERSION_MINOR = 0

UPEM = 1000
ADVANCE = 1000
ASCENDER = 800
DESCENDER = -200

NOTDEF = ".notdef"
SPACE = "space"
PADDING = "equal"

DESCRIPTION = (
    "Renders base64 as 64 symbols a person can identify, describe out loud, "
    "and compare by eye. Every symbol is encoded twice over -- by colour and by "
    "hatch -- so it survives greyscale printing and colour blindness."
)
DESIGNER = "Tacio Medeiros"
LICENSE = "SIL Open Font License 1.1"
LICENSE_URL = "https://openfontlicense.org"


def _info(font: ufoLib2.Font, family: str) -> None:
    info = font.info
    info.familyName = family
    info.styleName = STYLE_NAME
    info.unitsPerEm = UPEM
    info.versionMajor = VERSION_MAJOR
    info.versionMinor = VERSION_MINOR

    info.ascender = ASCENDER
    info.descender = DESCENDER
    info.capHeight = ASCENDER
    info.xHeight = ASCENDER

    # Keep the three competing vertical-metric schemes saying the same thing,
    # so line height does not shift between Windows, macOS and browsers.
    info.openTypeHheaAscender = ASCENDER
    info.openTypeHheaDescender = DESCENDER
    info.openTypeHheaLineGap = 0
    info.openTypeOS2TypoAscender = ASCENDER
    info.openTypeOS2TypoDescender = DESCENDER
    info.openTypeOS2TypoLineGap = 0
    info.openTypeOS2WinAscent = ASCENDER
    info.openTypeOS2WinDescent = -DESCENDER
    info.openTypeOS2Selection = [7]  # USE_TYPO_METRICS

    info.openTypeOS2WidthClass = 5
    info.openTypeOS2WeightClass = 400
    info.openTypeOS2VendorID = "64ID"
    info.openTypeOS2Type = []  # installable embedding

    # Latin Text / monospaced proportion. Declaring the PANOSE symbol family
    # instead would be more literally true but hides the font from the font
    # pickers of most terminals and editors, which is where it is wanted.
    info.openTypeOS2Panose = [2, 0, 5, 9, 0, 0, 0, 0, 0, 0]
    info.postscriptIsFixedPitch = True
    info.postscriptUnderlineThickness = 50
    info.postscriptUnderlinePosition = -150

    info.openTypeNameDesigner = DESIGNER
    info.openTypeNameDescription = DESCRIPTION
    info.openTypeNameLicense = LICENSE
    info.openTypeNameLicenseURL = LICENSE_URL
    info.copyright = f"Copyright (c) {DESIGNER}. Licensed under the {LICENSE}."


def _draw(font: ufoLib2.Font, name: str, path, unicodes: list[int] | None = None):
    glyph = font.newGlyph(name)
    glyph.width = ADVANCE
    glyph.unicodes = unicodes or []
    if path is not None:
        g.to_font_space(path).draw(glyph.getPen())
    return glyph


def build_ufo(family: str = FAMILY_NAME) -> ufoLib2.Font:
    """The shared source: 64 data glyphs, their colour layers, and the extras."""
    font = ufoLib2.Font()
    _info(font, family)

    _draw(font, NOTDEF, glyphs.notdef())
    _draw(font, SPACE, None, [0x0020, 0x00A0])
    _draw(font, PADDING, glyphs.padding(), [ord(PAD_CHAR)])

    # URL-safe base64 swaps '+' for '-' and '/' for '_'. Mapping both spellings
    # onto one glyph means JWTs and file-safe encodings just work.
    extra_codepoints: dict[str, list[int]] = {}
    for alias, standard in URLSAFE_ALIASES.items():
        extra_codepoints.setdefault(standard, []).append(ord(alias))

    for entry in TABLE:
        codepoints = [entry.codepoint] + extra_codepoints.get(entry.char, [])
        _draw(font, entry.glyph_name, glyphs.build_entry(entry), codepoints)

    return font


def add_color_layers(font: ufoLib2.Font) -> dict[str, str]:
    """Add one composite per data glyph for COLR to paint.

    A COLR layer has to name a glyph. Rather than duplicating outlines, each
    layer glyph is a single component pointing back at the base glyph, which
    costs a handful of bytes. Referencing the base glyph from its own COLR
    record would work in most renderers but is needless risk.
    """
    mapping = {}
    for entry in TABLE:
        layer_name = f"{entry.glyph_name}.clr"
        glyph = font.newGlyph(layer_name)
        glyph.width = ADVANCE
        glyph.getPen().addComponent(entry.glyph_name, (1, 0, 0, 1, 0, 0))
        mapping[entry.glyph_name] = layer_name
    return mapping
