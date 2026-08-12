---
id: KN-LIT-6803
type: literature
title: "Statistical ZAPR Arguments from Bilinear Maps"
authors:
  - "Alex Lombardi"
  - "Vinod Vaikuntanathan"
  - "Daniel Wichs"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, lattice, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Dwork and Naor (FOCS ’00) defined ZAPs as 2-message witness-indistinguishable proofs that are public-coin. We relax this to ZAPs with private randomness (ZAPRs), where the verifier can use private coins to sample the first message (independently of the statement being proved), but the proof must remain publicly verifiable given only the protocol transcript.

## Key claims (as reported)
- In particular, ZAPRs are reusable, meaning that the first message can be reused for multiple proofs without compromising security.
- Known constructions of ZAPs from trapdoor permutations or bilinear maps are only computationally WI (and statistically sound).
- Two recent results of Badrinarayanan-Fernando-Jain-Khurana-Sahai and Goyal-JainJin-Malavolta [EUROCRYPT ’20] construct the first statistical ZAP arguments, which are statistically WI (and computationally sound), from the quasi-polynomial LWE assumption.
- Here, we construct statistical ZAPR arguments from the quasi-polynomial decision-linear (DLIN) assumption on groups with a bilinear map.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105424 (1).pdf`
- `downloads/12105424.pdf`
