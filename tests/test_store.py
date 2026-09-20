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
