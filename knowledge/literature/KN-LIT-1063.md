---
id: KN-LIT-1063
type: literature
title: "A Post-Quantum Round-Optimal Oblivious PRF from Isogenies"
authors:
  - "Andrea Basso"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/225"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/225"
tags: [cryptanalysis, isogeny, mpc, pqc, protocol, quantum, rsa, sidh-csidh]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
An oblivious pseudorandom function, or OPRF, is an important primitive that is used to build many advanced cryptographic protocols. Despite its relevance, very few post-quantum solutions exist.

## Key claims (as reported)
- In this work, we propose a novel OPRF protocol that is post-quantum, verifiable, round-optimal, and moderately compact.
- Our protocol is based on a previous SIDH-based construction by Boneh, Kogan, and Woo, which was later shown to be insecure due to an attack on its one-more unpredictability.
- We first propose an efficient countermeasure against this attack by redefining the PRF function to use irrational isogenies.
- This prevents a malicious user from independently evaluating the PRF.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2023-225.pdf`
