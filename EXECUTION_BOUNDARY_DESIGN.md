# Execution Boundary Design: How Engine Proposes Its Own Implementations

## The Problem

You're currently "in the loop" to propose implementations. The engine produces a `BlueprintSpec`, but you have to guess:
- What modules to create?
- What functions to implement?
- What tests to write?
- What dependencies to add?

**This is wrong.** The engine should propose its own implementations safely.

## The Solution: Execution Boundary (Kernel-Correct)

### Architecture (Three Roles)

```
┌─────────────────────────────────────────────────────┐
│  ROLE 1: KERNEL (Authoritative)                    │
│  - Commits BlueprintSpec                           │
│  - Commits BuildPlan (after verification)          │
│  - Verifies Diff Proposals                         │
│  - Verifies Runner Results                         │
│  - Commits Only Verified Changes                    │
└──────────────┬──────────────────────────────────────┘
               │
               │ BuildPlan (committed)
               ▼
┌─────────────────────────────────────────────────────┐
│  ROLE 2: EXECUTOR (Non-Authoritative Proposer)      │
│  - Reads committed BuildPlan                       │
│  - Proposes Diffs as Proposal[Diff]                │
│  - Can learn from rejections (outside kernel)       │
└──────────────┬──────────────────────────────────────┘
               │
               │ Proposal[Diff]
               ▼
┌─────────────────────────────────────────────────────┐
│  ROLE 3: RUNNER (Non-Authoritative Evaluator)       │
│  - Applies diff in isolated sandbox                │
│  - Runs deterministic checks                      │
│  - Returns Proposal[RunResult]                      │
│  - All results recorded to ledger                   │
└──────────────┬──────────────────────────────────────┘
               │
               │ Proposal[RunResult]
               ▼
┌─────────────────────────────────────────────────────┐
│  KERNEL VERIFICATION (Autonomous)                   │
│  - Validates diff against BuildPlan                 │
│  - Checks invariants proven by RunResult            │
│  - Verifies safety                                  │
│  - Accepts or Rejects                               │
└──────────────┬──────────────────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
    ACCEPTED      REJECTED
        │             │
        ▼             ▼
┌──────────────┐ ┌──────────────┐
│ Commit Diff  │ │ RefusalReport│
│ to Ledger     │ │ (with reasons)│
└──────────────┘ └──────────────┘
```

**Critical Correction:**
- BuildPlan generation (if involving LLM/creativity) is a **Proposal first**
- Kernel verifies BuildPlan deterministically before committing
- Diff representation must be **hash-anchored** (not line numbers)

## Implementation Plan

### Phase 1: Enhanced BuildPlan Generation

**File:** `src/motherlabs_kernel/artifacts_buildplan.py` (to be created)

```python
class BuildStep:
    """A single step in the build plan."""
    id: str
    action: Literal["create_module", "create_function", "create_test", "add_dependency"]
    target: str  # File path
    content: str  # Code/content
    dependencies: List[str]  # Step IDs that must complete first
    invariants: List[str]  # Invariants this step must satisfy

class BuildPlan:
    """Step-by-step build instructions."""
    steps: List[BuildStep]
    invariants: List[str]  # Global invariants
    verification_checkpoints: List[Checkpoint]
    
    def generate_from_blueprint(self, blueprint: BlueprintSpec, dag: DAG) -> BuildPlan:
        """Generate BuildPlan from BlueprintSpec and DAG."""
        # Autonomous generation:
        # 1. Analyze DAG structure
        # 2. Determine module boundaries
        # 3. Generate function signatures
        # 4. Generate test plans
        # 5. Determine dependencies
        # 6. Create step-by-step plan
        ...
```

### Phase 2: Diff Proposal Structure (Hash-Anchored)

**File:** `src/motherlabs_kernel/artifacts_diff.py` (to be created)

**Critical:** Diff representation must be hash-anchored, not line-number based.

