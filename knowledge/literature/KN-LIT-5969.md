---
id: KN-LIT-5969
type: literature
title: "Provable Time-Memory Trade-Offs: Symmetric Cryptography Against Memory-Bounded Adversaries"
authors:
  - "Stefano Tessaro"
  - "Aishwarya Thiruvengadam"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, hash, pollard-rho, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We initiate the study of symmetric encryption in a regime where the memory of the adversary is bounded. For a block cipher with n-bit blocks, we present modes of operation for encryption and authentication that guarantee security beyond 2n encrypted/authenticated messages, as long as (1) the adversary’s memory is restricted to be less than 2n bits, and (2) the key of the block cipher is long enough to mitigate memory-less key-search attacks.

## Key claims (as reported)
- This is the first proposal of a setting which allows to bypass the 2n barrier under a reasonable assumption on the adversarial resources.
- Motivated by the above, we also discuss the problem of stretching the key of a block cipher in the setting where the memory of the adversary is bounded.
- We show a tight equivalence between the security of double encryption in the ideal-cipher model and the hardness of a special case of the element distinctness problem, which we call the list-disjointness problem.
- Our result in particular implies a conditional lower bound on time-memory trade-offs to break PRP security of double encryption, assuming optimality of the worst-case complexity of existing algorithms for list disjointness.

## Relevance to this program
Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11239220 (1).pdf`
- `downloads/11239220.pdf`
