---
id: KN-LIT-6684
type: literature
title: "Simulation-Based Concurrent Non-Malleable Commitments and Decommitments"
authors:
  - "Rafail Ostrovsky"
  - "Giuseppe Persiano"
  - "Ivan Visconti"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we consider commitment schemes that are secure against concurrent man-in-the-middle (cMiM) attacks. Under such attacks, two possible notions of security for commitment schemes have been proposed in the literature: concurrent non-malleability with respect to commitment and concurrent non-malleability with respect to decommitment (i.e., opening).

## Key claims (as reported)
- After the original notion of non-malleability introduced by [Dolev, Dwork and Naor STOC 91] that is based on the independence of the committed messages, a new and stronger simulation-based notion of non-malleability has been proposed with respect to openings or with respect to commitment [1,2,3,4] by requiring that for any man-in-the-middle adversary there is a stand-alone adversary that succeeds with the same probability.
- When commitment schemes are used as sub-protocols (which is often the case) the simulation-based notion is much more powerful and simplifies the task of proving the security of the larger protocols.
- The main result of this paper is a commitment scheme that is simulationbased concurrent non-malleable with respect to both commitment and decommitment.
- This property protects against cMiM attacks mounted during both commitments and decommitments which is a crucial security requirement in several applications, as in some digital auctions, in which players have to perform both commitments and decommitments.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54440091 (1).pdf`
- `downloads/54440091 (2).pdf`
- `downloads/54440091 (3).pdf`
- `downloads/54440091.pdf`