```python
class Diff:
    """A proposed code change (hash-anchored)."""
    step_id: str  # Which BuildStep this implements
    file_path: str
    
    # Hash-anchored representation (choose one):
    # Option 1: Full-file replacement
    after_content: str
    after_hash: str  # hash_canonical(after_content)
    before_hash: Optional[str]  # If modifying existing file
    
    # Option 2: Unified diff text (canonical format)
    unified_diff: str
    diff_hash: str  # hash_canonical(unified_diff)
    
    # Option 3: Patch with content hashes per hunk
    hunks: List[Hunk]
    # Each hunk has: before_hash, after_hash, content
    
    metadata: Dict[str, Any]  # Additional context
```

**Minimum requirement:** Every proposed change must include content hashes so kernel verification is deterministic and resistant to drift.

### Phase 3: Executor and Runner Interfaces

**File:** `src/motherlabs_kernel/executor_types.py` (to be created)

```python
class Executor(Protocol):
    """Protocol for executors that propose implementations (Role 2)."""
    
    def propose_implementation(self, step: BuildStep) -> Proposal[Diff]:
        """Propose implementation for a build step."""
        ...
    
    def learn_from_rejection(self, rejection: RefusalReport) -> None:
        """Learn from kernel rejection to improve future proposals (outside kernel)."""
        ...

class Runner(Protocol):
    """Protocol for runners that evaluate diffs in sandbox (Role 3)."""
    
    def evaluate_diff(self, diff: Diff) -> Proposal[RunResult]:
        """
        Apply diff in isolated sandbox and run deterministic checks.
        
        Returns Proposal[RunResult] with:
        - test_results: pass/fail (deterministic)
        - lint_results: issues found (deterministic)
        - typecheck_results: type errors (deterministic)
        - static_analysis: safety checks (deterministic)
        - logs: summarized deterministically
        """
        ...
```

**Critical:** Runner outputs are Proposals, recorded to ledger for replay.

### Phase 4: Kernel Verification (With Runner Results)

**File:** `src/motherlabs_kernel/verification_diff.py` (to be created)

```python
def verify_diff_proposal(
    proposal: Proposal[Diff],
    run_result: Proposal[RunResult],  # From runner
    build_plan: BuildPlan,
    completed_steps: Set[str]
) -> Tuple[bool, List[str]]:
    """
    Verify a diff proposal against BuildPlan + runner results.
    
    Returns:
        (is_valid, reason_codes)
    """
    reasons = []
    
    # 1. Check step exists in plan
    step = build_plan.get_step(proposal.value.step_id)
    if not step:
        reasons.append("step_not_in_plan")
        return (False, reasons)
    
    # 2. Check dependencies satisfied
    for dep in step.dependencies:
        if dep not in completed_steps:
            reasons.append(f"dependency_not_satisfied:{dep}")
            return (False, reasons)
    
    # 3. Check invariants proven by runner results
    for invariant in build_plan.invariants:
        if not run_result.value.proves_invariant(invariant):
            reasons.append(f"invariant_not_proven:{invariant}")
            return (False, reasons)
    
    # 4. Check safety (from runner static analysis)
    if run_result.value.has_dangerous_operations():
        reasons.append("dangerous_operation_detected")
        return (False, reasons)
    
    # 5. Check required checks pass (from runner)
    if not run_result.value.all_checks_pass():
        reasons.append("required_checks_failed")
        return (False, reasons)
    
    # 6. Verify hash matches (hash-anchored verification)
    if not verify_diff_hash(proposal.value):
        reasons.append("hash_mismatch")
        return (False, reasons)
    
    # 7. Check content matches step expectations
    if not matches_step_content(proposal.value, step):
        reasons.append("content_mismatch")
        return (False, reasons)
    
    return (True, [])
```

**Critical:** Verification uses runner results (Proposal[RunResult]) to prove invariants, not just static analysis.

### Phase 5: Build Loop

**File:** `src/motherlabs_kernel/build_loop.py` (to be created)

