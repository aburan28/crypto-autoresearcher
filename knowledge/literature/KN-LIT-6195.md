---
id: KN-LIT-6195
type: literature
title: "Registered ABE via Predicate Encodings"
authors:
  - "Ziqi Zhu"
  - "Kai Zhang"
  - "Junqing Gong"
  - "Haifeng Qian"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, lattice, pairing, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents the first generic black-box construction of registered attribute-based encryption (Reg-ABE) via predicate encoding [TCC’14]. The generic scheme is based on k-Lin assumption in the prime-order bilinear group and implies the following concrete schemes that improve existing results: – the first Reg-ABE scheme for span program in the prime-order group; prior work uses composite-order group; – the first Reg-ABE scheme for zero inner-product predicate from kLin assumption; prior work relies on generic group model (GGM); – the first Reg-ABE scheme for arithmetic branching program (ABP) which has not been achieved previously.

## Key claims (as reported)
- Technically, we follow the blueprint of Hohenberger et al.
- [EUROCRYPT’23] but start from the prime-order dual-system ABE by Chen et al.
- [EUROCRYPT’15], which transforms a predicate encoding into an ABE.
- The proof follows the dual-system method in the context of Reg-ABE: we conceptually consider helper keys as secret keys; furthermore, malicious public keys are handled via pairing-based quasi-adaptive non-interactive zero-knowledge argument by Kiltz and Wee [EUROCRYPT’15].

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438222 (1).pdf`
- `downloads/14438222.pdf`
