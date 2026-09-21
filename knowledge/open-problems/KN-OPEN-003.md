---
id: KN-OPEN-003
type: open_problem
title: Do curve representations/symmetries reduce decomposition cost over prime fields?
tags: [representation, symmetry, edwards, prime-field, index-calculus, groebner, open]
confidence: reported
status: open
source_refs: [KN-LIT-004, KN-OPEN-001, KN-OPEN-002]
added: 2026-07-19
superseded_by: null
---

## Statement
Over prime fields, does the choice of curve model (Weierstrass, Edwards,
twisted forms) or exploitable symmetry materially lower the decomposition /
Gröbner solving cost, as it does in the settings of KN-LIT-004?

## Current state (as reported)
Symmetry-based speedups are established for specific models and mostly analyzed
outside the plain prime-field short-Weierstrass baseline (KN-LIT-004). Whether
a comparable prime-field advantage exists, and how to separate a genuine
representation effect from random coefficient variance, is open.

## Why it matters here
Anchors the ROADMAP "representation search" program with a falsifiable,
controlled comparison: matched instances across models, measuring solving
degree/time, with isogeny/coefficient-variance controls. Guards against
mistaking coefficient noise for a representation effect.
