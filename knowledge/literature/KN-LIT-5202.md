---
id: KN-LIT-5202
type: literature
title: "Non-Interactive Zero-Knowledge Functional Proofs"
authors:
  - "Gongxian Zeng"
  - "Junzuo Lai( )"
  - "Zhengan Huang( )"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we consider to generalize NIZK by empowering a prover to share a witness in a fine-grained manner with verifiers. Roughly, the prover is able to authorize a verifier to obtain extra information of witness, i.e., besides verifying the truth of the statement, the verifier can additionally obtain certain function of the witness from the accepting proof using a secret functional key provided by the prover.

## Key claims (as reported)
- To fulfill these requirements, we introduce a new primitive called noninteractive zero-knowledge functional proofs (fNIZKs), and formalize its security notions.
- We provide a generic construction of fNIZK for any NP relation R, which enables the prover to share any function of the witness with a verifier.
- For a widely-used relation about set membership proof (implying range proof), we construct a concrete and efficient fNIZK, through new building blocks (set membership encryption and dual innerproduct encryption), which might be of independent interest.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438265 (1).pdf`
- `downloads/14438265.pdf`
