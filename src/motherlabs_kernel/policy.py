"""
Policy validation and deterministic tie-breaking.
"""

from typing import List

from .policy_types import Policy


def validate_policy(policy: Policy) -> None:
    """
    Validate policy configuration.
    
    Checks that all policy values are within valid ranges:
    - max_interpretations >= 1
    - max_nodes >= 1
    - max_depth >= 1
    - contradiction_budget >= 0
    - max_steps >= 1
    - deterministic_tiebreak is 'lexicographic' (only option for now)
    
    Args:
        policy: Policy to validate
        
    Raises:
        ValueError: If any policy value is invalid
    """
    if policy.max_interpretations < 1:
        raise ValueError(f"max_interpretations must be >= 1, got {policy.max_interpretations}")
    
    if policy.max_nodes < 1:
        raise ValueError(f"max_nodes must be >= 1, got {policy.max_nodes}")
    
    if policy.max_depth < 1:
        raise ValueError(f"max_depth must be >= 1, got {policy.max_depth}")
    
    if policy.contradiction_budget < 0:
        raise ValueError(f"contradiction_budget must be >= 0, got {policy.contradiction_budget}")
    
    if policy.max_steps < 1:
        raise ValueError(f"max_steps must be >= 1, got {policy.max_steps}")
    
    if policy.deterministic_tiebreak != 'lexicographic':
        raise ValueError(
            f"deterministic_tiebreak must be 'lexicographic', got {policy.deterministic_tiebreak}"
        )


def tie_break(strings: List[str], method: str = 'lexicographic') -> str:
    """
    Deterministically select one string from a list using tie-breaking method.
    
    Currently only supports 'lexicographic' method, which selects the
    lexicographically smallest string.
    
    Args:
        strings: List of strings to choose from
        method: Tie-breaking method (currently only 'lexicographic')
        
    Returns:
        The selected string
        
    Raises:
        ValueError: If strings list is empty or method is invalid
    """
    if not strings:
        raise ValueError("Cannot tie-break empty list")
    
    if method != 'lexicographic':
        raise ValueError(f"Unknown tie-break method: {method}")
    
    # Lexicographic: return the smallest string (deterministic)
    return min(strings)
