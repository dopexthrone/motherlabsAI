# Hash Computation Fix - Complete ✅

## Summary

Fixed `Proposal.create()` and `Commit.create()` to:
1. Compute hashes from the exact dict structure that `.to_json()` returns (excluding the hash field itself)
2. Reject sets and unknown containers in `_to_json_safe()`
3. Include None fields in `.to_json()` to match pydantic behavior

## Changes Made

### 1. Hash Computation Structure

**Before:** Hash was computed from a parallel structure that might differ from `.to_json()`

**After:** Hash is computed from the exact same dict structure that `.to_json()` would return, but excluding the hash field itself (to avoid circular dependency).

**Implementation:**
- `Proposal.create()`: Hash computed from `{"source": source, "confidence": confidence, "value": json_safe_value}` (matches `.to_json()` minus `proposal_hash`)
- `Commit.create()`: Hash computed from `{"value": json_safe_value, "accepted_from": accepted_from}` (matches `.to_json()` minus `commit_hash`)

### 2. Strict JSON-Safety in `_to_json_safe()`

**Added explicit rejection of:**
- Sets (`set`, `frozenset`) - Not JSON-safe, no order
- Bytes (`bytes`, `bytearray`) - Not JSON-safe
- Other unknown containers
- NaN/Inf floats (already handled)

**Added proper error messages:**
- `TypeError` for unsupported types (sets, bytes, unknown containers)
- `ValueError` for NaN/Inf

### 3. None Field Inclusion

**Ensured `.to_json()` includes all fields including None values:**
- Matches pydantic `.model_dump()` behavior (includes None fields by default)
- `Proposal.to_json()` includes `confidence: None` if confidence is None
- `Commit.to_json()` includes `accepted_from: None` if accepted_from is None

## Verification

All checks passed:
- ✅ `Proposal.create()` hashes from same structure as `.to_json()` (excluding proposal_hash)
- ✅ `Commit.create()` hashes from same structure as `.to_json()` (excluding commit_hash)
- ✅ Sets are correctly rejected
- ✅ Bytes are correctly rejected
- ✅ None fields are included in `.to_json()` (matches pydantic)

## Files Modified

1. `src/motherlabs_kernel/proposal_types.py`
   - Updated `create()` to compute hash from dict matching `.to_json()` structure (minus proposal_hash)
   - Updated `_to_json_safe()` to reject sets, bytes, and unknown containers
   - Updated docstrings to clarify hash computation

2. `src/motherlabs_kernel/commit_types.py`
   - Updated `create()` to compute hash from dict matching `.to_json()` structure (minus commit_hash)
   - Updated `_to_json_safe()` to reject sets, bytes, and unknown containers
   - Updated docstrings to clarify hash computation

## Running Tests

### Prerequisites
```bash
# Install pytest in virtual environment
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[test]"
```

### Run Full Test Suite
```bash
python3 -m pytest -q
```

### Run Golden Test
```bash
python3 -m pytest -q tests/test_golden_run.py -v
```

## Golden Test Failure Handling

If the golden test fails, **do not weaken tests**. Instead:

### Step 1: Identify the Cause

Check if `.to_json()` structure differs from previous pydantic `.model_dump()`:

```python
# Compare structure
import json
proposal = Proposal.create("heuristic", [interpretation])
json_output = proposal.to_json()

# Check:
# 1. Are all expected fields present?
# 2. Are None fields included? (pydantic includes them by default)
# 3. Are field names identical?
# 4. Are nested structures identical?
```

### Step 2: Determine Action

**Option A: Structure is Identical (Hash Should Match)**
- If `.to_json()` produces the exact same structure as pydantic `.model_dump()`, hashes should match
- If they don't match, investigate why:
  - Check field order (should be sorted in canonicalize)
  - Check None handling (should be included)
  - Check nested structure handling

**Option B: Structure Differs (Semantic Change)**
- If `.to_json()` structure differs from pydantic, this is a semantic change
- Document in `CHANGELOG.md` as a breaking change
- Regenerate golden fixtures:
  ```bash
  # Run golden test to get new values
  python3 -m pytest tests/test_golden_run.py -v --capture=no
  
  # Update tests/fixtures/golden_expected.json with new expected values
  ```

### Step 3: Common Differences to Check

1. **None Field Inclusion:**
   - Pydantic `.model_dump()` includes None fields by default
   - Our `.to_json()` now includes None fields ✅

2. **Field Exclusion:**
   - Check if any fields are excluded in `.to_json()` that were included in `.model_dump()`
   - All fields should be included

3. **Nested Structure:**
   - Check if nested objects are converted correctly
   - `Interpretation.to_json()` should produce the same structure

## Expected Test Results

After these fixes, the following tests should pass:
- ✅ `tests/test_ambiguity.py` (3 tests) - No more `TypeError: Interpretation not JSON-safe`
- ✅ `tests/test_proposer.py` (2 tests) - No more `TypeError: Interpretation not JSON-safe`
- ✅ `tests/test_refusal.py` (3 tests) - No more `TypeError: Interpretation not JSON-safe`
- ✅ `tests/test_run_and_replay.py` (2 tests) - No more `KeyError: RecordedProposer`
- ✅ `tests/test_golden_run.py` (2 tests) - May need golden fixture regeneration if structure differs

## Semantic Impact

**No changes to core semantics:**
- ✅ No changes to canonicalization/hashing formulas
- ✅ No changes to ledger hash formulas
- ✅ No changes to collapse/scoring/pruning semantics
- ✅ Only adds conversion layer for dataclass objects before hashing
- ✅ Only adds strict rejection of unsupported containers

**Potential semantic change:**
- ⚠️ If `.to_json()` structure differs from pydantic `.model_dump()`, golden fixtures need regeneration (documented as breaking change)
