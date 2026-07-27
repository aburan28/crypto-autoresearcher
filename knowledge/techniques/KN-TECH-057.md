---
id: KN-TECH-057
type: technique
title: Information set decoding (ISD) and the generic decoding exponent
tags: [code-based, information-set-decoding, isd, syndrome-decoding, baseline, exponent, meet-in-the-middle, representation-technique, memory, quantum, cryptanalysis]
confidence: reported
complexity: 2^{cn(1+o(1))}; reported half-distance worst-rate exponents c ~ 0.058 (Prange) -> 0.05563 (Stern) -> 0.054 (MMT) -> 0.05 (BJMM) -> ~0.047 (Both-May). Memory grows with c's decrease.
applicability: the generic attack against every code-based scheme; the baseline any claimed code-based advantage must beat
source_refs: [KN-LIT-7566, KN-LIT-7567, KN-LIT-7568, KN-LIT-3368, KN-LIT-3367, KN-LIT-5324, KN-LIT-7571, KN-LIT-6707, KN-LIT-2607, KN-LIT-6923, KN-LIT-4144, KN-LIT-4817, KN-LIT-4875, KN-LIT-1302]
added: 2026-07-27
superseded_by: null
---

## The family
Every ISD algorithm is the same loop: permute the coordinates, row-reduce, hope
the error is distributed favourably across the information set, and check. They
differ only in what "favourably" means and how the residual search inside each
iteration is done.

| Algorithm | Inner search | Ref |
| --- | --- | --- |
| Prange (1962) | none -- information set must be error-free | KN-LIT-7566 |
| Lee-Brickell / Leon | allow `p` errors, exhaustive | -- |
| Stern (1989) | birthday collision over two halves | KN-LIT-7567 |
| Canteaut-Chabaud (1998) | iterative reuse of the elimination | KN-LIT-7568 |
| Ball-collision (2011) | collision over overlapping balls | KN-LIT-6707 |
| MMT (2011) | representation technique | KN-LIT-3368 |
| BJMM (2012) | representations with `1+1=0` cancellation | KN-LIT-3367 |
| May-Ozerov (2015) | nearest-neighbour search | KN-LIT-5324 |
| Both-May (2018) | NN + representations, high error rate | KN-LIT-7571 |

## The exponent, and its honest reading
Reported half-distance worst-rate exponents `c` (runtime `2^{cn}`):

```
Prange   ~0.058   Stern  0.05563   MMT  0.054   BJMM  0.05   Both-May  ~0.047
```

Prange's *full-distance* worst-case figure is reported as ~`2^{0.1207n}`; the two
scales are different and are routinely confused in secondary sources.

**Read this as a near-flat curve.** Sixty-four years of sustained work moved the
half-distance exponent by roughly 19%. Nothing in this line resembles the
exponent movement that `docs/target-result-profile.md` holds up as the standard
(Wesolowski's `p^{1/3+o(1)}`). Two consequences for this program:

1. Code-based parameters are stable, which is why Classic McEliece's assumption
   has survived unchanged since 1978 (KN-LIT-7564, KN-LIT-7573).
2. Any proposal claiming a large ISD exponent improvement is, on the base rate,
   far more likely to contain a scoping or accounting error than a result. See
   KN-OPEN-019 for what a real improvement would have to look like.

## Memory is load-bearing
Every improvement past Prange buys its exponent with memory, and the better the
time exponent the worse the space term. An ISD comparison quoted in time alone
is not a comparison. This is the identical failure mode the program already
polices for lattice sieving (KN-TECH-044) and under the general full-cost rule
(KN-TECH-035). KN-LIT-4817 reports lower bounds covering both sieving and ISD,
which is the natural place to look for what the memory term cannot go below.

## Concrete versus asymptotic
The asymptotic ranking above does **not** determine which algorithm is fastest at
a given parameter set: the `o(1)` and the polynomial factors dominate at
cryptographic sizes, and crossovers are real. Concrete work uses estimators
(KN-TECH-061, KN-LIT-6923) and record computations (KN-LIT-4875 solving
McEliece-1284 and quasi-cyclic-2918; KN-LIT-1302 solving McEliece-1409) as the
calibration points -- exactly the role public ECDLP records play in KN-TECH-036
and lattice challenges play in KN-TECH-049.

## Quantum
Grover-accelerated ISD gives roughly a square-root speedup on the search loop,
not an exponent collapse (KN-LIT-4144). Code-based parameters therefore respond
to quantum attack the way symmetric parameters do -- doubling-ish -- not the way
factoring and DLP do. This is the substantive reason the family is a PQC
candidate at all.

## Applicability limits
No ISD implementation has been run in this program and no exponent here was
derived or reproduced locally. The `~0.047` and `~0.058` figures are relayed from
secondary sources and their third decimal is unconfirmed (see KN-LIT-7571). The
0.054 and 0.05 figures come from the MMT and BJMM paper titles respectively. Any
program claim that turns on a specific decimal must fetch the primary table
first.
