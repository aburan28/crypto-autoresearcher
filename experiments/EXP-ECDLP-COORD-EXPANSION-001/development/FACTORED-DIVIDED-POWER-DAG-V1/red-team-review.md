# Red-Team Review: Factored Divided-Power DAG V1

## Handoff: Rootless Divided-Power DAG

### Claim or task

Audit whether the experiment provides semantically correct rootless D4
membership/witness descent and a meaningful efficiency signal.

### Status

`NEGATIVE RESULT`, scoped to this explicit balanced all-degrees DAG.
Semantic correctness is independently reproduced `TOY-EVIDENCE` and
`MODEL-BOUND`.

### Assumptions

- fixed curve `p=971`, prime subgroup order `q=953`;
- one nested prefix per family and `B=2..5`;
- canonical four-multiset membership and first-route recovery only;
- no relation rank, `A+4R` integration, individual-log target descent, or
  exponent claim.

### Evidence so far

The online root genuinely has no cycle map and disables the membership
prefilter. It scans degree splits from retained children, then recurses through
child cycles. Root coefficients match direct canonical enumeration. An
independent `random_x, B=5` reconstruction matched all non-telemetry fields.

The initial review also exhausted all 953 targets at `B=5`:

| family | sampled DAG max | exhaustive DAG max | DAG words | D2 words | exhaustive D2 max |
|---|---:|---:|---:|---:|---:|
| x-interval | 14 | 17 | 489 | 75 | 15 |
| scalar progression | 11 | 11 | 489 | 65 | 13 |
| random-x | 14 | 17 | 489 | 75 | 15 |
| source-PRF-x | 16 | 17 | 489 | 70 | 14 |

The DAG has no same-function Pareto win.

### Failure modes

1. **CRITICAL: the 15 preregistered signal cells mix units.** They compare DAG
   records with base-field elements. At `B=5`, 90 records look smaller than
   136–142 polynomial elements, but the DAG retains 489 logical words.
2. **HIGH: reduced-D2 MITM dominates.** It gives the same membership and source
   routes with 13–15 records, versus 90 DAG records. Outside the scalar
   control, exhaustive DAG scans are also worse.
3. **HIGH: the recorded worst was sample-only.** The first artifact's 32
   sampled targets missed true maxima of 17 in three `B=5` families.
4. **HIGH: operation accounting omitted leaf construction, online sorting,
   route copying, and witness replay.**
5. **MEDIUM: memory accounting omitted metadata, hash-table overhead, a root
   wrapper, and build-peak serialized bytes.**
6. **MEDIUM: the verifier accepted negative telemetry and a false configured
   input path when an override supplied the real input.**
7. **MEDIUM: one fixed `q`, nested prefixes, and one seed per family provide no
   asymptotic or ECDLP inference.**

### Resolutions incorporated

- all 953 subgroup targets are now queried in every cell, and exhaustive maxima
  drive both gates;
- exhaustive query receipts are independently digested and reconstructed;
- leaf scalar steps and curve operations are charged;
- query sort calls/items and route-index copies are charged;
- witness replay operations are separate;
- full-build and retained-advice canonical JSON bytes are separate;
- telemetry must be nonnegative and the configured input path must match;
- 20 targeted mutations cover the new accounting, exhaustive digest,
  provenance, and telemetry fields;
- the analysis labels the 15 weak-gate passes as non-commensurate diagnostics,
  with zero same-function wins.

Python object/hash overhead and actual memory traffic remain unmeasured and
are explicit limitations.

### Exact narrow negative

> On the fixed `p=971`, `B=2..5` cells, the balanced contiguous,
> degree-0-through-4, rootless child-cycle DAG is semantically exact but does
> not jointly improve retained state and exhaustive online work over
> same-function support-index and reduced-D2 controls.

### Next concrete action

Do not optimize this all-degrees tree in isolation. Any successor must compare
from inception against a rootless `2+2` index and global reduced-D2 MITM,
charge full build operations/bytes and exhaustive target-query work, and sweep
at least three `q` sizes plus independent factor-base seeds. A recursive
candidate advances only if it is not dominated on the same
membership-and-witness function.

### Artifact paths

- `contract.md`
- `analysis.md`
- `raw-result.json`
- `verification.json`
- `../../src/factored_divided_power_dag.py`
- `../../src/verify_factored_divided_power_dag.py`
