# Semantic Invariants - Kernel Contract

**Version**: 0.1.0  
**Status**: Normative (breaking changes require version bump + golden regeneration)

## Path B: Conservatism-First Semantics

The kernel implements **Path B (conservatism-first)** ambiguity resolution. This is a non-negotiable semantic contract.

### Scoring as Cost (Lower Wins)

- **Formula**: `cost = base + penalty`
  - `base = len(intent_summary) + 10 * len(assumptions)`
    - `len(intent_summary)` is Python string length in **characters** (not tokens, not bytes)
    - `len(assumptions)` is the count of assumption strings in the list
  - `penalty`: For each assumption in the interpretation, if it appears in multiple interpretations (across all interpretations), add `5 * (occurrence_count - 1)` where `occurrence_count` is the total number of times that exact assumption string appears across all interpretations
    - If an interpretation has multiple assumptions that are duplicated, it pays multiple penalties (one per duplicated assumption)
    - Penalty is accumulated per assumption in the interpretation being scored
- **Sort Direction**: **Ascending** (lower cost wins, fewer assumptions preferred)
- **Semantics**:
  - Fewer assumptions → lower base → lower cost → **preferred** ✅
  - Duplicates → higher penalty → higher cost → **less preferred** ✅
  - Shorter summaries → lower base → lower cost → **preferred** ✅

**Measurement Units (v0.1.0)**:
- `len(intent_summary)` is Python string length in characters (Python `len(str)`)
- Duplicate assumptions are detected by **exact string equality (`==`)** across interpretations
- **No normalization is applied in v0.1.0** (case-sensitive, whitespace-sensitive)
- If normalization (trim/lower/collapse whitespace) is introduced, that is a **breaking change** unless explicitly excluded from hashing/outcomes

**Assumption List Invariant**:
- Within a single interpretation, `assumptions` must not contain duplicate strings
- Violation is invalid input (should trigger refusal or validation error)
- If an interpretation's assumptions list contains the same string twice, behavior is undefined in v0.1.0

### Golden Invariant (Mechanically Testable)

**SimpleCalc** (less assumptive) must always win over **AdvancedCalc** (more assumptive) for the golden fixture seed, without regenerating fixtures. This locks the "refusal over guessing" philosophy.

**Mechanical Requirements**:
- The golden test (`tests/test_golden_run.py`) is a **required status check** on `main` branch and must never be skipped
- The golden test must run and pass on every push and pull request (enforced by CI)
- Any PR that changes the winner for the golden fixture is a **breaking change** and must:
  - Bump version (semantic versioning)
  - Intentionally regenerate goldens (documented in CHANGELOG)
  - Update this document with formal justification

### Required Behavior

1. **Duplicate assumptions increase cost** (penalty is added, not subtracted)
2. **Sort is ascending** (minimize cost, minimize assumptions)
3. **Golden test must pass** without fixture changes
4. **Any change to scoring/pruning/collapse semantics** is a **breaking change** and requires:
   - Version bump (semantic versioning)
   - Golden fixture regeneration (intentional, documented)
   - Update to this document
   - Formal justification

### Prohibited Changes

The following changes are **explicitly prohibited** without version bump + formal justification:

- ❌ Changing `base + penalty` to `base - penalty` (would flip semantics)
- ❌ Changing sort from ascending to descending (would flip semantics)
- ❌ Treating duplicates as "consensus" (would contradict "refusal over guessing")
- ❌ Updating golden expected without changing code semantics

### Future Changes: Refusal or Justification

If a future change to scoring/pruning/collapse is proposed:

**Option A: Formal Justification + Version Bump**
1. Document the semantic change and justification
2. Bump version (e.g., v0.1.0 → v0.2.0)
3. Regenerate golden fixtures intentionally
4. Update this document
5. Update CHANGELOG.md

**Option B: Refusal**
If the change cannot be justified within the "refusal over guessing" philosophy, the kernel must **refuse** to implement it. This is not a bug—it's correct behavior.

## Commit Hash Formula Invariants

These hash formulas are **frozen** and must not change without version bump:

- `canonicalize(value) -> bytes`: Sorted keys, no whitespace, UTF-8
- `hash_canonical(value) -> sha256_hex(canonicalize(value))`
- `Proposal.create()`: Hash from `{source, confidence, value}` (JSON-safe projection)
- `Commit.create()`: Hash from `{value, accepted_from}` (JSON-safe projection)
- Node/Edge IDs: Domain-separated, deterministic, stable

## DAG Invariants

- Edges must reference existing nodes
- No cycles for `depends_on`/`refines` edges
- `contradicts` edges excluded from cycle constraint
- Node/Edge IDs deterministic regardless of insertion order

## Ledger Invariants

- Append-only (immutable records)
- Hash-chained (parent linkage)
- Payload hash computed independently of record hash
- Replay determinism: same seed + proposals → same DAG + artifacts

## Authority Boundary

- **Only kernel can commit** authoritative state
- LLM/retrieval/runner outputs are **always proposals** (untrusted)
- Proposals must be recorded in ledger for replay determinism

## Refusal Conditions (Mandatory)

Kernel must refuse (not guess) when:
- No interpretations proposed
- Policy budgets exceeded
- Contradiction budget exceeded
- Verification cannot prove invariants

Refusal is an **expected output mode**, not a failure.

**Clarification: "Autonomous" vs "Refusal"**:
- "Autonomous" refers to not requiring human selection among interpretations during a run
- The kernel can autonomously refuse when it cannot safely converge
- "Autonomous" does not mean "always returns a blueprint" - it means "makes all decisions (accept/reject/refuse) without human input"

## Change Control

**Breaking changes** (require version bump + golden regeneration):
- Scoring/pruning/collapse semantics
- Hash formulas
- DAG ID generation
- Ledger structure
- Artifact schemas (if they affect hashes)

**Non-breaking changes** (minor version bump):
- Adding optional artifact fields (excluded from hash computation)
- New refusal conditions (if documented)
- Documentation improvements

## Version History

- **v0.1.0** (current): Path B semantics locked, goldens preserved, hash computation fixed
