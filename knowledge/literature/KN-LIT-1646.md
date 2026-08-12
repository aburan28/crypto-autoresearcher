---
id: KN-LIT-1646
type: literature
title: "Fast Difficulty Adjustment in Proof-of-Work Consensus"
authors:
  - "Juan Garay"
  - "Aggelos Kiayias"
  - "Yu Shen"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1116"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1116"
tags: [implementation, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
One of the main hallmarks of proof-of-work (PoW) consensus protocols is their ability to adjust the difficulty of the PoW, so that it accurately reflects the level of participation and hence maintains security in a setting where protocol participation is unknown and may over time change dramatically. Importantly, this enables the protocol to retain its fundamental characteristics (such as the regularity of dispensing new tokens) irrespectively of the number of parties running the protocol (also known as “miners”) at any given time.

## Key claims (as reported)
- The speed with which difficulty can be adjusted is a fundamental feature of a blockchain protocol: The faster the rate with which the difficulty is adjusted, the more agile the protocol is in the face of fluctuating participation.
- In this work, we put forward, for the first time, a blockchain protocol that performs difficulty adjustment in constant time; prior provably secure designs only offered protocols with, at best, poly-logarithmic overhead for difficulty adjustment.
- Our construction is based on the parallel-chain approach and a new target recalculation function that adjusts mining difficulty making use of information from all chains in the past epoch via a novel application of approximate-agreement techniques that may be of independent interest. ∗ † An abridged version of this paper appears in Proc.
- Research supported in part by NSF grant no.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1116.pdf`
