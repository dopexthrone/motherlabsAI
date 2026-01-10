"""
Type definitions for ambiguity resolution.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Interpretation:
    """
    An interpretation of the seed intent.
    
    Fields:
        name: Unique name for this interpretation
        assumptions: List of assumption strings (must not contain duplicates)
        intent_summary: Summary of the intent for this interpretation
    
    Invariants (enforced at construction):
        - assumptions list must not contain duplicate strings
        - Violation raises ValueError (invalid input)
    """
    name: str
    assumptions: list[str]
    intent_summary: str
    
    def __post_init__(self):
        """
        Validate assumptions list has no duplicates (exact string equality).
        
        Raises:
            ValueError: If assumptions list contains duplicate strings
        """
        if len(self.assumptions) != len(set(self.assumptions)):
            # Find duplicates for error message
            seen = set()
            duplicates = []
            for assumption in self.assumptions:
                if assumption in seen:
                    duplicates.append(assumption)
                else:
                    seen.add(assumption)
            raise ValueError(
                f"Interpretation '{self.name}' contains duplicate assumptions: {duplicates}. "
                "Assumptions list must not contain duplicates (exact string equality)."
            )
    
    def to_json(self) -> dict:
        """Convert to JSON-safe dict."""
        return {
            "name": self.name,
            "assumptions": self.assumptions,
            "intent_summary": self.intent_summary
        }
