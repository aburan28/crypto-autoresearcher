---
id: KN-LIT-4758
type: literature
title: "Linear-Time Arguments with Sublinear Verification from Tensor Codes"
authors:
  - "Jonathan Bootle"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Minimizing the computational cost of the prover is a central goal in the area of succinct arguments. In particular, it remains a challenging open problem to construct a succinct argument where the prover runs in linear time and the verifier runs in polylogarithmic time.

## Key claims (as reported)
- We make progress towards this goal by presenting a new linear-time probabilistic proof.
- For any fixed  > 0, we construct an interactive oracle proof (IOP) that, when used for the satisfiability of an N -gate arithmetic circuit, has a prover that uses O(N ) field operations and a verifier that uses O(N  ) field operations.
- The sublinear verifier time is achieved in the holographic setting for every circuit (the verifier has oracle access to a linear-size encoding of the circuit that is computable in linear time).
- When combined with a linear-time collision-resistant hash function, our IOP immediately leads to an argument system where the prover performs O(N ) field operations and hash computations, and the verifier performs O(N  ) field operations and hash computations (given a short digest of the N -gate circuit).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550117 (1).pdf`
- `downloads/12550117.pdf`
