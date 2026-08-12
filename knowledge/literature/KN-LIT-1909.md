---
id: KN-LIT-1909
type: literature
title: "The Impossibility of Post-Quantum Public Indifferentiability for Merkle-Damgård"
authors:
  - "Akinori Hosoyamada"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/128"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/128"
tags: [hash, lattice, pqc, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Merkle-Damgård construction (in its strengthened form as used in SHA-256 and SHA-512, the untruncated members of SHA-2) is not classically indifferentiable from a Variable-Input-Length (VIL) random oracle because of the length-extension attack. Nevertheless, Dodis, Ristenpart, and Shrimpton showed that Merkle-Damgård is publicly indifferentiable, a weaker notion that still justifies replacing a VIL random oracle by Merkle-Damgård in many security proofs when all inputs to a random oracle are public (e.g., Fiat-Shamir and full-domain-hash signatures).

## Key claims (as reported)
- In this paper, we show that this replacement fails in the post-quantum setting: (Strengthened) Merkle-Damgård is not publicly indifferentiable from a VIL random oracle against quantum distinguishers with superposition access to the underlying primitive (while construction queries remain classical), even if the compression function is ideally random.
- We first formalize post-quantum public indifferentiability so that the corresponding composition theorem extends to the quantum random oracle model.
- We also introduce a post-quantum version of sequential indifferentiability, an even weaker notion.
- We then prove that (strengthened) Merkle-Damgård satisfies neither notion by showing that an explicit quantum distinguisher achieves non-negligible advantage against any efficient simulator, using Zhandry’s compressed-oracle technique.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-128.pdf`
