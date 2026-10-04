"""Harvard-Kyoto text handling: the alphabet, a lint, line/danda splitting, and the two
anusvara conventions.

`to_zuddha` and `to_saraLa` are pure HK -> HK functions. Every change either makes is the
substitution of exactly one character by one character, so ``len(out) == len(hk)`` always.

Each rule has an id (``Z1``.., ``S1``..). tests/test_rule_coverage.py fails if a rule listed in
``RULES`` has no test tagged with its id, so a rule cannot be added here without tests.
"""

from __future__ import annotations

import re

# --------------------------------------------------------------------------------------
# Alphabet
# --------------------------------------------------------------------------------------

# varga -> (non-nasal stops, nasal). Stops are listed with their aspirates, but only the first
# letter of a stop decides its varga (kh, gh start with k, g), which is what the code uses.
VARGAS: dict[str, tuple[tuple[str, ...], str]] = {
    "ka": (("k", "kh", "g", "gh"), "G"),
    "ca": (("c", "ch", "j", "jh"), "J"),
    "Ta": (("T", "Th", "D", "Dh"), "N"),
    "ta": (("t", "th", "d", "dh"), "n"),
    "pa": (("p", "ph", "b", "bh"), "m"),
}

# first letter of a non-nasal stop -> the nasal of its varga
NASAL_OF_STOP: dict[str, str] = {
    stop[0]: nasal for stops, nasal in VARGAS.values() for stop in stops
}
NASALS = frozenset(nasal for _, nasal in VARGAS.values())  # G J N n m
ANUSVARA = "M"

VOWEL_LETTERS = frozenset("aAiIuUReoEO")  # every HK vowel ends in one of these letters
HK_LETTERS = frozenset("aAiIuUReoEOMHkgGcjJTDNtdnpbmyrlvzSshL")
# Letters that are not part of Harvard-Kyoto at all; the lint reports them.
NON_HK_LETTERS = frozenset("BCFKPQVWXYZfqwx")

_LETTER = re.compile(r"[A-Za-z]")


def _is_letter(ch: str) -> bool:
    return bool(ch) and bool(_LETTER.match(ch))


# The pranava is written with anusvara in every convention: never "om" with a final m.
_PRANAVA = re.compile(r"(?<![A-Za-z])o[Mm](?![A-Za-z])")


RULES: dict[str, str] = {
    "Z1": "M + non-nasal stop inside a word -> that varga's nasal (saMkaTa -> saGkaTa)",
    "Z2": "M + nasal inside a word -> that same nasal (saMmAna -> sammAna)",
    "Z3": "M before y r l L v z S s h (or any other non-stop letter) stays M",
    "Z4": "word-final M/m -> m, word break kept, whatever follows (rAmaM ca -> rAmam ca)",
    "Z5": "everything else is untouched",
    "Z6": "the pranava is always oM, never om",
    "S1": "varga nasal + non-nasal stop of its own varga, after a vowel -> M (gaGgA -> gaMgA)",
    "S2": "nasal + nasal is never touched (amma, anna, janma)",
    "S3": "nasal + consonant of another varga, or + non-stop, is never touched (jJAna, tanmaya)",
    "S4": "word-final m/M -> M, whatever follows",
    "S5": "everything else is untouched",
    "S6": "the pranava is always oM",
}


def _pranava_spans(hk: str) -> set[int]:
    """Indexes of the M/m of every standalone om/oM."""
    return {m.start() + 1 for m in _PRANAVA.finditer(hk)}


def to_zuddha(hk: str) -> str:
    """The zuddha (శుద్ధ) convention: class nasals written out, word-final m kept as m."""
    pranava = _pranava_spans(hk)
    out = list(hk)
    for i, ch in enumerate(hk):
        if ch not in ("M", "m"):
            continue
        if i in pranava:  # Z6
            out[i] = "M"
            continue
        nxt = hk[i + 1] if i + 1 < len(hk) else ""
        if not _is_letter(nxt):  # Z4: word-final
            out[i] = "m"
        elif ch == "M":
            if nxt in NASAL_OF_STOP:  # Z1
                out[i] = NASAL_OF_STOP[nxt]
            elif nxt in NASALS:  # Z2
                out[i] = nxt
            # Z3: anything else keeps the anusvara
    return "".join(out)


def to_saraLa(hk: str) -> str:
    """The saraLa (సరళ) convention: anusvara before a stop of the same varga, and word-finally."""
    pranava = _pranava_spans(hk)
    out = list(hk)
    for i, ch in enumerate(hk):
        if ch != "M" and ch not in NASALS:
            continue
        if i in pranava:  # S6
            out[i] = "M"
            continue
        nxt = hk[i + 1] if i + 1 < len(hk) else ""
        if not _is_letter(nxt):  # S4: word-final m / M
            if ch in ("m", "M"):
                out[i] = "M"
            continue
        if ch == "M":
            continue
        prev = hk[i - 1] if i > 0 else ""
        if prev in VOWEL_LETTERS and NASAL_OF_STOP.get(nxt) == ch:  # S1
            out[i] = "M"
        # S2 / S3: every other cluster is left alone
    return "".join(out)


