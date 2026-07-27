---
id: KN-LIT-3205
type: literature
title: "Credibility in Private Set Membership Sanjam Garg1,2 , Mohammad Hajiabadi3 , Abhishek Jain4 , Zhengzhong Jin5"
authors:
  - "Omkant Pandey"
  - "Sina Shiehian"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A private set membership (PSM) protocol allows a “receiver” to learn whether its input x is contained in a large database DB held by a “sender”. In this work, we define and construct credible private set membership (C-PSM) protocols: in addition to the conventional notions of privacy, C-PSM provides a soundness guarantee that it is hard for a sender (that does not know x) to convince the receiver that x ∈ DB.

## Key claims (as reported)
- Furthermore, the communication complexity must be logarithmic in the size of DB.
- We provide 2-round (i.e., round-optimal) C-PSM constructions based on standard assumptions: – We present a black-box construction in the plain model based on DDH or LWE. – Next, we consider protocols that support predicates f beyond string equality, i.e., the receiver can learn if there exists w ∈ DB such that f (x, w) = 1.
- We present two results with transparent setups: (1) A black-box protocol, based on DDH or LWE, for the class of NC1 functions f which are efficiently searchable.
- (2) An LWE-based construction for all bounded-depth circuits.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/13940080 (1).pdf`
- `downloads/13940080.pdf`
