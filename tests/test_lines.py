"""Danda recognition and line splitting."""

import pytest

from tools import hk as HK
from tools import store
from tools.hk import split_line_spans, split_lines, tokenize

T, D, DD = "text", "danda", "ddanda"


@pytest.mark.parametrize(
    "line, kinds",
    [
        ("rAmam . kRSNam ..", [T, D, T, DD]),
        ("rAmam. kRSNam..", [T, D, T, DD]),
        ("rAma | kRSNa ||", [T, D, T, DD]),
        ("rAma| kRSNa||", [T, D, T, DD]),
        ("rAma . . kRSNa", [T, DD, T]),
        ("harohaM...", [T, DD]),
        ("oM.. tejasvinam", [T, DD, T]),
        ("om.", [T, D]),
        ("1. dhyAnam", [T]),  # a numbered list, not a danda
        ("bhAgavatam-7:5:23", [T]),
        ("rAma, kRSNa", [T]),
        ("", []),
    ],
)
def test_tokenize(line, kinds):
    assert [k for k, _ in tokenize(line)] == kinds


def test_tokenize_keeps_all_text():
    toks = tokenize("zrIkaram, zubhakaram . zivam ..")
    assert [t for k, t in toks if k == T] == ["zrIkaram, zubhakaram ", " zivam "]


def test_authors_line_breaks_win():
    assert split_lines("rAmam . kRSNam .\nzivam ..") == ["rAmam . kRSNam .", "zivam .."]


def test_run_on_verse_breaks_at_dandas():
    assert split_lines("rAmam. kRSNam. zivam..") == ["rAmam .", "kRSNam .", "zivam .."]


def test_verse_without_dandas_is_one_line():
    assert split_lines("namovAkam") == ["namovAkam"]


def test_blank_lines_are_dropped():
    assert split_lines("a\n\n b \n") == ["a", "b"]


@pytest.mark.parametrize(
    "hk",
    [
        "rAmam vande . kRSNam vande ..",
        "  rAmam vande.kRSNam vande..  ",
        "rAmam vande .\n\n  kRSNam vande ..\n",
        "oM.. tejasvinam | 1. dhyAnam",
        "",
    ],
)
def test_split_line_spans_point_at_the_source(hk):
    for line, src in split_line_spans(hk):
        assert len(src) == len(line)
        for ch, (a, b) in zip(line, src):
            # a letter comes from itself; the danda closing a run-on line from that danda
            assert hk[a:b] == ch or (ch in " ." and hk[a:b].strip(" .|") == "")



# ---- break_lines: one line of the verse per line of text ------------------------------------

BREAKS = [
    ("rAmam vande . kRSNam vande ..", "rAmam vande .\nkRSNam vande .."),
    ("rAmam vande. kRSNam vande..", "rAmam vande.\nkRSNam vande.."),
    ("rAmam vande | kRSNam vande ||", "rAmam vande |\nkRSNam vande ||"),
    ("a . b .\nc . d ..", "a .\nb .\nc .\nd .."),  # the author's own breaks are kept
    ("  rAmam vande .  \n kRSNam vande ..  ", "rAmam vande .\nkRSNam vande .."),  # spaces at line ends go
    ("rAmam vande ..", "rAmam vande .."),
    ("rAmam vande", "rAmam vande"),
    ("1. rAmam vande . 2. kRSNam vande ..", "1. rAmam vande .\n2. kRSNam vande .."),  # list labels are not dandas
    ('"rAmam vande." kRSNam vande ..', '"rAmam vande."\nkRSNam vande ..'),  # the closing quote stays
    ('"rAmam vande . kRSNam vande .. "', '"rAmam vande .\nkRSNam vande .. "'),
    ("a .\n\nb ..", "a .\n\nb .."),
]


@pytest.mark.parametrize("hk,expected", BREAKS)
def test_break_lines(hk, expected):
    assert HK.break_lines(hk) == expected
    assert HK.break_lines(expected) == expected


def test_break_lines_changes_only_white_space():
    for e in store.entries(store.load()):
        hk = str(e.get("hk") or "")
        assert "".join(HK.break_lines(hk).split()) == "".join(hk.split())


# ---- dot_dandas: | and || are written . and .. ----------------------------------------------

DOTS = [
    ("rAmam vande | kRSNam vande ||", "rAmam vande . kRSNam vande .."),
    ("rAmam vande| kRSNam vande||", "rAmam vande. kRSNam vande.."),
    ("rAmam vande | |", "rAmam vande .."),
    ("oM|| vande", "oM.. vande"),
    ("rAmam vande . kRSNam vande ..", "rAmam vande . kRSNam vande .."),
]


@pytest.mark.parametrize("hk,expected", DOTS)
def test_dot_dandas(hk, expected):
    assert HK.dot_dandas(hk) == expected
    kinds = lambda s: [k for k, _, _ in HK.token_spans(s)]  # noqa: E731
    assert kinds(hk) == kinds(expected)


def test_every_verse_is_stored_with_dot_dandas_and_one_line_per_danda():
    for e in store.entries(store.load()):
        if e.get("type") == "verse":
            hk = str(e.get("hk") or "")
            assert HK.break_lines(HK.dot_dandas(hk)) == hk, e["id"]
