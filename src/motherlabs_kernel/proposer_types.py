"""
Type definitions for proposers.
"""

from typing import Protocol

from .ambiguity_types import Interpretation
from .proposal_types import Proposal


class Proposer(Protocol):
    """
    Protocol for proposers that generate interpretations.
    
    This is the interface that all proposers must implement.
    """
    
    def propose_interpretations(self, seed_hash: str, n: int) -> Proposal[list[Interpretation]]:
        """
        Propose interpretations for a given seed.
        
        Args:
            seed_hash: Hash of the seed text
            n: Number of interpretations to propose
            
        Returns:
            Proposal containing list of interpretations
        """
        ...
