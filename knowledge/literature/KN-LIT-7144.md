---
id: KN-LIT-7144
type: literature
title: "Tighter Security for Generic Authenticated Key Exchange in the QROM"
authors:
  - "Jiaxin Pan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, protocol, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We give a tighter security proof for authenticated key exchange (AKE) protocols that are generically constructed from key encapsulation mechanisms (KEMs) in the quantum random oracle model (QROM). Previous works (Hövelmanns et al., PKC 2020) gave reductions for such a KEM-based AKE protocol in the QROM to the underlying primitives with square-root loss and a security loss in the number of users and total sessions.

## Key claims (as reported)
- Our proof is much tighter and does not have square-root loss.
- Namely, it only loses a factor depending on the number of users, not on the number of sessions.
- Our main enabler is a new variant of lossy encryption which we call parameter lossy encryption.
- In this variant, there are not only lossy public keys but also lossy system parameters.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438062 (1).pdf`
- `downloads/14438062.pdf`
