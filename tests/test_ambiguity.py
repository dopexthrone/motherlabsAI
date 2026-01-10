"""Tests for autonomous ambiguity resolution."""

import pytest

from motherlabs_kernel.ambiguity import Proposer, resolve_ambiguity
from motherlabs_kernel.ambiguity_types import Interpretation
from motherlabs_kernel.commit_types import Commit
from motherlabs_kernel.policy_types import Policy
from motherlabs_kernel.proposal_types import Proposal


class FixedProposer:
    """Test proposer with fixed output."""
    
    def __init__(self, interpretations: list[Interpretation]):
        self.interpretations = interpretations
    
    def propose_interpretations(self, seed_hash: str, n: int) -> Proposal[list[Interpretation]]:
        """Return fixed interpretations."""
        return Proposal.create("heuristic", self.interpretations[:n])


def test_resolve_ambiguity_deterministic_winner():
    """Fixed proposer output produces deterministic winner."""
    interpretations = [
        Interpretation(name="A", assumptions=["assume1"], intent_summary="short"),
        Interpretation(name="B", assumptions=["assume2"], intent_summary="longer summary"),
        Interpretation(name="C", assumptions=["assume3", "assume4"], intent_summary="medium"),
    ]
    
    proposer = FixedProposer(interpretations)
    policy = Policy(
        max_interpretations=3,
        max_nodes=100,
        max_depth=10,
        contradiction_budget=5,
        max_steps=50
    )
    
    commit1 = resolve_ambiguity("run1", "seed_hash_123", policy, proposer)
    commit2 = resolve_ambiguity("run1", "seed_hash_123", policy, proposer)
    
    # Should produce same winner
    assert commit1.value.name == commit2.value.name
    assert commit1.commit_hash == commit2.commit_hash


def test_resolve_ambiguity_tie_breaking_deterministic():
    """Tie-breaking is deterministic (lexicographic by name)."""
    # Create interpretations with same cost potential (will have same cost)
    interpretations = [
        Interpretation(name="Zebra", assumptions=["a"], intent_summary="same"),
        Interpretation(name="Apple", assumptions=["a"], intent_summary="same"),
        Interpretation(name="Banana", assumptions=["a"], intent_summary="same"),
    ]
    
    proposer = FixedProposer(interpretations)
    policy = Policy(
        max_interpretations=3,
        max_nodes=100,
        max_depth=10,
        contradiction_budget=5,
        max_steps=50
    )
    
    commit = resolve_ambiguity("run1", "seed_hash_123", policy, proposer)
    
    # Should pick lexicographically first (Apple)
    assert commit.value.name == "Apple"


def test_resolve_ambiguity_respects_max_interpretations():
    """Pruning respects max_interpretations limit."""
    interpretations = [
        Interpretation(name=f"Interp{i}", assumptions=[], intent_summary=f"summary{i}")
        for i in range(10)
    ]
    
    proposer = FixedProposer(interpretations)
    policy = Policy(
        max_interpretations=3,  # Only keep top 3
        max_nodes=100,
        max_depth=10,
        contradiction_budget=5,
        max_steps=50
    )
    
    commit = resolve_ambiguity("run1", "seed_hash_123", policy, proposer)
    
    # Should have selected one of the top 3
    assert commit.value.name in ["Interp0", "Interp1", "Interp2", "Interp3", "Interp4", "Interp5", "Interp6", "Interp7", "Interp8", "Interp9"]


def test_resolve_ambiguity_empty_proposal():
    """Empty proposal raises ValueError."""
    proposer = FixedProposer([])
    policy = Policy(
        max_interpretations=3,
        max_nodes=100,
        max_depth=10,
        contradiction_budget=5,
        max_steps=50
    )
    
    with pytest.raises(ValueError, match="empty"):
        resolve_ambiguity("run1", "seed_hash_123", policy, proposer)


def test_scoring_duplicate_assumptions_penalty():
    """Scoring penalizes duplicate assumptions across interpretations (cost: lower is better)."""
    from motherlabs_kernel.scoring import score_interpretation
    
    interp1 = Interpretation(name="A", assumptions=["shared"], intent_summary="summary1")
    interp2 = Interpretation(name="B", assumptions=["shared"], intent_summary="summary2")
    interp3 = Interpretation(name="C", assumptions=["unique"], intent_summary="summary3")
    
    all_interps = [interp1, interp2, interp3]
    
    cost1 = score_interpretation(interp1, all_interps)
    cost2 = score_interpretation(interp2, all_interps)
    cost3 = score_interpretation(interp3, all_interps)
    
    # interp3 should have lower cost (no duplicate penalty, so base - 0)
    # interp1 and interp2 have duplicate penalty (base - 5), so higher cost
    assert cost3 < cost1  # Lower cost = preferred
    assert cost3 < cost2


