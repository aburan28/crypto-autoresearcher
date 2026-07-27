---
id: KN-LIT-5637
type: literature
title: "Online/Offline Attribute-Based Encryption"
authors:
  - "Susan Hohenberger"
  - "Brent Waters"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Attribute-based encryption (ABE) is a type of public key encryption that allows users to encrypt and decrypt messages based on user attributes. For instance, one can encrypt a message to any user satisfying the boolean formula (“crypto conference attendee” AND “PhD student”) OR “IACR member”.

## Key claims (as reported)
- One drawback is that encryption and key generation computational costs scale with the complexity of the access policy or number of attributes.
- In practice, this makes encryption and user key generation a possible bottleneck for some applications.
- To address this problem, we develop new techniques for ABE that split the computation for these algorithms into two phases: a preparation phase that does the vast majority of the work to encrypt a message or create a secret key before it knows the message or the attribute list/access control policy that will be used (or even the size of the list or policy).
- A second phase can then rapidly assemble an ABE ciphertext or key when the specifics become known.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/83830105 (1).pdf`
- `downloads/83830105 (2).pdf`
- `downloads/83830105 (3).pdf`
- `downloads/83830105 (4).pdf`
- `downloads/83830105 (5).pdf`
- `downloads/83830105.pdf`
