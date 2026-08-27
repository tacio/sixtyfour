"""What has to hold for the alphabet to do its job.

The first tests are structural. The last three test the actual design goal --
that a person can tell sixty-four symbols apart, in colour and without it.
"""

from __future__ import annotations

import base64
import hashlib
import itertools
import re
import string
from pathlib import Path

import pytest
from fontTools.ttLib import TTFont
from PIL import ImageChops, ImageStat

from sixtyfour import glyphs, render, spec, web
from sixtyfour.cli import COLOR_STEM, DIST_DIR, DOCS_DIR, MONO_STEM
from sixtyfour.spec import BASE64_ALPHABET, FILLS, SILHOUETTES, TABLE
from sixtyfour.ufobuild import ADVANCE

COLOR_TTF = DIST_DIR / f"{COLOR_STEM}.ttf"
MONO_TTF = DIST_DIR / f"{MONO_STEM}.ttf"

#: Ink order, which is not value order: the tiers ramp none < lines < dots < solid.
INK_ORDER = ("none", "lines", "dots", "solid")

pytestmark = pytest.mark.skipif(
    not COLOR_TTF.exists(), reason="run `uv run sixty-four-build` first"
)


@pytest.fixture(scope="module")
def color_font() -> TTFont:
    return TTFont(COLOR_TTF)


@pytest.fixture(scope="module")
def mono_font() -> TTFont:
    return TTFont(MONO_TTF)


# --- 1. spec integrity -------------------------------------------------------


def test_table_has_64_entries():
    assert len(TABLE) == 64
    assert len({e.char for e in TABLE}) == 64
    assert "".join(e.char for e in TABLE) == BASE64_ALPHABET


def test_value_decomposes_into_tier_class_and_shape():
    for entry in TABLE:
        tier = FILLS.index(entry.fill)
        klass = spec.CLASSES.index(entry.klass)
        shape = spec.SYMBOLS[entry.klass].index(entry.symbol)
        assert entry.value == tier * 16 + klass * 4 + shape


def test_table_agrees_with_the_spec_sheet():
    assert spec.check_against_tsv() == []


# --- 2. metrics --------------------------------------------------------------


def test_every_glyph_is_one_em_wide(color_font):
    widths = {name: color_font["hmtx"][name][0] for name in color_font.getGlyphOrder()}
    assert set(widths.values()) == {ADVANCE}


def test_declared_monospaced(color_font):
    assert color_font["post"].isFixedPitch == 1
    assert color_font["head"].unitsPerEm == ADVANCE


def test_vertical_metrics_agree_across_the_three_schemes(color_font):
    os2, hhea = color_font["OS/2"], color_font["hhea"]
    assert hhea.ascender == os2.sTypoAscender == os2.usWinAscent
    assert hhea.descender == os2.sTypoDescender == -os2.usWinDescent


# --- 3. coverage -------------------------------------------------------------


def test_cmap_covers_base64_padding_urlsafe_and_space(color_font):
    cmap = color_font.getBestCmap()
    required = string.ascii_letters + string.digits + "+/=-_ "
    assert [c for c in required if ord(c) not in cmap] == []
    assert 0x00A0 in cmap  # non-breaking space, so chunked base64 stays aligned


def test_urlsafe_aliases_share_a_glyph_with_their_standard_form(color_font):
    cmap = color_font.getBestCmap()
    for alias, standard in spec.URLSAFE_ALIASES.items():
        assert cmap[ord(alias)] == cmap[ord(standard)]


def test_colr_covers_exactly_the_64_and_cpal_has_both_palettes(color_font):
    colr, cpal = color_font["COLR"], color_font["CPAL"]
    assert colr.version == 0
    assert set(colr.ColorLayers) == {e.glyph_name for e in TABLE}
    assert len(cpal.palettes) == 2


def test_empty_and_solid_tiers_follow_the_text_colour(color_font):
    """Palette index 0xFFFF means "use the foreground", which is what keeps the
    uncoloured tiers visible on a dark background."""
    layers = color_font["COLR"].ColorLayers
    for entry in TABLE:
        colour_ids = {record.colorID for record in layers[entry.glyph_name]}
        if entry.fill in ("none", "solid"):
            assert colour_ids == {0xFFFF}
        else:
            assert colour_ids != {0xFFFF}


