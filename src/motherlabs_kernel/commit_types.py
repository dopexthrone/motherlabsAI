"""
Type definitions for Commit (authoritative, deterministic).
"""

from dataclasses import dataclass
from typing import Any, Generic, Optional, TypeVar

from .hash import hash_canonical

T = TypeVar('T')


@dataclass(frozen=True, slots=True)
class Commit(Generic[T]):
    """
    An authoritative, committed value in the kernel.
    
    Commits are the ONLY authoritative state. They represent values that have
    been accepted by the kernel after validation. Proposals become commits only
    after passing kernel checks.
    
    Fields:
        value: The committed value (must be JSON-safe or contain objects with .to_json() method)
        accepted_from: Optional proposal_hash that this commit was accepted from
        commit_hash: Deterministic hash of the commit (value, accepted_from)
    
    Important: The value must be JSON-safe to ensure deterministic hashing.
    Objects with .to_json() method are automatically converted to JSON-safe dicts for hashing.
    """
    value: T
    accepted_from: Optional[str] = None
    commit_hash: str = ""
    
    @classmethod
    def create(cls, value: T, accepted_from: Optional[str] = None) -> 'Commit[T]':
        """
        Create a Commit with automatic hash computation.
        
        Hash is computed from the exact dict structure that .to_json() returns,
        but excluding commit_hash itself (to avoid circular dependency).
        
        Args:
            value: Committed value (must be JSON-safe or contain objects with .to_json() method)
            accepted_from: Optional proposal_hash this commit was accepted from
            
        Returns:
            Commit with computed commit_hash
            
        Raises:
            TypeError: If value is not JSON-safe
            ValueError: If value contains NaN/Inf
        """
        # Convert value to JSON-safe for hashing
        json_safe_value = cls._to_json_safe(value)
        
        # Build dict matching .to_json() structure (excluding commit_hash)
        # This ensures hash is computed from exact same dict that .to_json() returns
        hashable_dict = {
            "value": json_safe_value,
            "accepted_from": accepted_from  # Include None if None (matches pydantic)
            # Note: commit_hash is excluded from hash (it's the result)
        }
        
        # Compute hash from this dict (exact same structure as .to_json() minus commit_hash)
        commit_hash = hash_canonical(hashable_dict)
        
        return cls(
            value=value,  # Store original value (objects, not dicts)
            accepted_from=accepted_from,
            commit_hash=commit_hash
        )
    
    @staticmethod
    def _to_json_safe(value: Any) -> Any:
        """
        Convert value to JSON-safe primitives for hashing.
        
        Recursively converts objects with .to_json() method to dicts,
        and converts lists/tuples containing such objects.
        
        Rejects sets and unknown containers to ensure strict JSON-safety.
        
        Raises:
            TypeError: If value contains unsupported types (sets, unknown containers)
        """
        # If it has a .to_json() method, use it
        if hasattr(value, 'to_json') and callable(getattr(value, 'to_json', None)):
            return value.to_json()
        
        # Handle lists and tuples (preserve order)
        if isinstance(value, (list, tuple)):
            return [Commit._to_json_safe(item) for item in value]
        
        # Handle dicts (JSON-safe only: str keys)
        if isinstance(value, dict):
            for key in value.keys():
                if not isinstance(key, str):
                    raise TypeError(f"Dict keys must be strings, got {type(key).__name__}")
            return {k: Commit._to_json_safe(v) for k, v in value.items()}
        
        # Reject sets explicitly (not JSON-safe, no order)
        if isinstance(value, (set, frozenset)):
            raise TypeError(f"Sets are not JSON-safe: {type(value).__name__}")
        
        # Reject other containers (bytes, bytearray, etc.)
        if isinstance(value, (bytes, bytearray)):
            raise TypeError(f"Bytes are not JSON-safe: {type(value).__name__}")
        
        # JSON-safe primitives: None, bool, int, float, str
        if value is None or isinstance(value, (bool, int, str)):
            return value
        
        if isinstance(value, float):
            # Reject NaN/Inf
            if value != value:  # NaN check
                raise ValueError("NaN is not allowed in canonical JSON")
            if value == float('inf') or value == float('-inf'):
                raise ValueError("Inf is not allowed in canonical JSON")
            return value
        
        # Reject all other types
        raise TypeError(
            f"Type {type(value).__name__} is not JSON-safe. "
            "Allowed types: None, bool, int, float, str, list, tuple, dict(str->value), or objects with .to_json()"
        )
    
    def to_json(self) -> dict:
        """Convert to JSON-safe dict."""
        # Convert value to JSON-safe if needed
        json_safe_value = self._to_json_safe(self.value)
        
        return {
            "value": json_safe_value,
            "accepted_from": self.accepted_from,
            "commit_hash": self.commit_hash
        }
