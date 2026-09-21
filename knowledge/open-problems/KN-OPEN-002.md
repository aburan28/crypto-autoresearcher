---
id: KN-OPEN-002
type: open_problem
title: Growth of Groebner solving degree for prime-field summation-polynomial systems
tags: [prime-field, groebner, first-fall-degree, degree-of-regularity, summation-polynomial, open]
confidence: reported
status: open
source_refs: [KN-LIT-005, KN-LIT-010, KN-TECH-004]
added: 2026-07-19
superseded_by: null
---

## Statement
How does the Gröbner solving degree (and first-fall degree) of the point-
decomposition polynomial systems grow with field bit size and decomposition
length m, over *prime* fields specifically?

## Current state (as reported)
The low-degree-of-regularity heuristic and the d_ff proxy are studied mostly
over binary fields (KN-LIT-005, KN-LIT-010). Whether first-fall degree tracks
the true degree of regularity, and how both scale, is not settled over prime
fields.

## Why it matters here
This is a directly *measurable* toy-scale question and a natural first
experiment (EXP-SEMAEV-*): measure solving degree vs. bit size for S_3/S_4
decomposition over GF(p). A well-scoped result here is a legitimate finding
(bounded, artifact-backed) that motivates -- but does not settle -- KN-OPEN-001.
