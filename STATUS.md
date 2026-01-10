# Project Status

## Current State: Authority Core Complete ✅

**Version:** 0.1.0 (FROZEN)  
**Date:** 2024  
**Milestone:** Deterministic engine + replay + golden fixtures

## What's Complete

### ✅ Deterministic Engine
- Pure functions, no IO, no network, no system clock
- Canonical JSON serialization
- SHA-256 hashing
- Evidence ledger with hash chaining
- Policy-driven budgets
- Authoritative DAG with invariants
- Autonomous ambiguity resolution
- Proposal/Commit boundary
- Refusal paths

### ✅ Replay System
- Deterministic replay from ledger records
- Chain validation
- Hash verification
- Summary hash computation

### ✅ Golden Fixtures
- Golden seed, pin, policy, proposals
- Expected hashes and structure snapshot
- Permanent determinism lock
- Test that enforces exact matches

## What's Frozen

The kernel core is **FROZEN** at version 0.1.0. See `KERNEL_FREEZE.md` for details.

**Frozen Components:**
- Canonical serialization
- Ledger hashing
- Replay semantics
- Collapse rules
- DAG invariants
- Proposal/Commit boundary
- Policy structure

**Breaking changes require:** Version bump + regenerated golden fixtures

## What's Next

See `NEXT_STEPS.md` for the full roadmap.

### Immediate Next Steps

1. **Add LLM Adapter** (outside kernel boundary)
   - Implements `Proposer` interface
   - Wraps OpenAI/Anthropic API
   - Returns JSON-safe proposals

2. **Add Recorded Wrapper**
   - Wraps any proposer
   - Records all proposals
   - Enables deterministic replay of live runs

3. **Enhance Artifact Pipeline**
   - Real `BlueprintSpec` structure
   - `BuildPlan` generation
   - Enhanced `VerificationPack`

### Future Steps (Optional)

4. **Add Retrieval Adapter** (optional)
   - Vector DB queries
   - Returns snippets as proposals

5. **Add Execution Boundary** (only if truly want self-building)
   - Sandboxed executor
   - Proposes diffs as proposals
   - Kernel verifies and commits

6. **Prove Dogfooding**
   - Golden run: "build the kernel"
   - Kernel builds itself
   - Self-description + build plan + verification

## Architecture Summary

```
┌─────────────────────────────────────────┐
│  FROZEN KERNEL CORE (v0.1.0)            │
│  - Canonical serialization               │
│  - Evidence ledger                       │
│  - DAG with invariants                   │
│  - Proposal/Commit boundary              │
│  - Autonomous ambiguity resolution      │
│  - Refusal paths                         │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐    ┌───────▼────────┐
│ Adapters   │    │ Future:        │
│ (to build) │    │ - Retrieval    │
│ - LLM      │    │ - Executor     │
│ - Recorded │    │                │
└────────────┘    └────────────────┘
```

## Key Principles

1. **Kernel is frozen** - no changes without version bump
2. **Adapters, not features** - all external systems are adapters
3. **Proposal boundary** - nothing authoritative without kernel commit
4. **Deterministic replay** - every run can be replayed
5. **Golden fixtures lock** - permanent determinism guarantee
6. **Refusal over guessing** - kernel refuses when it cannot converge

## Documentation

- `README.md` - Overview and quick start
- `KERNEL_FREEZE.md` - Frozen core boundary and version protocol
- `NEXT_STEPS.md` - Adapter architecture and future development
- `ADAPTER_ARCHITECTURE.md` - How to build adapters
- `CHANGELOG.md` - Version history
- `STATUS.md` - This file

## Testing

```bash
# Run all tests
pytest

# Run golden run test (locks determinism)
pytest tests/test_golden_run.py -v

# Run specific test suite
pytest tests/test_ledger.py -v
pytest tests/test_dag.py -v
pytest tests/test_ambiguity.py -v
```

## Next Milestone

**"Authority Core Complete"** ✅ → **"Adapter Layer Complete"**

Target: LLM adapter + recorded wrapper + enhanced artifacts

---

**The foundation is solid. Now build around it.**
