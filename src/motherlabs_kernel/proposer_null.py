"""
NullProposer - Proposer that returns empty proposals.

Used for testing refusal paths and edge cases.
"""

from .ambiguity_types import Interpretation
from .proposal_types import Proposal


class NullProposer:
    """
    Proposer that always returns an empty list of interpretations.
    
    Used for testing refusal behavior when proposer returns no interpretations.
    """
    
    def propose_interpretations(self, seed_hash: str, n: int) -> Proposal[list[Interpretation]]:
        """
        Return empty proposal.
        
        Args:
            seed_hash: Hash of the seed text (ignored)
            n: Number of interpretations to propose (ignored)
            
        Returns:
            Proposal with empty list of interpretations
        """
        return Proposal.create("heuristic", [])
