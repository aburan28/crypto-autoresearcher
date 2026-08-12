---
id: KN-LIT-4017
type: literature
title: "Functional Commitments for All Functions, with Transparent Setup and from SIS"
authors:
  - "Leo de Castro"
  - "Chris Peikert"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, pairing, pqc, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A functional commitment scheme enables a user to concisely commit to a function from a specified family, then later concisely and verifiably reveal values of the function at desired inputs. Useful special cases, which have seen applications across cryptography, include vector commitments and polynomial commitments.

## Key claims (as reported)
- To date, functional commitments have been constructed (under falsifiable assumptions) only for functions that are essentially linear, with one recent exception that works for arbitrarily complex functions.
- However, that scheme operates in a strong and non-standard model, requiring an online, trusted authority to generate special keys for any opened function inputs.
- In this work, we give the first functional commitment scheme for nonlinear functions—indeed, for all functions of any bounded complexity—under a standard setup and a falsifiable assumption.
- Specifically, the setup is “transparent,” requiring only public randomness (and not any trusted entity), and the assumption is the hardness of the standard Short Integer Solution (SIS) lattice problem.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004065 (1).pdf`
- `downloads/14004065.pdf`
