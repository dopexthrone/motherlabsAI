"""
Authoritative DAG with deterministic IDs and invariants.
"""

from typing import Any, Dict, List, Optional, Set

from .dag_ids import edge_id, node_id
from .dag_invariants import (
    DAGInvariantError,
    check_cycles,
    check_duplicate_node_ids,
    check_edge_node_references,
    check_self_contradiction_edges,
)
from .dag_types import Edge, EdgeKind, Node, NodeKind
from .hash import hash_canonical


class DAG:
    """
    Authoritative DAG with deterministic IDs and invariant enforcement.
    
    The DAG maintains nodes and edges with deterministic IDs computed
    from their content. All invariants are enforced:
    - No duplicate node IDs with differing content
    - All edges reference existing nodes
    - No cycles for depends_on/refines edges
    - No self-contradiction edges
    """
    
    def __init__(self, run_id: str):
        """
        Initialize DAG with a run ID.
        
        Args:
            run_id: Unique run identifier for deterministic ID generation
        """
        self.run_id = run_id
        self._nodes: Dict[str, Node] = {}
        self._edges: Dict[str, Edge] = {}
    
    def add_node(self, kind: NodeKind, payload: Any) -> Node:
        """
        Add a node to the DAG.
        
        Computes deterministic node ID from run_id, kind, and payload_hash.
        Rejects duplicate IDs with differing content.
        
        Args:
            kind: Node kind
            payload: JSON-safe payload data
            
        Returns:
            The created Node
            
        Raises:
            DAGInvariantError: If duplicate ID with differing content
            TypeError: If payload is not JSON-safe
            ValueError: If payload contains NaN/Inf
        """
        payload_hash = hash_canonical(payload)
        node_id_val = node_id(self.run_id, kind, payload_hash)
        
        # Check for duplicate with different content
        if node_id_val in self._nodes:
            existing = self._nodes[node_id_val]
            if existing.kind != kind or existing.payload_hash != payload_hash:
                raise DAGInvariantError(
                    f"Duplicate node ID {node_id_val} with differing content"
                )
            # Same content, return existing
            return existing
        
        # Create new node
        node = Node(
            id=node_id_val,
            kind=kind,
            payload=payload,
            payload_hash=payload_hash
        )
        self._nodes[node_id_val] = node
        
        return node
    
    def add_edge(self, kind: EdgeKind, from_id: str, to_id: str) -> Edge:
        """
        Add an edge to the DAG.
        
        Computes deterministic edge ID from run_id, kind, from_id, and to_id.
        Validates that both nodes exist.
        
        Args:
            kind: Edge kind
            from_id: Source node ID
            to_id: Target node ID
            
        Returns:
            The created Edge
            
        Raises:
            DAGInvariantError: If nodes don't exist, cycle detected, or self-contradiction
        """
        # Check nodes exist
        if from_id not in self._nodes:
            raise DAGInvariantError(f"Source node {from_id} does not exist")
        if to_id not in self._nodes:
            raise DAGInvariantError(f"Target node {to_id} does not exist")
        
        edge_id_val = edge_id(self.run_id, kind, from_id, to_id)
        
        # Check for duplicate (same ID = same edge, allowed)
        if edge_id_val in self._edges:
            return self._edges[edge_id_val]
        
        # Create new edge
        edge = Edge(
            id=edge_id_val,
            kind=kind,
            from_id=from_id,
            to_id=to_id
        )
        self._edges[edge_id_val] = edge
        
        # Check invariants after adding edge
        self._check_invariants()
        
        return edge
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID."""
        return self._nodes.get(node_id)
    
    def get_edge(self, edge_id: str) -> Optional[Edge]:
        """Get an edge by ID."""
        return self._edges.get(edge_id)
    
    def get_nodes(self) -> List[Node]:
        """Get all nodes (immutable copy)."""
        return list(self._nodes.values())
    
    def get_edges(self) -> List[Edge]:
        """Get all edges (immutable copy)."""
        return list(self._edges.values())
    
    def get_node_ids(self) -> Set[str]:
        """Get set of all node IDs."""
        return set(self._nodes.keys())
    
    def _check_invariants(self) -> None:
        """
        Check all DAG invariants.
        
        Raises:
            DAGInvariantError: If any invariant is violated
        """
        nodes = self.get_nodes()
        edges = self.get_edges()
        node_ids_set = self.get_node_ids()
        
        check_duplicate_node_ids(nodes)
        check_edge_node_references(edges, node_ids_set)
        check_self_contradiction_edges(edges)
        check_cycles(edges, node_ids_set)
