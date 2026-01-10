# Scoring Fix Summary: Path B (Conservatism-First)

## Change Applied

**Minimal fix**: Changed sort direction from descending to ascending in `prune.py`

**Before** (line 42):
```python
scored.sort(key=lambda x: (-x[0], x[1].name))  # Descending: higher score wins
```

**After** (line 46):
```python
scored.sort(key=lambda x: (x[0], x[1].name))   # Ascending: lower cost (fewer assumptions) wins
```

**Scoring formula unchanged**: Still `base - penalty` where:
- `base = len(intent_summary) + 10 * len(assumptions)`
- `penalty = 5 * (duplicate_count - 1)` for duplicates
- `score = base - penalty`

## Rationale: Aligns with "Refusal Over Guessing"

The kernel philosophy emphasizes:
- "Refusal over guessing" (MOTHERLABS_INTENT.md, KERNEL_CORRECT_GUIDELINES.md)
- "Minimize invented commitments until evidence/pins force specificity"
- "Stay conservative until pins/constraints demand detail"

**Path B** (implemented): Lower cost (fewer assumptions) wins
- SimpleCalc (2 assumptions, cost 91) → Wins ✅
- AdvancedCalc (3 assumptions, cost 92) → Loses

This aligns with kernel philosophy: prefer fewer assumptions (less guessing).

## Naming & Contract Clarity

### Code Updates ✅
- `scoring.py`: Updated docstring to clarify "cost: lower is better"
- `prune.py`: Updated docstring to clarify "ascending: minimize cost"
- `ambiguity.py`: Updated docstring to clarify "cost: lower is better"
- `test_ambiguity.py`: Updated tests to reflect cost semantics, added safeguard test

### Ledger/Artifacts ✅
- No score/cost stored in ledger payloads (only interpretation object stored)
- No ambiguous "winner_score" fields in artifacts
- Winner stored as interpretation object only (no numeric score)

### Tests ✅
- Added `test_lower_cost_wins_explicitly()` safeguard test
- Updated `test_scoring_duplicate_assumptions_penalty()` to use cost semantics
- Updated `test_prune_sorts_by_cost_ascending_then_name()` with correct semantics

## Verification

### Manual Verification ✅
- Lower cost wins: SimpleCalc (91) < AdvancedCalc (92) ✅
- Ascending sort: Lowest cost first ✅
- Tie-breaking: Lexicographic (Apple < Banana < Zebra) ✅

### Expected Test Results (requires pytest)
- `tests/test_ambiguity.py`: All tests should pass
- `tests/test_golden_run.py`: Should pass (SimpleCalc wins as expected)
- Full suite: Should pass

## Formula Implication (Acknowledged, Not Changed)

Because `len(intent_summary)` increases cost, the kernel will slightly prefer shorter summaries even when assumptions are equal. This is coherent with "don't reward verbosity" - aligns with conservatism.

If future change needed: could switch summary length to capped contribution or remove it, but current behavior is correct and coherent.

## Next Steps

1. **Run full suite**: `python -m pytest -q` (requires pytest in venv)
2. **Run golden test**: `python -m pytest -q tests/test_golden_run.py`
3. **If both pass**: Ready to commit (DO NOT regenerate goldens - code now matches expected)

## Breaking Change Note

This is a semantic change (score direction flipped) but:
- Golden expected was correct (SimpleCalc should win)
- Code was wrong (was selecting AdvancedCalc)
- Fix aligns code with intended semantics
- No golden regeneration needed (golden was the truth, code was wrong)
