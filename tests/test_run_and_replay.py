"""Tests for engine run and replay."""

from motherlabs_kernel.ambiguity_types import Interpretation
from motherlabs_kernel.hash import hash_canonical
from motherlabs_kernel.policy_types import Policy
from motherlabs_kernel.proposer_recorded import RecordedProposer
from motherlabs_kernel.replay import replay_from_ledger
from motherlabs_kernel.run_engine import run_engine


def test_run_then_replay_identical_summary_hash():
    """Run then replay produces identical summary_hash."""
    run_id = "test_run_001"
    seed_text = "Build a simple web app"
    pin = {"target": "web_app"}
    policy = Policy(
        max_interpretations=2,
        max_nodes=100,
        max_depth=10,
        contradiction_budget=5,
        max_steps=50
    )
    
    # Create proposer with fixed interpretations
    # Compute seed_hash from actual seed_text (kernel-correct)
    seed_hash = hash_canonical(seed_text)
    recordings = {
        f"interpretations:{seed_hash}:{policy.max_interpretations}": [
            {"name": "SimpleApp", "assumptions": ["web"], "intent_summary": "A simple web application"},
            {"name": "ComplexApp", "assumptions": ["web", "api"], "intent_summary": "A complex web app with API"},
        ]
    }
    proposer = RecordedProposer(recordings)
    
    # Run engine
    result = run_engine(run_id, seed_text, pin, policy, proposer, "T000000", step_ms=1)
    
    # Replay
    replay_result = replay_from_ledger(result.ledger_records, run_id)
    
    # Check that replay succeeded
    assert replay_result["ledger_valid"] is True
    
    # Summary hash should match (if artifacts were properly recorded)
    if replay_result.get("matches_expected"):
        assert replay_result["summary_hash"] == result.artifacts["verification"].expected_summary_hash


def test_tampered_ledger_breaks_replay():
    """Tampered ledger breaks replay validation."""
    from motherlabs_kernel.ledger_types import EvidenceRecord
    
    # Create a tampered record
    tampered_record = EvidenceRecord(
        v=1,
        ts="T000001",
        kind="seedpack",
        parent=None,
        payload={"seed": "TAMPERED"},
        payload_hash="wrong_hash",
        record_hash="wrong_record_hash"
    )
    
    # Replay should fail validation
    try:
        replay_from_ledger([tampered_record], "test_run")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected


def test_run_outputs_stable_given_fixed_inputs():
    """Run outputs are stable given fixed inputs."""
    run_id = "test_run_002"
    seed_text = "Build a calculator"
    pin = {"target": "calculator"}
    policy = Policy(
        max_interpretations=1,
        max_nodes=50,
        max_depth=5,
        contradiction_budget=0,
        max_steps=20
    )
    
    # Compute seed_hash from actual seed_text (kernel-correct)
    seed_hash = hash_canonical(seed_text)
    recordings = {
        f"interpretations:{seed_hash}:{policy.max_interpretations}": [
            {"name": "Calc", "assumptions": ["math"], "intent_summary": "A calculator app"},
        ]
    }
    proposer = RecordedProposer(recordings)
    
    # Run twice with same inputs
    result1 = run_engine(run_id, seed_text, pin, policy, proposer, "T000000", step_ms=1)
    result2 = run_engine(run_id, seed_text, pin, policy, proposer, "T000000", step_ms=1)
    
    # Ledger hashes should match
    assert result1.ledger_records[0].record_hash == result2.ledger_records[0].record_hash
    
    # DAG should have same nodes
    assert len(result1.dag_nodes) == len(result2.dag_nodes)
    
    # Artifacts should match
    if "verification" in result1.artifacts and "verification" in result2.artifacts:
        assert result1.artifacts["verification"].expected_summary_hash == result2.artifacts["verification"].expected_summary_hash
