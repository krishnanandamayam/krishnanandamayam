"""One-time import: the Google Sheet export -> data/grantha.yaml (+ ISSUES.md, ZUDDHA_PASS.md).

Only the Harvard-Kyoto and English Translation columns are read as content. After this has run
and its output is committed, data/grantha.yaml is the ground truth and the sheet is history;
the script refuses to overwrite an existing grantha.yaml without --force.

    uv run python -m tools.import_sheet [--force]
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

import openpyxl

from tools import hk as HK
from tools import store

ROOT = store.ROOT
XLSX = ROOT / "data" / "source" / "krishnanandamayam-sheet.xlsx"
ISSUES = ROOT / "data" / "ISSUES.md"
ZUDDHA_PASS = ROOT / "data" / "ZUDDHA_PASS.md"

SECTION_TITLE_MAX = 70  # an unnumbered row with HK longer than this is an unnumbered verse


def clean(s) -> str:
    """Mechanical whitespace cleanup only; no letter is changed."""
    if s is None:
        return ""
    s = str(s).replace("\r\n", "\n").replace("\r", "\n").replace(" ", " ")
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in s.split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def number(no) -> str:
    if no is None:
        return ""
    if isinstance(no, float) and no.is_integer():
        return str(int(no))
    return re.sub(r"\s+", " ", str(no)).strip()


def slug(no: str) -> str:
    return re.sub(r"[^0-9A-Za-z]+", "-", no).strip("-")


def devanagari_to_hk(s: str) -> str:
    from aksharamukha import transliterate

    s = clean(s).strip("“”\"")
    s = re.sub(r"[।|]\s*[।|]|॥", " .. ", s)
    s = re.sub(r"[।|]", " . ", s)
    out = transliterate.process("Devanagari", "HK", s, nativize=False)
    return clean(out)


def import_main(ws, issues):
    items = []
    seen_hk: dict[str, str] = {}
    n_section = n_unnumbered = 0
    for row_no, row in enumerate(ws.iter_rows(values_only=True), 1):
        if row_no <= 3:  # link rows and the header
            continue
        no, hk, _sa, en, _te = row[:5]
        no, hk, en = number(no), clean(hk), clean(en)
        if not (no or hk or en):
            continue
        where = f"sheet row {row_no}" + (f", no. {no}" if no else "")
        if not hk or hk in ("(Telugu)",):
            issues["Rows with no Harvard-Kyoto text (not imported)"].append(
                f"{where}: HK cell is {hk!r}" + (f"; English: {en[:80]!r}" if en else "")
            )
            continue
        if not no and len(hk) <= SECTION_TITLE_MAX:
            n_section += 1
            items.append({"type": "section", "id": f"s{n_section:02d}", "hk": hk, "en": en})
            continue
        if no:
            vid = "v" + slug(no)
        else:
            n_unnumbered += 1
            vid = f"u{n_unnumbered}"
        if any(it["id"] == vid for it in items):
            issues["Duplicate verse numbers"].append(f"{where}: id {vid} already used; suffixed")
            vid += "-dup"
        key = re.sub(r"\s+", " ", hk)
        if key in seen_hk:
            issues["Verses whose HK is identical to an earlier verse"].append(
                f"{where} repeats no. {seen_hk[key]} word for word"
            )
        else:
            seen_hk[key] = no or vid
        if not en:
            issues["Verses with no English translation"].append(where)
        items.append({"type": "verse", "id": vid, "no": no, "hk": hk, "en": en, "te": ""})
    return items


def import_intro(ws, issues):
    blocks = []
    n = 0
    for row_no, row in enumerate(ws.iter_rows(values_only=True), 1):
        if row_no == 1:
            continue
        _no, _hk, sa, en, _te = row[:5]
        sa, en = clean(sa), clean(en)
        parts = []
        if sa:
            hk = devanagari_to_hk(sa)
            parts.append(("sloka", hk))
            issues["Preface slokas converted from Devanagari to HK (please check)"].append(
                f"Intro row {row_no}: `{hk.replace(chr(10), ' / ')}`"
            )
        if en:
            parts.append(("prose", en))
        if len(parts) == 2 and re.search(r"[-:]\s*$", en):  # "His declaration -" introduces it
            parts.reverse()
        for kind, body in parts:
            n += 1
            block = {"type": kind, "id": f"pe{n:02d}"}
            block["hk" if kind == "sloka" else "text"] = body
            blocks.append(block)
    return blocks


def zuddha_pass(doc, report):
    for e in store.entries(doc):
        if "hk" not in e:
            continue
        before = e["hk"]
        after = HK.to_zuddha(before)
        assert len(after) == len(before)
        if after == before:
            continue
        changed = []
        for m in re.finditer(r"\S+", before):
            a = after[m.start() : m.end()]
            if a != m.group() and (m.group(), a) not in changed:
                changed.append((m.group(), a))
        label = e.get("no") or e["id"]
        report.append((label, e["id"], changed))
        e["hk"] = after


def to_block_scalars(doc):
    for e in store.entries(doc):
        for k in ("hk", "en", "te", "text"):
            if k in e:
                e[k] = store.text(e[k])


def write_reports(doc, issues, report):
    for e in store.entries(doc):
        if "hk" in e:
            for finding in HK.lint(e["hk"]):
                issues["Findings in the HK text"].append(f"{e.get('no') or e['id']} (`{e['id']}`): {finding}")

    lines = [
        "# Import findings",
        "",
        "Nothing here was changed on import. Each item needs a human decision; fix them in the",
        "editor (`uv run python -m tools.serve`, then http://localhost:8000/edit).",
        "",
        "## Noticed by hand while reading the sheet",
        "",
        "- no. 91: the HK is a verse to Sri Rama (`…bhadrAdrirAmaM…`), but the English translation",
        "  is about Sri Krishna (Rasa dance, Govardhana). The translation probably belongs elsewhere.",
        "- no. 0: the HK cell is `(Hey Priyabhakta)`, which is English spelling, not Harvard-Kyoto",
        "  (`he priyabhakta`).",
        "- nos. 102, 105a and 106 carry the same verse (`bahurUpa zrIkRSNadhyAnam`) with different",
        "  English translations.",
        "- The Telugu preface (ముందుమాట) is empty: the sheet has no Telugu prose. Add it in the editor.",
        "- There are no Telugu tatparyas yet; the `te` field of every verse is empty.",
        "",
    ]
    for heading, found in issues.items():
        lines += [f"## {heading}", ""] + [f"- {f}" for f in found] + [""]
    ISSUES.write_text("\n".join(lines), encoding="utf-8")

    n_words = sum(len(c) for _, _, c in report)
    out = [
        "# The to_zuddha pass",
        "",
        "On import every HK text was normalised with `to_zuddha` (rules Z1-Z6 in `tools/hk.py`) and",
        "the result is what `data/grantha.yaml` holds. The untouched sheet is in `data/source/`.",
        f"{len(report)} entries changed, {n_words} distinct word changes. Only `M`/`m` characters",
        "were replaced, one for one; nothing was added, removed or moved.",
        "",
    ]
    for label, vid, changed in report:
        out += [f"## {label} (`{vid}`)", "", "| before | after |", "|---|---|"]
        out += [f"| `{b}` | `{a}` |" for b, a in changed] + [""]
    ZUDDHA_PASS.write_text("\n".join(out), encoding="utf-8")


def main(argv):
    if store.GRANTHA.exists() and "--force" not in argv:
        sys.exit(f"{store.GRANTHA} exists: it is the ground truth now. Use --force to re-import.")
    wb = openpyxl.load_workbook(XLSX)
    issues: dict[str, list[str]] = defaultdict(list)
    doc = {
        "title": {"hk": "zrI kRSNAnandamayam", "en": "Sri Krishnanandamayam", "author": {"hk": "", "en": ""}},
        "prefaces": {
            "en": {"title": "Preface", "blocks": import_intro(wb["Intro"], issues)},
            "te": {"title": "ముందుమాట", "blocks": []},
        },
        "items": import_main(wb["Sheet1"], issues),
    }
    report = []
    zuddha_pass(doc, report)
    to_block_scalars(doc)
    store.save(doc)
    write_reports(doc, issues, report)
    verses = sum(1 for it in doc["items"] if it["type"] == "verse")
    sections = sum(1 for it in doc["items"] if it["type"] == "section")
    print(f"{verses} verses, {sections} sections, {len(doc['prefaces']['en']['blocks'])} preface blocks")
    print(f"zuddha pass changed {len(report)} entries; see {ZUDDHA_PASS.name} and {ISSUES.name}")


if __name__ == "__main__":
    main(sys.argv[1:])
