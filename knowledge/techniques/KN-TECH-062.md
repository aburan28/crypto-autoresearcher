---
id: KN-TECH-062
type: technique
title: Code-based signatures - why hash-and-sign is hard and what replaced it
tags: [code-based, signature, cfs, wave, mpc-in-the-head, regular-syndrome-decoding, fiat-shamir, zk-proof, pqc]
confidence: reported
complexity: CFS signing cost superpolynomial in the security parameter; Wave uses generalized (U,U+V) codes at high error rate; MPCitH signature size dominated by the proof, not the key
applicability: assessing any code-based signature proposal; understanding why the code-based signature story diverged from the KEM story
source_refs: [KN-LIT-4258, KN-LIT-7487, KN-LIT-7571, KN-LIT-1137, KN-LIT-6591, KN-LIT-6232, KN-LIT-6578, KN-LIT-5097, KN-LIT-3490, KN-LIT-4337, KN-LIT-7570]
added: 2026-07-27
superseded_by: null
---

## The structural obstacle
Hash-and-sign needs the trapdoor function to be surjective onto the hash's range:
you must be able to invert *any* digest. But a Goppa code corrects only weight-`t`
errors, so only a vanishing fraction of syndromes are decodable. Hashing to a
random syndrome almost never lands on one. This is the reason code-based
signatures lagged code-based KEMs by decades, and it has no analogue on the
lattice side, where trapdoor sampling is comparatively natural (KN-TECH-023).

## The three responses
**Retry until decodable (CFS, KN-LIT-4258).** Hash with a counter and retry until
a decodable syndrome appears. Correct, and produces short signatures, but the
expected retry count forces very high-rate codes, which inflates keys and pushes
the scheme into precisely the high-rate regime where the Goppa distinguisher
lives (KN-LIT-2395, KN-TECH-059). Signing cost is superpolynomial. Not deployed.

**Change the code so everything is decodable (Wave, KN-LIT-7487).** Use
generalized `(U,U+V)` codes and decode at *high* error weight, where solutions are
plentiful and the map is surjective. Short signatures, large keys. The security
argument must additionally hide the `(U,U+V)` structure -- a structural
assumption of the KN-TECH-059 kind -- and it sits in the high-error regime where
Both-May-style decoding is the relevant attack (KN-LIT-7571), not half-distance
ISD.

**Abandon the trapdoor (MPC-in-the-head / Fiat-Shamir).** Prove knowledge of a
low-weight solution to a *random* SD instance and make it non-interactive. No
trapdoor, no structural assumption, no code family to hide -- the assumption is
plain syndrome decoding. The price is signature size: the proof dominates.
Regular syndrome decoding is the common instantiation because it proves more
cheaply (KN-LIT-1137, KN-LIT-6591, KN-LIT-6232). This is where the active work is.

## What this pattern is worth recording
The three responses are three different places to put the same difficulty --
in the signer's cost (CFS), in a structural assumption (Wave), or in the
signature size (MPCitH) -- and the field converged on the option that keeps the
*assumption* cleanest while paying in bandwidth. That ordering of preferences is
itself a datum about how the community prices assumption risk against efficiency,
and it is the opposite of the trade made on the KEM side by BIKE and HQC.

## Adjacent
KN-LIT-6578 and KN-LIT-5097 cover code-based privacy-preserving constructions and
one-out-of-many proofs. The rank-metric branch has its own signature line
(KN-LIT-3490, Durandal) and identity-based encryption (KN-LIT-4337); it is a
distinct metric with a distinct attack literature (KN-LIT-2452, KN-LIT-1894) and
should not be pooled with Hamming-metric results. Code equivalence (KN-LIT-7570)
supports a further signature family via its hull-dimension hardness.

## Applicability limits
Nothing here was implemented or measured. All cost and size characterizations are
`reported` from the cited sources. Whether any of these schemes is currently
under standardization consideration was not established beyond the round-4
outcome in KN-LIT-7575, which concerned KEMs only.
