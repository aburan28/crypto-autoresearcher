---
id: KN-LIT-6216
type: literature
title: "Removing Erasures with Explainable Hash Proof Systems"
authors:
  - "Michel Abdalla"
  - "Fabrice Benhamouda"
  - "David Pointcheval"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, mpc, pairing, protocol, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
An important problem in secure multi-party computation is the design of protocols that can tolerate adversaries that are capable of corrupting parties dynamically and learning their internal states. In this paper, we make significant progress in this area in the context of password-authenticated key exchange (PAKE) and oblivious transfer (OT) protocols.

## Key claims (as reported)
- More precisely, we first revisit the notion of projective hash proofs and introduce a new feature that allows us to explain any message sent by the simulator in case of corruption, hence the notion of Explainable Projective Hashing.
- Next, we demonstrate that this new tool generically leads to efficient PAKE and OT protocols that are secure against semiadaptive adversaries without erasures in the Universal Composability (UC) framework.
- We then show how to make these protocols secure even against adaptive adversaries, using non-committing encryption, in a much more efficient way than generic conversions from semi-adaptive to adaptive security.
- Finally, we provide concrete instantiations of explainable projective hash functions that lead to the most efficient PAKE and OT protocols known so far, with UC-security against adaptive adversaries, without assuming reliable erasures, in the single global CRS setting.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/101740146 (1).pdf`
- `downloads/101740146 (2).pdf`
- `downloads/101740146 (3).pdf`
- `downloads/101740146 (4).pdf`
- `downloads/101740146.pdf`