def test_colour_font_keeps_fallback_outlines(color_font):
    """A renderer with no COLR support must get the hatched artwork, not blank."""
    glyf = color_font["glyf"]
    for entry in TABLE:
        assert glyf[entry.glyph_name].numberOfContours > 0


def test_mono_font_carries_no_colour_tables(mono_font):
    assert "COLR" not in mono_font
    assert "CPAL" not in mono_font


def test_no_substitution_features_can_fuse_two_symbols(color_font):
    """Two data symbols must never render as one, or the byte count stops being
    countable by eye."""
    if "GSUB" not in color_font:
        return
    features = {r.FeatureTag for r in color_font["GSUB"].table.FeatureList.FeatureRecord}
    assert features.isdisjoint({"liga", "clig", "calt", "rlig", "dlig"})


# --- 4. uniqueness -----------------------------------------------------------


def test_all_64_outlines_are_distinct(color_font):
    """The hand-drawn originals had four files sharing identical path data,
    differing only by a fill colour. That must not come back."""
    glyf, seen = color_font["glyf"], {}
    for entry in TABLE:
        pen_points = tuple(glyf[entry.glyph_name].getCoordinates(glyf)[0])
        assert pen_points not in seen, f"{entry.glyph_name} duplicates {seen.get(pen_points)}"
        seen[pen_points] = entry.glyph_name


def test_padding_shares_no_silhouette_with_the_alphabet(color_font):
    glyf = color_font["glyf"]
    padding = tuple(glyf["equal"].getCoordinates(glyf)[0])
    for entry in TABLE:
        assert padding != tuple(glyf[entry.glyph_name].getCoordinates(glyf)[0])


# --- 5. the ink ramp ---------------------------------------------------------


@pytest.mark.parametrize("shape_index,shape", list(enumerate(SILHOUETTES)))
def test_hatch_alone_separates_the_four_tiers(shape_index, shape):
    """With the colour discarded, the four tiers of one shape must still ramp
    none < lines < dots < solid. This is the whole reason to carry a hatch."""
    ink = {
        fill: render.ink(COLOR_TTF, BASE64_ALPHABET[FILLS.index(fill) * 16 + shape_index], 48)
        for fill in FILLS
    }
    ramp = [ink[fill] for fill in INK_ORDER]
    assert ramp == sorted(ramp), f"{shape}: " + ", ".join(f"{f}={ink[f]:.3f}" for f in INK_ORDER)
    # And the ends must be well apart, not merely ordered.
    assert ramp[-1] - ramp[0] > 0.06, f"{shape}: ramp spans only {ramp[-1] - ramp[0]:.3f}"


def test_geometry_ramp_matches_the_rasterised_one():
    for shape in SILHOUETTES:
        areas = [glyphs.build(shape, fill).area for fill in INK_ORDER]
        assert areas == sorted(areas), shape


# --- 6. small-size distinguishability ----------------------------------------


#: RMS difference, 0-255, below which two glyphs are too alike to trust at 16px
#: with the colour stripped -- the worst case this font is asked to survive.
CONFUSION_FLOOR = 30.0


def test_no_two_symbols_collapse_together_at_small_size():
    bitmaps = {c: render.glyph_bitmap(COLOR_TTF, c, 16).convert("L") for c in BASE64_ALPHABET}
    worst = min(
        (ImageStat.Stat(ImageChops.difference(bitmaps[a], bitmaps[b])).rms[0], a, b)
        for a, b in itertools.combinations(BASE64_ALPHABET, 2)
    )
    distance, a, b = worst
    assert distance >= CONFUSION_FLOOR, f"{a!r} and {b!r} differ by only {distance:.1f} at 16px"


# --- 7. round trip -----------------------------------------------------------


