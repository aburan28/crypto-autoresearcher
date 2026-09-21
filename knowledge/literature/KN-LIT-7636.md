---
id: KN-LIT-7636
type: literature
title: "Removable Weak Keys for Discrete Logarithm Based Cryptography"
authors:
  - "Michael John Jacobson Jr."
  - "Prabhat Kushwaha"
year: 2020
venue: "Journal of Cryptographic Engineering; IACR ePrint 2020/1436; arXiv:2011.07483"
identifiers:
  eprint: "2020/1436"
  doi: "10.1007/s13389-020-00250-7"
  arxiv: "2011.07483"
  url: "https://eprint.iacr.org/2020/1436"
tags: [weak-keys, discrete-log, elliptic-curve, cheon, implicit-representation]
confidence: reported
citation_verified: true
added: "2026-07-31"
superseded_by: null
---

## Contribution

Identifies removable weak private keys in prime-order DLP groups when $p-1$
has small divisors: keys lying in small multiplicative subgroups of
$\mathbb{F}_p^*$, recoverable via implicit group representations without breaking
the curve for all users.

## Key claims (from fetched arXiv PDF)

- Weakness is parameter/key-level, not a universal curve trapdoor.
- Many standardized curves have a non-negligible number of such weak keys.
- Certicom challenge instances checked not weak up to a stated bound.

## Relevance to GOAL-ECTD-001

Baseline for key-level (not curve-universal) trapdoors / malicious key
generation. Distinct from a Teske-style system that recovers arbitrary
instance logs on $E_{\mathrm{pub}}$.

## Local copies

- `inputs/ECTD-TESKE-20260731/sources/jk-2020-1436.pdf`
  (arXiv:2011.07483; direct eprint HTTP 403;
  sha256 `65a8ecff9a6a3b275ff76682ea6a579791a4eee41ffd2365aba764a823f5fee8`, 13 pages)
