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


def build(svg_dir: Path = SVG_DIR, dist_dir: Path = DIST_DIR, clean: bool = False) -> list[Path]:
    if clean and dist_dir.exists():
        shutil.rmtree(dist_dir)
    written: list[Path] = []

    written += svgout.write_all(svg_dir)
    written += fontbuild.build_color(dist_dir, COLOR_STEM)
    written += fontbuild.build_mono(dist_dir, MONO_STEM)
    written += write_mapping(dist_dir)

    color_woff2 = dist_dir / f"{COLOR_STEM}.woff2"
    mono_woff2 = dist_dir / f"{MONO_STEM}.woff2"
    written += web.write_all(dist_dir, color_woff2, mono_woff2)

    specimen_png = dist_dir / "specimen.png"
    render.contact_sheet(dist_dir / f"{COLOR_STEM}.ttf", cell=104, color=True).save(specimen_png)
    written.append(specimen_png)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Sixty Four font and its assets.")
    parser.add_argument("--svg-dir", type=Path, default=SVG_DIR)
    parser.add_argument("--dist-dir", type=Path, default=DIST_DIR)
    parser.add_argument("--clean", action="store_true", help="empty dist/ first")
    args = parser.parse_args()

    written = build(args.svg_dir, args.dist_dir, args.clean)
    svgs = sum(1 for p in written if p.suffix == ".svg")
    print(f"{svgs} SVGs -> {args.svg_dir}")
    for path in written:
        if path.suffix != ".svg":
            print(f"  {path.stat().st_size:9,d}  {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
