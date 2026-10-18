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

## Reconciliation note, 2026-10-18 (appended; the entry above is unchanged)

Register status stays `open`. The path-algebra result is a scoped negative (word degree <= 6, p in {101, 431}); this entry itself says commutator collapse is not proved.

Premise check: the request that prompted this note cited DEC-20260722-003..006 as the proving decisions. They are not: DEC-20260722-003 targets GOAL-MLKEM-001/IDEA-20260722-001, -004 and -005 target GOAL-ECDLP-001 BATCH-002 task handling, and no DEC-20260722-006 exists. The records that do bear on this problem are below.

- EV-NCP-001 (H-NCP-001, `contradicts`, `replicated`): toy primes {101, 431}, orders 13..439, word degree <= 6, B in {4, 8}.
- DEC-20260724-011 and DEC-20260804-4f37d5 mention this route; H-NCP-4cc527 is `proposed`.
- A proof of commutator collapse would close this by theorem; none is committed. DEC-20260804-139a86 says "H-NCP-001 rejected_scoped (commutator collapse)", which is a scoped statement, not that theorem.

Decision request: `coordination/remediation/DECISION-REQUEST-20261018-ic-integrity.md`, item R-3.