def test_real_base64_renders_with_no_missing_glyphs(color_font):
    encoded = base64.b64encode(bytes(range(256))).decode("ascii")
    cmap = color_font.getBestCmap()
    assert [c for c in encoded if ord(c) not in cmap] == []


def test_urlsafe_base64_renders_with_no_missing_glyphs(color_font):
    encoded = base64.urlsafe_b64encode(bytes(range(256))).decode("ascii")
    cmap = color_font.getBestCmap()
    assert [c for c in encoded if ord(c) not in cmap] == []


def test_every_svg_was_written():
    svg_dir = Path(spec.REPO_ROOT) / "svg"
    for entry in TABLE:
        assert (svg_dir / entry.svg_filename).is_file()
    assert (svg_dir / "u003D.svg").is_file()


# --- 8. the hosted page ------------------------------------------------------


@pytest.fixture(scope="module")
def pages_html() -> str:
    return (DOCS_DIR / "index.html").read_text(encoding="utf-8")


def test_pages_site_has_an_index_and_opts_out_of_jekyll():
    assert (DOCS_DIR / "index.html").is_file()
    # Without .nojekyll, Pages drops anything whose path starts with an underscore.
    assert (DOCS_DIR / ".nojekyll").exists()


def test_every_advertised_asset_is_actually_served():
    for name in web.PAGES_ASSETS:
        served, built = DOCS_DIR / name, DIST_DIR / name
        assert served.is_file(), f"{name} is offered but not present in docs/"
        assert served.read_bytes() == built.read_bytes(), f"{name} is stale against dist/"


def test_no_link_on_the_page_points_at_a_missing_file(pages_html):
    hrefs = re.findall(r'href="([^"]+)"', pages_html)
    local = [h for h in hrefs if not h.startswith(("http://", "https://", "#", "mailto:"))]
    assert local, "expected the page to link its own downloads"
    assert [h for h in local if not (DOCS_DIR / h).is_file()] == []


def test_page_is_self_contained_apart_from_the_font_host(pages_html):
    """Everything needed to render must ship with the site. The one exception is
    Google Fonts, which degrades to the declared fallback stacks if blocked."""
    hosts = set(re.findall(r"https?://([^/\"\')]+)", pages_html))
    assert hosts <= {"fonts.googleapis.com"}
    assert "data:font/woff2;base64," in pages_html


def test_page_defines_every_colour_token_outside_the_dark_blocks(pages_html):
    """The classic unreadable-artifact bug: a colour whose only definition sits
    behind a media query never applies when the OS reports no preference."""
    style = "\n".join(re.findall(r"<style>(.*?)</style>", pages_html, re.S))
    root = set(re.findall(r"(--[a-z-]+)\s*:", re.search(r":root\s*\{(.*?)\}", style, re.S).group(1)))
    dark_blocks = re.findall(
        r'(?:@media \(prefers-color-scheme: dark\)|:root\[data-theme="dark"\])\s*\{(.*?)\n\}',
        style,
        re.S,
    )
    assert dark_blocks, "expected a dark theme"
    defined_in_dark = set()
    for block in dark_blocks:
        defined_in_dark |= set(re.findall(r"(--[a-z-]+)\s*:", block))
    assert defined_in_dark - root - {"--sf-dark"} == set()


def test_artifact_variant_offers_no_downloads():
    """An Artifact viewer is sandboxed against downloads the page starts itself,
    so the section must never reach that build."""
    body = web.specimen_html(DIST_DIR / f"{COLOR_STEM}.woff2", standalone=False)
    assert "download" not in body
    assert "<!doctype" not in body.lower()


# --- 9. reproducibility ------------------------------------------------------


def test_two_builds_produce_byte_identical_fonts(tmp_path):
    """dist/ and docs/ are committed, so a rebuild that changes nothing must
    change nothing. Left alone, fontTools stamps head.modified at save time and
    every run would show as a binary diff."""
    from sixtyfour import fontbuild

    first, second = tmp_path / "one", tmp_path / "two"
    digests = []
    for out in (first, second):
        built = fontbuild.build_color(out) + fontbuild.build_mono(out)
        digests.append({p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in built})
    assert digests[0] == digests[1]
