---
id: KN-TECH-034
type: technique
title: Curve and point validation - invalid-curve, small-subgroup, twist, and cofactor checks
tags: [point-validation, invalid-curve, small-subgroup, twist-security, cofactor, parameter-validation, instance-validity, fault-attack, leakage-model, harness, ecdlp-adjacent, hygiene]
confidence: established
complexity: negligible -- one curve-equation evaluation per point, one order factorization per curve, both dominated by any real computation
applicability: mandatory precondition for every generated or received curve/point in this program's harness; the attacks it blocks live in the chosen-input / fault model, not in the plain ECDLP model
source_refs: [KN-LIT-091, KN-LIT-092, KN-LIT-093, KN-LIT-082, KN-LIT-089]
added: 2026-07-24
superseded_by: null
---

## The checks
Four distinct preconditions, each with a matching attack in the literature:

| Check | Failure mode | Source |
| --- | --- | --- |
| Point satisfies the curve equation of E | invalid-curve attack: computation silently proceeds on a smooth-order curve E' and leaks the scalar mod its small factors | KN-LIT-092 |
| Point lies in the intended prime-order subgroup | small-subgroup confinement: attacker-supplied low-order element reveals the secret modulo that order, CRT-recombined | KN-LIT-091 |
| Quadratic twist is also strong (or x-only inputs rejected) | twist attack: x-coordinate-only arithmetic accepts twist points, so work happens in the twist group | KN-LIT-093 |
| Cofactor h known and prime subgroup order recorded | cost mis-charge and Pohlig-Hellman leakage | KN-LIT-082, KN-TECH-030 |

The invalid-curve case has a subtlety worth stating: Biehl, Meyer and Müller
give a variant that defeats input validation alone, by injecting the fault
*after* the check, so the output must also be verified to lie on E. Validation
is a two-sided obligation.

## Two roles here, kept separate
**Scope boundary.** These attacks require an oracle, chosen inputs, a static
reused secret, or fault injection. The program's target is the plain ECDLP:
given E, P, Q, find k, with no interaction. A proposal whose advantage needs
any of the above is operating in the adjacent leakage model and is not a
mathematical advance on the ECDLP -- the same line KN-OPEN-011 draws for the
Hidden Number Problem. Classifying such a proposal correctly is a novelty-screen
decision, not a merit judgement.

**Instrument integrity.** The same failure modes are live bugs in the
program's own harness. Curve generation, point encoding, and x-only or
Montgomery-ladder arithmetic can all put a computation on the twist or on a
neighbour curve without any adversary present. A "solve" obtained that way is
a solve of a different, easier instance. This is exactly what the certificate
re-verification in `docs/claims-and-verification.md` exists to catch: an
independent recompute that checks the recovered k against the *declared* curve
and point will fail loudly, whereas a prose `validity_reason` will not.
Curve25519's design (KN-LIT-093) is the constructive answer -- pick parameters
where the checks cannot fail -- and is why cofactor 8 / twist cofactor 4 is
worth recording for any curve the program adopts.

## Applicability limits
These checks establish instance validity; they say nothing about instance
*hardness*. A curve can pass all four and still be weak for reasons in
KN-TECH-032 (small embedding degree) or KN-TECH-033 (trace one), which are
separate tests. Conversely, failing a check does not make the underlying
mathematics wrong -- it makes the measurement inadmissible, which under
AGENTS.md rule 5 is an infrastructure failure rather than negative
mathematical evidence.

## Verified vs reported
The four attacks are established results, but the underlying papers were
read at abstract / partial level only (see each `Not verified here`), and
Curve25519's security level is the author's stated conjecture, not a proven
bound. The mapping of these attacks onto this program's harness obligations,
and the claim that certificate re-verification catches them, is this program's
own reasoning; it has not been tested by deliberately introducing an invalid
instance and confirming the verifier rejects it. That would be a cheap and
worthwhile validation experiment.
