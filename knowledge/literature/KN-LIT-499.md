---
id: KN-LIT-499
type: literature
title: "Efficient Secure Multiparty Computation with Identifiable Abort"
authors:
  - "Carsten Baum"
  - "Emmanuela Orsini"
  - "Peter Scholl"
year: 2016
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2016/187"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2016/187"
tags: [fhe, mpc, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study secure multiparty computation (MPC) in the dishonest majority setting providing security with identifiable abort, where if the protocol aborts, the honest parties can agree upon the identity of a corrupt party. All known constructions that achieve this notion require expensive zero-knowledge techniques to obtain active security, so are not practical.

## Key claims (as reported)
- In this work, we present the first efficient MPC protocol with identifiable abort.
- Our protocol has an information-theoretic online phase with message complexity O(n2 ) for each secure multiplication (where n is the number of parties), similar to the BDOZ protocol (Bendlin et al., Eurocrypt 2011), which is a factor in the security parameter lower than the identifiable abort protocol of Ishai et al.
- A key component of our protocol is a linearly homomorphic information-theoretic signature scheme, for which we provide the first definitions and construction based on a previous non-homomorphic scheme.
- We then show how to implement the preprocessing for our protocol using somewhat homomorphic encryption, similarly to the SPDZ protocol (Damgård et al., Crypto 2012).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/99850196 (1).pdf`
- `downloads/99850196.pdf`
