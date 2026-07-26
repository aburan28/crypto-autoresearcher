---
id: KN-LIT-1947
type: literature
title: "Updatable Public-Key Encryption from FESTA"
authors:
  - "Andrea Basso"
  - "Tako Boris Fouotsa"
  - "Fatna Kouider"
  - "Péter Kutas"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1014"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1014"
tags: [dlp, isogeny, lattice, mov-fr, pqc, sidh-csidh, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Updatable public-key encryption (UPKE) is a cryptographic primitive that was proposed for secure messaging to provide forward secrecy in public-key settings. It extends standard public-key encryption with a key-update mechanism that lets anyone update a receiver’s public key and issue a corresponding token for updating the secret key.

## Key claims (as reported)
- Unlike traditional forward secrecy where all past messages should remain secure after a key leakage, UPKEs guarantee security only as long as at least one honest update has occurred.
- While classically-secure efficient instantiations of UPKE are known from Diffie-Hellman assumptions, constructing an efficient post-quantum secure UPKE scheme with unbounded updates remains an open problem.
- In this work, we propose an isogeny-based UPKE that relies on a dimension-four version of the FESTA public-key encryption scheme.
- It is practically efficient and supports an unbounded amount of updates.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1014.pdf`
