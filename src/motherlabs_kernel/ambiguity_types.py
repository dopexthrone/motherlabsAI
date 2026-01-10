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
        assumptions: List of assumption strings
        intent_summary: Summary of the intent for this interpretation
    """
    name: str
    assumptions: list[str]
    intent_summary: str
    
    def to_json(self) -> dict:
        """Convert to JSON-safe dict."""
        return {
            "name": self.name,
            "assumptions": self.assumptions,
            "intent_summary": self.intent_summary
        }
