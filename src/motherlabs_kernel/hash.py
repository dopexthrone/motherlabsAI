"""
SHA-256 hashing for deterministic hash computation.
"""

import hashlib
from typing import Any, Union

from .canonical import canonicalize


def sha256_hex(data: Union[bytes, str]) -> str:
    """
    Compute SHA-256 hash and return as lowercase hex string.
    
    Args:
        data: Bytes or string to hash. Strings are encoded as UTF-8.
        
    Returns:
        Lowercase hexadecimal string of SHA-256 hash
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest().lower()


def hash_canonical(value: Any) -> str:
    """
    Canonicalize a value and return its SHA-256 hash.
    
    This is the primary hash function for the kernel. It ensures that
    equivalent values (same structure, same data) always produce the
    same hash, regardless of dict key order or other non-deterministic
    factors.
    
    Args:
        value: JSON-safe value to hash
        
    Returns:
        Lowercase hexadecimal string of SHA-256 hash of canonical JSON
        
    Raises:
        TypeError: If value contains non-JSON-safe types
        ValueError: If value contains NaN or Inf floats
    """
    canonical_bytes = canonicalize(value)
    return sha256_hex(canonical_bytes)
