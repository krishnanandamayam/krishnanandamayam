"""Read and write data/grantha.yaml, the ground truth.

Writing goes through ruamel's round-trip mode, so saving one verse from the editor leaves every
other line of the file byte-for-byte as it was and `git diff` shows only what was edited.
"""

from __future__ import annotations

import re
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
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


class DataFileError(Exception):
    """grantha.yaml cannot be read. `conflicts` lists unresolved git merge hunks, if that is why."""

    def __init__(self, message: str, conflicts: list[dict] | None = None):
        super().__init__(message)
        self.conflicts = conflicts or []


_MARKER = re.compile(r"^(<<<<<<< |=======$|>>>>>>> )", re.M)


def conflicts_in(text: str) -> list[dict]:
    """Unresolved merge hunks: the line each starts on and the verse (entry id) it sits in."""
    lines = text.splitlines()
    out = []
    for i, ln in enumerate(lines):
        if ln.startswith("<<<<<<< "):
            entry = next((m.group(1) for j in range(i - 1, -1, -1) if (m := re.match(r"\s*(?:- )?id: (\S+)", lines[j]))), None)
            out.append({"line": i + 1, "id": entry})
    return out


def load(path: Path = GRANTHA):
    text = path.read_text(encoding="utf-8")
    if _MARKER.search(text):
        hunks = conflicts_in(text)
        raise DataFileError(f"{path.name} has {len(hunks)} unresolved merge conflict(s)", hunks)
    try:
        return _yaml().load(text)
    except YAMLError as err:
        raise DataFileError(f"{path.name} is not valid YAML: {err}") from err


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


_INLINE_HK = re.compile(r"(?<!\\)\$[^$\n]+?(?<!\\)\$")
_TELUGU = re.compile(r"[\u0c00-\u0c7f]")
_LATIN = re.compile(r"[A-Za-z]")


def wrong_language(field: str, value: str) -> str | None:
    """Why this text cannot be saved in this meaning field, or None when it can.

    `en` is the English meaning and `te` the Telugu one; a meaning pasted into the other box
    is refused. Inline ``$hk$`` runs are Harvard-Kyoto in either field and are not counted.
    """
    body = _INLINE_HK.sub("", value or "")
    telugu, latin = len(_TELUGU.findall(body)), len(_LATIN.findall(body))
    if field == "en" and telugu:
        return "the English meaning has Telugu text in it"
    if field == "te" and latin > telugu:
        return "the Telugu meaning is not in Telugu"
    return None
