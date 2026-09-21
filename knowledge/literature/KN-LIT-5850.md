---
id: KN-LIT-5850
type: literature
title: "Practical Leakage-Resilient Symmetric Cryptography"
authors:
  - "Sebastian Faust⋆"
  - "Krzysztof Pietrzak⋆⋆"
  - "Joachim Schipper"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, quantum, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Leakage resilient cryptography attempts to incorporate sidechannel leakage into the black-box security model and designs cryptographic schemes that are provably secure within it. Informally, a scheme is leakage-resilient if it remains secure even if an adversary learns a bounded amount of arbitrary information about the schemes internal state.

## Key claims (as reported)
- Unfortunately, most leakage resilient schemes are unnecessarily complicated in order to achieve strong provable security guarantees.
- As advocated by Yu et al.
- [CCS’10], this mostly is an artefact of the security proof and in practice much simpler construction may already suffice to protect against realistic side-channel attacks.
- In this paper, we show that indeed for simpler constructions leakage-resilience can be obtained when we aim for relaxed security notions where the leakage-functions and/or the inputs to the primitive are chosen non-adaptively.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74280211 (1).pdf`
- `downloads/74280211 (2).pdf`
- `downloads/74280211 (3).pdf`
- `downloads/74280211.pdf`
