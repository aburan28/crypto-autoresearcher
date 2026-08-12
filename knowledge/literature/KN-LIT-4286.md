---
id: KN-LIT-4286
type: literature
title: "How to Hide Circuits in MPC An Efficient Framework for Private Function Evaluation"
authors:
  - "Payman Mohassel"
  - "Saeed Sadeghian"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We revisit the problem of general-purpose private function evaluation (PFE) wherein a single party P1 holds a circuit C, while each Pi for 1 ≤ i ≤ n holds a private input xi , and the goal is for a subset (or all) of the parties to learn C(x1 , . . . , xn ) but nothing else. We put forth a general framework for designing PFE where the task of hiding the circuit and securely evaluating its gates are addressed independently: First, we reduce the task of hiding the circuit topology to oblivious evaluation of a mapping that encodes the topology of the circuit, which we refer to as oblivious extended permutation (OEP) since the mapping is a generalization of the permutation mapping.

## Key claims (as reported)
- Second, we design a subprotocol for private evaluation of a single gate (PFE for one gate), which we refer to as private gate evaluation (PGE).
- Finally, we show how to naturally combine the two components to obtain efficient and secure PFE.
- We apply our framework to several well-known general-purpose MPC constructions, in each case, obtaining the most efficient PFE construction to date, for the considered setting.
- Similar to the previous work we only consider semi-honest adversaries in this paper.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/78810555 (1).pdf`
- `downloads/78810555 (2).pdf`
- `downloads/78810555 (3).pdf`
- `downloads/78810555.pdf`
