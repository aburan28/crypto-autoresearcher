---
id: KN-LIT-5167
type: literature
title: "Non-Committing Encryption with Quasi-Optimal Ciphertext-Rate Based on the DDH Problem"
authors:
  - "Yusuke Yoshida"
  - "Fuyuki Kitagawa"
  - "Keisuke Tanaka"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Non-committing encryption (NCE) was introduced by Canetti et al. Informally, an encryption scheme is non-committing if it can generate a dummy ciphertext that is indistinguishable from a real one.

## Key claims (as reported)
- The dummy ciphertext can be opened to any message later by producing a secret key and an encryption random coin which “explain” the ciphertext as an encryption of the message.
- Canetti et al. showed that NCE is a central tool to achieve multi-party computation protocols secure in the adaptive setting.
- An important measure of the efficiently of NCE is the ciphertext rate, that is the ciphertext length divided by the message length, and previous works studying NCE have focused on constructing NCE schemes with better ciphertext rates.
- We propose an NCE scheme satisfying the ciphertext rate O(log λ) based on the decisional Diffie-Hellman (DDH) problem, where λ is the security parameter.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210162 (1).pdf`
- `downloads/119210162.pdf`
