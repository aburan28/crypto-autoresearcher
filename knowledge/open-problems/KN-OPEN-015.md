---
id: KN-OPEN-015
type: open_problem
title: What does the SIDH break teach - when does publishing auxiliary structure (torsion images) collapse an isogeny/DL assumption, and which schemes are safe?
tags: [sidh-break, auxiliary-information, torsion-points, synthesis, lesson, isogeny, cross-domain, open, adjacent]
confidence: reported
status: open
source_refs: [KN-LIT-065, KN-LIT-067, KN-LIT-077]
added: 2026-07-23
superseded_by: null
---

## Statement
The 2022 SIDH break is a case study in a general phenomenon the program cares
about: publishing AUXILIARY STRUCTURE about a secret map can collapse an
assumption that looked exponentially hard. For SIDH the auxiliary data was the
images of a known torsion basis under the secret isogeny, at KNOWN, UNBALANCED
degrees. The general question: for which isogeny/DL-type assumptions does revealed
auxiliary information (torsion images, degrees, orientations, endomorphisms) admit
a polynomial or subexponential attack, and which do not?

## Current state (as reported) - the arc, summarized
- 2016 GPST (KN-LIT-076): adaptive torsion misuse breaks STATIC SIDH keys ->
  need FO/ephemeral keys.
- 2017 Petit (KN-LIT-077): revealed torsion images make UNBALANCED isogeny
  problems easier than the general case -- the conceptual seed.
- 2022 Castryck-Decru / Maino-Martindale / Robert (KN-LIT-065, -066, -067):
  torsion images + Kani reducibility (KN-TECH-026) give heuristic-poly ->
  subexponential-arbitrary-curve -> PROVABLE-POLY-TIME key recovery in increasing
  embedding dimension.
- SURVIVORS: CGL (KN-TECH-024), CSIDH (KN-TECH-027), SQIsign (KN-TECH-028) reveal
  NO torsion images and are untouched.
The dividing line -- "publishes images of points under the secret isogeny at known
degree" -- is now understood for the specific attack, but a general
characterization of which auxiliary data is fatal is not settled.

## Why it matters here
This is the single most program-relevant lesson of the isogeny literature: it is a
clean, proven instance of the theme running through the program's ECDLP questions
(KN-OPEN-005, KN-OPEN-011, KN-OPEN-012) -- auxiliary/algebraic structure changing
the complexity driver. It gives the program a concrete, worked template
(auxiliary-image -> higher-dimensional embedding -> reducibility -> recovery) and a
cautionary principle for evaluating any assumption, including the program's own
transfer/cover directions (RQ-ISO-001). Adjacent to the ECDLP mission; recorded as
a synthesis, not a program result.
