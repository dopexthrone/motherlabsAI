# Kernel-Correct Guidelines

## 1. What "Autonomous" Means Here

**"Autonomous" does not mean "the system guesses correctly without help."**

It means: **once a run starts, the kernel performs all decisions (select/prune/accept/reject/commit/refuse) without human input.**

Any probabilistic generation can exist only as **untrusted proposals**, recorded in the ledger, replayable, and never directly committed.

**Autonomy is enforced by:**
- Deterministic decision logic (scoring, pruning, tie-break, verification)
- Policy budgets (max nodes/steps/depth, contradiction budget, retry caps)
- Refusal over guessing
- Full evidence chain (hash-chained ledger) enabling deterministic replay

## 2. The Authority Boundary (Non-Negotiable)

There are only two classes of outputs:

### A) Proposals (Untrusted)
Produced by anything probabilistic or non-authoritative:
- LLM outputs (interpretations, summaries, build steps, diffs)
- Retrieval outputs (snippets, vector search results)
- Sandbox runner outputs (test logs, static analysis results)

**Proposals may be logged, scored, compared, rejected, or accepted, but never become state by themselves.**

### B) Commits (Authoritative)
Produced only by the kernel:
- Selection of a single intent root
- Creation of authoritative DAG nodes/edges
- Acceptance/rejection decisions
- Accepted diffs (if self-build is enabled)
- Final artifacts (BlueprintSpec / BuildPlan / VerificationPack / RefusalReport) but only after verification

**Rule: The kernel is the only writer of authoritative state.**

## 3. Determinism is End-to-End, Not Local

It is not enough that scoring/pruning is deterministic. **The whole run must be replay-deterministic.**

**Therefore:**
- If a proposer is live (LLM), its outputs must be recorded to the ledger as Proposal records
- Replay runs must use the recorded proposals, not re-call the LLM
- Any environment-dependent validation (tests, type checks) must be performed by a sandbox runner whose outputs are recorded and replayed

**Deterministic replay definition:**
Same SeedPack + same recorded proposals + same kernel code + same policy => same committed DAG + same artifacts + same summary hash.

## 4. Autonomous Ambiguity Resolution (Current Capability)

The kernel can already resolve ambiguity without HITL if it has candidate interpretations.

**Pipeline:**
```
SeedPack -> Proposer returns Proposal[List[Interpretation]] 
-> Kernel scoring -> Kernel pruning -> Kernel collapse -> Kernel commit
```

**Important clarification:**
- The "autonomy" is in the kernel's decision steps
- The proposer is not required to be deterministic in real time, but its output must be recorded for replay
- Without recording, overall behavior is nondeterministic

## 5. Scoring, Pruning, Collapse (Kernel-Owned Semantics)

Scoring/pruning/collapse are kernel semantics. Treat them like compiler rules.

**Requirements:**
- Score must be a deterministic function of the proposal content + policy
- Tie-break must be deterministic (lexicographic is fine)
- Pruning must be deterministic (stable sort + explicit criteria)
- Collapse selects the winner deterministically

**Versioning rule:**
Any change to scoring/pruning/collapse semantics is a breaking change. It must:
- bump kernel semantic version
- regenerate golden fixtures intentionally
- record the change in VERSIONING.md

## 6. Contradictions and Cycle Constraints (DAG Rules)

- "depends_on" and "refines" edges must remain acyclic
- "contradicts" edges are allowed to form cycles because they represent conflict, not derivation
- All edges must reference existing nodes
- **Decide explicitly whether self-contradiction edges (from==to) are allowed. Default should be "reject" unless you have a use case.**

## 7. Refusal is Mandatory, Not Optional

Refusal is an expected output mode, not a failure. If the kernel cannot safely converge, it must refuse and record why.

**Refusal conditions should include (minimum):**
- No interpretations proposed
- Policy budgets exceeded before selecting an intent root
- Contradiction budget exceeded
- Verification cannot prove invariants (for self-build steps)

**RefusalReport must include:**
- reason codes
- evidence record hashes
- what policy knob or input would be required to proceed (deterministic templates only)

## 8. "Self-Proposing Implementations" (Next Level) — Corrected Architecture

You don't jump from BlueprintSpec to "kernel generates build steps and executes them." Kernel correctness requires separating three roles:

### Role 1: Kernel (Authoritative)
- commits BlueprintSpec
- commits BuildPlan (after verification)
- verifies diff proposals against BuildPlan + invariants + runner results
- commits accepted diffs
- produces VerificationPack

### Role 2: Executor (Non-Authoritative Proposer)
- reads committed BuildPlan
- proposes diffs as Proposal[Diff]
- can learn from rejection, but learning is outside kernel

### Role 3: Runner (Non-Authoritative Evaluator in Sandbox)
- applies proposed diffs in an isolated workspace
- runs deterministic checks (lint/typecheck/tests/static analysis)
- returns Proposal[RunResult] (outputs/logs summarized deterministically)
- all results recorded to ledger

**Critical correction:**
If BuildPlan generation involves creativity or LLM work, it is a **Proposal first**. The kernel commits BuildPlan only after it passes deterministic verification rules (structure, step constraints, dependency DAG validity, safety constraints, budgets, pin alignment).

## 9. BuildPlan Correctness Constraints (Kernel-Verifiable)

BuildPlan must be defined so the kernel can verify it mechanically:

- Each step has an id, action type, target path, dependency ids, and expected outputs/hashes
- Dependencies form an acyclic plan graph
- Global invariants listed explicitly
- Each step declares what evidence proves it (e.g., runner check must pass)
- Safety constraints are explicit (no network, no exec, no dangerous modules, write roots only)

## 10. Diff Representation Must be Hash-Anchored

**Do not use line-number change lists as the authoritative diff format. It is too fragile.**

**Use one of:**
- Unified diff text (canonical newline and path format)
- Full-file replacement (after_content + after_hash, plus optional before_hash)
- Patch object with content hashes per hunk

**Minimum requirement:**
Every proposed change must include content hashes so kernel verification is deterministic and resistant to drift.

## 11. The Self-Build Loop (Kernel-Correct)

1. Kernel commits BlueprintSpec
2. Proposer proposes BuildPlan (or kernel deterministically derives BuildPlan)
3. Kernel verifies BuildPlan and commits it
4. For each BuildStep:
   - Executor proposes Diff (Proposal[Diff])
   - Runner evaluates Diff in sandbox (Proposal[RunResult])
   - Kernel verifies: step match + deps satisfied + invariants proven by RunResult
   - Kernel commits accepted diff (or rejects with reason codes)
5. Final: Kernel emits VerificationPack containing summary hash and replay instructions
6. Replay proves identical acceptance decisions and identical final artifact hashes

## 12. Why This Eliminates Your Guessing

Because:
- The kernel commits a plan
- The executor proposes implementations against that plan
- The runner provides proof signals
- The kernel accepts/rejects mechanically and logs the full trail

**You are not inventing steps or deciding correctness during the run.**
