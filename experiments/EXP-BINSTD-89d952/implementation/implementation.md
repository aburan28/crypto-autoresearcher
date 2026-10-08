# Implementation note — EXP-BINSTD-89d952 / TASK-20261001-e15653

Observations only. No hypothesis-status change. No break / rho claim.

## What was implemented

| path | role |
|---|---|
| `implementation/gf2n.py` | F_{2^19} table field (`t^19+t^5+t^2+t+1`) |
| `implementation/curve.py` | binary curve group law (from CERTBIN) |
| `implementation/macaulay.py` | monomial order helpers for Closure |
| `implementation/closure.py` | CERTBIN W_D engine (available; unused at D=4) |
| `implementation/s4_descent.py` | S_3/S_4 resultant + Weil descent + ClosureGeneric |
| `implementation/stage0_run.py` | corrected table, cancelation, census, note |
| `implementation/stage1_run.py` | two-arm feasibility + controls enumeration |
| `implementation/stage2_run.py` | feasibility-report |
| `implementation/runpack.py` | immutable run packages |

## Protocol deviations

1. **Frozen S_4/W_4 at D=4 unreachable.** Measured Boolean degree of the
   descended S_4 system at `(n,m,l)=(19,3,5)` is **6** on both arms. Macaulay
   columns at D=4 cannot host degree-6 monomials. Recorded as
   `instrument_unavailable` (infrastructure / DO-5), not negative math
   evidence. Arm-ratio seeds beyond the primary feasibility probe were not
   run for this reason.
2. **Non-protocol D=6 probe.** `stage1/d6-nonprotocol-probe.yaml` records that
   `M_6` *does* build (`macaulay_build_ok: true`) with tiny matrices. This is
   **not** used for `arm_ratio` / success criteria (frozen protocol is D=4).
3. **`arm-comparison.yaml` is non-decisive.** It points at
   `instrument_unavailable.yaml` as the decisive Stage-1 path; `arm_ratio`
   fields are null.
4. **Ordinary subgroup order.** Spec inherited `h=2` without an `l` hint.
   Measured `#E=523646=2·261823` with 261823 prime — documented as MEASURED.
   Koblitz `#E=4·130873` matched the inherited hint.
5. **No per-instance μ-orbit / canonical-representative constraint** was
   encoded in any solver or enumeration path.

## Runs

| run_id | stage | status / termination |
|---|---|---|
| `RUN-BINSTD-260c42` | 0 | `completed_valid` / completed |
| `RUN-BINSTD-8b78a7` | 1 | `failed_infrastructure` / instrument_unavailable |
| `RUN-BINSTD-97e1bf` | 1 | `completed_valid` / completed (enumeration certs) |
| `RUN-BINSTD-a5d4b9` | 2 | `completed_valid` / completed |

## certificate.kind

All manifests use vocabulary `discrete_log|decomposition|key_recovery|none`
only. Stage 0/2 and feasibility: `none`. Controls enumeration:
`decomposition` with independent curve-summation re-verify.
