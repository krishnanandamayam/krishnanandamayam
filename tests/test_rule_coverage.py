"""A rule in tools.hk.RULES without tests fails the build."""

from tests import test_to_saraLa, test_to_zuddha
from tools.hk import RULES


def test_every_rule_has_cases():
    cases = {**test_to_zuddha.CASES, **test_to_saraLa.CASES}
    missing = [rule for rule in RULES if not cases.get(rule)]
    assert not missing, f"rules with no test cases: {missing}"


def test_no_cases_for_unknown_rules():
    cases = {**test_to_zuddha.CASES, **test_to_saraLa.CASES}
    assert set(cases) <= set(RULES)


def test_each_rule_is_documented():
    assert all(text.strip() for text in RULES.values())
