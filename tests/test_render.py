"""End to end: HK -> script, for both conventions, in every script the site ships."""

import re

import pytest

from tools import render, store

SCRIPTS = [s["id"] for s in render.config()["script"]]

# gaGgA in each script: (saraLa, zuddha). Written by hand, not produced by the code.
GANGA = {
    "telugu": ("గంగా", "గఙ్గా"),
    "devanagari": ("गंगा", "गङ्गा"),
    "kannada": ("ಗಂಗಾ", "ಗಙ್ಗಾ"),
    "malayalam": ("ഗംഗാ", "ഗങ്ഗാ"),
    "gujarati": ("ગંગા", "ગઙ્ગા"),
    "roman": ("gaṃgā", "gaṅgā"),
    # Odia, Bengali and Tamil write the class nasal natively in both conventions
    "odia": ("ଗଙ୍ଗା", "ଗଙ୍ଗା"),
    "bengali": ("গঙ্গা", "গঙ্গা"),
    "tamil": ("கங்கா", "க³ங்கா³"),
}


@pytest.mark.parametrize("script", sorted(GANGA))
@pytest.mark.parametrize("source", ["gaGgA", "gaMgA"])
def test_ganga(script, source):
    saraLa, zuddha = GANGA[script]
    assert render.render(source, script, "saraLa") == [saraLa]
    assert render.render(source, script, "zuddha") == [zuddha]


def test_word_final_m_telugu():
    assert render.render("rAmaM ca", "telugu", "zuddha") == ["రామమ్ చ"]
    assert render.render("rAmam ca", "telugu", "saraLa") == ["రామం చ"]


def test_pranava_is_never_om_with_halant():
    for mode in render.MODES:
        assert render.render("om namaH", "telugu", mode) == ["ఓం నమః"]


def test_telugu_short_vowels():
    assert render.render("kOlturu paracEda", "telugu", "zuddha") == ["కొల్తురు పరచెద"]


def test_dandas_indic_and_roman():
    assert render.render("rAma . kRSNa ..", "telugu", "saraLa") == ["రామ ।", "కృష్ణ ॥"]
    assert render.render("rAma . kRSNa ..", "roman", "saraLa") == ["rāma |", "kṛṣṇa ||"]


def test_gurmukhi_pranava_is_not_ik_onkar():
    assert "ੴ" not in " ".join(render.render("oM namaH", "gurmukhi", "saraLa"))


DOC = store.load()
HK = [str(e["hk"]) for e in store.entries(DOC) if e.get("hk")]


@pytest.mark.parametrize("mode", render.MODES)
@pytest.mark.parametrize("script", SCRIPTS)
def test_whole_corpus_renders(script, mode):
    out = render.render_many(HK, script, mode)
    assert len(out) == len(HK)
    assert all(lines and all(ln.strip() for ln in lines) for lines in out)


@pytest.mark.parametrize("script", [s for s in SCRIPTS if s != "roman"])
def test_clean_hk_leaves_no_latin_behind(script):
    sample = "zrI kRSNAya vAsudevAya haraye paramAtmane . praNata klezanAzAya govindAya namo namaH .."
    text = " ".join(render.render(sample, script, "zuddha"))
    assert not re.search(r"[A-Za-z]", text)


def test_spans_point_at_the_hk_they_render():
    hk = "  rAmam ca vande.\nkRSNam vande .. "
    spans = render.render_spans(hk, "telugu", "saraLa")
    assert [[t for t, _, _ in line] for line in spans] == [["రామం", "చ", "వందే", "।"], ["కృష్ణం", "వందే", "॥"]]
    assert [[hk[a:b] for _, a, b in line] for line in spans] == [["rAmam", "ca", "vande", "."], ["kRSNam", "vande", ".."]]


def test_spans_of_a_run_on_verse():
    hk = "rAmam vande . kRSNam vande .."
    spans = render.render_spans(hk, "telugu", "zuddha")
    assert [[hk[a:b] for _, a, b in line] for line in spans] == [["rAmam", "vande", "."], ["kRSNam", "vande", ".."]]


@pytest.mark.parametrize("script", ["telugu", "tamil", "roman"])
@pytest.mark.parametrize("mode", render.MODES)
def test_spans_read_as_the_rendition(script, mode):
    verses = [e["hk"] for e in store.entries(store.load()) if e.get("type") == "verse" and e.get("hk")]
    for hk in verses:
        spans = render.render_spans(hk, script, mode)
        assert [" ".join(t for t, _, _ in line) for line in spans] == [" ".join(line.split()) for line in render.render(hk, script, mode)]


def test_braces_keep_the_anusvara_in_zuddha_and_are_not_shown():
    assert render.render("gaMgA {gaMgA}", "telugu", "zuddha") == ["గఙ్గా గంగా"]
    assert render.render("gaGgA {gaMgA}", "telugu", "saraLa") == ["గంగా గంగా"]
    hk = "zrI{veMkaTa}ezvaram vande ."
    spans = render.render_spans(hk, "telugu", "zuddha")
    assert [[hk[a:b] for _, a, b in line] for line in spans] == [["zrI{veMkaTa}ezvaram", "vande", "."]]
    assert "{" not in spans[0][0][0]
