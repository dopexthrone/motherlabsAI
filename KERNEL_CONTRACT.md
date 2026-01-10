# Kernel Contract (Invariants, Interfaces, Acceptance Tests)

**Version:** 0.1.0  
**Status:** Normative  
**Scope:** Kernel core engine library (pure, in-memory)

## 1. Contract Summary

The kernel is a deterministic authority core that:
1. Accepts SeedPack inputs (seed_text + pin + policy + run_id + ts_base)
2. Consumes only Proposals from external systems (LLM/retrieval/runner)
3. Deterministically commits an intent root and a context DAG
4. Emits artifacts (BlueprintSpec + VerificationPack) or RefusalReport
5. Records every step in a hash-chained evidence ledger
6. Replays deterministically from recorded evidence

## 2. Public Interfaces (Normative)

These are kernel-level interfaces; implementations may vary, but semantics must not.

### 2.1 Canonicalization + Hashing
- `canonicalize(value) -> bytes`
- `sha256_hex(data: bytes|str) -> str`
- `hash_canonical(value) -> str`

**Requirements:**
- JSON-safe values only; reject NaN/Inf/unsupported types
- Stable key ordering; no whitespace
- UTF-8 bytes

### 2.2 Evidence Ledger (In-Memory)
- `Ledger.append(ts: str, kind: str, payload: JSON) -> EvidenceRecord`
- `validate_chain(records: list[EvidenceRecord]) -> None (raises on failure)`

**EvidenceRecord v1:**
- `v=1`
- `ts, kind, parent, payload, payload_hash, record_hash`
- Hash formulas are governed by kernel version

### 2.3 Policy
**Policy fields (minimum):**
- `max_interpretations >= 1`
- `max_nodes >= 1`
- `max_depth >= 1`
- `contradiction_budget >= 0`
- `max_steps >= 1`
- `deterministic_tiebreak = "lexicographic"`

**Kernel must:**
- validate policy deterministically
- implement deterministic tie-break

### 2.4 Proposer Boundary (External)
**Kernel consumes:**
- `Proposal[source, confidence?, value, proposal_hash]`

**Normative proposer interface for interpretations:**
- `propose_interpretations(seed_hash: str, n: int) -> Proposal[list[Interpretation]]`

**Interpretation (JSON-safe):**
- `name: str`
- `assumptions: list[str]`
- `intent_summary: str`

**Rule:**
- Proposer can be live/nondeterministic, but its outputs must be recorded to ledger for replay

### 2.5 DAG (Authoritative State)
**Node:**
- `id: sha256 hex`
- `kind: seed|interpretation|assumption|claim|decision|artifact`
- `payload, payload_hash`

**Edge:**
- `id: sha256 hex`
- `kind: depends_on|refines|contradicts`
- `from_id, to_id`

**Deterministic IDs:**
- node: `sha256(canonical({t:"node", run_id, kind, payload_hash}))`
- edge: `sha256(canonical({t:"edge", run_id, kind, from, to}))`

**Invariants:**
- edges reference existing nodes
- no cycles for depends_on/refines
- contradict edges excluded from cycle constraint

### 2.6 Engine Run
- `run_engine(run_id, seed_text, pin, policy, proposer, ts_base, ...) -> RunResult`

**RunResult must include:**
- `records: list[EvidenceRecord]`
- `dag: DAG`
- `artifacts: dict[str, JSON]`
- `summary_hash: str`

**Summary hash must be deterministic:**
- `summary_hash = hash_canonical({ledger_last_hash, dag_root_hash, artifact_hashes})`

**Artifact hashes:**
- `artifact_hashes[name] = hash_canonical(artifact_payload)`

**DAG root hash:**
- `dag_root_hash = hash_canonical({sorted_node_ids, sorted_edge_ids})`

### 2.7 Replay
- `replay(records: list[EvidenceRecord]) -> ReplayResult`

**Replay must:**
- validate chain
- reconstruct DAG + artifacts
- recompute summary_hash identically

## 3. Mandatory Outcomes

The engine must produce exactly one of:
- **Success**: BlueprintSpec + VerificationPack
- **Refusal**: RefusalReport

**RefusalReport must include:**
- `run_id, seed_hash`
- `reason_codes: list[str]`
- `evidence_record_hashes: list[str]`
- `policy_suggestions: list[str]` (deterministic templates)
- `status: "refused"`

## 4. Acceptance Tests (Must Pass)

### 4.1 Hashing and canonicalization
- Same semantic JSON -> same bytes -> same hash (key order invariance)
- Unsupported types rejected
- NaN/Inf rejected

### 4.2 Ledger integrity
- Parent linkage correct
- Tampering with any record field breaks validation
- Payload changes break validation (via payload_hash mismatch)

### 4.3 DAG invariants
- Cycles in depends_on/refines rejected
- Contradict cycles allowed
- Missing node references rejected
- Deterministic IDs stable regardless of insertion order

### 4.4 Ambiguity resolution determinism
Given recorded interpretations:
- scoring deterministically produces same scores
- pruning deterministically selects top-K
- collapse deterministically selects winner
- committed intent root is stable

### 4.5 End-to-end determinism (Run + Replay)
- `run_engine` produces records, DAG, artifacts, summary_hash
- `replay(records)` reproduces identical DAG root hash, artifact hashes, summary_hash
- Tampered records cause replay failure

### 4.6 Golden fixtures
A golden fixture must lock:
- expected summary hash
- expected ledger last hash
- expected DAG root hash
- expected artifact hashes
- minimal structure checks:
  - chosen interpretation name
  - node count and edge count
  - node kinds multiset

## 5. Change Control

**Breaking changes (major bump + regenerate goldens + document):**
- canonicalization / hashing
- ledger fields or hash formulas
- DAG id formulas or invariants
- scoring/pruning/collapse semantics
- replay semantics
- artifact schemas that affect hashes

**Non-breaking changes (minor bump):**
- adding new artifact fields that do not affect existing hash computation rules (only if explicitly excluded—by default, artifact hash includes full payload, so schema changes are breaking unless carefully versioned)

## 6. Motherlabs Intent (Pinned Context)

**Pinned target for kernel evolution:**
- Deterministic authority kernel for autonomous context engineering
- Proposal/commit separation (LLM/retrieval/runner are non-authoritative)
- Evidence ledger + deterministic replay
- DAG with invariants
- Autonomous ambiguity handling (no HITL during a run)
- Refusal over guessing
- Artifacts: BlueprintSpec + VerificationPack (BuildPlan and self-apply loop later, behind execution boundary)

**Non-goals for kernel core:**
- UI/CLI, database, "unlimited memory," formal proof claims, direct execution, external side effects
