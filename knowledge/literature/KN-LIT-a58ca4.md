---
id: KN-LIT-a58ca4
type: literature
title: "How to lose some weight - a practical template syndrome decoding attack"
authors:
  - "Sebastian Bitzer"
  - "Jeroen Delvaux"
  - "Elena Kirshanova"
  - "Sebastian Maaßen"
  - "Alexander May"
  - "Antonia Wachter-Zeh"
year: 2025
venue: "Designs, Codes and Cryptography"
identifiers:
  eprint: "iacr:2024/621"
  doi: "10.1007/s10623-025-01603-1"
  arxiv: null
  url: "https://eprint.iacr.org/2024/621"
tags: [side-channel, code-based, classic-mceliece, implementation-attack, template-attack, syndrome-decoding, practical, isd]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**"How to lose some weight"** — a practical template attack on syndrome
decoding. The title puns on error weight: leakage reduces the effective weight
of the decoding problem the attacker faces, converting a hard instance into an
easy one.

## Key claims (as reported)
- A practical template attack against syndrome decoding.
- Leakage reduces the effective difficulty of the decoding instance.

## Relevance to this program
The cleanest statement of the mechanism running through this whole section:
side-channel information does not usually *replace* cryptanalysis — it **moves
the instance into a range where standard cryptanalysis works.** The attacker's
tool remains ISD; leakage just makes the instance small enough.

That composition — measurement plus existing algorithm — is worth internalising
as a general attack shape, and it is why [[KN-LIT-8285cb]] (ISD with hints)
matters as much as any of the measurement papers.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2024/621 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/s10623-025-01603-1).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The weight reduction achieved and the resulting decoding cost are NOT recorded
here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
