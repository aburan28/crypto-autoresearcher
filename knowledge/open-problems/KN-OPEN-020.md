---
id: KN-OPEN-020
type: open_problem
title: Universal algebraic-factor-base no-go for prime-field index calculus
tags: [prime-field, ecdlp, index-calculus, factor-base, algebraic-description, lower-bound, open]
confidence: unverified
status: open
source_refs: [KN-OPEN-001, KN-OPEN-019, KN-TECH-003, KN-TECH-005, KN-TECH-080]
added: 2026-08-02
superseded_by: null
---

## Statement

Can one prove that **every** algebraically described factor base over a
generic prime-field elliptic-curve subgroup fails to yield a subexponential
index-calculus algorithm, with all description, membership, relation, descent,
time, and memory costs charged?

## What is now proved only conditionally by interface

`ideas/artifacts/IDEA-20260801-021/bounded_degree_factor_base_theorem.md`
gives a derivation-level obstruction for one nonzero bounded-degree plane
polynomial predicate, and its algebraic-degree generalization to any proper
locus with explicit finite intersection degree `Delta`. For explicit
bounded-arity sumset descent and min-entropy-random targets, Bezout bounds the
factor base by `3d` (or `Delta`); tuple-image counting bounds the reachable
target set by `B^m`; and the optional fresh-rerandomized descent interface has
the expected charged-trial lower bound `Omega(N/B^m)`.

## Why the universal statement remains open

“Algebraically defined” can include high-degree interpolation descriptions,
multiple constructible predicates, target-dependent descriptions, and implicit
membership or source-recovery algorithms. A generic-group lower bound does not
cover those concrete curve-structure interfaces, and the ECDLP attack-family
taxonomy is not closed (`KN-OPEN-019`). A relation bank or a verifier receipt
also does not imply random-target descent.

## Required next result

A universal theorem would need either a formal complexity class for algebraic
descriptions plus a lower bound for its implicit membership/source solver, or a
complete classification of relation mechanisms with explicit source-to-target
cost accounting. Until then, the bounded-degree theorem must remain a scoped
negative and the universal question must remain open.
