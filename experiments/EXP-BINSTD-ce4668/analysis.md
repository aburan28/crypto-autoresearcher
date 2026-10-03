# Analysis — EXP-BINSTD-ce4668 / H-BINSTD-533de4

Review plan: `experiments/EXP-BINSTD-ce4668/review/review-plan.yaml`
(`REVIEW-BINSTD-ce4668-20261003`). Producer: `TASK-20261003-e3df30`
(snapshot archive `TASK-20261003-a23e07`; producer tip
`ebefdc9af5bee46e3737b342cd9ee5002b6bc77e` on
`cursor/run-binstd-ce4668-stages01-3601`). Evidence: `EV-BINSTD-163b42`.
Decision: `DEC-20261003-8939f2`.

Class: **measurement** (toy matched-dim poly↔normal
`usable_dimensions` basis-swap meter). No ECDLP attack, no break, no
exponent-moving claim, no n≥131 transfer. Scope: Stages 0–1 at n=17
only.

---

## Observation

**Validity.** Two runs, both `completed_valid` / check.py `PASS`;
`n_runs=2 ≤ maximum_runs=3`:

| Run | Stage | Outcome | Primary metrics |
| --- | --- | --- | --- |
| `RUN-BINSTD-c7c079` | 0 | `S0-FREEZE-OK` | freeze artifacts + Part-1 census + predicate pin |
| `RUN-BINSTD-27cb98` | 1 | `O-EQUIVALENT` | median_abs_diff=0.0; shuffle_median=0.0; pair_count=20 |

Manifest/`raw-result.json` metrics agree with `stage0/*` and
`stage1/*` artifact hashes (re-verified this review). `RESULTS.md`
names exactly one label (`**O-EQUIVALENT**`). No Bedrock.
`certificate.kind=none`. Claims `break=false`, `exponent_move=false`.
Stage 0 wall ≈0.107 s; Stage 1 wall ≈0.106 s (execution-receipt).
Producer execution commit `52472e22` (from environment/launch);
snapshot tip `ebefdc9af5`.

**Stage 0.** Frozen pair plan, preregistered predictions
(`HEUR-BINSTD-880180-H1`), Part-1 census, predicate pin present.
Census dual routes agree for n∈{17,23,31}:

- n=17: `ord_n(2)=8`; `usable_dimensions={8,9}`; `usable_cardinality=2`
- n=23: `ord_n(2)=11`; `usable_dimensions={11,12}`
- n=31: `ord_n(2)=5`; `usable_dimensions` includes {5,6,…,26}

Predicate pin hashes the Part-1 slice inside
`experiments/EXP-BINSTD-ce4668/implementation/run.py` (not the external
`part1_surface.py` path named as reference). Live
`predicate_source_hash()` matches the pin (`a6128dac…`); check.py
Stage-0 pin check passed.

**Stage 1.** Twenty matched pairs at n=17, dim band ℓ∈{2,3,4}
(=`[⌊17/8⌋,⌊17/4⌋]`). Histogram of abs_diff: `{0: 20}`. Median 0.0;
shuffle median 0.0. Control table: `predicate_pin_ok=true`,
`pairs_built=20`.

Panel inspection (all 20 pairs):

- `part1_usable = [8, 9]` on every pair
- `ell ∈ {2,3,4}` on every pair → **no pair has `ell ∈ U(17)`**
- `tau_stable_poly = false` and `tau_stable_normal = false` on every pair
- `usable_card_poly = 0` and `usable_card_normal = 0` on every pair

Under the frozen definition
`usable_card(V)=|U(n)| if τ-stable and dim(V)∈U(n) else 0`, both arms
score 0 by construction at this dim band.

---

## Comparison

Blind re-derivation (allowed sources only; before writing EV/DEC
prose conclusions):

1. `⌊17/8⌋=2`, `⌊17/4⌋=4`; census `U(17)={8,9}` →
   `dim_band ∩ U(17) = ∅`.
2. Median of twenty archived `abs_diff=0` values is 0.0 — matches
   `raw-result.json` / `RESULTS.md`.
3. Shuffle gate (`shuffle < observed when observed ≥ 1`) does not
   fire when observed=0; `shuffle_median=0` is consistent and
   non-discriminating.

Protocol label `O-EQUIVALENT` matches the preregistered dichotomic
rule (median = 0). HEUR-BINSTD-880180-H1's diverge prediction
(median ≥ 1) is numerically unmet, but the unmet prediction is
**vacuous**: the meter never produces a nonzero usable_card under the
authorized dim band at n=17.

Note: at n=31, `U(31) ∩ [⌊31/8⌋,⌊31/4⌋] = {5,6}` is nonempty — Stage 2
could be non-vacuous — but Stage 2 is **not authorized** under this
card (`DEC-20261003-d10361`).

---

## Inference

Stages 0–1 package is **valid**. The dichotomic meter decided
`O-EQUIVALENT` under the frozen protocol. That decision does **not**
justify a support reading of basis-invariance for the Part-1 usable
readout, nor a clean weaken/reject of HEUR-H1 as a statement about
coordinate dependence, because usable_card is identically zero for a
construction reason (dim band misses U(n); additionally no τ-stable
pair). Official decision: **refine** (non-vacuous dim sampling /
successor authorization). Hypothesis `approved→analyzed`. Experiment
`approved→analyzed`. Strength **inconclusive**. No break; no exponent;
no n≥131 transfer.

---

## Limitation

- Toy n=17 only; Stage 2 (n=23,31) not run.
- Vacuous zero meter: dim_band ∩ U(17)=∅ and no τ-stable pair.
- Single unreplicated producer package; Coordinator-direct review (PD-1).
- Shuffle null non-discriminating at observed median 0.
- Geometric-progression spans are a disclosed optimistic V family
  (specification).
- No Magma/Sage/AUXIN/Bedrock path used or required.
- IDEA-20261001-880180 claim text left immutable/`proposed`.