```python
def execute_build_plan(
    build_plan: BuildPlan,
    executor: Executor,
    ledger: Ledger,
    dag: DAG
) -> RunResult:
    """
    Execute build plan with autonomous verification.
    
    This is the main loop that:
    1. Iterates through BuildPlan steps
    2. Executor proposes implementation
    3. Kernel verifies proposal
    4. If accepted: commit to ledger
    5. If rejected: executor learns and retries
    6. Continues until all steps complete or refusal
    """
    completed_steps = set()
    ts_base = "T000000"
    step_counter = 0
    
    for build_step in build_plan.steps:
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            # Executor proposes implementation
            proposal = executor.propose_implementation(build_step)
            
            # Record proposal
            ledger.append(
                generate_ts(ts_base, step_counter),
                "proposal",
                {"diff": proposal.value.model_dump()}
            )
            step_counter += 1
            
            # Kernel verifies (autonomous)
            is_valid, reasons = verify_diff_proposal(
                proposal, build_plan, completed_steps
            )
            
            if is_valid:
                # Accept and commit
                commit = Commit.create(proposal.value, accepted_from=proposal.proposal_hash)
                ledger.append(
                    generate_ts(ts_base, step_counter),
                    "commit",
                    {"diff": commit.value.model_dump()}
                )
                step_counter += 1
                completed_steps.add(build_step.id)
                break  # Move to next step
            else:
                # Reject and provide feedback
                refusal = RefusalReport(
                    run_id=build_plan.run_id,
                    seed_hash=build_plan.seed_hash,
                    reason_codes=reasons,
                    evidence_record_hashes=[ledger.get_last_hash()],
                    policy_suggestions=generate_policy_suggestions(reasons),
                    status="refused"
                )
                
                # Executor learns from rejection
                executor.learn_from_rejection(refusal)
                retry_count += 1
        
        if retry_count >= max_retries:
            # Too many failures, refuse entire build
            return RunResult(
                ledger_records=ledger.get_records(),
                dag_nodes=dag.get_nodes(),
                dag_edges=dag.get_edges(),
                artifacts={"refusal": refusal}
            )
    
    # All steps completed
    return RunResult(
        ledger_records=ledger.get_records(),
        dag_nodes=dag.get_nodes(),
        dag_edges=dag.get_edges(),
        artifacts={"build_complete": True}
    )
```

## Safety Mechanisms

### 1. Invariant Enforcement

```python
INVARIANTS = [
    "no_import_cycles",           # No circular imports
    "all_functions_have_tests",   # Every function has a test
    "type_hints_required",        # All functions have type hints
    "no_dangerous_operations",     # No eval, exec, etc.
    "dependencies_satisfied",     # All dependencies exist
]
```

### 2. Sandboxed Execution

- Executor runs in isolated environment
- No network access
- No filesystem access outside project
- No system calls

### 3. Deterministic Verification

- Same proposal → same verification result
- No randomness in verification
- Fully replayable

### 4. Full Audit Trail

- Every proposal logged
- Every decision logged
- Every commit logged
- Fully replayable

## Example Flow

```
1. Kernel generates BuildPlan:
   - Step 1: Create src/calculator/__init__.py
   - Step 2: Create src/calculator/arithmetic.py with add() function
   - Step 3: Create tests/test_arithmetic.py with test_add()

2. Executor proposes Step 1:
   Proposal: Create __init__.py with "# Calculator module"
   Kernel verifies: ✅ Matches plan, no dependencies, invariants OK
   Kernel commits: ✅ Recorded in ledger

3. Executor proposes Step 2:
   Proposal: Create arithmetic.py with:
     def add(a: int, b: int) -> int:
         return a + b
   Kernel verifies: ✅ Matches plan, dependency (Step 1) satisfied, invariants OK
   Kernel commits: ✅ Recorded in ledger

4. Executor proposes Step 3:
   Proposal: Create test_arithmetic.py with:
     def test_add():
         assert add(2, 3) == 5
   Kernel verifies: ✅ Matches plan, dependency (Step 2) satisfied, invariants OK
   Kernel commits: ✅ Recorded in ledger

5. Build complete: All steps verified and committed
```

## Why This Eliminates Your Guessing

**Before:**
- You guess what modules to create
- You guess what functions to implement
- You guess what tests to write
- You make assumptions that might be wrong

**After:**
- Engine produces BuildPlan (autonomous)
- Executor proposes implementations (autonomous)
- Kernel verifies proposals (autonomous)
- You're out of the loop ✅

## Next Steps

1. Implement `BuildPlan` generation from `BlueprintSpec`
2. Implement `Diff` proposal structure
3. Implement `Executor` interface
4. Implement kernel verification
5. Implement build loop
6. Test with golden run

---

**The engine will propose its own implementations safely, eliminating your guessing.**
