---
id: KN-TECH-061
type: technique
title: Concrete security estimation and parameter selection for code-based schemes
tags: [code-based, parameter-selection, estimator, cost-model, memory, doom, quasi-cyclic, calibration, security-estimate, isd]
confidence: reported
complexity: estimator-driven; concrete bit-security figures depend on which ISD variant, which memory charge, and which multi-target discount are assumed
applicability: any claim of the form "this code-based parameter set has X bits of security"
source_refs: [KN-LIT-6923, KN-LIT-6503, KN-LIT-2607, KN-LIT-4817, KN-LIT-4875, KN-LIT-1302, KN-LIT-7568, KN-LIT-7573, KN-LIT-7574]
added: 2026-07-27
superseded_by: null
---

## Why asymptotics do not set parameters
The exponent ranking of KN-TECH-057 is a statement about `n -> infinity` at the
worst rate. Deployed schemes sit at fixed `n`, fixed rate, and a specific error
regime, where polynomial factors and the `o(1)` dominate and the asymptotic
ranking can invert. Parameters are therefore set by concrete estimators.

**The tool of record is the Syndrome Decoding Estimator** (KN-LIT-6923), which
evaluates the ISD family at given parameters under a stated cost model. It plays
the same role for code-based schemes that the lattice estimator plays in
KN-TECH-023, and the same caveat applies: an estimator output is a *cost model
evaluation*, not a fact, and two defensible models can differ by tens of bits.

Foundational parameter-selection guidance is KN-LIT-6503 (Finiasz-Sendrier);
KN-LIT-2607 (Bernstein-Lange-Peters) is the reference concrete attack-and-defend
analysis for McEliece.

## The three knobs that move the answer
1. **Which ISD variant.** BJMM-class algorithms have better exponents but worse
   memory and larger polynomial overheads; at deployed parameters simpler
   variants can win. Report which was assumed.
2. **How memory is charged.** Free memory versus a realistic access cost can swing
   an estimate substantially, and always in the direction of *more* security when
   memory is charged. This program's standing rule (KN-TECH-035, KN-TECH-044)
   applies unchanged: a bit-security number with an uncharged memory term is not
   comparable to one with a charged term. KN-LIT-4817 is the reference for lower
   bounds spanning both sieving and ISD.
3. **Multi-target and structural discounts.** Decoding One Out of Many (DOOM)
   lets an attacker attack many instances at once for less than the sum;
   quasi-cyclic structure supplies such instances for free by rotation, giving a
   discount on the order of the square root of the block size. Quasi-cyclic
   parameter sets must include it (KN-LIT-7574); see KN-OPEN-020 for whether
   that is the *whole* effect of quasi-cyclicity.

## Calibration against records
Concrete claims are checkable against solved instances: KN-LIT-4875 reports
solving McEliece-1284 and quasi-cyclic-2918 with modern ISD, and KN-LIT-1302
reports solving McEliece-1409 in one day. These serve the code-based branch
exactly as public ECDLP records serve KN-TECH-036 and lattice challenges serve
KN-TECH-049: they convert an estimator from an unfalsifiable model into one with
at least a few anchored points. **Any estimator that misprices a solved record is
wrong at that point**, and that check is cheap.

Note the gap these records reveal: the largest solved McEliece instance is at
`n ~ 1409`, while mceliece348864 -- the *smallest* deployed set -- has
`n = 3488`. As with ECDLP (KN-TECH-036), no deployed parameter set is within
reach of validation, so all security statements are extrapolations from a
calibrated model. Say so when making them.

## Applicability limits
No estimator was run in this program and no parameter set was independently
evaluated. Every figure referenced here lives in its cited source. The `sqrt`
DOOM discount shape is relayed and was not derived here.
