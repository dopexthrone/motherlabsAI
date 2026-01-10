"""
Deterministic ID generation for DAG nodes and edges.
"""

from .dag_types import Edge, EdgeKind, Node, NodeKind
from .hash import hash_canonical


def node_id(run_id: str, kind: NodeKind, payload_hash: str) -> str:
    """
    Generate deterministic node ID using domain-separated hashing.
    
    The ID is computed as:
    sha256_hex(canonicalize({
        't': 'node',
        'run_id': run_id,
        'kind': kind,
        'payload_hash': payload_hash
    }))
    
    This ensures:
    - Same run_id + kind + payload_hash always produces same ID
    - IDs are stable regardless of insertion order
    - Domain separation prevents ID collisions with edges
    
    Args:
        run_id: Unique run identifier
        kind: Node kind
        payload_hash: Hash of the node's payload
        
    Returns:
        Deterministic SHA-256 hex node ID
    """
    domain_data = {
        't': 'node',
        'run_id': run_id,
        'kind': kind,
        'payload_hash': payload_hash
    }
    return hash_canonical(domain_data)


def edge_id(run_id: str, kind: EdgeKind, from_id: str, to_id: str) -> str:
    """
    Generate deterministic edge ID using domain-separated hashing.
    
    The ID is computed as:
    sha256_hex(canonicalize({
        't': 'edge',
        'run_id': run_id,
        'kind': kind,
        'from': from_id,
        'to': to_id
    }))
    
    This ensures:
    - Same run_id + kind + from_id + to_id always produces same ID
    - IDs are stable regardless of insertion order
    - Domain separation prevents ID collisions with nodes
    
    Args:
        run_id: Unique run identifier
        kind: Edge kind
        from_id: Source node ID
        to_id: Target node ID
        
    Returns:
        Deterministic SHA-256 hex edge ID
    """
    domain_data = {
        't': 'edge',
        'run_id': run_id,
        'kind': kind,
        'from': from_id,
        'to': to_id
    }
    return hash_canonical(domain_data)
