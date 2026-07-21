---
id: KN-LIT-013
type: literature
title: The Discrete-Logarithm Problem with Preprocessing
authors: [Corrigan-Gibbs Henry, Kogan Dmitry]
year: 2018
venue: EUROCRYPT 2018, LNCS 10821, pp. 415-447
identifiers:
  eprint: iacr:2017/1113
  doi: 10.1007/978-3-319-78375-8_14
  url: https://eprint.iacr.org/2017/1113
tags: [preprocessing, non-uniform, advice, generic-group-model, lower-bound, discrete-logarithm, baseline, ecdlp]
confidence: reported
citation_verified: web
added: 2026-07-21
superseded_by: null
---

## Contribution
Studies generic discrete-log algorithms with *preprocessing*: an unbounded
offline phase emits an S-bit advice string about a specific fixed group (e.g. a
standardized curve), then an online phase uses that advice to solve DL in time
T with success probability epsilon. Proves any such generic algorithm satisfies
S*T^2 = Omega~(epsilon*N) for a group of prime order N, and shows the bound is
essentially tight via a matching generic algorithm.

## Key claims (as reported)
- Generic preprocessing lower bound S*T^2 = Omega~(epsilon*N); tight
  (a construction achieves S*T^2 ~ N), so with advice the online cost *can*
  beat the classic sqrt(N) generic bound.
- Analogous preprocessing bounds hold for CDH, DDH, and the squaring problem.
- The unified proof technique is generalized by Coretti, Dodis, Guo,
  "Non-Uniform Bounds in the Random-Permutation, Ideal-Cipher, and
  Generic-Group Models," CRYPTO 2018 (iacr:2018/226), via bit-fixing /
  presampling.

## Relevance to this program
Sets the generic bar in the *fixed-curve / advice* regime -- exactly the
setting of the program's isogeny-class-amortized preprocessing candidate
(RQ-ISADV / EXP-ISADV-001) and the "fixed-curve preprocessing compiler vs the
S*T^2 frontier" open question the research-direction docs cite (OFQ-autolab-81).
A non-generic preprocessing attack must surpass the S*T^2 ~ N tradeoff, not the
sqrt(N) online bound alone.

## Not verified here
Full paper not read; the S*T^2 bound, its tightness, and the CDG generalization
are relayed from the ePrint abstract and secondary sources. Bibliographic
fields confirmed against IACR ePrint / publisher DOI via search.
