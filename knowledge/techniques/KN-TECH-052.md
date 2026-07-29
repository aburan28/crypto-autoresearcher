---
id: KN-TECH-052
type: technique
title: Fitting and extrapolating cost exponents from bounded experiments
tags: [scaling-exponent, extrapolation, power-law, bootstrap, confidence-interval, model-selection, multiple-comparison, experimental-design, claim-tier, methodology, statistics, calibration, cross-domain]
confidence: reported
complexity: not a cost model - a discipline for producing and reporting cost exponents; the operative quantity is the tested parameter range, not the width of the confidence interval
applicability: every program claim of the form "cost scales as size^gamma", every comparison of a measured exponent against the rho baseline of 1/2, and every claim-tier assignment that rests on a fitted trend
source_refs: [KN-LIT-134, KN-LIT-135, KN-LIT-136, KN-LIT-137, KN-LIT-111, KN-LIT-123, KN-TECH-036, KN-TECH-049, KN-TECH-035]
added: 2026-07-25
superseded_by: null
---

## Method
The program's characteristic claim is that some measured cost grows as
`size^gamma`, and that `gamma` sits above or below a baseline exponent. Producing
such a claim honestly requires five steps, of which this program currently
performs the first two well.

1. **Measure across a range, with replication and seeds.** Done — the frozen
   protocols, deterministic seeds, and matched controls are the program's
   strongest asset.
2. **Quantify sampling uncertainty**, e.g. by bootstrap (`KN-LIT-134`). Done —
   `EXP-ICI-001` and `FINDING-PF-IC-001` report bootstrap intervals.
3. **Estimate properly and test against alternatives** (`KN-LIT-135`). A
   least-squares line through a log-log plot is a biased estimator and is not a
   test. The question is never "does a power law fit?" but "does it fit better
   than the specific alternatives I named in advance?" — a likelihood-ratio style
   comparison against competitors declared in the frozen protocol.
4. **State the range of validity as part of the claim** (`KN-LIT-135`'s `x_min`
   discipline). An exponent measured at `p <= 2^16` is a statement about
   `p <= 2^16`.
5. **Account for selection** (`KN-LIT-136`). An exponent reported from a wide
   screen of levers — positive or negative — must say how many comparisons it was
   drawn from.

## The distinction that does the work
**A confidence interval is not an extrapolation interval.** A bootstrap CI
describes how the estimate would move under resampling *from the tested
distribution at the tested scale*. It carries no information about behaviour
outside the tested range, because nothing in the resampling procedure has seen
that range.

This matters concretely. `FINDING-PF-IC-001` reports a total-cost exponent of
2.05 with 90% CI `[1.86, 2.29]` against rho's 0.5, measured at toy scale
(`p <= 2^16`, `m <= 3`, `d <= 24`). The correct reading is that the exponent is
tightly determined *at that scale* and that the gap to 0.5 is far larger than
sampling noise there. The incorrect reading — that the interval bounds the
crypto-scale exponent — would be a claim-tier violation
(`docs/claims-and-verification.md`) dressed as a statistic. The finding's own
scope section states this correctly; the discipline exists to keep it stated as
the result propagates.

Practical rule: **widening the tested parameter range is worth more than
narrowing the interval.** `KN-LIT-137` is the worked case — an in-sample-excellent
power-law fit gave the wrong prescription because of how the sweep was designed,
and was corrected by a larger and more systematic sweep rather than by better
statistics on the same data.

## Applicability limits
This is a reporting and inference discipline, not a source of cost models, and it
does not make an extrapolation valid. No amount of statistical care converts a
toy-scale measurement into a cryptographic-scale claim; the claim-tier ceiling is
not a statistical criterion and is not negotiable by better fitting. Where an
extrapolation is genuinely needed, the available checks are external: calibration
against public record computations (`KN-TECH-036`, `KN-TECH-049`) and a stated
mechanism for why the fitted form should persist outside the tested range.

Note also that `KN-LIT-135`'s estimators are for power-law **distributions**,
while the program fits power-law **relations**; the standard transfers, the
machinery does not (see that entry's scope caveat).

## Verified vs reported
All four source entries (`KN-LIT-134`-`137`) are `citation_verified: web`,
written under an egress policy that blocked every direct fetch, so their
bibliographic details are corroborated across primary-index listings but their
full texts were not read here. Efron and Benjamini-Hochberg are recorded at
`confidence: established` on their textbook status, not on a reading performed
for this corpus.

The five-step structure, the CI-versus-extrapolation distinction, and the
assessment of which steps this program currently performs are **this program's
own reasoning**, not claims imported from any of the four papers. The
characterisation of steps 1-2 as "done" is based on reading `EXP-ICI-001`,
`FINDING-PF-IC-001` and the frozen protocols, and has not been independently
audited; steps 3-5 are not currently evidenced anywhere in the ledger, which is
an observation about the record rather than a claim that they were not performed.
