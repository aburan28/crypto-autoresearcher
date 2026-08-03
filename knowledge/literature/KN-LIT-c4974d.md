---
id: KN-LIT-c4974d
type: literature
title: "Analysis of backdoored (Classic) McEliece in a multi-user setting"
authors:
  - "Dai Miura"
  - "Hyungrok Jo"
  - "Shingo Sato"
  - "Junji Shikata"
year: 2024
venue: "MobiSec"
identifiers:
  eprint: null
  doi: "10.1007/978-981-95-0172-4_1"
  arxiv: null
  url: "https://link.springer.com/chapter/10.1007/978-981-95-0172-4_1"
tags: [side-channel, code-based, classic-mceliece, implementation-attack, backdoor, multi-user, key-generation, subversion]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Analyses **backdoored (Classic) McEliece in a multi-user setting** — extending
the backdoor question of [[KN-LIT-b9d3e0]] to the case of many users sharing a
subverted key generator.

## Key claims (as reported)
- Backdoored Classic McEliece key generation is analysed across multiple users.
- Multi-user framing: the question is what a subverted generator yields at population scale.

## Relevance to this program
Held with [[KN-LIT-b9d3e0]] as the subversion pair. The threat model is
different in kind from everything else in this sweep — the adversary is the
implementer, not an outsider — and the defensive question becomes whether a key
can be **audited** rather than whether an attack is expensive.

For this program the relevant analogue is verifiability of its own artifacts:
the reason run records are immutable, certificates are re-verified independently
by the run wrapper, and the dispatcher's post-commit verifier must accept a
declared path set is that **the producer of a result cannot be the only party
able to check it.**

**Does not bear on the ECDLP.**

## Not verified here
citation verified against the Crossref record (DOI 10.1007/978-981-95-0172-4_1).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The backdoor construction analysed and the multi-user consequences are NOT
recorded here. The Springer chapter was not fetched.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
