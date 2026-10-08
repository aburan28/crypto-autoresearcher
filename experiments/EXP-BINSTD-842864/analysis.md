# Analysis — EXP-BINSTD-842864 / H-BINSTD-944a66

Review plan: `experiments/EXP-BINSTD-842864/review/review-plan.yaml`
(`REVIEW-BINSTD-842864-20261001`). Producer: `TASK-20261001-25b6dd`
(branch tip at review start `7c7783187`; implementation commit cited
in execution_report `ab1d0bdef`). Evidence: `EV-BINSTD-2d41c3`.
Decision: `DEC-20261001-685b3f`.

Class: **structural_certificate / enumeration measurement** (exact
Rolle-pruned Weil-polynomial census over \(\mathbb{F}_2\) for
\(131 \mid h(3)\), with LMFDB unfiltered completeness control). No
ECDLP attack, no break, no Jacobian sufficiency, no rho
competitiveness, no exponent-moving claim.
`certificate.kind=none` on all run manifests.

---

## Observation

**Validity.** Eight runs total: six `completed_valid`, two
`failed_infrastructure`, zero `invalid`:

| Run | Stage / arm | Status | Primary metrics |
| --- | --- | --- | --- |
| `RUN-BINSTD-e09cbb` | 0 ceilings | `completed_valid` | ceilings 6725/39201; multiples 51/299 |
| `RUN-BINSTD-0c9eef` | 0 baseline g≤4 | `completed_valid` | unfiltered 5,35,215,1645; filtered 0 |
| `RUN-BINSTD-901ffc` | 1 unfiltered g=5 | `completed_valid` | classes 14325=LMFDB; amb=0; tests≈1.98e7; wall≈7159s |
| `RUN-BINSTD-fe7020` | 1 filtered g=5 | `completed_valid` | hit_count=24; amb=0; tests≈7.0e6; wall≈2050s |
| `RUN-BINSTD-353c72` | 1 sympy + dual-box | `completed_valid` | 24/24 hits agree; sample 10k/10k agree on dims 5 and 6 |
| `RUN-BINSTD-839c43` | 2 nearby-object | `completed_valid` | mod5 finds 5-pt; mod1=unfiltered g=1..3; surface only @19 |
| `RUN-BINSTD-69747c` | 1 unfiltered g=6 | `failed_infrastructure` | partial 99/164937 classes; ~5.6e6 tests; ~3044s; timed_out |
| `RUN-BINSTD-eb2003` | 1 filtered g=6 | `failed_infrastructure` | not_launched after IMP-H1 |

Manifest metrics agree with stage YAML summaries and
`execution_report.yaml`. `n_runs=8 ≤ maximum_runs=12`. Deterministic
enumeration (seed-free) except dual-box sample seed 0.
`certificate.kind=none` with `verified: true` on every manifest. No
Bedrock. Producer sets observations-only / no break.

**Stage 0.** Frozen before Stage 1 claims:
`ceilings-and-multiples.yaml` match_g5/match_g6 true;
`baseline-g4-reproduction.yaml` all_unfiltered_match / all_filtered_zero /
all_ambiguous_zero true. Protocol deviation disclosed: Rolle DFS reports
`exact_tests_performed` rather than exact_targets.py head-product
`candidates_scanned` (104/234220); class counts and filtered zeros remain
the comparable metrics. Numerical `weil_census.py` not imported.

**Stage 1 (g=5 complete).** Unfiltered class count 14325 matches LMFDB;
`ambiguous_count=0`. Filtered modulus-131 census yields **24 hits**,
each with \(P,h,N_r,a_r\); sympy re-verification
`all_hits_agree=true` (24/24); dual-box random sample
`all_agree` on dims 5 and 6 (10k each). Several hits have
`all_a_r_nonnegative=false` (necessary Jacobian screen fails); others
pass the necessary screen only — **never upgraded to "is a Jacobian"**
(`jacobian_sufficiency_claimed: false` on every hit).

**Stage 1 (g=6 incomplete — IMP-H1).** Unfiltered run stopped after
99/164937 LMFDB classes (~5.6e6 exact tests, ~3044s wall). Linear
projection ~1409h (producer cites ~1377h) ≫ advisory 86400s and ≫
HEUR-H1 modeled "hours". Recorded `failed_infrastructure`, **not
outcome A**. Filtered g=6 not launched. Partial prefix reports
`ambiguous_count=0` on explored nodes only — not a completeness claim.

**Stage 2.** Nearby-object controls pass:
`mod5_finds_5_point=true`; mod1 equals unfiltered at g=1,2,3;
`surface_only_19_observed=true` among toy ladder
{17,19,23,29,31,37,41}. `no_break_claim: true`.

