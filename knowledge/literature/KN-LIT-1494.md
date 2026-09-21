---
id: KN-LIT-1494
type: literature
title: "Threshold Public-Key Encryption:"
authors:
  - "CPA-to-CCA Transforms"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/1665"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/1665"
tags: [mov-fr, provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Threshold public-key encryption (TPKE) allows t out of k parties to jointly decrypt a ciphertext, while ensuring confidentiality against any coalition of t − 1 parties. Despite its long history and ongoing standardisation efforts, there has not been a dedicated study on its basic security notions, and a handful of variations are currently in use.

## Key claims (as reported)
- We initiate the systematic study of TPKE confidentiality and develop relations between notions contrasting indistinguishability (IND) vs. simulatability (SIM), passive (CPA) vs. active (CCA) attacks, and static vs. adaptive corruptions.
- One of our insights is that security under maximal corruptions does not imply security under fewer corruptions when the adversary has access to partial decryptions on challenge ciphertexts.
- Maximal corruption was adopted by a significant portion of prior works, and this calls for cautious interpretation when using such a notion.
- We complement our study by providing two generic CPA-to-CCA transforms for TPKE.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-1665.pdf`
