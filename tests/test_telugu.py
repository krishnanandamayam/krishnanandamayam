"""The Telugu preface and the Telugu meanings taken from the family's Telugu document."""

from tools import store

DOC = store.load()
TE = DOC["prefaces"]["te"]["blocks"]


def test_telugu_preface_has_prose_and_slokas():
    kinds = [b["type"] for b in TE]
    assert kinds.count("sloka") == 4 and kinds.count("prose") >= 10


def test_the_authors_address_and_phone_are_not_published():
    text = " ".join(str(b.get("text") or "") for b in TE)
    assert "9908231582" not in text and "సూపర్ మార్కెట్" not in text


def test_verses_1_to_25_have_a_telugu_meaning():
    for n in range(1, 26):
        te = str(store.find(DOC, f"v{n}").get("te") or "")
        assert len(te) > 40, n


def test_the_meaning_of_the_matrikrishna_sloka_is_on_the_sloka_that_has_it():
    v = store.find(DOC, "v54")
    assert "vakSoj" in str(v["hk"])
    assert "అమ్మా ఆకలేస్తోంది" in str(v["te"])
