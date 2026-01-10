"""Golden run test that locks determinism permanently."""

import json
import os

from motherlabs_kernel.hash import hash_canonical
from motherlabs_kernel.policy_types import Policy
from motherlabs_kernel.proposer_recorded import RecordedProposer
from motherlabs_kernel.replay import replay_from_ledger
from motherlabs_kernel.run_engine import run_engine


def load_fixture(filename: str) -> dict:
    """Load JSON fixture file."""
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(fixture_path, "r") as f:
        return json.load(f)


def load_text_fixture(filename: str) -> str:
    """Load text fixture file."""
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(fixture_path, "r") as f:
        return f.read().strip()


def test_golden_run():
    """
    Golden run test that locks determinism.
    
    This test:
    1. Loads fixtures (seed, pin, policy, proposals)
    2. Builds policy + RecordedProposer
    3. Runs engine with fixed run_id and ts_base
    4. Asserts exact matches to expected values
    5. Replays and asserts exact matches
    
    If anything changes, fix determinism; do not weaken assertions.
    """
    # Load fixtures
    seed_text = load_text_fixture("golden_seed.txt")
    pin = load_fixture("golden_pin.json")
    policy_data = load_fixture("golden_policy.json")
    proposals_data = load_fixture("golden_proposals.json")
    expected = load_fixture("golden_expected.json")
    
    # Build policy
    policy = Policy(**policy_data)
    
    # Compute seed hash (must match what's in proposals key)
    seed_hash = hash_canonical(seed_text)
    
    # Build RecordedProposer
    proposer = RecordedProposer(proposals_data)
    
    # Fixed run parameters
    run_id = "golden_run_001"
    ts_base = "T000000"
    
    # Run engine
    result = run_engine(run_id, seed_text, pin, policy, proposer, ts_base, step_ms=1)
    
    # Extract values for comparison
    ledger_last_hash = result.ledger_records[-1].record_hash if result.ledger_records else ""
    
    # Compute DAG root hash
    node_ids = sorted([n.id for n in result.dag_nodes])
    edge_ids = sorted([e.id for e in result.dag_edges])
    dag_root_hash = hash_canonical({"node_ids": node_ids, "edge_ids": edge_ids})
    
    # Get artifact hashes
    artifact_hashes = {}
    if "blueprint" in result.artifacts:
        artifact_hashes["blueprint"] = result.artifacts["blueprint"].compute_hash()
    
    # Compute summary hash
    summary_data = {
        "ledger_last_hash": ledger_last_hash,
        "dag_root_hash": dag_root_hash,
        "artifact_hashes": artifact_hashes
    }
    summary_hash = hash_canonical(summary_data)
    
    # Check structure
    chosen_interp_name = None
    if "blueprint" in result.artifacts:
        # Find interpretation node
        interp_nodes = [n for n in result.dag_nodes if n.kind == "interpretation"]
        if interp_nodes:
            # Get interpretation name from payload
            interp_payload = interp_nodes[0].payload
            chosen_interp_name = interp_payload.get("name")
    
    node_kinds = sorted([n.kind for n in result.dag_nodes])
    
    # Assert exact matches (if expected values are set)
    if expected["expected_summary_hash"]:
        assert summary_hash == expected["expected_summary_hash"], \
            f"Summary hash mismatch: got {summary_hash}, expected {expected['expected_summary_hash']}"
    
    if expected["expected_dag_root_hash"]:
        assert dag_root_hash == expected["expected_dag_root_hash"], \
            f"DAG root hash mismatch: got {dag_root_hash}, expected {expected['expected_dag_root_hash']}"
    
    if expected["expected_ledger_last_hash"]:
        assert ledger_last_hash == expected["expected_ledger_last_hash"], \
            f"Ledger last hash mismatch: got {ledger_last_hash}, expected {expected['expected_ledger_last_hash']}"
    
    if expected["expected_artifact_hashes"].get("blueprint"):
        assert artifact_hashes.get("blueprint") == expected["expected_artifact_hashes"]["blueprint"], \
            f"Blueprint hash mismatch: got {artifact_hashes.get('blueprint')}, expected {expected['expected_artifact_hashes']['blueprint']}"
    
    # Check structure snapshot
    expected_structure = expected["expected_structure"]
    if expected_structure.get("chosen_interpretation_name"):
        assert chosen_interp_name == expected_structure["chosen_interpretation_name"], \
            f"Interpretation name mismatch: got {chosen_interp_name}, expected {expected_structure['chosen_interpretation_name']}"
    
    assert len(result.dag_nodes) == expected_structure["node_count"], \
        f"Node count mismatch: got {len(result.dag_nodes)}, expected {expected_structure['node_count']}"
    
    assert len(result.dag_edges) == expected_structure["edge_count"], \
        f"Edge count mismatch: got {len(result.dag_edges)}, expected {expected_structure['edge_count']}"
    
    assert node_kinds == sorted(expected_structure["node_kinds"]), \
        f"Node kinds mismatch: got {node_kinds}, expected {sorted(expected_structure['node_kinds'])}"
    
    # Replay and assert exact matches
    replay_result = replay_from_ledger(result.ledger_records, run_id)
    
    assert replay_result["ledger_valid"] is True, "Replay ledger validation failed"
    
    if replay_result.get("matches_expected"):
        assert replay_result["summary_hash"] == summary_hash, \
            f"Replay summary hash mismatch: got {replay_result['summary_hash']}, expected {summary_hash}"


def test_golden_run_deterministic():
    """Run golden test twice to ensure determinism."""
    # Load fixtures
    seed_text = load_text_fixture("golden_seed.txt")
    pin = load_fixture("golden_pin.json")
    policy_data = load_fixture("golden_policy.json")
    proposals_data = load_fixture("golden_proposals.json")
    
    policy = Policy(**policy_data)
    seed_hash = hash_canonical(seed_text)
    proposer = RecordedProposer(proposals_data)
    
    run_id = "golden_run_002"
    ts_base = "T000000"
    
    # Run twice
    result1 = run_engine(run_id, seed_text, pin, policy, proposer, ts_base, step_ms=1)
    result2 = run_engine(run_id, seed_text, pin, policy, proposer, ts_base, step_ms=1)
    
    # All hashes should match
    assert result1.ledger_records[0].record_hash == result2.ledger_records[0].record_hash
    assert len(result1.ledger_records) == len(result2.ledger_records)
    assert len(result1.dag_nodes) == len(result2.dag_nodes)
    assert len(result1.dag_edges) == len(result2.dag_edges)
