## Handoff: SGCP V5 exact-commit accounting audit

### Claim or task

Review only commit `606daf8fee72979403915d23011f987f01007b74` for
EXP-SGCP-EMBED-002 V5 accounting integrity and readiness for a separate
hash-complete canonical launch-plan design.

### Status

`OBSERVATION`; the underlying claim remains `HYPOTHESIS`, `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

Accounting recommendation: `GO` for launch-plan design only. Execution remains
`NO-GO`. This is one scoped role decision; it does not override theory or
red-team `REVISE` decisions.

### Assumptions

- Only exact Git blobs at the requested commit were reviewed.
- No producer CLI, family row, canonical matrix, runner, or plan was launched
  or created.
- Optimizer nodes, proof nodes, structural cells, field operations, memory
  traffic, and wall time are unequal resources and must not be conflated.
- Any missing row, timeout, OOM, unresolved cell, invalid receipt, or verifier
  failure is `INCONCLUSIVE`.

### Evidence so far

All nine V5 hashes match the committed blobs exactly:

| Blob | SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `d9cf9eeb5cda649956e3b8b1b6a754909869e53fd053c7ef2da14809b94c81dc` |
| `src/verify_sgcp_embed_family.py` | `053c11426031e53df5ef7c11cd4d652fa65c7effed3411924a6f4016d18cf776` |
| `tests/test_sgcp_embed_family.py` | `2900c3bad72096e2d12bca5720d2eb5fb26937af9867841cd07ca4d7602da903` |
| `hypothesis.json` | `b9514323c1ab5aa1c4e2046b810306e04d937bb0714ec6efc0e2eaade3ad1597` |
| `specification.json` | `0e4390d1e4cc726b86d830426ad8d06debcb438a2d4295d78c516ddb2e3445f1` |
| `contract.md` | `714ff8d09d1e45c3c0b04bf4b7cf23cd1a31e4e7f1a173beaaa1e2e74202d992` |
| `protocol-amendment-v5.json` | `43fc0af4a834e2b8e036dcb5b36f8c088c890fdc791711e1a9670dc3148ae04f` |
| `revision-response-v5.md` | `d76d68c518fa17fea48d49923dd8d1bfc5adc1a40a6f494b37f7a22c3a2bdebb` |
| `source-self-review-v5.md` | `45f5028b173c7d10fd944a95cfb1d2d985caf7f1b316eec8f39d53537625ae86` |

- All 33 committed focused tests passed from exact blobs.
- The four V4 crash mutations return repeatable invalid receipts with zero
  independent-proof nodes.
- Legacy V1-V4 schemas are rejected with zero row reports.
- Exact schemas validate both research records, and `ledger.json` exactly
  matches specification version 5 with `status=review_required` and `runs=[]`.
- Both producer CLI branches raise before output. The exact tree contains no
  V5 run, runner, canonical matrix, launch plan, or development result.
- Governance is internally consistent: maximum runs, wall time, CPU hours,
  memory authorization, and additional V5 development rows are all zero;
  `approved_by` is null and `launch_plan_authorized` is false.

Static expansion accounting for the canonical 168-row grid is:

| B | Rows | Expansion cells/row | Expansion EC-add calls/row | Max degree-4 candidates | Max conflict pairs | Worst subset space |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 56 | 214 | 1,484 | 35 | 595 | `2^35` |
| 6 | 56 | 1,440 | 10,848 | 126 | 7,875 | `2^126` |
| 8 | 56 | 6,809 | 52,880 | 330 | 54,285 | `2^330` |

- Producer expansion alone totals 473,928 multiset cells and 3,651,872 EC-add
  calls. Verifier reconstruction doubles the latter to at least 7,303,744
  add calls before graph, search, proof, serialization, or provenance work.
- Whole-matrix producer search permits `672 * 2,000,000 = 1.344 billion`
  nodes. Replay permits another 1.344 billion. Independent proof at the
  five-million default permits 3.36 billion, for a combined default ceiling of
  6.048 billion nodes.
- At the hard 100-million verifier ceiling, the combined nominal ceiling is
  69.888 billion nodes. These are ceilings, not runtime predictions.
- The frozen p=19, B4 fixture used 31 candidates, 12 eligible vertices, 20
  conflicts, 218 producer optimizer nodes, and 250 proof nodes. It recorded
  14,353 producer point additions, 10,117 inversions, 33,282 counted
  multiplications, and a 24,674-byte document.

No matched ECDLP baseline conclusion is available:

| Comparator | V5 status |
|---|---|
| Four matched hash-ranked predicate controls | Registered, but no canonical matrix exists |
| Independent finite optimizer | Confirmed only for frozen B4 |
| Pollard rho and van Oorschot-Wiener | Not implemented or compared |
| BSGS/MITM | Not implemented or compared |
| Index calculus, Groebner, SAT, or crossbred | No end-to-end relation pipeline exists |
| Fixed-curve preprocessing crossover | Explicitly unsupported |

V5 therefore implies no rho, VW, BSGS, index-calculus, fixed-curve, operation
count, or exponent advantage.

### Failure modes

- A one-GiB file can require several GiB of parser and Python-object memory;
  the parser ceiling is not a role memory authorization.
- The ten-million JSON-node check occurs only after materialization.
- Invalid canonical matrix envelopes do not immediately stop row
  reconstruction.
- Producer, replay, proof, pair-output, and parser caches lack committed byte
  and entry ceilings.
- Producer counters omit curve generation, enumeration, Python container/hash
  work, JSON work, verifier work, and complete field-operation accounting.
- Canonical B6/B8 feasibility and canonical artifact size remain unmeasured.
- The four nulls are deterministic controls, not a calibrated random null
  distribution.
- Accepted toy curves include small MOV embedding degrees. This does not
  invalidate the finite experiment, but it forbids security inference.
- There is no relation collection, rank, linear algebra, target descent, or
  many-target amortization measurement.

### Next concrete action

After all three independent roles issue GO, draft but do not execute a separate
hash-complete plan that freezes exact code, commands, environments, hardware,
roles, outputs, retries, phase receipts, and aggregate wall/CPU/RSS/disk/I/O/
node/cache limits. Retain `maximum_runs=0` pending coordinator approval.

### Artifact paths

- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/contract.md`
- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/hypothesis.json`
- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/specification.json`
- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/protocol-amendment-v5.json`
- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/development-test-log-v5.md`
- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `606daf8fee72979403915d23011f987f01007b74:tests/test_sgcp_embed_family.py`

Final accounting recommendation: **GO for separate launch-plan DESIGN only.
Execution remains NO-GO.**
