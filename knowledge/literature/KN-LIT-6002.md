---
id: KN-LIT-6002
type: literature
title: "PSS is Secure against Random Fault Attacks"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, lattice, provable-security, quantum, rsa, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A fault attack consists in inducing hardware malfunctions in order to recover secrets from electronic devices. One of the most famous fault attack is Bellcore’s attack against RSA with CRT; it consists in inducing a fault modulo p but not modulo q at signature generation step; then by taking a gcd the attacker can recover the factorization of N = pq.

## Key claims (as reported)
- The Bellcore attack applies to any encoding function that is deterministic, for example FDH.
- Recently, the attack was extended to randomized encodings based on the iso/iec 9796-2 signature standard.
- Extending the attack to other randomized encodings remains an open problem.
- In this paper, we show that the Bellcore attack cannot be applied to the PSS encoding; namely we show that PSS is provably secure against random fault attacks in the random oracle model, assuming that inverting RSA is hard.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/59120649 (1).pdf`
- `downloads/59120649 (2).pdf`
- `downloads/59120649 (3).pdf`
- `downloads/59120649.pdf`
