---
id: KN-FIND-7f2a1c
type: internal_finding
title: "An estimator's reference must be fixed independently of the sample it scores: the unpaired-intercept defect and the self-conditioned-null defect are two instances of one family, and each returned a confident number with no power"
tags:
- estimator-design
- calibration
- null-object
- controls-before-belief
- reference-measure
- extrapolation
- intercept-slope-pairing
- self-conditioning
- instrument-defect
- experiment-design
- methodology
- derivation
- isogeny
- cost-model
- toy-scale
- scoped-negative
confidence: established
confidence_note: >-
  `established` applies to the TWO DERIVATIONS and to their committed instances,
  each of which is elementary and each of which was reached independently by two
  reviewers in separate sessions by different arithmetic. It applies to NOTHING
  ELSE. In particular it does not attach to any cost figure, to any margin, to
  Heuristic 1, to the p^{1/3+o(1)} exponent, or to the concrete threat against any
  parameter set - all of which are untouched by this entry and remain exactly where
  their own records leave them. The evidence record that carries the second
  instance (EV-PEC-7d8de9) has strength `inconclusive`; that is not a contradiction,
  because what is promoted here is the LEMMA, which stands on its own derivation,
  and not the batch's statistics, which do not.
internal_refs:
- H-P13-001
- EV-PEC-857664
- EV-PEC-7d8de9
- EXP-PEC-6be870
- EXP-PEC-49c773
- EXP-HEUR-d640d9
- EXP-PEC-d7979c
- DEC-20260802-8227b9
- DEC-20260802-48c72c
- DEC-20260802-611354
proof_status: derivation
proof_refs:
- coordination/goals/GOAL-P13-001/batches/BATCH-003/reviews/TASK-20260802-8e00fe/red_team_report.yaml
- coordination/goals/GOAL-P13-001/batches/BATCH-003/reviews/TASK-20260802-c50ea2/validation_report.yaml
- coordination/goals/GOAL-P13-001/batches/BATCH-004/reviews/TASK-20260802-cd08cd/validation_report.yaml
- coordination/goals/GOAL-P13-001/batches/BATCH-004/reviews/TASK-20260802-44c6a2/red_team_report.yaml
- experiments/EXP-PEC-49c773/runs/RUN-PEC-49c773-a/raw-result.json
- experiments/EXP-HEUR-d640d9/runs/RUN-HEUR-d640d9-a/raw-result.json
- experiments/EXP-HEUR-d640d9/implementation/heuristic_tail.py
- experiments/EXP-PEC-6be870/implementation/per_entry_cost.py
added: 2026-08-03
superseded_by: null
---

## The general statement

> A calibration or rejection statistic is meaningful only against a reference
> that is fixed **independently of the sample it is applied to**. If the
> reference is derived from the sample's own realised values — whether by
> discarding half of a fit and re-supplying the missing half by assumption, or by
> evaluating a null probability at the outcome itself — the statistic is not
> centred under the model it claims to test, and it will report a confident
> number that carries no information about that model.

This is not a new idea in statistics. It is recorded here because **this
programme has now built two separate instruments that violate it, in two
different batches, under two independently frozen contracts, and neither was
caught before execution.** Both were caught only by null objects and by
independent review, and in both cases the number that emerged first looked like a
finding.

The two instances below are the derivations. The general statement above is what
they have in common, and it is the promotable object.

---

## Instance 1 — the unpaired intercept (`EXP-PEC-6be870` → `EXP-PEC-49c773`)

**The lemma.**

> An intercept is only meaningful **paired with the slope of the same fit of the
> same series over the same window.** A slope-only calibration law reports **zero
> overhead for an object carrying a large constant one.**

**The derivation.** A fitted cost curve `log2 cost(ell) = log2 A + gamma *
log2(ell)` has two parameters. An extrapolation law that maps only `gamma`
forward and re-supplies `A` by convention (implicitly `A = 1`) is not
extrapolating the fitted object; it is extrapolating a different object that
happens to share a slope. For an object whose cost is `O(1)` in `ell` the true
slope is zero, so a slope-only law returns "no overhead" regardless of how large
the constant is. The failure is not approximate and not asymptotic — it is exact,
and it is worst precisely where the constant dominates.

**The committed counterexample.** The pre-registered law was applied to the run's
own null object, whose per-entry cost is `O(1)` in `ell` **by construction** and
which was measured at roughly `2^12.3` counted field multiplications per entry
against an assumed 1. The superseded law **misses that object's known level by up
to 12.605090 bits and fails at every one of its ten evaluation points.** The
corrected, pairing-respecting law passes the same gate at a worst miss of
0.271670 bits of a 0.75-bit tolerance. Both reviewers recomputed the corrected
value independently and agreed to about 1e-16.

