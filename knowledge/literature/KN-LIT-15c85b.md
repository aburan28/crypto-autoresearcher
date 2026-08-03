---
id: KN-LIT-15c85b
type: literature
title: "A note on the Goppa code distinguishing problem"
authors:
  - "Andreas Wiemers"
year: 2025
venue: null
identifiers:
  eprint: "iacr:2025/1661"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/1661"
tags: [code-based, mceliece, structural-attack, goppa, distinguisher, indistinguishability, unread]
confidence: reported
citation_verified: web
supersedes: KN-LIT-e37d4c
supersedes_reason: >-
  KN-LIT-e37d4c carried the tag `key-recovery`, which nothing this program has
  read supports. DEC-20260803-a5b9b1 D-5. The removal asserts nothing about the
  paper's content, which remains unread.
added: "2026-08-03"
superseded_by: null
---

## Contribution
A note on the **Goppa code distinguishing problem** — the assumption, separate
from syndrome decoding, that a Goppa code's public generator matrix cannot be
told apart from a random one. McEliece's security needs both, and the
distinguishing assumption is the weaker-understood of the two.

## Key claims (as reported)
- A contribution to understanding when Goppa codes can be distinguished from
  random.
- Note-length: a focused observation rather than a full attack.

**Both bullets are relayed from a bibliography line and an ePrint title. The
paper has not been read by anyone in this program.**

## Relevance to this program
The distinguishing problem is where **all the structural attacks in this section
live**, and it is the part of McEliece's security that rests on the least
theory. Held as part of that thread ([[KN-LIT-6b5b72]], [[KN-LIT-819780]],
[[KN-LIT-45b1b2]]).

The transferable observation for this program is architectural: a cryptosystem
built on a hidden-structure trapdoor has **two** assumptions, and the one about
the structure being hidden is usually the softer one. Any ECDLP-side proposal
introducing a structured object should expect its structural assumption, not its
hardness assumption, to be the first thing attacked.

## Why this entry supersedes KN-LIT-e37d4c
`KN-LIT-e37d4c` is retained unchanged under its own ID and marked
`superseded_by: KN-LIT-15c85b`.

The defect (`DEC-20260803-a5b9b1` D-5): the superseded entry carried
`key-recovery` in its `tags`.

**The justification for removal is narrow and is stated narrowly, because the
paper is unread.** This entry does NOT claim the paper is a distinguisher result
and not a key recovery — that would be a claim about a document nobody here has
opened, which is the failure mode `KN-OPEN-3f7a21` and `DEC-20260803-a5b9b1` D-2
record. The claim made is only this: **nothing this program holds supports a
`key-recovery` tag on this entry.** The entry's own body describes a contribution
to the *distinguishing* problem and a note-length observation; the ePrint title
recorded below is *"Distinguishing Goppa codes using higher-order vanishing"*.
An unsupported tag is removed; its negation is not asserted.

If a later task reads `iacr:2025/1661` and finds a key-recovery claim in it, the
correct response is a new superseding entry restoring the tag with the source
sentence attached — not a repair of this one.

## Not verified here
Citation verified against the IACR ePrint record for report 2025/1661 (title and
author list checked) on 2026-08-03.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page
(https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved
2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The note's actual observation is NOT recorded here. **Title drift:** the
bibliography lists this as "A note on the Goppa code distinguishing problem",
but the current IACR ePrint record for report 2025/1661 is titled
*"Distinguishing Goppa codes using higher-order vanishing"*. This entry keeps the
bibliography's title as listed and records the ePrint title here; the two were
reconciled during verification, not assumed equal.

**The full text was NOT read**, for the original entry or for this supersession.
Everything under "Key claims" is relayed, not re-derived, and no complexity
figure, benchmark, or security estimate in this entry has been reproduced by this
program. The `unread` tag is carried in `tags` so this state is greppable.
