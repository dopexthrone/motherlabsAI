"""
Engine run reducer: seed → ledger → committed DAG → artifacts.

This is the main entry point that orchestrates the entire engine run.
"""

from typing import Any

from .ambiguity import resolve_ambiguity
from .artifacts_blueprint import BlueprintSpec
from .artifacts_refusal import RefusalReport
from .artifacts_verification import VerificationPack
from .dag import DAG
from .dag_types import Node
from .engine_types import RunResult
from .hash import hash_canonical
from .ledger import Ledger
from .policy_types import Policy
from .proposer_types import Proposer
from .refusal import check_refusal_conditions, generate_policy_suggestions


def generate_ts(ts_base: str, step: int) -> str:
    """
    Generate deterministic timestamp token.
    
    Uses format: ts_base#NNNN where NNNN is zero-padded step number.
    This is a deterministic ordering key, NOT a real timestamp.
    
    Args:
        ts_base: Base timestamp token (provided by caller)
        step: Step number (0-based)
        
    Returns:
        Deterministic timestamp token
    """
    return f"{ts_base}#{step:04d}"


def run_engine(
    run_id: str,
    seed_text: str,
    pin: dict,
    policy: Policy,
    proposer: Proposer,
    ts_base: str,
    step_ms: int = 1
) -> RunResult:
    """
    Run the engine: seed → ledger → committed DAG → artifacts.
    
    Process:
    1. Ledger record kind 'seedpack' with payload: {seed_text, seed_hash, pin, policy_summary}
    2. Ambiguity resolution:
       - Call proposer for interpretations (record kind 'proposal')
       - Select winner deterministically (record kind 'commit')
    3. Build DAG:
       - seed node
       - interpretation node
       - assumption nodes
       - edges: seed -> interpretation (refines), interpretation -> assumptions (depends_on)
       - Record kind 'commit' with payload describing committed node/edge IDs
    4. Emit artifacts (record kind 'artifact'):
       - BlueprintSpec
       - VerificationPack
    
    Args:
        run_id: Unique run identifier
        seed_text: Seed text input
        pin: Pinned target (JSON-safe dict)
        policy: Policy configuration
        proposer: Proposer for interpretations
        ts_base: Base timestamp token (deterministic ordering key, not wall-clock time)
        step_ms: Step increment (unused, kept for compatibility)
        
    Returns:
        RunResult with ledger records, DAG state, and artifacts
    """
    ledger = Ledger()
    dag = DAG(run_id=run_id)
    step = 0
    
    # Step 1: Record seedpack
    seed_hash = hash_canonical(seed_text)
    policy_summary = {
        "max_interpretations": policy.max_interpretations,
        "max_nodes": policy.max_nodes,
        "max_depth": policy.max_depth,
        "contradiction_budget": policy.contradiction_budget,
        "max_steps": policy.max_steps
    }
    seedpack_payload = {
        "seed_text": seed_text,
        "seed_hash": seed_hash,
        "pin": pin,
        "policy_summary": policy_summary
    }
    ledger.append(generate_ts(ts_base, step), "seedpack", seedpack_payload)
    step += 1
    
    # Step 2: Resolve ambiguity
    # Get interpretations proposal
    proposal = proposer.propose_interpretations(seed_hash, policy.max_interpretations)
    ledger.append(
        generate_ts(ts_base, step),
        "proposal",
        {"interpretations": [interp.to_json() for interp in proposal.value]}
    )
    step += 1
    
    # Check refusal conditions
    refusal_reasons = check_refusal_conditions(
        proposal, policy, step, len(dag.get_nodes()), proposal.value
    )
    
    if refusal_reasons:
        # Generate refusal report
        evidence_hashes = [r.record_hash for r in ledger.get_records()]
        policy_suggestions = generate_policy_suggestions(refusal_reasons)
        
        refusal = RefusalReport(
            run_id=run_id,
            seed_hash=seed_hash,
            reason_codes=refusal_reasons,
            evidence_record_hashes=evidence_hashes,
            policy_suggestions=policy_suggestions,
            status="refused"
        )
        
        # Record refusal artifact
        ledger.append(
            generate_ts(ts_base, step),
            "artifact",
            {"refusal": refusal.to_json()}
        )
        
        return RunResult(
            ledger_records=ledger.get_records(),
            dag_nodes=dag.get_nodes(),
            dag_edges=dag.get_edges(),
            artifacts={"refusal": refusal}
        )
    
    # Resolve ambiguity (selects winner)
    try:
        commit = resolve_ambiguity(run_id, seed_hash, policy, proposer)
    except ValueError:
        # If resolve_ambiguity fails, create refusal
        refusal_reasons = ["resolve_ambiguity_failed"]
        evidence_hashes = [r.record_hash for r in ledger.get_records()]
        policy_suggestions = generate_policy_suggestions(refusal_reasons)
        
        refusal = RefusalReport(
            run_id=run_id,
            seed_hash=seed_hash,
            reason_codes=refusal_reasons,
            evidence_record_hashes=evidence_hashes,
            policy_suggestions=policy_suggestions,
            status="refused"
        )
        
        ledger.append(
            generate_ts(ts_base, step),
            "artifact",
            {"refusal": refusal.to_json()}
        )
        
        return RunResult(
            ledger_records=ledger.get_records(),
            dag_nodes=dag.get_nodes(),
            dag_edges=dag.get_edges(),
            artifacts={"refusal": refusal}
        )
    
    ledger.append(
        generate_ts(ts_base, step),
        "commit",
        {"interpretation": commit.value.to_json(), "commit_hash": commit.commit_hash}
    )
    step += 1
    
    interpretation = commit.value
    
    # Step 3: Build DAG
    # Create seed node
    seed_node = dag.add_node("seed", {"seed_text": seed_text, "seed_hash": seed_hash})
    
    # Create interpretation node
    interp_node = dag.add_node(
        "interpretation",
        {"name": interpretation.name, "intent_summary": interpretation.intent_summary}
    )
    dag.add_edge("refines", seed_node.id, interp_node.id)
    
    # Create assumption nodes
    assumption_nodes = []
    for assumption in interpretation.assumptions:
        assumpt_node = dag.add_node("assumption", {"assumption": assumption})
        assumption_nodes.append(assumpt_node)
        dag.add_edge("depends_on", interp_node.id, assumpt_node.id)
    
    # Record committed DAG state
    dag_commit_payload = {
        "nodes": [{"id": n.id, "kind": n.kind} for n in dag.get_nodes()],
        "edges": [{"id": e.id, "kind": e.kind, "from": e.from_id, "to": e.to_id} for e in dag.get_edges()]
    }
    ledger.append(generate_ts(ts_base, step), "commit", dag_commit_payload)
    step += 1
    
    # Step 4: Emit artifacts
    # Compute DAG root hash
    node_ids = sorted([n.id for n in dag.get_nodes()])
    edge_ids = sorted([e.id for e in dag.get_edges()])
    dag_root_hash = hash_canonical({"node_ids": node_ids, "edge_ids": edge_ids})
    
    # Create BlueprintSpec
    blueprint = BlueprintSpec(
        run_id=run_id,
        seed_hash=seed_hash,
        intent_root_node_id=interp_node.id,
        pinned_target=pin,
        invariants=["no_cycles", "all_edges_reference_nodes", "deterministic_ids"],
        module_contracts=[]  # Stub for now
    )
    blueprint_hash = blueprint.compute_hash()
    
    # Create VerificationPack
    artifact_hashes = {"blueprint": blueprint_hash}
    # Compute summary hash first
    summary_data = {
        "ledger_last_hash": ledger.get_last_hash() or "",
        "dag_root_hash": dag_root_hash,
        "artifact_hashes": artifact_hashes
    }
    summary_hash = hash_canonical(summary_data)
    
    verification = VerificationPack(
        ledger_last_hash=ledger.get_last_hash() or "",
        dag_root_hash=dag_root_hash,
        artifact_hashes=artifact_hashes,
        expected_summary_hash=summary_hash,
        replay_instructions="Replay by validating ledger chain and rebuilding DAG from records"
    )
    
    # Record artifacts
    artifacts_payload = {
        "blueprint": blueprint.to_json(),
        "verification": verification.to_json()
    }
    ledger.append(generate_ts(ts_base, step), "artifact", artifacts_payload)
    
    return RunResult(
        ledger_records=ledger.get_records(),
        dag_nodes=dag.get_nodes(),
        dag_edges=dag.get_edges(),
        artifacts={"blueprint": blueprint, "verification": verification}
    )
