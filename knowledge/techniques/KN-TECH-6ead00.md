---
id: KN-TECH-6ead00
type: technique
title: >-
  ECDLP trapdoor systems -- taxonomy of the known constructions and the hiding criterion (what a secret can and cannot conceal)
tags: [trapdoor, backdoor, taxonomy, isogeny, hidden-snfs, seed-manipulation, dual-ec, kleptography, twist, cheon, precomputation, ring-curve, prime-field, ecdlp, survey]
confidence: reported
complexity: >-
  n/a (taxonomy); per-construction costs are in the cited entries
applicability: >-
  any review of a curve, parameter set, or protocol for planted weakness; the entry point for GOAL-ECTD-001 ideation and for red-team challenge of "verifiably random" parameters
source_refs: [KN-TECH-8ef4c3, KN-TECH-fcd4a7, KN-TECH-031027, KN-TECH-a7e9a8, KN-TECH-906e14, KN-TECH-90e273, KN-TECH-febb4f, KN-TECH-778752, KN-TECH-257dbc, KN-TECH-4409e1, KN-TECH-c3a5e4, KN-OPEN-cc1988, KN-OPEN-cbbd97, KN-OPEN-9b71bb, KN-OPEN-b9907c, KN-LIT-7261, KN-LIT-4290, KN-LIT-7635, KN-LIT-3476, KN-LIT-7633, KN-LIT-7634, GOAL-ECTD-001, RQ-ECTD-001]
added: 2026-09-30
superseded_by: null
---

## Definition used throughout

An **ECDLP trapdoor system** is a parameter-generation procedure
`Gen -> (public parameters, secret tau)` such that the discrete logarithm on
the public parameters is easy for the holder of `tau` and, to the best of
public knowledge, generic-hard (`~0.886*sqrt(n)`, KN-TECH-006) for everyone
else. Two weaker classes are included because deployed "ECC backdoors" have
almost all been of these kinds: a trapdoor on a *protocol* built over a sound
curve (KN-TECH-a7e9a8, KN-TECH-c3a5e4, KN-TECH-257dbc) and a *visible but
unchecked* weakness that a standardizer can plant in the expectation that
implementations will not test for it (KN-TECH-90e273, KN-TECH-febb4f,
KN-TECH-4409e1).

## The hiding criterion

A weakness can be hidden behind a secret only if it is **not a public
invariant** of what is published. For a curve `E/F_q` with base point of
prime order `n`, the following are computable in polynomial time by anyone:
`#E(F_q)` and hence `n` (SEA), the embedding degree `k = ord_n(q)`, anomaly
(`n = q`), smoothness of `n` and of `n +- 1` (with factoring effort), the
twist order, the discriminant (singularity), and whether `q` is prime or a
prime power. Every weakness decided by these quantities is *detectable*, not
*hideable*; a "trapdoor" built on one is only an unchecked weakness.

What can be hidden is a property that varies **within** the public
equivalence class:

| Secret map or object | Public image | Weakness hidden | Instance |
| --- | --- | --- | --- |
| isogeny `E_s -> E_pub` | same order, same `k`, same field | GHS Weil-descent vulnerability (not an isogeny invariant) | KN-TECH-8ef4c3 |
| special polynomial form of `p` | an ordinary-looking prime | SNFS-friendly `F_{p^k}` after MOV transfer | KN-TECH-fcd4a7 |
| seed preimage | a "verifiably random" curve | membership in a secret weak class | KN-TECH-031027 |
| factorization of `N` | a curve over `Z/NZ` | group order and the additive kernel of reduction mod `p^2` | KN-TECH-906e14 |
| scalar `d` with `Q = dP` | two standard points | the relation between the points | KN-TECH-a7e9a8, KN-TECH-c3a5e4 |
| stored distinguished-point table | a fixed standard curve | `n^{1/3}` per-instance cost after `n^{2/3}` one-time work | KN-TECH-778752 |
| attacker public key inside the implementation | ordinary-looking keys and nonces | the key itself | KN-TECH-257dbc |

The consequence for prime fields is sharp and is the standing gap of
GOAL-ECTD-001: over `F_p` with `p` prime there is no subfield to descend to,
and every known qualitative ECDLP weakness (anomaly, small `k`, smooth order,
Cheon divisors) is an isogeny-class invariant, so the only published genuine
hidden-weakness construction (Teske's) has no known prime-field analogue.
KN-OPEN-cc1988 states that gap; KN-OPEN-cbbd97 states the one gating
mechanism (endomorphism-ring knowledge across a large-conductor barrier) that
would make a prime-field analogue deployable if an endpoint weakness were ever
found.

## What is ruled out, and why it stays on the list

Entries that were once proposed as trapdoors and are now understood to be
unchecked weaknesses or dead ends are recorded here so ideation does not
re-derive them: anomalous, MOV/Frey-Rueck, Pohlig-Hellman and Cheon-type
weaknesses (all public-order invariants); hidden CM discriminant (no known
speedup beyond the `sqrt(#Aut)` automorphism factor); lifting / xedni
approaches (no advantage, see the JKSST analysis cited in KN-TECH-005's
lineage); singular models (nodal -> `F_p^*`, cuspidal -> additive, but
exposed by the discriminant). The composite-order and partially-anomalous
ring variants are kept as *open problems with an expected negative answer*
(KN-OPEN-9b71bb, KN-OPEN-b9907c) because the negative argument is a cost
bound, not a theorem.

## Adjacent, deliberately excluded

Trapdoor DDH groups (KN-LIT-7633, KN-LIT-7634, KN-LIT-5102) hide a pairing or
an isogeny to supply a private *decision* oracle; they do not solve the DLP.
Hidden endomorphism rings of supersingular curves (SQIsign, Seta; KN-TECH-028)
are trapdoors for isogeny problems, and the ECDLP on a supersingular curve is
already easy by MOV, so no ECDLP trapdoor is needed there.

## Use in this program

Rule 4 of AGENTS.md scopes every conclusion; this taxonomy is a checklist for
two roles. The **red team** uses the hiding criterion to ask, of any proposed
parameter set, which secret could have been retained by its generator. The
**idea generator** uses the "public invariant" column to reject, before
compute, any proposal that hides a class invariant behind an isogeny
(the deprioritized list of GOAL-ECTD-001).
