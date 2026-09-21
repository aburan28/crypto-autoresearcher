---
id: KN-LIT-5959
type: literature
title: "Protecting Obfuscation Against Algebraic Attacks"
authors:
  - "Boaz Barak"
  - "Sanjam Garg"
  - "Yael Tauman Kalai"
  - "Omer Paneth"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mov-fr, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Recently, Garg, Gentry, Halevi, Raykova, Sahai, and Waters (FOCS 2013) constructed a general-purpose obfuscating compiler for NC1 circuits. We describe a simplified variant of this compiler, and prove that it is a virtual black box obfuscator in a generic multilinear map model.

## Key claims (as reported)
- This improves on Brakerski and Rothblum (eprint 2013) who gave such a result under a strengthening of the Exponential Time Hypothesis.
- We remove this assumption, and thus resolve an open question of Garg et al.
- As shown by Garg et al., a compiler for NC1 circuits can be bootstrapped to a compiler for all polynomial-sized circuits under the learning with errors (LWE) hardness assumption.
- Our result shows that there is a candidate obfuscator that cannot be broken by algebraic attacks, hence reducing the task of creating secure obfuscators in the plain model to obtaining sufficiently strong security guarantees on candidate instantiations of multilinear maps.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84410177 (1).pdf`
- `downloads/84410177 (2).pdf`
- `downloads/84410177 (3).pdf`
- `downloads/84410177.pdf`
