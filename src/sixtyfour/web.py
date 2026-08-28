"""The shipped CSS and the specimen page.

The page is generated from the same table as the font, so a change to the
alphabet cannot leave the documentation behind.
"""

from __future__ import annotations

import base64
import html
from pathlib import Path

from .spec import (
    BASE64_ALPHABET,
    BY_CHAR,
    CLASSES,
    FILLS,
    SILHOUETTES,
    SPOKEN_FILL,
    SPOKEN_ORDER,
    TABLE,
    URLSAFE_ALIASES,
)
from .ufobuild import DESCRIPTION, FAMILY_NAME, MONO_FAMILY_NAME

CSS_CLASS = "sixty-four"
MONO_CSS_CLASS = "sixty-four-mono"
PAGE_TITLE = "Sixty Four Alphabet"

SAMPLE_TEXT = "Sixty Four makes base64 legible."


def _data_uri(woff2: Path) -> str:
    return "data:font/woff2;base64," + base64.b64encode(woff2.read_bytes()).decode("ascii")


#: The colour font carries two CPAL palettes. Renderers use the first unless
#: asked otherwise, so without this the dark palette would never be reached and
#: the light-background red would sit at poor contrast on a dark page.
_DARK_PALETTE = """
@font-palette-values --{slug}-dark {{
  font-family: "{family}";
  base-palette: 1;
}}

@media (prefers-color-scheme: dark) {{
  .{css_class} {{ font-palette: --{slug}-dark; }}
}}
"""


def font_face_css(woff2: Path, family: str, css_class: str, dark_palette: bool = True) -> str:
    """A drop-in stylesheet with the font embedded -- no asset hosting needed."""
    slug = css_class
    palette = (
        _DARK_PALETTE.format(slug=slug, family=family, css_class=css_class)
        if dark_palette
        else ""
    )
    return f"""/* {family} -- {DESCRIPTION}
   The font is embedded below, so this one file is the whole install:
   link it, then put class="{css_class}" on any element holding base64. */

@font-face {{
  font-family: "{family}";
  src: url({_data_uri(woff2)}) format("woff2");
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}}

.{css_class} {{
  font-family: "{family}", ui-monospace, monospace;
  /* The font ships no substitution features, but belt and braces: two data
     symbols must never fuse into one, or the byte count stops being countable. */
  font-variant-ligatures: none;
  font-feature-settings: "liga" 0, "clig" 0, "calt" 0;
  word-break: break-all;
}}
{palette}"""


# --- the specimen page -------------------------------------------------------

