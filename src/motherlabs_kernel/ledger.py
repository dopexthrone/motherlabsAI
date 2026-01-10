"""
In-memory, append-only evidence ledger with tamper-evident hash chaining.
"""

from typing import Any, List, Optional

from .hash import hash_canonical
from .ledger_types import EvidenceRecord


class Ledger:
    """
    Append-only evidence ledger with hash chaining.
    
    The ledger maintains an immutable chain of evidence records, where each
    record's hash depends on the previous record's hash, creating a tamper-evident
    chain. Once appended, records cannot be modified.
    """
    
    def __init__(self):
        """Initialize an empty ledger."""
        self._records: List[EvidenceRecord] = []
    
    def append(self, ts: str, kind: str, payload: Any) -> EvidenceRecord:
        """
        Append a new evidence record to the ledger.
        
        Computes:
        - payload_hash: Hash of the canonicalized payload
        - parent: Hash of the previous record (None if this is the first record)
        - record_hash: Hash of the record metadata (v, ts, kind, parent, payload_hash)
        
        Args:
            ts: Timestamp token (deterministic ordering key, not wall-clock time)
            kind: Record kind (e.g., 'seedpack', 'proposal', 'commit', 'artifact')
            payload: JSON-safe payload data
            
        Returns:
            The newly created and appended EvidenceRecord
            
        Raises:
            TypeError: If payload is not JSON-safe
            ValueError: If payload contains NaN/Inf
        """
        # Compute payload hash
        payload_hash = hash_canonical(payload)
        
        # Get parent hash (previous record's record_hash)
        parent: Optional[str] = None
        if self._records:
            parent = self._records[-1].record_hash
        
        # Compute record hash from metadata only (not full payload)
        record_metadata = {
            "v": 1,
            "ts": ts,
            "kind": kind,
            "parent": parent,
            "payload_hash": payload_hash
        }
        record_hash = hash_canonical(record_metadata)
        
        # Create immutable record
        record = EvidenceRecord(
            v=1,
            ts=ts,
            kind=kind,
            parent=parent,
            payload=payload,
            payload_hash=payload_hash,
            record_hash=record_hash
        )
        
        # Append to ledger
        self._records.append(record)
        
        return record
    
    def get_records(self) -> List[EvidenceRecord]:
        """
        Get all records in the ledger (immutable copy).
        
        Returns:
            List of all evidence records in order
        """
        return self._records.copy()
    
    def get_last_hash(self) -> Optional[str]:
        """
        Get the hash of the last record in the ledger.
        
        Returns:
            record_hash of the last record, or None if ledger is empty
        """
        if not self._records:
            return None
        return self._records[-1].record_hash
    
    def __len__(self) -> int:
        """Return the number of records in the ledger."""
        return len(self._records)
