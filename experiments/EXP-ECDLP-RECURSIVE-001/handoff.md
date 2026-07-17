## Handoff: Recursive expansion pre-run review

### Claim or task

Audit whether the frozen recursive coordinate-support experiment soundly measures exact final expansion, witness-bearing split advice, first-witness online work, and matched construction cost before any canonical run.

### Status

OPEN

### Assumptions

- Generated curves are ordinary and prime order, and subgroup order increases across each seeded size schedule.
- Exact finite support, not Poisson occupancy, determines target coverage.
- The split compiler is a preflight subproblem; rank, linear algebra, and target descent remain future gates.
- CPython deep-size measurements are implementation-specific and must be interpreted only within the recorded environment.

### Evidence so far

- `recursive_expansion.py` SHA-256: `f17cb9d63eca4473d0b3ab15563a233f3252449a7d599bf1f468577a64b54275`.
- `verify_recursive_expansion.py` SHA-256: `6107a381d654affb8a28dde80794a71bce9f9d088ee35a899f5477d836bfb0e0`.
- The independent verifier pins and reconstructs the generator source hash.
- A reduced noncanonical integration sweep is deterministic and passes exact independent replay.
- All eight repository tests pass; the verifier's 13-case self-test passes.
- All 13 checked-in experiment records validate against repository schemas.

### Failure modes

- The random-x path may still fail to match a coordinate family's exact candidate-order or fiber-selection semantics.
- Diagnostic full-support enumeration could be mistaken for compiler cost despite separate counters.
- Deep-byte accounting may omit allocator or cache effects and is not portable across Python runtimes.
- The success gate may reward toy finite-size effects that do not persist with `q`.
- A preflight promotion could be overread despite the explicit no-break boundary.

### Next concrete action

Have a separate red-team agent issue `GO`, `REVISE`, or `NO-GO` after checking the frozen config, source hashes, exact sign/cancellation model, first-witness stopping rule, functional advice bytes, random-x fairness, monotone multi-seed schedule, promotion logic, and verifier independence. Do not approve or launch before that verdict.

### Artifact paths

- `experiments/EXP-ECDLP-RECURSIVE-001/specification.json`
- `experiments/EXP-ECDLP-RECURSIVE-001/contract.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/candidate-checklist.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/src/recursive_expansion.py`
- `experiments/EXP-ECDLP-RECURSIVE-001/src/verify_recursive_expansion.py`
- `research_ledger.md`
