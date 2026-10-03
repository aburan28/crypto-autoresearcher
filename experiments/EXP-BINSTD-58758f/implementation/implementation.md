# Implementation notes — EXP-BINSTD-58758f Stages 0–2

Task: `TASK-20261001-c04c94`. Observations only; no H/EXP/IDEA status changes.
No deployed-curve break claim. No free-cofactor framing. HOLD-O corrections bind.

## Code

| Path | Role |
| --- | --- |
| `implementation/gf2n.py` | Schoolbook + table `F_{2^n}` (from CERTBIN) |
| `implementation/curve.py` | Binary `Y^2+XY=X^3+AX^2+B` + Miller–Rabin |
| `implementation/coset.py` | Windows, Z/4 class via order-4 point, census, Z/(4l) replica |
| `implementation/runpack.py` | Immutable run package writer (`certificate.kind: none`) |
| `implementation/stage0_run.py` | Chain certificate + builder audit + methodological note |
| `implementation/stage1_run.py` | Toy census + replica + HEUR comparison artifacts |
| `implementation/stage2_run.py` | h=2 control (Z/4 undefined; parity ~2) |

## Protocol notes / deviations

1. **Primary V/V_C statistic** is `mean_V / mean_V_C` (equivalently total-count
   ratio). Averaging only per-target ratios with nonzero `V_C` denominator
   biases low when counts are sparse (m=2); that quantity is retained only as
   a tail/extreme check per the specification's "most extreme per-target"
   requirement.
2. **Census definition**: signed additive decompositions
   `T = Q_1+…+Q_m` with `Q_i ∈ {±P : x(P)∈ window}` and class-sum check in
   `Z/4` (or `Z/2` on h=2). Every counted hit is re-checked by curve group
   law. This is the geometric content behind Semaev `S_{m+1}=0` up to signs.
3. **m=2 band instability**: at toy scale, m=2 totals are small (tens of
   hits). One n=19 seed and the Z/(4l) replica sit outside `[0.5,2]×4` while
   m=3 stays inside `[0.5,2]×16` on curve and replica. Because curve and
   replica move together at m=2, the observation is labeled
   `DO-artifact_or_window_size_arithmetic_both_deviate` (not a curve-only
   HEUR fail). No threshold was edited post hoc.
4. **Builder audit**: all four named families read as `H_spent` (no
   cofactor-coset filter). SEMBIN is derivation-only; row still labeled with
   code+spec pointers (not silent H_unspent).
5. Run manifests record `code.dirty: true` at execution time because stage
   artifacts were written before commit (immutable run records; not rewritten).

## Seeds / randomness

| Seed | Use |
| --- | --- |
| 20261001 | Stage 1 n=19 census + replica sizing reference |
| 20261002 | Stage 1 n=19 replicate |
| 20261003 | Stage 1 RC-1 n=17 |
| 20261004 | Stage 2 h=2 |

No other RNG sources.

## Bedrock / AUXIN / status

No Amazon Bedrock. No AUXIN edits. No H/EXP/IDEA status edits.

## Comparison vs frozen prediction (observations only)

| Item | Frozen | Observed |
| --- | --- | --- |
| Stage 0 Z/12 + n=19 chain | pass | pass (`RUN-BINSTD-2f2e4b`) |
| Builder H_spent prior | more likely | 4/4 H_spent |
| Coset x-fractions | ~(1/4,1/4,1/2) | ≈(0.22,0.25,0.52) n=19; similar n=17 |
| V/V_C m=2 | 4 within [2,8] | mixed: 4.17, 12.0, 3.61 (curve); replica 12.3 |
| V/V_C m=3 | 16 within [8,32] | ≈19–25 curve; replica ≈23.8 (all in band) |
| Parity ~2 (h=4) | 2 | mixed at m=2; ≈1.8–2.0 at m=3 |
| Class-sum violations | 0 | 0 |
| Class-2 mirrors under V_C | 0 | 0 |
| h=2 Z/4 | undefined | undefined (`RUN-BINSTD-bb6967`) |
| h=2 parity | ~2 | 2.14 (m=2), 1.97 (m=3) |
| h=1 null | absent | absent |
| Break / free-cofactor claim | none | none |
