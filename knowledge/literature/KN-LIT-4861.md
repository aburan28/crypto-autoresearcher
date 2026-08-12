---
id: KN-LIT-4861
type: literature
title: "Masking the GLP Lattice-Based Signature Scheme at Any Order Gilles Barthe1 , Sonia Belaı̈d2 , Thomas Espitau3 , Pierre-Alain Fouque4"
authors:
  - "Benjamin Grégoire"
  - "Mélissa Rossi"
  - "Mehdi Tibouchi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, ecdsa, elliptic-curve, lattice, rsa, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Recently, numerous physical attacks have been demonstrated against lattice-based schemes, often exploiting their unique properties such as the reliance on Gaussian distributions, rejection sampling and FFT-based polynomial multiplication. As the call for concrete implementations and deployment of postquantum cryptography becomes more pressing, protecting against those attacks is an important problem.

## Key claims (as reported)
- However, few countermeasures have been proposed so far.
- In particular, masking has been applied to the decryption procedure of some lattice-based encryption schemes, but the much more difficult case of signatures (which are highly non-linear and typically involve randomness) has not been considered until now.
- In this paper, we describe the first masked implementation of a latticebased signature scheme.
- Since masking Gaussian sampling and other procedures involving contrived probability distribution would be prohibitively inefficient, we focus on the GLP scheme of Güneysu, Lyubashevsky and Pöppelmann (CHES 2012).

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10822206 (1).pdf`
- `downloads/10822206.pdf`
