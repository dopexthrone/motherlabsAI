"""
Validation functions for the evidence ledger.
"""

from typing import List

from .hash import hash_canonical
from .ledger_types import EvidenceRecord


def validate_chain(records: List[EvidenceRecord]) -> bool:
    """
    Validate the hash chain of evidence records.
    
    For each record, recomputes:
    - payload_hash from the payload
    - record_hash from the record metadata (v, ts, kind, parent, payload_hash)
    
    Then checks:
    - All payload_hashes match
    - All record_hashes match
    - Parent linkage is correct (each record's parent matches previous record's record_hash)
    
    Args:
        records: List of evidence records to validate
        
    Returns:
        True if chain is valid, False otherwise
    """
    if not records:
        return True  # Empty chain is valid
    
    for i, record in enumerate(records):
        # Recompute payload hash
        computed_payload_hash = hash_canonical(record.payload)
        if computed_payload_hash != record.payload_hash:
            return False
        
        # Determine expected parent
        expected_parent: str | None = None
        if i > 0:
            expected_parent = records[i - 1].record_hash
        
        # Check parent linkage
        if record.parent != expected_parent:
            return False
        
        # Recompute record hash from metadata
        record_metadata = {
            "v": record.v,
            "ts": record.ts,
            "kind": record.kind,
            "parent": record.parent,
            "payload_hash": record.payload_hash
        }
        computed_record_hash = hash_canonical(record_metadata)
        
        if computed_record_hash != record.record_hash:
            return False
    
    return True
