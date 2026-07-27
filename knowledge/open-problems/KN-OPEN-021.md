---
id: KN-OPEN-021
type: open_problem
title: Can the high-rate Goppa distinguisher be turned into an attack at Classic McEliece parameters?
tags: [code-based, goppa, distinguisher, structural-attack, mceliece, cfs, filtration, indistinguishability, open]
confidence: reported
status: open
source_refs: [KN-TECH-059, KN-TECH-058, KN-LIT-2395, KN-LIT-2383, KN-LIT-5792, KN-LIT-2127, KN-LIT-7573, KN-LIT-4258, KN-LIT-7572]
added: 2026-07-27
superseded_by: null
---

## Statement
Classic McEliece's key security rests on an unproven assumption: that a scrambled
binary Goppa parity-check matrix is indistinguishable from a random one
(KN-TECH-058). The assumption is known to be **false at high rate** -- there is a
published distinguisher for high-rate Goppa codes (KN-LIT-2395). Deployed KEM
parameters are not in that regime.

**Two questions, and they are different.** (1) Does the distinguisher extend to
the rates Classic McEliece actually uses? (2) Even where it applies, can it be
bootstrapped into key recovery, rather than remaining a distinguisher only?

## Current state (as reported)
- **The distinguisher exists and is rate-limited.** KN-LIT-2395 reports it for
  high-rate Goppa and alternant codes. Deployed KEM parameter sets sit outside
  the reported range; the entry does not establish how far outside.
- **Distinguisher-to-attack is a proven pipeline on other families.**
  KN-LIT-5792 breaks Wild McEliece over quadratic extensions by exactly this
  route -- distinguish, then peel a filtration to recover the structure
  (KN-TECH-059). The route is not hypothetical; it just has not reached plain
  binary Goppa at deployed rates.
- **Related algebraic lines are active.** KN-LIT-2383 (special-form Goppa
  polynomials) and KN-LIT-2127 (a quadratic-forms formulation) are recent attempts
  on the same target from different directions.
- **CFS signatures are the acute case.** CFS forces very high-rate codes to make
  retry-until-decodable affordable (KN-TECH-062, KN-LIT-4258), which places it
  much closer to the regime where the distinguisher is known to work. The
  question is materially more urgent for signatures than for KEMs.

## Why it matters here
It is the single assumption on which the most conservative deployed
post-quantum primitive rests, and it is *empirical* -- it has no reduction behind
it. Alekhnovich's construction (KN-LIT-7572) shows what the alternative costs:
security from random-code decoding alone, with no hidden structure and no
distinguisher question, at efficiency nobody deploys. The entire practical
code-based branch is a bet that hiding a decodable structure is safe, and this is
the precise statement of what would settle that bet.

For the program's methodology, it is also the cleanest available example of a
distinction the corpus should keep sharp: **a distinguisher is not a break**, and
the gap between them is where most of the real cryptanalytic work lives. That
distinction transfers directly to how this program should read its own
red-team findings -- an anomaly that separates a construction from random is a
lead, and reporting it as a break would be exactly the overclaim AGENTS.md rule 4
prohibits.

## What would close it
- **Extension analysis.** Determine the rate threshold at which the KN-LIT-2395
  distinguisher stops working, and compare it against the mceliece* parameter
  sets (KN-LIT-7573). This is a bounded literature-and-computation task and the
  obvious first step; the answer is not recorded in this corpus.
- **A filtration attack at deployed rate.** Would break Classic McEliece and would
  be a major result.
- **A proof of indistinguishability**, even under a stated heuristic, would be
  the first structural backing the assumption has ever had.

Nothing here has been attempted in this program, and the first item is the only
one that is cheap.
