"""
RefusalReport artifact definition.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True, slots=True)
class RefusalReport:
    """
    Refusal report when kernel cannot converge deterministically.
    
    The kernel must refuse rather than guess when it cannot achieve
    convergence within policy limits.
    """
    run_id: str
    seed_hash: str
    reason_codes: List[str]
    evidence_record_hashes: List[str]
    policy_suggestions: List[str]
    status: str = "refused"
    
    def to_json(self) -> dict:
        """Convert to JSON-safe dict."""
        return {
            "run_id": self.run_id,
            "seed_hash": self.seed_hash,
            "reason_codes": self.reason_codes,
            "evidence_record_hashes": self.evidence_record_hashes,
            "policy_suggestions": self.policy_suggestions,
            "status": self.status
        }
