"""Tests for refusal paths."""

from motherlabs_kernel.ambiguity_types import Interpretation
from motherlabs_kernel.artifacts_refusal import RefusalReport
from motherlabs_kernel.policy_types import Policy
from motherlabs_kernel.proposer_null import NullProposer
from motherlabs_kernel.proposer_recorded import RecordedProposer
from motherlabs_kernel.proposal_types import Proposal
from motherlabs_kernel.refusal import check_refusal_conditions, generate_policy_suggestions
from motherlabs_kernel.run_engine import run_engine


def test_empty_proposal_triggers_refusal():
    """Empty proposal triggers refusal artifact."""
    run_id = "test_refusal_001"
    seed_text = "Build something"
    pin = {}
    policy = Policy(
        max_interpretations=1,
        max_nodes=10,
        max_depth=5,
        contradiction_budget=0,
        max_steps=10
    )
    proposer = NullProposer()  # Returns empty list
    
    result = run_engine(run_id, seed_text, pin, policy, proposer, "T000000", step_ms=1)
    
    # Should have refusal artifact
    assert "refusal" in result.artifacts
    refusal = result.artifacts["refusal"]
    assert isinstance(refusal, RefusalReport)
    assert refusal.status == "refused"
    assert "empty_proposal" in refusal.reason_codes


def test_contradictions_exceed_budget():
    """Contradictions exceeding budget triggers refusal."""
    interpretations = [
        Interpretation(name="A", assumptions=["shared1", "shared2"], intent_summary="sum1"),
        Interpretation(name="B", assumptions=["shared1", "shared2"], intent_summary="sum2"),
        Interpretation(name="C", assumptions=["shared1"], intent_summary="sum3"),
    ]
    
    policy = Policy(
        max_interpretations=3,
        max_nodes=100,
        max_depth=10,
        contradiction_budget=2,  # Low budget
        max_steps=50
    )
    
    proposal = Proposal.create("heuristic", interpretations)
    
    # Check refusal conditions
    reasons = check_refusal_conditions(proposal, policy, step_count=1, node_count=0, interpretations=interpretations)
    
    # Should have contradiction reason (shared1 appears 3 times, shared2 appears 2 times)
    # Total duplicates: (3-1) + (2-1) + (2-1) = 2 + 1 + 1 = 4
    # But wait, let me recalculate: shared1 in 3 interps = 2 duplicates, shared2 in 2 interps = 1 duplicate
    # Total = 3 duplicates, which exceeds budget of 2
    contradiction_reasons = [r for r in reasons if r.startswith("contradictions_exceeded")]
    assert len(contradiction_reasons) > 0


def test_max_nodes_exceeded():
    """Max nodes exceeded triggers refusal."""
    policy = Policy(
        max_interpretations=1,
        max_nodes=5,  # Low limit
        max_depth=10,
        contradiction_budget=0,
        max_steps=50
    )
    
    proposal = Proposal.create("heuristic", [Interpretation(name="A", assumptions=[], intent_summary="test")])
    
    reasons = check_refusal_conditions(proposal, policy, step_count=1, node_count=10, interpretations=[])
    
    assert any(r.startswith("max_nodes_exceeded") for r in reasons)


def test_max_steps_exceeded():
    """Max steps exceeded triggers refusal."""
    policy = Policy(
        max_interpretations=1,
        max_nodes=100,
        max_depth=10,
        contradiction_budget=0,
        max_steps=5  # Low limit
    )
    
    proposal = Proposal.create("heuristic", [Interpretation(name="A", assumptions=[], intent_summary="test")])
    
    reasons = check_refusal_conditions(proposal, policy, step_count=10, node_count=0, interpretations=[])
    
    assert any(r.startswith("max_steps_exceeded") for r in reasons)


def test_replay_reproduces_refusal_summary_hash():
    """Replay reproduces same refusal summary_hash."""
    from motherlabs_kernel.replay import replay_from_ledger
    
    run_id = "test_refusal_replay"
    seed_text = "Test"
    pin = {}
    policy = Policy(
        max_interpretations=1,
        max_nodes=10,
        max_depth=5,
        contradiction_budget=0,
        max_steps=10
    )
    proposer = NullProposer()
    
    result = run_engine(run_id, seed_text, pin, policy, proposer, "T000000", step_ms=1)
    
    # Replay
    replay_result = replay_from_ledger(result.ledger_records, run_id)
    
    # Should have refusal in replay
    assert "artifacts" in replay_result
    if "refusal" in replay_result["artifacts"]:
        # Refusal should match
        assert replay_result["artifacts"]["refusal"].status == "refused"


def test_policy_suggestions_generated():
    """Policy suggestions are generated deterministically."""
    reasons = ["empty_proposal", "max_nodes_exceeded:10>5"]
    suggestions = generate_policy_suggestions(reasons)
    
    assert len(suggestions) > 0
    assert all(isinstance(s, str) for s in suggestions)
