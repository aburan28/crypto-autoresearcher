---
id: KN-OPEN-cbbd97
type: open_problem
title: >-
  Endomorphism-ring-gated isogeny walks -- can secret knowledge of End(E) across a large-conductor barrier (where computing End requires factoring the conductor) gate a DLP advantage that the public cannot reach by isogeny-path search?
tags: [trapdoor, endomorphism-ring, conductor, volcano, vertical-isogeny, class-group, kohel, galbraith, gating, prime-field, ecdlp, open]
confidence: reported
status: open
source_refs: [KN-TECH-6ead00, KN-OPEN-cc1988, KN-LIT-7630, KN-LIT-7631, KN-FIND-f293c6, GOAL-ECTD-001, H-ECTD-001]
added: 2026-09-30
superseded_by: null
---

## Statement

For an ordinary curve `E/F_p` with Frobenius `pi`, write
`4p - t^2 = f^2 * |D_K|` with `D_K` the fundamental discriminant. The
endomorphism ring `End(E)` is an order `Z[pi] subseteq End(E) subseteq O_K`
of conductor dividing `f`. Kohel's algorithm and its successors determine
`End(E)` by locating `E` on the `l`-isogeny volcanoes for each prime
`l | f`, at cost polynomial in `l`; when `f` has a large prime factor `l`,
determining the level at `l` costs about `l` operations, and factoring `f`
itself may be hard. A generator who *constructs* `E` (via the CM method or by
a chosen vertical walk) knows `End(E)` and the class-group action for free.

**Question.** Suppose `E_pub` and `E_s` are in the same isogeny class,
separated by a vertical `l`-isogeny chain with `l` a large prime dividing
`f`. The holder knows the chain. Is there any ECDLP-relevant advantage at
`E_s` (or any endpoint reachable from the holder's End-ring knowledge) that
a public attacker cannot reproduce because (a) the vertical step at `l` is
infeasible without knowing the level, and (b) Galbraith's isogeny-path
algorithm (KN-LIT-7630) is stated to be incomplete exactly when the
endomorphism-ring index contains a large prime?

## What is known (as reported)

- The **gate** is real: the incompleteness boundary in KN-LIT-7630 and the
  cost of a large-`l` vertical step are established, and the JMV
  random-self-reduction (KN-LIT-7631) is proved only *within* a level, so a
  large-conductor barrier is the one place where DLP difficulty is not
  proved uniform across a class. KN-FIND-f293c6 shows the concrete JMV
  walk-length bound is vacuous at 256 bits for small polynomial-degree
  parameters, so even within a level the concrete uniformity is weaker than
  the asymptotic statement.
- The **prize** is missing: no ECDLP advantage is known at any endpoint of
  a prime-field class (KN-OPEN-cc1988). Without one, the gate guards an empty
  room; the maximal-order endpoint gives only GLV-type constant factors, which
  GOAL-ECTD-001 explicitly deprioritizes.
- The gate also protects the **holder's own search**: if the weak endpoint
  must be found by trial across the class, the holder needs an efficient
  navigation, which is exactly what End-ring knowledge supplies. This makes
  the mechanism the natural *delivery* component of any positive answer to
  KN-OPEN-cc1988, in the way seed manipulation (KN-TECH-031027) is the
  delivery component for a weak class of random curves.

## Minimal discriminating test

At toy size (`p` of 40 to 80 bits) construct classes with `f` having one
moderately large prime factor; place `E_pub` and `E_s` on different levels
at that prime; measure, per level, the candidate endpoint statistics of
KN-OPEN-cc1988 (Semaev relation density, `d_reg`, first-fall, maps to low-
genus curves). A heavy-tailed level-dependence would be the first positive
signal; a flat profile across levels closes this mechanism as a *source* of
weakness and leaves it only as a *gate*. This is the shape of
`H-ECTD-19017a` / `EXP-ECTD-9e4248` in GOAL-ECTD-001.

## Why it matters here

It is the only known mechanism by which a prime-field isogeny trapdoor could
satisfy condition (4) of KN-OPEN-cc1988 (public path search at least
`sqrt(n)`-hard) *by theorem* rather than by hoping the class is large.
Whether the room behind the gate is empty is the open question.
