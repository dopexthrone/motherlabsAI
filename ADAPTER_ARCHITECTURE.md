# Adapter Architecture

This document outlines how to build adapters around the frozen kernel core.

## Core Principle

**The kernel is frozen. Build adapters, not features.**

All external systems (LLMs, vector DBs, executors) are implemented as adapters that conform to kernel interfaces. The kernel never directly calls external systems.

## Adapter Pattern

### Interface: Proposer

All adapters implement the `Proposer` protocol:

```python
class Proposer(Protocol):
    def propose_interpretations(self, seed_hash: str, n: int) -> Proposal[List[Interpretation]]:
        ...
```

### Key Requirements

1. **JSON-Safe Output**: All proposal values must be JSON-safe (no NaN, no datetimes, etc.)
2. **Deterministic Hashing**: Equivalent proposals must hash identically (uses canonicalization)
3. **Never Authoritative**: Proposals are suggestions; only kernel commits are authoritative

## Adapter Types

### 1. LLM Adapter

**Location:** `src/motherlabs_kernel/adapters/llm_proposer.py` (to be created)

**Purpose:** Wraps LLM API calls to generate interpretations.

**Implementation:**
```python
class LLMProposer:
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def propose_interpretations(self, seed_hash: str, n: int) -> Proposal[List[Interpretation]]:
        # Call LLM API
        # Parse response
        # Ensure JSON-safe
        # Return Proposal
        ...
```

**Important:**
- LLM calls happen **outside kernel boundary**
- All responses must be validated as JSON-safe
- Errors should return empty proposal (triggers refusal)

### 2. Recorded Wrapper

**Location:** `src/motherlabs_kernel/adapters/recorded_wrapper.py` (to be created)

**Purpose:** Wraps any proposer and records all proposals for deterministic replay.

**Implementation:**
```python
class RecordedWrapper:
    def __init__(self, proposer: Proposer):
        self.proposer = proposer
        self.recordings = {}
    
    def propose_interpretations(self, seed_hash: str, n: int) -> Proposal[List[Interpretation]]:
        # Record key
        key = f"interpretations:{seed_hash}:{n}"
        
        # Call wrapped proposer
        proposal = self.proposer.propose_interpretations(seed_hash, n)
        
        # Record proposal
        self.recordings[key] = proposal.value
        
        return proposal
    
    def get_recordings(self) -> Dict[str, Any]:
        """Get recordings for RecordedProposer."""
        return self.recordings
```

**Usage:**
```python
# Live run with recording
llm_proposer = LLMProposer(api_key="...")
recorded = RecordedWrapper(llm_proposer)
result = run_engine(..., proposer=recorded, ...)

# Save recordings
with open("recordings.json", "w") as f:
    json.dump(recorded.get_recordings(), f)

# Replay with recorded proposals
with open("recordings.json", "r") as f:
    recordings = json.load(f)
recorded_proposer = RecordedProposer(recordings)
result2 = run_engine(..., proposer=recorded_proposer, ...)
# Should produce identical results
```

### 3. Retrieval Adapter (Optional, Later)

**Location:** `src/motherlabs_kernel/adapters/retrieval_proposer.py` (to be created)

**Purpose:** Queries vector DB and returns relevant snippets as proposals.

**Implementation:**
```python
class RetrievalProposer:
    def __init__(self, vector_db: Any):  # LanceDB, Pinecone, etc.
        self.db = vector_db  # Outside kernel boundary
    
    def propose_interpretations(self, seed_hash: str, n: int) -> Proposal[List[Interpretation]]:
        # Query vector DB
        # Convert snippets to interpretations
        # Ensure JSON-safe
        # Return Proposal
        ...
```

**Important:**
- Vector DB is **outside kernel boundary**
- Snippets must be JSON-safe
- Kernel decides admissibility

## Adapter Directory Structure

```
src/motherlabs_kernel/
├── adapters/              # NEW: Adapter layer
│   ├── __init__.py
│   ├── llm_proposer.py    # LLM adapter
│   ├── recorded_wrapper.py # Recording wrapper
│   └── retrieval_proposer.py # Retrieval adapter (future)
├── ...                    # Frozen core (unchanged)
```

## Testing Adapters

### Unit Tests

Test each adapter independently:
- `tests/adapters/test_llm_proposer.py`
- `tests/adapters/test_recorded_wrapper.py`

### Integration Tests

Test adapters with kernel:
- `tests/integration/test_llm_adapter_integration.py`
- Verify proposals are JSON-safe
- Verify replay works with recorded proposals

## Error Handling

Adapters should handle errors gracefully:

1. **LLM API errors**: Return empty proposal (triggers refusal)
2. **Parsing errors**: Return empty proposal (triggers refusal)
3. **JSON-safety violations**: Reject and return empty proposal

**Never crash the kernel.** Adapters fail gracefully, kernel refuses.

## Versioning

Adapters are **not frozen**. They can be modified freely:
- Add new adapters
- Improve error handling
- Add features
- Change implementations

**Only the kernel core is frozen.**

## Example: Complete Adapter Flow

```python
# 1. Create LLM adapter
llm = LLMProposer(api_key=os.getenv("OPENAI_API_KEY"))

# 2. Wrap with recording
recorded = RecordedWrapper(llm)

# 3. Run engine
result = run_engine(
    run_id="run_001",
    seed_text="Build a calculator",
    pin={"target": "calculator"},
    policy=Policy(...),
    proposer=recorded,  # Uses adapter
    ts_base="T000000"
)

# 4. Save recordings for replay
with open("recordings.json", "w") as f:
    json.dump(recorded.get_recordings(), f)

# 5. Replay deterministically
with open("recordings.json", "r") as f:
    recordings = json.load(f)
replay_proposer = RecordedProposer(recordings)
replay_result = run_engine(
    run_id="run_001",
    seed_text="Build a calculator",
    pin={"target": "calculator"},
    policy=Policy(...),
    proposer=replay_proposer,
    ts_base="T000000"
)

# Should produce identical results
assert result.ledger_records[0].record_hash == replay_result.ledger_records[0].record_hash
```

---

**Build adapters. Keep the core frozen.**
