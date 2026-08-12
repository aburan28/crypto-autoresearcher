---
id: KN-LIT-7486
type: literature
title: "Waters Signatures with Optimal Security Reduction"
authors:
  - "Dennis Hofheinz"
  - "Tibor Jager"
  - "Edward Knapp"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Waters signatures (Eurocrypt 2005) can be shown existentially unforgeable under chosen-message attacks under the assumption that the computational Diffie-Hellman problem in the underlying (pairing-friendly) group is hard. The corresponding security proof has a reduction loss of O(` · q), where ` is the bitlength of messages, and q is the number of adversarial signature queries.

## Key claims (as reported)
- The original reduction could √ meanwhile be improved to O( ` · q) (Hofheinz and Kiltz, Crypto 2008); however, it is currently unknown whether a better reduction exists.
- We answer this question as follows: (a) We give a simple modification of Waters signatures, where messages are encoded such that each two encoded messages have a suitably large Hamming distance.
- Somewhat surprisingly, this simple modification suffices to prove security under the CDH assumption with a reduction loss of O(q).
- (b) We also show that any black-box security proof for a signature scheme with re-randomizable signatures must have a reduction loss of at least Ω(q), or the underlying hardness assumption is false.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72930069 (1).pdf`
- `downloads/72930069 (2).pdf`
- `downloads/72930069 (3).pdf`
- `downloads/72930069.pdf`
