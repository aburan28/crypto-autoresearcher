---
id: KN-LIT-6e1eb5
type: literature
title: "A side-channel attack against Classic McEliece when loading the Goppa polynomial"
authors:
  - "Boly Seck"
  - "Pierre-Louis Cayrel"
  - "Vlad-Florin Dragoi"
  - "Idy Diop"
  - "Morgan Barbier"
  - "Jean Belo Klamti"
  - "Vincent Grosso"
  - "Brice Colombier"
year: 2023
venue: "Africacrypt"
identifiers:
  eprint: null
  doi: "10.1007/978-3-031-37679-5_5"
  arxiv: null
  url: "https://web.archive.org/web/20230924072632/https://bcolombier.fr/assets/publis_PDF/2023/Seck_AFRICACRYPT_2023.pdf"
tags: [side-channel, code-based, classic-mceliece, implementation-attack, goppa-polynomial, key-loading, power-analysis]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
A side-channel attack mounted **when the Goppa polynomial is loaded** from
storage into working memory. The attack targets neither key generation nor
decoding, but the data movement between them.

## Key claims (as reported)
- Loading the secret Goppa polynomial leaks enough to attack the key.
- The vulnerable operation is data transfer, not computation.

## Relevance to this program
The most instructive entry in the side-channel cluster for a reason unrelated to
codes: **the attack surface was not in the algorithm.** A constant-time,
carefully audited implementation of every arithmetic step can still lose the key
in the memcpy that precedes it.

Any threat model this program writes should therefore state where its boundary
is drawn, and note explicitly what falls outside — the same honesty about test
boundaries that rule 9 requires of a deprioritisation.

**Does not bear on the ECDLP.**

## Not verified here
citation verified against the Crossref record (DOI 10.1007/978-3-031-37679-5_5).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Target platform, leakage model, and success rate are NOT recorded here. The
archived PDF was not fetched.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
