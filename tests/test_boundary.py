"""Tests for Proposal vs Commit boundary."""

from motherlabs_kernel.commit_types import Commit
from motherlabs_kernel.proposal_types import Proposal


def test_proposal_deterministic_hash():
    """Proposal hashing is deterministic."""
    proposal1 = Proposal.create("llm", {"data": "value"}, confidence=0.9)
    proposal2 = Proposal.create("llm", {"data": "value"}, confidence=0.9)
    
    assert proposal1.proposal_hash == proposal2.proposal_hash


def test_proposal_hash_includes_source_confidence_value():
    """Proposal hash includes source, confidence, and value."""
    proposal1 = Proposal.create("llm", {"data": "value1"}, confidence=0.9)
    proposal2 = Proposal.create("retrieval", {"data": "value1"}, confidence=0.9)
    proposal3 = Proposal.create("llm", {"data": "value2"}, confidence=0.9)
    proposal4 = Proposal.create("llm", {"data": "value1"}, confidence=0.8)
    
    # All should have different hashes
    hashes = {p.proposal_hash for p in [proposal1, proposal2, proposal3, proposal4]}
    assert len(hashes) == 4


def test_commit_deterministic_hash():
    """Commit hashing is deterministic."""
    commit1 = Commit.create({"data": "value"}, accepted_from="proposal_hash_123")
    commit2 = Commit.create({"data": "value"}, accepted_from="proposal_hash_123")
    
    assert commit1.commit_hash == commit2.commit_hash


def test_commit_hash_includes_value_accepted_from():
    """Commit hash includes value and accepted_from."""
    commit1 = Commit.create({"data": "value1"}, accepted_from="prop1")
    commit2 = Commit.create({"data": "value2"}, accepted_from="prop1")
    commit3 = Commit.create({"data": "value1"}, accepted_from="prop2")
    commit4 = Commit.create({"data": "value1"}, accepted_from=None)
    
    # All should have different hashes
    hashes = {c.commit_hash for c in [commit1, commit2, commit3, commit4]}
    assert len(hashes) == 4


def test_proposal_commit_cannot_be_confused():
    """Proposals and commits have different structure and cannot be confused."""
    proposal = Proposal.create("llm", {"data": "value"})
    commit = Commit.create({"data": "value"})
    
    # Different fields
    assert hasattr(proposal, "source")
    assert hasattr(proposal, "proposal_hash")
    assert not hasattr(proposal, "commit_hash")
    
    assert hasattr(commit, "commit_hash")
    assert hasattr(commit, "accepted_from")
    assert not hasattr(commit, "source")
    assert not hasattr(commit, "proposal_hash")
    
    # Different hash values (even with same value)
    assert proposal.proposal_hash != commit.commit_hash


def test_proposal_acceptance_creates_commit():
    """Accepting a proposal creates a commit with accepted_from."""
    proposal = Proposal.create("llm", {"data": "value"}, confidence=0.9)
    
    # Accept the proposal
    commit = Commit.create(proposal.value, accepted_from=proposal.proposal_hash)
    
    assert commit.value == proposal.value
    assert commit.accepted_from == proposal.proposal_hash


def test_commit_without_proposal():
    """Commits can be created without a proposal (direct kernel decision)."""
    commit = Commit.create({"data": "value"}, accepted_from=None)
    
    assert commit.value == {"data": "value"}
    assert commit.accepted_from is None
    assert commit.commit_hash is not None


def test_proposal_commit_type_hints():
    """Proposals and commits support type hints via Generic."""
    proposal: Proposal[dict] = Proposal.create("llm", {"key": "value"})
    commit: Commit[dict] = Commit.create({"key": "value"})
    
    assert isinstance(proposal.value, dict)
    assert isinstance(commit.value, dict)


def test_proposal_confidence_none():
    """Proposals can have None confidence."""
    proposal = Proposal.create("llm", {"data": "value"}, confidence=None)
    
    assert proposal.confidence is None
    assert proposal.proposal_hash is not None


def test_proposal_equivalent_values_hash_identically():
    """Equivalent proposal values hash identically (canonicalization)."""
    # Same dict with different key order
    proposal1 = Proposal.create("llm", {"a": 1, "b": 2})
    proposal2 = Proposal.create("llm", {"b": 2, "a": 1})
    
    # Should hash identically due to canonicalization
    assert proposal1.proposal_hash == proposal2.proposal_hash
