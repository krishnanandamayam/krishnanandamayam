"""Danda recognition and line splitting."""

import pytest

from tools.hk import split_lines, tokenize

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
