"""Tests for policy validation and tie-breaking."""

import pytest

from motherlabs_kernel.policy import tie_break, validate_policy
from motherlabs_kernel.policy_types import Policy


def test_validate_policy_valid():
    """Valid policy passes validation."""
    policy = Policy(
        max_interpretations=3,
        max_nodes=100,
        max_depth=10,
        contradiction_budget=5,
        max_steps=50
    )
    # Should not raise
    validate_policy(policy)


def test_validate_policy_max_interpretations_invalid():
    """max_interpretations < 1 raises ValueError."""
    policy = Policy(
        max_interpretations=0,
        max_nodes=100,
        max_depth=10,
        contradiction_budget=5,
        max_steps=50
    )
    with pytest.raises(ValueError, match="max_interpretations"):
        validate_policy(policy)


def test_validate_policy_max_nodes_invalid():
    """max_nodes < 1 raises ValueError."""
    policy = Policy(
        max_interpretations=3,
        max_nodes=0,
        max_depth=10,
        contradiction_budget=5,
        max_steps=50
    )
    with pytest.raises(ValueError, match="max_nodes"):
        validate_policy(policy)


def test_validate_policy_max_depth_invalid():
    """max_depth < 1 raises ValueError."""
    policy = Policy(
        max_interpretations=3,
        max_nodes=100,
        max_depth=0,
        contradiction_budget=5,
        max_steps=50
    )
    with pytest.raises(ValueError, match="max_depth"):
        validate_policy(policy)


def test_validate_policy_contradiction_budget_invalid():
    """contradiction_budget < 0 raises ValueError."""
    policy = Policy(
        max_interpretations=3,
        max_nodes=100,
        max_depth=10,
        contradiction_budget=-1,
        max_steps=50
    )
    with pytest.raises(ValueError, match="contradiction_budget"):
        validate_policy(policy)


def test_validate_policy_max_steps_invalid():
    """max_steps < 1 raises ValueError."""
    policy = Policy(
        max_interpretations=3,
        max_nodes=100,
        max_depth=10,
        contradiction_budget=5,
        max_steps=0
    )
    with pytest.raises(ValueError, match="max_steps"):
        validate_policy(policy)


def test_validate_policy_tiebreak_invalid():
    """Invalid tiebreak method raises ValueError."""
    policy = Policy(
        max_interpretations=3,
        max_nodes=100,
        max_depth=10,
        contradiction_budget=5,
        max_steps=50,
        deterministic_tiebreak='invalid'  # type: ignore
    )
    with pytest.raises(ValueError, match="deterministic_tiebreak"):
        validate_policy(policy)


def test_tie_break_lexicographic():
    """tie_break selects lexicographically smallest string."""
    strings = ["zebra", "apple", "banana"]
    result = tie_break(strings)
    assert result == "apple"


def test_tie_break_lexicographic_deterministic():
    """tie_break is deterministic (same input = same output)."""
    strings = ["zebra", "apple", "banana"]
    result1 = tie_break(strings)
    result2 = tie_break(strings)
    assert result1 == result2 == "apple"


def test_tie_break_lexicographic_order_invariant():
    """tie_break result is invariant to input order."""
    strings1 = ["zebra", "apple", "banana"]
    strings2 = ["banana", "zebra", "apple"]
    strings3 = ["apple", "banana", "zebra"]
    
    result1 = tie_break(strings1)
    result2 = tie_break(strings2)
    result3 = tie_break(strings3)
    
    assert result1 == result2 == result3 == "apple"


def test_tie_break_empty_list():
    """tie_break raises ValueError for empty list."""
    with pytest.raises(ValueError, match="empty"):
        tie_break([])


def test_tie_break_single_item():
    """tie_break returns single item."""
    result = tie_break(["single"])
    assert result == "single"


def test_tie_break_invalid_method():
    """tie_break raises ValueError for invalid method."""
    with pytest.raises(ValueError, match="Unknown tie-break method"):
        tie_break(["a", "b"], method="invalid")


def test_tie_break_case_sensitive():
    """tie_break is case-sensitive (lexicographic order)."""
    strings = ["Apple", "apple", "BANANA"]
    result = tie_break(strings)
    # 'A' < 'B' < 'a' in ASCII
    assert result == "Apple"
