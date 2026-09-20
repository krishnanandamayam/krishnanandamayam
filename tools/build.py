"""data/grantha.yaml -> site/index.html + site/data/<script>-<mode>.json

    uv run python -m tools.build

site/app.js, style.css and print.css are hand-written and committed; index.html and data/ are
generated here and are not committed.
"""

from __future__ import annotations

import html
import json
import re
import sys

from tools import inline, render, store

SITE = store.ROOT / "site"
DEFAULT_MODE = "saraLa"

_LIST_ITEM = re.compile(r"^\(?[A-Za-z0-9]{1,3}[)}.]\s")


def paragraphs(text: str) -> list[str]:
    """Undo the hard wrapping the prose picked up in typesetting; keep real breaks and lists."""
    out: list[str] = []
    prev = ""
    for line in (text or "").split("\n"):
        line = line.strip()
        if not line:
            prev = ""
            continue
        starts_new = not out or not prev or _LIST_ITEM.match(line) or len(prev) < 50 or prev.endswith(":")
        if starts_new:
            out.append(line)
        else:
            out[-1] += " " + line
        prev = line
    return out


def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def prose_html(text: str, entry_id: str, field: str, e: dict) -> str:
    """Paragraphs of prose; every inline ``$hk$`` run becomes a span that follows the script."""
    out, n = "", 0
    for para in paragraphs(text):
        out += "<p>"
        for kind, body in inline.split(para):
            if kind == "text":
                out += esc(body)
                continue
            fid = inline.fragment_id(entry_id, field, n)
            n += 1
            out += f'<span class="indic il" data-e="{fid}" data-inline>{esc(" ".join(e[fid]))}</span>'
        out += "</p>"
    return out


def lines_html(lines: list[str]) -> str:
    return "".join(f'<span class="ln">{esc(ln)}</span>' for ln in lines)


# --------------------------------------------------------------------------------------


def title_id(verse) -> str:
    return f"{verse['id']}.title"


def hk_entries(doc) -> list[tuple[str, str]]:
    """(id, hk) for everything that follows the script switch."""
    out = [("title", doc["title"]["hk"])]
    author = (doc["title"].get("author") or {}).get("hk")
    if author:
        out.append(("author", author))
    for e in store.entries(doc):
        if e.get("hk"):
            out.append((e["id"], e["hk"]))
        if e.get("title"):
            out.append((title_id(e), e["title"]))
        out += inline.entry_fragments(e)
    return out


def build_data(doc) -> dict[tuple[str, str], dict]:
    (SITE / "data").mkdir(parents=True, exist_ok=True)
    pairs = hk_entries(doc)
    ids = [i for i, _ in pairs]
    texts = [t for _, t in pairs] + ["saraLa", "zuddha"]
    built = {}
    for sc in render.config()["script"]:
        for mode in render.MODES:
            rendered = render.render_many(texts, sc["id"], mode)
            data = {
                "script": sc["id"],
                "mode": mode,
                "ui": {"saraLa": rendered[-2][0], "zuddha": rendered[-1][0]},
                "e": dict(zip(ids, rendered[:-2])),
            }
            path = SITE / "data" / f"{sc['id']}-{mode}.json"
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            built[(sc["id"], mode)] = data
    return built


def sections(doc):
    """Group items: [(section_or_None, [verses])]."""
    groups = [(None, [])]
    for it in doc["items"]:
        if it["type"] == "section":
            groups.append((it, []))
        else:
            groups[-1][1].append(it)
    return [g for g in groups if g[0] is not None or g[1]]


def verse_range(verses) -> str:
    nos = [v["no"] for v in verses if v.get("no")]
    if not nos:
        return ""
    return nos[0] if len(nos) == 1 else f"{nos[0]}–{nos[-1]}"


def verse_html(v, e) -> str:
    no = esc(v.get("no") or "")
    meanings = ""
    for lang, label in (("en", "English"), ("te", "తెలుగు")):
        if (v.get(lang) or "").strip():
            meanings += (
                f'<details class="m m-{lang}"><summary>{label}</summary>'
                f'<div class="m-body" lang="{lang}">{prose_html(v[lang], v["id"], lang, e)}</div></details>'
            )
    num = f'<a class="no" href="#{v["id"]}" title="Link to verse {no}">{no}</a>' if no else ""
    head = ""
    if v.get("title"):
        tid = title_id(v)
        head = f'<h3 class="vtitle indic" data-e="{tid}" data-inline>{esc(" ".join(e[tid]))}</h3>'
    lines = ""
    if v.get("hk"):  # a verse can be a header and nothing else
        lines = f'<div class="lines indic" data-e="{v["id"]}">{lines_html(e[v["id"]])}</div>'
    return (
        f'<article class="verse" id="{v["id"]}">{num}{head}{lines}'
        f'<div class="meanings">{meanings}</div></article>'
    )


