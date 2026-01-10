# Final Commit Plan: Fixes Applied (Ready for Execution)

## Files Changed (13 files total)

**Kernel Core (5 files)**:
- `src/motherlabs_kernel/proposal_types.py`
- `src/motherlabs_kernel/commit_types.py`
- `src/motherlabs_kernel/scoring.py`
- `src/motherlabs_kernel/prune.py`
- `src/motherlabs_kernel/ambiguity.py`

**Tests (2 files)**:
- `tests/test_ambiguity.py`
- `tests/test_run_and_replay.py`

**Fixtures (1 file)**:
- `tests/fixtures/golden_proposals.json`

**Documentation (5 files)**:
- `ALL_FIXES_COMPLETE.md`
- `FINAL_VERIFICATION_SUMMARY.md`
- `HASH_COMPUTATION_FIX.md`
- `SCORING_FIX_FINAL.md`
- `SCORING_FIX_SUMMARY.md`

## Recommended Commit Plan (3-4 Commits)

### Commit 1: Hash computation from .to_json() + strict JSON-safety
**Files**:
- `src/motherlabs_kernel/proposal_types.py`
- `src/motherlabs_kernel/commit_types.py`

**Command**:
```bash
git add src/motherlabs_kernel/proposal_types.py src/motherlabs_kernel/commit_types.py
git commit -m "fix: compute Proposal/Commit hashes from exact .to_json() structure + strict JSON-safety

Proposal.create() and Commit.create() now compute hashes from the exact
dict structure that .to_json() returns (excluding the hash field itself
to avoid circular dependency).

Changes:
- Hash computed from hashable_dict matching .to_json() structure minus hash field
- Added _to_json_safe() helper: rejects sets, bytes, unknown containers
- None fields included in .to_json() to match pydantic behavior
- Recursive conversion of objects with .to_json() method

This ensures hash computation uses same structure as serialization, preventing
drift. Strict JSON-safety enforces deterministic hashing by rejecting
non-JSON-safe types explicitly.

Fixes: TypeError when hashing Interpretation objects and other dataclasses"
```

### Commit 2: Scoring semantics: cost (lower wins) + duplicate penalty added
**Files**:
- `src/motherlabs_kernel/scoring.py`
- `src/motherlabs_kernel/prune.py`
- `src/motherlabs_kernel/ambiguity.py`

**Command**:
```bash
git add src/motherlabs_kernel/scoring.py src/motherlabs_kernel/prune.py src/motherlabs_kernel/ambiguity.py
git commit -m "fix: implement Path B (conservatism-first) scoring semantics

Changed scoring to cost semantics (lower is better) with duplicate penalty
ADDED (not subtracted), aligning with 'refusal over guessing' philosophy.

Critical changes (DO NOT REVERT):
- Formula: base + penalty (duplicates INCREASE cost, indicating contradiction)
  - Before: base - penalty (duplicates reduced cost, wrong for Path B)
  - After: base + penalty (duplicates increase cost, correct for Path B)
- Sort direction: ascending (LOWER cost wins, fewer assumptions preferred)
  - Before: descending (higher score wins, wrong for Path B)
  - After: ascending (lower cost wins, correct for Path B)
- Variable renamed: score → cost (for clarity, prevents confusion)

Semantics (Path B: conservatism-first):
- Fewer assumptions → lower base → lower cost → preferred ✅
- Duplicates → higher penalty → higher cost → less preferred ✅
- Shorter summaries → lower base → lower cost → preferred ✅

This aligns with 'refusal over guessing' by minimizing invented commitments
until evidence/pins force specificity. Golden test winner (SimpleCalc)
unchanged, confirming correct semantics without moving goalposts.

Fixes: golden test interpretation name mismatch (SimpleCalc now wins correctly)"
```

### Commit 3: Test fixes: seed hash computation + cost semantics assertions
**Files**:
- `tests/test_run_and_replay.py`
- `tests/fixtures/golden_proposals.json`
- `tests/test_ambiguity.py`

