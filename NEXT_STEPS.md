# Next Steps: Building Around the Frozen Core

The deterministic engine is complete. The kernel is **FROZEN** (see `KERNEL_FREEZE.md`).

All future development must build **around** the core, not modify it. This document outlines the adapter architecture.

## 1. Freeze the Core ✅

**Status:** COMPLETE

The core is frozen at version 0.1.0. See `KERNEL_FREEZE.md` for details.

## 2. Add Adapters (Not Features)

### LLM Adapter

**Principle:** Don't add LLMs to the engine. Add an adapter that implements `Proposer`.

**Implementation:**
- Create `src/motherlabs_kernel/adapters/llm_proposer.py`
- Implements `Proposer` protocol
- Calls external LLM API (OpenAI, Anthropic, etc.)
- Returns `Proposal[List[Interpretation]]`
- **Must be JSON-safe** (no NaN, no datetimes)

**Recorded Mode Wrapper:**
- Create `src/motherlabs_kernel/adapters/recorded_wrapper.py`
- Wraps any `Proposer` and records all proposals
- Enables deterministic replay by reusing recorded proposals
- Every live run can be replayed deterministically

**Example:**
```python
# Live run
llm_proposer = LLMProposer(api_key="...")
recorded = RecordedWrapper(llm_proposer)
result = run_engine(..., proposer=recorded, ...)

# Replay run
recorded_proposer = RecordedProposer(recorded.get_recordings())
result2 = run_engine(..., proposer=recorded_proposer, ...)
# Should produce identical results
```

## 3. Add Retrieval as Proposal Supplier (Optional, Later)

**Principle:** Same adapter pattern - retrieval returns `Proposal[snippets]`.

**Implementation:**
- Create `src/motherlabs_kernel/adapters/retrieval_proposer.py`
- Implements `Proposer` protocol
- Queries vector DB (LanceDB, Pinecone, etc.) - **outside kernel boundary**
- Returns `Proposal[List[Snippet]]` where Snippet is JSON-safe
- Kernel decides admissibility and commits only hashed, canonicalized snippets

**Architecture:**
```
┌─────────────────────────────────────┐
│  Kernel (Frozen)                   │
│  - Proposer interface               │
│  - Proposal → Commit boundary       │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐    ┌───────▼────────┐
│ LLM Adapter│    │Retrieval Adapter│
│ (outside)  │    │ (outside)       │
└────────────┘    └─────────────────┘
                         │
                  ┌──────▼──────┐
                  │ Vector DB   │
                  │ (LanceDB)   │
                  │ (outside)   │
                  └─────────────┘
```

## 4. Add Real Artifact Pipeline

**Current State:** Toy `BlueprintSpec` with stub fields.

**Target State:** Structured, buildable artifacts.

### Enhanced BlueprintSpec

```python
class BlueprintSpec:
    run_id: str
    seed_hash: str
    intent_root_node_id: str
    pinned_target: dict
    invariants: List[str]
    
    # NEW: Real structure
    module_contracts: List[ModuleContract]  # Not stub
    dependency_graph: DependencyGraph       # From DAG
    test_plan: TestPlan                     # Generated tests
    acceptance_criteria: List[Criterion]    # Success conditions
```

### BuildPlan

```python
class BuildPlan:
    steps: List[BuildStep]
    dependencies: Dict[str, List[str]]
    verification_checkpoints: List[Checkpoint]
```

### Enhanced VerificationPack

```python
class VerificationPack:
    ledger_last_hash: str
    dag_root_hash: str
    artifact_hashes: Dict[str, str]
    expected_summary_hash: str
    replay_instructions: str
    
    # NEW: Real verification
    test_results: TestResults
    build_verification: BuildVerification
    acceptance_status: AcceptanceStatus
```

**Implementation:**
- Extend `artifacts_blueprint.py` with real structures
- Generate from DAG structure
- Keep deterministic (same DAG → same artifacts)

## 5. Add Execution Boundary (Only If Truly Want Self-Building)

**Warning:** Don't add executor until blueprint pipeline is strong, or you'll get "autonomous chaos."

**Architecture:**
```
┌─────────────────────────────────────┐
│  Kernel (Frozen)                    │
│  - Emits BuildPlan                   │
└──────────────┬──────────────────────┘
               │
        ┌──────▼──────┐
        │ Executor    │
        │ (Service)   │
        │ - Sandboxed │
        │ - Proposes  │
        │   diffs     │
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │ Kernel      │
        │ - Verifies  │
        │ - Accepts/  │
        │   Rejects   │
        │ - Logs all  │
        └─────────────┘
```

**Flow:**
1. Kernel emits `BuildPlan`
2. Executor proposes changes (diffs) as `Proposal[Diff]`
3. Kernel verifies and accepts/rejects
4. All changes are hashed, logged, replayable

**Requirements:**
- Executor is **outside kernel boundary**
- All proposals go through kernel verification
- Nothing is committed without kernel approval
- Full audit trail in ledger

## 6. Prove Dogfooding with One Golden Run

**Goal:** "Build the kernel" - kernel builds itself.

**Process:**
1. Pick pinned seed: `"build the kernel"`
2. Run with recorded proposals
3. Output must reproduce:
   - The kernel spec of itself (self-description)
   - The build plan to recreate itself
   - A verification pack that validates the recreated output against the golden

**Success Criteria:**
- Golden run produces kernel specification
- Build plan can recreate the kernel
- Verification pack validates recreated kernel matches golden
- Replay produces identical results

**This is the first credible "bootstraps a kernel to build a kernel" milestone.**

## Implementation Order

1. ✅ Freeze core (DONE)
2. Add LLM adapter + recorded wrapper
3. Test adapter with golden run
4. Enhance BlueprintSpec structure
5. Add BuildPlan generation
6. Enhance VerificationPack
7. (Optional) Add retrieval adapter
8. (Optional) Add execution boundary
9. Prove dogfooding with self-building golden run

## Key Principles

1. **Kernel is frozen** - no changes without version bump
2. **Adapters, not features** - all external systems are adapters
3. **Proposal boundary** - nothing authoritative without kernel commit
4. **Deterministic replay** - every run can be replayed
5. **Golden fixtures lock** - permanent determinism guarantee

---

**Build around the core. Don't contaminate it.**
