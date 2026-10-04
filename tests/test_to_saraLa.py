"""to_saraLa: every transformation, one named case each.

The heart of the suite is the full 5 nasals x 34 consonants matrix: the 20 cells that convert
are written out literally in CONVERTS; the other 150 must come back unchanged.
"""

import pytest

from tests.hk_cases import CONSONANTS, NASALS, VOWELS, WORD_ENDERS
from tools.hk import to_saraLa

CASES: dict[str, list[tuple[str, str, str]]] = {}

# (nasal, following consonant) -> expected, for a nasal between "a" and the consonant + "a".
CONVERTS = {
    ("G", "k"): "aMka", ("G", "kh"): "aMkha", ("G", "g"): "aMga", ("G", "gh"): "aMgha",
    ("J", "c"): "aMca", ("J", "ch"): "aMcha", ("J", "j"): "aMja", ("J", "jh"): "aMjha",
    ("N", "T"): "aMTa", ("N", "Th"): "aMTha", ("N", "D"): "aMDa", ("N", "Dh"): "aMDha",
    ("n", "t"): "aMta", ("n", "th"): "aMtha", ("n", "d"): "aMda", ("n", "dh"): "aMdha",
    ("m", "p"): "aMpa", ("m", "ph"): "aMpha", ("m", "b"): "aMba", ("m", "bh"): "aMbha",
}  # fmt: skip
assert len(CONVERTS) == 20

# ---- S1: the 20 converting cells, plus real words -----------------------------------------
CASES["S1"] = [(f"{n}+{c}", f"a{n}{c}a", exp) for (n, c), exp in CONVERTS.items()] + [
    ("word-gaGgA", "gaGgA", "gaMgA"),
    ("word-zaGkha", "zaGkha", "zaMkha"),
    ("word-paJca", "paJca", "paMca"),
    ("word-kuJja", "kuJja", "kuMja"),
    ("word-kaNTha", "kaNTha", "kaMTha"),
    ("word-daNDa", "daNDa", "daMDa"),
    ("word-nanda", "nanda", "naMda"),
    ("word-zAnta", "zAnta", "zAMta"),
    ("word-bandha", "bandha", "baMdha"),
    ("word-zambhu", "zambhu", "zaMbhu"),
    ("word-ambA", "ambA", "aMbA"),
    ("word-saJjJA", "saJjJA", "saMjJA"),
    ("word-saGkSepa", "saGkSepa", "saMkSepa"),
    ("after-A", "AGka", "AMka"),
    ("after-i", "iGka", "iMka"),
    ("after-I", "IGka", "IMka"),
    ("after-u", "uGka", "uMka"),
    ("after-U", "UGka", "UMka"),
    ("after-R", "kRnta", "kRMta"),
    ("after-e", "eGka", "eMka"),
    ("after-ai", "aiGka", "aiMka"),
    ("after-o", "koGka", "koMka"),
    ("after-au", "auGka", "auMka"),
    ("after-E", "EGka", "EMka"),
    ("after-O", "OGka", "OMka"),
    ("several-in-one-word", "saGkaTaGkaNTaka", "saMkaTaMkaMTaka"),
    ("several-in-one-line", "paJca gaGgA zambhu nanda", "paMca gaMgA zaMbhu naMda"),
    ("already-saraLa", "gaMgA paMca", "gaMgA paMca"),
    ("telugu-word", "anugrahiJci", "anugrahiMci"),
    ("telugu-word-2", "santasaparacEda", "saMtasaparacEda"),
]

# ---- S2: nasal + nasal, all 25 cells --------------------------------------------------------
CASES["S2"] = [(f"{a}+{b}", f"a{a}{b}a", f"a{a}{b}a") for a in NASALS for b in NASALS] + [
    ("word-amma", "amma", "amma"),
    ("word-anna", "anna", "anna"),
    ("word-janma", "janma", "janma"),
    ("word-sammAna", "sammAna", "sammAna"),
    ("word-sannidhi", "sannidhi", "sannidhi"),
    ("word-kannayya", "kannayya", "kannayya"),
    ("word-viSaNNa", "viSaNNa", "viSaNNa"),
]

# ---- S3: nasal + consonant that is not a stop of its own varga, all remaining cells ---------
CASES["S3"] = [
    (f"{n}+{c}", f"a{n}{c}a", f"a{n}{c}a")
    for n in NASALS
    for c in CONSONANTS
    if (n, c) not in CONVERTS and c not in NASALS
] + [
    ("word-jJAna", "jJAna", "jJAna"),
    ("word-yajJa", "yajJa", "yajJa"),
    ("word-tanmaya", "tanmaya", "tanmaya"),
    ("word-vAGmaya", "vAGmaya", "vAGmaya"),
    ("word-puNya", "puNya", "puNya"),
    ("word-kRSNa", "kRSNa", "kRSNa"),
    ("word-samrAT", "samrAT", "samrAT"),
    ("word-amRta", "amRta", "amRta"),
    ("word-nyAya", "nyAya", "nyAya"),
    ("word-anya", "anya", "anya"),
    ("word-kanyA", "kanyA", "kanyA"),
    ("word-brahmANDa-hm", "brahma", "brahma"),
    ("case:n+T", "anTa", "anTa"),
    ("case:N+t", "aNta", "aNta"),
    ("case:n+D", "anDa", "anDa"),
    ("case:N+dh", "aNdha", "aNdha"),
    # a nasal that does not follow a vowel is not an anusvara candidate
    ("after-consonant", "arGka", "arGka"),
    ("at-start-of-text", "Gka", "Gka"),
    ("after-visarga", "aHnta", "aHnta"),
    # nasal + vowel
    *[(f"nasal-{n}-before-vowel-{v}", f"a{n}{v}", f"a{n}{v}") for n in NASALS for v in VOWELS],
    # M itself inside a word is never changed by to_saraLa
    ("M+y", "saMyama", "saMyama"),
    ("M+z", "saMzaya", "saMzaya"),
    ("M+h", "siMha", "siMha"),
]

