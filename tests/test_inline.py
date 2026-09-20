"""Inline $hk$ runs inside prose."""

import pytest

from tools import build, inline, render, store
from tools.hk import NON_HK_LETTERS, to_zuddha

T, H = "text", "hk"


@pytest.mark.parametrize(
    "text, expected",
    [
        ("plain prose", [(T, "plain prose")]),
        ("the $jIvAtma$ is", [(T, "the "), (H, "jIvAtma"), (T, " is")]),
        ("$oM namo nArAyaNAya namaH$", [(H, "oM namo nArAyaNAya namaH")]),
        ("$hAm$/$hrIm$", [(H, "hAm"), (T, "/"), (H, "hrIm")]),
        ('"$ta$" from "$tat$"', [(T, '"'), (H, "ta"), (T, '" from "'), (H, "tat"), (T, '"')]),
        ("$ kRSNa $", [(H, "kRSNa")]),
        (r"it costs \$5 and \$6", [(T, "it costs $5 and $6")]),
        ("a lone $ sign", [(T, "a lone $ sign")]),
        ("never across\n$a line\nbreak$", [(T, "never across\n$a line\nbreak$")]),
        ("", []),
    ],
)
def test_split(text, expected):
    assert inline.split(text) == expected


def test_fragment_ids_are_numbered_per_field():
    entry = {"id": "pe01", "text": "$a$ and $i$", "en": "$u$"}
    assert inline.entry_fragments(entry) == [("pe01.text.0", "a"), ("pe01.text.1", "i"), ("pe01.en.0", "u")]


def test_html_carries_the_same_ids_the_data_does():
    e = {"x.text.0": ["జీవాత్మ"], "x.text.1": ["మోక్షమ్"]}
    html = build.prose_html("the $jIvAtma$ gets\n$mokSam$ & more", "x", "text", e)
    assert 'data-e="x.text.0" data-inline>జీవాత్మ</span>' in html
    assert 'data-e="x.text.1" data-inline>మోక్షమ్</span>' in html
    assert "&amp; more" in html and "$" not in html


def test_rendering_an_inline_run():
    assert render.render("jIvAtma", "telugu", "zuddha") == ["జీవాత్మ"]
    assert render.render("zrI kRSNa", "roman", "zuddha") == ["śrī kṛṣṇa"]


DOC = store.load()
FRAGMENTS = [pair for e in store.entries(DOC) for pair in inline.entry_fragments(e)]


def test_the_english_preface_uses_inline_hk():
    assert len([i for i, _ in FRAGMENTS if i.startswith("pe")]) > 50


@pytest.mark.parametrize("hk", [h for _, h in FRAGMENTS], ids=[i for i, _ in FRAGMENTS])
def test_inline_runs_are_clean_zuddha_hk(hk):
    assert to_zuddha(hk) == hk
    assert not set(hk) & NON_HK_LETTERS


def test_no_unclosed_runs_in_the_corpus():
    for e in store.entries(DOC):
        for field in inline.PROSE_FIELDS:
            text = str(e.get(field) or "").replace("\\$", "")
            leftovers = "".join(body for kind, body in inline.split(text) if kind == "text")
            assert "$" not in leftovers, (e["id"], field)


def test_verse_header_is_rendered_and_listed_in_contents():
    doc = store.load()
    data = {"e": {}}
    verse = next(v for v in doc["items"] if v.get("title") and v.get("hk"))
    tid = build.title_id(verse)
    e = {verse["id"]: ["పద్యం"], tid: ["శీర్షిక"]}
    html = build.verse_html({**verse, "en": "", "te": ""}, e)
    assert f'data-e="{tid}" data-inline>శీర్షిక</h3>' in html and "పద్యం" in html
    assert f'href="#{verse["id"]}"' in build.toc_titles([verse], e)


def test_header_only_verse_has_no_empty_lines_block():
    html = build.verse_html({"id": "v105", "no": "105", "title": "x", "hk": "", "en": "", "te": ""}, {"v105.title": ["శీర్షిక"]})
    assert 'class="lines' not in html and "శీర్షిక" in html


def test_prose_heading_marker_renders_as_a_heading():
    html = build.prose_html("## మనవి\n\nఓం శ్రీ", "pt01", "text", {})
    assert '<h3 class="pfh">మనవి</h3>' in html and "<p>ఓం శ్రీ</p>" in html
