# Analysis: EXP-BINSTD-58758f (H-BINSTD-a45444)

Review plan: `experiments/EXP-BINSTD-58758f/review/review-plan.yaml`
(`REVIEW-BINSTD-58758f-20261001`), written before this analysis.
Producer: TASK-20261001-c04c94. Decision target: **inconclusive**
(mixed HEUR-H1; window-size arithmetic at m=2; limited data_quality)
preferred over support; denser m=2 replicate/refine as successor.
No break; no free-cofactor framing.

## Observation

**Validity (J1).** 6 run directories under `runs/`; execution_report lists
the same 6 completed IDs, `invalid: []`, `failed: []`. Every run has
`manifest.yaml`, `raw-result.json`, `environment.json`, `stdout.log`,
`command.txt`. All `raw.valid: true`, `termination_reason: completed`,
`status: completed_valid`. Stage split: 1 Stage 0 (`RUN-BINSTD-2f2e4b`),
4 Stage 1 (`80eb23` n19/20261001, `e72758` n19/20261002, `33d7d1` n17/20261003,
`bbaf9e` Z/(4l) replica), 1 Stage 2 (`bb6967` h=2/20261004). Within
`maximum_runs: 24`. Required stage0/1/2 artifacts all present. Amazon
Bedrock not selected. Every run sets `certificate.kind: none` (measurement /
symbolic; no discrete_log / key_recovery claim). Producer disclosures
retained: primary HEUR statistic uses mean_V/mean_V_C; `data_quality:
limited`; m=2 sparse anomaly recorded not discarded.

**Stage 0 (J2).** Chain certificate `pass: true` on Z/12 (orders match
{1,2,3,4,6,12}; endomorphism preservation pass) and on n=19 Koblitz
(`#E=523492=4*130873`, `l` prime, `4E=C`, quotients Z/2 and Z/4, trivial on
C). Blind re-derivation: `523492 == 4*130873` and `130873` prime — agree.
Builder audit: CERTBIN, DREG, SEMBIN, QSP all `H_spent`
(`restricted_to_one_cofactor_coset: false`) with code/spec pointers;
`n_H_unspent: 0`. Methodological note closes target-side reading, prices
part (B) as base-size `4^{m-1}`, cross-cites DC-04 for leg-side, forbids
free-cofactor framing and h=1 null.

**Stage 1 (J3).** Class-sum violations = 0 on all three curve cells;
mirror `V_C` zero-check true at m=2 and m=3. Coset fractions near modeled
(1/4, 1/4, 1/2). HEUR-H1 blind band check vs `4^{m-1}`:

| cell | m | measured | modeled | in [0.5,2]x |
| --- | --- | --- | --- | --- |
| n19 seed 20261001 | 2 | 4.17 | 4 | yes |
| n19 seed 20261001 | 3 | 24.27 | 16 | yes |
| n19 seed 20261002 | 2 | 12.0 | 4 | **no** |
| n19 seed 20261002 | 3 | 23.00 | 16 | yes |
| n17 seed 20261003 | 2 | 3.61 | 4 | yes |
| n17 seed 20261003 | 3 | 19.44 | 16 | yes |
| Z/(4l) replica | 2 | 12.33 | 4 | **no** |
| Z/(4l) replica | 3 | 23.76 | 16 | yes |

Producer verdict `DO-artifact_or_window_size_arithmetic_both_deviate`
matches: m=3 in band on curve and replica; m=2 out-of-band on one n=19
seed **and** on the replica together (not curve-only ⇒ not DO-3). One
parity outlier (n19/20261001 m=2 parity 4.875 vs modeled 2) retained.

**Stage 2 (J4).** h=2 cell `#E=525086=2*262543` (blind: equality and
`262543` prime agree). `z4_bookkeeping.status: undefined`, `coerced:
false`. Parity ratios 2.14 (m=2) and 1.97 (m=3) within [0.5,2]x of 2.
Class-sum violations 0; `h1_null_absent: true`; no break / free-cofactor
flags.

## Comparison

Against preregistered prediction / DO map:

- Part (A) chain: **holds** at tested Z/12 and n=19 (DO-1 arm for Stage 0).
- Part (B) builders: **H_spent** on all four audited families (predicted
  prior; not H_unspent surprise).
- HEUR-H1 `V/V_C ~ 4^{m-1}`: **mixed** — m=3 consistent with band on curve
  and replica; m=2 fails band on curve seed 20261002 and replica jointly →
  window-size / sparse-count arithmetic per hypothesis falsification note,
  not coset-dependent concentration.
- Stage 2 controls: **hold** (Z/4 undefined; parity ~2).
- Clean DO-1 (H_spent + full HEUR match) is **not** met because of m=2.
- DO-3 (curve-only deviation) is **not** met (replica co-deviates).
- DO-4 (instrument / chain fail) is **not** met (class-sum 0; chain pass).

## Inference

The package is **valid** and **does not discriminate** a clean DO-1
seam-closure from a sparse-window artifact at m=2. Stage 0 HOLD-O chain
and H_spent audit stand as scoped observations. HEUR-H1 is neither
supported nor rejected at the full `{m=2,3}` test boundary under limited
toy power. Official decision: **inconclusive**. Hypothesis
`approved → analyzed`. Do **not** support. Do **not** reject_scoped
(no checkable HEUR counterexample at unreplicated empirical-only sparse
m=2; replica co-deviation points to arithmetic artifact). No deployed
break; no free-cofactor framing; no exponent claim. Successor: denser m=2
census / larger windows (replicate or protocol_amendment) before any
stronger HEUR reading.

## Limitation

- Toy n in {17,19} only; no transfer to m=131 claimed.
- `data_quality: limited`; m=2 sparse zeros bias per-target ratios
  (producer deviation disclosed).
- `certificate.kind=none` — measurement package, not a solve certificate.
- First unreplicated observation; no independent validator/red-team (PD-1).
- Builder audit includes some spec-level pointers (CERTBIN review cite;
  SEMBIN derivation-only path) — H_spent is engineering observation, not
  a runtime exhaustive proof.
- Strength inconclusive — insufficient for support or KN-FIND promotion.
