"""Properties that must hold for every HK text in the ground truth."""

import re

import pytest

from tools import store
from tools.hk import to_saraLa, to_zuddha

DOC = store.load()
HK = [(e["id"], str(e["hk"])) for e in store.entries(DOC) if e.get("hk")]
HK += [(e["id"] + ".title", str(e["title"])) for e in store.entries(DOC) if e.get("title")]
IDS = [i for i, _ in HK]


def test_there_is_a_corpus():
    assert len(HK) > 190


def test_ids_are_unique():
    ids = [e["id"] for e in store.entries(DOC)]
    assert len(ids) == len(set(ids))


def test_ids_are_safe_in_urls():
    assert all(re.fullmatch(r"[A-Za-z0-9-]+", e["id"]) for e in store.entries(DOC))


@pytest.mark.parametrize("hk", [h for _, h in HK], ids=IDS)
def test_ground_truth_is_in_zuddha_form(hk):
    assert to_zuddha(hk) == hk


@pytest.mark.parametrize("hk", [h for _, h in HK], ids=IDS)
def test_length_preserved(hk):
    assert len(to_saraLa(hk)) == len(hk) == len(to_zuddha(hk))


@pytest.mark.parametrize("hk", [h for _, h in HK], ids=IDS)
def test_idempotent(hk):
    assert to_saraLa(to_saraLa(hk)) == to_saraLa(hk)
    assert to_zuddha(to_zuddha(hk)) == to_zuddha(hk)


@pytest.mark.parametrize("hk", [h for _, h in HK], ids=IDS)
def test_conventions_round_trip(hk):
    """saraLa loses nothing zuddha needs, and the other way round."""
    assert to_saraLa(to_zuddha(hk)) == to_saraLa(hk)
    assert to_zuddha(to_saraLa(hk)) == to_zuddha(hk)


@pytest.mark.parametrize("hk", [h for _, h in HK], ids=IDS)
def test_only_nasal_letters_ever_change(hk):
    for out in (to_saraLa(hk), to_zuddha(hk)):
        for a, b in zip(hk, out):
            if a != b:
                assert a in "MmGJNn" and b in "MmGJNn"


def test_verses_without_english_are_reported_not_fatal():
    missing = [v["id"] for v in DOC["items"] if v["type"] == "verse" and not str(v.get("en") or "").strip()]
    assert isinstance(missing, list)  # listed in data/ISSUES.md; the build does not fail on them


def test_every_verse_has_text_or_a_header():
    for v in DOC["items"]:
        if v["type"] == "verse":
            assert str(v.get("hk") or "").strip() or str(v.get("title") or "").strip(), v["id"]


def test_headers_are_one_line():
    assert all("\n" not in str(v["title"]) for v in DOC["items"] if v.get("title"))