def toc_titles(verses, e) -> str:
    """The verses of a section that carry their own header, as a nested contents list."""
    rows = ""
    for v in verses:
        if v.get("title"):
            tid = title_id(v)
            rows += (
                f'<li><a href="#{v["id"]}"><span class="indic" data-e="{tid}" data-inline>'
                f'{esc(" ".join(e[tid]))}</span></a> <span class="toc-range">{esc(v.get("no") or "")}</span></li>'
            )
    return f'<ol class="toc-sub">{rows}</ol>' if rows else ""


def live_blocks(doc, lang):
    """Preface blocks that have something in them (the editor can leave empty ones behind)."""
    return [b for b in doc["prefaces"][lang]["blocks"] if str(b.get("hk") or b.get("text") or "").strip()]


def preface_html(doc, lang, e) -> str:
    pf = doc["prefaces"][lang]
    blocks = live_blocks(doc, lang)
    if not blocks:
        return ""
    body = ""
    for b in blocks:
        if b["type"] == "sloka":
            body += f'<blockquote class="lines indic" data-e="{b["id"]}">{lines_html(e[b["id"]])}</blockquote>'
        else:
            body += f'<div class="prose" lang="{lang}">{prose_html(b["text"], b["id"], "text", e)}</div>'
    return (
        f'<section class="preface" id="preface-{lang}" data-part="preface-{lang}">'
        f'<h2 lang="{lang}">{esc(pf["title"])}</h2>{body}</section>'
    )


def build_html(doc, data) -> str:
    cfg = render.config()
    default = cfg["default"]
    e = data[(default, DEFAULT_MODE)]["e"]
    sc = render.script(default)

    toc, body = "", ""
    for lang in ("en", "te"):
        if live_blocks(doc, lang):
            toc += (
                f'<li data-toc="preface-{lang}"><div class="toc-row"><a href="#preface-{lang}" lang="{lang}">'
                f'{esc(doc["prefaces"][lang]["title"])}</a></div></li>'
            )
    part_list = []
    for n, (sec, verses) in enumerate(sections(doc)):
        sid = sec["id"] if sec else "s00"
        rng = verse_range(verses)
        if sec:
            head = f'<h2 class="indic" data-e="{sid}">{lines_html(e[sid])}</h2>'
            if sec.get("en"):
                head += f'<p class="sec-en">{esc(sec["en"])}</p>'
            toc_label = f'<span class="indic" data-e="{sid}" data-inline>{esc(" ".join(e[sid]))}</span>'
            if sec.get("en"):
                toc_label += f' <span class="toc-en">{esc(sec["en"])}</span>'
            plain = sec.get("en") or sec["hk"].replace("\n", " ")
        else:
            head = ""
            toc_label = '<span class="toc-en">Opening verses</span>'
            plain = "Opening verses"
        toc += (
            f'<li data-toc="{sid}"><div class="toc-row"><a href="#{sid}">{toc_label}</a> '
            f'<span class="toc-range">{esc(rng)}</span></div>{toc_titles(verses, e)}</li>'
        )
        part_list.append({"id": sid, "label": plain, "range": rng})
        body += (
            f'<section class="sec" id="{sid}" data-part="{sid}">{head}'
            + "".join(verse_html(v, e) for v in verses)
            + "</section>"
        )

    title = doc["title"]
    author = title.get("author") or {}
    author_html = ""
    if author.get("hk"):
        author_html += f'<p class="author indic" data-e="author">{lines_html(e["author"])}</p>'
    if author.get("en"):
        author_html += f'<p class="author-en">{esc(author["en"])}</p>'

    client_cfg = {
        "default": default,
        "defaultMode": DEFAULT_MODE,
        "scripts": [
            {k: s.get(k) for k in ("id", "label", "english", "lang", "font", "roman")} for s in cfg["script"]
        ],
        "parts": part_list,
        "prefaces": [lang for lang in ("en", "te") if live_blocks(doc, lang)],
        "hasTe": any((v.get("te") or "").strip() for v in doc["items"] if v["type"] == "verse"),
    }
    options = "".join(
        f'<option value="{s["id"]}">{esc(s["label"])} · {esc(s["english"])}</option>' for s in cfg["script"]
    )
    template = (SITE / "template.html").read_text(encoding="utf-8")
    return (
        template.replace("{{TITLE_EN}}", esc(title["en"]))
        .replace("{{TITLE_LINES}}", lines_html(e["title"]))
        .replace("{{AUTHOR}}", author_html)
        .replace("{{LANG}}", sc["lang"])
        .replace("{{SCRIPT_OPTIONS}}", options)
        .replace("{{TOC}}", toc)
        .replace("{{PREFACES}}", preface_html(doc, "en", e) + preface_html(doc, "te", e))
        .replace("{{BODY}}", body)
        .replace("{{CONFIG}}", json.dumps(client_cfg, ensure_ascii=False).replace("</", "<\\/"))
    )


def build(quiet: bool = False) -> None:
    doc = store.load()
    data = build_data(doc)
    (SITE / "index.html").write_text(build_html(doc, data), encoding="utf-8")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    if not quiet:
        n = sum(1 for it in doc["items"] if it["type"] == "verse")
        print(f"built site/: {n} verses x {len(data)} script renditions")


if __name__ == "__main__":
    build(quiet="-q" in sys.argv)
