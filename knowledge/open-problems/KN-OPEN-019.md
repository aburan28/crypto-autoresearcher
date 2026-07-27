---
id: KN-OPEN-019
type: open_problem
title: Is the information-set-decoding exponent stuck, and what would move it?
tags: [code-based, information-set-decoding, isd, exponent, syndrome-decoding, target-result-profile, lower-bound, open]
confidence: reported
status: open
source_refs: [KN-TECH-057, KN-LIT-7566, KN-LIT-7567, KN-LIT-3368, KN-LIT-3367, KN-LIT-5324, KN-LIT-7571, KN-LIT-4817, KN-TECH-056]
added: 2026-07-27
superseded_by: null
---

## Statement
Sixty-four years of work on generic decoding of random binary linear codes has
moved the reported half-distance worst-rate exponent from Prange's ~`0.058` to
Both-May's ~`0.047` -- roughly 19%, with every step after Stern paying in memory
(KN-TECH-057). **Is this near-flatness evidence of a real barrier, or of a
technique ceiling?** Concretely: is there a lower bound explaining why
`2^{cn}` with `c` bounded away from zero is forced, or has the ISD family simply
exhausted one idea (permute-reduce-search) without anyone finding a second?

## Current state (as reported)
- **Every algorithm in the family shares one skeleton.** Prange, Stern,
  Canteaut-Chabaud, ball-collision, MMT, BJMM, May-Ozerov, Both-May differ only
  in the inner search. No published algorithm attacks random-code decoding by a
  structurally different route at a competitive exponent.
- **Improvements are bought with memory.** The time-exponent gains past Stern
  come from meet-in-the-middle and representation techniques whose space term
  grows as the time term shrinks. Under a memory-charged cost model
  (KN-TECH-035, KN-TECH-044) the effective gain is smaller than the time
  exponent suggests, and possibly much smaller.
- **There is partial lower-bound work.** KN-LIT-4817 reports lower bounds
  covering lattice sieving and ISD together. This corpus has not established
  what model those bounds assume or how close they come to the achieved
  exponents.
- **No worst-case-to-average-case reduction exists** for syndrome decoding at
  these parameters (KN-TECH-056), so hardness has no structural backing beyond
  this empirical record.

## Why it matters here
Directly, for two reasons. First, `docs/target-result-profile.md` sets
exponent-moving results on central hard problems as the standard, and the ISD
exponent is one of the few such exponents in cryptography that has barely moved
-- which makes it simultaneously a high-value target and a strong prior against
any claimed improvement. This program should hold code-based exponent claims to
the base rate implied above: on the historical record, a large claimed gain is
much more likely to be a scoping error (wrong regime, uncharged memory, worst-rate
maximum confused with a scheme's actual rate) than a result.

Second, it is a clean external test of the program's own cost discipline. The ISD
literature is a decades-long record of exponent claims with memory terms attached
-- an ideal corpus for checking whether the program's full-cost rules
(KN-TECH-035) would have ranked those results the way the field eventually did.

## What would close it
Either direction is a genuine result, and both are cheaper to attempt than most
things in this corpus because no cryptographic-scale computation is involved:

- **A lower bound.** A model-relative bound showing `c` cannot fall below some
  explicit constant for any algorithm in a suitably general class -- the
  code-based analogue of the generic-group argument the program already uses for
  ECDLP (KN-TECH-005). Establishing what KN-LIT-4817 already proves, and against
  which model, is the correct first step and is a literature task, not a compute
  task.
- **A structurally new algorithm.** Any competitive decoder not of
  permute-reduce-search shape would reopen the question regardless of its exponent.

A useful intermediate, and the cheapest concrete deliverable: **re-rank the
published ISD family under a memory-charged cost model** and report how much of
the 0.058 -> 0.047 movement survives. This program has the cost-model machinery
(KN-TECH-035, KN-TECH-044) and the estimator reference (KN-LIT-6923) to do it,
and the answer is not recorded anywhere in this corpus. Nothing here has been
attempted.
