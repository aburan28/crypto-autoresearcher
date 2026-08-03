---
id: KN-LIT-45b1b2
type: literature
title: "Understanding the new distinguisher of alternant codes at degree 2"
authors:
  - "Axel Lemoine"
  - "Rocco Mora"
  - "Jean-Pierre Tillich"
year: 2025
venue: "Designs, Codes and Cryptography"
identifiers:
  eprint: "iacr:2025/531"
  doi: "10.1007/s10623-025-01626-8"
  arxiv: null
  url: "https://eprint.iacr.org/2025/531"
source_artifact:            # NOT under `identifiers`; see superseding_entries.md section 5
  kind: abstract_page_only
  url: "https://eprint.iacr.org/2025/531"
  sha256: "88035f1a7a0f59750cbaf89a770295643f0e9a111d72b43bbb6d9ad497bfb299"
  retrieved_by: TASK-20260803-292b99
  committed_locally: false
  note: >-
    ABSTRACT PAGE ONLY. The full text was not obtained; see
    citation_verified_note.
tags: [code-based, mceliece, structural-attack, distinguisher, alternant-codes, goppa, algebraic-cryptanalysis]
confidence: reported
citation_verified: web
citation_verified_note: >-
  Stays `web`, deliberately. The FULL TEXT WAS NOT OBTAINED:
  inria.hal.science/hal-05461754/document and .../hal-04953992/document both
  returned HTTP 200 whose body is a proof-of-work bot interstitial rather than
  a PDF (not circumvented), and the ePrint PDF endpoint is
  Cloudflare-challenged. Only the ePrint ABSTRACT was read
  (TASK-20260803-292b99, HTTP 200, sha256 88035f1a...bfb299). Under
  knowledge/SEEDING.md a `read` flag would assert that this entry's claims
  reflect the paper's real content; they reflect its abstract.
supersedes: KN-LIT-7ee1a9
supersedes_reason: >-
  KN-LIT-7ee1a9 carried the tag `key-recovery` on a paper its own abstract
  describes as a distinguisher. DEC-20260803-a5b9b1 D-5.
added: "2026-08-03"
superseded_by: null
---

## Contribution
Explains the **new distinguisher of alternant codes at degree 2** — an analysis
paper clarifying why a recently discovered distinguisher works, rather than
introducing a new one. **This is a distinguisher result, not a key recovery**;
its abstract frames distinguishing as *"a first step before being able to attack
McEliece"* and places the key recovery elsewhere ([BMT24]). Alternant codes are
the family containing Goppa codes, so a distinguisher there bears on McEliece's
structural assumption; what it bears is not established by this program.

## Key claims (as reported, from the ABSTRACT only)
- An explanation of the mechanism behind the degree-2 alternant distinguisher.
- Understanding-oriented: the contribution is the reason, not the attack.
- VERBATIM: *"Computing $\mathrm{HF}(2)$ still gives a polynomial time
  distinguisher for alternant or Goppa codes and is apparently able to
  distinguish Goppa or alternant codes in a **much broader regime of rates** as
  the one of [FGO+11]."* **The abstract's own hedge — "apparently" — is
  preserved and must not be dropped.**
- On the reach of the earlier distinguisher, VERBATIM: *"Whereas the
  distinguisher of [FGO+11] is only able to distinguish Goppa codes or alternant
  codes of **rate very close to 1**, in [CMT23a] a much more powerful (and more
  general) distinguisher was proposed."*
- VERBATIM: *"The value of $\mathrm{HF}(2)$ corresponding to random linear codes
  is known and this yields **a precise description of the new regime of rates**
  that can be distinguished by this new method."*

## THE RATE REGIME IS ANNOUNCED IN THE ABSTRACT AND LIVES IN THE BODY, WHICH WAS NOT OBTAINED
The abstract says a precise description of the new rate regime exists. **This
program does not hold it.** The regime for this paper is **NOT TRANSCRIBED**, and
the fact that it exists is not a substitute for having it. Any deliverable of
this program that needs this paper's rate regime must obtain the body first.

## Relevance to this program
Held for the genre as much as the content. Papers whose contribution is
**understanding why an existing attack works** are how a field converts a
surprising result into a predictive theory — and predictive theory is what tells
you which *other* parameters are affected.

This program has the same obligation in its own lifecycle: `/review-evidence`
requires the mechanism to be stated, not only the outcome, because an
unexplained empirical win cannot be scoped and therefore cannot be safely
generalised.

Held together with [[KN-LIT-6b5b72]], [[KN-LIT-819780]] and [[KN-LIT-c4c2ac]] as
the modern distinguisher cluster.

**Does not bear on the ECDLP.**

## Why this entry supersedes KN-LIT-7ee1a9
`KN-LIT-7ee1a9` is retained unchanged under its own ID and marked
`superseded_by: KN-LIT-45b1b2`.

The defect (`DEC-20260803-a5b9b1` D-5): the superseded entry carried
`key-recovery` in its `tags`. The paper's own abstract calls the object a
distinguisher and places the key recovery in another work. `RQ-MCE-e65b3c`
constrains *"Distinguisher is not break … Any deliverable naming a distinguisher
states which it is"*, and `docs/claims-and-verification.md` forbids promoting one
to the other — a `key-recovery` tag is that promotion at the grep level. The tag
is withdrawn.

Two additions carry over from `TASK-20260803-292b99`, which read the abstract:
the paper's own rate-regime sentences (quoted above, with the "apparently"
hedge), and the explicit statement that the precise regime was **not obtained**.

## Not verified here
Citation verified against the IACR ePrint record for report 2025/531 (title and
author list checked) on 2026-08-03; citation verified against the Crossref
record (DOI 10.1007/s10623-025-01626-8).

**The full text was NOT read.** Only the ePrint abstract was obtained, at the
sha256 in `source_artifact`. Everything under "Key claims" is relayed from that
abstract, not re-derived, and no complexity figure, benchmark, or security
estimate in this entry has been reproduced by this program. The mechanism
explained, and its consequences for Goppa codes at Classic McEliece parameters,
are NOT recorded here.

**This entry asserts nothing about Classic McEliece's security in either
direction.**

Bibliographic line transcribed from the Classic McEliece project's "Papers" page
(https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved
2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.
Retrieval record:
`coordination/goals/GOAL-MCE-001/batches/BATCH-001/tasks/TASK-20260803-292b99/source_access_log.yaml`.
