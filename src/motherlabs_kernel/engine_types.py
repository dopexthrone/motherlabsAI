"""
Type definitions for engine run.
"""

from typing import Any, List

from .ledger_types import EvidenceRecord


class RunResult:
    """
    Result of an engine run.
    
    Contains:
        - ledger_records: List of evidence records
        - dag_state: Committed DAG state (nodes and edges)
        - artifacts: BlueprintSpec + VerificationPack OR RefusalReport
    """
    
    def __init__(
        self,
        ledger_records: List[EvidenceRecord],
        dag_nodes: List[Any],  # Will be Node from dag_types
        dag_edges: List[Any],  # Will be Edge from dag_types
        artifacts: Any  # Will be BlueprintSpec or RefusalReport
    ):
        self.ledger_records = ledger_records
        self.dag_nodes = dag_nodes
        self.dag_edges = dag_edges
        self.artifacts = artifacts
