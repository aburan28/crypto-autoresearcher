---
id: KN-LIT-84f404
type: literature
title: "Scalable Small ECDLP Solver via Windowed-Batch Inversion for Additively Homomorphic Encryption"
authors:
  - "Murat Cenk"
  - "Muhammad ElSheikh"
  - "Irem Keskinkurt Paksoy"
  - "M. Anwar Hasan"
year: 2026
venue: "IACR ePrint 2026/2102"
identifiers:
  eprint: "iacr:2026/2102"
  arxiv: null
  doi: null
  url: null
tags: [pollard-rho, small-dlp, batch-inversion, homomorphic-encryption, secp256k1, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Removes FastECDLP's giant-step table by advancing the giant step in Jacobian coordinates and using windowed batch inversion. This makes 64-bit bounded-plaintext ECDLP recovery practical on a workstation for secp256k1-based EC-ElGamal/Twisted ElGamal (Zether, Solana confidential transfers, XRPL XLS-96).

## Key claims (as reported)

- FastECDLP giant-step table on secp256k1: 5.91 GB at 58 bits, 378 GB at 64 bits, which this work eliminates.

## Relevance to this program

Windowed batch inversion removes FastECDLP's giant-step table for 64-bit bounded ECDLP (2026). Recent evidence that batch-inversion scheduling is still active engineering territory.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