_STYLE = """
:root {
  --paper:  #FBFAF7;
  --raised: #FFFFFF;
  --ink:    #1A1C22;
  --muted:  #6C6E76;
  --rule:   #E2E0D9;
  --blue:   #1B4FD8;
  --red:    #D42A20;

  /* The both-grounds panel shows the light and the dark rendering side by side,
     so its colours are deliberately fixed rather than following the theme --
     otherwise half the demonstration would always be the half you can see. */
  --lit-bg:   #FBFAF7;
  --lit-fg:   #1A1C22;
  --lit-rule: #E2E0D9;
  --dim-bg:   #121419;
  --dim-fg:   #ECEBE6;
  --dim-rule: #2A2E37;
}
:root:not([data-theme="light"]) {
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper:  #121419;
    --raised: #1A1D24;
    --ink:    #ECEBE6;
    --muted:  #92949C;
    --rule:   #2A2E37;
    --blue:   #7FA8FF;
    --red:    #FF7A6E;
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --paper:  #121419;
  --raised: #1A1D24;
  --ink:    #ECEBE6;
  --muted:  #92949C;
  --rule:   #2A2E37;
  --blue:   #7FA8FF;
  --red:    #FF7A6E;
  color-scheme: dark;
}

*, *::before, *::after { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: "Archivo", ui-sans-serif, system-ui, sans-serif;
  font-size: 16px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

.wrap {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 28px 96px;
}

section { padding-block: 56px; border-top: 1px solid var(--rule); }
section:first-of-type { border-top: 0; }

h1, h2, h3 { text-wrap: balance; margin: 0; font-weight: 400; }
h1 {
  font-family: "Bodoni Moda", "Times New Roman", serif;
  font-size: clamp(2.9rem, 7vw, 5.4rem);
  line-height: 1.02;
  letter-spacing: -0.015em;
}
h2 {
  font-family: "Bodoni Moda", "Times New Roman", serif;
  font-size: clamp(1.6rem, 3vw, 2.3rem);
  line-height: 1.15;
}
h3 { font-size: 1rem; font-weight: 600; }

p { margin: 0; max-width: 64ch; }
.lede { font-size: 1.12rem; color: var(--muted); }

.eyebrow {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .72rem;
  letter-spacing: .16em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0 0 14px;
}

.stack { display: flex; flex-direction: column; gap: 18px; }
.stack-tight { display: flex; flex-direction: column; gap: 10px; }

/* --- hero ---------------------------------------------------------------- */

header.hero { padding: 72px 0 56px; }
.hero-grid { display: flex; flex-direction: column; gap: 30px; }
.hero-strip {
  font-size: clamp(30px, 5.6vw, 62px);
  line-height: 1.35;
  overflow-x: auto;
  padding-bottom: 6px;
}

.byline {
  display: flex; flex-wrap: wrap; gap: 10px 26px;
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .8rem; color: var(--muted);
}
.byline b { color: var(--ink); font-weight: 600; }

/* --- the matrix ---------------------------------------------------------- */

.matrix-scroll { overflow-x: auto; padding-bottom: 8px; }
table.matrix { border-collapse: collapse; font-variant-numeric: tabular-nums; }
table.matrix th {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .68rem; font-weight: 500; letter-spacing: .08em;
  text-transform: uppercase; color: var(--muted);
  padding: 6px 4px; text-align: center; white-space: nowrap;
}
table.matrix th.row-head { text-align: right; padding-right: 14px; }
table.matrix td { padding: 3px; }

.cell {
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  width: 62px; padding: 7px 0 5px;
  background: var(--raised);
  border: 1px solid var(--rule);
  border-radius: 3px;
  cursor: default;
  transition: border-color .12s ease, transform .12s ease;
}
.cell:hover, .cell:focus-visible {
  border-color: var(--ink);
  transform: translateY(-1px);
  outline: none;
}
.cell .sym { font-size: 34px; line-height: 1; }
.cell .meta {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .64rem; color: var(--muted);
  font-variant-numeric: tabular-nums;
}
.cell .meta b { color: var(--ink); font-weight: 600; }

/* --- controls ------------------------------------------------------------ */

.controls { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 22px; }
button.toggle {
  font: inherit; font-size: .84rem;
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  padding: 7px 15px;
  color: var(--ink); background: var(--raised);
  border: 1px solid var(--rule); border-radius: 999px;
  cursor: pointer;
  transition: border-color .12s ease, background .12s ease;
}
button.toggle:hover { border-color: var(--ink); }
button.toggle:focus-visible { outline: 2px solid var(--blue); outline-offset: 2px; }
button.toggle[aria-pressed="true"] { background: var(--ink); color: var(--paper); border-color: var(--ink); }

.desaturated { filter: grayscale(1) contrast(1.08); }

.switch { display: inline-flex; gap: 0; border: 1px solid var(--rule); border-radius: 999px; overflow: hidden; }
.switch button {
  font: inherit; font-size: .78rem;
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  padding: 6px 14px; border: 0; cursor: pointer;
  color: var(--muted); background: var(--raised);
  transition: color .12s ease, background .12s ease;
}
.switch button + button { border-left: 1px solid var(--rule); }
.switch button:hover { color: var(--ink); }
.switch button:focus-visible { outline: 2px solid var(--blue); outline-offset: -2px; }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }

/* --- spoken vocabulary --------------------------------------------------- */

.tierkey { display: flex; gap: 14px; flex-wrap: wrap; }
.tierkey .item {
  display: flex; flex-direction: column; align-items: center; gap: 10px;
  flex: 1 1 90px; padding: 18px 10px 14px;
  background: var(--raised); border: 1px solid var(--rule); border-radius: 4px;
}
.tierkey .glyph { font-size: 46px; line-height: 1; }
.tierkey .word {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .74rem; letter-spacing: .1em; text-transform: uppercase; color: var(--ink);
}
.tierkey .gloss {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .62rem; color: var(--muted); text-align: center;
}

.dictation { display: flex; flex-wrap: wrap; gap: 10px; }
.dictation .word {
  display: flex; flex-direction: column; align-items: center; gap: 7px;
  flex: 0 0 auto; min-width: 96px; padding: 14px 12px 11px;
  background: var(--raised); border: 1px solid var(--rule); border-radius: 4px;
}
.dictation .glyph { font-size: 40px; line-height: 1; }
.dictation .say { font-size: .84rem; white-space: nowrap; }
.dictation .code {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .64rem; color: var(--muted); font-variant-numeric: tabular-nums;
}

.mono-run { font-size: clamp(24px, 3vw, 34px); line-height: 1.4; }

/* --- graceful degradation ------------------------------------------------ */

.degrade { display: flex; flex-direction: column; gap: 12px; }
.degrade .row {
  display: flex; flex-direction: column; gap: 10px;
  background: var(--raised); border: 1px solid var(--rule); border-radius: 4px;
  padding: 16px 18px;
}
.degrade .tag {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .68rem; letter-spacing: .12em; text-transform: uppercase; color: var(--muted);
}
.degrade .text { overflow-x: auto; }
.degrade .text.symbols { font-size: clamp(26px, 3.4vw, 36px); line-height: 1.25; }
/* The declared fallback stack, shown as a viewer without the font would get it. */
.degrade .text.plain {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 1.05rem; color: var(--ink); word-break: break-all;
}
.status {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .76rem; color: var(--muted); overflow-wrap: anywhere;
}
.status b { color: var(--ink); font-weight: 500; }

/* --- both grounds -------------------------------------------------------- */

.grounds { display: grid; gap: 20px; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
.ground { border-radius: 5px; padding: 24px; display: flex; flex-direction: column; gap: 20px; }
.ground-lit { background: var(--lit-bg); color: var(--lit-fg); border: 1px solid var(--lit-rule); }
.ground-dim { background: var(--dim-bg); color: var(--dim-fg); border: 1px solid var(--dim-rule); }
.ground .tag {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .7rem; letter-spacing: .16em; text-transform: uppercase; opacity: .6;
}
.ground .strip { font-size: clamp(26px, 3.4vw, 38px); line-height: 1.2; overflow-x: auto; }
.ground .tiers { display: flex; gap: 12px; flex-wrap: wrap; }
.ground .tier { display: flex; flex-direction: column; align-items: center; gap: 6px; flex: 1 1 60px; }
.ground .tier .glyph { font-size: 44px; line-height: 1; }
.ground .tier .name {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .62rem; letter-spacing: .06em; text-transform: uppercase; opacity: .6;
  text-align: center;
}


/* --- encoder ------------------------------------------------------------- */

.encoder { display: grid; gap: 16px; }
.encoder label {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .72rem; letter-spacing: .12em; text-transform: uppercase; color: var(--muted);
}
.encoder input {
  font: inherit; width: 100%; padding: 13px 16px;
  color: var(--ink); background: var(--raised);
  border: 1px solid var(--rule); border-radius: 4px;
}
.encoder input:focus-visible { outline: 2px solid var(--blue); outline-offset: 1px; border-color: transparent; }

.readout {
  background: var(--raised); border: 1px solid var(--rule); border-radius: 4px;
  padding: 16px; min-height: 62px; overflow-wrap: anywhere;
}
.readout.raw { font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .92rem; color: var(--muted); }
.readout.symbols { font-size: 40px; line-height: 1.3; }

/* --- decode walkthrough -------------------------------------------------- */

.decode { display: grid; gap: 22px; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); }
.step {
  background: var(--raised); border: 1px solid var(--rule); border-radius: 4px;
  padding: 20px; display: flex; flex-direction: column; gap: 8px;
}
.step .k {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .68rem; letter-spacing: .12em; text-transform: uppercase; color: var(--muted);
}
.step .v { font-size: 1.25rem; }
.step .v.big { font-size: 52px; line-height: 1; }
.step p { font-size: .88rem; color: var(--muted); }

/* --- sizes --------------------------------------------------------------- */

.sizes { display: flex; flex-direction: column; gap: 20px; }
.size-row { display: flex; align-items: baseline; gap: 18px; }
.size-row .tag {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .7rem; color: var(--muted); width: 46px; flex: none;
  font-variant-numeric: tabular-nums;
}
.size-row .run { overflow-x: auto; white-space: nowrap; }

/* --- code ---------------------------------------------------------------- */

pre {
  margin: 0; padding: 18px 20px; overflow-x: auto;
  background: var(--raised); border: 1px solid var(--rule); border-radius: 4px;
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .84rem; line-height: 1.65;
}
code { font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .92em; }
p code { background: var(--raised); border: 1px solid var(--rule); border-radius: 3px; padding: 1px 5px; }

/* --- full table ---------------------------------------------------------- */

.table-scroll { overflow-x: auto; max-height: 520px; overflow-y: auto; border: 1px solid var(--rule); border-radius: 4px; }
table.full { border-collapse: collapse; width: 100%; font-size: .84rem; font-variant-numeric: tabular-nums; }
table.full th {
  position: sticky; top: 0; z-index: 1;
  background: var(--raised); color: var(--muted);
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .68rem; letter-spacing: .1em; text-transform: uppercase; font-weight: 500;
  text-align: left; padding: 11px 14px; border-bottom: 1px solid var(--rule);
}
table.full td { padding: 8px 14px; border-bottom: 1px solid var(--rule); }
table.full tr:last-child td { border-bottom: 0; }
table.full td.sym { font-size: 26px; line-height: 1; width: 1%; }
table.full td.mono { font-family: "IBM Plex Mono", ui-monospace, monospace; }
.swatch { display: inline-flex; align-items: center; gap: 7px; white-space: nowrap; }
.swatch i { width: 9px; height: 9px; border-radius: 2px; border: 1px solid var(--rule); }
/* Blank and Fill store no colour -- they paint with the text foreground. A chip
   of a fixed colour would contradict its own label on one ground or the other,
   so these two show the tier itself: hollow for Blank, inked for Fill. */
.swatch i.hollow { background: transparent; border-color: currentColor; }
.swatch i.inked { background: currentColor; border-color: currentColor; }

footer {
  border-top: 1px solid var(--rule); padding-top: 28px;
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .76rem; color: var(--muted);
}

@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}
""" + f"""
/* The page-level palette rule matches these on specificity, so raise them above
   it: each card keeps its own palette whatever theme the page is in. */
:root .ground-lit .{CSS_CLASS} {{ font-palette: normal; }}
:root .ground-dim .{CSS_CLASS} {{ font-palette: --sf-dark; }}
"""


