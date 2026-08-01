---
id: KN-LIT-4473
type: literature
title: "IND-CCA-secure Key Encapsulation Mechanism in the Quantum Random Oracle Model, Revisited"
authors:
  - "Haodong Jiang"
  - "Zhenfeng Zhang"
  - "Long Chen"
  - "Hong Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, pqc, protocol, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
With the gradual progress of NIST’s post-quantum cryptography standardization, the Round-1 KEM proposals have been posted for public to discuss and evaluate. Among the IND-CCA-secure KEM constructions, mostly, an IND-CPA-secure (or OW-CPA-secure) public-key encryption (PKE) scheme is first introduced, then some generic transformations are applied to it.

## Key claims (as reported)
- All these generic transformations are constructed in the random oracle model (ROM).
- To fully assess the post-quantum security, security analysis in the quantum random oracle model (QROM) is preferred.
- However, current works either lacked a QROM security proof or just followed Targhi and Unruh’s proof technique (TCC-B 2016) and modified the original transformations by adding an additional hash to the ciphertext to achieve the QROM security.
- In this paper, by using a novel proof technique, we present QROM security reductions for two widely used generic transformations without suffering any ciphertext overhead.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993220 (1).pdf`
- `downloads/10993220.pdf`
