---
id: KN-LIT-5056
type: literature
title: "Naor-Reingold Goes Public: The Complexity of Known-key Security"
authors:
  - "Pratik Soni"
  - "Stefano Tessaro"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, quantum, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the complexity of building secure block ciphers in the setting where the key is known to the attacker. In particular, we consider two security notions with useful implications, namely public-seed pseudorandom permutations (or psPRPs, for short) (Soni and Tessaro, EUROCRYPT ’17) and correlation-intractable ciphers (Knudsen and Rijmen, ASIACRYPT ’07; Mandal, Seurin, and Patarin, TCC ’12).

## Key claims (as reported)
- For both these notions, we exhibit constructions which make only two calls to an underlying non-invertible primitive, matching the complexity of building a pseudorandom permutation in the secret-key setting.
- Our psPRP result instantiates the round functions in the Naor-Reingold (NR) construction with a secure UCE hash function.
- For correlation intractability, we instead instantiate them from a (public) random function, and replace the pairwise-independent permutations in the NR construction with (almost) O(k2 )-wise independent permutations, where k is the arity of the relations for which we want correlation intractability.
- Our constructions improve upon the current state of the art, requiring five- and six-round Feistel networks, respectively, to achieve psPRP security and correlation intractability.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10822222 (1).pdf`
- `downloads/10822222.pdf`
