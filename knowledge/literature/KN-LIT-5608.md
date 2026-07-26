---
id: KN-LIT-5608
type: literature
title: "On Tight Security Proofs for Schnorr Signatures"
authors:
  - "Nils Fleischhacker"
  - "Tibor Jager"
  - "Dominique Schröder"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, dlp, pairing, provable-security, quantum, rsa, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Schnorr signature scheme is the most efficient signature scheme based on the discrete logarithm problem and a long line of research investigates the existence of a tight security reduction for this scheme in the random oracle. Almost all recent works present lower tightness bounds and most recently Seurin (Eurocrypt 2012) showed that under certain assumptions the non-tight security proof for Schnorr signatures in the random oracle by Pointcheval and Stern (Eurocrypt 1996) is essentially optimal.

## Key claims (as reported)
- All previous works in this direction rule out tight reductions from the (one-more) discrete logarithm problem.
- In this paper we introduce a new meta-reduction technique, which shows lower bounds for the large and very natural class of generic reductions.
- A generic reduction is independent of a particular representation of group elements and most reductions in state-of-the-art security proofs have this desirable property.
- Our approach shows unconditionally that there is no tight generic reduction from any natural computational problem Π defined over algebraic groups (including even interactive problems) to breaking Schnorr signatures, unless solving Π is easy.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/88730258 (1).pdf`
- `downloads/88730258 (2).pdf`
- `downloads/88730258 (3).pdf`
- `downloads/88730258.pdf`
