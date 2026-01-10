"""Tests for canonical JSON serialization."""

import pytest

from motherlabs_kernel.canonical import canonicalize
from motherlabs_kernel.hash import hash_canonical


def test_dict_key_order_invariance():
    """Same dict with different key order produces same canonical bytes."""
    dict1 = {"b": 2, "a": 1, "c": 3}
    dict2 = {"a": 1, "b": 2, "c": 3}
    dict3 = {"c": 3, "a": 1, "b": 2}
    
    bytes1 = canonicalize(dict1)
    bytes2 = canonicalize(dict2)
    bytes3 = canonicalize(dict3)
    
    assert bytes1 == bytes2 == bytes3
    assert bytes1 == b'{"a":1,"b":2,"c":3}'


def test_deterministic_bytes_output():
    """Canonical bytes are deterministic for same input."""
    value = {"x": [1, 2, 3], "y": {"nested": True}}
    bytes1 = canonicalize(value)
    bytes2 = canonicalize(value)
    
    assert bytes1 == bytes2


def test_arrays_preserve_order():
    """Arrays preserve order in canonical output."""
    value = [3, 1, 2]
    bytes_out = canonicalize(value)
    
    assert bytes_out == b'[3,1,2]'


def test_nested_structures():
    """Nested dicts and lists are canonicalized correctly."""
    value = {
        "outer": {
            "inner": [1, 2, {"deep": "value"}]
        }
    }
    bytes_out = canonicalize(value)
    
    # Should be sorted by key at each level
    assert b'"deep"' in bytes_out
    assert b'"inner"' in bytes_out
    assert b'"outer"' in bytes_out


def test_invalid_types_rejected():
    """Non-JSON-safe types raise TypeError."""
    with pytest.raises(TypeError):
        canonicalize(set([1, 2, 3]))
    
    with pytest.raises(TypeError):
        canonicalize(b"bytes")
    
    with pytest.raises(TypeError):
        canonicalize(bytearray(b"data"))


def test_dict_with_non_str_keys_rejected():
    """Dicts with non-string keys raise TypeError."""
    with pytest.raises(TypeError):
        canonicalize({1: "value"})
    
    with pytest.raises(TypeError):
        canonicalize({None: "value"})


def test_nan_rejected():
    """NaN floats raise ValueError."""
    import math
    with pytest.raises(ValueError, match="NaN"):
        canonicalize(float('nan'))


def test_inf_rejected():
    """Inf floats raise ValueError."""
    with pytest.raises(ValueError, match="Inf"):
        canonicalize(float('inf'))
    
    with pytest.raises(ValueError, match="Inf"):
        canonicalize(float('-inf'))


def test_none_allowed():
    """None is allowed in canonical JSON."""
    bytes_out = canonicalize(None)
    assert bytes_out == b'null'


def test_bool_allowed():
    """Booleans are allowed."""
    assert canonicalize(True) == b'true'
    assert canonicalize(False) == b'false'


def test_int_allowed():
    """Integers are allowed."""
    assert canonicalize(42) == b'42'
    assert canonicalize(-100) == b'-100'


def test_float_allowed():
    """Valid floats are allowed."""
    assert canonicalize(3.14) == b'3.14'
    assert canonicalize(-0.5) == b'-0.5'


def test_str_allowed():
    """Strings are allowed."""
    assert canonicalize("hello") == b'"hello"'
    assert canonicalize("") == b'""'


def test_tuple_treated_as_list():
    """Tuples are treated as lists."""
    assert canonicalize((1, 2, 3)) == canonicalize([1, 2, 3])


def test_hash_canonical_deterministic():
    """hash_canonical produces deterministic hashes."""
    value = {"a": 1, "b": 2}
    hash1 = hash_canonical(value)
    hash2 = hash_canonical(value)
    
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex is 64 chars
    assert hash1.islower()  # Should be lowercase


def test_hash_canonical_key_order_invariant():
    """hash_canonical is invariant to dict key order."""
    dict1 = {"b": 2, "a": 1}
    dict2 = {"a": 1, "b": 2}
    
    hash1 = hash_canonical(dict1)
    hash2 = hash_canonical(dict2)
    
    assert hash1 == hash2
