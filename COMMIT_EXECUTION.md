# Commit Execution Plan - Ready to Execute

## Pre-Commit Verification ✅

**All checks passed**:
- ✅ Scoring: base + penalty formula
- ✅ Scoring: ascending (lower cost) documented  
- ✅ Prune: ascending sort (lower cost wins)
- ✅ Proposal/Commit: hash from .to_json() structure
- ✅ JSON-safety: _to_json_safe() rejects sets/bytes
- ✅ Tests: safeguard test exists, cost semantics assertions
- ✅ Seed hash: uses hash_canonical(seed_text)
- ✅ Fixture: key uses actual seed hash (64 chars)

**Test Status**: 
- ✅ Full suite: 92 passed in 0.06s
- ✅ Golden test: 2 passed in 0.01s

## Recommended: 4 Coherent Commits (Kernel Fixes + Docs Separate)

### Commit 1: Hash computation + JSON-safety
**Files** (2 files):
- `src/motherlabs_kernel/proposal_types.py`
- `src/motherlabs_kernel/commit_types.py`

### Commit 2: Scoring semantics (CRITICAL - explicit message)
**Files** (3 files):
- `src/motherlabs_kernel/scoring.py`
- `src/motherlabs_kernel/prune.py`
- `src/motherlabs_kernel/ambiguity.py`

### Commit 3: Test fixes (harness coherence)
**Files** (3 files):
- `tests/test_run_and_replay.py`
- `tests/fixtures/golden_proposals.json`
- `tests/test_ambiguity.py`

### Commit 4: Documentation (separate from fix set)
**Files** (must match exact list below):
- `ALL_FIXES_COMPLETE.md`
- `FINAL_VERIFICATION_SUMMARY.md`
- `HASH_COMPUTATION_FIX.md`
- `SCORING_FIX_FINAL.md`
- `SCORING_FIX_SUMMARY.md`
- `COMMIT_PLAN_FIXES.md`
- `FINAL_COMMIT_PLAN.md`
- `COMMIT_EXECUTION.md`

Verify `git diff --cached --name-only` output matches this exact list before committing.

## Execution Commands (Copy-Paste Ready - No Comments)

```bash
python -m pytest -q
python -m pytest -q tests/test_golden_run.py

git status --porcelain
git add src/motherlabs_kernel/proposal_types.py src/motherlabs_kernel/commit_types.py
git status --porcelain
git diff --cached --stat
git diff --cached --name-only
git commit -m "fix: compute Proposal/Commit hashes from exact .to_json() structure + strict JSON-safety" -m "Proposal.create() and Commit.create() now compute hashes from the exact dict structure that .to_json() returns (excluding the hash field itself)." -m "Changes:" -m "- Hash computed from hashable_dict matching .to_json() structure minus hash field" -m "- Added _to_json_safe() helper: rejects sets, bytes, unknown containers" -m "- None fields included in .to_json() to match pydantic behavior" -m "- Recursive conversion of objects with .to_json() method" -m "Fixes: TypeError when hashing Interpretation objects and other dataclasses"
python -m pytest -q
python -m pytest -q tests/test_golden_run.py

git add src/motherlabs_kernel/scoring.py src/motherlabs_kernel/prune.py src/motherlabs_kernel/ambiguity.py
git status --porcelain
git diff --cached --stat
git diff --cached --name-only
git commit -m "fix: implement Path B (conservatism-first) scoring semantics" -m "Changed scoring to cost semantics (lower is better) with duplicate penalty ADDED (not subtracted), aligning with 'refusal over guessing' philosophy." -m "CRITICAL CHANGES (DO NOT REVERT):" -m "- Formula: base + penalty (duplicates INCREASE cost, indicating contradiction)" -m "  - Before: base - penalty (duplicates reduced cost, wrong for Path B)" -m "  - After: base + penalty (duplicates increase cost, correct for Path B)" -m "- Sort direction: ascending (LOWER cost wins, fewer assumptions preferred)" -m "  - Before: descending (higher score wins, wrong for Path B)" -m "  - After: ascending (lower cost wins, correct for Path B)" -m "- Variable renamed: score → cost (for clarity, prevents confusion)" -m "Semantics (Path B: conservatism-first):" -m "- Fewer assumptions → lower base → lower cost → preferred" -m "- Duplicates → higher penalty → higher cost → less preferred" -m "- Shorter summaries → lower base → lower cost → preferred" -m "This aligns with 'refusal over guessing' by minimizing invented commitments until evidence/pins force specificity." -m "Golden invariant preserved: SimpleCalc remains the winner without regenerating fixtures, confirming code semantics align with intended behavior."
python -m pytest -q
python -m pytest -q tests/test_golden_run.py

git add tests/test_run_and_replay.py tests/fixtures/golden_proposals.json tests/test_ambiguity.py
git status --porcelain
git diff --cached --stat
git diff --cached --name-only
git commit -m "test: fix seed hash computation + update for cost semantics" -m "Updated tests to compute seed_hash from actual seed_text (kernel-correct) and updated assertions for cost semantics (lower wins, duplicates increase cost)." -m "Changes:" -m "- test_run_then_replay_identical_summary_hash: compute seed_hash from seed_text" -m "- test_run_outputs_stable_given_fixed_inputs: compute seed_hash from seed_text" -m "- golden_proposals.json: key updated to use actual computed seed_hash" -m "- test_scoring_duplicate_assumptions_penalty: expect duplicates increase cost (23 > 18)" -m "- test_prune_sorts_by_cost_ascending_then_name: expect ascending sort" -m "- test_lower_cost_wins_explicitly: NEW safeguard test (prevents sort reversal)" -m "This ensures RecordedProposer keys match hash computed by run_engine() and test assertions match Path B semantics. The safeguard test prevents accidental reversal of sort direction that would flip semantics from conservatism-first to specificity-first."
python -m pytest -q
python -m pytest -q tests/test_golden_run.py

git add ALL_FIXES_COMPLETE.md FINAL_VERIFICATION_SUMMARY.md HASH_COMPUTATION_FIX.md SCORING_FIX_FINAL.md SCORING_FIX_SUMMARY.md COMMIT_PLAN_FIXES.md FINAL_COMMIT_PLAN.md COMMIT_EXECUTION.md
git status --porcelain
git diff --cached --stat
git diff --cached --name-only
git commit -m "docs: add fix summaries for hash computation and scoring semantics" -m "Documented fixes applied: hash computation, JSON-safety, scoring semantics, and test fixes. Provides traceability for semantic changes." -m "Separate from fix commits to keep kernel changes surgically auditable."
python -m pytest -q
python -m pytest -q tests/test_golden_run.py
```

