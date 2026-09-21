---
id: KN-LIT-2c8264
type: literature
title: "A Subexponential-Time Quantum Algorithm for the Dihedral Hidden Subgroup Problem (Kuperberg 2005)"
authors:
  - "Greg Kuperberg"
year: 2005
venue: "SIAM Journal on Computing, 35(1):170-188"
identifiers:
  eprint: null
  doi: 10.1137/S0097539703436345
  arxiv: "quant-ph/0302112"
  url: https://epubs.siam.org/doi/10.1137/S0097539703436345
tags: [quantum, dihedral, hidden-subgroup, kuperberg-sieve, dcp, dsp, csidh, hidden-shift, isogeny, lattice, pqc, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-08-06
superseded_by: null
---

## Contribution
The "Kuperberg sieve": a quantum algorithm for the dihedral hidden subgroup
problem in time and query count `2^{O(sqrt(log N))}` — subexponential, and
until 2026 the best known algorithm for the problem. It combines coset-state
samples pairwise to produce states with progressively more structured phase
differences, in the spirit of a sieve.

## Key claims (as reported)
- `2^{O(sqrt(log N))}` time for the dihedral HSP, versus the exponential-time
  classical baseline.
- **The algorithm requires error-free samples.** This is the property that
  matters for lattice cryptanalysis: composed with Regev's noisy reduction
  (KN-LIT-21383c), which forces a `1/a(n)` faulty-sample rate, it yields only
  a `2^{O(sqrt n)}` SVP approximation factor — no improvement on classical BKZ
  (KN-LIT-e204ab). Noise tolerance, not raw speed, is the binding constraint.

## Relevance to this program
Two distinct roles.

- **Post-quantum lattice branch:** the incumbent DCP algorithm that Simon 2026
  (KN-LIT-e204ab) claims to supersede, and the reason the pre-2026 consensus was
  that DCP posed no threat to lattice cryptography. See KN-TECH-d1bc4f.
- **Isogeny branch:** the same sieve is the quantum attack on commutative
  class-group actions via abelian hidden shift — the CSIDH security ceiling
  (KN-LIT-071, KN-TECH-027, KN-TECH-051) and the subject of the concrete-cost
  dispute in KN-OPEN-014. Already cited across those entries; this entry gives
  the primary source its own record.

## Not verified here
Paper not read. The complexity bound and the error-free-input requirement are
relayed from KN-LIT-071, KN-TECH-027 and Simon 2026's account (KN-LIT-e204ab);
citation metadata confirmed via search on 2026-08-06 against SIAM DOI
10.1137/S0097539703436345. Confidence `reported`.
