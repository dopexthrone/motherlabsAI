# Motherlabs Kernel

Engine-only, deterministic Python kernel for context engineering.

**Version:** 0.1.0 (FROZEN)  
**Status:** Core complete, ready for adapters

## Principles

- **Pure Functions**: No filesystem IO, no network calls, no system clock dependencies
- **Determinism**: Fixed inputs produce identical outputs
- **Evidence Ledger**: Hash-chained, append-only audit trail
- **Proposal vs Commit**: LLM proposals are never authoritative; only committed state is
- **Refusal over Guessing**: Kernel refuses when it cannot converge deterministically
- **Frozen Core**: Kernel boundary is frozen; build around it, not through it

## Development

```bash
pip install -e ".[test]"
pytest
```

## Architecture

The kernel is organized as a pure engine with:
- Canonical serialization and hashing
- Evidence ledger with hash chaining
- Policy-driven budgets and limits
- Authoritative DAG with invariants
- Autonomous ambiguity resolution
- Deterministic artifact generation

All IO (filesystem, network, CLI, web) is outside the engine boundary.

## Core Status

**The kernel core is FROZEN at version 0.1.0.**

See `KERNEL_FREEZE.md` for details on what is frozen and the version bump protocol.

## Next Steps

See `NEXT_STEPS.md` for the adapter architecture plan:
1. Add LLM adapter (implements Proposer interface)
2. Add recorded wrapper for deterministic replay
3. Enhance artifact pipeline (BlueprintSpec, BuildPlan)
4. (Optional) Add retrieval adapter
5. (Optional) Add execution boundary
6. Prove dogfooding with self-building golden run

## Documentation

- `KERNEL_FREEZE.md` - Frozen core boundary and version protocol
- `NEXT_STEPS.md` - Adapter architecture and future development
- `CHANGELOG.md` - Version history and breaking changes
