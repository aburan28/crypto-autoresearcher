---
id: KN-TECH-4409e1
type: technique
title: >-
  Extension-field decomposition (Gaudry-Diem index calculus on E(F_{q^n}), small n) as a visible but normalizable weakness -- a standardizer can publish a curve over F_{p^2}, F_{p^3} whose ECDLP is asymptotically below rho without hiding anything
tags: [trapdoor, extension-field, decomposition, gaudry, diem, joux-vitse, summation-polynomials, weil-restriction, fourq, unchecked-weakness, ecdlp]
confidence: established
complexity: >-
  Gaudry's decomposition attack solves ECDLP on E(F_{q^n}) for fixed small n in O~(q^{2 - 2/n}), with a constant that grows super-exponentially in n (the Groebner solve of the Weil-restricted summation polynomial S_{n+1}); against rho at q^{n/2}. Gain for n = 3: q^{4/3} versus q^{3/2}; for n = 2 no gain (q vs q). Diem proved subexponential bounds when n grows with q; Joux-Vitse made n = 5, 6 practical at cryptographic sizes for a range of q
applicability: >-
  curves over proper extension fields F_{q^n} with n small; the field structure is public, so this is the paradigm of a weakness that cannot be hidden but can still be normalized by a standard that users do not audit (FourQ over F_{(2^127 - 1)^2} is the deployed n = 2 case, where no asymptotic gain exists)
source_refs: [KN-LIT-002, KN-LIT-022, KN-LIT-673219, KN-LIT-41fe5c, KN-LIT-fbb9fd, KN-TECH-8ef4c3, KN-TECH-6ead00]
added: 2026-09-30
superseded_by: null
---

## Mechanism

Weil restriction of `E/F_{q^n}` to `F_q` gives an `n`-dimensional abelian
variety `A/F_q`. Gaudry (KN-LIT-002) chose the factor base
`F = {P in E(F_{q^n}) : x(P) in F_q}` (about `q` points) and used Semaev's
summation polynomial `S_{n+1}` to decompose a random point into `n` factor-
base points by solving a polynomial system over `F_q` (via Weil restriction
of the summation polynomial). About `q` relations are needed; each costs a
Groebner-basis solve of size depending on `n` only, so the total is
`O~(q^{2 - 2/n})` after linear algebra, beating `q^{n/2}` for `n >= 3`.
Joux and Vitse (KN-LIT-022) traded relation yield for cheaper decompositions
(decomposing into `n - 1` points) and gave practical attacks for `n = 5, 6`.
KN-LIT-41fe5c gives the static-DH variant, and KN-LIT-fbb9fd extends to
hyperelliptic Jacobians.

## Relation to Teske's trapdoor

Teske's construction (KN-TECH-8ef4c3) needs a *rare* weakness (GHS applies
only to some curves in the class) so that hiding is meaningful. Decomposition
applies to **every** curve over `F_{q^n}` with small `n`, so there is nothing
to hide: the weakness is decided by the field, and the field is public.

## As a standardizer's lever

A standard can still normalize an extension-field curve and rely on users not
comparing the decomposition cost with the advertised security level. For
`n = 2` (FourQ) the decomposition gives no asymptotic gain and the choice is
defensible; for `n = 3` and above the gap is real and grows with `n`. This is
why the taxonomy (KN-TECH-6ead00) classifies it with the *unchecked*
weaknesses next to twist security and Cheon divisors.

## Detectability

Immediate: `q^n` with `n > 1` is visible in the field definition. The
relevant audit is a cost estimate, not a search.

## Applicability limits

- Prime fields (`n = 1`) are untouched: the factor base collapses to all of
  `E(F_p)` and no decomposition exists. This is the second of the four
  obstructions to a prime-field Teske analogue (KN-OPEN-cc1988).
- For fixed `n` the gain is a constant in the exponent; the subexponential
  regime (Diem) needs `n` to grow with `log q` and is not reached by any
  deployed curve.

## Relevance

The program's own index-calculus lineage (Semaev, first-fall degree, WDSat)
is the prime-field descendant of this technique; its `n = 1` failure is the
recurring obstruction in the F1-F7 tracked-object enumeration
(KN-TECH-ee6696).
