"""
Pruning logic for interpretations.
"""

from typing import List

from .ambiguity_types import Interpretation
from .policy import tie_break
from .policy_types import Policy
from .scoring import score_interpretation


def prune_interpretations(
    interpretations: List[Interpretation],
    policy: Policy
) -> List[Interpretation]:
    """
    Prune interpretations to top K based on score (cost) and tie-breaking.
    
    Process:
    1. Score all interpretations (treated as cost: lower is better, fewer assumptions preferred)
    2. Sort by score (ascending: minimize cost), then by name (lexicographic) for ties
    3. Keep top K (policy.max_interpretations)
    
    This aligns with "refusal over guessing" by preferring interpretations with
    fewer assumptions (less guessing) unless other factors override.
    
    Args:
        interpretations: List of interpretations to prune
        policy: Policy with max_interpretations limit
        
    Returns:
        Pruned list of top K interpretations (least assumptive first)
    """
    if not interpretations:
        return []
    
    # Score all interpretations (treated as cost)
    scored = [
        (score_interpretation(interp, interpretations), interp)
        for interp in interpretations
    ]
    
    # Sort by score (ascending: minimize cost/assumptions), then by name (lexicographic) for ties
    # Lower score = fewer assumptions = more conservative = preferred
    scored.sort(key=lambda x: (x[0], x[1].name))
    
    # Keep top K (lowest scores = least assumptive)
    top_k = scored[:policy.max_interpretations]
    
    # Return just the interpretations
    return [interp for _, interp in top_k]
