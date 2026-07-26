---
id: KN-LIT-6473
type: literature
title: "Secure Two-Party Computation with Reusable Bit-Commitments, via a Cut-and-Choose with Forge-and-Lose Technique"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A secure two-party computation (S2PC) protocol allows two parties to compute over their combined private inputs, as if intermediated by a trusted third party. In the malicious model, this can be achieved with a cut-and-choose of garbled circuits (C&C-GCs), where some GCs are verified for correctness and the remaining are evaluated to determine the circuit output.

## Key claims (as reported)
- This paper presents a new C&C-GCs-based S2PC protocol, with significant advantages in efficiency and applicability.
- First, in contrast with prior protocols that require a majority of evaluated GCs to be correct, the new protocol only requires that at least one evaluated GC is correct.
- In practice this reduces the total number of GCs to approximately one third, for the same statistical security goal.
- This is accomplished by augmenting the C&C with a new forge-and-lose technique based on bit commitments with trapdoor.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/82700441 (1).pdf`
- `downloads/82700441 (2).pdf`
- `downloads/82700441 (3).pdf`
- `downloads/82700441.pdf`