**The second instance, and why it makes the rule load-bearing rather than
merely correct.** Anomaly A-3 — a window-dependent shift in the fitted exponent —
looked like a 2.4-bit excursion **outside** the published bracket when the
intercept was left unpaired. Correctly paired, the higher slope arrives with a
lower intercept and the two nearly cancel: the same anomaly is worth **1.007
bits, inside the bracket.** Deleting the pairing rule re-creates the excursion.
So the rule is not a stylistic preference about how to report a fit; it is what
determines whether an observed anomaly is an exponent revision or an
implementation artifact.

**What Instance 1 does not say.** It says nothing about the *value* of any
overhead constant, and **no such value appears in this entry, deliberately** — a
caveated figure placed in a curated corpus will be quoted without its caveats.
The citable form of that constant, its bracket, and its eight mandatory
attachments live in `DEC-20260802-48c72c` and in `H-P13-001`, and they travel
together or not at all.

---

## Instance 2 — the self-conditioned null (`EXP-HEUR-d640d9`)

**The lemma.**

> A null probability evaluated at the sample's **own realised value** is not a
> null. The event being tested and the quantity conditioning it are then the same
> random variable, the estimator is self-conditioned, and its expectation under
> the model it claims to test is not zero.

**The derivation, in the two forms two independent reviewers reached it.**

Let `n` be a positive integer random variable and consider testing "`n` behaves
like a uniform random integer" by comparing `1{n even}` against
`q(n) = floor(n/2)/n`. Note what `q(n)` is: the probability that a *different*
uniform integer in `[1, n]` is even. It is not the probability that `n` itself is
even.

*Form A (exact decomposition).*

```
E[ 1{n even} − floor(n/2)/n ]  =  (1/2)(P(even) − P(odd))  +  E[ 1{odd} / (2n) ]
```

The second term is **strictly positive** for any distribution with mass on small
odd values. The statistic therefore measures a construction artifact plus the
parity signal, with no way to separate them.

*Form B (tabulated bias).* For `n` uniform on `[1, X]`, `E[1{n even}] −
E[floor(n/2)/n]` equals `+0.2500` at `X=2`, `+0.0556` at `X=3`, `+0.0533` at
`X=5`, `+0.0483` at `X=7`, `+0.0437` at `X=9`. The bias is largest exactly where
the support is smallest — i.e. exactly in the toy regime where such an
enumeration is feasible.

**The committed counterexample — and it is the run's own.** The frozen contract
carried a second null arm in which a *bona fide* uniform random integer is pushed
through the identical estimator. It returns
**`z = +16.818982749412662` to `+19.520138`, in 200 of 200 replications.** That
is the estimator's zero point for a single-realisation object. The arithmetic
object under test scored `+8.645103378616307` — *below* the artifact floor, not
above a null. Data generated with the arithmetic removed entirely score higher
than the arithmetic data do.

**Exact decomposition of the observed excess** (independent recomputation from
the committed raw result, in rational arithmetic): a parity term of
`−0.09679849` and a self-conditioning offset of `+0.14831138`, summing to
`+0.05151289` and matching the run's own reported difference to eight decimals.
**64.2 per cent of the offset comes from a single atom** — the smallest value of
the statistic's support.

**The sign consequence.** The reported constant factor of `+0.1972` bits reverses
to `−0.1900` bits when the size scale is taken **exogenously** rather than read
off the sample. Neither number is a property of the object; they are two readings
of an uncentred estimator, and their disagreement is the finding.

---

## The companion failure mode: a reference measure chosen by assumption

Recorded here because it surfaced in the **same batch, in the same package**, and
because it is the same error one level up: not a mis-derived reference *value*,
but a mis-chosen reference *measure*.

A goodness-of-fit test was run against the measure the contract *asserted* the
sampler targets, rather than the measure the sampler *provably* equilibrates to.
The measured signature separates the two cases cleanly and is worth recording as
a diagnostic:

| walk length | mean TV to the asserted reference | mean TV to the true stationary measure |
|---|---|---|
| 1× | 0.13044 | 0.03485 |
| 3× | 0.12782 | 0.01102 |
| 10× | 0.12752 | 0.01055 |

with a sampling-noise floor of `0.00846`. **Convergence to a non-zero limit
against one reference and decay to the noise floor against another is the
signature of a chain that has mixed to the wrong reference — the exact opposite
of an under-mixing signature.** A verdict of "sampler rejected at the tested
lengths" wrongly implies a longer walk might pass; no walk length repairs a
reference-measure error.

