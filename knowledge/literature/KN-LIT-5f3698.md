---
id: KN-LIT-5f3698
type: literature
title: "Sloppy Alice attacks! Adaptive chosen ciphertext attacks on the McEliece public-key cryptosystem"
authors:
  - "Eric R. Verheul"
  - "Jeroen M. Doumen"
  - "Henk C. A. van Tilborg"
year: 2002
venue: "Information, coding and mathematics"
identifiers:
  eprint: null
  doi: "10.1007/978-1-4757-3585-7_7"
  arxiv: null
  url: null
tags: [cca, kem, provable-security, code-based, adaptive-cca, message-recovery, historical, attack]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**"Sloppy Alice attacks!"** — adaptive chosen-ciphertext attacks on the
McEliece public-key cryptosystem. Exploits a sender ("sloppy Alice") who can be
induced to encrypt related messages, or a decryption oracle whose behaviour
varies with the ciphertext, to recover plaintexts from the raw, unconverted
scheme.

## Key claims (as reported)
- The plain McEliece PKC is insecure under adaptive chosen-ciphertext attack.
- Attacks are practical against the unconverted scheme.

## Relevance to this program
Together with [[KN-LIT-c2c4d0]], this is the pair of results establishing that
**raw McEliece must never be used directly** — the one-wayness is fine, and
one-wayness alone is not a usable security property.

The generalisable point for this program is that a mathematical hardness result
does not transfer to a deployed system without the intervening argument, and the
intervening argument is where the failures actually happened. When an evidence
record here establishes something about a core problem, the decision citing it
must not silently upgrade that to a claim about a system built on it.

## Not verified here
citation verified against the Crossref record (DOI 10.1007/978-1-4757-3585-7_7).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The attack's precise oracle requirements and query counts are NOT recorded here.
No online copy listed.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
