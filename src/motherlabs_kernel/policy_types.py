"""
Type definitions for policy configuration.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class Policy:
    """
    Policy configuration that governs exploration and convergence.
    
    Fields:
        max_interpretations: Maximum number of interpretations to consider (>= 1)
        max_nodes: Maximum number of nodes in DAG (>= 1)
        max_depth: Maximum exploration depth (>= 1)
        contradiction_budget: Maximum allowed contradictions (>= 0)
        max_steps: Maximum number of steps in engine run (>= 1)
        deterministic_tiebreak: Method for breaking ties (currently only 'lexicographic')
    
    Important: Changing scoring/collapse rules requires deliberate golden update
    and version bump, as it changes collapse outcomes and artifacts.
    """
    max_interpretations: int
    max_nodes: int
    max_depth: int
    contradiction_budget: int
    max_steps: int
    deterministic_tiebreak: Literal['lexicographic'] = 'lexicographic'
    
    def to_json(self) -> dict:
        """Convert to JSON-safe dict."""
        return {
            "max_interpretations": self.max_interpretations,
            "max_nodes": self.max_nodes,
            "max_depth": self.max_depth,
            "contradiction_budget": self.contradiction_budget,
            "max_steps": self.max_steps,
            "deterministic_tiebreak": self.deterministic_tiebreak
        }
