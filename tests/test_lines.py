"""Danda recognition and line splitting."""

import pytest

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
