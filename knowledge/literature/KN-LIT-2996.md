---
id: KN-LIT-2996
type: literature
title: "Compact Selective Opening Security From LWE"
authors:
  - "Dennis Hofheinz"
  - "Kristina Hostáková"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, pqc, provable-security, rsa, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Selective opening (SO) security is a security notion for publickey encryption schemes that captures security against adaptive corruptions of senders. SO security comes in chosen-plaintext (SO-CPA) and chosen-ciphertext (SO-CCA) variants, neither of which is implied by standard security notions like IND-CPA or IND-CCA security.

## Key claims (as reported)
- In this paper, we present the first SO-CCA secure encryption scheme that combines the following two properties: (1) it has a constant ciphertext expansion (i.e., ciphertexts are only larger than plaintexts by a constant factor), and (2) its security can be proven from a standard assumption.
- Previously, the only known SO-CCA secure encryption scheme achieving (1) was built from an ad-hoc assumption in the RSA regime.
- Our construction builds upon LWE, and in particular on a new and surprisingly simple construction of compact lossy trapdoor functions (LTFs).
- Our LTF can be converted into an “all-but-many LTF” (or ABM-LTF), which is known to be sufficient to obtain SO-CCA security.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14602162 (1).pdf`
- `downloads/14602162.pdf`
