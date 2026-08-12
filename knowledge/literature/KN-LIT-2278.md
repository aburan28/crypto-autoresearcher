---
id: KN-LIT-2278
type: literature
title: "A Universally Composable PAKE with Zero Communication Cost (And Why It Shouldn’t Be Considered UC-Secure)"
authors:
  - "Lawrence Roy"
  - "Jiayu Xu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, mpc, pairing, protocol, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A Password-Authenticated Key Exchange (PAKE) protocol allows two parties to agree upon a cryptographic key, when the only information shared in advance is a low-entropy password. The standard security notion for PAKE (Canetti et al., Eurocrypt 2005) is in the Universally Composable (UC) framework.

## Key claims (as reported)
- We show that unlike most UC security notions, UC PAKE does not imply correctness.
- While Canetti et al. has briefly noticed this issue, we present the first comprehensive study of correctness in UC PAKE: 1.
- We show that TrivialPAKE, a no-message protocol that does not satisfy correctness, is a UC PAKE; 2.
- We propose nine approaches to guaranteeing correctness in the UC security notion of PAKE, and show that seven of them are equivalent, whereas the other two are unachievable; 3.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/13940170 (1).pdf`
- `downloads/13940170.pdf`
