---
id: KN-OPEN-008
type: open_problem
title: Does a noncommutative path-algebra (quiver) word search find target-reaching ECDLP relations that the commutative subset-sum quotient misses, at lower cost or sub-birthday exponent?
tags: [noncommutative, path-algebra, quiver, word-relations, commutator-collapse, birthday, ecdlp, open]
confidence: reported
status: open
source_refs: [KN-LIT-035, KN-LIT-036, KN-TECH-014]
added: 2026-07-22
superseded_by: null
---

## Statement
Model translations, negation, and small correspondences on E(F_p) as arrows of a
quiver and let its noncommutative path algebra act on formal point-sums. Does a
noncommutative Grobner / syzygy (Bergman overlap) word search find word-level
relations reaching the target Q from factor-base words that the *commutative*
subset-sum quotient cannot produce -- and if so, at lower cost per relation or a
sub-birthday charged exponent than the generic square-root bound?

## Current state (as reported)
Path-algebra Grobner theory (KN-LIT-035, KN-LIT-036, KN-TECH-014) is established
but only SEMI-DECIDABLE (bases may be infinite; completion need not terminate),
so there is no a priori cost bound. No cryptographic/ECDLP application is known.
The program's noncommutative candidate (RQ-NCP-001, EXP-NCP-001, round-1 C3)
reported a scoped negative. The central obstruction is *commutator collapse*: if
every target-reaching word relation abelianizes to a commutative relation, the
path algebra is a relabeling inside the generic group model (KN-TECH-005) and
supplies nothing new.

## Why it matters here
It is a sharp, cheap-to-falsify probe: exhibit ONE genuinely non-commutative
(non-abelianizable) target-reaching relation and the collapse argument fails;
prove commutator collapse and the whole path-algebra route closes by theorem.
Either way it delimits how much word-order structure the ECDLP relation problem
actually carries beyond its commutative image -- a boundary of KN-OPEN-001 for
noncommutative representations. Any positive claim must survive the fully-charged
cost model, given the unbounded (semi-decidable) word search.
