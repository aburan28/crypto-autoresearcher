---
id: KN-LIT-c2c4d0
type: literature
title: "Reaction attacks against several public-key cryptosystems"
authors:
  - "Chris Hall"
  - "Ian Goldberg"
  - "Bruce Schneier"
year: 1999
venue: "ICICS"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://cypherpunks.ca/~iang/pubs/paper-reaction-attacks.pdf"
tags: [cca, kem, provable-security, code-based, reaction-attack, decoding-failure, foundational, attack]
confidence: reported
citation_verified: false
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Reaction attacks**: the attacker learns from the *reaction* of the recipient —
whether decryption succeeded or failed — rather than from any output. Applied to
several public-key cryptosystems including McEliece and to the Ajtai–Dwork and
NTRU-style lattice schemes.

## Key claims (as reported)
- Observing only decryption success/failure leaks enough to mount an attack.
- Applies across several cryptosystem families, not one scheme.

## Relevance to this program
The conceptual ancestor of the entire side-channel section that follows, and one
of the most quietly important papers in this bibliography. It established that
**the failure/success bit is itself a channel** — a single bit per query,
adaptively chosen, is a working attack.

Two consequences this program should hold onto. Information-theoretically tiny
leakage is not cryptographically negligible leakage; the relevant question is
what the attacker can *do* with a bit, not how many bits there are. And the
decoding failure rate, treated as a correctness parameter, is a security
parameter — the line of reasoning that governs BIKE's design today.

## Not verified here
**Citation NOT independently verified.** The paper was not found in IACR ePrint, arXiv or Crossref during this sweep, so the reference rests on the Classic McEliece bibliography alone and `citation_verified` is `false`.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

**Citation NOT independently verified** — not found in ePrint or Crossref during
this sweep; the cypherpunks.ca URL is transcribed from the bibliography and was
not resolved. The attacks' specifics against each named cryptosystem are NOT
recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
