"""Writing the 67 SVGs.

One `<path>`, no styles, no strokes, no <pattern>, no clipPath. Everything is
already baked into filled geometry, so these survive any SVG toolchain --
including picosvg, which silently discarded the strokes and patterns the
original hand-drawn files relied on.
"""

from __future__ import annotations

from pathlib import Path

import pathops

from . import geometry as g
from . import glyphs
from .spec import TABLE, Entry

_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">
  <title>{title}</title>
  <path fill="{colour}" fill-rule="nonzero" d="{d}"/>
</svg>
"""

#: The SVGs carry the tier colour so they are useful as standalone assets. The
#: font does not read these back -- it builds from the same geometry directly.
FILL_COLOURS = {
    "none": "#111111",
    "solid": "#111111",
    "dots": "#1B4FD8",
    "lines": "#D42A20",
}

NEUTRAL = "#111111"


def render(path: pathops.Path, title: str, colour: str = NEUTRAL) -> str:
    return _TEMPLATE.format(title=_escape(title), colour=colour, d=g.to_d(path))


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def entry_svg(entry: Entry) -> str:
    title = f"{entry.char} = {entry.value} : {entry.symbol} / {entry.tier_name} / {entry.hatch_name}"
    return render(glyphs.build_entry(entry), title, FILL_COLOURS[entry.fill])


def write_all(out_dir: Path) -> list[Path]:
    """Write all 64 data symbols plus '=' and space. Returns the paths written."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for entry in TABLE:
        target = out_dir / entry.svg_filename
        target.write_text(entry_svg(entry), encoding="utf-8")
        written.append(target)

    padding = out_dir / "u003D.svg"
    padding.write_text(render(glyphs.padding(), "= : padding, no data"), encoding="utf-8")
    written.append(padding)

    space = out_dir / "u0020.svg"
    space.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" '
        'width="1000" height="1000">\n  <title>space</title>\n</svg>\n',
        encoding="utf-8",
    )
    written.append(space)
    return written
