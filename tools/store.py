"""Read and write data/grantha.yaml, the ground truth.

Writing goes through ruamel's round-trip mode, so saving one verse from the editor leaves every
other line of the file byte-for-byte as it was and `git diff` shows only what was edited.
"""

from __future__ import annotations

from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString

ROOT = Path(__file__).resolve().parent.parent
GRANTHA = ROOT / "data" / "grantha.yaml"


def _yaml() -> YAML:
    y = YAML()  # round-trip
    y.width = 100_000  # never re-wrap a long line
    y.indent(mapping=2, sequence=4, offset=2)
    y.preserve_quotes = True
    return y


def text(s: str):
    """A string as it should sit in the file: block literal when it has line breaks."""
    s = (s or "").strip("\n")
    return LiteralScalarString(s) if "\n" in s else s


def load(path: Path = GRANTHA):
    with path.open(encoding="utf-8") as f:
        return _yaml().load(f)


def save(doc, path: Path = GRANTHA) -> None:
    tmp = path.with_suffix(".yaml.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        _yaml().dump(doc, f)
    tmp.replace(path)


def entries(doc):
    """Every editable entry: preface blocks first, then sections and verses, in reading order."""
    for lang in ("en", "te"):
        for block in doc["prefaces"][lang]["blocks"]:
            yield block
    yield from doc["items"]


def find(doc, entry_id: str):
    for e in entries(doc):
        if e["id"] == entry_id:
            return e
    raise KeyError(entry_id)


def set_title(verse, title: str) -> None:
    """A verse's own header (HK). Kept just before `hk`; the key is absent when there is none."""
    title = (title or "").strip()
    if not title:
        verse.pop("title", None)
    elif "title" in verse:
        verse["title"] = title
    else:
        keys = list(verse.keys())
        verse.insert(keys.index("hk") if "hk" in keys else len(keys), "title", title)
