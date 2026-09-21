---
id: KN-OPEN-001
type: open_problem
title: Does index calculus beat Pollard rho for prime-field ECDLP?
tags: [prime-field, index-calculus, pollard-rho, baseline, ecdlp, open]
confidence: reported
status: open
source_refs: [KN-LIT-006, KN-LIT-002, KN-LIT-003, KN-LIT-008]
added: 2026-07-19
superseded_by: null
---

## Statement
For elliptic curves over prime fields GF(p), is there an algorithm with
expected cost asymptotically below the generic ~sqrt(p) of Pollard rho?

## Current state (as reported)
No. Summation-polynomial / point-decomposition index calculus gives
subexponential results over small-degree *extension* fields (KN-LIT-002/003)
but no known construction yields an advantage over prime fields; the survey
KN-LIT-006 reports rho as still the best known prime-field attack. The
obstruction is the lack of a good structured factor base and the cost of the
decomposition/Gröbner step.

## Why it matters here
This is the program's central scoping fact. Prime-field proposals that
implicitly assume an index-calculus advantage are proposing *into an open
problem*, not applying a known result -- the Idea Generator must classify them
`speculative`, not `adaptation`. Toy-scale prime-field measurements can only
motivate scaling studies, never settle this.
