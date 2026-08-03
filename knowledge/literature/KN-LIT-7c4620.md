---
id: KN-LIT-7c4620
type: literature
title: "A heuristic subexponential attack on the McEliece cryptosystem"
authors:
  - "Pierre Briaud"
  - "Axel Lemoine"
  - "Hugues Randriambololona"
  - "Jean-Pierre Tillich"
year: 2026
venue: null
identifiers:
  eprint: "iacr:2026/1232"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1232"
tags: [code-based, mceliece, structural-attack, key-recovery, goppa, subexponential, heuristic, algebraic-cryptanalysis]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
A **heuristic subexponential attack on the McEliece cryptosystem** — by some
distance the most consequential item in this sweep. A subexponential key-recovery
attack, if it holds at cryptographic parameters, is an exponent-moving result on
a central hard problem: the category `docs/target-result-profile.md` names as the
target profile for this program's own work.

The word carrying the weight is **heuristic**. As with the exemplar result the
profile is built on, the claim is stated conditionally on assumptions that are
not proven, and the honest reading depends entirely on what those assumptions
are and how well they have been tested.

## Key claims (as reported)
- A subexponential attack on the McEliece cryptosystem.
- **Heuristic** — the paper's own titular qualifier. The complexity claim is therefore conditional on stated assumptions rather than proven.
- Aimed at McEliece as such, following the alternant/Goppa distinguisher line ([[KN-LIT-71d1a0]], [[KN-LIT-4c8135]], [[KN-LIT-7ee1a9]]) rather than the generic-decoding line.

## Relevance to this program
This is the closest published analogue to what this program is trying to do,
transposed to a different hard problem — and it should be read as a model for
**form**, not as a result this corpus can rely on.

The form worth copying: an exponent-moving claim on a central problem, stated
subexponential, with the heuristic character declared in the title rather than
buried. That is exactly the disclosure standard AGENTS.md rule 4 and
`docs/target-result-profile.md` impose here.

What this entry deliberately does **not** do is characterise the attack's
practical impact on Classic McEliece parameters. Nothing in this sweep
establishes that, the paper was not read, and a 2026 preprint on a
thirty-year-old target warrants the same scepticism this program applies to its
own strongest claims until independent analysis accumulates. Treat as a
high-priority read, not as an established fact.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2026/1232 (title and author list checked) on 2026-08-03.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

**Nothing about this attack's validity, scope, complexity exponent, heuristic
assumptions, or applicability to Classic McEliece parameters is verified here.**
Only the citation is verified. This entry deliberately relays the title-level
claim and no more; any use of it in a novelty or prioritisation judgment must
read the paper first.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
