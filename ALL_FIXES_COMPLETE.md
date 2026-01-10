# All Fixes Complete - Ready for Commit ✅

## Test Results

✅ **Full Suite**: 92 passed in 0.06s
✅ **Golden Test**: 2 passed in 0.01s

## Fixes Applied

### 1. Hash Computation from `.to_json()` Structure ✅

**Files**: `src/motherlabs_kernel/proposal_types.py`, `src/motherlabs_kernel/commit_types.py`

- `Proposal.create()` and `Commit.create()` now compute hashes from the exact dict structure that `.to_json()` returns (excluding the hash field itself)
- Hash is computed from `hashable_dict` matching `.to_json()` structure minus `proposal_hash`/`commit_hash`
- None fields are included in `.to_json()` (matches pydantic behavior)

### 2. Strict JSON-Safety in `_to_json_safe()` ✅

**Files**: `src/motherlabs_kernel/proposal_types.py`, `src/motherlabs_kernel/commit_types.py`

- Sets (`set`, `frozenset`) are explicitly rejected with `TypeError`
- Bytes (`bytes`, `bytearray`) are explicitly rejected with `TypeError`
- Unknown containers are rejected with clear error messages
- Recursive conversion of objects with `.to_json()` method

### 3. Scoring Formula Fix (Path B: Conservatism-First) ✅

**File**: `src/motherlabs_kernel/scoring.py`

**Before** (wrong for Path B):
```python
score = base - penalty  # Duplicates reduce cost (WRONG)
```

**After** (correct for Path B):
```python
cost = base + penalty  # Duplicates increase cost (CORRECT)
```

**Formula**:
- `base = len(intent_summary) + 10 * len(assumptions)` (more commitments → higher cost)
- `penalty = 5 * (duplicate_count - 1)` (contradictions → higher cost)
- `cost = base + penalty` (both increase cost)

**Semantics**:
- Fewer assumptions → lower base → lower cost → **preferred** ✅
- Duplicates → higher penalty → higher cost → **less preferred** ✅
- Shorter summaries → lower base → lower cost → **preferred** ✅

### 4. Sort Direction Fix (Ascending: Lower Cost Wins) ✅

**File**: `src/motherlabs_kernel/prune.py`

**Before** (wrong for Path B):
```python
scored.sort(key=lambda x: (-x[0], x[1].name))  # Descending: higher score wins
```

**After** (correct for Path B):
```python
scored.sort(key=lambda x: (x[0], x[1].name))   # Ascending: lower cost wins
```

**Result**: Lower cost (fewer assumptions) wins, aligning with "refusal over guessing"

### 5. Documentation Updates ✅

**Files Updated**:
- `scoring.py`: Clarified "cost: lower is better", duplicates increase cost
- `prune.py`: Clarified "ascending: minimize cost", least assumptive first
- `ambiguity.py`: Clarified "cost: lower is better" in docstring
- `test_ambiguity.py`: Updated test logic, added safeguard test

### 6. Test Fixes ✅

**File**: `tests/test_ambiguity.py`

- `test_scoring_duplicate_assumptions_penalty`: Fixed to expect duplicates increase cost
- `test_prune_sorts_by_cost_ascending_then_name`: Fixed to expect ascending sort
- `test_lower_cost_wins_explicitly`: Added safeguard test to prevent accidental reversal

**File**: `tests/test_run_and_replay.py`

- Fixed seed hash computation: uses `hash_canonical(seed_text)` instead of placeholders

**File**: `tests/fixtures/golden_proposals.json`

- Fixed key to use actual computed seed hash

## Alignment with Kernel Philosophy

✅ **"Refusal over guessing"**:
- Fewer assumptions preferred (minimize invented commitments)
- Duplicates increase cost (indicate contradiction/confusion)
- Shorter summaries preferred (avoid over-specification)

✅ **Deterministic tie-breaking**:
- Sort by cost (ascending), then name (lexicographic)
- Fully deterministic and reproducible

✅ **Golden test locked**:
- SimpleCalc (cost 101, 2 assumptions) wins
- AdvancedCalc (cost 102, 3 assumptions) loses
- Code matches expected (DO NOT regenerate goldens)

## Files Modified (Summary)

1. `src/motherlabs_kernel/proposal_types.py`: Hash from `.to_json()`, strict JSON-safety
2. `src/motherlabs_kernel/commit_types.py`: Hash from `.to_json()`, strict JSON-safety
3. `src/motherlabs_kernel/scoring.py`: Formula fixed (`base + penalty`), variable renamed to `cost`
4. `src/motherlabs_kernel/prune.py`: Sort direction fixed (ascending), docstring updated
5. `src/motherlabs_kernel/ambiguity.py`: Docstring updated to clarify cost semantics
6. `tests/test_ambiguity.py`: Test logic fixed, safeguard test added
7. `tests/test_run_and_replay.py`: Seed hash computation fixed
8. `tests/fixtures/golden_proposals.json`: Key updated to use actual seed hash

## Verification Status

✅ All tests pass (92 passed in 0.06s)
✅ Golden test passes (2 passed in 0.01s)
✅ Formula correct: `base + penalty` (duplicates increase cost)
✅ Sort correct: ascending (lower cost wins)
✅ Winner correct: SimpleCalc (matches golden expected)
✅ Syntax verified: All files parse correctly
✅ Semantics verified: Aligns with "refusal over guessing"

## Status: ✅ READY FOR COMMIT

All fixes are complete, verified, and tests pass. The kernel now correctly implements Path B (conservatism-first), aligning with "refusal over guessing" by preferring interpretations with fewer assumptions and penalizing duplicates (contradictions).

**Next Step**: Commit the changes with clear messages documenting each fix.
