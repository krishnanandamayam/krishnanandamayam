"""Saving one entry must leave every other line of grantha.yaml untouched."""

import difflib
import shutil

from tools import store


def test_load_save_is_lossless(tmp_path):
    copy = tmp_path / "grantha.yaml"
    shutil.copy(store.GRANTHA, copy)
    store.save(store.load(copy), copy)
    assert copy.read_text(encoding="utf-8") == store.GRANTHA.read_text(encoding="utf-8")


def test_editing_one_verse_changes_only_its_lines(tmp_path):
    copy = tmp_path / "grantha.yaml"
    shutil.copy(store.GRANTHA, copy)
    doc = store.load(copy)
    verse = store.find(doc, "v2")
    old = str(verse["hk"])
    verse["hk"] = store.text(old.replace("zrI", "zrI zrI", 1))
    store.save(doc, copy)

    before = store.GRANTHA.read_text(encoding="utf-8").splitlines()
    after = copy.read_text(encoding="utf-8").splitlines()
    changed = [ln for ln in difflib.ndiff(before, after) if ln[:1] in "+-"]
    assert 0 < len(changed) <= 2 * (old.count("\n") + 1)
    assert all("zrI" in ln for ln in changed if ln.startswith("+"))


def test_multiline_text_is_a_block_scalar():
    assert "\n" in store.text("a\nb") and type(store.text("a\nb")).__name__ == "LiteralScalarString"
    assert type(store.text("one line")) is str


def test_set_title_adds_the_key_before_hk_and_removes_it_when_empty(tmp_path):
    copy = tmp_path / "grantha.yaml"
    shutil.copy(store.GRANTHA, copy)
    doc = store.load(copy)
    verse = store.find(doc, "v2")
    assert "title" not in verse
    store.set_title(verse, "  gaNeza stutiH ")
    keys = list(verse.keys())
    assert verse["title"] == "gaNeza stutiH" and keys.index("title") + 1 == keys.index("hk")
    store.save(doc, copy)
    before = store.GRANTHA.read_text(encoding="utf-8").splitlines()
    after = copy.read_text(encoding="utf-8").splitlines()
    assert [ln for ln in difflib.ndiff(before, after) if ln[:1] in "+-"] == ["+     title: gaNeza stutiH"]
    store.set_title(verse, "")
    assert "title" not in verse


def test_merge_conflict_is_reported_with_its_verse(tmp_path):
    import pytest

    copy = tmp_path / "grantha.yaml"
    lines = store.GRANTHA.read_text(encoding="utf-8").split("\n")
    i = next(n for n, ln in enumerate(lines) if ln.strip() == "id: v2")
    lines[i + 2 : i + 3] = ["<<<<<<< HEAD", lines[i + 2], "=======", lines[i + 2] + " x", ">>>>>>> abc123"]
    copy.write_text("\n".join(lines), encoding="utf-8")
    with pytest.raises(store.DataFileError) as err:
        store.load(copy)
    assert err.value.conflicts == [{"line": i + 3, "id": "v2"}]


# ---- pre-save check: each meaning is in its own language ---------------------------------------
TELUGU = "లోకములన్నిట వ్యాపించిన తండ్రి, ఈశ్వరుడు పాలకుడు."
ENGLISH = "Oh all-pervading father, controller and maintainer of the universe."


def test_meaning_in_its_own_language_is_accepted():
    assert store.wrong_language("en", ENGLISH) is None
    assert store.wrong_language("te", TELUGU) is None
    assert store.wrong_language("en", "") is None and store.wrong_language("te", "") is None


def test_telugu_in_the_english_meaning_is_refused():
    assert store.wrong_language("en", TELUGU)
    assert store.wrong_language("en", ENGLISH + " " + TELUGU)


def test_english_in_the_telugu_meaning_is_refused():
    assert store.wrong_language("te", ENGLISH)


def test_inline_hk_runs_are_not_counted_as_english():
    assert store.wrong_language("te", "శ్రీ $zrIkRSNa paramAtma bhagavAn$ కి నమస్కారం") is None
    assert store.wrong_language("en", "You ($jIvAtma$) are part of my soul ($paramAtma$).") is None


def test_other_fields_are_not_checked():
    assert store.wrong_language("hk", "rAmam vande") is None
    assert store.wrong_language("text", TELUGU) is None


def test_every_meaning_in_the_ground_truth_passes():
    bad = [
        (e["id"], k)
        for e in store.entries(store.load())
        for k in ("en", "te")
        if k in e and store.wrong_language(k, str(e.get(k) or ""))
    ]
    assert not bad


def test_saving_a_meaning_in_the_wrong_box_is_refused_and_changes_nothing():
    import pytest

    from tools import serve

    doc = store.load()
    before = str(store.find(doc, "v2").get("en") or "")
    with pytest.raises(ValueError, match="English meaning has Telugu"):
        serve._apply(doc, "v2", {"en": TELUGU})
    with pytest.raises(ValueError, match="Telugu meaning is not in Telugu"):
        serve._apply(doc, "v2", {"te": ENGLISH})
    assert str(store.find(doc, "v2").get("en") or "") == before
    assert serve._apply(doc, "v2", {"te": TELUGU}) in (["te"], [])
