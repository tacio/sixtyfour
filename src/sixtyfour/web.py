"""The shipped CSS and the specimen page.

The page is generated from the same table as the font, so a change to the
alphabet cannot leave the documentation behind.
"""

from __future__ import annotations

import base64
import html
from pathlib import Path

from .spec import BASE64_ALPHABET, CLASSES, FILLS, SILHOUETTES, TABLE, URLSAFE_ALIASES
from .ufobuild import DESCRIPTION, FAMILY_NAME, MONO_FAMILY_NAME

CSS_CLASS = "sixty-four"
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

footer {
  border-top: 1px solid var(--rule); padding-top: 28px;
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: .76rem; color: var(--muted);
}

@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}
"""


def _swatch_colour(fill: str) -> str:
    return {"none": "var(--ink)", "solid": "var(--ink)", "dots": "var(--blue)", "lines": "var(--red)"}[fill]


def _matrix() -> str:
    heads = "".join(f"<th>{html.escape(name)}</th>" for name in SILHOUETTES)
    rows = []
    for fill_index, fill in enumerate(FILLS):
        colour, hatch = TABLE[fill_index * 16].color_name, TABLE[fill_index * 16].hatch_name
        cells = []
        for column in range(16):
            entry = TABLE[fill_index * 16 + column]
            title = f"{entry.char} = {entry.value} · {entry.klass} / {entry.symbol} · {entry.color_name} / {entry.hatch_name}"
            cells.append(
                f'<td><div class="cell" tabindex="0" title="{html.escape(title)}">'
                f'<span class="sym {CSS_CLASS}">{html.escape(entry.char)}</span>'
                f'<span class="meta"><b>{html.escape(entry.char)}</b> {entry.value}</span>'
                f"</div></td>"
            )
        rows.append(
            f'<tr><th class="row-head">{html.escape(colour)}<br>{html.escape(hatch)}</th>'
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
            f'<td><span class="swatch"><i style="background:{_swatch_colour(entry.fill)}"></i>'
            f"{html.escape(entry.color_name)}</span></td>"
            f"<td>{html.escape(entry.hatch_name)}</td>"
            f'<td class="mono">{alias_cell}</td>'
            f"</tr>"
        )
    heads = "".join(
        f"<th>{h}</th>"
        for h in ("Symbol", "Char", "Value", "Codepoint", "Class", "Shape", "Colour", "Hatch", "URL-safe")
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
        "Character, value, class, shape, colour and hatch for all 64, for writing your "
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


def _body(woff2: Path, downloads: str = "") -> str:
    walk = TABLE[41]  # 'p' -- Flame, dots. A worked example with every field distinct.
    sizes = "".join(
        f'<div class="size-row"><span class="tag">{px}px</span>'
        f'<span class="run {CSS_CLASS}" style="font-size:{px}px">{html.escape(_encoded_sample())}</span></div>'
        for px in (14, 20, 32, 56)
    )
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
.{CSS_CLASS} {{
  font-family: "{FAMILY_NAME}", ui-monospace, monospace;
  font-variant-ligatures: none;
  font-feature-settings: "liga" 0, "clig" 0, "calt" 0;
  word-break: break-all;
}}
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
        <span class="v">{html.escape(walk.hatch_name)} &middot; {html.escape(walk.color_name)}</span>
        <p>Tier {walk.value // 16} of 0&ndash;3. Colour and hatch say the same thing, so either one on its own is enough to read it.</p>
      </div>
      <div class="step">
        <span class="k">Therefore</span>
        <span class="v"><code>{html.escape(walk.char)}</code> = {walk.value}</span>
        <p>{walk.value // 16} &times; 16 + {(walk.value // 4) % 4} &times; 4 + {walk.value % 4} = {walk.value}</p>
      </div>
    </div>
  </section>

  <section>
    <p class="eyebrow">At size</p>
    <h2>It holds down to body text.</h2>
    <div class="sizes" style="margin-top:28px" data-desaturable>{sizes}</div>
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


def specimen_html(woff2: Path, standalone: bool = True, downloads: str = "") -> str:
    """The specimen page.

    `standalone` wraps it in a full document; an Artifact supplies its own
    skeleton and takes the body alone. `downloads` is only ever passed for a
    hosted page -- an Artifact viewer cannot save a file the page offers it.
    """
    body = _body(woff2, downloads)
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
    page.write_text(specimen_html(color_woff2, standalone=True), encoding="utf-8")
    written.append(page)
    return written


#: Everything the hosted site serves alongside the page itself.
PAGES_ASSETS = [name for _, _, names in DOWNLOAD_BUNDLES for name in names] + ["specimen.png"]


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
