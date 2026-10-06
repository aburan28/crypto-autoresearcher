---
id: KN-TECH-6a2ef9
type: technique
title: Rigorous weak-curve and isogenous-representative audit protocol
tags: [ecdlp, curve-audit, weak-curve, isogeny, point-counting, subgroup, twist, embedding-degree, endomorphism-ring, attack-cost, sampling, confidence, evidence-boundary]
confidence: reported
claim_status: literature_synthesis
evidence_level: internal_analysis
complexity: Exact algebraic checks plus the cost of the best applicable attack and any declared isogeny search; prevalence sampling requires a separately justified sample size and mixing argument
applicability: Conventional elliptic-curve DLP parameter review over an explicitly defined finite field, including audits of twists, reachable isogenous representatives, and implementations that process adversarial points
source_refs: [KN-TECH-006, KN-TECH-018, KN-TECH-030, KN-TECH-032, KN-TECH-033, KN-TECH-034, KN-TECH-061, KN-TECH-6ead00, KN-TECH-8ef4c3, KN-LIT-171, KN-LIT-ca35e0, KN-FIND-f293c6, KN-OPEN-cc1988, KN-OPEN-cbbd97]
related_open_problems: [KN-OPEN-cc1988, KN-OPEN-cbbd97]
added: '2026-10-06'
superseded_by: null
---

## Purpose and claim boundary

This entry is an operational protocol for answering four different questions
without conflating them:

1. Does a certified invariant make the entire `F_q`-isogeny class weak?
2. Does an explicit representative admit an attack that does not follow from
   those invariants?
3. Can that attack be transferred from the source through a usable isogeny?
4. Does a protocol or implementation accept points for which a different
   attack applies?

It combines established results already recorded in the corpus with an
evidence and sampling discipline. It reports no new curve, attack, security
proof, experiment, or hardness lower bound. `confidence: reported` applies to
the protocol as a synthesis; each audit must grade its own ingredients as
certificate, derivation, measurement, literature report, or unresolved.

## Freeze the audit before testing

An audit starts from an exact field representation, curve equation, subgroup,
generator, total group order, cofactor, protocol use, and isogeny field of
definition. It also freezes the attacker, success probability, security
threshold, common operation unit, memory, data/query budget, parallelism, and
whether preprocessing is reusable. For every isogeny route, state whether the
path is public, supplied as private advice, or must be discovered by the
attacker; those are different threat models.

A named curve or bit length is not an identity. Use the full representation
record in `docs/curve-identities.md`; its hash binds metadata but does not
certify the mathematics. For extension fields, record the characteristic,
degree, defining polynomial or basis, and element encoding. For a named
standard, retain the authoritative parameter source.

The output vocabulary is deliberately narrower than "secure":

- `CLASS_WEAK`
- `WEAK_REPRESENTATIVE_EXISTS`
- `SOURCE_TRANSFER_WEAK`
- `IMPLEMENTATION_WEAK`
- `NO_WEAKNESS_FOUND_WITHIN_SCOPE`
- `INDETERMINATE`
- `INVALID_INSTANCE`

The fifth label enumerates the attacks and search boundary actually checked.
It is not an absence or hardness claim.

## Exact instance checks

Use exact arithmetic and retain commands, versions, raw output, and
certificates. Every check is `PASS`, `FAIL`, `NOT_RUN`, `INDETERMINATE`, or
`NOT_APPLICABLE`; a timeout or unavailable arithmetic package is never a
pass.

1. Prove the field definition is valid and the curve is nonsingular.
2. Check the generator is on the declared curve, `P != O`, and `[r]P = O`.
   With a complete certified factorization of `r`, prove exact order with
   `[r/ell]P != O` for every distinct prime divisor `ell | r`, including the
   sole divisor when `r` is prime. Retain factor and primality certificates;
   an incomplete factorization cannot certify exact order by this test.
3. Compute or independently certify `N = #E(F_q)`. The relation `[N]P = O`
   alone is insufficient. A Hasse-interval unique-multiple proof is valid when
   the field, point order or certified divisor, and interval hypotheses are
   all proved. Record the rational group invariant factors where protocol
   behavior or full-group structure matters.