# ---- S4: word-final m and M -> M -----------------------------------------------------------
CASES["S4"] = (
    [(f"m-before-{c}", f"rAmam {c}a", f"rAmaM {c}a") for c in CONSONANTS]
    + [(f"M-before-{c}", f"rAmaM {c}a", f"rAmaM {c}a") for c in CONSONANTS]
    + [(f"m-before-vowel-{v}", f"rAmam {v}ti", f"rAmaM {v}ti") for v in VOWELS]
    + [(f"M-before-vowel-{v}", f"rAmaM {v}ti", f"rAmaM {v}ti") for v in VOWELS]
    + [(f"m-before-{e!r}", f"rAmam{e}", f"rAmaM{e}") for e in WORD_ENDERS]
    + [(f"M-before-{e!r}", f"rAmaM{e}", f"rAmaM{e}") for e in WORD_ENDERS]
    + [
        ("every-word", "zrIkaram zubhakaram zivam", "zrIkaraM zubhakaraM zivaM"),
        ("after-long-vowel", "devIm", "devIM"),
        ("final-and-internal", "saGkaTam", "saMkaTaM"),
        ("hyphen-is-a-break", "yugam-mama", "yugaM-mama"),
        ("lone-m", "m", "M"),
        # only m: the other nasals and consonants stay as they are at the end of a word
        ("final-n-kept", "bhagavAn ca", "bhagavAn ca"),
        ("final-n-before-t-kept", "bhagavAn tatra", "bhagavAn tatra"),
        ("final-G-kept", "pratyaG", "pratyaG"),
        ("final-N-kept", "sugaN", "sugaN"),
        ("final-J-kept", "aJ", "aJ"),
        ("final-k-kept", "vAk ca", "vAk ca"),
        ("final-t-kept", "tat sat", "tat sat"),
        ("telugu-final-mu-kept", "rAmanAmamu", "rAmanAmamu"),
        # a nasal is never converted because of a stop in the NEXT word
        ("no-conversion-across-words-n", "bhagavAn dadAti", "bhagavAn dadAti"),
    ]
)

# ---- S5: everything else is untouched ------------------------------------------------------
_UNTOUCHED = [
    "", " ", "\n", "a", "kRSNa", "zrIH", "namaH", "kSetra", "lakSmI", "'pi", "so'haH",
    "a~", "klRpta", "kaLyANa", "kOlturu", "paracEda", "nanukOlturubhaktulu", "mama", "nAma",
    "madhu", "12", "7:5:23", "1. dhyAna", "(zrI)", "[zrI]", '"zrI"', "“zrI”", "zrI - rAma",
    "a  b", "a\tb", "rAma . kRSNa ..", "rAma | kRSNa ||", "rAma, kRSNa; ziva! hari?",
]  # fmt: skip
CASES["S5"] = [(f"untouched-{i}-{s!r}", s, s) for i, s in enumerate(_UNTOUCHED)] + [
    (f"vowel-{v}-untouched", f"k{v}ta", f"k{v}ta") for v in VOWELS
] + [(f"consonant-{c}-untouched", f"a{c}a", f"a{c}a") for c in CONSONANTS]

# ---- S6: the pranava ------------------------------------------------------------------------
CASES["S6"] = [
    ("oM", "oM", "oM"),
    ("om", "om", "oM"),
    ("om-danda", "om.", "oM."),
    ("om-then-word", "om namaH zivAya", "oM namaH zivAya"),
    ("mid-line", "hariH om tat", "hariH oM tat"),
    ("not-pranava-soma", "soma", "soma"),
    ("not-pranava-kom", "kom", "koM"),
    ("oGkAra", "oGkAra", "oMkAra"),
]

# ---- S7: braces keep a run as typed --------------------------------------------------
CASES["S7"] = [
    ("class-nasal-kept", "{gaGgA}", "{gaGgA}"),
    ("word-final-m", "{rAmam} ca", "{rAmam} ca"),
    ("only-the-braced-word", "gaGgA {gaGgA} gaGgA", "gaMgA {gaGgA} gaMgA"),
    ("nasal-before-a-brace-is-inside-the-word", "saG{gIta} rAmam{}", "saM{gIta} rAmaM{}"),
    ("unclosed-brace-protects-nothing", "{gaGgA", "{gaMgA"),
]

ALL = [pytest.param(i, e, id=f"{rule}:{cid}") for rule, cs in CASES.items() for cid, i, e in cs]


@pytest.mark.parametrize("hk, expected", ALL)
def test_to_saraLa(hk, expected):
    assert to_saraLa(hk) == expected


@pytest.mark.parametrize("hk, expected", ALL)
def test_length_preserved(hk, expected):
    assert len(to_saraLa(hk)) == len(hk)


@pytest.mark.parametrize("hk, expected", ALL)
def test_idempotent(hk, expected):
    assert to_saraLa(expected) == expected


def test_case_ids_are_unique():
    ids = [f"{rule}:{cid}" for rule, cs in CASES.items() for cid, _, _ in cs]
    assert len(ids) == len(set(ids))


def test_matrix_is_complete():
    """Every one of the 5 x 34 = 170 nasal + consonant cells has a named case."""
    seen = set()
    for rule in ("S1", "S2", "S3"):
        for cid, _, _ in CASES[rule]:
            n, plus, c = cid.partition("+")
            if plus and n in NASALS and c in CONSONANTS:
                seen.add((n, c))
    assert seen == {(n, c) for n in NASALS for c in CONSONANTS}
    assert len(seen) == 170
