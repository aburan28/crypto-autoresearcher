---
id: KN-LIT-7638
type: literature
title: "Publicly Verifiable Zero-Knowledge and Post-Quantum Signatures From VOLE-in-the-Head"
authors:
  - "Carsten Baum"
  - "Lennart Braun"
  - "Cyprien Delpech de Saint Guilhem"
  - "Michael Klooß"
  - "Emmanuela Orsini"
  - "Lawrence Roy"
  - "Peter Scholl"
year: 2023
venue: 'CRYPTO 2023 (IACR); Cryptology ePrint Archive, Paper 2023/996'
identifiers:
  eprint: '2023/996'
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2023/996
tags: [faest, vole-in-the-head, zero-knowledge, fiat-shamir, nizk, mpc-in-the-head, post-quantum-signatures, aes, crypto-2023, primary-source]
confidence: reported
citation_verified: true
added: "2026-07-31"
superseded_by: null
---

## Citation (verified against the eprint landing page)

Carsten Baum, Lennart Braun, Cyprien Delpech de Saint Guilhem, Michael
Klooß, Emmanuela Orsini, Lawrence Roy, Peter Scholl. *Publicly Verifiable
Zero-Knowledge and Post-Quantum Signatures From VOLE-in-the-Head.*
Cryptology ePrint Archive, Paper 2023/996. IACR publication info: "A major
revision of an IACR publication in CRYPTO 2023". Received 2023-06-26,
approved 2023-06-27. Short URL: https://ia.cr/2023/996. License CC BY.

## Abstract (as shown on the verified eprint page)

A method for transforming zero-knowledge protocols in the designated-verifier
setting into public-coin protocols, which can be made non-interactive and
publicly verifiable. Applies to a large class of ZK protocols based on
oblivious transfer, in particular fast protocols based on vector oblivious
linear evaluation (VOLE), via the authors' "VOLE-in-the-head" technique.
Claims: linear proof size; simpler, smaller and faster than MPC-in-the-head
approaches; new proof of security for SoftSpokenOT (Crypto 2022) generalized
to produce VOLE correlations over large fields; a ZK protocol with only 2x
more communication than the best designated-verifier VOLE-based protocols;
soundness of the Fiat-Shamir non-interactive version analyzed via
round-by-round soundness. Application: **FAEST**, a post-quantum signature
scheme based on AES — the first AES-based signature scheme smaller than
SPHINCS+, with signature sizes between 5.6 and 6.6 kB at the 128-bit security
level (per the abstract; sign 8x-40x faster than smallest SPHINCS+, slower
verification).

## Verification performed

- `https://eprint.iacr.org/2023/996` — fetched 200. Full metadata and
  abstract read from the primary eprint page: title, all seven authors with
  affiliations, abstract, category (Cryptographic protocols), keywords,
  CRYPTO 2023 publication info, history dates, and BibTeX.
- This entry is abstract-level: the full PDF text (`/2023/996.pdf`, linked
  from the landing page) was not fetched or read in this session.

## Relevance to this program

Primary-source anchor for the FAEST/VOLEitH mechanism that RQ-FAEST-001
targets. The RQ's attack objects (VOLEitH consistency-check soundness error,
grinding parameter tradeoff, QROM extractor loss) all trace back to this
paper's construction and its Fiat-Shamir round-by-round soundness analysis.
The tighter-QROM follow-up line mentioned in RQ-FAEST-001 motivation is
**not** this paper; that is separate 2026 work to be filed separately.

## Limits

- `citation_verified: true` covers the bibliographic identity (title,
  authors, eprint id, CRYPTO 2023 status, abstract) as served by the
  primary eprint page on 2026-07-31. No claim in this entry asserts more
  than the abstract states; in particular the paper's internal soundness
  bounds have not been re-derived here.
