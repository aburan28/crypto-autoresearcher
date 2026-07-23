---
id: KN-LIT-045
type: literature
title: Lattice Attacks on Digital Signature Schemes
authors: [Howgrave-Graham Nick A., Smart Nigel P.]
year: 2001
venue: Designs, Codes and Cryptography, 23(3):283-290
identifiers:
  eprint: null
  doi: 10.1023/A:1011214926272
  url: https://link.springer.com/article/10.1023/A:1011214926272
tags: [dsa, ecdsa, nonce-leakage, lattice, hidden-number-problem, key-recovery, ecdlp-adjacent, cryptanalysis]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
The founding (heuristic) paper on recovering (EC)DSA/DSA secret keys from
signatures whose per-signature nonces are partially known. Formulates
partial-nonce key recovery as a lattice problem and solves it with lattice basis
reduction, demonstrating experimentally that a few leaked bits per nonce across
several signatures suffice.

## Key claims (as reported)
- Small nonce-bit leakage across several signatures -> private-key reconstruction
  via lattice reduction.
- Heuristic / experimental, not rigorously proven; later cited by
  Nguyen-Shparlinski (KN-LIT-044) as the first treatment before their provable
  bounds.

## Relevance to this program
Establishes the practical template -- nonce-leakage + lattice reduction ->
key recovery -- for the lattice/ECDLP intersection this repo tracks. Same crucial
scoping as KN-LIT-044: it attacks the signature scheme under partial-information
leakage, NOT the plain ECDLP (KN-OPEN-011). Historically seeds the entire line;
Nguyen-Shparlinski made it provable and quantified the minimal leakage.

## Not verified here
Full paper not read; the heuristic lattice-attack template relayed from the
abstract and from Nguyen-Shparlinski's account (hence confidence: reported). An
earlier HP Labs technical report (HPL-1999-90) exists but is not an IACR ePrint.
Fields confirmed against Springer/DBLP records via search, not by fetching the
primary page.
