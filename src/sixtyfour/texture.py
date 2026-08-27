"""Hatch textures: diagonal stripes and a staggered dot grid.

The four fills form an ink ramp -- empty, lines, dots, solid -- so that the
tiers stay tellable apart with the colour thrown away, which is the whole point
of carrying a hatch at all.

Density is driven by *achieved coverage of the area actually available*, not by
a fixed pitch. A cross or a crescent leaves only a narrow channel once its
outline and inset are taken out; at the pitch that suits a circle, such a shape
catches one or two marks and ends up looking like the empty tier. When coverage
falls short the grid is refined and retried.

Both grids are anchored to the centre of the canvas rather than to each shape's
bounding box, so the texture rhythm lines up across adjacent glyphs in a run of
base64 instead of jittering from cell to cell.
"""

from __future__ import annotations

import math
from functools import lru_cache

import pathops

from . import geometry as g

#: 45 degrees. Diagonal reads as "hatch"; horizontal reads as "lines of text".
STRIPE_ANGLE = 45.0
STRIPE_PITCH = 132.0
STRIPE_WIDTH = 54.0
STRIPE_TARGET = 0.40

DOT_PITCH = 158.0
DOT_RADIUS = 66.0
DOT_TARGET = 0.60

#: Clipped fragments smaller than this fraction of a whole mark are dropped --
#: at text size they stop reading as texture and start reading as dirt.
MIN_FRAGMENT = 0.30

#: Refinement stops once coverage reaches this fraction of the target.
COVERAGE_TOLERANCE = 0.80
REFINE_FACTOR = 0.62
MAX_REFINEMENTS = 4


def _merge(parts: list[pathops.Path]) -> pathops.Path:
    """Draw many non-overlapping shapes into one path.

    The marks in a grid never touch, so a union here would be hundreds of
    boolean ops to produce exactly what concatenation already gives.
    """
    merged = pathops.Path()
    pen = merged.getPen()
    for part in parts:
        part.draw(pen)
    return merged


def drop_small_contours(path: pathops.Path, min_area: float) -> pathops.Path:
    """Keep only contours enclosing at least `min_area`."""
    kept = pathops.Path()
    pen = kept.getPen()
    for contour in path.contours:
        if abs(contour.area) >= min_area:
            contour.draw(pen)
    return kept


@lru_cache(maxsize=64)
def stripe_field(pitch: float, width: float, angle: float = STRIPE_ANGLE) -> pathops.Path:
    """Parallel bars covering the whole canvas, centred on the canvas centre."""
    centre = g.CANVAS / 2
    # The canvas diagonal, so bars still cover the corners once rotated.
    reach = g.CANVAS * math.sqrt(2)
    count = int(reach / pitch) + 2
    rad = math.radians(angle)
    bars = []
    for i in range(-count, count + 1):
        offset = i * pitch
        # Step perpendicular to the bar direction.
        cx = centre - math.sin(rad) * offset
        cy = centre + math.cos(rad) * offset
        bars.append(g.rotated_rect(cx, cy, reach, width, angle))
    return _merge(bars)


@lru_cache(maxsize=64)
def dot_field(pitch: float, radius: float) -> pathops.Path:
    """A staggered (hexagonal) grid of circles covering the whole canvas."""
    centre = g.CANVAS / 2
    row_step = pitch * math.sqrt(3) / 2
    rows = int(g.CANVAS / row_step) + 3
    cols = int(g.CANVAS / pitch) + 3
    dots = []
    for row in range(-rows, rows + 1):
        cy = centre + row * row_step
        # Offset alternate rows by half a pitch for hexagonal packing.
        shift = (pitch / 2) if row % 2 else 0.0
        for col in range(-cols, cols + 1):
            dots.append(g.circle(centre + col * pitch + shift, cy, radius))
    return _merge(dots)


def _clip(field: pathops.Path, grid: pathops.Path, whole_mark_area: float) -> pathops.Path:
    clipped = g.intersection(grid, field)
    return drop_small_contours(clipped, whole_mark_area * MIN_FRAGMENT)


def _refine(field: pathops.Path, make_grid, mark_area, target: float) -> pathops.Path:
    """Tighten the grid until it covers `target` of the field, or we run out."""
    if not field.area:
        return pathops.Path()
    scale = 1.0
    best = pathops.Path()
    for _ in range(MAX_REFINEMENTS + 1):
        result = _clip(field, make_grid(scale), mark_area(scale))
        if result.area > best.area:
            best = result
        if result.area >= target * COVERAGE_TOLERANCE * field.area:
            return g.simplify(result)
        scale *= REFINE_FACTOR
    return g.simplify(best)


def lines(field: pathops.Path) -> pathops.Path:
    """Diagonal hatching clipped into `field`."""
    return _refine(
        field,
        lambda s: stripe_field(STRIPE_PITCH * s, STRIPE_WIDTH * s),
        # A "whole mark" for a stripe is a square of its own width; anything
        # shorter than that is a corner speck rather than a line.
        lambda s: (STRIPE_WIDTH * s) ** 2,
        STRIPE_TARGET,
    )


def dots(field: pathops.Path) -> pathops.Path:
    """A dot grid clipped into `field`."""
    return _refine(
        field,
        lambda s: dot_field(DOT_PITCH * s, DOT_RADIUS * s),
        lambda s: math.pi * (DOT_RADIUS * s) ** 2,
        DOT_TARGET,
    )