# --------------------------------------------------------------------------------------
# Lines and dandas
# --------------------------------------------------------------------------------------

DANDA = "।"
DOUBLE_DANDA = "॥"

# A danda is "|" or a full stop that is not part of a number ("1." in a numbered list) and is
# followed by a space or the end; doubled, it is a double danda.
_PUNCT = re.compile(
    r"""
      (?P<dd>\|\s?\||(?<!\d)\.(?:\s?\.)+)       # ||  | |  ..  . .  ...
    | (?P<d>\||(?<!\d)\.(?=\s|$|["”’')\]]))     # |   .
    """,
    re.VERBOSE,
)


def token_spans(line: str) -> list[tuple[str, int, int]]:
    """Split one line into ("text" | "danda" | "ddanda", start, end) tokens."""
    tokens: list[tuple[str, int, int]] = []
    pos = 0
    for m in _PUNCT.finditer(line):
        if m.start() > pos:
            tokens.append(("text", pos, m.start()))
        tokens.append(("ddanda" if m.group("dd") else "danda", m.start(), m.end()))
        pos = m.end()
    if pos < len(line):
        tokens.append(("text", pos, len(line)))
    return tokens


def tokenize(line: str) -> list[tuple[str, str]]:
    """Split one line into ("text", s) / ("danda", "") / ("ddanda", "") tokens."""
    return [(kind, line[a:b] if kind == "text" else "") for kind, a, b in token_spans(line)]


Span = tuple[int, int]


def split_line_spans(hk: str) -> list[tuple[str, list[Span]]]:
    """The display lines of a verse, each with the (start, end) in ``hk`` of every character.

    The author's own line breaks are kept. A verse typed as one run-on paragraph is broken
    after each danda / double danda instead; the danda written at the end of such a line
    points back at the danda it was made from.
    """

    def trim(text: str, src: list[Span]) -> tuple[str, list[Span]]:
        lead = len(text) - len(text.lstrip())
        text = text.strip()
        return text, src[lead : lead + len(text)]

    lines: list[tuple[str, list[Span]]] = []
    pos = 0
    for raw in hk.split("\n"):
        if raw.strip():
            lines.append(trim(raw, [(pos + i, pos + i + 1) for i in range(len(raw))]))
        pos += len(raw) + 1
    if len(lines) > 1:
        return lines
    out: list[tuple[str, list[Span]]] = []
    for body, origin in lines:
        cur, src = "", []
        for kind, a, b in token_spans(body):
            if kind == "text":
                cur += body[a:b]
                src += origin[a:b]
            else:
                keep = len(cur.rstrip())
                mark = " ." if kind == "danda" else " .."
                cur = cur[:keep] + mark
                src = src[:keep] + [(origin[a][0], origin[b - 1][1])] * len(mark)
                out.append(trim(cur, src))
                cur, src = "", []
        if cur.strip():
            out.append(trim(cur, src))
    return out


def split_lines(hk: str) -> list[str]:
    """The display lines of a verse (see ``split_line_spans``)."""
    return [line for line, _ in split_line_spans(hk)]


# --------------------------------------------------------------------------------------
# Lint
# --------------------------------------------------------------------------------------


# real one- and two-letter words that can end a line
_SHORT_WORDS = frozenset("om oM ca me te tu na vA hi ha ya sa mA no".split())


def lint(hk: str) -> list[str]:
    """Human-readable findings about one HK text. Never changes anything."""
    found: list[str] = []
    bad = sorted({ch for ch in hk if ch in NON_HK_LETTERS})
    if bad:
        found.append("letters outside Harvard-Kyoto: " + " ".join(bad))
    if re.search(r"[A-Za-z]:(?=[A-Za-z]|\s|$)", hk) and re.search(r"[aAiIuUeo]:", hk):
        words = sorted(set(re.findall(r"[A-Za-z]+[aAiIuUeo]:(?!\s*\n)", hk)))[:6]
        if words:
            found.append("':' after a vowel, possibly a visarga typed as colon (use H): " + ", ".join(words))
    for m in re.finditer(r"(?<![A-Za-z])([A-Za-z]{1,2}) ?\. ([a-z]{2,})", hk):
        if m.group(1) not in _SHORT_WORDS:
            found.append(f"possible line-break residue inside a word: '{m.group(0)}'")
    if "\\" in hk:
        found.append("backslash in text")
    if to_zuddha(hk) != hk:
        found.append("not in zuddha form (run normalize)")
    return found
