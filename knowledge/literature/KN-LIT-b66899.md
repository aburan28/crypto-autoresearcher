---
id: KN-LIT-b66899
type: literature
title: "Statistical decoding"
authors:
  - "Thomas Debris-Alazard"
  - "Jean-Pierre Tillich"
year: 2017
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: "1701.07416"
  url: "https://arxiv.org/abs/1701.07416"
tags: [code-based, mceliece, structural-attack, key-recovery, statistical-decoding, lpn, dual-attack]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Statistical decoding** in its modern form: rather than searching for an
error-free information set, collect many low-weight parity checks and decide
each error coordinate by a statistical test over their evaluations. An entirely
different attack shape from ISD.

## Key claims (as reported)
- A statistical alternative to ISD for decoding random linear codes.
- Its competitiveness against ISD depends on regime and on the availability of low-weight parity checks.

## Relevance to this program
Held as the **principal alternative attack paradigm** to ISD, and as the origin
of a line that took decades to become competitive — Al Jabri
([[KN-LIT-fb3102]], 2001), Overbeck ([[KN-LIT-70266b]], 2006), Niebuhr
([[KN-LIT-288b99]], 2011), then this, then Statistical Decoding 2.0
([[KN-LIT-6796]]) and Dual Attack 3.0 ([[KN-LIT-38b647]]).

That trajectory is the substantive point. An approach that was **repeatedly
judged inferior for twenty years** became a serious contender once the right
reformulation (reduction to LPN) was found. Under `docs/inventor-protocol.md`
this is the canonical argument against premature closure: "this direction has
been tried and does not work" is a claim about past formulations, not about the
direction.

## Not verified here
citation verified against the arXiv record for 1701.07416.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The complexity of statistical decoding as presented here, and the regime where
it beats ISD, are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
