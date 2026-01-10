"""
Canonical JSON serialization for absolute determinism.

This module provides canonical serialization that ensures identical inputs
produce identical byte outputs, regardless of dict key order or other
non-deterministic factors.
"""

import json
from typing import Any


def canonicalize(value: Any) -> bytes:
    """
    Convert a JSON-safe value to canonical JSON bytes.
    
    Canonical JSON rules:
    - dict keys sorted lexicographically
    - no whitespace (separators=(',', ':'))
    - arrays preserve order
    - only JSON-safe types allowed: None, bool, int, float (but reject NaN/Inf), str, list/tuple, dict(str->value)
    - reject: set, bytes, bytearray, datetime, Decimal, UUID, custom objects, dict with non-str keys, None keys
    
    Args:
        value: JSON-safe value to canonicalize
        
    Returns:
        UTF-8 encoded bytes of canonical JSON
        
    Raises:
        TypeError: If value contains non-JSON-safe types
        ValueError: If value contains NaN or Inf floats
    """
    _validate_json_safe(value)
    # Use separators=(',', ':') to remove all whitespace
    # sort_keys=True ensures dict keys are sorted lexicographically
    json_str = json.dumps(
        value,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False
    )
    return json_str.encode('utf-8')


def _validate_json_safe(value: Any) -> None:
    """
    Recursively validate that value is JSON-safe.
    
    Raises:
        TypeError: If value contains non-JSON-safe types
        ValueError: If value contains NaN or Inf floats
    """
    if value is None:
        return
    if isinstance(value, bool):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        # Reject NaN and Inf
        if not (value == value):  # NaN check
            raise ValueError("NaN is not allowed in canonical JSON")
        if value == float('inf') or value == float('-inf'):
            raise ValueError("Inf is not allowed in canonical JSON")
        return
    if isinstance(value, str):
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _validate_json_safe(item)
        return
    if isinstance(value, dict):
        for key, val in value.items():
            if not isinstance(key, str):
                raise TypeError(f"Dict keys must be strings, got {type(key).__name__}")
            if key is None:
                raise TypeError("Dict keys cannot be None")
            _validate_json_safe(val)
        return
    
    # Reject all other types
    raise TypeError(
        f"Type {type(value).__name__} is not JSON-safe. "
        "Allowed types: None, bool, int, float, str, list, tuple, dict(str->value)"
    )
