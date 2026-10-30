---
id: KN-LIT-10b0fa
type: literature
title: "PKM prime-field factor bases: primary-source construction review"
authors: [Christophe Petit, Michiel Kosters, Ange Messeng]
year: 2016
venue: "PKC 2016, sections 3.1–3.4"
identifiers:
  doi: 10.1007/978-3-662-49387-8_1
  url: https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf
tags: [prime-field, factor-base, pkm, isogeny, kummer]
confidence: reported
citation_verified: read
provenance: retrieved
verified_by: "Codex /root, 2026-10-30; constructions and limitations"
added: "2026-10-30"
superseded_by: null
---

The primary PDF was retrieved and its factor-base constructions reviewed.
This supersedes the abstract-only construction account in KN-LIT-025; it does
not independently verify the complete complexity analysis.

The paper uses an abscissa set described by a composition of low-degree maps.
Its concrete cases are cosets of smooth-order subgroups of Fp* and fibres of
isogenies on an auxiliary curve over the same field. Existence of a base,
construction cost and solving the resulting Semaev system remain separate.
The authors explicitly leave asymptotic efficiency dependent on understanding
the structured polynomial systems.

The native factory integration in `crypto:tools/factor-base/` adds bounded
arbitrary-order multiplicative cosets, norm-one torus traces and Dickson images
alongside progression/random-x controls. The latter constructions also refer
to the existing internal `crypto:research/pkm_dickson_torus_20261015/` study;
they are implementation alternatives, not new claims attributed to PKM.
Existing Kummer/isogeny plug-ins and their solver obligations are preserved.
No source or internal result is promoted to a new performance conclusion.
