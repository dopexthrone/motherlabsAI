"""
Type definitions for the evidence ledger.
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    """
    Evidence record v1 - immutable, hash-chained ledger entry.
    
    Fields:
        v: Version (currently 1)
        ts: Timestamp token (deterministic ordering key, not wall-clock time)
        kind: Record kind (e.g., 'seedpack', 'proposal', 'commit', 'artifact')
        parent: Hash of previous record (None for first record)
        payload: JSON-safe payload data
        payload_hash: SHA-256 hash of canonicalized payload
        record_hash: SHA-256 hash of canonicalized record metadata (v, ts, kind, parent, payload_hash)
    
    Important: record_hash does NOT include the full payload, only payload_hash.
    This ensures that record_hash is independent of payload size and can be computed
    without deserializing the full payload.
    """
    v: int = 1
    ts: str = ""
    kind: str = ""
    parent: Optional[str] = None
    payload: Any = None
    payload_hash: str = ""
    record_hash: str = ""
    
    def to_json(self) -> dict:
        """Convert to JSON-safe dict."""
        return {
            "v": self.v,
            "ts": self.ts,
            "kind": self.kind,
            "parent": self.parent,
            "payload": self.payload,  # Already JSON-safe
            "payload_hash": self.payload_hash,
            "record_hash": self.record_hash
        }
