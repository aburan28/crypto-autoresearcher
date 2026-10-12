# Analysis — EXP-BINSTD-a8efe2 / H-BINSTD-340284

Review plan: `experiments/EXP-BINSTD-a8efe2/review/review-plan.yaml`
(`REVIEW-BINSTD-a8efe2-20261001`). Producer: `TASK-20261001-f5e965`
(package tip at review start ~`fd03ee0cf`; implementation commit
`b31c2ba6f`). Evidence: `EV-BINSTD-f9262a`. Decision:
`DEC-20261001-9c36b3`.

Class: **measurement** (encoder-level cost-attribution / structure
validation). No ECDLP attack, no break, no rho competitiveness claim, no
exponent-moving claim. No phi-transport / Hamming-weight sibling protocol.

---

## Observation

**Validity.** Five runs:

| Run | Stage | Status | Primary metrics |
| --- | --- | --- | --- |
| `RUN-BINSTD-54aa8c` | 0 | `completed_valid` | both irreducible; predictions before Stage 1; census pp=8/tp=7 |
| `RUN-BINSTD-ffab44` | 1 | `completed_valid` | `structural_fixture_pass=true`; per-arm `certificate_set_equality=true`; mean N_leaf ratio 0.991666…; mean clause_width_ratio 1.081967… |
| `RUN-BINSTD-53d976` | 2a | `completed_valid` | clause_width_ratio l6/l7/l8 = 1.7628… / 1.9770… / 2.1034… (all >1); substitution_variable_count_ratio = 1.0 all l |
| `RUN-BINSTD-7979df` | 3 | `completed_valid` | `discriminator_null_on_N_leaf_axis`; `unmatched_large_effect_any_cell=false`; `width_matched_all_in_band=true` |
| `RUN-BINSTD-ad5e6f` | 2b | `failed_infrastructure` | `instrument_unavailable` (WDSat absent); `valid=true` as infra receipt; **not** H1 falsification |

Manifest metrics agree with raw-result.json and with stage YAML/JSON
artifacts. `n_runs=5 ≤ maximum_runs=30`. Required stage0/1/2a/2b/3
artifacts present. Certificate kind is `none` on all runs (no solve claimed).
No Bedrock. Seeds `[20261001..20261005]` on Stages 1/2a/3.

**Stage 0.** Trinomial `x^9+x+1` and pentanomial `x^9+x^4+x^2+x+1` both
irreducible (Rabin checks recorded). Preregistered predictions committed
before Stage 1 (`committed_before_stage1: true`). Basis-type census:
ppBasis=8, tpBasis=7, other=0. Primary-text re-verification checklist
written; `primary_text_rows_verified: false` (obligation remains). OpenSSL
dump bit-label anomalies flagged (e.g. sect283r1 dump says 282) — anomaly
recording, not a Stage-0 fail.

**Stage 1.** Structural fixture passes on all 10 cells: core-variable
count and block partition identical across trinomial/pentanomial
(`ml` cores: l=3→9, l=4→12). Certificate equality is **per-arm**
encoder↔algebraic-oracle (producer deviation; cross-arm geometric tuple
identity deferred — requires excluded f37254 phi-transport). Normal-basis
arm constructible (`normal_element=3`) but structure-constant CNF encoder
not expanded; reported separately, not folded into ratios.

Blind recompute of Stage-1 planted ratios from the structural-fixture
report: cell ratios
`[1,1,1,1,1, 0.666…,1,1,1.25,1]`; **mean = 0.991666…** (matches
manifest); **spread min=0.666… max=1.25** — two l=4 cells leave the
preregistered [0.95,1.05] band. Mean clause_width_ratio = 1.081967…
(direction >1); at l=3 widths are identical (ratio 1.0); separation
appears at l=4 (~1.164).

**Stage 2a.** Encoder-level only (solver-free). Blind recompute from
`clause-width-summary.json` means:

| l | tri mean width | pent mean width | ratio | >1 |
| --- | --- | --- | --- | --- |
| 6 | 52.0 | 91.666… | 1.762820512820513 | yes |
| 7 | 87.222… | 172.444… | 1.9770700636942675 | yes |
| 8 | 136.444… | 287.0 | 2.1034201954397393 | yes |

Naive 5-vs-3 term ratio **MODELED** = 1.666… (poor predictor; not mixed
into measured columns). Seeds ≥5; instances 10 UNSAT-intent + 10
planted-SAT per arm status. Substitution-variable count ratios = 1.0 at
all three l (direction prediction "higher" **not** observed on this
proxy).

