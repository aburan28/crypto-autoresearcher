# Analysis — EXP-BINSTD-cedae5 / H-BINSTD-fe6b59

Review plan: `experiments/EXP-BINSTD-cedae5/review/review-plan.yaml`
(`REVIEW-BINSTD-cedae5-20261001`). Producer: `TASK-20261001-e57118`
(package tip at review start ~`77fe5a98d`; implementation commit
`f316dafc`). Evidence: `EV-BINSTD-769c7c`. Decision:
`DEC-20261001-fe73db`.

Class: **measurement** (toy free-leg residual-banking / relation-
collection instrument). No ECDLP attack, no break, no rho
competitiveness, no GTTD, no exponent-moving claim. Scope: RC-1 n=17
primary + optional n=19 Koblitz sibling only.

---

## Observation

**Validity.** Ten runs, all `completed_valid`; `invalid=[]`;
`failed=[]`; `n_runs=10 ≤ maximum_runs=24`:

| Run | Stage | Arm | Certificate | Primary metrics |
| --- | --- | --- | --- | --- |
| `RUN-BINSTD-1b0b64` | 0 | pricing verify | `none` | floors_match_hold_q=true; RC-1 order 130412 |
| `RUN-BINSTD-ad20e8` | 1 | curve V | `decomposition` verified | T=116162; combined=160633; pass=1.0; ratio≈3.105; S_fit≈42001 |
| `RUN-BINSTD-e0b78d` | 1 | curve V'_0 | `decomposition` verified | T=29768; combined=28436; pass=1.0; ratio≈8.37; S_fit≈15581 |
| `RUN-BINSTD-c85825` | 1 | recomb-off | `decomposition` (full only) | combined=0; full=390; full/modeled_freeleg≈0.907 |
| `RUN-BINSTD-6696d3` | 2 | T-growth | `decomposition` | 3 seeds; tracks T²/(2S_fit) |
| `RUN-BINSTD-041330` | 3 | Z/(4·32603) | `decomposition` verified | primary combined=51298; ratio≈0.987 |
| `RUN-BINSTD-3e3cae` | 3 | curve/generic | `none` | curve_over_generic≈3.131; trigger FIRED |
| `RUN-BINSTD-7bcd67` | 4 | adversarial 8-bit | `decomposition` | failure_rate≈0.9939 |
| `RUN-BINSTD-fdff79` | 5 | n=19 census | `decomposition` verified | combined=735192; pass=1.0; ratio≈3.03 |
| `RUN-BINSTD-981b8a` | 5 | n=19 generic | `decomposition` verified | combined=242323; ratio≈0.997 |

Manifest metrics agree with `raw-result.json` and with stage YAML
artifacts. No Bedrock. Stage 0 commit `0681afbb` precedes Stage 1+
package `f316dafc`. Producer discloses char-2 combined certificate
uses signed cancellation `P1+P2+(-P3)+(-P4)` when L matches (not naive
four-sum). Claim-boundary flags false on all stage artifacts
(`deployed_curve_break_claimed`, `rho_competitiveness_claimed`,
`gttd_claimed`).

**Stage 0.** HOLD-Q dominated_by pricing written before Stage 1.
Independent recompute (this review): for `N=2^131`,
`log2(sqrt(2 N B))` = 66.0 / 71.0 / 76.0 / 81.0 at
`B=1 / 2^10 / 2^20 / 2^30`; gaps above matched rho 60.809 =
5.191 / 10.191 / 15.191 / 20.191. Matches
`stage0/dominated-by-pricing.yaml` and RUN-1b0b64. Preregistered
predictions, methodological note, literature note, canonicalisation
convention present. Deployed bearing: none (MODELED domination only).

**Stage 1.** Exhaustive free-leg census on RC-1 (`n=17`, `m=3`):

- **V** (`|V|=483`, `T=116162`): combined=160633, all verified;
  `S_fit = T²/(2·combined) ≈ 42001.36 ≪ N=130412`;
  `residual_collision_rate_ratio ≈ 3.105` vs uniform-N model;
  `combined / (T²/(2S_fit)) = 1.0` exactly by construction of S_fit.
  Distinct residual keys 38445; max multiplicity 16.
- **V'_0** (aligned half, `|V|=245`, `T=29768`): combined=28436,
  pass=1.0; ratio≈8.37 (~2.70× V's ratio — directionally elevated vs
  the preregistered ~2× coset-confinement check).
- **Recombination-off**: combined=0 (no phantoms); full=390 vs
  modeled free-leg `T·|V|/N ≈ 430` (ratio ≈0.907, within lane
  tolerance).

Merge wall-clock on V: collection ≈0.189 s, merge ≈0.280 s;
`merge/collection ≈ 1.485` (≫ 10% HEUR-H1 threshold) — disclosed in
metrics, no "cheap pre-processing" restatement filed.

**Stage 2.** T-subsample growth on V, seeds
`{20261001,20261002,20261003}`. Across the grid, combined counts track
`T²/(2S_fit)` closely once T is past the sparse small-T noise regime;
collision_rate_ratio stays ≈3.1 at large T (consistent with fixed
S_fit≪N). Certificate pass rate 1.0 on all series points with
combined>0.

