"""
Type definitions for the DAG (Directed Acyclic Graph).
"""

from dataclasses import dataclass
from typing import Any, Literal


NodeKind = Literal['seed', 'interpretation', 'assumption', 'claim', 'decision', 'artifact']
EdgeKind = Literal['depends_on', 'refines', 'contradicts']


@dataclass(frozen=True, slots=True)
class Node:
    """
    A node in the DAG.
    
    Fields:
        id: Deterministic SHA-256 hex hash (domain-separated)
        kind: Node kind (seed, interpretation, assumption, claim, decision, artifact)
        payload: JSON-safe payload data
        payload_hash: SHA-256 hash of canonicalized payload
    """
    id: str
    kind: NodeKind
    payload: Any
    payload_hash: str
    
    def to_json(self) -> dict:
        """Convert to JSON-safe dict."""
        return {
            "id": self.id,
            "kind": self.kind,
            "payload": self.payload,  # Already JSON-safe
            "payload_hash": self.payload_hash
        }


@dataclass(frozen=True, slots=True)
class Edge:
    """
    An edge in the DAG.
    
    Fields:
        id: Deterministic SHA-256 hex hash (domain-separated)
        kind: Edge kind (depends_on, refines, contradicts)
        from_id: Source node ID
        to_id: Target node ID
    """
    id: str
    kind: EdgeKind
    from_id: str
    to_id: str
    
    def to_json(self) -> dict:
        """Convert to JSON-safe dict."""
        return {
            "id": self.id,
            "kind": self.kind,
            "from_id": self.from_id,
            "to_id": self.to_id
        }