4. Factor `N` as required by the threat model, recording every unfactored
   cofactor. Charge Pohlig-Hellman against the actual subgroup order as in
   KN-TECH-030.
5. Compute `t = q + 1 - N`, `X^2 - tX + q`, and
   `Delta_pi = t^2 - 4q`; classify ordinary versus supersingular. When
   `q = p` is prime, test the prime-field trace-one anomalous attack of
   KN-TECH-033. Do not extend that citation to `F_(p^m)` without a separately
   verified result.
6. Split composite `r` as required by Pohlig--Hellman. For every relevant
   prime factor `ell | r` with `gcd(q, ell) = 1`, prove the exact embedding
   degree `k_ell = ord_ell(q)`. Showing only `ell | q^k - 1` gives an upper
   bound. When `ell | q`, pairing transfer is `NOT_APPLICABLE` for that factor
   and characteristic-specific attacks must be checked separately. Estimate
   the actual target-field DLP cost for KN-TECH-032 rather than treating
   `k_ell` as the cost.
7. In odd characteristic compute the quadratic-twist order `q + 1 + t`, its
   known factors and invariant factors. Handle the additional twists at
   exceptional `j` separately.
8. Audit point, curve, subgroup, output, and cofactor validation using
   KN-TECH-034 when an implementation or chosen-input protocol is in scope.

These establish a valid instance and the known attack surface. Passing them
does not prove ECDLP hardness.

Run planted controls through the same arithmetic and reporting path before
trusting it: malformed or singular curves, incorrect order claims, and small
known examples that trigger anomalous, low-embedding-degree, and twist-factor
findings. Preserve expected and actual results. If a material control fails or
is skipped, dependent conclusions are `INDETERMINATE` rather than passing.

## What an `F_q`-isogeny fixes

For elliptic curves connected by an isogeny defined over `F_q`, Tate/Honda-Tate
(KN-TECH-061) fixes the Frobenius polynomial and hence the point count over
every finite extension. For a fixed target subgroup order `r`, the following
are therefore class invariants:

- `N`, its factorization, Pohlig-Hellman exposure, and the cofactor `N/r`;
- anomalous status and ordinary versus supersingular status;
- each `ord_ell(q)` and MOV/Frey-Ruck target field for fixed prime factors
  `ell | r` with `gcd(q, ell) = 1`;
- the ordinary rational endomorphism algebra;
- in odd characteristic, the quadratic-twist order.

For composite `r`, `r | N` and the numerical cofactor `N/r` are invariant,
but existence of a cyclic point of exact order `r` can vary with the rational
group decomposition. A class-wide attack claim must therefore be factor-wise,
or conditional on a certified exact-order subgroup and its preservation along
the path.

Sampling more vertices supplies no independent evidence about these values.
If one yields a certified below-threshold attack, the class is weak in the
declared game. Conversely, passing these tests closes only these named routes.
The conclusion does not automatically apply to an isogeny defined only over
an extension or the algebraic closure.

The rational group decomposition, exact integral endomorphism ring and
conductor, rational torsion, `j`-invariant, available models, explicit
endomorphism formulas, descent behavior, and cost of reaching a representative
can vary. These are the proper per-vertex audit targets. Small coefficients,
a special model, low-degree edges, a small discriminant, or unusual `j` are
signals to investigate, not weakness predicates.

## Do not overstate isogeny hardness equivalence

Jao-Miller-Venkatesan (KN-LIT-171) gives a GRH-conditional random reduction for
ordinary curves within suitable endomorphism-ring levels. KN-FIND-f293c6 shows
why its concrete walk bound must be costed rather than invoked as a slogan.
The newer conductor-gap analysis in KN-LIT-ca35e0 is directional: it supplies
stronger transfer bounds in several regimes but leaves a hard descent-to-an-unknown-
floor problem and reports no evidence that a floor is ECDLP-weak.

