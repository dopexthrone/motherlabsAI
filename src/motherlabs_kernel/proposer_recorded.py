"""
RecordedProposer - Deterministic proposer for testing.

This proposer uses pre-recorded proposals stored in a dictionary, enabling
deterministic testing without external dependencies.
"""

from typing import Any, Dict

from .ambiguity_types import Interpretation
from .proposal_types import Proposal


class RecordedProposer:
    """
    Proposer that returns pre-recorded proposals from a dictionary.
    
    Used for deterministic testing. Proposals are keyed by:
    f'interpretations:{seed_hash}:{n}'
    
    The stored values must be JSON-safe lists of interpretation data that can
    be converted to Interpretation objects.
    """
    
    def __init__(self, recordings: Dict[str, Any]):
        """
        Initialize with pre-recorded proposals.
        
        Args:
            recordings: Dictionary mapping keys to proposal payloads.
                       Keys should be f'interpretations:{seed_hash}:{n}'
                       Values should be JSON-safe lists of interpretation data
        """
        self.recordings = recordings
    
    def propose_interpretations(self, seed_hash: str, n: int) -> Proposal[list[Interpretation]]:
        """
        Return pre-recorded interpretations.
        
        Args:
            seed_hash: Hash of the seed text
            n: Number of interpretations to propose
            
        Returns:
            Proposal containing list of interpretations
            
        Raises:
            KeyError: If the key is not found in recordings
        """
        key = f'interpretations:{seed_hash}:{n}'
        
        if key not in self.recordings:
            raise KeyError(f"No recording found for key: {key}")
        
        # Get the recorded data
        recorded_data = self.recordings[key]
        
        # Convert to Interpretation objects
        interpretations = [
            Interpretation(**item) if isinstance(item, dict) else item
            for item in recorded_data
        ]
        
        # Create proposal deterministically
        return Proposal.create("heuristic", interpretations)
