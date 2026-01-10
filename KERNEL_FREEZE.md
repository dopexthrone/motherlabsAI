# Kernel Freeze Declaration

**Version:** 0.1.0  
**Date:** 2024  
**Status:** FROZEN

## Core Boundary

The following components are **FROZEN** and form the authoritative kernel boundary:

### Frozen Components

1. **Canonical Serialization** (`canonical.py`, `hash.py`)
   - `canonicalize()` - Canonical JSON serialization
   - `hash_canonical()` - Deterministic hashing
   - `sha256_hex()` - SHA-256 hex output
   - **Breaking changes require:** Version bump + regenerated golden fixtures

2. **Evidence Ledger** (`ledger.py`, `ledger_types.py`, `ledger_validate.py`)
   - `Ledger` - Append-only, hash-chained ledger
   - `EvidenceRecord` - Immutable record structure
   - `validate_chain()` - Chain validation
   - **Breaking changes require:** Version bump + regenerated golden fixtures

3. **Replay Semantics** (`replay.py`)
   - `replay_from_ledger()` - Deterministic replay
   - Replay validation logic
   - **Breaking changes require:** Version bump + regenerated golden fixtures

4. **Collapse Rules** (`scoring.py`, `prune.py`, `ambiguity.py`)
   - Scoring algorithm (base + penalty formula)
   - Pruning logic (top K, tie-breaking)
   - Collapse selection
   - **Breaking changes require:** Version bump + regenerated golden fixtures + semantic version bump

5. **DAG Invariants** (`dag.py`, `dag_invariants.py`, `dag_ids.py`)
   - Deterministic ID generation
   - Cycle detection rules
   - Invariant checks
   - **Breaking changes require:** Version bump + regenerated golden fixtures

6. **Proposal/Commit Boundary** (`proposal_types.py`, `commit_types.py`)
   - Proposal structure (never authoritative)
   - Commit structure (authoritative)
   - Hash computation
   - **Breaking changes require:** Version bump + regenerated golden fixtures

7. **Policy Structure** (`policy_types.py`, `policy.py`)
   - Policy fields and validation
   - Tie-breaking rules
   - **Breaking changes require:** Version bump + regenerated golden fixtures

## Version Bump Protocol

When making breaking changes to frozen components:

1. **Increment version** in `__init__.py` and `pyproject.toml`
2. **Document changes** in `CHANGELOG.md`
3. **Regenerate golden fixtures** (`tests/fixtures/golden_expected.json`)
4. **Update golden run test** if structure changed
5. **Verify replay still works** with new version

## What Can Change Outside Core

- **Adapters** (LLM, Retrieval) - Can be added/modified freely
- **Artifact structures** (BlueprintSpec, BuildPlan) - Can evolve
- **Execution boundary** - Can be added as separate service
- **Test fixtures** (non-golden) - Can be modified

## Golden Fixtures Lock

The golden fixtures (`tests/fixtures/golden_*.json`, `tests/test_golden_run.py`) are the **permanent lock** on determinism. Any change that breaks golden fixtures must be:

1. Intentional (not accidental)
2. Documented (in CHANGELOG)
3. Version-bumped
4. Regenerated with new expected values

## No "Rebuild Mode"

Once frozen, the core does not enter "rebuild mode." Changes are:
- **Additive** (new adapters, new artifact types)
- **External** (services outside kernel boundary)
- **Versioned** (explicit version bumps for breaking changes)

---

**This kernel is the foundation. Build around it, not through it.**
