---
id: KN-LIT-2689
type: literature
title: "Beyond Birthday Bound Secure MAC in Faulty Nonce Model"
authors:
  - "Avijit Dutta"
  - "Mridul Nandi"
  - "Suprita Talnikar"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Encrypt-then-MAC (EtM) is a popular mode for authenticated encryption (AE). Unfortunately, almost all designs following the EtM paradigm, including the AE suites for TLS, are vulnerable against nonce misuse.

## Key claims (as reported)
- A single repetition of the nonce value reveals the hash key, leading to a universal forgery attack.
- There are only two authenticated encryption schemes following the EtM paradigm which can resist nonce misuse attacks, the GCM-RUP (CRYPTO-17) and the GCM/2+ (INSCRYPT-12).
- However, they are secure only up to the birthday bound in the nonce respecting setting, resulting in a restriction on the data limit for a single key.
- In this paper we show that nEHtM, a nonce-based variant of EHtM (FSE-10) constructed using a block cipher, has a beyond birthday bound (BBB) unforgeable security that gracefully degrades under nonce misuse.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114760251 (1).pdf`
- `downloads/114760251.pdf`