---

## Comparison

Blind re-derivation this review session (from hypothesis / specification
parameters; without reading producer implementation for the quantities):

| Quantity | Predicted / frozen | Recomputed | Match |
| --- | --- | --- | --- |
| Multiples of 131 ≤ 6725 (g=5) | 51 | 6725//131 = 51 | yes |
| Multiples of 131 ≤ 39201 (g=6) | 299 | 39201//131 = 299 | yes |
| Unfiltered g=1..4 | 5,35,215,1645 | measured match | yes |
| Unfiltered g=5 | 14325 | 14325 | yes |
| Unfiltered g=6 | 164937 | incomplete (99 partial) | infra |
| Filtered hits g≤4 | 0 | 0 | yes |
| Filtered hits g=5 | no direction | 24 | measured |
| Ambiguous g≤5 | 0 | 0 | yes |
| Sympy vs integer Sturm (24 hits) | agree | 24/24 | yes |
| Dual-box sample dims 5,6 | agree | 10k/10k each | yes |
| g=6 wall projection | infra ≫ hours | ~1409h linear | yes (infra) |
| Stage 2 mod5 / mod1 / surface@19 | pass | pass | yes |

Success-criterion mapping:

- **Not DO-A** (exclusion to dim 6): g=5 already has 24 hits; g=6 incomplete.
- **DO-B** at g=5: nonempty sympy-verified hit list with LMFDB match and amb=0.
- **Not DO-C** at completed dims: no unfiltered mismatch / amb>0 through g=5.
- **Not DO-D**: g≤4 baseline reproduction passed.
- **DO-E** at g=6: `failed_infrastructure` under IMP-H1-runtime-g6.

HEUR-H1 runtime advisory: g=5 wall ~7159s is order-compatible with
modeled "minutes–hours"; g=6 projection ~10³ hours under-predicted
modeled "hours". Timeout alone is infrastructure (hypothesis
assumption + AGENTS.md rule 3), not H1 math falsification; complete
level-(g−1) survivor count vs 10×14325 was not obtained.

---

## Inference

Stages 0 + Stage 1(g=5) + Stage 2 package is **valid**. Stage 1(g=6)
is infrastructure-incomplete and contributes **no mathematical
exclusion**.

Scoped reading licensed by the data:

1. **Outcome B at dimension 5**: there exist (at least) 24 isogeny
   classes of abelian varieties over \(\mathbb{F}_2\) of dimension 5
   with \(131 \mid \#A(\mathbb{F}_2)\), each sympy-agreed, under an
   unfiltered completeness control that matches LMFDB 14325 with
   `ambiguous_count=0`.
2. **Outcome A (exclusion through dimension 6) is not available** —
   already contradicted at g=5 by the hit list, and separately blocked
   at g=6 by IMP-H1 infrastructure.
3. **No Jacobian / break / rho / exponent claim** is licensed.
4. **HEUR-H1 runtime** advisory needs amendment (filters / parallelism /
   longer wall) before a g=6 retry; do not reject_scoped H1 from timeout.

Official decision: **refine** (DO-B follow-on for Jacobian-or-not /
non-linear-base reading of the 24 hits, plus protocol_amendment path
to clear IMP-H1 for any g=6 completion attempt). Strength
**preliminary** (g=5 census complete with controls; single unreplicated
package; Coordinator-direct PD-1; g=6 incomplete). Hypothesis
`approved → analyzed`. Experiment `approved → analyzed`. No KN-FIND
(decision is refine; strength below replicated/strong).

---

## Limitation

- Scope: exact census over \(\mathbb{F}_2\), dimensions ≤5 complete,
  dimension 6 incomplete; modulus 131; pure-Python integer Sturm +
  sympy re-verify; LMFDB counts inherited from IDEA retrieval (not
  re-fetched this session).
- g=6 contributes infrastructure signal only — never cite partial
  99/164937 as exclusion or as LMFDB mismatch.
- `a_r >= 0` is a necessary Jacobian screen only; several hits fail it;
  none are claimed to be Jacobians.
- Hit utility constrained by torus-row pricing companion
  (IDEA-20260926-6f2601); outcome B is not a factor base.
- HEUR-H1 math falsification threshold (survivors >10×14325) not
  scored on a completed g=6 census.
- Coordinator-direct review without independent validator/red-team
  (PD-1); single unreplicated package; manifests dirty-at-write.
- No break; no rho; no exponent; no ECC2K-130 attack claim.
- Transfer beyond dim≤5 exact census / dim-6 infra note is
  unvalidated.
