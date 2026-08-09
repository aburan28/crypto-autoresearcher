---
id: KN-LIT-d82a53
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
tags: [code-based, mceliece, structural-attack, goppa, distinguisher, indistinguishability, claim-class-corrected]
supersedes: [KN-LIT-e37d4c]
confidence: reported
citation_verified: web
citation_verified_note: >-
  Inherited, not re-earned. KN-LIT-e37d4c records a 2026-08-03 verification of
  this bibliographic line against the IACR ePrint record for report 2025/1661.
  No DOI was recorded and none is invented here. TASK-20260808-f9374d performed
  NO retrieval of any kind and read no full text; it re-tagged. Not raised to
  `read`: nobody in this program has read this paper.
added: "2026-08-08"
superseded_by: null
---

## Why this entry exists

**It supersedes `KN-LIT-e37d4c` on one point only: the claim-class tags.**

`KN-LIT-e37d4c` carries both `distinguisher` and `key-recovery`, which makes
`RQ-MCE-e65b3c`'s standing constraint *"Distinguisher is not break"*
unauditable except by human reading. This entry drops `key-recovery` and keeps
`distinguisher`, per `knowledge/TAG-CLAIM-CLASS.md` rule R-CC-1.

`KN-LIT-e37d4c` is **not edited**; it is retired by being named in this entry's
`supersedes:` field (rule R-CC-6). Nothing else about the entry changed — in
particular the title-drift observation below is carried forward exactly as
recorded, not resolved.

## Claim class

`distinguisher`. The subject concerns the Goppa code *distinguishing* problem:
when a Goppa code's public matrix can be told apart from a random one. No key
recovery is claimed on this program's record.

**On what basis.** Two titles and `KN-LIT-e37d4c`'s recorded description. Both
titles — the bibliography's *"A note on the Goppa code distinguishing problem"*
and the ePrint record's *"Distinguishing Goppa codes using higher-order
vanishing"* — name distinguishing and neither names recovery. **This program has
not read the note.**

**Falsification condition.** If a read shows a recovery result, the correct
token is `distinguish-then-recover` (rule R-CC-2) and this entry must be
superseded under a new id.

## Contribution

A note on the **Goppa code distinguishing problem** — the assumption, separate
from syndrome decoding, that a Goppa code's public generator matrix cannot be
told apart from a random one. McEliece's security needs both, and the
distinguishing assumption is the weaker-understood of the two.

## Key claims (as reported)

- A contribution to understanding when Goppa codes can be distinguished from
  random.
- Note-length: a focused observation rather than a full attack.

## Relevance to this program

The distinguishing problem is where **all the structural attacks in this thread
live**, and it is the part of McEliece's security that rests on the least
theory. Held as part of that thread ([[KN-LIT-3c9f21]], [[KN-LIT-a4d70e]],
[[KN-LIT-6b1fc8]] — which supersede [[KN-LIT-13a01d]], [[KN-LIT-71d1a0]] and
[[KN-LIT-7ee1a9]] respectively).

That thread is also exactly the two-assumption structure `RQ-MCE-e65b3c` records
for Classic McEliece: syndrome decoding is one assumption, indistinguishability
of the scrambled Goppa matrix is the other, and *"every break in the McEliece
family has come through"* the second.

The transferable observation for this program is architectural: a cryptosystem
built on a hidden-structure trapdoor has **two** assumptions, and the one about
the structure being hidden is usually the softer one. Any ECDLP-side proposal
introducing a structured object should expect its structural assumption, not its
hardness assumption, to be the first thing attacked.

## Not verified here

The full text was **not read** for this entry, and was not read for
`KN-LIT-e37d4c` either. Everything under "Key claims" is relayed at one further
remove. The note's actual observation is NOT recorded here, and no condition,
bound or estimate in it has been reproduced by this program.

**Title drift, carried forward unresolved.** The bibliography lists this as *"A
note on the Goppa code distinguishing problem"*; `KN-LIT-e37d4c` records that
the current IACR ePrint record for report 2025/1661 is titled *"Distinguishing
Goppa codes using higher-order vanishing"*. That entry kept the bibliography's
title and recorded the ePrint title in its body, stating the two *"were
reconciled during verification, not assumed equal"*. This entry keeps that
arrangement unchanged and adds nothing to it: **no retrieval was performed here
and this task cannot say which title the document itself prints.**

Bibliographic line originally transcribed from the Classic McEliece project's
"Papers" page (https://classic.mceliece.org/papers.html, page version
2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md`.
