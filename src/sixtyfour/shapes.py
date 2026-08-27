"""The 16 silhouettes.

Each entry is a closed, filled region in the 1000x1000 design canvas. Six are
lifted from the hand-drawn originals in `reference/svgs_original/` -- in those
files the path *is* the fill boundary, so it transfers directly. The rest are
authored here, including Cloud, whose original was an open stroked polyline
rather than a silhouette and so had nothing to lift.

`fit_into` normalises every shape to the same bounding box, which is not the
same as making them look the same size: a circle inscribed in a square reads
markedly smaller than the square. `OPTICAL` corrects for that by eye, and
`NUDGE_Y` re-centres shapes whose visual mass sits off their geometric centre.
"""

from __future__ import annotations

import math

import pathops

from . import geometry as g
from .spec import SILHOUETTES

#: Bounding box every silhouette is normalised into, before optical correction.
TARGET_BOX = 760.0

#: Width of the outline that every glyph carries, whatever its fill.
OUTLINE_WIDTH = 68.0

#: Gap between the inside of the outline and where texture may start.
TEXTURE_INSET = 20.0

#: Per-shape area correction. A square filling its box looks bigger than a
#: circle filling the same box; these bring the 16 to a common optical weight.
OPTICAL: dict[str, float] = {
    "Cross": 1.02,
    "Circle": 1.06,
    "Triangle": 1.08,
    "Square": 0.94,
    "Clubs": 1.02,
    "Diamonds": 1.06,
    "Hearts": 1.02,
    "Spades": 1.02,
    "Drop": 1.04,
    "Flame": 1.02,
    "Cloud": 1.04,
    "Ingot": 1.00,
    "Mushroom": 1.02,
    "Flower": 1.04,
    "Star": 1.10,
    "Moon": 1.08,
}

#: Downward shift in design units applied after centring.
NUDGE_Y: dict[str, float] = {
    "Flame": 10.0,
    "Mushroom": 12.0,
    "Clubs": -8.0,
    "Spades": -6.0,
}


# --- lifted from the hand-drawn originals ------------------------------------

_CLUBS = (
    "M 668.604 354.865 C 668.11 354.865 667.638 354.952 667.144 354.952 "
    "C 667.998 348.107 668.604 341.197 668.604 334.13 C 668.604 242.537 "
    "593.117 168.26 500.006 168.26 C 406.872 168.26 331.406 242.537 331.406 334.13 "
    "C 331.406 341.197 332.002 348.107 332.867 354.952 C 332.373 354.952 "
    "331.901 354.865 331.406 354.865 C 238.272 354.865 162.807 429.141 162.807 520.734 "
    "C 162.807 612.327 238.272 686.604 331.406 686.604 C 385.436 686.604 "
    "433.408 661.492 464.251 622.601 L 457.856 676.243 C 452.179 715.93 "
    "424.203 752.234 384.088 759.177 L 331.406 769.54 L 331.406 831.74 "
    "L 668.604 831.74 L 668.604 769.54 L 615.912 759.167 C 575.785 752.223 "
    "547.798 715.941 542.144 676.231 L 535.726 622.589 C 566.569 661.492 "
    "614.552 686.593 668.593 686.593 C 761.705 686.593 837.193 612.317 837.193 520.724 "
    "C 837.193 429.129 761.717 354.865 668.604 354.865 Z"
)

_DIAMONDS = (
    "M 237.231 561.704 C 213.337 527.64 213.337 472.361 237.231 438.297 "
    "L 456.738 125.276 C 480.633 91.211 519.369 91.211 543.298 125.276 "
    "L 762.77 438.297 C 786.664 472.361 786.664 527.64 762.77 561.704 "
    "L 543.298 874.725 C 519.369 908.789 480.633 908.789 456.738 874.725 "
    "L 237.231 561.704 Z"
)

_HEARTS = (
    "M 499.708 820.741 C 671.708 689.276 757.756 569.025 798.221 477.301 "
    "C 845.494 370.13 804.372 237.278 701.228 192.698 C 579.99 140.319 "
    "499.708 261.165 499.708 261.165 C 499.708 261.165 419.999 140.005 "
    "298.771 192.407 C 195.627 236.986 154.505 369.839 201.779 477.01 "
    "C 242.242 568.722 327.71 689.287 499.708 820.741 Z"
)

_DROP = (
    "M 798 577.618 C 798 749.086 664.582 888.087 500 888.087 C 335.419 888.087 "
    "202 749.086 202 577.618 C 202 536.446 209.692 497.144 223.662 461.192 "
    "C 267.869 347.412 500 111.914 500 111.914 C 500 111.914 732.131 347.412 "
    "776.339 461.192 C 790.308 497.144 798 536.446 798 577.618 Z"
)

_FLAME = (
    "M 586.244 102.662 C 587.55 101.879 589.243 102.754 589.293 104.235 "
    "C 589.298 104.408 589.281 104.58 589.238 104.748 C 581.421 134.589 "
    "542.998 307.381 681.886 419.526 C 817.613 529.265 821.77 694.357 720.641 804.577 "
    "C 599.717 936.617 390.638 913.354 300.652 826.557 C 237.28 765.75 "
    "122.179 567.451 319.282 401.718 C 319.948 400.863 321.277 400.863 321.943 401.718 "
    "C 326.766 421.452 360.2 546.111 449.354 562.156 C 453.511 562.156 "
    "455.507 560.39 453.511 556.7 C 427.231 507.606 308.803 257.324 586.244 102.662 Z"
)


