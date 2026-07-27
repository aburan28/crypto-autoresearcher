---
id: KN-LIT-7116
type: literature
title: "Threshold Ring Signatures:"
authors:
  - "New Definitions"
  - "Post-Quantum Security"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, pqc, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A t-out-of-N threshold ring signature allows t parties to jointly and anonymously compute a signature on behalf on N public keys, selected in an arbitrary manner among the set of all public keys registered in the system. Existing definitions for t-out-of-N threshold ring signatures guarantee security only when the public keys are honestly generated, and many even restrict the ability of the adversary to actively participate in the computation of the signatures.

## Key claims (as reported)
- Such definitions do not capture the open settings envisioned for threshold ring signatures, where parties can independently add themselves to the system, and join other parties for the computation of the signature.
- Furthermore, known constructions of threshold ring signatures are not provably secure in the post-quantum setting, either because they are based on non-post quantum secure problems (e.g.
- Discrete Log, RSA), or because they rely on transformations such as Fiat-Shamir, that are not always secure in the quantum random oracle model (QROM).
- In this paper, we provide the first definition of t-out-of-N threshold ring signatures against active adversaries who can participate in the system and arbitrarily deviate from the prescribed procedures.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12110260 (1).pdf`
- `downloads/12110260.pdf`
