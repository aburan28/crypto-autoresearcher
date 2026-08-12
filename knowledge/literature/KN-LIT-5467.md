---
id: KN-LIT-5467
type: literature
title: "On the Exact Security of Schnorr-Type Signatures in the Random Oracle Model"
authors:
  - "Yannick Seurin"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, dlp, provable-security, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Schnorr signature scheme has been known to be provably secure in the Random Oracle Model under the Discrete Logarithm (DL) assumption since the work of Pointcheval and Stern (EUROCRYPT ’96), at the price of a very loose reduction though: if there is a forger making at most qh random oracle queries, and forging signatures with probability εF , then the Forking Lemma tells that one can compute discrete logarithms with constant probability by rewinding the forger O(qh /εF ) times. In other words, the security reduction loses a factor O(qh ) in its time-to-success ratio.

## Key claims (as reported)
- This is rather unsatisfactory since qh may be quite large.
- Yet Paillier and Vergnaud (ASIACRYPT 2005) later showed that under the One More Discrete Logarithm (OMDL) assumption, any alge1/2 braic reduction must lose a factor at least qh in its time-to-success ratio.
- 2/3 This was later improved by Garg et al.
- (CRYPTO 2008) to a factor qh .

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72370550 (1).pdf`
- `downloads/72370550 (2).pdf`
- `downloads/72370550 (3).pdf`
- `downloads/72370550.pdf`