# --- authored here -----------------------------------------------------------


def _circle() -> pathops.Path:
    return g.circle(500, 500, 380)


def _triangle() -> pathops.Path:
    return g.polygon([(500, 130), (868, 800), (132, 800)])


def _square() -> pathops.Path:
    return g.rounded_rect(150, 150, 850, 850, 56)


def _cross() -> pathops.Path:
    """A Greek cross with arms at 37% of its span.

    The hand-drawn original had arms a fifth as wide as the cross was tall.
    Once the outline band and the texture inset are subtracted from that, the
    channel left inside an arm is too narrow to hold a legible hatch, and the
    dotted and striped tiers collapse towards the empty one.
    """
    a, b, c, d = 100.0, 350.0, 650.0, 900.0
    return g.polygon(
        [(b, a), (c, a), (c, b), (d, b), (d, c), (c, c),
         (c, d), (b, d), (b, c), (a, c), (a, b), (b, b)]
    )


def _spades() -> pathops.Path:
    """Apex, two shoulders, and a flared stem.

    Flipping the heart over would be cheaper but gives a shield: the shoulders
    stay round and the stem disappears inside them, leaving something too close
    to Drop to tell apart in a row of symbols.
    """
    return g.from_d(
        "M 500 105 "
        "C 600 260 760 400 818 520 "
        "C 880 650 800 762 690 742 "
        "C 620 730 560 690 536 632 "
        "C 548 740 580 826 648 884 "
        "L 352 884 "
        "C 420 826 452 740 464 632 "
        "C 440 690 380 730 310 742 "
        "C 200 762 120 650 182 520 "
        "C 240 400 400 260 500 105 Z"
    )


def _cloud() -> pathops.Path:
    """Overlapping discs on a flat base -- the classic cumulus silhouette."""
    return g.union(
        g.rounded_rect(190, 520, 810, 706, 92),
        g.circle(370, 476, 168),
        g.circle(548, 418, 204),
        g.circle(700, 528, 148),
    )


def _ingot() -> pathops.Path:
    """A cast bar: top plate and front face, held apart by a visible seam.

    Merging the two into one outline would collapse to a plain trapezoid and
    lose the read entirely, so they stay as two contours with a gap.
    """
    top = g.polygon([(342, 258), (658, 258), (712, 442), (288, 442)])
    front = g.polygon([(268, 478), (732, 478), (840, 742), (160, 742)])
    return g.union(top, front)


def _mushroom() -> pathops.Path:
    """A domed cap on a stem."""
    cap = g.intersection(
        g.ellipse(500, 452, 348, 268),
        g.polygon([(0, 0), (1000, 0), (1000, 452), (0, 452)]),
    )
    stem = g.rounded_rect(402, 400, 598, 792, 66)
    return g.union(cap, stem)


def _flower() -> pathops.Path:
    """Five petals around a hub."""
    petals = []
    for i in range(5):
        angle = math.radians(-90 + i * 72)
        petals.append(g.circle(500 + math.cos(angle) * 218, 500 + math.sin(angle) * 218, 190))
    return g.union(g.circle(500, 500, 150), *petals)


def _star() -> pathops.Path:
    """A five-pointed star."""
    outer, inner = 400.0, 194.0
    points = []
    for i in range(10):
        radius = outer if i % 2 == 0 else inner
        angle = math.radians(-90 + i * 36)
        points.append((500 + math.cos(angle) * radius, 500 + math.sin(angle) * radius))
    return g.polygon(points)


def _moon() -> pathops.Path:
    """A crescent: one disc bitten out of another."""
    return g.difference(g.circle(452, 500, 372), g.circle(660, 404, 330))


_BUILDERS = {
    "Cross": _cross,
    "Circle": _circle,
    "Triangle": _triangle,
    "Square": _square,
    "Clubs": lambda: g.from_d(_CLUBS),
    "Diamonds": lambda: g.from_d(_DIAMONDS),
    "Hearts": lambda: g.from_d(_HEARTS),
    "Spades": _spades,
    "Drop": lambda: g.from_d(_DROP),
    "Flame": lambda: g.from_d(_FLAME),
    "Cloud": _cloud,
    "Ingot": _ingot,
    "Mushroom": _mushroom,
    "Flower": _flower,
    "Star": _star,
    "Moon": _moon,
}


def silhouette(name: str) -> pathops.Path:
    """The normalised, optically corrected silhouette for one symbol."""
    raw = g.simplify(_BUILDERS[name]())
    box = TARGET_BOX * OPTICAL.get(name, 1.0)
    return g.simplify(g.fit_into(raw, box, nudge_y=NUDGE_Y.get(name, 0.0)))


def all_silhouettes() -> dict[str, pathops.Path]:
    return {name: silhouette(name) for name in SILHOUETTES}
