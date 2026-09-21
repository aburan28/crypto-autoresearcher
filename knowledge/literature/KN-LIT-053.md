---
id: KN-LIT-053
type: literature
title: On Ideal Lattices and Learning with Errors over Rings (Ring-LWE)
authors: [Lyubashevsky Vadim, Peikert Chris, Regev Oded]
year: 2013
venue: Journal of the ACM 60(6):Art.43 (EUROCRYPT 2010, LNCS 6110:1-23)
identifiers:
  eprint: iacr:2012/230
  doi: 10.1145/2535925
  url: https://eprint.iacr.org/2012/230
tags: [ring-lwe, ideal-lattice, learning-with-errors, quantum-reduction, structured-lattice, post-quantum, adjacent]
confidence: established
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Defines Ring-LWE, an algebraic variant of LWE (KN-LIT-050) over polynomial rings,
giving much smaller keys and near-linear (vs quadratic) overhead. Proves the
Ring-LWE distribution is pseudorandom under a QUANTUM worst-case-to-average-case
reduction from hard problems on IDEAL lattices.

## Key claims (as reported)
- Ideal-lattice worst-case hardness => Ring-LWE pseudorandomness (quantum
  reduction); the efficiency foundation for practical lattice crypto.
- JACM 60(6), 2013 is the full version of EUROCRYPT 2010.

## Relevance to this program
POST-QUANTUM foundation, ADJACENT to the ECDLP mission. Recorded as context: the
ring/ideal structure buys efficiency but concentrates security in ideal-lattice
problems; the module generalization (KN-LIT-054) underlies Kyber/Dilithium
(KN-LIT-055, KN-LIT-056). The added algebraic structure is what raises the natural
cross-domain question of whether ideal/module lattices admit structure-exploiting
attacks (KN-OPEN-012) -- the lattice analogue of index calculus.

## Not verified here
Full paper not read; Ring-LWE and its quantum reduction are textbook-level in
lattice cryptography (hence confidence: established). Fields for both JACM 2013 and
EUROCRYPT 2010 confirmed against ACM DL / Springer / IACR records via search, not
by fetching the primary pages.
