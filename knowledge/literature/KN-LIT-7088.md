---
id: KN-LIT-7088
type: literature
title: "The Usefulness of Sparsifiable Inputs: How to Avoid Subexponential iO"
authors:
  - "Thomas Agrikola"
  - "Geoffroy Couteau"
  - "Dennis Hofheinz"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mov-fr, mpc, pairing, protocol, provable-security, quantum, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider the problem of removing subexponential reductions to indistinguishability obfuscation (iO) in the context of obfuscating probabilistic programs. Specifically, we show how to apply complexity absorption (Zhandry, Crypto 2016) to the recent notion of probabilistic indistinguishability obfuscation (piO, Canetti et al., TCC 2015).

## Key claims (as reported)
- As a result, we obtain a variant of piO which allows to obfuscate a large class of probabilistic programs, from polynomially secure indistinguishability obfuscation and extremely lossy functions.
- Particularly, our piO variant is able to obfuscate circuits with specific input domains regardless of the performed computation.
- We then revisit several (direct or indirect) applications of piO, and obtain – a fully homomorphic encryption scheme (without circular security assumptions), – a multi-key fully homomorphic encryption scheme with threshold decryption, – an encryption scheme secure under arbitrary key-dependent messages, – a spooky encryption scheme for all circuits, – a function secret sharing scheme with additive reconstruction for all circuits, all from polynomially secure iO, extremely lossy functions, and, depending on the scheme, also other (but polynomial and comparatively mild) assumptions.
- All of these assumptions are implied by polynomially secure iO and the (non-polynomial, but very well-investigated) exponential DDH assumption.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12110120 (1).pdf`
- `downloads/12110120.pdf`
