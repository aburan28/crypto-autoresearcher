---
name: audit-curve
description: Rigorously audit a specified elliptic curve, its twist, and reachable isogenous representatives for conventional ECDLP, transfer, and implementation weaknesses. Use when asked whether a named or supplied curve is weak, safe, or vulnerable through an isogeny.
---

# Audit a curve

Read `AGENTS.md` and `knowledge/techniques/KN-TECH-6a2ef9.md` before
starting. This skill produces a scoped audit; it does not certify security,
change research state, or replace the public `run` entry point. If the audit
requires launching an existing scientific experiment, route that launch
through `/run` and consume its archived result separately.

The default threat model is classical ECDLP on an explicitly identified
elliptic-curve subgroup. Do not reuse that conclusion for an isogeny-based
protocol such as CSIDH or SQIsign; state and audit that protocol's security
game separately.

## Required input

Resolve these values before assigning a mathematical verdict. Ask for only
the fields that cannot be recovered from an authoritative parameter source.

- The base field, including characteristic, extension degree, defining
  polynomial or basis, and element encoding.
- The exact curve model and coefficients, target subgroup, generator, claimed
  subgroup order `r`, claimed total order `N`, and cofactor.
- The protocol use: ECDH, ECDSA, x-only ladder, pairing protocol, plain ECDLP,
  or another named game.
- The attacker model and security threshold: classical or quantum, fixed
  success probability, time/operation unit, memory, data or queries,
  parallelism, and reusable precomputation.
- The isogeny scope: only the supplied curve, an explicit path, a bounded
  rational graph, or a declared distribution over the full class; state
  whether a path is public, private advice, or must be discovered.
- Any implementation in scope, including its point validation, subgroup
  checks, cofactor handling, coordinate formulas, and accepted encodings.

Record a global representation identity following `docs/curve-identities.md`.
That identity binds metadata; it is not a proof of curve equivalence or
correct arithmetic.

## 1. Establish the instance exactly

Use exact arithmetic and preserve commands, software versions, raw output,
and certificates. A timeout, missing package, partial factorization, or failed
point count is `INDETERMINATE`, never a passing check.

1. Prove the field definition is valid and the curve is nonsingular.
2. Check the generator is on the declared curve, `P != O`, and `[r]P = O`.
   With a complete certified factorization of `r`, prove its exact order by
   checking `[r/ell]P != O` for every distinct prime divisor `ell` of `r`
   (including the sole divisor when `r` is prime). Retain the primality and
   factor certificates; an incomplete factorization cannot certify exact
   order by this test.
3. Compute or independently certify `N = #E(F_q)`. The relation `[N]P = O`
   alone does not prove a point count. A certified Hasse-interval
   unique-multiple argument is valid when its field, divisor, point-order, and
   interval hypotheses are all proved. Record every unfactored cofactor
   explicitly.
4. Compute `t = q + 1 - N`, the Frobenius polynomial
   `X^2 - tX + q`, `Delta_pi = t^2 - 4q`, ordinary or supersingular status,
   and the rational group invariant factors.
5. For odd `q`, compute the quadratic-twist order `q + 1 + t`, its known
   factorization, subgroup sizes, and invariant factors. Treat other twists
   separately at exceptional `j`-invariants.
6. After splitting composite `r` for Pohlig--Hellman, compute
   `k_ell = ord_ell(q)` for every attack-relevant prime factor `ell | r` with
   `gcd(q, ell) = 1`, using an exact minimality certificate. Reporting only
   that `ell | q^k - 1` proves an upper bound, not the embedding degree. If
   `ell | q`, mark pairing transfer `NOT_APPLICABLE` for that factor and test
   the characteristic-specific attacks separately; never write `ord_r(q)`
   blindly for a composite subgroup.

Before trusting an arithmetic path, run planted positive and negative controls
through the same code path: at minimum a singular or malformed instance, an
incorrect point/order claim, and small examples exercising anomalous,
low-embedding-degree, and twist-factor findings. Preserve expected and actual
outputs. A failed or skipped material control makes dependent checks
`INDETERMINATE`.

For already-certified prime-field ordinary inputs,
`tools/isogeny_class_screen.py` may provide an advisory secondary structural
screen. It does not validate the primality of `p` or a custom total order `N`;
its custom `--n` argument is the total group order, not merely a subgroup
order. Require certified `p`, certified `N`, `p > 3`, and the documented short
Weierstrass preconditions before invoking it. Its sampled neighbors and output
are never coverage, point-count, or hardness certificates.

## 2. Separate class invariants from representative properties

First state whether each isogeny is defined over `F_q`, over an extension, or
only geometrically. For `F_q`-isogenous elliptic curves, the trace,
Frobenius polynomial, zeta function, and point counts over every extension
are equal. Consequently these checks are class-wide for a fixed `r`:

- total order, order factorization, Pohlig-Hellman exposure, and cofactor;
- anomalous status and ordinary versus supersingular status;
- factor-wise embedding degrees and MOV/Frey-Ruck target fields where
  `gcd(q, ell) = 1`;
- quadratic-twist order in odd characteristic;
- the rational endomorphism algebra, though not necessarily the integral
  endomorphism ring.

For composite `r`, the divisibility `r | N` and numerical cofactor `N/r` are
invariant, but existence of a cyclic point of exact order `r` can vary with
the rational group decomposition. State class-wide attack claims factor by
factor, or condition them on a certified subgroup and its preservation along
the path.

