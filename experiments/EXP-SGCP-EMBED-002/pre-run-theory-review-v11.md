## Findings — severity order

1. **LOW — one self-review scope sentence is overbroad.** `source-self-review-v11.md:58-59` says no generated density-row or run artifact exists. The commit retains historical, noncanonical V1 density rows and a development run manifest (`development/DEV-SGCP-EMBED-002-V1/raw-result.json:1`; `run-manifest.json:2-14`). The accurate statement is: **no generated V11 density row, canonical run, runner, or launch plan exists**. The governing contract already makes this distinction at `contract.md:493-509`, so this is non-blocking.

No HIGH or MEDIUM findings.

## Completed-work equality

The equality is mathematically and semantically justified:

- Curve provenance is reconstructed first, followed by independent curve enumeration and factor-base reconstruction; any failure marks work incomplete and invalidates the row (`src/verify_sgcp_embed_family.py:4457-4480`).
- Document-level equality runs only when every row report is valid (`:6459-6513`), which is stronger than merely requiring curve/factor-base success.
- Expected counts are derived from the now-verified public transcripts (`:580-617`), not from reservations or observed counters.
- Overall validity separately requires `actual_work_complete=true` (`:6031-6046`) and successful phase closure includes the equality phase (`:6596-6638`).

Independent totals, ordering curves as `(5,101),(5,211),…,(8,211)`:

| Counter | Independent derivation | Total |
|---|---|---:|
| Registered prime candidates | `2 × (2^4 + 2^5 + 2^6 + 2^7)` | 480 |
| Curve draws | `12+49+4+15+11+8+3+10` | 112 |
| Curve hashes | `3 × 112` | 336 |
| Registered-curve point enumerations | 109 nonsingular draws, each enumerated twice | 218 |
| Predicate hashes | `12 × (15+9+18+23+53+41+105+69) + 222` | 4,218 |

For predicate hashes, the first term is four hash-null replicates across three B values over 333 admissible roots. Möbius reconstruction contributes 216 baseline hashes plus two extra three-hash nonce attempts. These semantics match `:593-616`, `:1080-1099`, and `:1236-1256`.

## HASH_CHECK

**HASH_CHECK: PASS — 9/9 exact committed blobs match `development-test-log-v11.md:18-26`.**

| Artifact | Computed SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `42e77b58419c2e5e1d1df4fc9e21a1ecc736863f2cff2bb6eda0bad8c25f0282` |
| `src/verify_sgcp_embed_family.py` | `a0bab9d018ea12af5bfbfa9f80d7ac55094cc2355f7367ad330f91c8fd8d093b` |
| `tests/test_sgcp_embed_family.py` | `45b2665b44fd0bc3ca0c7feac7c86df24ea2c85390ff3f7defa19801acb5afef` |
| `hypothesis.json` | `31bf9007fb61e85e01db9ec1bb51885d1f9c5a2b8875b7d3c75f3ab5d37ac1a8` |
| `specification.json` | `d2d63fedabed0ea5f220ea002628e9c2a8871059c736513261f21cc40e8ae17f` |
| `contract.md` | `3ac4bc7265f767736d4070f196fca5f9399b83e61da638abeb85d4de035a3ee5` |
| `protocol-amendment-v11.json` | `4a101b1e8eccf2ca4f460d4d0c92e98bde8cdefb40514e2bbab07df52041cda9` |
| `revision-response-v11.md` | `59412b0a01db07688b4107e35f547dae28d26c8875c2fe5928b3599249b602df` |
| `source-self-review-v11.md` | `69104e98e690beb0ed4009c0fcd52e5f37131fdc155760e578f32f15d3314fb0` |

## SCOPE_CHECK

**SCOPE_CHECK: PASS, with the LOW wording correction above.**

- One transient frozen `p=19, B=4` density-row control is explicitly constructed by the tests (`tests/test_sgcp_embed_family.py:643-657`).
- Every non-frozen V11 density-row construction is rejected (`src/sgcp_embed_family.py:1467-1510`).
- No V11 canonical run exists. Canonical and development execution entry points refuse execution (`:2125-2128`, `:2149-2157`).
- No execution authorization exists: status is `review_required`, `maximum_runs=0`, and all CPU/memory/run budgets are zero (`specification.json:193-202`; `contract.md:498-509`).
- Claim boundaries remain properly limited to `HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`, and `NOVELTY-UNVERIFIED`; relation yield, rank, descent, rho improvement, exponent, and ECDLP claims remain excluded (`contract.md:511-516`).

## Verdict

**GO — launch-plan DESIGN ONLY.**

This is one scoped Theory GO for exact commit `f8e4606d7aa86fac9d79872be63e9a22e3854d52`. It does not itself authorize design, execution, generated rows, or a budget change; independent accounting and red-team GO plus coordinator action remain necessary.

```yaml
handoff:
  id: TASK-20260723-001
  from: coordinator
  to: executor
  objective: Obtain a fresh independent accounting review of exact commit f8e4606d7aa86fac9d79872be63e9a22e3854d52 for launch-plan design only.
  inputs:
    - git:f8e4606d7aa86fac9d79872be63e9a22e3854d52
    - git:2a954438add9ba6c1ce487b25d3d71a21e4019e5
    - this independent Theory GO
  constraints:
    - read committed bytes with git show only
    - treat prior and self-reviews as claims
    - do not modify files
    - do not construct density rows or execute experiments
    - preserve maximum_runs=0
  deliverables:
    - severity-ordered accounting findings
    - HASH_CHECK and SCOPE_CHECK
    - GO or REVISE for launch-plan design only
  budget:
    wall_clock_seconds: null
    memory_gb: null
    maximum_runs: 0
  completion_gate:
    - verdict is bound to the exact commit
    - execution remains explicitly unauthorized
```