**A second, cheaper tell in the same measurement.** The aggregated rejection
statistic was identical to the last printed digit at all three walk lengths, and
that identity is arithmetic rather than empirical: the statistic equals
`2 · 288 · ln(10001) = 5305.2136513784735` against a committed
`5305.213651378483`, i.e. every rejecting prime is pinned at the Monte-Carlo
resolution floor and the statistic is a re-encoding of the rejection count with
**no resolution left**. A quantity that is exactly `2 · (count) · ln(1/floor)` is
saturated, and "flat across three conditions" is then a censored measurement, not
an informative one.

---

## Why this is one finding and not two

Both defects have the same shape: **the reference was taken from the object being
scored.** Instance 1 took the intercept from a convention instead of from the
fit that produced the slope; Instance 2 took the null probability from the
outcome itself; the companion took the measure from an assertion instead of from
the chain. In all three the resulting statistic was *arithmetically correct*, was
*computed exactly as frozen*, produced a *large and confident number*, and had
**no power against the hypothesis it was written to test.**

That is why "the code is right" and "the number reproduces bit-identically"
cannot be the end of a review, and both were true here in every case.

---

## The operational rules this supports

1. **Pair the intercept with the slope of the same fit, same series, same
   window.** Any law that maps one and re-supplies the other by convention is
   defective until the convention is itself measured.
2. **Fix the null's reference exogenously.** If a null probability is a function
   of the sample's realised value, the arm is calibrated by construction and
   cannot detect its own bias. Pre-register the null as the **empirical
   distribution of the statistic on a genuine null object**, never as an analytic
   zero.
3. **Run the null in the reading the primary arm actually uses.** Here the
   calibration arm that exonerated the instrument held the reference fixed and
   re-drew only the outcome — a reading *unavailable* to the arithmetic object,
   which has exactly one number per sample. Reporting the reading that matches
   the primary arm is what made the defect visible.
4. **Check for saturation before reading flatness.** If an aggregated statistic
   equals a closed form in the rejection count and the resolution floor, it has
   no resolution and cannot support a trend claim in either direction.
5. **A null object placed inside a falsification criterion can only subtract
   power.** Where the null shares the defect by construction — as any
   single-realisation null must share a self-conditioning offset — the criterion
   is *structurally unable to fire* against the leading failure mode. Such a null
   belongs in the mechanism-attribution column, reported beside a finding, not
   able to veto one.

---

## What this entry does not settle

- **Nothing about Heuristic 1, in either direction.** The measurements that
  exposed Instance 2 reached `u ∈ [0.2354, 3.1699]` against an operating point of
  `u ≈ 13.1` where `ρ(13) ≈ 2^-60`. The tail has zero experimental resolution
  there, structurally. A defective instrument in the body is not evidence about
  the tail.
- **Nothing about the attack, any margin, or any concrete threat.** Those sit in
  `H-P13-001` and are unmoved. No cost constant appears here.
- **It does not close the lane it disturbed.** The parity question at the small
  prime is **unmeasured, not answered**: the instrument that probed it had no
  power, and the corrected statement — that the observed value sits *below* the
  artifact floor — is confounded in the other direction, because the arithmetic
  and synthetic arms have different size distributions. A centred, size-free
  statistic is still required.
- **Both instances are toy-scale.** The single atom carrying 64 per cent of
  Instance 2's offset has measured mass `Θ(p^{-1/2+o(1)})` (fitted exponent
  `−0.4587` over 299 primes), of order `1e-34` at cryptographic size, and the
  reference-measure gap of the companion decays at the same rate. **These are
  defects of the instruments, real at the scale they were run and with no
  cryptographic-scale analogue.** Neither may be presented as a fact about
  cryptographic parameters (AGENTS.md rule 7).
- **No `review-breakthrough` review exists.** Under
  `INFAMEND-20260802-P13-002` every policy alias in this harness falls back to one
  inherited model, so the non-degradable tier of AGENTS.md rule 12 is
  unavailable. This entry is a derivation, not a closure result.

## Attribution

Instance 1's lemma and its counterexample came from the BATCH-002 and BATCH-003
independent reviewers (`TASK-20260802-96d908`, `TASK-20260802-9ade2e`,
`TASK-20260802-8e00fe`, `TASK-20260802-c50ea2`), and the pairing rule was adopted
as official in `DEC-20260802-48c72c`. Instance 2 and the companion
reference-measure diagnosis came from the BATCH-004 reviewers
(`TASK-20260802-cd08cd`, `TASK-20260802-44c6a2`), who reached the same defect
independently and by different arithmetic in separate sessions. The Red Team
additionally **withdrew its own BATCH-001 control** on discovering that, run as
it had specified it, that control would have manufactured a false falsification —
recorded because retracting one's own instrument against one's own prior
objection is the behaviour that produced this entry.

The Executors implemented both frozen formulas verbatim, ran every pre-registered
null, reported the void, attempted no repair, and disclosed the readings that made
the defects visible. **Both defects are contract-design defects and both belong to
the Coordinator who froze them.**
