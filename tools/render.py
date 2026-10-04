"""HK -> any script. The build and the editor preview both go through here, so the editor shows
exactly what the site will show."""

from __future__ import annotations

import re
import tomllib
import warnings
from functools import lru_cache

from tools import hk as HK
from tools.store import ROOT

warnings.filterwarnings("ignore", category=SyntaxWarning)  # aksharamukha's regex literals
from aksharamukha import transliterate  # noqa: E402

MODES = ("saraLa", "zuddha")
_SEP = "\n"


@lru_cache(maxsize=1)
def config() -> dict:
    with (ROOT / "scripts.toml").open("rb") as f:
        cfg = tomllib.load(f)
    cfg["by_id"] = {s["id"]: s for s in cfg["script"]}
    return cfg


def script(script_id: str) -> dict:
    return config()["by_id"][script_id]


def _convention(hk: str, which: str) -> str:
    return HK.to_zuddha(hk) if which == "zuddha" else HK.to_saraLa(hk)


def _transliterate(texts: list[str], sc: dict, mode: str) -> list[str]:
    """Transliterate many HK fragments in one Aksharamukha call (it is slow per call)."""
    if not texts:
        return []
    opts = sc[mode]

    def run(s: str) -> str:
        out = transliterate.process(
            "HK", sc["name"], s, nativize=opts["nativize"], post_options=opts.get("post", [])
        )
        for a, b in sc.get("replace", {}).items():
            out = out.replace(a, b)
        return out

    joined = run(_SEP.join(texts))
    parts = joined.split(_SEP)
    if len(parts) != len(texts):  # the script reflowed our separator: fall back to one by one
        parts = [run(t) for t in texts]
    return parts


def _dandas(sc: dict) -> tuple[str, str]:
    return ("|", "||") if sc.get("roman") else (HK.DANDA, HK.DOUBLE_DANDA)


def render_many(hk_texts: list[str], script_id: str, mode: str) -> list[list[str]]:
    """Each HK text -> its display lines in the script."""
    sc = script(script_id)
    danda, ddanda = _dandas(sc)
    plan: list[list[list[tuple[str, int | None]]]] = []  # text -> lines -> tokens
    fragments: list[str] = []
    for text in hk_texts:
        conv = _convention(text, sc[mode]["hk"])
        lines = []
        for line in HK.split_lines(conv):
            toks = []
            for kind, frag in HK.tokenize(line):
                if kind == "text":
                    toks.append(("text", len(fragments)))
                    fragments.append(HK.unbrace(frag))
                else:
                    toks.append((kind, None))
            lines.append(toks)
        plan.append(lines)
    done = _transliterate(fragments, sc, mode)
    out = []
    for lines in plan:
        rendered = []
        for toks in lines:
            s = ""
            for kind, idx in toks:
                if kind == "text":
                    s += done[idx]
                else:
                    s = s.rstrip() + " " + (danda if kind == "danda" else ddanda) + " "
            rendered.append(s.strip())
        out.append(rendered)
    return out


def render_spans(hk_text: str, script_id: str, mode: str) -> list[list[tuple[str, int, int]]]:
    """The display lines of one HK text as (shown, start, end) pieces: a word or a danda, and
    where in ``hk_text`` it was written. Joined with spaces, a line reads as ``render`` gives it.
    The editor uses this to tie a selection in the rendition to the HK box."""
    sc = script(script_id)
    danda, ddanda = _dandas(sc)
    conv = _convention(hk_text, sc[mode]["hk"])  # one character for one: offsets still hold
    plan = []
    fragments: list[str] = []
    for line, src in HK.split_line_spans(conv):
        toks = []
        for kind, a, b in HK.token_spans(line):
            toks.append((kind, a, b, len(fragments) if kind == "text" else None))
            if kind == "text":
                fragments.append(HK.unbrace(line[a:b]))
        plan.append((line, src, toks))
    done = _transliterate(fragments, sc, mode)
    out = []
    for line, src, toks in plan:
        pieces = []
        for kind, a, b, idx in toks:
            if kind != "text":
                pieces.append((danda if kind == "danda" else ddanda, src[a][0], src[b - 1][1]))
                continue
            words = [(a + m.start(), a + m.end()) for m in re.finditer(r"\S+", line[a:b])]
            shown = done[idx].split()
            if not words or not shown:
                continue
            if len(shown) != len(words):  # the script joined or split words: tie the whole run
                words, shown = [(words[0][0], words[-1][1])], [" ".join(shown)]
            pieces += [(t, src[x][0], src[y - 1][1]) for t, (x, y) in zip(shown, words)]
        out.append(pieces)
    return out


def render(hk_text: str, script_id: str, mode: str) -> list[str]:
    return render_many([hk_text], script_id, mode)[0]
