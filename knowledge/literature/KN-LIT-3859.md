---
id: KN-LIT-3859
type: literature
title: "Fault-Injection Attacks against NIST’s"
authors:
  - "Post-Quantum Cryptography Round KEM"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, factoring, lattice, pqc, protocol, provable-security, quantum, side-channel, sidh-csidh, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We investigate all NIST PQC Round 3 KEM candidates from the viewpoint of fault-injection attacks: Classic McEliece, Kyber, NTRU, Saber, BIKE, FrodoKEM, HQC, NTRU Prime, and SIKE. All KEM schemes use variants of the Fujisaki-Okamoto transformation, so the equality test with re-encryption in decapsulation is critical.

## Key claims (as reported)
- We survey effective key-recovery attacks when we can skip the equality test.
- We found the existing key-recovery attacks against Kyber, NTRU, Saber, FrodoKEM, HQC, one of two KEM schemes in NTRU Prime, and SIKE.
- We propose a new key-recovery attack against the other KEM scheme in NTRU Prime.
- We also report an attack against BIKE that leads to leakage of information of secret keys.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900205 (1).pdf`
- `downloads/130900205.pdf`
