---
id: KN-LIT-5915
type: literature
title: "Private Mutual Authentication and Conditional Oblivious Transfer"
authors:
  - "Stanislaw Jarecki"
  - "Xiaomin Liu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, protocol, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A bi-directional Private Authentication, or Unlinkable Secret Handshake, allows two parties to authenticate each other as certified by given certification authorities (i.e. affiliated with given groups), in a mutually private way, in the sense that the protocol leaks no information about either participant to a party which does not satisfy that participant’s authentication policy. In particular, the protocol hides what group this participant belongs to, and protocol instances involving the same participant are unlinkable.

## Key claims (as reported)
- We construct the first realization of such private authentication using O(1) exponentiations and bilinear maps, secure under Strong Diffie-Hellman and Decisional Linear assumptions.
- Our protocols rely on a novel technical tool, a family of efficient Private Conditional Oblivious Transfer (COT) protocols, secure under DDH, for languages defined by modular arithmetic constraints (e.g. equality, inequality, sums, products) on discrete-log representations of some group elements.
- (Recall that (w1 , ..., wn ) is a representation of C in bases (g1 , ..., gn ) if C = g1w1 ...gnwn .) A COT protocol for language L allows sender S to encrypt message m “under” statement x so that receiver R gets m only if R holds a witness for membership of x in L, while S learns nothing.
- A private COT for L hides not only message m but also statement x from any R that does not know a witness for x in L.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56770090 (1).pdf`
- `downloads/56770090 (2).pdf`
- `downloads/56770090 (3).pdf`
- `downloads/56770090.pdf`
