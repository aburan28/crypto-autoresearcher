---
id: KN-OPEN-f2f6dc
type: open_problem
title: >-
  The KKM crater/floor asymmetry -- across a large prime conductor gap, can ECDLP be strictly easier on the volcano floor than on the crater, and can an attacker ever exploit a floor-only weakness against a crater curve faster than sqrt(q)?
tags: [kkm, volcano, crater, conductor, conductor-gap, isogeny-class, random-self-reduction, jmv, problem-b, descending-isogeny, cm-method, pairing-friendly, ecdlp, open]
confidence: reported
status: open
source_refs: [KN-LIT-0cb87e, KN-LIT-ca35e0, KN-LIT-7630, KN-LIT-237, KN-OPEN-cc1988, KN-OPEN-cbbd97, RQ-VOLC-f6253b, GOAL-ECTD-001]
added: 2026-10-03
superseded_by: null
---

## Statement

Ordinary isogeny class over F_q, t^2 - 4q = f^2 D0, with a prime N | f,
N > q^{1/4}. Crater set S1: End-ring conductor coprime to N (includes every
CM-method / pairing-friendly curve). Floor set S2: conductor divisible by N;
#S2 ~ N #S1.

Known asymmetry (KN-LIT-ca35e0, as reported):

- floor -> crater isogeny: O~(q^{1/4});
- crater -> *some* floor curve (Problem B): best known ~min(N^2, q^{1/2});
- within S2, ECDLP is random self-reducible in O~(q^{2/5}) (Theorem 5).

Consequences: any sub-sqrt ECDLP attack on crater curves (with small h(O_K))
propagates to the whole class; a sub-sqrt attack on a positive fraction of
floor curves covers all of S2 but **does not** reach S1 unless Problem B
gets faster than q^{1/2}.

**Question (KKM, 2011).** (a) Is there a non-isogeny-invariant ECDLP weakness
that lives on S2 but not S1 -- making crater curves strictly safer? (b)
Independently of (a): is there an o(q^{1/2}) algorithm for Problem B
(construct and evaluate a descending N-isogeny from a given crater curve)?
A yes to (b) erases the asymmetry and makes ECDLP hardness uniform across
every isogeny class up to O~(q^{2/5}) transfer cost.

## What is known (as reported)

- KKM (KN-LIT-0cb87e Sec. 11.3) argue (a) heuristically, assuming weakness is
  independent of endomorphism class; only concrete instance is binary-field
  Weil descent (Menezes-Teske, eps ~ 2^-58), not prime fields.
- Galbraith (KN-LIT-ca35e0 Sec. 10): "no direct evidence"; results are
  "consistent with" KKM. (b) is his stated main open problem (Sec. 11).
- No ECDLP difference between volcano levels is known on prime-order
  subgroups, where every endomorphism acts as a scalar (H-ENDO-001,
  RQ-VOLC-f6253b decision target).
- Relation to existing problems: KN-OPEN-cc1988 asks whether *any*
  non-invariant weakness exists; this entry fixes its direction (floor-only
  is the only direction that survives the cheap ascent). KN-OPEN-cbbd97 is the
  trapdoor use of the same barrier.

## Why it matters here

The answer decides whether "special" CM curves (secp256k1 j=0, BN/BLS
pairing curves, K-curves) are, even in principle, isolated from attacks that
hit generic curves of the same order -- KKM's claim that special can beat
random -- or whether that isolation is an artefact of a missing Problem-B
algorithm. Problem B is a concrete algorithmic target with a sharp baseline
(q^{1/2}); toy-scale stratified measurement by level is already scoped in
RQ-VOLC-f6253b.

## Minimal discriminating tests

1. Problem B at toy size (q ~ 2^40-2^60, N ~ q^{1/4..1/2}): implement both
   baselines (N-isogeny via sqrt-Velu; point-count-biased guessing) and any
   candidate, measure exponent; certificate = explicit isogeny verified on
   points.
2. For (a): per-level stratified ECDLP cost under the program's matched rho
   controls, with null objects (KN-OPEN-cc1988 / RQ-VOLC-f6253b protocols).
   A level effect that does not survive nulls is closure evidence only at the
   tested scale.
