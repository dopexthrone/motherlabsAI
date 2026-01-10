"""Tests for the evidence ledger."""

from motherlabs_kernel.ledger import Ledger
from motherlabs_kernel.ledger_types import EvidenceRecord
from motherlabs_kernel.ledger_validate import validate_chain
from motherlabs_kernel.hash import hash_canonical


def test_ledger_append_first_record():
    """Appending first record creates correct hash chain."""
    ledger = Ledger()
    record = ledger.append("T000001", "seedpack", {"seed": "test"})
    
    assert record.v == 1
    assert record.ts == "T000001"
    assert record.kind == "seedpack"
    assert record.parent is None
    assert record.payload == {"seed": "test"}
    assert record.payload_hash == hash_canonical({"seed": "test"})
    assert len(ledger) == 1


def test_ledger_append_chains_correctly():
    """Appending multiple records creates correct parent linkage."""
    ledger = Ledger()
    
    record1 = ledger.append("T000001", "seedpack", {"seed": "test1"})
    record2 = ledger.append("T000002", "proposal", {"proposal": "data"})
    record3 = ledger.append("T000003", "commit", {"commit": "value"})
    
    assert record1.parent is None
    assert record2.parent == record1.record_hash
    assert record3.parent == record2.record_hash
    
    assert len(ledger) == 3


def test_ledger_record_hash_independent_of_payload():
    """record_hash does not depend on full payload, only payload_hash."""
    ledger = Ledger()
    
    # Same payload should produce same payload_hash
    payload = {"data": "value"}
    payload_hash = hash_canonical(payload)
    
    record1 = ledger.append("T000001", "test", payload)
    
    # record_hash should be computed from metadata only
    record_metadata = {
        "v": 1,
        "ts": "T000001",
        "kind": "test",
        "parent": None,
        "payload_hash": payload_hash
    }
    expected_record_hash = hash_canonical(record_metadata)
    
    assert record1.record_hash == expected_record_hash
    assert record1.payload_hash == payload_hash


def test_ledger_get_last_hash():
    """get_last_hash returns the last record's hash."""
    ledger = Ledger()
    
    assert ledger.get_last_hash() is None
    
    record1 = ledger.append("T000001", "test1", {"a": 1})
    assert ledger.get_last_hash() == record1.record_hash
    
    record2 = ledger.append("T000002", "test2", {"b": 2})
    assert ledger.get_last_hash() == record2.record_hash


def test_validate_chain_correct_linkage():
    """validate_chain returns True for valid chain."""
    ledger = Ledger()
    ledger.append("T000001", "seedpack", {"seed": "test1"})
    ledger.append("T000002", "proposal", {"proposal": "data"})
    ledger.append("T000003", "commit", {"commit": "value"})
    
    records = ledger.get_records()
    assert validate_chain(records) is True


def test_validate_chain_empty():
    """validate_chain returns True for empty chain."""
    assert validate_chain([]) is True


def test_validate_chain_mutation_breaks_validation():
    """Mutating a record breaks chain validation."""
    ledger = Ledger()
    ledger.append("T000001", "seedpack", {"seed": "test1"})
    ledger.append("T000002", "proposal", {"proposal": "data"})
    
    records = ledger.get_records()
    assert validate_chain(records) is True
    
    # Mutate a payload (this would break the chain in real usage)
    # We can't directly mutate a Pydantic model, but we can create a new one with wrong hash
    mutated_record = EvidenceRecord(
        v=records[0].v,
        ts=records[0].ts,
        kind=records[0].kind,
        parent=records[0].parent,
        payload={"seed": "MUTATED"},  # Changed payload
        payload_hash=records[0].payload_hash,  # But kept old hash (invalid)
        record_hash=records[0].record_hash  # And kept old record_hash (invalid)
    )
    
    mutated_records = [mutated_record] + records[1:]
    assert validate_chain(mutated_records) is False


def test_validate_chain_wrong_parent_linkage():
    """Wrong parent linkage breaks validation."""
    ledger = Ledger()
    record1 = ledger.append("T000001", "seedpack", {"seed": "test1"})
    record2 = ledger.append("T000002", "proposal", {"proposal": "data"})
    
    records = ledger.get_records()
    assert validate_chain(records) is True
    
    # Create record with wrong parent
    wrong_parent_record = EvidenceRecord(
        v=record2.v,
        ts=record2.ts,
        kind=record2.kind,
        parent="wrong_parent_hash",  # Wrong parent
        payload=record2.payload,
        payload_hash=record2.payload_hash,
        record_hash=record2.record_hash
    )
    
    wrong_records = [record1, wrong_parent_record]
    assert validate_chain(wrong_records) is False


def test_ledger_determinism_fixed_ts_payload():
    """Ledger produces deterministic hashes given fixed ts and payload."""
    ledger1 = Ledger()
    record1 = ledger1.append("T000001", "test", {"data": "value"})
    
    ledger2 = Ledger()
    record2 = ledger2.append("T000001", "test", {"data": "value"})
    
    # Same inputs should produce same hashes
    assert record1.payload_hash == record2.payload_hash
    assert record1.record_hash == record2.record_hash


def test_ledger_determinism_chain():
    """Full chain is deterministic given fixed sequence of inputs."""
    ledger1 = Ledger()
    ledger1.append("T000001", "seedpack", {"seed": "test1"})
    ledger1.append("T000002", "proposal", {"proposal": "data"})
    ledger1.append("T000003", "commit", {"commit": "value"})
    
    ledger2 = Ledger()
    ledger2.append("T000001", "seedpack", {"seed": "test1"})
    ledger2.append("T000002", "proposal", {"proposal": "data"})
    ledger2.append("T000003", "commit", {"commit": "value"})
    
    records1 = ledger1.get_records()
    records2 = ledger2.get_records()
    
    # All hashes should match
    for r1, r2 in zip(records1, records2):
        assert r1.payload_hash == r2.payload_hash
        assert r1.record_hash == r2.record_hash
        assert r1.parent == r2.parent
    
    # Both chains should validate
    assert validate_chain(records1) is True
    assert validate_chain(records2) is True
