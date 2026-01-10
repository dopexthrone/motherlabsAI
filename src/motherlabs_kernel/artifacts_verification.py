"""
VerificationPack artifact definition.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

from .hash import hash_canonical


@dataclass(frozen=True, slots=True)
class VerificationPack:
    """
    Verification pack that proves the integrity of the run.
    
    Contains hashes and metadata that enable replay and verification.
    """
    ledger_last_hash: str
    dag_root_hash: str
    artifact_hashes: Dict[str, str]
    expected_summary_hash: str
    replay_instructions: str
    
    def compute_summary_hash(self) -> str:
        """
        Compute summary hash from ledger, DAG, and artifacts.
        
        summary_hash = hash_canonical({
            ledger_last_hash,
            dag_root_hash,
            artifact_hashes
        })
        """
        summary_data = {
            "ledger_last_hash": self.ledger_last_hash,
            "dag_root_hash": self.dag_root_hash,
            "artifact_hashes": self.artifact_hashes
        }
        return hash_canonical(summary_data)
    
    def to_json(self) -> dict:
        """Convert to JSON-safe dict."""
        return {
            "ledger_last_hash": self.ledger_last_hash,
            "dag_root_hash": self.dag_root_hash,
            "artifact_hashes": self.artifact_hashes,
            "expected_summary_hash": self.expected_summary_hash,
            "replay_instructions": self.replay_instructions
        }
