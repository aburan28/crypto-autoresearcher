---
id: KN-LIT-1915
type: literature
title: "The Privacy Subsidy: Kyle’s λ under Noise-Perturbed Order-Flow Observation"
authors:
  - "Yuki Nakamura"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2605.15746"
  url: "https://arxiv.org/abs/2605.15746"
tags: [mov-fr, mpc, pairing, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Privacy-preserving cryptocurrency exchanges alter what the pricing mechanism observes about order flow. We derive the unique linear Kyle equilibrium when a committed Bayesian market maker observes order flow perturbed by independent Gaussian privacy noise.

## Key claims (as reported)
- The priceimpact coefficient and informed-trader strategy both rescale by a single factor in the privacy parameter, and their product is invariant.
- A welfare decomposition then identifies a closed-form per-period transfer from the protocol’s LP pool to traders — the privacy subsidy, the break-even fee any privacy-aggregated exchange must charge.
- The result is the singleperiod closed-form privacy-noise analog of Loss-Versus-Rebalancing [11].
- The primary application is shielded AMMs with explicit additive-noise injection (e.g., differential privacy); related designs (batched swaps, sealedbid auctions, oracle-pegged crossings) require separate frameworks that we leave to future work.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2605.15746v2.pdf`
