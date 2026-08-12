---
id: KN-LIT-2606
type: literature
title: "Attack on Broadcast RC4 Revisited"
authors:
  - "Subhamoy Maitra"
  - "Goutam Paul"
  - "Sourav Sen Gupta"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mov-fr, pairing, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, contrary to the claim of Mantin and Shamir (FSE 2001), we prove that there exist biases in the initial bytes (3 to 255) of the RC4 keystream towards zero. These biases immediately provide distinguishers for RC4.

## Key claims (as reported)
- Additionally, the attack on broadcast RC4 to recover the second byte of the plaintext can be extended to recover the bytes 3 to 255 of the plaintext given Ω(N 3 ) many ciphertexts.
- Further, we also study the non-randomness of index j for the first two rounds of PRGA, and identify a strong bias of j2 towards 4.
- This in turn provides us with certain state information from the second keystream byte.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/67330204 (1).pdf`
- `downloads/67330204 (2).pdf`
- `downloads/67330204 (3).pdf`
- `downloads/67330204.pdf`
