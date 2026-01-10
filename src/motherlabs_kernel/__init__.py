"""
Motherlabs Kernel - Engine-only, deterministic context engineering system.

This package provides a pure, in-memory engine with no filesystem IO,
no network calls, and no system clock dependencies. All functions are
deterministic given fixed inputs.

Key Principles:
- Timestamps are ordering tokens, not wall-clock time
- Any scoring/collapse rule change requires deliberate golden update and version bump
- LLM proposals are never authoritative; only committed state is
- Kernel refuses when it cannot converge deterministically
"""

__version__ = "0.1.0"  # FROZEN - See KERNEL_FREEZE.md

from .ambiguity import Proposer, resolve_ambiguity
from .ambiguity_types import Interpretation
from .artifacts_blueprint import BlueprintSpec
from .artifacts_refusal import RefusalReport
from .artifacts_verification import VerificationPack
from .canonical import canonicalize
from .commit_types import Commit
from .dag import DAG
from .dag_ids import edge_id, node_id
from .dag_invariants import DAGInvariantError
from .dag_types import Edge, EdgeKind, Node, NodeKind
from .engine_types import RunResult
from .hash import hash_canonical, sha256_hex
from .ledger import Ledger
from .ledger_types import EvidenceRecord
from .ledger_validate import validate_chain
from .policy import tie_break, validate_policy
from .policy_types import Policy
from .proposer_null import NullProposer
from .proposer_recorded import RecordedProposer
from .proposer_types import Proposer as ProposerProtocol
from .proposal_types import Proposal
from .replay import replay_from_ledger
from .run_engine import run_engine

__all__ = [
    "canonicalize",
    "hash_canonical",
    "sha256_hex",
    "Ledger",
    "EvidenceRecord",
    "validate_chain",
    "Policy",
    "validate_policy",
    "tie_break",
    "DAG",
    "Node",
    "Edge",
    "NodeKind",
    "EdgeKind",
    "node_id",
    "edge_id",
    "DAGInvariantError",
    "Proposal",
    "Commit",
    "Interpretation",
    "Proposer",
    "ProposerProtocol",
    "RecordedProposer",
    "NullProposer",
    "resolve_ambiguity",
    "run_engine",
    "replay_from_ledger",
    "RunResult",
    "BlueprintSpec",
    "VerificationPack",
    "RefusalReport",
]
