"""The 64-symbol alphabet.

The whole system is a 4x4x4 matrix::

    value = fill * 16 + klass * 4 + symbol

`Cyphenture entities - base64.tsv` is the authority for the naming; this module
derives the table from the formula and checks the two agree row for row.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TSV_PATH = REPO_ROOT / "Cyphenture entities - base64.tsv"

#: Standard base64 alphabet, in value order (RFC 4648 section 4).
BASE64_ALPHABET = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "abcdefghijklmnopqrstuvwxyz" "0123456789+/"
)

#: URL-safe base64 substitutes '+' -> '-' and '/' -> '_' (RFC 4648 section 5).
URLSAFE_ALIASES = {"-": "+", "_": "/"}

PAD_CHAR = "="

#: The four fill treatments, in value order. Index is `value // 16`.
FILLS = ("none", "solid", "dots", "lines")
FILL_LABELS = {
    "none": ("White", "No fill"),
    "solid": ("Black", "Total fill"),
    "dots": ("Blue", "Dots"),
    "lines": ("Red", "Line"),
}

#: The four classes of four symbols each. Index is `(value // 4) % 4`.
CLASSES = ("Shapes", "Suits", "Elements", "Powers")
SYMBOLS = {
    "Shapes": ("Cross", "Circle", "Triangle", "Square"),
    "Suits": ("Clubs", "Diamonds", "Hearts", "Spades"),
    "Elements": ("Drop", "Flame", "Cloud", "Ingot"),
    "Powers": ("Mushroom", "Flower", "Star", "Moon"),
}

#: All 16 silhouette names in class order, i.e. indexed by `value % 16`.
SILHOUETTES = tuple(sym for klass in CLASSES for sym in SYMBOLS[klass])


@dataclass(frozen=True)
class Entry:
    """One of the 64 data symbols."""

    value: int
    char: str
    klass: str
    symbol: str
    fill: str

    @property
    def codepoint(self) -> int:
        return ord(self.char)

    @property
    def color_name(self) -> str:
        return FILL_LABELS[self.fill][0]

    @property
    def hatch_name(self) -> str:
        return FILL_LABELS[self.fill][1]

    @property
    def glyph_name(self) -> str:
        """e.g. ``cross.none``, ``moon.lines`` -- stable and human-readable."""
        return f"{self.symbol.lower()}.{self.fill}"

    @property
    def svg_filename(self) -> str:
        """nanoemoji-style ``u0041.svg``, the convention this repo started with."""
        return f"u{self.codepoint:04X}.svg"


def build_table() -> tuple[Entry, ...]:
    """Derive all 64 entries from ``value = fill*16 + klass*4 + symbol``."""
    entries = []
    for value, char in enumerate(BASE64_ALPHABET):
        fill = FILLS[value // 16]
        klass = CLASSES[(value // 4) % 4]
        symbol = SYMBOLS[klass][value % 4]
        entries.append(Entry(value=value, char=char, klass=klass, symbol=symbol, fill=fill))
    return tuple(entries)


TABLE: tuple[Entry, ...] = build_table()
BY_CHAR: dict[str, Entry] = {e.char: e for e in TABLE}


def read_tsv(path: Path | None = None) -> list[dict[str, str]]:
    """Read the spec sheet, skipping the '=' padding row which carries no symbol."""
    path = path or TSV_PATH
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    return [r for r in rows if r["Char"] != PAD_CHAR]


def check_against_tsv(path: Path | None = None) -> list[str]:
    """Return a list of disagreements between the derived table and the TSV.

    Empty list means the spec sheet and the formula agree everywhere.
    """
    problems: list[str] = []
    rows = read_tsv(path)
    if len(rows) != len(TABLE):
        problems.append(f"TSV has {len(rows)} symbol rows, expected {len(TABLE)}")

    for row, entry in zip(rows, TABLE):
        where = f"value {entry.value} ({entry.char})"
        if row["Char"] != entry.char:
            problems.append(f"{where}: TSV char is {row['Char']!r}")
            continue
        if int(row["Value"]) != entry.value:
            problems.append(f"{where}: TSV value is {row['Value']}")
        if row["Class"] != entry.klass:
            problems.append(f"{where}: TSV class {row['Class']!r} != {entry.klass!r}")
        if row["Symbol"] != entry.symbol:
            problems.append(f"{where}: TSV symbol {row['Symbol']!r} != {entry.symbol!r}")
        if row["Color"] != entry.color_name:
            problems.append(f"{where}: TSV color {row['Color']!r} != {entry.color_name!r}")
        if row["Hatch"] != entry.hatch_name:
            problems.append(f"{where}: TSV hatch {row['Hatch']!r} != {entry.hatch_name!r}")
        if int(row["Unicode"], 16) != entry.codepoint:
            problems.append(f"{where}: TSV unicode {row['Unicode']!r} != {entry.codepoint:04X}")
    return problems


def as_records() -> list[dict[str, object]]:
    """The alphabet as plain data, for the shipped mapping files."""
    records = []
    for entry in TABLE:
        record = {
            "value": entry.value,
            "char": entry.char,
            "codepoint": f"U+{entry.codepoint:04X}",
            "class": entry.klass,
            "symbol": entry.symbol,
            "color": entry.color_name,
            "hatch": entry.hatch_name,
            "fill": entry.fill,
            "glyph": entry.glyph_name,
            "svg": entry.svg_filename,
        }
        aliases = [a for a, standard in URLSAFE_ALIASES.items() if standard == entry.char]
        # Present on every row, empty where there is none, so the TSV stays rectangular.
        record["urlsafe_alias"] = aliases[0] if aliases else ""
        records.append(record)
    return records
