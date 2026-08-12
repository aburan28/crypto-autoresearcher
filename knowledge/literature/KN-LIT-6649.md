---
id: KN-LIT-6649
type: literature
title: "Simple and Generic Constructions of Succinct Functional Encryption"
authors:
  - "Fuyuki Kitagawa"
  - "Ryo Nishimaki"
  - "Keisuke Tanaka"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose simple and generic constructions of succinct functional encryption. Our key tool is exponentially-efficient indistinguishability obfuscator (XIO), which is the same as indistinguishability obfuscator (IO) except that the size of an obfuscated circuit (or the running-time of an obfuscator) is slightly smaller than that of a bruteforce canonicalizer that outputs the entire truth table of a circuit to be obfuscated.

## Key claims (as reported)
- A “compression factor” of XIO indicates how much XIO compresses the brute-force canonicalizer.
- In this study, we propose a significantly simple framework to construct succinct functional encryption via XIO and show that XIO is a powerful enough to achieve cutting-edge cryptography.
- In particular, we prove the followings: – Single-key weakly succinct secret-key functional encryption (SKFE) is constructed from XIO (even with a bad compression factor) and one-way function. – Single-key weakly succinct public-key functional encryption (PKFE) is constructed from XIO with a good compression factor and publickey encryption. – Single-key weakly succinct PKFE is constructed from XIO (even with a bad compression factor) and identity-based encryption.
- Our new framework has side benefits.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10770139 (1).pdf`
- `downloads/10770139 (2).pdf`
- `downloads/10770139 (3).pdf`
- `downloads/10770139 (4).pdf`
- `downloads/10770139.pdf`
