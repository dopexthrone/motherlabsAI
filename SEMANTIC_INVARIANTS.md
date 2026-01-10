# Semantic Invariants - Kernel Contract

**Version**: 0.1.0  
**Status**: Normative (breaking changes require version bump + golden regeneration)

## Path B: Conservatism-First Semantics

The kernel implements **Path B (conservatism-first)** ambiguity resolution. This is a non-negotiable semantic contract.

### Scoring as Cost (Lower Wins)

- **Formula**: `cost = base + penalty`
  - `base = len(intent_summary) + 10 * len(assumptions)`
  - `penalty = 5 * (duplicate_occurrences - 1)` for each assumption that appears in multiple interpretations
- **Sort Direction**: **Ascending** (lower cost wins, fewer assumptions preferred)
- **Semantics**:
  - Fewer assumptions → lower base → lower cost → **preferred** ✅
  - Duplicates → higher penalty → higher cost → **less preferred** ✅
  - Shorter summaries → lower base → lower cost → **preferred** ✅

### Golden Invariant

**SimpleCalc** (less assumptive) must always win over **AdvancedCalc** (more assumptive) for the golden fixture seed, without regenerating fixtures. This locks the "refusal over guessing" philosophy.

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
