---
id: KN-LIT-7022
type: literature
title: "The More The Merrier: Reducing the Cost of Large Scale MPC"
authors:
  - "S. Dov Gordon"
  - "Daniel Starin"
  - "Arkady Yerukhimovich"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, mov-fr, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Secure multi-party computation (MPC) allows multiple parties to perform secure joint computations on their private inputs. Today, applications for MPC are growing with thousands of parties wishing to build federated machine learning models or trusted setups for blockchains.

## Key claims (as reported)
- To address such scenarios we propose a suite of novel MPC protocols that maximize throughput when run with large numbers of parties.
- In particular, our protocols have both communication and computation complexity that decrease with the number of parties.
- Our protocols build on prior protocols based on packed secret-sharing, introducing new techniques to build more efficient computation for general circuits.
- Specifically, we introduce a new approach for handling linear attacks that arise in protocols using packed secret-sharing and we propose a method for unpacking shared multiplication triples without increasing the asymptotic costs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960144 (1).pdf`
- `downloads/126960144.pdf`
