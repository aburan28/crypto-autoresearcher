# CTRL-VALUESHUFFLE re-analysed with the circular arm removed

Coordinator analysis artifact. Discharges `CORR-20260807-f551a5` required-action
item 2. **Producer artifact, pre-independent-review.** No evidence record is
written here and no status moves.

## Why this re-analysis exists

`CORR-20260807-f551a5` finding 2 recorded a defect in a control this Coordinator
designed and approved: `CTRL-VALUESHUFFLE` destroys value–N association by
construction, and `RT-20260807-743198` item 3b had already established that four
functionals — `order`, `full_liftable`, and `liftable_density` at W = p (W4001,
W6007) — are monotone *because* they are coupled to N. Their reversal under the
shuffle is therefore guaranteed before any data is drawn, and they contributed
19.12 of the 57.64-cell gap: **33.2% of the measured effect was mechanically
forced.**

The correction called for re-reporting the statistic with those four excluded, as
a free re-analysis of committed artifacts. This is that re-analysis. It draws no
new replicate and re-measures nothing; it re-sums the committed per-replicate
`by_functional` counts over a restricted functional set.

## Result

| | frozen primary | corrected (N-coupled excluded) |
|---|---|---|
| cells in frame | 144 | **120** |
| observed residue | 50 | **50** |
| null min / median / max | 89 / 108 / 123 | **71 / 89 / 102** |
| null mean (sd) | 107.635 (5.632) | **88.510 (5.174)** |
| \|observed − median\| | 58 | **39** |
| replicates at least as extreme | 0 of 200 | **0 of 200** |
| two-sided empirical p | 1/201 = 0.004975 | **1/201 = 0.004975** |
| observed below entire null support | yes | **yes** |

The four excluded functionals had observed residue **0**, so the observed count is
unchanged at 50; only the null moves.

## Reading

**The effect survives removal of its circular component.** With the mechanically
forced third removed, the observed value still lies **below the entire null
support** — 50 against a null minimum of 71 — and still no replicate of 200 comes
as close to the null median. The gap is 39 cells, about 7.5 null standard
deviations below the null mean.

So `CORR-20260807-f551a5` finding 2 weakens the control's *design* without
overturning its *result*. That was the honest possibility when the defect was
recorded, and it is the one that obtained.

Three things this does **not** change, carried forward verbatim:

1. **The direction is still inverted relative to the state name.** Real values
   produce *fewer* type-A reversals than shuffled ones (50 against a null median
   of 89 here). `STRUCTURE_PRESENT` must never be read as excess
   non-monotonicity from arithmetic structure.
2. **p = 1/201 is still the resolution floor**, a bound and not an estimate. The
   observed value sitting below the null minimum means more replicates would push
   the bound lower, not that the result is marginal.
3. **The m = 3 localization stays withdrawn.** Excluding N-coupled functionals
   does not revive it; `sumset_m3` and `sumset_eff_m3` were unaffected by the
   exclusion and remain unseparated at p ≈ 0.26.

## What is now known, and what is not

Established across `CORR-20260807-732541`, `RT-20260807-743198` and this artifact,
all at toy scale (p ∈ {4001, 6007}), `claim_tier: toy`, `sota_delta` zero:

- The ladder's non-monotonicity is **not** Monte-Carlo noise — the exact
  zero-MC-error closed form reproduces the identical count, 74 against 74.
- It is **not** a pure artifact of N-band blocking geometry acting on an
  arbitrary value multiset — the shuffled null generates far *more*
  non-monotonicity than the data, and the separation survives removing the one
  arm that was circular.
- It is **not** localized to the m = 3 sum-set family at this replicate count.

**No mechanism is identified.** Three candidate explanations have been eliminated
and none has been confirmed. That is the accurate state of this line, and it
licenses no claim about isogeny-class structure or ECDLP cost.

## Status

Under `AGENTS.md` rule 12 this line requires review at `review-breakthrough`
before any evidence record is written — a contradiction between a validated
execution report and two independent reviews, compounded by a
Coordinator-identified defect in a control this Coordinator approved. That review
is dispatched; this artifact is one of its inputs and is explicitly **not** a
finding of record until it reports.

Artifacts read (none modified):
`experiments/EXP-INSTR-85b102/runs/RUN-INSTR-85b102-valueshuffle/valueshuffle-null.json`,
`.../reproduction-gate.json`.