Do not sample multiple representatives as independent support for these
facts. Properties worth checking per representative include rational group
decomposition, exact endomorphism order and conductor, rational torsion,
`j`-invariant, efficiently computable automorphisms or endomorphisms, model
and formula behavior, descent-friendly representation, and explicit path
cost. A small coefficient, special model, short isogeny, small discriminant,
or unusual `j`-invariant is only a lead until tied to an attack.

## 3. Verify every claimed isogeny transfer

For each path from source `E` to candidate `E'`, retain the ordered endpoint
identities, maps or kernel descriptions, edge degrees, field of definition,
and independent checks such as the dual composition. Measure separately:

- finding the path;
- constructing or loading it;
- mapping the input points;
- destination attack work;
- reusable offline work versus per-instance online work.

For a target subgroup of order `r`, `gcd(deg(phi), r) = 1` is a sufficient
condition that `phi` is injective on the subgroup. Otherwise compute the
order of `phi(P)` explicitly. An abstract existence theorem or matching point
count is not an operational transfer attack. If the path is supplied as
private advice, `SOURCE_TRANSFER_WEAK` applies only to the advice holder; do
not assign zero discovery cost to a public attacker.

## 4. Build one attack ledger

Evaluate every applicable row at one frozen success probability and in
compatible cost units:

- Pohlig-Hellman followed by the best generic algorithm on each prime-power
  component;
- Pollard rho using the repository convention in `KN-TECH-006`, adjusted only
  for demonstrably usable automorphisms, multi-target effects, and declared
  parallelism;
- MOV or Frey-Ruck, factor by factor where `gcd(q, ell) = 1`, followed by the
  best applicable finite-field DLP method in `F_(q^k_ell)`; `k_ell` or the
  target-field bit length alone is not a cost estimate;
- anomalous, supersingular, subfield, Weil-descent, or other special attacks
  whose exact preconditions hold;
- when the frozen attacker is quantum, Shor's algorithm with the declared
  logical and physical qubit counts, gate counts and depth, error-correction
  assumptions, runtime, and success probability;
- an explicit isogeny transfer to a representative with a concrete attack;
- protocol and implementation attacks, kept separate from plain ECDLP.

For source `E`, compare unlogged costs using

`C*(E) = min_E' (C_find/build_path + C_transfer + C_best_attack(E'))`.

Include `E` itself as the identity-path candidate with zero transfer cost.
Report `log2(C*)` only after the sum is formed. Include memory, data, success
probability, timeouts, preprocessing amortization, and uncertainty. A curve is
weak only relative to the frozen threshold and threat model.

## 5. Treat statistics as coverage evidence

A single verified representative, usable path, and below-threshold attack
establish existence without a p-value. Statistics are for prevalence,
search-hit rate, or randomized runtime—not algebraic truth.

Before sampling, freeze the population and distribution: uniform
`F_q`-isomorphism classes, the deployed curve generator, and a neighbor walk
are different populations. Deduplicate isomorphism classes rather than
equations or `j`-invariants alone. Record allowed edge degrees, component,
radius, conductor or volcano strata, stopping rule, revisits, and coverage.
Correct degree bias and autocorrelation with a justified mixing or
finite-population argument; an effective sample size is a diagnostic, not a
mixing proof. Confirm adaptive discoveries on fresh samples and account for
multiple testing.

For i.i.d. Bernoulli samples from one fixed law and a predeclared fixed
weakness predicate, report a predeclared exact binomial interval. In that
i.i.d. setting, zero hits gives the one-sided `1-alpha` prevalence bound
`1 - alpha^(1/n)`; `3/n` is only its large-`n` 95% approximation. Count in
`n` only samples on which the frozen predicate is determinate, and report
excluded and `INDETERMINATE` samples separately. Without a quantified
false-negative and missingness model, the interval bounds validated detector
hits rather than the prevalence of truly weak curves. Stratified,
unequal-probability, or dependent samples require stratum- or design-aware
inference; use a hypergeometric bound for sampling without replacement from a
known finite population. None of these bounds proves absence, and a low
estimated prevalence does not protect against a parameter generator
deliberately selecting a rare representative.

## 6. Emit a scoped verdict

Use [the report template](references/report-template.md). Every individual
check has one of `PASS`, `FAIL`, `NOT_RUN`, `INDETERMINATE`, or
`NOT_APPLICABLE`, plus its evidence basis. The final label is exactly one of:

- `CLASS_WEAK`
- `WEAK_REPRESENTATIVE_EXISTS`
- `SOURCE_TRANSFER_WEAK`
- `IMPLEMENTATION_WEAK`
- `NO_WEAKNESS_FOUND_WITHIN_SCOPE`
- `INDETERMINATE`
- `INVALID_INSTANCE`

Never emit `SAFE` or `SECURE`. A weakness verdict requires a reproducible
attack or a certified structural condition with a cited reduction and total
cost below the threshold. `NO_WEAKNESS_FOUND_WITHIN_SCOPE` must enumerate the
attacks, path boundary, and coverage actually checked. Absence across an
isogeny class requires exhaustive coverage or a mathematical exclusion proof.

Keep audit artifacts outside immutable evidence directories until a
Coordinator assigns write scope and archival ownership. The Coordinator alone
may promote the result or change official research state. If the audit expands
into a substantive search for new curves, isogenies, endomorphisms, or scalar
rules, also follow `.claude/skills/research-visuals/SKILL.md` and produce its
source-linked report, diagram, and PDF.
