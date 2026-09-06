---
id: KN-TECH-95a42b
type: technique
title: Check a permutation test's achievable p-value floor against its own multiple-comparison threshold at design time, before spending any compute
tags: [permutation-test, p-value-floor, multiple-comparison, holm-bonferroni, statistical-power, pre-registration, design-time-check, resolution-limit, methodology, statistics]
confidence: reported
complexity: >-
  not a cost model - a single arithmetic inequality (floor < alpha/m) that
  must be checked for every declared correction family before any draw is
  spent; the operative quantities are the null-sample size n and the family
  size m, not anything about the underlying effect
applicability: >-
  every program instrument that computes a rank-based or permutation-based
  p-value against a matched-null sample of size n, then declares a
  multiple-comparison correction (Bonferroni, Holm, or any family-wise
  error-rate method) over m>1 such tests
source_refs: [EV-MONO-849355, EXP-MONO-670aa6, CORR-20260831-d15d36, KN-TECH-7745e6, KN-FIND-031]
added: '2026-08-31'
superseded_by: null
---

## Method

A two-sided permutation p-value computed against `n` matched-null draws has
an ABSOLUTE FLOOR of `1/(n+1)`: the smallest possible numerator (the real
observation more extreme than every null draw) over the denominator
`n+1`. No possible outcome of the test -- not even the maximally extreme
one -- can produce a smaller p-value than this, REGARDLESS of the true
effect size.

Holm-Bonferroni (and plain Bonferroni) correction over a declared family of
`m` such tests rejects the smallest p-value in the family only if it falls
below `alpha/m` (Holm's most lenient, first-step threshold; plain
Bonferroni uses the same threshold for every test). If

```
1/(n+1) >= alpha/m
```

then **no test in the family can ever be corrected-significant, at any true
effect size** -- the declared decision rule is a constant function of the
data before a single draw is collected. This is not a data-dependent
judgment call or a power estimate; it is an unconditional arithmetic fact
about the chosen `(n, m, alpha)` triple, checkable in one line before any
compute is spent.

EXP-MONO-670aa6 was approved and executed with `n=200`, `m` in {49, 50,
98, 100} across four declared families, `alpha=0.05`. Floor `1/201 ≈
0.004975` exceeds every one of those families' thresholds (`alpha/m`
ranging `0.0005` to `0.00102`) by 5-10x. Independent review (validator and
red-team, both blind, both re-deriving the check from raw data before
reading any prior analysis) confirmed the archived data's actual minimum
p-value landed exactly on the floor, and confirmed no possible rearrangement
of the data could have crossed any of the four thresholds. The experiment's
entire declared primary metric (a mandatory pre-treatment null-object gate
plus a real-arm Holm-corrected test) carried zero discriminating power by
construction -- discovered only after the run completed, at the cost of a
full Executor dispatch and both review passes, because the check was never
run before approval.

**The same defect, unremarked, is present in an already-closed, already-
cited record's own text**: EXP-MONO-c819ba's Red Team review recommended,
and this program adopted verbatim, "200 null draws per cell... Bonferroni
over the full 96-comparison family" as evidence that no cell in that
run's own data survived correction. At `n=200`, `m=96`, that same
inequality holds (floor `0.004975 > alpha/96 = 0.000521`) — the sentence
was exactly as vacuous as EXP-MONO-670aa6's later, fully-executed failure,
just never separately spent 7200s of budget to demonstrate it. It did not
retroactively invalidate that record's overall conclusion (four other,
non-floor-limited lines of evidence carried the actual weight), but it
shows the pattern recurring within a single lane across two consecutive
experiments, unnoticed by two separate review rounds and this program's
own KN-TECH-7745e6 entry (which documents null-CALIBRATION failures at
small `n` but does not check its own worked Bonferroni example against
this orthogonal floor-vs-threshold constraint -- see that entry's
Addendum).

## The rule this establishes

**Before running a single draw, compute `1/(n+1)` and `alpha/m` for every
declared correction family, for every statistic, and require
`1/(n+1) < alpha/m` by a stated safety margin for the TIGHTEST family.**
This is a strictly cheaper check than KN-TECH-7745e6's bootstrap-
recalibration recipe (it requires no simulation, only arithmetic on the
planned `n` and `m`) and answers a different question: KN-TECH-7745e6 asks
"is my declared band's actual false-positive rate close to nominal?";
this check asks "can my declared test ever reject at all?" A design can
fail either, both, or neither independently -- EXP-MONO-c819ba failed the
first (band too loose, ~65% false-positive rate); EXP-MONO-670aa6 failed
the second (test structurally powerless). Both are design-time-checkable
before any compute is spent, and neither check substitutes for the other.

A design that fails this check is not necessarily unsalvageable: a
different combining procedure that pools evidence across the family
without per-test multiplicity correction (e.g. Fisher's combined-
probability test, or any other omnibus statistic computed once per family
rather than once per test) sidesteps the floor-vs-threshold problem
entirely, because it has no per-test correction threshold to be capped by.
Such a statistic should be PRE-REGISTERED alongside, not substituted
post-hoc for, the per-test test -- a post-hoc combining choice made after
seeing the per-test results is exactly the kind of after-the-fact
decision-rule change this program's own invalidation rules (and
AGENTS.md's evidence discipline generally) exist to prevent.

## Relation to KN-TECH-7745e6

KN-TECH-7745e6 documents a null-CALIBRATION failure (a band's actual
false-positive rate differing from its nominal rate, discovered by
bootstrap recalibration). This entry documents a distinct, ARITHMETIC
failure mode (a correction procedure's threshold falling below what the
chosen sample size can ever produce). Both belong to the same broader
discipline -- "check your instrument's actual operating characteristics
before trusting its verdict" -- and a properly designed experiment should
run both checks: KN-TECH-7745e6's four-step calibration bootstrap, AND
this entry's one-line floor-vs-threshold arithmetic, before any treatment
draw is computed.

## What this technique is not

This is not a claim that permutation tests or Holm-Bonferroni correction
are wrong in general, or that larger `n` always fixes the problem for a
fixed `m` (raising `n` to reduce the floor works, but so does reducing `m`
via a coarser combining statistic, or restructuring which comparisons are
declared as one "family"). It is a narrow, one-line, design-time check
that would have caught both of this lane's consecutive experiment
failures before either spent any compute, and a concrete alternative
(pre-registered panel-level combining) for when the check fails.

## Addendum (2026-08-31): the same discipline applies ACROSS a composite gate, not only within one test

EXP-MONO-b19c6b's own Stage-2 gate declared PASS only if six separate
tests (two Holm families plus four Fisher-combined checks) each showed no
significant result — each implicitly evaluated at the nominal `alpha`
independently. This is the SAME uncorrected-multiplicity mistake this
entry warns against, one level up: with six tests each at `alpha=0.05`
uncorrected, a genuinely well-calibrated instrument trips the gate by
chance on at least one of them roughly `1-(1-alpha)^6 ≈ 26.5%` of the
time per seed, not 5%. Disclosed and independently verified in
`CORR-20260831-d663e0`; empirically inconsequential for that specific
run (every observed statistic was far from either threshold), but a real
design defect for the general case. **The floor-vs-threshold check this
entry documents must be applied to EVERY test in a declared gate
individually, AND the gate's overall false-stop rate must itself be
corrected (Bonferroni or equivalent) across however many tests jointly
define "the gate passed."** A gate built from `k` sub-tests each at
`alpha` needs each evaluated at `alpha/k` (or an equivalent joint
correction) for the gate's own advertised false-stop rate to hold.
