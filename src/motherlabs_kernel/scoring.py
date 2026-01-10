"""
Deterministic scoring for interpretations (treated as cost: lower is better).

IMPORTANT: Changing scoring rules requires deliberate golden update and version bump.
Scoring changes affect collapse outcomes, which change artifacts. Treat scoring
changes like changing a compiler - they require intentional regeneration of
golden fixtures.

The score is interpreted as a COST metric. Lower cost = fewer assumptions =
more conservative interpretation = preferred (aligns with "refusal over guessing").
"""

from typing import List

from .ambiguity_types import Interpretation


def score_interpretation(interpretation: Interpretation, all_interpretations: List[Interpretation]) -> int:
    """
    Score an interpretation deterministically (treated as cost: lower is better).
    
    Scoring formula (interpreted as cost):
    - base = len(intent_summary) + 10 * len(assumptions)
    - penalty = number of duplicate assumption strings across all interpretations
      (add 5 per duplicate occurrence beyond first)
    - score = base + penalty
    
    Note: This is a COST metric. The kernel prefers interpretations with:
    - Fewer assumptions (minimize invented commitments, aligns with "refusal over guessing")
    - Shorter summaries (avoid over-specification)
    - Fewer duplicate assumptions (less contradiction/confusion)
    
    Selection minimizes this score (ascending sort), then uses lexicographic tie-break.
    Fewer assumptions and shorter summaries result in lower base, thus lower cost (preferred).
    Duplicates increase cost (indicate contradiction/confusion), thus less preferred.
    
    Args:
        interpretation: The interpretation to score
        all_interpretations: All interpretations (for duplicate detection)
        
    Returns:
        Integer score (cost: lower is better, fewer assumptions preferred)
    """
    # Base cost: intent_summary length + assumption count weight
    # Longer summaries and more assumptions increase base (penalize over-specification)
    base = len(interpretation.intent_summary) + 10 * len(interpretation.assumptions)
    
    # Count duplicate assumptions across all interpretations
    # Duplicates increase cost (indicate contradiction/confusion) - added to base
    # For each assumption in this interpretation, count how many times it appears
    # in all interpretations (beyond the first occurrence)
    penalty = 0
    for assumption in interpretation.assumptions:
        # Count occurrences in all interpretations
        occurrence_count = sum(
            1 for interp in all_interpretations
            if assumption in interp.assumptions
        )
        # Penalty is 5 per duplicate occurrence beyond first (added, so duplicates increase cost)
        if occurrence_count > 1:
            penalty += 5 * (occurrence_count - 1)
    
    # Cost: base + penalty (both increase cost)
    # Lower base (fewer assumptions) = lower cost = preferred
    # Duplicates increase cost = less preferred
    cost = base + penalty
    return cost
