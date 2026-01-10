"""Tests for proposer implementations."""

import pytest

from motherlabs_kernel.ambiguity_types import Interpretation
from motherlabs_kernel.proposer_null import NullProposer
from motherlabs_kernel.proposer_recorded import RecordedProposer


def test_recorded_proposer_returns_stable_proposal_hash():
    """RecordedProposer returns stable proposal_hash."""
    interpretations = [
        Interpretation(name="A", assumptions=["a"], intent_summary="summary1"),
        Interpretation(name="B", assumptions=["b"], intent_summary="summary2"),
    ]
    
    recordings = {
        "interpretations:seed_hash_123:2": [
            {"name": "A", "assumptions": ["a"], "intent_summary": "summary1"},
            {"name": "B", "assumptions": ["b"], "intent_summary": "summary2"},
        ]
    }
    
    proposer = RecordedProposer(recordings)
    
    proposal1 = proposer.propose_interpretations("seed_hash_123", 2)
    proposal2 = proposer.propose_interpretations("seed_hash_123", 2)
    
    # Should produce same proposal hash
    assert proposal1.proposal_hash == proposal2.proposal_hash
    assert len(proposal1.value) == 2
    assert proposal1.value[0].name == "A"


def test_recorded_proposer_missing_key():
    """RecordedProposer raises KeyError for missing key."""
    proposer = RecordedProposer({})
    
    with pytest.raises(KeyError, match="No recording found"):
        proposer.propose_interpretations("seed_hash_123", 2)


def test_null_proposer_returns_empty_list():
    """NullProposer returns empty list deterministically."""
    proposer = NullProposer()
    
    proposal1 = proposer.propose_interpretations("seed_hash_123", 5)
    proposal2 = proposer.propose_interpretations("seed_hash_456", 10)
    
    assert proposal1.value == []
    assert proposal2.value == []
    assert proposal1.proposal_hash == proposal2.proposal_hash  # Empty lists hash same


def test_recorded_proposer_deterministic():
    """RecordedProposer is deterministic given same inputs."""
    recordings = {
        "interpretations:seed1:3": [
            {"name": "A", "assumptions": ["a"], "intent_summary": "sum1"},
            {"name": "B", "assumptions": ["b"], "intent_summary": "sum2"},
            {"name": "C", "assumptions": ["c"], "intent_summary": "sum3"},
        ]
    }
    
    proposer = RecordedProposer(recordings)
    
    proposal1 = proposer.propose_interpretations("seed1", 3)
    proposal2 = proposer.propose_interpretations("seed1", 3)
    
    assert proposal1.proposal_hash == proposal2.proposal_hash
    assert len(proposal1.value) == len(proposal2.value) == 3
    assert proposal1.value[0].name == proposal2.value[0].name