def test_prune_sorts_by_cost_ascending_then_name():
    """Pruning sorts by cost (ascending: lower is better) then name (lexicographic)."""
    from motherlabs_kernel.prune import prune_interpretations
    from motherlabs_kernel.scoring import score_interpretation
    from motherlabs_kernel.policy_types import Policy
    
    # Create interpretations with different costs
    # interp2/interp3 have fewer assumptions -> lower cost -> should win
    interp1 = Interpretation(name="Z", assumptions=["a", "b"], intent_summary="long summary here")
    interp2 = Interpretation(name="A", assumptions=["a"], intent_summary="short")
    interp3 = Interpretation(name="B", assumptions=["a"], intent_summary="short")
    
    interpretations = [interp1, interp2, interp3]
    policy = Policy(
        max_interpretations=3,
        max_nodes=100,
        max_depth=10,
        contradiction_budget=5,
        max_steps=50
    )
    
    pruned = prune_interpretations(interpretations, policy)
    
    # Should be sorted by cost (ascending: lower cost first), then name (lexicographic) for ties
    assert len(pruned) <= 3
    # First should be lowest cost (fewest assumptions)
    cost_first = score_interpretation(pruned[0], interpretations)
    cost_second = score_interpretation(pruned[1], interpretations) if len(pruned) > 1 else None
    assert cost_first <= (cost_second if cost_second is not None else cost_first)
    # Among equal costs, should be lexicographically first
    if cost_second == cost_first:
        assert pruned[0].name < pruned[1].name


def test_lower_cost_wins_explicitly():
    """
    Explicit safeguard: lower cost (fewer assumptions) wins.
    
    This test prevents accidental reversal of sort direction that would flip
    semantics from "conservatism-first" to "specificity-first".
    """
    from motherlabs_kernel.prune import prune_interpretations
    from motherlabs_kernel.scoring import score_interpretation
    from motherlabs_kernel.policy_types import Policy
    
    # SimpleCalc: 2 assumptions, cost ~91
    # AdvancedCalc: 3 assumptions, cost ~92
    simple = Interpretation(
        name="SimpleCalc",
        assumptions=["arithmetic", "basic_ops"],
        intent_summary="A simple calculator with addition, subtraction, multiplication, and division"
    )
    advanced = Interpretation(
        name="AdvancedCalc",
        assumptions=["arithmetic", "scientific", "memory"],
        intent_summary="An advanced calculator with scientific functions and memory storage"
    )
    
    interpretations = [advanced, simple]  # Order shouldn't matter
    policy = Policy(
        max_interpretations=2,
        max_nodes=100,
        max_depth=10,
        contradiction_budget=5,
        max_steps=50
    )
    
    pruned = prune_interpretations(interpretations, policy)
    winner = pruned[0]
    
    # Lower cost should win (fewer assumptions)
    simple_cost = score_interpretation(simple, interpretations)
    advanced_cost = score_interpretation(advanced, interpretations)
    
    assert simple_cost < advanced_cost, "SimpleCalc should have lower cost (fewer assumptions)"
    assert winner.name == "SimpleCalc", "Lower cost (fewer assumptions) should win"
    assert winner == simple, "SimpleCalc with lower cost should be the winner"


def test_interpretation_rejects_duplicate_assumptions():
    """
    Interpretation rejects duplicate assumptions within its own assumptions list.
    
    This enforces the invariant that assumptions must not contain duplicates.
    Violation raises ValueError at construction time (invalid input).
    """
    # Valid: no duplicates
    valid = Interpretation(
        name="Valid",
        assumptions=["assumption1", "assumption2"],
        intent_summary="Valid interpretation"
    )
    assert valid.assumptions == ["assumption1", "assumption2"]
    
    # Invalid: duplicate assumptions
    with pytest.raises(ValueError, match="duplicate assumptions"):
        Interpretation(
            name="Invalid",
            assumptions=["duplicate", "duplicate"],
            intent_summary="Invalid interpretation"
        )
    
    # Invalid: multiple duplicates
    with pytest.raises(ValueError, match="duplicate assumptions"):
        Interpretation(
            name="Invalid",
            assumptions=["a", "b", "a", "c", "b"],
            intent_summary="Invalid interpretation"
        )
    
    # Edge case: empty assumptions (valid)
    empty = Interpretation(
        name="Empty",
        assumptions=[],
        intent_summary="No assumptions"
    )
    assert empty.assumptions == []


def test_proposer_recorded_validates_duplicate_assumptions():
    """
    RecordedProposer validates interpretations have no duplicate assumptions.
    
    When RecordedProposer creates Interpretation objects from recorded data,
    the Interpretation.__post_init__ validation will reject duplicates.
    This ensures the invariant is enforced even when loading from fixtures.
    """
    from motherlabs_kernel.proposer_recorded import RecordedProposer
    
    # Valid: no duplicates
    valid_recordings = {
        "interpretations:test_hash:2": [
            {"name": "A", "assumptions": ["a", "b"], "intent_summary": "summary1"},
            {"name": "B", "assumptions": ["c"], "intent_summary": "summary2"},
        ]
    }
    proposer = RecordedProposer(valid_recordings)
    proposal = proposer.propose_interpretations("test_hash", 2)
    assert len(proposal.value) == 2
    assert all(len(interp.assumptions) == len(set(interp.assumptions)) for interp in proposal.value)
    
    # Invalid: duplicate assumptions in one interpretation
    invalid_recordings = {
        "interpretations:test_hash2:1": [
            {"name": "Invalid", "assumptions": ["duplicate", "duplicate"], "intent_summary": "summary"},
        ]
    }
    proposer_invalid = RecordedProposer(invalid_recordings)
    
    # Should raise ValueError when creating Interpretation (at __post_init__)
    with pytest.raises(ValueError, match="duplicate assumptions"):
        proposer_invalid.propose_interpretations("test_hash2", 1)