def _tier_mark(entry) -> str:
    """The reference table's tier chip.

    Blue and Red are stored colours, so they get a chip of that colour. Blank and
    Fill are not colours at all, so they get a mark that shows what the tier does
    instead: an outline and a solid, both in the text colour they actually use.
    """
    if not entry.has_colour:
        return '<i class="%s"></i>' % ("inked" if entry.fill == "solid" else "hollow")
    colour = {"dots": "var(--blue)", "lines": "var(--red)"}[entry.fill]
    return f'<i style="background:{colour}"></i>'


def _matrix() -> str:
    heads = "".join(f"<th>{html.escape(name)}</th>" for name in SILHOUETTES)
    rows = []
    for fill_index, fill in enumerate(FILLS):
        tier, hatch = TABLE[fill_index * 16].tier_name, TABLE[fill_index * 16].hatch_name
        cells = []
        for column in range(16):
            entry = TABLE[fill_index * 16 + column]
            title = (
                f"{entry.spoken} \u2014 {entry.char} = {entry.value} \u00b7 "
                f"{entry.klass} \u00b7 {entry.tier_name} / {entry.hatch_name}"
            )
            cells.append(
                f'<td><div class="cell" tabindex="0" title="{html.escape(title)}">'
                f'<span class="sym {CSS_CLASS}">{html.escape(entry.char)}</span>'
                f'<span class="meta"><b>{html.escape(entry.char)}</b> {entry.value}</span>'
                f"</div></td>"
            )
        rows.append(
            f'<tr><th class="row-head">{html.escape(tier)}<br>{html.escape(hatch)}</th>'
            + "".join(cells)
            + "</tr>"
        )
    return (
        '<div class="matrix-scroll"><table class="matrix">'
        f'<thead><tr><th class="row-head"></th>{heads}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


def _full_table() -> str:
    rows = []
    for entry in TABLE:
        alias = next((a for a, s in URLSAFE_ALIASES.items() if s == entry.char), "")
        alias_cell = f"<code>{html.escape(alias)}</code>" if alias else "—"
        rows.append(
            f"<tr>"
            f'<td class="sym {CSS_CLASS}">{html.escape(entry.char)}</td>'
            f'<td class="mono">{html.escape(entry.char)}</td>'
            f'<td class="mono">{entry.value}</td>'
            f'<td class="mono">U+{entry.codepoint:04X}</td>'
            f"<td>{html.escape(entry.klass)}</td>"
            f"<td>{html.escape(entry.symbol)}</td>"
            f"<td>{html.escape(entry.spoken)}</td>"
            f'<td><span class="swatch">{_tier_mark(entry)}'
            f"{html.escape(entry.tier_name)}</span></td>"
            f"<td>{html.escape(entry.hatch_name)}</td>"
            f'<td class="mono">{alias_cell}</td>'
            f"</tr>"
        )
    heads = "".join(
        f"<th>{h}</th>"
        for h in (
            "Symbol", "Char", "Value", "Codepoint", "Class", "Shape",
            "Say it", "Tier", "Hatch", "URL-safe",
        )
    )
    return (
        '<div class="table-scroll"><table class="full">'
        f"<thead><tr>{heads}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    )


_DOWNLOAD_STYLE = """
/* --- downloads (hosted page only) ---------------------------------------- */

.downloads { display: grid; gap: 26px; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
.bundle {
  background: var(--raised); border: 1px solid var(--rule); border-radius: 4px;
  padding: 20px; display: flex; flex-direction: column; gap: 14px;
}
.bundle h3 { font-size: .95rem; }
.bundle p { font-size: .86rem; color: var(--muted); }
.bundle ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 1px; }
.bundle li { display: flex; align-items: baseline; justify-content: space-between; gap: 14px; padding: 5px 0; border-top: 1px solid var(--rule); }
.bundle li:first-child { border-top: 0; }
.bundle a {
  font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .82rem;
  color: var(--ink); text-decoration: none;
  border-bottom: 1px solid var(--rule);
}
.bundle a:hover, .bundle a:focus-visible { border-bottom-color: var(--ink); }
.bundle a:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; }
.bundle .size {
  font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .72rem;
  color: var(--muted); white-space: nowrap; font-variant-numeric: tabular-nums;
}
"""

#: Grouped for the hosted page: what someone is actually choosing between is a
#: bundle, not a file extension.
DOWNLOAD_BUNDLES: list[tuple[str, str, list[str]]] = [
    (
        "Colour font",
        "COLR v0 with CPAL. Keeps full hatched outlines as fallback, so renderers "
        "without colour support show the artwork rather than nothing.",
        ["SixtyFour-Regular.ttf", "SixtyFour-Regular.woff2", "SixtyFour-Regular.woff"],
    ),
    (
        "Monochrome font",
        "No colour tables at all, for anywhere a colour table is unwelcome. The hatch "
        "still separates all four tiers on its own.",
        [
            "SixtyFourMono-Regular.ttf",
            "SixtyFourMono-Regular.woff2",
            "SixtyFourMono-Regular.otf",
        ],
    ),
    (
        "Stylesheets",
        "The font is embedded inside each one as a data URI. Link it and add the class "
        "\u2014 there is no second request and nothing to upload.",
        ["sixty-four.css", "sixty-four-mono.css"],
    ),
    (
        "The alphabet as data",
        "Character, value, class, shape, tier and hatch for all 64, for writing your "
        "own renderer.",
        ["mapping.json", "mapping.tsv"],
    ),
]


def _human_size(count: int) -> str:
    return f"{count / 1024:.1f} KB" if count >= 1024 else f"{count} B"


def _downloads(asset_dir: Path) -> str:
    """The download panel. Hosted pages only -- an Artifact cannot serve files."""
    bundles = []
    for title, note, filenames in DOWNLOAD_BUNDLES:
        items = []
        for filename in filenames:
            asset = asset_dir / filename
            if not asset.is_file():
                continue
            items.append(
                f'<li><a href="{filename}" download>{html.escape(filename)}</a>'
                f'<span class="size">{_human_size(asset.stat().st_size)}</span></li>'
            )
        if items:
            bundles.append(
                f'<div class="bundle"><h3>{html.escape(title)}</h3>'
                f"<p>{note}</p><ul>{''.join(items)}</ul></div>"
            )
    return (
        f"<style>{_DOWNLOAD_STYLE}</style>"
        '<section><p class="eyebrow">Download</p><h2>Take the files.</h2>'
        f'<div class="downloads" style="margin-top:28px">{"".join(bundles)}</div></section>'
    )


def _ground_card(kind: str, label: str, sample: str) -> str:
    """One side of the both-grounds panel."""
    tiers = []
    for fill in FILLS:
        entry = TABLE[FILLS.index(fill) * 16 + 1]  # Circle, so only the tier varies
        tiers.append(
            f'<div class="tier"><span class="glyph {CSS_CLASS}">{html.escape(entry.char)}</span>'
            f'<span class="name">{html.escape(entry.hatch_name)}</span></div>'
        )
    return (
        f'<div class="ground ground-{kind}">'
        f'<span class="tag">{html.escape(label)}</span>'
        f'<div class="strip {CSS_CLASS}">{html.escape(sample)}</div>'
        f'<div class="tiers">{"".join(tiers)}</div>'
        "</div>"
    )


def _grounds() -> str:
    sample = _encoded_sample()[:14]
    return (
        '<div class="grounds">'
        + _ground_card("lit", "Light ground", sample)
        + _ground_card("dim", "Dark ground", sample)
        + "</div>"
    )


def _tier_key(css_class: str = CSS_CLASS, shape_index: int = 0) -> str:
    """The four texture words, in the order they are recited: blank, lines, dots, fill."""
    items = []
    for fill in SPOKEN_ORDER:
        entry = TABLE[FILLS.index(fill) * 16 + shape_index]
        items.append(
            f'<div class="item"><span class="glyph {css_class}">{html.escape(entry.char)}</span>'
            f'<span class="word">{html.escape(SPOKEN_FILL[fill])}</span>'
            f'<span class="gloss">{html.escape(entry.hatch_name)}</span></div>'
        )
    return f'<div class="tierkey">{"".join(items)}</div>'


def _dictation(text: str) -> str:
    """A run of base64 with each symbol's spoken name under it."""
    words = []
    for char in text:
        entry = BY_CHAR.get(char)
        if entry is None:
            continue
        words.append(
            f'<div class="word"><span class="glyph {CSS_CLASS}">{html.escape(entry.char)}</span>'
            f'<span class="say">{html.escape(entry.spoken)}</span>'
            f'<span class="code">{html.escape(entry.char)} &middot; {entry.value}</span></div>'
        )
    return f'<div class="dictation">{"".join(words)}</div>'


def _script() -> str:
    return """
(function () {
  var input = document.getElementById('sf-input');
  var raw = document.getElementById('sf-raw');
  var symbols = document.getElementById('sf-symbols');

  function encode(text) {
    var bytes = new TextEncoder().encode(text);
    var binary = '';
    for (var i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
    return btoa(binary);
  }

  function update() {
    var encoded = encode(input.value);
    raw.textContent = encoded || '\\u2014';
    symbols.textContent = encoded;
  }

  input.addEventListener('input', update);
  update();

  var root = document.documentElement;
  var themeButtons = Array.prototype.slice.call(
    document.querySelectorAll('[data-theme-set]')
  );

  function applyTheme(mode) {
    if (mode === 'auto') {
      root.removeAttribute('data-theme');
    } else {
      root.setAttribute('data-theme', mode);
    }
    themeButtons.forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-theme-set') === mode));
    });
    try { localStorage.setItem('sixty-four-theme', mode); } catch (e) { /* private mode */ }
  }

  var saved = null;
  try { saved = localStorage.getItem('sixty-four-theme'); } catch (e) { /* private mode */ }
  // With nothing stored, follow whatever the host already stamped; an unstamped
  // root means the viewer is on system preference, which is 'auto'.
  applyTheme(saved || root.getAttribute('data-theme') || 'auto');

  themeButtons.forEach(function (b) {
    b.addEventListener('click', function () {
      applyTheme(b.getAttribute('data-theme-set'));
    });
  });

  var symbols = document.getElementById('sf-degrade-symbols');
  var copyButton = document.getElementById('sf-copy');
  var copyStatus = document.getElementById('sf-copy-status');

  function selectSymbols() {
    var range = document.createRange();
    range.selectNodeContents(symbols);
    var selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
  }

  function showCopied(text) {
    copyStatus.innerHTML = 'On your clipboard: <b></b>';
    copyStatus.querySelector('b').textContent = text;
  }

  copyButton.addEventListener('click', function () {
    var text = symbols.textContent;
    // Clipboard access is refused outright in plenty of contexts -- an iframe
    // without permission, a page served over http. Selecting the text is the
    // honest fallback: the point being demonstrated is that it is only text.
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(
        function () { showCopied(text); },
        function () {
          selectSymbols();
          copyStatus.textContent = 'Selected \u2014 press Ctrl+C. It is only text.';
        }
      );
    } else {
      selectSymbols();
      copyStatus.textContent = 'Selected \u2014 press Ctrl+C. It is only text.';
    }
  });

  var button = document.getElementById('sf-grey');
  button.addEventListener('click', function () {
    var on = button.getAttribute('aria-pressed') !== 'true';
    button.setAttribute('aria-pressed', String(on));
    button.textContent = on ? 'Colour off \\u2014 hatch only' : 'Drop the colour';
    document.querySelectorAll('[data-desaturable]').forEach(function (el) {
      el.classList.toggle('desaturated', on);
    });
  });
})();
"""


def _body(woff2: Path, mono_woff2: Path, downloads: str = "") -> str:
    walk = TABLE[41]  # 'p' -- Fire, dots. A worked example with every field distinct.
    sizes = "".join(
        f'<div class="size-row"><span class="tag">{px}px</span>'
        f'<span class="run {CSS_CLASS}" style="font-size:{px}px">{html.escape(_encoded_sample())}</span></div>'
        for px in (14, 20, 32, 56)
    )
    # One per class, one per texture -- the whole system in four words.
    spoken_examples = "".join(BASE64_ALPHABET[v] for v in (0, 21, 42, 61))
    dictation_sample = _encoded_sample()[:8]
    degrade_sample = base64.b64encode(b"the text is still base64").decode("ascii")

    # Only the hosted build has a downloads section; keep its absence from
    # leaving a hole in the markup.
    downloads_block = f"  {downloads}\n\n" if downloads else ""
    alias_list = ", ".join(f"<code>{html.escape(a)}</code>" for a in URLSAFE_ALIASES)
    standard_list = " and ".join(
        f"<code>{html.escape(s)}</code>" for s in URLSAFE_ALIASES.values()
    )

    return f"""<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,400;6..96,500&family=Archivo:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
@font-face {{
  font-family: "{FAMILY_NAME}";
  src: url({_data_uri(woff2)}) format("woff2");
  font-weight: 400; font-style: normal; font-display: swap;
}}
@font-face {{
  font-family: "{MONO_FAMILY_NAME}";
  src: url({_data_uri(mono_woff2)}) format("woff2");
  font-weight: 400; font-style: normal; font-display: swap;
}}
.{CSS_CLASS}, .{MONO_CSS_CLASS} {{
  font-variant-ligatures: none;
  font-feature-settings: "liga" 0, "clig" 0, "calt" 0;
  word-break: break-all;
}}
.{CSS_CLASS} {{ font-family: "{FAMILY_NAME}", ui-monospace, monospace; }}
.{MONO_CSS_CLASS} {{ font-family: "{MONO_FAMILY_NAME}", ui-monospace, monospace; }}
@font-palette-values --sf-dark {{
  font-family: "{FAMILY_NAME}";
  base-palette: 1;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) .{CSS_CLASS} {{ font-palette: --sf-dark; }}
}}
:root[data-theme="dark"] .{CSS_CLASS} {{ font-palette: --sf-dark; }}
{_STYLE}
</style>

<div class="wrap">

  <header class="hero">
    <div class="hero-grid">
      <div class="stack">
        <p class="eyebrow">A typeface for base64</p>
        <h1>Sixty four symbols<br>you can say out loud.</h1>
        <p class="lede">Base64 is text no one can read. <code>aGVsbG8gd29ybGQ</code> cannot be
        compared at a glance, dictated over a phone, or checked by eye. Sixty Four gives each of
        the 64 characters a symbol instead &mdash; and encodes it twice, once as colour and once as
        hatch, so it survives a black-and-white printer and colour blindness alike.</p>
      </div>
      <div class="hero-strip {CSS_CLASS}" data-desaturable>{html.escape(_encoded_sample())}</div>
      <div class="byline">
        <span class="switch" role="group" aria-label="Page theme">
          <button type="button" data-theme-set="light" aria-pressed="false">Light</button>
          <button type="button" data-theme-set="dark" aria-pressed="false">Dark</button>
          <button type="button" data-theme-set="auto" aria-pressed="false">Auto</button>
        </span>
        <span><b>64</b> symbols</span>
        <span><b>16</b> shapes &times; <b>4</b> tiers</span>
        <span><b>COLR</b> colour, with outline fallback</span>
        <span><b>{woff2.stat().st_size / 1024:.1f} KB</b> woff2</span>
      </div>
    </div>
  </header>

  <section>
    <p class="eyebrow">Try it</p>
    <h2>Type anything.</h2>
    <div class="encoder" style="margin-top:26px">
      <div class="stack-tight">
        <label for="sf-input">Your text</label>
        <input id="sf-input" type="text" value="{html.escape(SAMPLE_TEXT)}" autocomplete="off" spellcheck="false">
      </div>
      <div class="stack-tight">
        <label>As base64</label>
        <div class="readout raw" id="sf-raw"></div>
      </div>
      <div class="stack-tight">
        <label>As Sixty Four</label>
        <div class="readout symbols {CSS_CLASS}" id="sf-symbols" data-desaturable></div>
      </div>
    </div>
  </section>

  <section>
    <p class="eyebrow">The alphabet</p>
    <h2>Four tiers, sixteen shapes.</h2>
    <p class="lede" style="margin-top:14px">Every value decomposes cleanly:
    <code>value = tier &times; 16 + class &times; 4 + shape</code>. Read the column for the shape,
    the row for the tier, and you have the number.</p>
    <div class="controls" style="margin-top:26px">
      <button class="toggle" id="sf-grey" type="button" aria-pressed="false">Drop the colour</button>
      <span class="eyebrow" style="margin:0">Hatch alone still separates all four tiers</span>
    </div>
    <div data-desaturable>{_matrix()}</div>
  </section>

  <section>
    <p class="eyebrow">Light and dark</p>
    <h2>Legible on either ground.</h2>
    <p class="lede" style="margin-top:14px">The empty and solid tiers paint with the text colour
    rather than a stored one, so they invert with the page instead of vanishing into it &mdash;
    which is why a solid symbol reads black on white and white on black. The dotted and striped
    tiers switch to a lighter blue and red on dark grounds. Both renderings are shown here at once,
    whichever theme you happen to be reading in.</p>
    <p class="lede" style="margin-top:14px">Which is also why those two tiers are called
    <b>Blank</b> and <b>Fill</b> rather than white and black. They hold no colour to be named
    after &mdash; only Blue and Red do &mdash; and a tier named &ldquo;black&rdquo; would be
    telling you the opposite of what you were looking at on half the pages it is read on.</p>
    <div style="margin-top:28px" data-desaturable>{_grounds()}</div>
  </section>

  <section>
    <p class="eyebrow">Reading one symbol</p>
    <h2>Shape, then texture.</h2>
    <div class="decode" style="margin-top:28px">
      <div class="step">
        <span class="k">The symbol</span>
        <span class="v big {CSS_CLASS}" data-desaturable>{html.escape(walk.char)}</span>
      </div>
      <div class="step">
        <span class="k">Shape</span>
        <span class="v">{html.escape(walk.symbol)}</span>
        <p>{html.escape(walk.klass)}, shape {walk.value % 4} of 0&ndash;3. Carries the low two bits.</p>
      </div>
      <div class="step">
        <span class="k">Texture</span>
        <span class="v">{html.escape(walk.hatch_name)} &middot; {html.escape(walk.tier_name)}</span>
        <p>Tier {walk.value // 16} of 0&ndash;3. Tier and hatch say the same thing, so either one on its own is enough to read it.</p>
      </div>
      <div class="step">
        <span class="k">Therefore</span>
        <span class="v"><code>{html.escape(walk.char)}</code> = {walk.value}</span>
        <p>{walk.value // 16} &times; 16 + {(walk.value // 4) % 4} &times; 4 + {walk.value % 4} = {walk.value}</p>
      </div>
    </div>
  </section>

  <section>
    <p class="eyebrow">Saying them out loud</p>
    <h2>Shape, then texture.</h2>
    <p class="lede" style="margin-top:14px">Name the shape, then the texture. Four texture words
    cover every tier &mdash; <b>blank</b>, <b>lines</b>, <b>dots</b>, <b>fill</b> &mdash; so any of
    the sixty-four is two plain words, and a string can be read down a phone line without anyone
    spelling anything.</p>
    <div style="margin-top:26px" data-desaturable>{_tier_key()}</div>
    <p class="lede" style="margin-top:34px">One from each class, one of each texture:</p>
    <div style="margin-top:16px" data-desaturable>{_dictation(spoken_examples)}</div>
    <p class="lede" style="margin-top:34px">And a real string, read straight through:</p>
    <div style="margin-top:16px" data-desaturable>{_dictation(dictation_sample)}</div>
  </section>

  <section>
    <p class="eyebrow">Without colour</p>
    <h2>The hatch carries it alone.</h2>
    <p class="lede" style="margin-top:14px">This section is set in <code>{MONO_FAMILY_NAME}</code>,
    which has no colour tables at all &mdash; nothing to strip, nothing to fall back from. The
    texture is doing all the work, and all sixty-four stay distinct. This is what a photocopy, a
    laser printer, or an e-ink screen gives you.</p>
    <div style="margin-top:26px">{_tier_key(MONO_CSS_CLASS)}</div>
    <p class="lede" style="margin-top:34px">All sixty-four, in value order:</p>
    <div class="mono-run {MONO_CSS_CLASS}" style="margin-top:14px">{html.escape(BASE64_ALPHABET)}</div>
    <p style="margin-top:26px">Ships as <code>SixtyFourMono-Regular.ttf</code> and
    <code>sixty-four-mono.css</code>. The colour font keeps these same outlines as its fallback, so
    a renderer that cannot do COLR lands here rather than on nothing.</p>
  </section>

  <section>
    <p class="eyebrow">At size</p>
    <h2>It holds down to body text.</h2>
    <div class="sizes" style="margin-top:28px" data-desaturable>{sizes}</div>
  </section>

  <section>
    <p class="eyebrow">If the font never loads</p>
    <h2>It degrades to itself.</h2>
    <p class="lede" style="margin-top:14px">Nothing here is an image, an icon set, or a
    substitution. The characters underneath are ordinary base64 &mdash; the font only changes how
    they are drawn. Take it away and you are left with exactly the string you started with, which
    is not true of any approach that swaps the text for pictures.</p>
    <div class="degrade" style="margin-top:26px">
      <div class="row">
        <span class="tag">With the font</span>
        <div class="text symbols {CSS_CLASS}" id="sf-degrade-symbols" data-desaturable>{degrade_sample}</div>
      </div>
      <div class="row">
        <span class="tag">Font unavailable &mdash; the same element, same characters</span>
        <div class="text plain">{degrade_sample}</div>
      </div>
    </div>
    <div class="controls" style="margin-top:18px">
      <button class="toggle" id="sf-copy" type="button">Copy the symbols</button>
      <span class="status" id="sf-copy-status" role="status" aria-live="polite"></span>
    </div>
    <div class="decode" style="margin-top:34px">
      <div class="step">
        <span class="k">Select and copy</span>
        <p>Drag across the symbols and you have selected base64. What lands on the clipboard is the
        string, not a row of pictures.</p>
      </div>
      <div class="step">
        <span class="k">Find in page</span>
        <p>Ctrl+F searches the real characters. So does your editor, your terminal, and
        <code>grep</code>.</p>
      </div>
      <div class="step">
        <span class="k">Screen readers</span>
        <p>Announce the base64 itself. There are no alt texts to write and none to get wrong.</p>
      </div>
      <div class="step">
        <span class="k">Everything else</span>
        <p>Diffs, logs, <code>curl</code>, a text field, a tool that has never heard of this font.
        The bytes never changed.</p>
      </div>
    </div>
  </section>

  <section>
    <p class="eyebrow">Using it</p>
    <h2>One file, no hosting.</h2>
    <div class="stack" style="margin-top:24px">
      <p><code>sixty-four.css</code> carries the font inside it as a data URI, so there is no
      second request and nothing to upload. Link it and add the class.</p>
      <pre>&lt;link rel="stylesheet" href="sixty-four.css"&gt;

&lt;span class="{CSS_CLASS}"&gt;{html.escape(_encoded_sample()[:24])}&lt;/span&gt;</pre>
      <p>Outside the browser, install <code>SixtyFour-Regular.ttf</code> and set it as the font in
      any editor or terminal &mdash; every glyph is one em wide, so columns stay aligned.
      Where colour fonts are not supported the same file falls back to the hatched outlines rather
      than to nothing. <code>{MONO_FAMILY_NAME}</code> ships separately for anywhere that prefers
      no colour table at all.</p>
      <p>URL-safe base64 works too: {alias_list} map onto the same symbols as
      {standard_list}, so JWTs and file-safe encodings need no conversion.</p>
    </div>
  </section>

{downloads_block}  <section>
    <p class="eyebrow">Reference</p>
    <h2>All sixty-four.</h2>
    <div style="margin-top:24px" data-desaturable>{_full_table()}</div>
  </section>

  <footer>
    Sixty Four &middot; {len(BASE64_ALPHABET)} symbols across {len(CLASSES)} classes &middot;
    colour and hatch carry the same information, on purpose.
  </footer>
</div>

<script>{_script()}</script>
"""


def _encoded_sample() -> str:
    return base64.b64encode(SAMPLE_TEXT.encode("utf-8")).decode("ascii")


def specimen_html(
    woff2: Path, mono_woff2: Path, standalone: bool = True, downloads: str = ""
) -> str:
    """The specimen page.

    `standalone` wraps it in a full document; an Artifact supplies its own
    skeleton and takes the body alone. `downloads` is only ever passed for a
    hosted page -- an Artifact viewer cannot save a file the page offers it.
    """
    body = _body(woff2, mono_woff2, downloads)
    if not standalone:
        return f"<title>{PAGE_TITLE}</title>\n{body}"
    description = html.escape(DESCRIPTION)
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{PAGE_TITLE}</title>\n"
        f'<meta name="description" content="{description}">\n'
        f'<meta property="og:title" content="{PAGE_TITLE}">\n'
        f'<meta property="og:description" content="{description}">\n'
        '<meta property="og:type" content="website">\n'
        '<meta property="og:image" content="specimen.png">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        "</head>\n<body>\n"
        f"{body}\n</body>\n</html>\n"
    )


def write_all(out_dir: Path, color_woff2: Path, mono_woff2: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []

    css = out_dir / "sixty-four.css"
    css.write_text(font_face_css(color_woff2, FAMILY_NAME, CSS_CLASS), encoding="utf-8")
    written.append(css)

    mono_css = out_dir / "sixty-four-mono.css"
    mono_css.write_text(
        font_face_css(mono_woff2, MONO_FAMILY_NAME, f"{CSS_CLASS}-mono", dark_palette=False),
        encoding="utf-8",
    )
    written.append(mono_css)

    page = out_dir / "specimen.html"
    page.write_text(specimen_html(color_woff2, mono_woff2, standalone=True), encoding="utf-8")
    written.append(page)
    return written


#: Everything the hosted site serves alongside the page itself.
PAGES_ASSETS = [name for _, _, names in DOWNLOAD_BUNDLES for name in names] + [
    "specimen.png",
    "grounds.png",
]


def write_pages(docs_dir: Path, dist_dir: Path) -> list[Path]:
    """A GitHub Pages site: the specimen plus every file it offers for download.

    Everything is flat in the one directory, so the `href="sixty-four.css"` in
    the page's own install snippet is literally true of the page serving it.
    """
    docs_dir.mkdir(parents=True, exist_ok=True)
    written = []

    for name in PAGES_ASSETS:
        source = dist_dir / name
        if not source.is_file():
            continue
        target = docs_dir / name
        target.write_bytes(source.read_bytes())
        written.append(target)

    index = docs_dir / "index.html"
    index.write_text(
        specimen_html(
            dist_dir / "SixtyFour-Regular.woff2",
            dist_dir / "SixtyFourMono-Regular.woff2",
            standalone=True,
            downloads=_downloads(docs_dir),
        ),
        encoding="utf-8",
    )
    written.append(index)

    # Without this, Pages runs the files through Jekyll, which ignores paths
    # beginning with an underscore and can rewrite what it thinks is templating.
    nojekyll = docs_dir / ".nojekyll"
    nojekyll.write_text("", encoding="utf-8")
    written.append(nojekyll)
    return written