**Stage 3.** Generic replica on `Z/130412` with random matched
`|V|=483`, three seeds: primary seed combined=51298,
`collision_rate_ratio≈0.987` (near-uniform). Curve-over-generic
`160633/51298 ≈ 3.131` outside preregistered band `[0.5, 2]` →
concentration trigger FIRED (authorized Stage 5).

**Stage 4.** Adversarial 8-bit truncated hash keys:
`combined_relation_count=26463885`, `combined_failed=26303252`,
`adversarial_certificate_failure_rate≈0.9939 > 0` — control has
power (DO-3 not triggered).

**Stage 5.** n=19 Koblitz sibling (`y²+xy=x³+1`, window deg<10,
`|V|=1005`): curve combined=735192, pass=1.0, ratio≈3.030,
`S_fit≈172760`; generic `Z/523492` combined=242323, ratio≈0.997;
`curve_over_generic_n19 ≈ 3.034` — excess **persists** off RC-1.
Structural observation only; no deployed claim.

---

## Comparison

Blind re-derivations (review plan quantities; producer implementation
not used for the arithmetic):

| Quantity | Independent value | Producer | Match |
| --- | --- | --- | --- |
| HOLD-Q floors | 66.0/71.0/76.0/81.0 | same | yes |
| V S_fit | 42001.364… | 42001.364… | yes |
| V collision ratio | 3.10495… | 3.10495… | yes |
| curve/generic | 3.13137… | 3.13137… | yes |
| adversarial failure | 0.99393… | 0.99393… | yes |
| n=19 curve/generic | 3.03393… | 3.03393… | yes |

Against distinguishable outcomes (`H-BINSTD-fe6b59`):

| DO | Criterion | Result |
| --- | --- | --- |
| DO-1 birthday-confirmed-toy | curve **and** replica ratios in [0.5,2] | **FAIL** (curve≈3.13; replica≈0.99) |
| DO-2 curve-concentration | excess vs replica / outside-band + Stage 5 | **HIT** (trigger fired; n=19 persists ≈3.03; not >4× but outside band — Stage 5 path / structural finding) |
| DO-3 cert-power-absent | adversarial failure_rate = 0 | **not hit** (≈0.994) |
| DO-4 baseline-mismatch | recomb-off full vs modeled | **not hit** (≈0.907; combined=0 clean) |
| DO-5 infra | timeout/crash/numpy | **not hit** |

HEUR-BINSTD-fe6b59-H0: birthday count vs **fitted S** holds
(factor ≈1.0); group-free / S≈N reading **fails** (curve/generic
outside [0.5,2]; S_fit/N ≈ 0.322). HEUR-H1 merge-cost: **fails** at
this toy T (`merge/collection≈1.485`) without disclosed restatement.

---

## Inference

The package is valid. Certificate-verified free-leg residual banking
works as a **toy instrument** on RC-1 / n=19: combined relations
re-sum to O at pass=1.0; recombination-off produces no phantoms;
adversarial truncated keys fail certificates at high rate; growth
tracks `T²/(2S_fit)`.

The HOLD-Q blocking control does its job: residual collisions are
**curve-structured**, not group-free. Generic `Z/(4l)` is near
uniform (≈0.99); curve excess ≈3.1× persists at n=19 (≈3.03). This
is DO-2: refine + report structural finding — **not** a rejection of
instrument existence, and **not** a break / rho / GTTD result.
Optimistic assumption `S≈N` is falsified at these toy cells; any
honest reading must price with measured S and must not transfer the
concentration factor to deployed `N=2^131`.

Dominated_by pricing (Stage 0) remains intact as modeled arithmetic:
even under S≈N the free-leg large-prime floor sits above matched rho
on ECC2K-130 for every `B≥1`. Concentration at toy scale does not
license a deployed claim.

Official decision: **refine** (DO-2). Hypothesis `approved→analyzed`.
Experiment `approved→analyzed`. Strength: **preliminary** (single
unreplicated package; Coordinator-direct PD-1; structural finding
clear but not independently re-implemented). No KN-FIND (below
replicated/strong; refine not support/reject_scoped).

---

## Limitation

- Toy only: n∈{17,19}, m=3, window deg<9/10; zero deployed bearing.
- Curve/generic ≈3.1 is outside [0.5,2] but not >4×; DO-2 text says
  ">factor 4" while Stage 5 trigger is "outside [0.5,2] OR >4×" —
  this review treats the Stage 5 path as DO-2 structural refine.
- S_fit is defined from the same combined count it predicts
  (`combined ≡ T²/(2S_fit)`); discriminative content is (i) pass=1.0
  certificates, (ii) growth-curve agreement across T, (iii)
  curve≠generic.
- Merge wall-clock exceeds collection at this T; HEUR-H1 "cheap
  merge" framing needs restatement or engineering follow-up —
  measurement may be Python/hash overhead, not asymptotic UF cost.
- Char-2 signed-cancellation convention is a disclosed protocol
  deviation; correctness rests on independent re-sum (pass=1.0), not
  on a separate formal proof of the sign rule.
- Coordinator-direct review (PD-1); manifests dirty-at-write at
  producer commits; single unreplicated package.
- No break; no rho; no GTTD; no exponent; no F7 advice reuse.
