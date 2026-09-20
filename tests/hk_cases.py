"""Literal alphabet tables shared by the to_zuddha / to_saraLa suites.

These are written out by hand on purpose: they must not be imported from tools.hk, or a
mistake in the code's tables would be copied into the tests.
"""

# All 34 consonants of Harvard-Kyoto, varga by varga, then the rest.
CONSONANTS = [
    "k", "kh", "g", "gh", "G",
    "c", "ch", "j", "jh", "J",
    "T", "Th", "D", "Dh", "N",
    "t", "th", "d", "dh", "n",
    "p", "ph", "b", "bh", "m",
    "y", "r", "l", "v", "z", "S", "s", "h", "L",
]  # fmt: skip
assert len(CONSONANTS) == 34 and len(set(CONSONANTS)) == 34

VOWELS = ["a", "A", "i", "I", "u", "U", "R", "RR", "lR", "e", "ai", "o", "au", "E", "O"]

NASALS = ["G", "J", "N", "n", "m"]

# What can follow the last letter of a word.
WORD_ENDERS = [
    "", " ", "  ", "\n", "\t", " .", " ..", ".", "..", " |", " ||", "|", "||",
    ",", ", ", ";", "!", "?", ":", " :", "-", " - ", ")", "]", '"', "”", "'", "’", " 'pi",
    " 12", "1",
]  # fmt: skip
