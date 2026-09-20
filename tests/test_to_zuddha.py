"""to_zuddha: every transformation, one named case each.

CASES maps a rule id (tools.hk.RULES) to (id, input, expected) triples. Expected values are
literals, or are assembled from literal pieces; none is computed by the code under test.
"""

import pytest

from tests.hk_cases import CONSONANTS, VOWELS, WORD_ENDERS
from tools.hk import to_zuddha

CASES: dict[str, list[tuple[str, str, str]]] = {}

# ---- Z1: M + each of the 20 non-nasal stops ------------------------------------------------
CASES["Z1"] = [
    ("M+k", "saMkaTa", "saGkaTa"),
    ("M+kh", "zaMkha", "zaGkha"),
    ("M+g", "gaMgA", "gaGgA"),
    ("M+gh", "saMgha", "saGgha"),
    ("M+c", "paMca", "paJca"),
    ("M+ch", "vAMchA", "vAJchA"),
    ("M+j", "kuMja", "kuJja"),
    ("M+jh", "jhaMjhA", "jhaJjhA"),
    ("M+T", "ghaMTA", "ghaNTA"),
    ("M+Th", "kaMTha", "kaNTha"),
    ("M+D", "daMDa", "daNDa"),
    ("M+Dh", "SaMDha", "SaNDha"),
    ("M+t", "zAMta", "zAnta"),
    ("M+th", "paMthA", "panthA"),
    ("M+d", "naMda", "nanda"),
    ("M+dh", "baMdha", "bandha"),
    ("M+p", "caMpaka", "campaka"),
    ("M+ph", "guMpha", "gumpha"),
    ("M+b", "aMbA", "ambA"),
    ("M+bh", "zaMbhu", "zambhu"),
    # retroflex vs dental is decided by case alone
    ("case:T-vs-t", "kaMTa kaMta", "kaNTa kanta"),
    ("case:D-vs-d", "caMDa caMda", "caNDa canda"),
    ("case:Dh-vs-dh", "aMDha aMdha", "aNDha andha"),
    # after every vowel letter
    ("after-a", "aMka", "aGka"),
    ("after-A", "AMka", "AGka"),
    ("after-i", "iMka", "iGka"),
    ("after-I", "IMka", "IGka"),
    ("after-u", "uMka", "uGka"),
    ("after-U", "UMka", "UGka"),
    ("after-R", "kRMta", "kRnta"),
    ("after-e", "eMka", "eGka"),
    ("after-ai", "aiMka", "aiGka"),
    ("after-o", "koMka", "koGka"),
    ("after-au", "auMka", "auGka"),
    ("after-E", "EMka", "EGka"),
    ("after-O", "OMka", "OGka"),
    # M + jJ: j is a ca-varga stop
    ("M+jJ", "saMjJA", "saJjJA"),
    # M + kS: k is a ka-varga stop
    ("M+kS", "saMkSepa", "saGkSepa"),
    ("omkara-compound", "oMkAra", "oGkAra"),
    ("several-in-one-word", "saMkaTaMkaMTaka", "saGkaTaGkaNTaka"),
    ("several-in-one-line", "paMca gaMgA zaMbhu naMda", "paJca gaGgA zambhu nanda"),
    ("at-start-of-text", "Mka", "Gka"),
    ("telugu-word", "anugrahiMci", "anugrahiJci"),
    ("telugu-word-2", "saMtasaparacEda", "santasaparacEda"),
]

# ---- Z2: M + each nasal --------------------------------------------------------------------
CASES["Z2"] = [
    ("M+G", "aMGa", "aGGa"),
    ("M+J", "aMJa", "aJJa"),
    ("M+N", "aMNa", "aNNa"),
    ("M+n", "saMnidhi", "sannidhi"),
    ("M+m", "saMmAna", "sammAna"),
]

# ---- Z3: M before a non-stop stays M -------------------------------------------------------
CASES["Z3"] = [
    ("M+y", "saMyama", "saMyama"),
    ("M+r", "saMrakSaNa", "saMrakSaNa"),
    ("M+l", "saMlApa", "saMlApa"),
    ("M+L", "aMLa", "aMLa"),
    ("M+v", "saMvAda", "saMvAda"),
    ("M+z", "saMzaya", "saMzaya"),
    ("M+S", "daMSTra", "daMSTra"),
    ("M+s", "saMsAra", "saMsAra"),
    ("M+h", "siMha", "siMha"),
    ("M+H", "aMH", "aMH"),
] + [(f"M+vowel-{v}", f"aM{v}ka", f"aM{v}ka") for v in VOWELS]