**Stage 3.** Fixture-scale unmatched vs width-matched relabelling.
`unmatched_large_effect_any_cell=false` on algebraic N_leaf (ratio vs
trinomial = 1.0 every cell). Unmatched **does** inflate clause_width_mean
(e.g. l=3: 6.0 → ~12–17). Width-matched stays in [0.9,1.1], but
`match_method: identity_fallback_after_rejection_sampling_exhausted` on
every cell — random width-matched sampling exhausted; control collapses
to identity. Stage-3 pent/tri N_leaf ratios include l=4 values
`1.535…, 1.25, 0.5, 1.25, 0.8` outside [0.95,1.05].

**Stage 2b.** Optional SAT arm: WDSat / CryptoMiniSat not on PATH;
`instrument_unavailable.yaml` written. Infrastructure (DO-5); asserts
nothing about H1/H2 mathematics.

---

## Comparison

Against `H-BINSTD-340284` / preregistered predictions and DOs:

| Criterion | Required | Observed |
| --- | --- | --- |
| Stage 0 both moduli irreducible | true | true |
| Predictions before Stage 1 | true | true |
| Structural fixture | pass | pass |
| Certificate equality | exact | true **per-arm**; cross-arm geometric deferred |
| N_leaf ratio band [0.95,1.05] | every cell (H1) | **mean** in band; **cells** leave band at l=4 |
| clause_width_ratio >1 | measurable | Stage 2a yes (1.76–2.10); Stage 1 weak/local |
| substitution_variable_count_ratio higher | consistent direction | **=1.0** all Stage 2a cells |
| Unmatched large N_leaf effect (H2 power) | required | **false** (discriminator_null) |
| Width-matched N_leaf in [0.9,1.1] | required | true, via **identity fallback** |
| Stage 2b | optional | instrument_unavailable (not falsification) |
| Break / exponent / phi / Hamming | forbidden | absent |

Maps to **DO-3** (discriminator powerless on algebraic N_leaf /
sparsity attribution not licensed) with **DO-5** (Stage 2b infra)
alongside. **Not DO-1** (requires discriminator pass). **Not DO-2** as a
clean H1 reject: cell-level N_leaf departures exist, but cross-arm
geometric instance identity is not certified without phi-transport, so
escalate-to-weaken needs a matched-instance refine first. **Not DO-4**
(fixture passed).

---

## Inference

Stages 0/1/2a/3 package is **valid**. Encoder-level clause_width
direction at Stage 2a (l∈{6,7,8}) is a clear measured observation
consistent with the c_leaf half of H1. The H2 unmatched-vs-width-matched
discriminator **fails as an N_leaf instrument**: invertible F₂-linear
relabelling preserves algebraic |solution set| (derivation), so unmatched
cannot show large N_leaf effect; width-matched fell to identity. Sparsity
attribution against IDEA-20260915-7ef636-style order effects is therefore
**not licensed** on the algebraic N_leaf axis at this fixture (DO-3).

Official reading: **refine** — (1) re-target the unmatched power check to
an observable unmatched *does* move (clause-width / SAT-order /
conflicts when Stage 2b clears); (2) optionally amend cross-arm instance
matching (phi-transport or shared algebraic instance) before treating
l=4 N_leaf cell outliers as H1 falsifiers; (3) do not reject_scoped from
missing WDSat. Hypothesis `approved` → `analyzed`. Strength
**inconclusive** on the joint H1∧H2 sparsity-attribution claim; Stage 2a
clause_width direction remains a scoped unreplicated observation only.

---

## Limitation

- Toy tier only: n=9, m=3, l≤8. No transfer to m≥131 / deployed curves.
- Single unreplicated producer package; Coordinator-direct PD-1 review.
- Certificate equality is per-arm, not cross-arm geometric.
- Width-matched control is identity_fallback — weak as a null.
- substitution_variable_count_ratio flat (1.0) — proxy miss.
- Stage 2b SAT conflict / seconds-per-leaf unmeasured (infra).
- Primary-text FIPS/ANSI re-verification of flagged census rows still open.
- Normal-basis structure-constant encoder not expanded.
- Manifests dirty-at-write at producer implementation commit.
- No break; no rho; no exponent; no phi-transport / Hamming-weight adjudication.