Accordingly, neither "same order means uniformly hard everywhere" nor
"different conductor means a weak level exists" is an admissible audit
conclusion. KN-OPEN-cc1988 is still the endpoint-weakness question;
KN-OPEN-cbbd97 is the possible navigation gate. The protocol measures both
the prize and the gate rather than assuming either.

## Transfer gate and total cost

For every claimed path `phi:E -> E'`, retain ordered endpoint identities,
field of definition, maps or kernels, edge degrees, and independent checks
such as the dual composition. If `gcd(deg(phi), r) = 1`, the restriction to
the order-`r` subgroup is injective. Otherwise verify that `phi(P)` still has
order `r`; the map may kill the target subgroup.

At a fixed success probability compare unlogged costs:

`C*(E) = min_E' (C_find/build_path + C_transfer + C_best_attack(E'))`.

The candidate set includes `E` itself with the identity path and zero transfer
cost. Only after summing should an audit report `log2(C*)`. Keep offline reusable
precomputation separate from per-instance work and state time, memory,
data/queries, parallelism, and failure probability. An existential isogeny
without a feasible path is not a transfer attack; a cheap path without a
destination attack is not a weakness. A path supplied as private advice gives
an advice-holder result only; its discovery cost is not zero for a public
attacker.

The attack ledger includes at least Pohlig-Hellman, the rho baseline of
KN-TECH-006 with only demonstrably usable KN-TECH-018 discounts, the concrete
finite-field DLP after pairing transfer, anomalous/supersingular and applicable
descent attacks, the selected Shor resource model when quantum attacks are in
scope, explicit isogeny transfer, and any separate implementation attack. A
quantum row reports logical and physical qubits, gate counts and depth,
error-correction assumptions, runtime, and success probability. A weakness
label requires a reproducible attack or a certified
condition with a cited reduction and total cost below the frozen threshold.

## Statistics measure coverage, not algebraic truth

A verified weak witness establishes existence without statistics. Sampling is
appropriate only for prevalence under a declared distribution, search hit
rate, or randomized runtime.

Define the population as `F_q`-isomorphism classes, not equations, and state
whether its measure is uniform vertices, a deployed curve generator, or an
attacker's graph walk. Record allowed edge degrees, component, radius,
conductor/volcano strata, stopping rule, revisits, and unique samples.
Neighbor walks may be degree-biased and autocorrelated; independent restarts,
a justified mixing or Markov-chain bound, and correctly weighted strata are
required. An effective sample size is a diagnostic rather than proof of
mixing. Adaptive screens require fresh confirmation, and multiple tests need
an explicit correction.

For i.i.d. Bernoulli samples from one fixed law and a predeclared fixed
weakness predicate, use a predeclared exact binomial interval. In that i.i.d.
setting, zero hits gives the one-sided `1-alpha` upper prevalence bound

`p_U = 1 - alpha^(1/n)`,

with `3/n` only its large-`n` 95% approximation. Count in `n` only samples on
which the frozen predicate is determinate, and report excluded and
`INDETERMINATE` samples separately. Without a quantified false-negative and
missingness model, the interval bounds validated detector-hit prevalence, not
the prevalence of truly weak curves. Stratified, unequal-probability, or
dependent sampling requires stratum- or design-aware inference; sampling
without replacement from a known finite class uses a hypergeometric bound.
These statements concern a declared prevalence, never cryptographic bits and
never nonexistence. "No weak representative exists" requires exhaustive
coverage or a mathematical exclusion proof. A low prevalence estimate does
not address a generator that deliberately selects a rare representative.

## Program use

The canonical workflow is `.claude/skills/audit-curve/SKILL.md`,
with a cross-host adapter under `.agents/skills/audit-curve/`. It uses
`tools/isogeny_class_screen.py` only as an advisory prime-field ordinary
structural screen after `p` and total order `N` have been independently
certified. That tool does not validate the primality of `p` or a custom `N`,
and its sampled neighbors are never a point-count, coverage, or hardness
certificate. Scientific experiments still launch only through `run`;
substantive searches for new curves or isogenies also produce the
`research-visuals` artifacts required by AGENTS.md. Audit output does not
change a hypothesis, evidence, or goal status; the Coordinator owns any later
archival and promotion decision.
