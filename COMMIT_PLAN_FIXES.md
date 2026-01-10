# Commit Plan: Fixes Applied (Ready for Commit)

## Summary of Changes

**Files Modified**: 13 files
- 5 kernel core files (proposal_types, commit_types, scoring, prune, ambiguity)
- 3 test files (test_ambiguity, test_run_and_replay, golden_proposals.json)
- 5 documentation files (created during fixes)

## Commit Organization

### Commit 1: Hash computation from .to_json() structure
**Files**:
- `src/motherlabs_kernel/proposal_types.py`
- `src/motherlabs_kernel/commit_types.py`

**Message**:
```
fix: compute Proposal/Commit hashes from exact .to_json() structure

Proposal.create() and Commit.create() now compute hashes from the exact
dict structure that .to_json() returns (excluding the hash field itself
to avoid circular dependency).

This ensures hash computation uses the same structure as serialization,
preventing drift between hashing and serialization.

- Proposal: hash from {source, confidence, value} (matches .to_json() minus proposal_hash)
- Commit: hash from {value, accepted_from} (matches .to_json() minus commit_hash)
- None fields included in .to_json() to match pydantic behavior
```

### Commit 2: Strict JSON-safety: reject sets and unknown containers
**Files**:
- `src/motherlabs_kernel/proposal_types.py` (updated)
- `src/motherlabs_kernel/commit_types.py` (updated)

**Message**:
```
fix: enforce strict JSON-safety in _to_json_safe()

Added explicit rejection of sets, bytes, and unknown containers in
_to_json_safe() helper methods to ensure deterministic hashing.

- Reject sets (set, frozenset) with TypeError: "Sets are not JSON-safe"
- Reject bytes (bytes, bytearray) with TypeError: "Bytes are not JSON-safe"
- Reject unknown containers with clear error messages
- Recursively converts objects with .to_json() method to dicts
- Preserves order for lists/tuples

This ensures only JSON-safe primitives reach canonicalize(), preventing
subtle nondeterminism from unsupported types.
```

### Commit 3: Scoring semantics: cost (lower wins) + duplicate penalty added
**Files**:
- `src/motherlabs_kernel/scoring.py`
- `src/motherlabs_kernel/prune.py`
- `src/motherlabs_kernel/ambiguity.py`

**Message**:
```
fix: implement Path B (conservatism-first) scoring semantics

Changed scoring to cost semantics (lower is better) with duplicate penalty
added (not subtracted), aligning with "refusal over guessing" philosophy.

Changes:
- Formula: base + penalty (duplicates increase cost, indicating contradiction/confusion)
  - Before: base - penalty (duplicates reduced cost, wrong for Path B)
  - After: base + penalty (duplicates increase cost, correct for Path B)
- Sort direction: ascending (lower cost wins, fewer assumptions preferred)
  - Before: descending (higher score wins, wrong for Path B)
  - After: ascending (lower cost wins, correct for Path B)
- Variable renamed: score → cost (for clarity, prevents confusion)

Semantics:
- Fewer assumptions → lower base → lower cost → preferred ✅
- Duplicates → higher penalty → higher cost → less preferred ✅
- Shorter summaries → lower base → lower cost → preferred ✅

This aligns with "refusal over guessing" by minimizing invented commitments
until evidence/pins force specificity. Golden test winner (SimpleCalc) unchanged,
confirming correct semantics without moving goalposts.
```

### Commit 4: Test fixes: seed hash computation + JSON-safety assertions
**Files**:
- `tests/test_run_and_replay.py`
- `tests/fixtures/golden_proposals.json`

**Message**:
```
fix: use computed seed hash in test recordings

Updated tests to compute seed_hash from actual seed_text using hash_canonical()
instead of placeholder values. This aligns test harness with kernel's internal
seed hash computation.

Changes:
- test_run_then_replay_identical_summary_hash: compute seed_hash from seed_text
- test_run_outputs_stable_given_fixed_inputs: compute seed_hash from seed_text
- golden_proposals.json: key updated to use actual computed seed_hash

This ensures RecordedProposer keys match the hash computed by run_engine(),
preventing KeyError and maintaining test determinism.
```

### Commit 5: Test updates: cost semantics + safeguard test
**Files**:
- `tests/test_ambiguity.py`

**Message**:
```
test: update ambiguity tests for cost semantics (lower wins)

Updated tests to reflect cost semantics (ascending sort, duplicates increase cost)
and added safeguard test to prevent accidental reversal of sort direction.

Changes:
- test_scoring_duplicate_assumptions_penalty: expect duplicates increase cost (23 > 18)
- test_prune_sorts_by_cost_ascending_then_name: expect ascending sort (lower cost first)
- test_lower_cost_wins_explicitly: NEW safeguard test to prevent sort reversal

The safeguard test explicitly asserts "lower cost wins" using golden fixture
interpretations (SimpleCalc vs AdvancedCalc), ensuring future changes don't
accidentally flip semantics from conservatism-first to specificity-first.
```

### Commit 6: Documentation: fix summaries
**Files**:
- `HASH_COMPUTATION_FIX.md`
- `SCORING_FIX_FINAL.md`
- `ALL_FIXES_COMPLETE.md`
- `FINAL_VERIFICATION_SUMMARY.md`
- `SCORING_FIX_SUMMARY.md`

**Message**:
```
docs: add fix summaries for hash computation and scoring semantics

Documented all fixes applied during this session:
- Hash computation from .to_json() structure
- Strict JSON-safety enforcement
- Scoring semantics fix (Path B: conservatism-first)
- Test fixes and safeguard test

These docs provide traceability for the semantic changes and verification
steps taken to ensure kernel correctness.
```

## Execution Order

1. **Commit 1-2**: Hash computation + JSON-safety (logical group: Proposal/Commit hashing)
2. **Commit 3**: Scoring semantics (critical semantic change, explicit message)
3. **Commit 4**: Test harness fixes (seed hash computation + fixtures)
4. **Commit 5**: Test updates (cost semantics assertions)
5. **Commit 6**: Documentation (optional, can be combined or separate)

## Alternative: Fewer Commits

If preferred, can group into 3 commits:

### Option A (Logical Groups):
1. **Hash + JSON-safety** (Commits 1-2 combined)
2. **Scoring semantics** (Commit 3 - keep explicit message about cost/duplicate penalty)
3. **Tests + Fixtures** (Commits 4-5 combined, keeps harness coherent)
4. **Docs** (Commit 6 - optional)

### Option B (Minimal):
1. **Hash computation + JSON-safety** (Commits 1-2)
2. **Scoring: cost semantics + duplicate penalty added** (Commit 3 - critical)
3. **Test fixes + updates** (Commits 4-5 + docs optional)

## Recommendation

**Use Option A (3-4 commits)** to keep logical groups together:
- Hash/JSON-safety: coherent boundary
- Scoring: critical semantic change (explicit message)
- Tests: harness coherence (seed hash + fixtures + assertions)
- Docs: optional, can be separate or combined

This balances granularity with logical coherence.
