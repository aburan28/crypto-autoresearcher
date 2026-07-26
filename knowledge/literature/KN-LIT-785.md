---
id: KN-LIT-785
type: literature
title: "Modified Cache Template Attack on AES"
authors:
  - "Mahdi Esfahani"
  - "Hadi Soleimany"
  - "Mohammad Reza Aref"
year: 2020
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2020/1560"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2020/1560"
tags: [cryptanalysis, rsa, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
CPU caches are a powerful source of information leakage. To develop practical cache-based attacks, there is an increasingly need to automate the process of finding exploitable cache-based side-channels in computer systems.

## Key claims (as reported)
- Cache template attack is a generic technique that utilizes Flush+Reload attack in order to automatically exploit cache vulnerability of Intel platforms.
- Cache template attack on T-table-based AES implementation consists of two phases including the profiling phase and the key exploitation phase.
- Profiling is a preprocessing phase to monitor dependencies between the secret key and behavior of the cache memory.
- In addition, the addresses of T-tables can be obtained automatically.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2020-1560.pdf`
