"""
Type definitions for Proposal (probabilistic, non-authoritative).
"""

from dataclasses import dataclass
from typing import Any, Generic, Literal, Optional, TypeVar

from .hash import hash_canonical

T = TypeVar('T')


@dataclass(frozen=True, slots=True)
class Proposal(Generic[T]):
    """
    A probabilistic proposal from an external source (LLM, retrieval, heuristic).
    
    Proposals are NEVER authoritative. They represent suggestions that may
    be accepted or rejected by the kernel. Only committed state is authoritative.
    
    Fields:
        source: Source of the proposal ('llm', 'retrieval', 'heuristic')
        confidence: Optional confidence score (float or None)
        value: The proposed value (must be JSON-safe)
        proposal_hash: Deterministic hash of the proposal (source, confidence, value)
    
    Important: The value must be JSON-safe (no NaN, no datetimes, etc.) to ensure
    deterministic hashing. Proposal hashing uses canonicalization so two equivalent
    proposals hash identically. Objects with .to_json() method are automatically
    converted to JSON-safe dicts for hashing.
    """
    source: Literal['llm', 'retrieval', 'heuristic']
    confidence: Optional[float] = None
    value: T = None
    proposal_hash: str = ""
    
    @classmethod
    def create(cls, source: Literal['llm', 'retrieval', 'heuristic'], 
               value: T, confidence: Optional[float] = None) -> 'Proposal[T]':
        """
        Create a Proposal with automatic hash computation.
        
        Hash is computed from the exact dict structure that .to_json() returns,
        but excluding proposal_hash itself (to avoid circular dependency).
        
        Args:
            source: Source of the proposal
            value: Proposed value (must be JSON-safe or contain objects with .to_json() method)
            confidence: Optional confidence score
            
        Returns:
            Proposal with computed proposal_hash
            
        Raises:
            TypeError: If value is not JSON-safe
            ValueError: If value contains NaN/Inf
        """
        # Convert value to JSON-safe for hashing
        json_safe_value = cls._to_json_safe(value)
        
        # Build dict matching .to_json() structure (excluding proposal_hash)
        # This ensures hash is computed from exact same dict that .to_json() returns
        hashable_dict = {
            "source": source,
            "confidence": confidence,  # Include None if None (matches pydantic)
            "value": json_safe_value
            # Note: proposal_hash is excluded from hash (it's the result)
        }
        
        # Compute hash from this dict (exact same structure as .to_json() minus proposal_hash)
        proposal_hash = hash_canonical(hashable_dict)
        
        return cls(
            source=source,
            confidence=confidence,
            value=value,  # Store original value (objects, not dicts)
            proposal_hash=proposal_hash
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
            return [Proposal._to_json_safe(item) for item in value]
        
        # Handle dicts (JSON-safe only: str keys)
        if isinstance(value, dict):
            for key in value.keys():
                if not isinstance(key, str):
                    raise TypeError(f"Dict keys must be strings, got {type(key).__name__}")
            return {k: Proposal._to_json_safe(v) for k, v in value.items()}
        
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
            "source": self.source,
            "confidence": self.confidence,
            "value": json_safe_value,
            "proposal_hash": self.proposal_hash
        }
