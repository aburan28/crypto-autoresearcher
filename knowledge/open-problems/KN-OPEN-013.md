---
id: KN-OPEN-013
type: open_problem
title: How hard is the supersingular endomorphism-ring / isogeny-path problem, and is it a sound post-quantum foundation after the SIDH break?
tags: [endomorphism-ring, isogeny-path, supersingular, hardness-foundation, sqisign, cgl, post-quantum, open, adjacent]
confidence: reported
status: open
source_refs: [KN-LIT-074, KN-LIT-076, KN-LIT-078]
added: 2026-07-23
superseded_by: null
---

## Statement
After the 2022 SIDH break, the surviving supersingular schemes (CGL hash,
SQIsign) rest on the hardness of computing the ENDOMORPHISM RING of a supersingular
curve -- equivalently (under GRH, KN-LIT-074) finding an isogeny path between two
curves. How hard is this problem really? Best known is Otilde(p^{1/4}) classical
and quantum for pure path-finding (KN-LIT-078, KN-LIT-079). Is that the true
complexity, or does extra structure (orientation, small-degree endomorphisms,
special curves) admit faster attacks -- and is the problem a sound long-term
post-quantum foundation?

## Current state (as reported)
The endomorphism-ring problem and isogeny path-finding are equivalent under GRH
(KN-LIT-074), unifying the hardness question. No sub-p^{1/4} generic attack is
known, classical or quantum. But the field is moving fast: the SIDH break
(KN-LIT-065..067) showed that AUXILIARY structure can be catastrophic, and
oriented / CM-endowed curves are known to be weaker in some regimes. This is an
ADJACENT (post-quantum) hardness question, not the program's ECDLP mission.

## Why it matters here
It is the closest isogeny analogue of the program's core ECDLP hardness question
(KN-OPEN-001), and it is directly answerable with the program's own methodology:
"does exploitable algebraic structure (here, the endomorphism ring / orientation /
Deuring image) lower the complexity driver?" The program's CM / volcano /
orientation expertise (RQ-ISO-001, ISO-AR) is exactly the toolkit for probing it.
Recorded to mark the surviving foundation and a legitimate cross-domain direction;
no program result is claimed.
