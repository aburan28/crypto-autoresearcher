---
id: KN-LIT-3797
type: literature
title: "Fast Cryptography in Genus"
authors:
  - "Joppe W. Bos"
  - "Craig Costello"
  - "Huseyin Hisil"
  - "Kristin Lauter"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, dlp, elliptic-curve, endomorphism, extension-field, glv-gls, hyperelliptic, implementation, jacobian, pairing, prime-field, protocol, provable-security, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we highlight the benefits of using genus 2 curves in public-key cryptography. Compared to the standardized genus 1 curves, or elliptic curves, arithmetic on genus 2 curves is typically more involved but allows us to work with moduli of half the size.

## Key claims (as reported)
- We give a taxonomy of the best known techniques to realize genus 2 based cryptography, which includes fast formulas on the Kummer surface and efficient 4-dimensional GLV decompositions.
- By studying different modular arithmetic approaches on these curves, we present a range of genus 2 implementations.
- On a single core of an Intel Core i7-3520M (Ivy Bridge), our implementation on the Kummer surface breaks the 120 thousand cycle barrier which sets a new software speed record at the 128-bit security level for constant-time scalar multiplications compared to all previous genus 1 and genus 2 implementations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/78810192 (1).pdf`
- `downloads/78810192 (2).pdf`
- `downloads/78810192 (3).pdf`
- `downloads/78810192.pdf`
