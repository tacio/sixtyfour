"""Turning 16 silhouettes into 64 glyphs.

Every glyph carries the same outline band, whatever its fill; only the interior
changes. That keeps the silhouette readable across all four tiers, and makes the
tier itself a property of the interior alone:

    none    outline only        -- the background shows through, so it works on
                                   any background colour rather than assuming white
    solid   outline + interior
    dots    outline + dot grid clipped into the interior
    lines   outline + diagonal hatch clipped into the interior
"""

from __future__ import annotations

from functools import lru_cache

import pathops

from . import geometry as g
from . import shapes, texture
from .spec import TABLE, Entry


@lru_cache(maxsize=None)
def _parts(name: str) -> tuple[pathops.Path, pathops.Path, pathops.Path]:
    """(outline band, interior, texture field) for one silhouette."""
    sil = shapes.silhouette(name)
    band = g.stroke_band(sil, shapes.OUTLINE_WIDTH)
    interior = g.simplify(g.difference(sil, band))
    field = g.inset(interior, shapes.TEXTURE_INSET)
    return band, interior, field


@lru_cache(maxsize=None)
def build(name: str, fill: str) -> pathops.Path:
    """The finished design-space geometry for one of the 64 glyphs."""
    band, interior, field = _parts(name)
    if fill == "none":
        body = pathops.Path()
    elif fill == "solid":
        body = interior
    elif fill == "dots":
        body = texture.dots(field)
    elif fill == "lines":
        body = texture.lines(field)
    else:
        raise ValueError(f"unknown fill {fill!r}")
    return g.simplify(g.union(band, body))


def build_entry(entry: Entry) -> pathops.Path:
    return build(entry.symbol, entry.fill)


def build_all() -> dict[str, pathops.Path]:
    """Every data glyph, keyed by glyph name (``cross.none`` ...)."""
    return {entry.glyph_name: build_entry(entry) for entry in TABLE}


# --- glyphs that are not one of the 64 ---------------------------------------


def padding() -> pathops.Path:
    """The '=' padding mark.

    Deliberately unlike all 64: a low, hollow, wide bar. It reads as "slot with
    no data in it" and shares no silhouette with any symbol, so padding can
    never be mistaken for a value.
    """
    outer = g.rounded_rect(240, 560, 760, 700, 70)
    return g.simplify(g.stroke_band(outer, 54.0))


def notdef() -> pathops.Path:
    """A hollow box with a diagonal, so malformed base64 is visible as such."""
    outer = g.rounded_rect(180, 150, 820, 850, 20)
    box = g.stroke_band(outer, 60.0)
    slash = g.stroke_band(g.from_d("M 260 780 L 740 220"), 52.0)
    return g.simplify(g.union(box, slash))
