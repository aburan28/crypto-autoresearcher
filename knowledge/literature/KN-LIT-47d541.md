---
id: KN-LIT-47d541
type: literature
title: "Elliptic Curves over Goldilocks (EcMasFp5 design note, read at source)"
authors: [HackMD page @Wimet; implementation cross-link to Polygon Hermez pil2-proofman]
year: 2025
venue: HackMD design note (not peer-reviewed)
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: https://hackmd.io/@Wimet/S1R3RAY5yx
  source_package: inputs/ECMASFP5-HACKMD-2025
tags: [ecmasfp5, ecgfp5, goldilocks, quintic-extension, elliptic-curve,
  twist-security, design-note, unrefereed, retrieved]
confidence: reported
citation_verified: read
provenance: retrieved
frozen_source: inputs/ECMASFP5-HACKMD-2025/
source_record: SRC-ECMASFP5-HACKMD-2025
verified_by: cloud-agent session on branch cursor/gfpn-ideas-intake-dcc3, 2026-09-20; frozen bytes and hashes in inputs/ECMASFP5-HACKMD-2025/provenance.json
added: 2026-09-20
superseded_by: null
---

## Why this record exists

GFPN intake cites EcMasFp5's equation and its self-reported twist security
(101.93 bits) and inherited ~142-bit field claim. An unrefereed design note
is still a source that must be frozen before those figures are quoted.

## What was read

Decoded markdown from the frozen HackMD HTML. Curve
`E / F_{p^5} : y^2 = x^3 + 3x + 8z^4` over `F_p[z]/(z^5 - 3)` with the same
Goldilocks `p`. Line: "Twist security (Pollard-Rho): 101.93 bits". Claims
inheritance of EcGFp5 field security at approximately 142 bits.

## What this record does not assert

The 101.93-bit twist figure is a **self-report**. It is a comparison target for
`IDEA-20260920-63a902`, not a verified SafeCurves certificate. No PDP or
OA-SDH analysis appears in the note.