**Command**:
```bash
git add tests/test_run_and_replay.py tests/fixtures/golden_proposals.json tests/test_ambiguity.py
git commit -m "test: fix seed hash computation + update for cost semantics

Updated tests to compute seed_hash from actual seed_text (kernel-correct)
and updated assertions for cost semantics (lower wins, duplicates increase cost).

Changes:
- test_run_then_replay_identical_summary_hash: compute seed_hash from seed_text
- test_run_outputs_stable_given_fixed_inputs: compute seed_hash from seed_text
- golden_proposals.json: key updated to use actual computed seed_hash
- test_scoring_duplicate_assumptions_penalty: expect duplicates increase cost (23 > 18)
- test_prune_sorts_by_cost_ascending_then_name: expect ascending sort
- test_lower_cost_wins_explicitly: NEW safeguard test (prevents sort reversal)

This ensures RecordedProposer keys match hash computed by run_engine() and
test assertions match Path B semantics (cost: lower wins). The safeguard
test prevents accidental reversal of sort direction that would flip semantics."
```

### Commit 4: Documentation: fix summaries (optional)
**Files**:
- `ALL_FIXES_COMPLETE.md`
- `FINAL_VERIFICATION_SUMMARY.md`
- `HASH_COMPUTATION_FIX.md`
- `SCORING_FIX_FINAL.md`
- `SCORING_FIX_SUMMARY.md`

**Command**:
```bash
git add ALL_FIXES_COMPLETE.md FINAL_VERIFICATION_SUMMARY.md HASH_COMPUTATION_FIX.md SCORING_FIX_FINAL.md SCORING_FIX_SUMMARY.md
git commit -m "docs: add fix summaries for hash computation and scoring semantics

Documented fixes applied during this session:
- Hash computation from .to_json() structure
- Strict JSON-safety enforcement
- Scoring semantics fix (Path B: conservatism-first)
- Test fixes and safeguard test

These docs provide traceability for semantic changes and verification steps."
```

## Alternative: Single Coherent Commit

If you prefer a single commit for all fixes:

```bash
git add src/motherlabs_kernel/proposal_types.py src/motherlabs_kernel/commit_types.py \
        src/motherlabs_kernel/scoring.py src/motherlabs_kernel/prune.py src/motherlabs_kernel/ambiguity.py \
        tests/test_ambiguity.py tests/test_run_and_replay.py tests/fixtures/golden_proposals.json

git commit -m "fix: hash computation, JSON-safety, and scoring semantics (Path B: conservatism-first)

Hash Computation:
- Proposal/Commit hashes computed from exact .to_json() structure
- Added _to_json_safe() with strict rejection of sets, bytes, unknown containers
- None fields included to match pydantic behavior

Scoring Semantics (Path B - DO NOT REVERT):
- Formula: base + penalty (duplicates INCREASE cost)
- Sort: ascending (LOWER cost wins, fewer assumptions preferred)
- Aligns with 'refusal over guessing' philosophy

Test Fixes:
- Seed hash computation: use hash_canonical(seed_text) instead of placeholders
- Cost semantics assertions: expect duplicates increase cost, ascending sort
- Safeguard test: prevents accidental sort reversal

All tests pass (92 passed). Golden test passes (SimpleCalc wins correctly)."
```

## Verification Before Committing

**Run these commands to verify**:
```bash
# 1. Verify all tests pass
python -m pytest -q
python -m pytest -q tests/test_golden_run.py

# 2. Check git status
git status --short

# 3. Review changes (optional)
git diff src/motherlabs_kernel/scoring.py | head -50
git diff src/motherlabs_kernel/prune.py | head -30
```

## Key Commit Message Elements

**For Commit 2 (Scoring) - MUST INCLUDE**:
- "cost semantics (ascending) + duplicate penalty added"
- "DO NOT REVERT" or similar warning
- Explicit formula: `base + penalty` (duplicates INCREASE cost)
- Explicit sort: ascending (LOWER cost wins)

This prevents future "optimizations" that would flip semantics back.

## Status

✅ All fixes complete and verified
✅ All tests pass (92 passed, 2 golden passed)
✅ Ready for commit execution

**Next**: Execute commits using the plan above when git_write access is available.