# ---- Z4: word-final M and m -> m, whatever follows ----------------------------------------
CASES["Z4"] = (
    [(f"M-before-{c}", f"rAmaM {c}a", f"rAmam {c}a") for c in CONSONANTS]
    + [(f"m-before-{c}", f"rAmam {c}a", f"rAmam {c}a") for c in CONSONANTS]
    + [(f"M-before-vowel-{v}", f"rAmaM {v}ti", f"rAmam {v}ti") for v in VOWELS]
    + [(f"m-before-vowel-{v}", f"rAmam {v}ti", f"rAmam {v}ti") for v in VOWELS]
    + [(f"M-before-{e!r}", f"rAmaM{e}", f"rAmam{e}") for e in WORD_ENDERS]
    + [(f"m-before-{e!r}", f"rAmam{e}", f"rAmam{e}") for e in WORD_ENDERS]
    + [
        # the word break is kept: nothing is carried into the next word
        ("no-sandhi-into-c", "rAmaM ca", "rAmam ca"),
        ("no-sandhi-into-k", "ahaM kRSNaM", "aham kRSNam"),
        ("no-sandhi-into-t", "taM tam", "tam tam"),
        ("space-count-kept", "rAmaM   ca", "rAmam   ca"),
        ("newline-kept", "rAmaM\nca", "rAmam\nca"),
        ("hyphen-is-a-break", "yugaM-mama", "yugam-mama"),
        ("every-word", "zrIkaraM zubhakaraM zivaM", "zrIkaram zubhakaram zivam"),
        ("after-long-vowel", "devIM", "devIm"),
        ("lone-M", "M", "m"),
        ("final-and-internal", "saMkaTaM", "saGkaTam"),
    ]
)

# ---- Z5: everything else is untouched ------------------------------------------------------
_UNTOUCHED = [
    "", " ", "\n", "a", "kRSNa", "zrIH", "namaH", "jJAna", "kSetra", "lakSmI", "'pi", "so'ham",
    "a~", "nRRNAm", "klRpta", "kaLyANa", "kOlturu", "paracEda", "rAmanAmamu", "nanukOlturubhaktulu",
    "amma", "anna", "janma", "tanmaya", "vAGmaya", "puNya", "zambhu", "gaGgA", "paJca", "kaNTha",
    "nanda", "mama", "mAm", "nAma", "madhu", "12", "7:5:23", "1. dhyAnam", "(zrI)", "[zrI]",
    '"zrI"', "“zrI”", "zrI - rAma", "a  b", "a\tb", "rAma . kRSNa ..", "rAma | kRSNa ||",
    "rAma, kRSNa; ziva! hari?", "bhagavAn ca", "vAk ca", "samrAT", "G J N n m",
]  # fmt: skip
CASES["Z5"] = [(f"untouched-{i}-{s!r}", s, s) for i, s in enumerate(_UNTOUCHED)] + [
    (f"vowel-{v}-untouched", f"k{v}ta", f"k{v}ta") for v in VOWELS
] + [(f"consonant-{c}-untouched", f"a{c}a", f"a{c}a") for c in CONSONANTS]

# ---- Z6: the pranava ------------------------------------------------------------------------
CASES["Z6"] = [
    ("oM", "oM", "oM"),
    ("om", "om", "oM"),
    ("om-danda", "om.", "oM."),
    ("oM-ddanda", "oM.. tejasvinam", "oM.. tejasvinam"),
    ("om-then-word", "om namaH zivAya", "oM namaH zivAya"),
    ("oM-then-stop", "oM tat sat", "oM tat sat"),
    ("mid-line", "hariH om tat", "hariH oM tat"),
    ("after-newline", "rAma\nom", "rAma\noM"),
    ("in-quotes", '"om"', '"oM"'),
    ("not-pranava-soma", "soma", "soma"),
    ("not-pranava-homa", "homaM", "homam"),
    ("not-pranava-kom", "kom", "kom"),
    ("not-pranava-oMkAra", "oMkAra", "oGkAra"),
]

ALL = [pytest.param(i, e, id=f"{rule}:{cid}") for rule, cs in CASES.items() for cid, i, e in cs]


@pytest.mark.parametrize("hk, expected", ALL)
def test_to_zuddha(hk, expected):
    assert to_zuddha(hk) == expected


@pytest.mark.parametrize("hk, expected", ALL)
def test_length_preserved(hk, expected):
    assert len(to_zuddha(hk)) == len(hk)


@pytest.mark.parametrize("hk, expected", ALL)
def test_idempotent(hk, expected):
    assert to_zuddha(expected) == expected


def test_case_ids_are_unique():
    ids = [f"{rule}:{cid}" for rule, cs in CASES.items() for cid, _, _ in cs]
    assert len(ids) == len(set(ids))


def test_matrix_is_complete():
    """One Z1 case per non-nasal stop, one Z2 per nasal, one Z4 pair per consonant and vowel."""
    z1 = {cid for cid, _, _ in CASES["Z1"]}
    stops = [c for c in CONSONANTS[:25] if c not in ("G", "J", "N", "n", "m")]
    assert len(stops) == 20
    assert {f"M+{s}" for s in stops} <= z1
    assert {f"M+{n}" for n in ("G", "J", "N", "n", "m")} == {c for c, _, _ in CASES["Z2"]}
    z4 = {cid for cid, _, _ in CASES["Z4"]}
    for c in CONSONANTS:
        assert f"M-before-{c}" in z4 and f"m-before-{c}" in z4
    for v in VOWELS:
        assert f"M-before-vowel-{v}" in z4 and f"m-before-vowel-{v}" in z4
