---
id: KN-TECH-020
type: technique
title: Lattice basis reduction (LLL / BKZ) and SVP/CVP algorithms
tags: [lattice-reduction, lll, bkz, svp, cvp, enumeration, sieving, root-hermite-factor, cryptanalysis]
confidence: established
complexity: LLL poly-time, 2^{O(n)} approx; BKZ tunable by block size beta; SVP oracle ~2^{0.292n} heuristic (sieving) or 2^{O(n log n)} (enumeration)
applicability: finding short/close vectors in a lattice; the engine for HNP/Coppersmith attacks and lattice-crypto security estimates
source_refs: [KN-LIT-046, KN-LIT-047, KN-LIT-048]
added: 2026-07-23
superseded_by: null
---

## Method
Lattice reduction transforms a basis into one of shorter, more orthogonal
vectors:
- **LLL** (KN-LIT-046): polynomial time, first vector within 2^{O(n)} of the
  shortest; the base case.
- **BKZ** (KN-LIT-047): calls an SVP oracle on projected blocks of size beta,
  interpolating LLL (beta=2) to HKZ (beta=n); the standard strength/cost dial.
- **SVP oracle**: enumeration (2^{O(n log n)} time, poly space) or sieving
  (2^{0.292n} heuristic time and space, KN-LIT-048).
Output quality is predicted by the *root Hermite factor* delta (Gama-Nguyen); the
BKZ 2.0 simulator predicts delta for a given beta without running it.

## Program usage
The computational engine behind every lattice method in the corpus: it solves the
CVP/SVP instances that HNP nonce attacks (KN-TECH-019) and Coppersmith small-roots
(KN-LIT-037) reduce to, and it prices lattice-crypto security (KN-TECH-023). The
delta predictor decides whether a given instance (e.g. a nonce-leakage HNP
lattice, or an LWE embedding) is breakable at feasible beta.

## Applicability limits
LLL's worst-case approximation factor is exponential (though practice is far
better); strong reduction needs large beta, whose cost grows super-polynomially
(the SVP-oracle exponent). Concrete cost estimates depend on the assumed SVP-oracle
model (enumeration vs sieving) and on sieving heuristics, so published bit-security
numbers carry model uncertainty. Reduction finds SHORT vectors; it only breaks a
problem that has been embedded so the secret IS short (HNP leakage, LWE, NTRU) --
it gives no leverage on the plain ECDLP (KN-OPEN-011).
