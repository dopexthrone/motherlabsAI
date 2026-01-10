"""
Invariant checking for the DAG.
"""

from typing import Dict, List, Set

from .dag_types import Edge, EdgeKind, Node


class DAGInvariantError(Exception):
    """Raised when a DAG invariant is violated."""
    pass


def check_duplicate_node_ids(nodes: List[Node]) -> None:
    """
    Check for duplicate node IDs with differing content.
    
    Raises:
        DAGInvariantError: If duplicate IDs with different content are found
    """
    seen: Dict[str, Node] = {}
    for node in nodes:
        if node.id in seen:
            existing = seen[node.id]
            # Check if content differs
            if (existing.kind != node.kind or 
                existing.payload_hash != node.payload_hash):
                raise DAGInvariantError(
                    f"Duplicate node ID {node.id} with differing content: "
                    f"existing={existing.kind}/{existing.payload_hash}, "
                    f"new={node.kind}/{node.payload_hash}"
                )
        else:
            seen[node.id] = node


def check_edge_node_references(edges: List[Edge], node_ids: Set[str]) -> None:
    """
    Check that all edges reference existing nodes.
    
    Args:
        edges: List of edges to check
        node_ids: Set of valid node IDs
        
    Raises:
        DAGInvariantError: If an edge references a non-existent node
    """
    for edge in edges:
        if edge.from_id not in node_ids:
            raise DAGInvariantError(
                f"Edge {edge.id} references non-existent from node: {edge.from_id}"
            )
        if edge.to_id not in node_ids:
            raise DAGInvariantError(
                f"Edge {edge.id} references non-existent to node: {edge.to_id}"
            )


def check_self_contradiction_edges(edges: List[Edge]) -> None:
    """
    Check for self-contradiction edges (from == to for contradicts edges).
    
    Self-contradiction edges can be a cheap way to smuggle "conflict exists"
    without content. This check prevents them unless explicitly allowed.
    
    Args:
        edges: List of edges to check
        
    Raises:
        DAGInvariantError: If a contradicts edge has from == to
    """
    for edge in edges:
        if edge.kind == 'contradicts' and edge.from_id == edge.to_id:
            raise DAGInvariantError(
                f"Self-contradiction edge detected: {edge.id} "
                f"(from={edge.from_id}, to={edge.to_id})"
            )


def check_cycles(edges: List[Edge], node_ids: Set[str]) -> None:
    """
    Check for cycles in the DAG.
    
    Only checks cycles for 'depends_on' and 'refines' edges.
    'contradicts' edges are ignored for cycle detection, as they represent
    conflicts, not derivation dependencies.
    
    Uses DFS to detect cycles.
    
    Args:
        edges: List of edges to check
        node_ids: Set of valid node IDs
        
    Raises:
        DAGInvariantError: If a cycle is detected
    """
    # Build adjacency list for depends_on and refines edges only
    graph: Dict[str, List[str]] = {node_id: [] for node_id in node_ids}
    
    for edge in edges:
        if edge.kind in ('depends_on', 'refines'):
            if edge.from_id in graph and edge.to_id in graph:
                graph[edge.from_id].append(edge.to_id)
    
    # DFS to detect cycles
    visited: Set[str] = set()
    rec_stack: Set[str] = set()
    
    def has_cycle(node: str) -> bool:
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                # Found back edge = cycle
                return True
        
        rec_stack.remove(node)
        return False
    
    # Check all nodes
    for node_id in node_ids:
        if node_id not in visited:
            if has_cycle(node_id):
                raise DAGInvariantError(f"Cycle detected in DAG starting from node {node_id}")
