"""Inline Harvard-Kyoto inside prose, written like inline math in LaTeX: ``$jIvAtma$``.

A prose field (a preface paragraph, an English or Telugu meaning) may mark any run of text as
HK by putting it between dollar signs. The marked run follows the reader's script choice like
a sloka does; everything else is shown as typed. A literal dollar sign is written ``\\$``.
"""

from __future__ import annotations

import re

_INLINE = re.compile(r"(?<!\\)\$([^$\n]+?)(?<!\\)\$")
PROSE_FIELDS = ("text", "en", "te")


def split(text: str) -> list[tuple[str, str]]:
    """``"the $jIva$ is"`` -> ``[("text", "the "), ("hk", "jIva"), ("text", " is")]``."""
    out: list[tuple[str, str]] = []
    pos = 0
    for m in _INLINE.finditer(text or ""):
        if m.start() > pos:
            out.append(("text", text[pos : m.start()].replace("\\$", "$")))
        out.append(("hk", m.group(1).strip()))
        pos = m.end()
    if pos < len(text or ""):
        out.append(("text", text[pos:].replace("\\$", "$")))
    return out


def fragments(text: str) -> list[str]:
    return [body for kind, body in split(text) if kind == "hk"]


def fragment_id(entry_id: str, field: str, n: int) -> str:
    return f"{entry_id}.{field}.{n}"


def entry_fragments(entry) -> list[tuple[str, str]]:
    """(id, hk) for every inline fragment in an entry's prose fields, in reading order."""
    out = []
    for field in PROSE_FIELDS:
        for n, hk in enumerate(fragments(str(entry.get(field) or ""))):
            out.append((fragment_id(entry["id"], field, n), hk))
    return out
