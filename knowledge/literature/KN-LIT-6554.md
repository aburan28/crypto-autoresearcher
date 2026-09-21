---
id: KN-LIT-6554
type: literature
title: "Separate Your Domains:"
authors:
  - "NIST PQC KEMs"
  - "Oracle Cloning and"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pqc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
It is convenient and common for schemes in the random oracle model to assume access to multiple random oracles (ROs), leaving to implementations the task —we call it oracle cloning— of constructing them from a single RO. The first part of the paper is a case study of oracle cloning in KEM submissions to the NIST Post-Quantum Cryptography standardization process.

## Key claims (as reported)
- We give key-recovery attacks on some submissions arising from mistakes in oracle cloning, and find other submissions using oracle cloning methods whose validity is unclear.
- Motivated by this, the second part of the paper gives a theoretical treatment of oracle cloning.
- We give a definition of what is an “oracle cloning method” and what it means for such a method to “work,” in a framework we call readonly indifferentiability, a simple variant of classical indifferentiability that yields security not only for usage in single-stage games but also in multistage ones.
- We formalize domain separation, and specify and study many oracle cloning methods, including common domain-separating ones, giving some general results to justify (prove read-only indifferentiability of) certain classes of methods.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105462 (1).pdf`
- `downloads/12105462.pdf`
