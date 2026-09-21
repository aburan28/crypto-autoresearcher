---
id: KN-LIT-6872
type: literature
title: "Subversion-zero-knowledge SNARKs"
authors:
  - "Georg Fuchsbauer"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Subversion zero knowledge for non-interactive proof systems demands that zero knowledge (ZK) be maintained even when the common reference string (CRS) is chosen maliciously. SNARKs are proof systems with succinct proofs, which are at the core of the cryptocurrency Zcash, whose anonymity relies on ZK-SNARKs; they are also used for ZK contingent payments in Bitcoin.

## Key claims (as reported)
- We show that under a plausible hardness assumption, the most efficient SNARK schemes proposed in the literature, including the one underlying Zcash and contingent payments, satisfy subversion ZK or can be made to at very little cost.
- In particular, we prove subversion ZK of the original SNARKs by Gennaro et al. and the almost optimal construction by Groth; for the Pinocchio scheme implemented in libsnark we show that it suffices to add 4 group elements to the CRS.
- We also argue informally that Zcash is anonymous even if its parameters were set up maliciously.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10770155 (1).pdf`
- `downloads/10770155 (2).pdf`
- `downloads/10770155 (3).pdf`
- `downloads/10770155 (4).pdf`
- `downloads/10770155.pdf`
