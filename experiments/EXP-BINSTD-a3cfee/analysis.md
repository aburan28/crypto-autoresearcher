# Analysis — EXP-BINSTD-a3cfee (TASK-20261001-3d2adf)

Review plan: `experiments/EXP-BINSTD-a3cfee/review/review-plan.yaml`
(REVIEW-BINSTD-a3cfee-20261001). Snapshot tip: `7dbb9e7b2`.

## Observation

- Stage 0 artifacts present; `replay-check.yaml` records `pass: true` (8/8
  successful DP+replay vectors after seed scan); cutoff `c=4`, `N=96` frozen
  for n=17 before Stage 1; modeled uniform E≈8.80 written in
  `uniform-baseline-plan.yaml`.
- Nine runs under `runs/`: Stage0 `RUN-BINSTD-09f640`, `RUN-BINSTD-f17ead`;
  Stage1 `RUN-BINSTD-6a2a20` (DP), `811f0f` (uniform), `14d961` (HW);
  Stage2 `ba45f7`/`dcf12a`/`9c2e6c` (n=23 arms), `b34e25` (second cutoff).
  Manifests `completed_valid`; `certificate.kind` ∈ {`decomposition`,`none`};
  decomposition `verified: true` when relation_count>0; pass_rate=1.0.
- Stage 1 (n=17, m=2, attempts=250): counts DP=31, uniform=38,
  HW_filter_only=18. Rates 0.124 / 0.152 / 0.072.
- Stage 2 (n=23): counts DP=2, uniform=4, HW=6. Second cutoff c=5 at n=17:
  DP relations=14. m=3 skipped (`m3_status` disclosed).
- No Bedrock. No break / rho / exponent / n=131-transfer text in manifests.

## Comparison

- Blind re-derivation (from freeze + counts; not from implementation):
  - E_uni = 250·96²/(2·130972) ≈ **8.7958** (matches Stage-0 plan).
  - n=17 ratios: 31/38≈**0.8158**, 31/18≈**1.722**, 18/38≈**0.474**.
  - n=23 ratios: 2/4=**0.5**, 2/6≈**0.333**, 6/4=**1.5**.
- HEUR-H1 band [0.7,1.4]: n=17 has DP/uni in-band; DP/HW and HW/uni out.
  n=23 all three out. Out-of-band **directions disagree** across cells
  (n=17 suggests HW depletion vs uniform; n=23 has HW highest among tiny
  counts).
- Uniform baseline: observed 38 vs modeled ≈8.80 → relative error ≈**3.32**.
  Instrument control **fails** under the Stage-0 modeled formula.
- Permutation p-values (producer): DP vs uni ≈0.46; DP vs HW ≈0.075;
  HW vs uni ≈0.0055 (n=17 only).
- Replay-cost (DP arm, n=17): mean≈14.0 steps, max=83 (toy; not 2^25.27).

## Inference

- Validity of the run set is acceptable for a **refine** decision: schema,
  certificates, Stage-0-before-1 ordering, and claim boundary hold.
- HEUR-H1 / DO-1 **cannot** be supported: (i) uniform baseline fails;
  (ii) not all pairwise ratios in band.
- H_alt **cannot** be declared: two-cell out-of-band directions disagree,
  and n=23 counts {2,4,6} are noise-scale under E≈O(1).
- Strongest reading: **instrument / baseline / power defect** — repair the
  modeled success probability (ordered mitt vs unordered |F|^m/(m!|G|),
  sampling measure on E vs prime-order subgroup) and re-run with adequate
  expected counts at the second cell. Do **not** reject_scoped the
  independence heuristic from this unreplicated empirical_only package.
- Preferred official transition: **refine**; H/EXP `approved` → `analyzed`;
  strength **preliminary**; no KN-FIND.

## Limitation

- Toy tier only (n∈{17,23}); cutoff denser than 1/√(2^n) due to short
  Bailey cycles (disclosed Stage-0 confounder).
- Uniform baseline model disagrees with measurement by factor ~4.
- n=23 underpowered for ratio tests.
- m=3 not run.
- Coordinator-direct review (PD-1) and same-session producer (PD-2).
- No n=131 transfer; no break; no exponent.
