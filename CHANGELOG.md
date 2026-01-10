# Changelog

All notable changes to the Motherlabs Kernel will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024 - FROZEN

### Added - Initial Release

- **Canonical Serialization** (`canonical.py`, `hash.py`)
  - `canonicalize()` - Canonical JSON serialization with sorted keys, no whitespace
  - `hash_canonical()` - Deterministic SHA-256 hashing
  - `sha256_hex()` - SHA-256 hex string output
  - Rejects NaN, Inf, non-JSON-safe types

- **Evidence Ledger** (`ledger.py`, `ledger_types.py`, `ledger_validate.py`)
  - Append-only, hash-chained ledger
  - `EvidenceRecord` with version, timestamp token, kind, parent, payload
  - `validate_chain()` - Validates hash chain integrity
  - Tamper-evident audit trail

- **Policy System** (`policy_types.py`, `policy.py`)
  - `Policy` with budgets (max_interpretations, max_nodes, max_depth, contradiction_budget, max_steps)
  - `tie_break()` - Deterministic lexicographic tie-breaking
  - `validate_policy()` - Policy validation

- **Authoritative DAG** (`dag.py`, `dag_types.py`, `dag_ids.py`, `dag_invariants.py`)
  - Deterministic node and edge ID generation (domain-separated hashing)
  - Cycle detection for depends_on/refines edges
  - Self-contradiction prevention
  - Invariant enforcement

- **Proposal/Commit Boundary** (`proposal_types.py`, `commit_types.py`)
  - `Proposal[T]` - Probabilistic, non-authoritative proposals
  - `Commit[T]` - Authoritative, committed state
  - Clear separation: LLM proposals are never authoritative

- **Autonomous Ambiguity Resolution** (`ambiguity.py`, `ambiguity_types.py`, `scoring.py`, `prune.py`)
  - `Interpretation` - Intent interpretation with assumptions
  - Deterministic scoring (base + duplicate penalty)
  - Pruning (top K with tie-breaking)
  - Collapse to winner
  - Fully autonomous (no human-in-the-loop)

- **Engine Run** (`run_engine.py`, `replay.py`)
  - `run_engine()` - Complete engine run: seed → ledger → DAG → artifacts
  - `replay_from_ledger()` - Deterministic replay from ledger records
  - Timestamp tokens (deterministic ordering keys, not wall-clock time)

- **Artifacts** (`artifacts_blueprint.py`, `artifacts_verification.py`, `artifacts_refusal.py`)
  - `BlueprintSpec` - Blueprint specification (currently minimal structure)
  - `VerificationPack` - Verification and replay metadata
  - `RefusalReport` - Refusal when kernel cannot converge

- **Refusal Paths** (`refusal.py`)
  - `check_refusal_conditions()` - Detects refusal conditions
  - Kernel refuses rather than guesses
  - Policy suggestions for refusal reasons

- **Proposers** (`proposer_types.py`, `proposer_recorded.py`, `proposer_null.py`)
  - `Proposer` protocol interface
  - `RecordedProposer` - Deterministic proposer for testing
  - `NullProposer` - Empty proposer for refusal testing

- **Golden Fixtures** (`tests/fixtures/`, `tests/test_golden_run.py`)
  - Golden seed, pin, policy, proposals
  - Expected hashes and structure snapshot
  - Permanent determinism lock

### Design Decisions

- **Timestamps are ordering tokens** - Not wall-clock time, deterministic sequence
- **Scoring changes are semantic version bumps** - Changing scoring changes outcomes
- **Proposal hashing uses canonicalization** - Equivalent proposals hash identically
- **DAG contradicts edges ignored for cycles** - Contradictions are conflicts, not dependencies
- **Self-contradiction edges prevented** - Cannot have from==to for contradicts

### Semantic Invariants (v0.1.0)

**Path B: Conservatism-First Semantics** (locked in v0.1.0):
- Scoring formula: `cost = base + penalty` where:
  - `base = len(intent_summary) + 10 * len(assumptions)`
  - `penalty = 5 * (duplicate_occurrences - 1)` for duplicate assumptions
  - Duplicates **increase** cost (penalty is added, not subtracted)
- Sort direction: **ascending** (lower cost wins, fewer assumptions preferred)
- Golden invariant: SimpleCalc must always win over AdvancedCalc (without regenerating fixtures)
- Future changes to scoring/pruning/collapse semantics require:
  - Version bump (semantic versioning)
  - Golden fixture regeneration (intentional, documented)
  - Formal justification
  - Update to SEMANTIC_INVARIANTS.md

See `SEMANTIC_INVARIANTS.md` for complete contract.

### Breaking Changes

None - this is the initial release.

**Note**: Any future change to scoring/pruning/collapse semantics is a breaking change and requires version bump + golden regeneration.

### Deprecated

Nothing yet.

### Security

- All hashing uses SHA-256
- Ledger provides tamper-evident audit trail
- Proposal/Commit boundary prevents LLM from being authoritative

---

## Future Versions

### [0.2.0] - Planned

- LLM adapter (outside kernel boundary)
- Recorded wrapper for live runs
- Enhanced BlueprintSpec structure

### [0.3.0] - Planned

- Retrieval adapter (optional)
- BuildPlan generation
- Enhanced VerificationPack

### [1.0.0] - Planned

- Execution boundary (optional)
- Self-building proof (dogfooding golden run)

---

**Note:** Version 0.1.0 is FROZEN. See `KERNEL_FREEZE.md` for details.
