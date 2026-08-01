---
id: KN-LIT-4379
type: literature
title: "Improved (Hierarchical) Inner-Product Encryption from Lattices"
authors:
  - "Keita Xagawa"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Inner-product encryption (IPE) provides fine-grained access control and has attractive applications. Agrawal, Freeman, and Vaikuntanathan (Asiacrypt 2011) proposed the first IPE scheme from lattices by twisting the identity-based encryption (IBE) scheme by Agrawal, Boneh, and Boyen (Eurocrypt 2010).

## Key claims (as reported)
- Their IPE scheme supports inner-product predicates over Rμ , where the ring is R = Zq .
- Several applications require the ring R to be exponentially large and, thus, they set q = 2O(n) to implement such applications.
- This choice results in the AFV IPE scheme with public parameters of size O(μn2 lg3 q) = O(μn5 ) and ciphertexts of size O(μn lg3 q) = O(μn4 ), where n is the security parameter.
- Hence, this makes the scheme impractical, as they noted.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/77780232 (1).pdf`
- `downloads/77780232 (2).pdf`
- `downloads/77780232 (3).pdf`
- `downloads/77780232 (4).pdf`
- `downloads/77780232.pdf`
