## Handoff: Recursive expansion pre-run review

### Claim or task

Launch the independently approved protocol `v2` generator as the first immutable run without changing audited source bytes or frozen parameters.

### Status

OBSERVATION

### Assumptions

- Generated curves are ordinary and prime order, and subgroup order increases across each seeded size schedule.
- Seeded field primes are constrained to `p mod 4 = 3`; this is disclosed special modulus structure used for deterministic square roots.
- Exact finite support, not Poisson occupancy, determines target coverage.
- The split compiler is a preflight subproblem; rank, linear algebra, and target descent remain future gates.
- CPython deep-size measurements are implementation-specific and must be interpreted only within the recorded environment.

### Evidence so far

- The `v1` draft at `b28b813` received `REVISE`; the exact audit SHA-256 is `8b6b3723f3198dcc607eb17b5937adab16f0305142a8ad67dd1fc484e3a933b7`.
- Protocol `v2` at `90ff031` received `GO`; the exact audit SHA-256 is `541e36ea90f0aeb6e0146f42efbe6b8760ca2d5f32806f781210efa324cd0690`.
- `recursive_expansion.py` `v2` SHA-256: `c8e6986dd48e341b3e585a170990a018210602f99fc6cd748b81902f1b4e446d`.
- `verify_recursive_expansion.py` `v2` SHA-256: `d677d1bc9c7efa9c3a94704eddd2f80ea651074f55c4a8452e5295f5d9797552`.
- Imported `coordinate_energy.py` SHA-256: `7e9b16c18c5855ef7786f78d42300e63fb2a3dcf768413355a31d14160c6ea71`.
- The generator emits both source hashes; the independent verifier recomputes and enforces both before exact reconstruction.
- Promotion charges a matched-random functional-advice-byte `S*T^2/(epsilon*q)` ratio; entry and online ratios cannot bypass it.
- A reduced noncanonical integration sweep is deterministic and passes exact independent replay.
- All eight repository tests pass; the verifier's 18-case self-test includes duplicate-key, non-finite JSON, source-chain, and gate-bypass checks.
- All 13 checked-in experiment records validate against repository schemas.

### Failure modes

- The random-x path may still fail to match a coordinate family's exact candidate-order or fiber-selection semantics.
- Diagnostic full-support enumeration could be mistaken for compiler cost despite separate counters.
- Deep-byte accounting may omit allocator or cache effects and is not portable across Python runtimes.
- The normalized `S*T^2/(epsilon*q)` ratio is not a calibrated instantiation of the generic preprocessing theorem.
- The success gate may reward toy finite-size effects that do not persist with `q`.
- A preflight promotion could be overread despite the explicit no-break boundary.

### Next concrete action

Run `RUN-ECDLP-RECURSIVE-001` through the immutable wrapper with the exact generator command in `contract.md`, then commit its artifacts before running the verifier.

### Artifact paths

- `experiments/EXP-ECDLP-RECURSIVE-001/specification.json`
- `experiments/EXP-ECDLP-RECURSIVE-001/contract.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/candidate-checklist.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/pre-run-audit-v1.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/pre-run-audit-v2.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/revision-response-v2.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/src/recursive_expansion.py`
- `experiments/EXP-ECDLP-RECURSIVE-001/src/verify_recursive_expansion.py`
- `research_ledger.md`
