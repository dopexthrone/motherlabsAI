# Motherlabs Intent (Pinned Target)

**This is the missing "Motherlabs intent context" for Cursor sessions.**

Paste this at the top of Cursor sessions before generating code/spec updates. It's compact, pinned, and mechanically oriented.

## Motherlabs Kernel Intent (Pinned Target)

We are building a **deterministic authority kernel** for autonomous context engineering. It takes an ambiguous human seed prompt and autonomously produces a committed context graph (DAG) and downstream artifacts (BlueprintSpec, BuildPlan, VerificationPack), with full traceability from seed to output via SHA-256.

**LLMs and retrieval are non-authoritative:** they may propose interpretations/plans/diffs, but the kernel alone decides and commits. The system must refuse rather than guess when it cannot converge within policy budgets. Runs must be replay-deterministic by recording all proposals and evaluation results into an append-only, hash-chained evidence ledger.

## Non-Goals (for the kernel core)

- Not building a web UI or CLI in this phase
- Not claiming formal proof like seL4; we adopt microkernel discipline (small TCB, strict boundaries) but formal verification is a later program
- Not "unlimited memory" as a magical feature; memory is externalized storage with explicit retention/compaction policy outside kernel
- Not allowing the kernel to execute arbitrary code or perform external side effects. Any execution happens in a sandbox runner outside the kernel boundary

## Core Concepts and Definitions

- **Seed**: a short ambiguous prompt (human-like)
- **Pin**: a minimal "north star" constraint set that prevents goal drift
- **SeedPack**: {seed_text, pin, policy, run_id, ts_base}
- **Proposal**: any untrusted output from LLM/retrieval/runner. Must be JSON-safe and canonically hashed
- **Commit**: kernel-authored acceptance of a proposal or a kernel-derived state transition
- **Evidence Ledger**: append-only hash-chained records enabling traceability and replay
- **DAG**: authoritative context state (nodes/edges) with invariants
- **Convergence**: deterministic scoring/pruning/collapse under budgets
- **Refusal**: required output mode when convergence or verification fails

## Kernel Invariants (must always hold)

1. **Deterministic replay**: SeedPack + recorded proposals + kernel code => identical DAG + artifacts + summary hash
2. **Authority separation**: only kernel can commit authoritative state
3. **Evidence completeness**: every proposal, decision, and proof signal is recorded and hash-linked
4. **Refusal over guessing**: if uncertain or over budget, refuse with reasons
5. **No hidden nondeterminism**: no system clock, no random, no unordered iteration; all ordering rules explicit

## Acceptance Criteria (kernel core)

- Ledger validates hash chain; any tampering breaks validation
- Replay reconstructs identical state and artifacts from ledger
- Ambiguous prompt is resolved autonomously via interpretation branching + deterministic collapse
- Golden fixtures lock determinism (expected summary hash + expected artifact hashes + small structural checks)

## Seeds Strategy (do not confuse these)

- **Golden unit seed**: small test seed (e.g., "build a calculator") used to lock deterministic mechanics
- **Integration seed**: Motherlabs seed (e.g., "build a deterministic context-engineering kernel that can bootstrap itself into a spec+plan+verify pipeline") used to test real intent. Pin is what constrains evolution, not seed verbosity

## Example Motherlabs Seed (ambiguous, human-like)

"I want a system that can take a vague idea and turn it into a rigorous, replayable blueprint and plan—without forgetting what it's building. It should keep track of decisions, refuse when it can't be certain, and be able to rebuild the same result from the same starting point."

## Example Pin (north star constraints)

- Deterministic authority kernel
- Proposal/commit boundary
- Evidence ledger + replay
- DAG state + invariants
- BlueprintSpec + VerificationPack (BuildPlan later if self-build enabled)
- No HITL during a run
- LLM only as proposer, never as authority

## How to Use This in Cursor

- Any code produced must preserve the authority boundary
- Any addition of LLM calls must be behind a proposer adapter and recorded for replay
- Any change to canonicalization, hashing, or collapse semantics requires regenerating golden fixtures
