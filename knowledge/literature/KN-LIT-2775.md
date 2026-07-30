---
id: KN-LIT-2775
type: literature
title: "Bounded CCA2-Secure"
authors:
  - "Eike Kiltz"
  - "Rafael Pass"
  - "abhi shelat"
  - "Vinod Vaikuntanathan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, lattice, mpc, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Whereas encryption schemes withstanding passive chosenplaintext attacks (CPA) can be constructed based on a variety of computational assumptions, only a few assumptions are known to imply the existence of encryption schemes withstanding adaptive chosen-ciphertext attacks (CCA2). Towards addressing this asymmetry, we consider a weakening of the CCA2 model — bounded CCA2-security — wherein security needs only hold against adversaries that make an a-priori bounded number of queries to the decryption oracle.

## Key claims (as reported)
- Regarding this notion we show (without any further assumptions): – For any polynomial q, a simple black-box construction of q-bounded IND-CCA2-secure encryption schemes, from any IND-CPA-secure encryption scheme.
- When instantiated with the Decisional DiffieHellman (DDH) assumption, this construction additionally yields encryption schemes with very short ciphertexts. – For any polynomial q, a (non-black box) construction of q-bounded NM-CCA2-secure encryption schemes, from any IND-CPA-secure encryption scheme.
- Bounded-CCA2 non-malleability is the strongest notion of security yet known to be achievable assuming only the existence of IND-CPA secure encryption schemes.
- Finally, we show that non-malleability and indistinguishability are not equivalent under bounded-CCA2 attacks (in contrast to general CCA2 attacks).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/48330505 (1).pdf`
- `downloads/48330505 (2).pdf`
- `downloads/48330505 (3).pdf`
- `downloads/48330505.pdf`
