---
id: KN-LIT-099
type: literature
title: Quantum Resource Estimates for Computing Elliptic Curve Discrete Logarithms
authors: [Roetteler Martin, Naehrig Michael, Svore Krysta M., Lauter Kristin]
year: 2017
venue: Advances in Cryptology - ASIACRYPT 2017 (Part II), Springer LNCS, pp. 241-270
identifiers:
  eprint: iacr:2017/598
  arxiv: 1706.06752
  doi: 10.1007/978-3-319-70697-9_9
  url: https://eprint.iacr.org/2017/598
tags: [quantum, shor, resource-estimate, toffoli, qubits, reversible-arithmetic, nist-curves, prime-field, post-quantum, cost-model, ecdlp]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Turns Shor's asymptotic result (KN-LIT-098) into concrete circuit counts for
elliptic curves over prime fields. The authors build reversible circuits for
modular addition, multiplication and inversion, assemble them into controlled
elliptic-curve point addition, classically simulate the resulting Toffoli
networks in the LIQUi|> framework, and report qubit counts, Toffoli counts and
Toffoli depth for the NIST curves P-192 through P-521.

## Key claims (as reported)
- An n-bit prime-field ECDLP needs at most 9n + 2*ceil(log2 n) + 10 logical
  qubits and a circuit of at most 448 n^3 log2(n) + 4090 n^3 Toffoli gates
  (interpolated from simulation data; the point addition alone is about
  224 n^2 log2(n) + 2045 n^2 Toffoli gates, run 2n times).
- Simulated data points (logical qubits / Toffoli gates / Toffoli depth):
  110-bit 1014 / 9.44e9 / 8.66e9; 160-bit 1466 / 2.97e10 / 2.73e10;
  192-bit 1754 / 5.30e10 / 4.86e10; 224-bit 2042 / 8.43e10 / 7.73e10;
  **256-bit 2330 / 1.26e11 / 1.16e11**; 384-bit 3484 / 4.52e11 / 4.15e11;
  521-bit 4719 / 1.14e12 / 1.05e12.
- Comparison at matched classical security: factoring a 3072-bit RSA modulus
  needs 6146 qubits and 1.86e13 Toffoli gates, so ECC is the easier quantum
  target -- supporting the earlier Proos-Zalka estimates.
- All counts are for logical qubits in a fault-free model; no error-correction
  overhead is included.

## Relevance to this program
Gives the corpus its only concrete quantum cost model, and it is directly
usable as a scoping instrument. A P-256 ECDLP is ~2^128 classical group
operations (KN-LIT-097 puts the public record at 2^60) versus 2330 logical
qubits and ~1.26e11 Toffoli gates quantum -- roughly 2^37 gates. That
separation is the reason a classical advantage claim must always state its
model: a mechanism offering a modest classical constant-factor gain does not
interact with this threat at all, and conversely a "quantum-inspired" proposal
must be checked for whether it is silently assuming quantum resources. It also
supplies the honest caveat for any timeline claim -- these are logical qubits
with no error correction, so they are a lower bound on hardware, not a
prediction.

## Not verified here
The ePrint PDF (2017/598) was fetched and the abstract, the results paragraph,
and the full simulation table (reproduced above) were read directly. The
reversible-arithmetic constructions, the interpolation methodology, and the
LIQUi|> simulations were not checked or reproduced, so the content claims are
`reported`. Note the published Springer version's summary text quotes a
different RSA-3072 Toffoli figure than the ePrint table (1.5e14 versus
1.86e13); the value recorded above is the one in the ePrint text and its
table. Authors, title, venue (ASIACRYPT 2017 Part II, pp. 241-270) and the
identifiers were confirmed against the IACR CryptoDB BibTeX entry, the Springer
DOI record, the arXiv posting and the Microsoft Research publication page; the
LNCS volume number was not separately confirmed and is therefore omitted.
