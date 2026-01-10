"""
Refusal path detection and reporting.

The kernel must refuse rather than guess when it cannot converge
deterministically within policy limits.
"""

from typing import List

from .ambiguity_types import Interpretation
from .policy_types import Policy
from .proposal_types import Proposal


def check_refusal_conditions(
    proposal: Proposal[List[Interpretation]],
    policy: Policy,
    step_count: int,
    node_count: int,
    interpretations: List[Interpretation]
) -> List[str]:
    """
    Check if refusal conditions are met.
    
    Refusal conditions (deterministic):
    1. Proposer returns 0 interpretations
    2. Contradictions exceed contradiction_budget
       (contradictions = total duplicates of assumption strings across
        interpretations after prune)
    3. max_nodes or max_steps exceeded before selecting intent root
    
    Args:
        proposal: Proposal from proposer
        policy: Policy with limits
        step_count: Current step count
        node_count: Current node count
        interpretations: List of interpretations (after prune if applicable)
        
    Returns:
        List of refusal reason codes (empty if no refusal needed)
    """
    reasons = []
    
    # Condition 1: Empty proposal
    if not proposal.value:
        reasons.append("empty_proposal")
    
    # Condition 2: Contradictions exceed budget
    if interpretations:
        # Count duplicate assumptions
        assumption_counts = {}
        for interp in interpretations:
            for assumption in interp.assumptions:
                assumption_counts[assumption] = assumption_counts.get(assumption, 0) + 1
        
        # Count duplicates (occurrences beyond first)
        total_duplicates = sum(count - 1 for count in assumption_counts.values() if count > 1)
        
        if total_duplicates > policy.contradiction_budget:
            reasons.append(f"contradictions_exceeded:{total_duplicates}>{policy.contradiction_budget}")
    
    # Condition 3: Budgets exceeded
    if node_count > policy.max_nodes:
        reasons.append(f"max_nodes_exceeded:{node_count}>{policy.max_nodes}")
    
    if step_count > policy.max_steps:
        reasons.append(f"max_steps_exceeded:{step_count}>{policy.max_steps}")
    
    return reasons


def generate_policy_suggestions(reason_codes: List[str]) -> List[str]:
    """
    Generate deterministic policy suggestion templates.
    
    Args:
        reason_codes: List of refusal reason codes
        
    Returns:
        List of policy suggestion template strings
    """
    suggestions = []
    
    for reason in reason_codes:
        if reason == "empty_proposal":
            suggestions.append("Increase proposer output or check proposer configuration")
        elif reason.startswith("contradictions_exceeded"):
            suggestions.append("Increase contradiction_budget or reduce assumption overlap")
        elif reason.startswith("max_nodes_exceeded"):
            suggestions.append("Increase max_nodes or simplify seed intent")
        elif reason.startswith("max_steps_exceeded"):
            suggestions.append("Increase max_steps or reduce exploration depth")
    
    return suggestions
