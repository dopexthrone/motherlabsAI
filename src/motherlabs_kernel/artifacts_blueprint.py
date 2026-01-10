"""
BlueprintSpec artifact definition.
"""

from dataclasses import dataclass, field
from typing import Any, List

from .hash import hash_canonical


@dataclass(frozen=True, slots=True)
class BlueprintSpec:
    """
    Blueprint specification artifact.
    
    This is the primary output artifact when the engine successfully
    converges. It contains all information needed to build the system.
    """
    run_id: str
    seed_hash: str
    intent_root_node_id: str
    pinned_target: dict
    invariants: List[str]
    module_contracts: List[dict] = field(default_factory=list)
    
    def compute_hash(self) -> str:
        """Compute hash of this blueprint spec."""
        return hash_canonical(self.to_json())
    
    def to_json(self) -> dict:
        """Convert to JSON-safe dict."""
        return {
            "run_id": self.run_id,
            "seed_hash": self.seed_hash,
            "intent_root_node_id": self.intent_root_node_id,
            "pinned_target": self.pinned_target,  # Already JSON-safe
            "invariants": self.invariants,
            "module_contracts": self.module_contracts  # Already JSON-safe
        }
