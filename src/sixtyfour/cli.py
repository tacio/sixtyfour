"""One command that builds everything shippable."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path

from . import fontbuild, render, svgout, web
from .spec import REPO_ROOT, as_records

SVG_DIR = REPO_ROOT / "svg"
DIST_DIR = REPO_ROOT / "dist"
#: GitHub Pages serves from /docs on the default branch with no extra config.
DOCS_DIR = REPO_ROOT / "docs"

COLOR_STEM = "SixtyFour-Regular"
MONO_STEM = "SixtyFourMono-Regular"


def write_mapping(out_dir: Path) -> list[Path]:
    """The alphabet as machine-readable data, for anyone writing their own renderer."""
    records = as_records()
    out_dir.mkdir(parents=True, exist_ok=True)

    as_json = out_dir / "mapping.json"
    as_json.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")

    as_tsv = out_dir / "mapping.tsv"
    with as_tsv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(records[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(records)
    return [as_json, as_tsv]


def build(
    svg_dir: Path = SVG_DIR,
    dist_dir: Path = DIST_DIR,
    docs_dir: Path = DOCS_DIR,
    clean: bool = False,
) -> list[Path]:
    if clean:
        for stale in (dist_dir, docs_dir):
            if stale.exists():
                shutil.rmtree(stale)
    written: list[Path] = []

    written += svgout.write_all(svg_dir)
    written += fontbuild.build_color(dist_dir, COLOR_STEM)
    written += fontbuild.build_mono(dist_dir, MONO_STEM)
    written += write_mapping(dist_dir)

    color_woff2 = dist_dir / f"{COLOR_STEM}.woff2"
    mono_woff2 = dist_dir / f"{MONO_STEM}.woff2"
    written += web.write_all(dist_dir, color_woff2, mono_woff2)

    specimen_png = dist_dir / "specimen.png"
    color_ttf = dist_dir / f"{COLOR_STEM}.ttf"
    render.contact_sheet(color_ttf, cell=104, color=True).save(specimen_png)
    written.append(specimen_png)

    grounds_png = dist_dir / "grounds.png"
    render.grounds_sheet(color_ttf).save(grounds_png)
    written.append(grounds_png)

    written += web.write_pages(docs_dir, dist_dir)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Sixty Four font and its assets.")
    parser.add_argument("--svg-dir", type=Path, default=SVG_DIR)
    parser.add_argument("--dist-dir", type=Path, default=DIST_DIR)
    parser.add_argument("--docs-dir", type=Path, default=DOCS_DIR)
    parser.add_argument("--clean", action="store_true", help="empty dist/ and docs/ first")
    args = parser.parse_args()

    written = build(args.svg_dir, args.dist_dir, args.docs_dir, args.clean)
    svgs = sum(1 for p in written if p.suffix == ".svg")
    print(f"{svgs} SVGs -> {args.svg_dir}")
    for path in written:
        if path.suffix != ".svg":
            print(f"  {path.stat().st_size:9,d}  {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
