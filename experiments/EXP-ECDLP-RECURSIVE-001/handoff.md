## Handoff: Repaired recursive coverage successor

### Claim or task

Test whether the verified eight-term coverage/first-witness signal survives non-special curves, replicated null distributions, and order-independent online accounting.

### Status

HYPOTHESIS

### Assumptions

- Successor curves must be prime order, non-supersingular, non-anomalous, and free of predeclared special `j` values.
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
- All checked-in experiment records validate against repository schemas.
- The canonical generator raw SHA-256 is `cf9e8fc8fa26bb5ea40e289bae435f0147ecc6e87da17482772528c8496d2890`; the verifier raw SHA-256 is `a99acde52f07d52600fa89a93250b4e253eca70bcdbe5c25c165c4153b3f81b0`.
- Independent replay verified 216 configurations and the frozen three-family sign-complete `m=8` gate crossing.
- Every per-instance passing row had generic-maximum four-term support and approximately random advice bytes, so no split-compression signal was observed.
- Random-x/random-scalar frontier ratios ranged from `0.5705` to `1.4155`, and no family passed three instances against both controls.
- One instance was anomalous (`p=q=3931`, trace `1`) under the candidate checklist boundary.
- Independent result review returned `REVISE_INTERPRETATION`; its SHA-256 is `6ff6ba623b34bb363115b1a00d90b7ef9e67b0ca869c17ed8e5b9a7f465e5e77`.

### Failure modes

- A one-draw random control may manufacture an apparent family effect.
- First-witness cost may depend on support-map insertion order and the 256-target sample.
- Accidental anomalous or special curves may contaminate a multi-instance count.
- Deep-byte accounting may omit allocator or cache effects and is not portable across Python runtimes.
- The normalized `S*T^2/(epsilon*q)` ratio is not a calibrated instantiation of the generic preprocessing theorem.
- The success gate may reward toy finite-size effects that do not persist with `q`.
- A preflight promotion could be overread despite the explicit no-break boundary.

### Next concrete action

Implement `EXP-ECDLP-RECURSIVE-002` with trace `not in {0,1}`, special-`j` rejection, many paired random controls, exact support percentiles, and shuffled plus order-independent scan metrics.

### Artifact paths

- `experiments/EXP-ECDLP-RECURSIVE-001/specification.json`
- `experiments/EXP-ECDLP-RECURSIVE-001/contract.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/candidate-checklist.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/pre-run-audit-v1.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/pre-run-audit-v2.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/revision-response-v2.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/result-red-team.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/evidence.json`
- `experiments/EXP-ECDLP-RECURSIVE-001/decision.json`
- `experiments/EXP-ECDLP-RECURSIVE-001/runs/RUN-ECDLP-RECURSIVE-001/raw-result.json`
- `experiments/EXP-ECDLP-RECURSIVE-001/runs/RUN-ECDLP-RECURSIVE-002/raw-result.json`
- `experiments/EXP-ECDLP-RECURSIVE-001/src/recursive_expansion.py`
- `experiments/EXP-ECDLP-RECURSIVE-001/src/verify_recursive_expansion.py`
- `research_ledger.md`
