"""
Autonomous ambiguity resolution protocol.

Implements: expand → score → prune → collapse
"""

from typing import List, Protocol

from .ambiguity_types import Interpretation
from .commit_types import Commit
from .policy import tie_break
from .policy_types import Policy
from .prune import prune_interpretations
from .proposal_types import Proposal


class Proposer(Protocol):
    """
    Protocol for proposers that generate interpretations.
    
    Proposers are external sources (LLM, retrieval, heuristic) that generate
    probabilistic proposals. The kernel uses proposers but never treats their
    output as authoritative - proposals must be committed.
    """
    
    def propose_interpretations(self, seed_hash: str, n: int) -> Proposal[List[Interpretation]]:
        """
        Propose interpretations for a given seed.
        
        Args:
            seed_hash: Hash of the seed text
            n: Number of interpretations to propose
            
        Returns:
            Proposal containing list of interpretations
        """
        ...


def resolve_ambiguity(
    run_id: str,
    seed_hash: str,
    policy: Policy,
    proposer: Proposer
) -> Commit[Interpretation]:
    """
    Resolve ambiguity autonomously: expand → score (cost) → prune → collapse.
    
    Process:
    1. Expand: Call proposer to get interpretations (proposal)
    2. Score: Score all interpretations deterministically (as cost: lower is better)
    3. Prune: Keep top K interpretations based on cost (ascending) and tie-breaking
    4. Collapse: Select winner (first after prune: lowest cost/least assumptive)
    5. Commit: Create commit from winner
    
    Note: Score is interpreted as cost. Lower cost = fewer assumptions = more conservative = preferred.
    This aligns with "refusal over guessing" by minimizing invented commitments.
    
    Args:
        run_id: Unique run identifier
        seed_hash: Hash of the seed text
        policy: Policy with max_interpretations limit
        proposer: Proposer that generates interpretations
        
    Returns:
        Commit containing the chosen interpretation
        
    Raises:
        ValueError: If proposer returns empty list or no valid interpretations
    """
    # Expand: Get proposals
    proposal = proposer.propose_interpretations(seed_hash, policy.max_interpretations)
    interpretations = proposal.value
    
    if not interpretations:
        raise ValueError("Proposer returned empty interpretations list")
    
    # Prune: Keep top K
    pruned = prune_interpretations(interpretations, policy)
    
    if not pruned:
        raise ValueError("No interpretations after pruning")
    
    # Collapse: Winner is first after prune
    winner = pruned[0]
    
    # Commit: Create commit from winner
    commit = Commit.create(winner, accepted_from=proposal.proposal_hash)
    
    return commit
