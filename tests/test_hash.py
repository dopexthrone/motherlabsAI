"""Tests for SHA-256 hashing functions."""

from motherlabs_kernel.hash import sha256_hex, hash_canonical


def test_sha256_hex_bytes():
    """sha256_hex works with bytes input."""
    data = b"hello world"
    result = sha256_hex(data)
    
    assert isinstance(result, str)
    assert len(result) == 64  # SHA-256 hex is 64 chars
    assert result.islower()
    # Known SHA-256 hash of "hello world"
    assert result == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"


def test_sha256_hex_string():
    """sha256_hex works with string input (UTF-8 encoded)."""
    data = "hello world"
    result = sha256_hex(data)
    
    assert isinstance(result, str)
    assert len(result) == 64
    assert result.islower()
    # Should match bytes version
    assert result == sha256_hex(b"hello world")


def test_sha256_hex_deterministic():
    """sha256_hex produces deterministic results."""
    data = "test data"
    result1 = sha256_hex(data)
    result2 = sha256_hex(data)
    
    assert result1 == result2


def test_hash_canonical_simple():
    """hash_canonical works with simple values."""
    result = hash_canonical("hello")
    assert isinstance(result, str)
    assert len(result) == 64
    assert result.islower()


def test_hash_canonical_complex():
    """hash_canonical works with complex nested structures."""
    value = {
        "nested": {
            "list": [1, 2, 3],
            "bool": True,
            "null": None
        }
    }
    result = hash_canonical(value)
    assert isinstance(result, str)
    assert len(result) == 64
    assert result.islower()


def test_hash_canonical_key_order_invariant():
    """hash_canonical is invariant to dict key order."""
    dict1 = {"z": 3, "a": 1, "m": 2}
    dict2 = {"a": 1, "m": 2, "z": 3}
    
    hash1 = hash_canonical(dict1)
    hash2 = hash_canonical(dict2)
    
    assert hash1 == hash2
