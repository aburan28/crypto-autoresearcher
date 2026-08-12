---
id: KN-TECH-014
type: technique
title: Noncommutative Grobner bases and path algebras of quivers
tags: [noncommutative, groebner, path-algebra, quiver, diamond-lemma, word-problem, semi-decidable, ecdlp]
confidence: reported
complexity: semi-decidable in general; the noncommutative Grobner basis may be infinite and the completion procedure need not terminate
applicability: normal forms and relation search in free associative / path algebras (arrow-words on a quiver)
source_refs: [KN-LIT-035, KN-LIT-036]
added: 2026-07-22
superseded_by: null
---

## Method
A *quiver* Q is a directed multigraph; its *path algebra* kQ is spanned by the
directed paths with multiplication by concatenation (zero when paths do not
compose). Relations are two-sided ideals of kQ. Noncommutative Grobner bases
(Mora, KN-LIT-036; path-algebra specialization by Green) with an admissible order
and the diamond-lemma confluence criterion (Bergman, KN-LIT-035) compute normal
forms and reduce overlaps (S-polynomial analogues) to find word-level relations.

## Role
Models translations, negation, and small correspondences as arrows, letting the
path algebra act on formal point-sums; NC overlap/syzygy reduction searches for
word-level relations between a target word and factor-base words that the
commutative subset-sum quotient cannot see (order is retained).

## Program usage
The mechanism of RQ-NCP-001 / EXP-NCP-001, and of round-1 candidate C3. The
question is whether word-order structure yields Q-reaching relations at lower
cost per relation or a sub-birthday charged exponent (KN-OPEN-008).

## Applicability limits
CRITICAL: NC Grobner computation is only SEMI-DECIDABLE -- the basis may be
infinite and the completion procedure may not terminate -- so there is no generic
cost bound, and unbounded word search has no birthday-style guarantee. The
strongest kill (commutator collapse): if word-level relations merely shadow the
commutative ones after abelianization, the path algebra is a relabeling and the
generic bound (KN-TECH-005) applies. The program's NCP experiment reported a
scoped negative. Any claimed advantage must exhibit a genuinely non-commutative,
target-reaching relation not present in the commutative quotient.
