---
id: KN-LIT-755
type: literature
title: "Enhanced Flush+Reload Attack on AES?"
authors:
  - "Milad Seddigh"
  - "Hadi Soleimany"
year: 2020
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2020/907"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2020/907"
tags: [cryptanalysis, pairing, rsa, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In cloud computing, multiple users can share the same physical machine that can potentially leak secret information, in particular when the memory de-duplication is enabled. Flush+Reload attack is a cache-based attack that makes use of resource sharing.

## Key claims (as reported)
- T-table implementation of AES is commonly used in the crypto libraries like OpenSSL.
- Several Flush+Reload attacks on T-table implementation of AES have been proposed in the literature which requires a notable number of encryptions.
- In this paper, we present a technique to enhance the Flush+Reload attack on AES in the ciphertext-only scenario by significantly reducing the number of needed encryptions in both native and cross-VM setups.
- In this paper, we focus on finding the wrong key candidates and keep the right key by considering only the cache miss event.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2020-907.pdf`
