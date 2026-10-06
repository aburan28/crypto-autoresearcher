---
id: KN-OPEN-b9907c
type: open_problem
title: >-
  Partially anomalous ring curves over Z/NZ -- when E mod p is anomalous and E mod q is ordinary, the factorization holder solves the p-part by the Smart / Satoh-Araki / Semaev lift; can the remaining q-part be made easy for the holder without becoming easy for the public, so that the halves compose into a full trapdoor?
tags: [trapdoor, ring-curve, anomalous, smart-attack, p-adic-lift, composite-modulus, partial-trapdoor, factoring, ecdlp, open]
confidence: reported
status: open
source_refs: [KN-TECH-906e14, KN-LIT-088, KN-TECH-6ead00, KN-OPEN-9b71bb]
added: 2026-09-30
superseded_by: null
---

## Statement

Take `N = pq` and a curve `E/(Z/NZ)` with `#E(F_p) = p` (anomalous mod `p`)
and `#E(F_q)` prime and ordinary. The DLP on `E(Z/NZ)` splits by CRT into a
DLP on `E(F_p)` and one on `E(F_q)`. The holder of `(p, q)` solves the first
in polynomial time by the anomalous-curve attack (KN-LIT-088: lift to
`Z/p^2 Z`, multiply by `p`, read the answer in the additive kernel of
reduction). The second remains a generic ECDLP of size `q`.

**Question.** Is there a choice of the `q`-component that is (a) easy for
the factorization holder and (b) not easy for the public, such that the two
halves compose into a full trapdoor on `E(Z/NZ)`? Two candidate answers and
why each is currently unsatisfying:

1. **Make `E mod q` anomalous too.** Then the holder solves both halves, but
   so does anyone who factors `N`, and moreover `#E(Z/NZ) = pq = N` is
   public, so the curve advertises its anomaly. It reduces exactly to the
   factoring-based ring-curve trapdoor of KN-TECH-906e14 with no added
   hiding.
2. **Choose `E mod q` from some other holder-easy class.** Every known
   holder-easy class over a prime field is a public invariant of `E mod q`
   (KN-TECH-6ead00 hiding criterion), and once `N` is factored it is exposed,
   so again the security is factoring and the anomaly adds nothing.

## What is known (as reported)

- The `p`-part solution is exact and cheap; this is the same mechanism as
  the elliptic-curve Okamoto-Uchiyama and Paillier variants recorded in
  KN-TECH-906e14, where it is used constructively.
- The Smart-style lift needs `p`; without the factorization the public
  cannot even reduce mod `p`, so the `p`-half is genuinely hidden. The
  problem is entirely in the `q`-half.
- The public's best attack is to factor `N`, after which every half is as
  easy or as hard as its own prime-field structure says. So the construction
  can never be *stronger* than factoring, and the only question is whether
  it can be arranged to be exactly as strong as factoring while looking, to
  someone who does not factor, like an ordinary ECDLP over a ring.

## Minimal discriminating test

At toy size, construct `N = pq` with the `p`-half anomalous and measure
whether any public statistic of `E(Z/NZ)` (order of random points modulo
small primes, distribution of `x`-coordinates, behaviour under the
`Z/NZ` group law's failure set) distinguishes it from a curve with two
ordinary halves faster than factoring `N`. A distinguisher would show the
partial anomaly *leaks*; none would leave the construction as a factoring-
hard trapdoor with no ECDLP content.

## Why it is filed

Like KN-OPEN-9b71bb it is a recurring proposal with an expected negative
answer, recorded so the reasoning is citable rather than repeated. Its
resolution has no bearing on prime-field standards (reduce mod one prime and
the trapdoor is gone) and it is not a candidate for GOAL-ECTD-001.
