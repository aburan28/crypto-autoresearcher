---
id: KN-LIT-6665
type: literature
title: "Simple Threshold (Fully Homomorphic) Encryption From LWE With Polynomial Modulus"
authors:
  - "Katharina Boudgoust ID"
  - "Peter Scholl ID"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mpc, pqc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The learning with errors (LWE) assumption is a powerful tool for building encryption schemes with useful properties, such as plausible resistance to quantum computers, or support for homomorphic computations. Despite this, essentially the only method of achieving threshold decryption in schemes based on LWE requires a modulus that is superpolynomial in the security parameter, leading to a large overhead in ciphertext sizes and computation time.

## Key claims (as reported)
- In this work, we propose a (fully homomorphic) encryption scheme that supports a simple t-out-of-n threshold decryption protocol while allowing for a polynomial modulus.
- The main idea is to use the Rényi divergence (as opposed to the statistical distance as in previous works) as a measure of distribution closeness.
- This comes with some technical obstacles, due to the difficulty of using the Rényi divergence in decisional security notions such as standard semantic security.
- We overcome this by constructing a threshold scheme with a weaker notion of one-way security and then showing how to transform any one-way (fully homomorphic) threshold scheme into one guaranteeing indistinguishability-based security.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438289 (1).pdf`
- `downloads/14438289.pdf`
