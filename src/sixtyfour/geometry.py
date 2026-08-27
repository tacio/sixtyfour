"""Path algebra on top of skia-pathops.

Everything the font contains is a closed, filled contour. Strokes and textures
are baked into real geometry here so that neither the SVGs nor the font need a
stroke, a <pattern>, or a clipPath -- constructs that font formats cannot carry
and that picosvg silently discards.

All coordinates in this module are in *design space*: a 1000x1000 box with the
origin top-left and y pointing down, matching SVG. The flip to font space
happens once, in `to_font_space`.
"""

from __future__ import annotations

import math

import pathops
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path

CANVAS = 1000.0

#: y_font = FONT_ASCENDER - y_design, putting the canvas at y in [-200, 800].
FONT_ASCENDER = 800.0

#: Flatness for conic -> quadratic conversion, in design units.
CONIC_TOLERANCE = 0.05


def from_d(d: str) -> pathops.Path:
    """Parse an SVG path 'd' string into a path."""
    path = pathops.Path()
    parse_path(d, path.getPen())
    return path


def to_d(path: pathops.Path) -> str:
    """Serialise a path back to an SVG 'd' string."""
    pen = SVGPathPen(glyphSet=None, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    path.draw(pen)
    return pen.getCommands()


def transformed(path: pathops.Path, matrix: tuple[float, ...]) -> pathops.Path:
    """Apply a 6-tuple affine transform, returning a new path."""
    out = pathops.Path()
    path.draw(TransformPen(out.getPen(), matrix))
    return out


def translated(path: pathops.Path, dx: float, dy: float) -> pathops.Path:
    return transformed(path, (1, 0, 0, 1, dx, dy))


def to_font_space(path: pathops.Path) -> pathops.Path:
    """Flip design space (y down) to font space (y up)."""
    return transformed(path, (1, 0, 0, -1, 0, FONT_ASCENDER))


# --- boolean algebra ---------------------------------------------------------


def union(*paths: pathops.Path) -> pathops.Path:
    result = pathops.Path()
    for path in paths:
        if path.area:
            result = pathops.op(result, path, pathops.PathOp.UNION)
    return result


def difference(a: pathops.Path, b: pathops.Path) -> pathops.Path:
    return pathops.op(a, b, pathops.PathOp.DIFFERENCE)


def intersection(a: pathops.Path, b: pathops.Path) -> pathops.Path:
    return pathops.op(a, b, pathops.PathOp.INTERSECTION)


def simplify(path: pathops.Path) -> pathops.Path:
    """Remove self-overlap so the result fills identically under any fill rule."""
    return pathops.simplify(path, fix_winding=True)


# --- strokes and insets ------------------------------------------------------


def stroke_band(path: pathops.Path, width: float) -> pathops.Path:
    """The ring you get by stroking `path`, as a filled region.

    Round joins throughout: at text size, mitres on a star or a cross spike turn
    into isolated specks that read as noise.
    """
    band = pathops.Path(path)
    band.stroke(width, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4.0)
    # Skia's stroker emits conics for round joins; nothing downstream of here --
    # not the boolean ops, not the SVG writer, not glyf -- can represent one.
    band.convertConicsToQuads(CONIC_TOLERANCE)
    return simplify(band)


def inset(path: pathops.Path, amount: float) -> pathops.Path:
    """Shrink a filled region by `amount` on every side.

    Implemented as `region - stroke(region, 2*amount)`: the stroke straddles the
    boundary, so half of it lies inside, and removing it eats exactly `amount`.
    """
    if amount <= 0:
        return pathops.Path(path)
    return simplify(difference(path, stroke_band(path, amount * 2.0)))


# --- primitives --------------------------------------------------------------

#: Cubic circle constant: control-point offset for a quarter arc.
_KAPPA = 0.5522847498307936


def circle(cx: float, cy: float, r: float) -> pathops.Path:
    """A circle as four cubic segments."""
    k = r * _KAPPA
    path = pathops.Path()
    pen = path.getPen()
    pen.moveTo((cx, cy - r))
    pen.curveTo((cx + k, cy - r), (cx + r, cy - k), (cx + r, cy))
    pen.curveTo((cx + r, cy + k), (cx + k, cy + r), (cx, cy + r))
    pen.curveTo((cx - k, cy + r), (cx - r, cy + k), (cx - r, cy))
    pen.curveTo((cx - r, cy - k), (cx - k, cy - r), (cx, cy - r))
    pen.closePath()
    return path


def ellipse(cx: float, cy: float, rx: float, ry: float) -> pathops.Path:
    """An axis-aligned ellipse."""
    return transformed(circle(0, 0, 1.0), (rx, 0, 0, ry, cx, cy))


def polygon(points: list[tuple[float, float]]) -> pathops.Path:
    path = pathops.Path()
    pen = path.getPen()
    pen.moveTo(points[0])
    for point in points[1:]:
        pen.lineTo(point)
    pen.closePath()
    return path


def rounded_rect(x0: float, y0: float, x1: float, y1: float, r: float) -> pathops.Path:
    """An axis-aligned rectangle with uniformly rounded corners."""
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    k = r * _KAPPA
    path = pathops.Path()
    pen = path.getPen()
    pen.moveTo((x0 + r, y0))
    pen.lineTo((x1 - r, y0))
    pen.curveTo((x1 - r + k, y0), (x1, y0 + r - k), (x1, y0 + r))
    pen.lineTo((x1, y1 - r))
    pen.curveTo((x1, y1 - r + k), (x1 - r + k, y1), (x1 - r, y1))
    pen.lineTo((x0 + r, y1))
    pen.curveTo((x0 + r - k, y1), (x0, y1 - r + k), (x0, y1 - r))
    pen.lineTo((x0, y0 + r))
    pen.curveTo((x0, y0 + r - k), (x0 + r - k, y0), (x0 + r, y0))
    pen.closePath()
    return path


def rotated_rect(cx: float, cy: float, length: float, width: float, degrees: float) -> pathops.Path:
    """A rectangle of `length` x `width` centred on (cx, cy), rotated."""
    rad = math.radians(degrees)
    ux, uy = math.cos(rad), math.sin(rad)
    vx, vy = -uy, ux
    hl, hw = length / 2, width / 2
    return polygon(
        [
            (cx + ux * hl + vx * hw, cy + uy * hl + vy * hw),
            (cx + ux * hl - vx * hw, cy + uy * hl - vy * hw),
            (cx - ux * hl - vx * hw, cy - uy * hl - vy * hw),
            (cx - ux * hl + vx * hw, cy - uy * hl + vy * hw),
        ]
    )


# --- normalisation -----------------------------------------------------------


def fit_into(
    path: pathops.Path, box: float, centre: float = CANVAS / 2, nudge_y: float = 0.0
) -> pathops.Path:
    """Scale a silhouette so its longest side is `box`, then centre it.

    `nudge_y` shifts the result in design space afterwards, for shapes whose
    optical centre is not their geometric one (a flame, a mushroom).
    """
    x0, y0, x1, y1 = path.bounds
    span = max(x1 - x0, y1 - y0)
    factor = box / span
    out = transformed(path, (factor, 0, 0, factor, 0, 0))
    x0, y0, x1, y1 = out.bounds
    return translated(out, centre - (x0 + x1) / 2, centre - (y0 + y1) / 2 + nudge_y)