## Safety Steps (Already Included Above)

### Before Commit 1: Index Clean Check

Before staging any files, verify the working tree state:

```bash
git status --porcelain
```

**Expected output**: Should show only untracked/modified files you're about to stage. If you see unexpected changes, resolve them first.

After `git add ...` but before commit:

```bash
git status --porcelain
git diff --cached --stat
git diff --cached --name-only
```

**Note**: `--cached` flag is CRITICAL - it checks the staged set, not the working tree.

**Important**: Always use `git diff --cached --name-only` (not `git diff --name-only`) to check the **staged set**, not the working tree.

### Before Each Commit: Staged Set Verification

Before each commit (after `git add`), the execution commands include:

```bash
git status --porcelain
git diff --cached --stat
git diff --cached --name-only
```

Expected staged file lists:
- **Commit 1**: 2 files (after `git add`)
  - `src/motherlabs_kernel/proposal_types.py`
  - `src/motherlabs_kernel/commit_types.py`
- **Commit 2**: 3 files (after `git add`)
  - `src/motherlabs_kernel/scoring.py`
  - `src/motherlabs_kernel/prune.py`
  - `src/motherlabs_kernel/ambiguity.py`
- **Commit 3**: 3 files (after `git add`)
  - `tests/test_run_and_replay.py`
  - `tests/fixtures/golden_proposals.json`
  - `tests/test_ambiguity.py`
- **Commit 4**: Must match exact list in "Commit 4" section above (verify manually, don't rely on count)

This prevents accidental staging drift, especially for Commit 4 where doc churn is common.

### After Each Commit: Test Verification

After each commit, the execution commands automatically run:

```bash
python -m pytest -q
python -m pytest -q tests/test_golden_run.py
```

**Critical**: Both commands must pass after EACH commit, not just at the end. This provides an audit trail for "what changed when" and ensures no commit breaks the test suite.

If tests fail after any commit, investigate immediately before proceeding. This creates a strong audit trail showing exactly which commit introduced any issues.

## Verification After All Commits

```bash
python -m pytest -q && python -m pytest -q tests/test_golden_run.py
git log --oneline -5
```

Expected log output (shows last 5 commits, including the 4 new ones):
- HEAD (newest): docs: add fix summaries...
- HEAD~1: test: fix seed hash computation...
- HEAD~2: fix: implement Path B...
- HEAD~3: fix: compute Proposal/Commit hashes...
- HEAD~4: ... (previous commit before these fixes)

All tests must pass before considering commits complete.

## Status: ✅ READY FOR EXECUTION

All fixes verified, tests pass, commit plan ready.
