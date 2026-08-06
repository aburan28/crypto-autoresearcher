# PREREGISTRATION — TASK-20260805-8fa4c6 (RC-B)

Written and committed to the task working directory BEFORE either of the two
central comparison runs in STEP 4 was executed. The substrate-reproduction
run (STEP 1) and the two instrument-extension equivalence checks (STEP 2,
STEP 3) preceded this document, because they are prerequisite instrument
validation, not measurement of the two mechanism claims under test — the
handoff's own ordering (confirm substrate, then add instrumentation, then
prove equivalence, then measure) requires this. This file is written before
`RESULTS.json`'s comparison sections (a) and (b) exist.

## inference block

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  resolved_model: claude-sonnet-5
  fallback_used: true
  model_verified: false
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
```

## What is being tested

Two mechanism claims from the yoyo_sbox_v2->v3->v4 lineage (BATCH-008,
BATCH-009), re-run on rc8probe.c (BATCH-007 RANK 2, committed 1a0ad198), an
independently-authored codebase measuring the same yoyo W>=1 statistic:

- **Comparison (a)** (mirrors BATCH-008 / EV-AES-8b8dcf OBS-B8-2): at r=5,
  the k-byte prefix-zero event count, k=1,2,3,4, shows an obs/model excess
  present ONLY at k=4, essentially absent at k=1,2,3.
- **Comparison (b)** (mirrors BATCH-009 / EV-AES-e4c091 OBS-B9-3): at r=5,
  the W>=1 count under an ideal-permutation null-object substitution for the
  cipher is consistent with that null object's own analytic expectation,
  while the live cipher's W>=1 count is not — i.e. the excess does not
  survive cipher substitution.

## Exposure and why it is modest, not a full replication

Per the handoff, exposure is capped at 2^24-2^27, NOT the campaign's usual
2^30-2^33. This has a direct, disclosed consequence for statistical power
that is stated here BEFORE any run, not discovered after:

- BATCH-008's r=5 k=4 excess was ~13-14 events ABOVE a model expectation of
  ~1 event, measured at N=2^30. Model expectation scales linearly with N, so
  at N=2^27 (this task's ceiling for comparison (a)) the k=4 model
  expectation is ~0.125 events — an order of magnitude below 1. A test at
  this exposure has essentially no power to detect or refute the k=4 excess
  itself; it DOES have adequate power for the k=1,2,3 "absence" sub-claims,
  whose model counts (~2.1M, ~8.2K, ~32 respectively at N=2^27) are large
  enough for a meaningful ratio/z-test.
- BATCH-009's live-r=5 W>=1 excess was ~14 hits over a null model of ~1, at
  N=2^30. At N=2^24 (this task's exposure for comparison (b), chosen for the
  ideal-permutation arm's memory ceiling — see below), the expected excess
  under the SAME rate is ~14/64 ~ 0.22 events. This comparison is therefore
  ALSO expected to be underpowered for a definitive verdict; this is stated
  before running, not used after the fact to explain away a null result.

This is disclosed in advance so a null or ambiguous result at k=4 / W>=1 is
correctly attributed to POWER, never silently read as either confirmation
or refutation. A definitive non-replication signal, if it appears, would
have to show up as an EXCESS at k=1-3 that should not be there (comparison
a) or a COMPARABLE excess in the ideal-permutation arm (comparison b) — both
of which the chosen exposure CAN detect, because they do not require
observing the rare k=4/W>=1 event itself, only the well-populated control
cells.

## Exposure values (fixed before running)

- Comparison (a): N = 2^27 trials, one rc8probe `arm` run, `rand:<seed>`
  S-box, rounds=5, amask=1, smask=1, 4 worker threads (thread count does not
  affect final aggregate correctness, only wall-clock; verified by the
  STEP-2 equivalence proof using threads=2 and reproducing an existing
  threads=2 record bit-exactly — the aggregation code sums per-thread
  totals and does not depend on partition boundaries for correctness of the
  SUM, only for bit-exact reproduction of a specific prior run at its
  specific thread count).
- Comparison (b): N = 2^24 trials for BOTH the live-cipher `arm` run
  (rounds=5, amask=1, smask=1, threads=1) and the `armideal` run (amask=1,
  smask=1), using the SAME `seed` and `arm_id` values in both, chosen so the
  two runs' `seed_thread` values are identical by construction (`arm` with
  threads=1 computes `seed_thread = seed ^ (armid*C1) ^ (1*C2)`; `armideal`
  computes `seed_thread = seed ^ (armid*C1) ^ C2` — identical when
  threads=1, since `1*C2 == C2`). Because both the `arm` worker() and the
  new `run_ideal()` draw the plaintext pair and active-word swap with
  IDENTICAL code (same sm64 call order, same PW-based rejection logic) from
  an identical `seed_thread`, the plaintext/swap-target stream up to the
  point of the first cipher/oracle call is identical between the two arms
  by construction. This is a CODE-LEVEL claim, checkable by reading the two
  functions side by side; it is NOT independently verified by a digest-based
  run comparison (unlike BATCH-009's OBS-B9-3, which did run such a check)
  because that additional control was not budgeted. Recorded as a gap
  below.
  N=2^24 for the `armideal` arm is set by that mode's memory footprint: the
  perm128 table allocates for a hard cap of `4*N` pairs (worst case, one per
  oracle query), each pair 32 bytes, plus two open-addressed hash-index
  tables sized to the next power of two above `2*max_pairs`. At N=2^24 this
  totals ~4.3 GB, within the task's 8 GB budget with headroom; at N=2^25 the
  index-table sizing crosses a power-of-two boundary and totals ~8.6 GB,
  exceeding budget. N=2^24 is therefore the largest exposure in the
  instructed 2^24-2^27 range this implementation can run within budget for
  comparison (b).

## Metrics

- `model_k = (N - trivial) * 4 / 256^k` for k=1,2,3,4 (comparison a); same
  formula the campaign and rc8probe's own `null_expectation_analytic` field
  already use at k=4.
- `ratio_k = observed_k / model_k`.
- `z_k = (observed_k - model_k) / sqrt(model_k)` (Poisson normal
  approximation; reported as descriptive, not treated as exact for small
  model_k, e.g. k=4 here).
- Comparison (b): `W_ge1_nontrivial` and `null_expectation_analytic` (the
  existing rc8probe field, `(N-trivial)*4/2^32`) reported for both the live
  and ideal-permutation arms, plus each arm's own ratio to its own null
  model.

## Decision rule, fixed before measuring

**Comparison (a):**
- CONFIRMS BATCH-008's byte-locality finding (on this substrate, at this
  exposure) if, for k in {1,2,3}, `|z_k| < 3` (no significant deviation from
  model at the well-powered prefix lengths) — i.e. no byte-local excess is
  seen where BATCH-008 found none.
- Separately, the k=4 count and ratio are reported as a DESCRIPTIVE
  statistic only; given the ~0.125 expected-event floor at this exposure,
  no confirm/disconfirm verdict is drawn from k=4 alone. If k=4 happens to
  show a nonzero count, that is reported as consistent with (not proof of)
  the original finding's direction.
- FALSIFIES (would replicate the "shared-harness bug" concern) if any of
  k=1,2,3 shows `|z_k| >= 3`: a byte-local excess on THIS substrate would
  contradict BATCH-008's specific claim that the excess is not byte-local,
  since that claim was itself established only on the v2-v3-v4 lineage.

**Comparison (b):**
- CONFIRMS BATCH-009's finding (on this substrate, at this exposure) if the
  live-cipher arm's `W_ge1_nontrivial` count exceeds its
  `null_expectation_analytic` by a visibly larger margin (in ratio terms)
  than the ideal-permutation arm exceeds ITS OWN
  `null_expectation_analytic` — i.e. any elevation present is specific to
  the live cipher, not the ideal-permutation null object, even if absolute
  counts are small.
- FALSIFIES if the ideal-permutation arm shows an elevation over its own
  null model comparable to or exceeding the live cipher's elevation over
  its null model — this would mean the excess pattern survives cipher
  substitution on THIS substrate, directly contradicting BATCH-009's claim
  and corroborating the shared-harness risk BATCH-010 named.
- Given the ~0.22-event expected floor at N=2^24, a result of 0 hits in
  both arms, or 0-vs-1, is explicitly anticipated as the LIKELY outcome and
  will be reported as INCONCLUSIVE BY POWER, not as confirming either
  direction — this is stated here, before running, precisely so that
  outcome cannot later be read as a quiet confirmation.

## What would NOT be measured / acknowledged gaps, stated before running

- No digest-based empirical proof that the plaintext streams of the
  comparison-(b) live and ideal arms are bit-identical up to the cipher
  call (see above) — only the code-level argument. If budget remains after
  the two comparisons, this control may be added; if not, it is named in
  the final report as unreached, not silently assumed away.
- No replication of BATCH-008/009's r=10 decay-check arm or the paired
  trial-index (RC-11-style) analysis; out of scope for this task's two
  named comparisons.
- No claim about which specific mechanism (if any) produces the r=5
  excess; this task only checks whether two PRIOR mechanism findings
  replicate on an independent substrate.

## Certificate

`certificate.kind: none`. This is a pure measurement task; no discrete-log
solve or relation is claimed.

## Parse confirmation

This file is plain Markdown (not schema-validated JSON/YAML); it is
authored to be read in full alongside RESULTS.json, which IS
machine-parseable and is parsed in full (with `json.load`) as stated in its
own SELF_CHECK block before this task is reported complete.
