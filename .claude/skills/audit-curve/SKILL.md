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

For a supplied isogeny, closed path, or representation-changing map, also
follow `.claude/skills/transfer/SKILL.md`. Use
`docs/endomorphism-rules.md` for the additional closed-loop and GLV
certificate; neither document changes this skill's verdict vocabulary.

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

For an ordinary curve, factor
`Delta_pi = f_pi^2 D_K` with `D_K` fundamental and retain the
factorization, primality, and fundamental-discriminant certificates. Record

`Z[pi] = O_(f_pi) subseteq End(E) = O_(f_E) subseteq O_K`,

so `f_E | f_pi`, the representative order has discriminant
`D_E = f_E^2 D_K`, and
`g_(pi,E) = [End(E):Z[pi]] = f_pi/f_E`. Determine `f_E` from an
endomorphism-ring basis or an independently checkable equivalent certificate;
never copy `f_pi` into `f_E`. If that certificate is absent, report `f_E`,
`D_E`, and `g_(pi,E)` as `INDETERMINATE`. Retain the complete known
factorizations and every local valuation of `f_pi` and `f_E`.

5. For odd `q`, compute the quadratic-twist order `q + 1 + t`, its known
   factorization, subgroup sizes, and invariant factors. Treat other twists
   separately at exceptional `j`-invariants.
6. For any claimed extension-torsion signal, compute `t_0 = 2`, `t_1 = t`,
   and `t_m = t t_(m-1) - q t_(m-2)`, hence
   `N_m = #E(F_(q^m)) = q^m + 1 - t_m`, through a stated bounded `m`.
   A prime `ell | N_m` certifies a point of order `ell`; it does not prove
   that all of `E[ell]` is rational. For `ell != char(F_q)`, full rational
   `ell`-torsion requires `Frob_q^m` to act as the identity on `E[ell]`;
   a repeated characteristic-polynomial root modulo `ell` is insufficient.
   Treat characteristic-`ell` torsion separately and identify the original
   order-`r` subgroup under the field embedding instead of replacing it with
   newly visible torsion.
7. After splitting composite `r` for Pohlig--Hellman, compute
   `k_ell = ord_ell(q)` for every attack-relevant prime factor `ell | r` with
   `gcd(q, ell) = 1`, using an exact minimality certificate. Reporting only
   that `ell | q^k - 1` proves an upper bound, not the embedding degree. If
   `ell | q`, mark pairing transfer `NOT_APPLICABLE` for that factor and test
   the characteristic-specific attacks separately; never write `ord_r(q)`
   blindly for a composite subgroup.
8. When adversarial inputs, post-validation faults, or a raw scalar-
   multiplication API are in scope, audit the formulas actually reached.
   Record which curve coefficients the decoder, addition, doubling, ladder,
   and output path consume. Enumerate the **formula-compatible companion
   family** obtained by varying coefficients that the arithmetic omits; test
   both nonsingular companions and deliberately singular controls. For a
   singular cubic, work only with its smooth locus, prove the applicable
   group law and order, and label the result `IMPLEMENTATION_WEAK`: a singular
   companion is not an elliptic curve, an isogenous representative, or
   evidence about the source ECDLP.

   Price the attack from the output oracle the implementation really exposes.
   Full point coordinates or a raw shared-coordinate target can support
   Pohlig--Hellman/generic DLP accounting. A KDF, MAC, accept/reject, or
   ciphertext-confirmation oracle does not expose a group element and cannot
   inherit a square-root DLP cost automatically. In that case record exact
   subgroup enumeration or prime-power digit-lifting queries, sign ambiguity
   from x-only outputs, the CRT modulus, and any bounded-interval completion
   against a legitimate public key. Require scalar reuse and the necessary
   chosen-input, fault, or local-API capability; otherwise mark the attack
   precondition false.

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
- the CM field, fundamental discriminant `D_K`, and Frobenius-order
  conductor `f_pi`;

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

The conductor `f_E` of the actual endomorphism ring is
representative-dependent. For a separable `ell`-isogeny with
`ell != char(F_q)`, classify the edge from certified endpoint valuations:

- horizontal: `v_ell(f_E') = v_ell(f_E)`;
- ascending: `v_ell(f_E') = v_ell(f_E) - 1`;
- descending: `v_ell(f_E') = v_ell(f_E) + 1`.

The total `ell`-volcano depth is `v_ell(f_pi)`, while the source level is
`v_ell(f_E)`. A modular-polynomial root count, graph distance, or square
factor of `Delta_pi` is diagnostic evidence, not an endpoint
endomorphism-ring certificate. If `f_pi = 1`, then `f_E = 1` throughout the
class and no separable conductor-changing edge exists.

Characteristic-power Frobenius requires a separate record. In particular,
Koblitz `tau` has degree two and is inseparable; record its explicit map,
order relation, subgroup eigenvalue, action order, and evaluation cost, but
do not label it a horizontal degree-two volcano edge.

## 3. Verify every claimed isogeny transfer

For each path from source `E` to candidate `E'`, retain the ordered endpoint
identities, maps or kernel descriptions, edge degrees, field of definition,
and independent checks such as the dual composition. Measure separately:

- finding the path;
- constructing or loading it;
- mapping the input points;
- destination attack work;
- reusable offline work versus per-instance online work.
- the certified `f_E` and order discriminant at every endpoint;
- each edge's separability and horizontal, ascending, descending, or
  unresolved direction;
- the conductor-changing degree obligation independently of horizontal
  navigation.

For a target subgroup of order `r`, `gcd(deg(phi), r) = 1` is a sufficient
condition that `phi` is injective on the subgroup. Otherwise compute the
order of `phi(P)` explicitly. An abstract existence theorem or matching point
count is not an operational transfer attack. If the path is supplied as
private advice, `SOURCE_TRANSFER_WEAK` applies only to the advice holder; do
not assign zero discovery cost to a public attacker.

For endpoints with certified conductors `f_1` and `f_2`, record

`N_vertical = lcm(f_1, f_2) / gcd(f_1, f_2)
            = product_ell ell^abs(v_ell(f_1)-v_ell(f_2))`

as the necessary conductor-changing degree factor. It is not the total path
degree, a construction algorithm, or a runtime estimate; horizontal
navigation and map construction remain separately charged.

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
- protocol and implementation attacks, including formula-compatible smooth
  and singular companions when adversarial points are in scope, kept separate
  from plain ECDLP.

For source `E`, compare unlogged costs using

`C*(E) = min_E' (C_find/build_path + C_transfer + C_best_attack(E'))`.

Include `E` itself as the identity-path candidate with zero transfer cost.
Report `log2(C*)` only after the sum is formed. Include memory, data, success
probability, timeouts, preprocessing amortization, and uncertainty. A curve is
weak only relative to the frozen threshold and threat model.

Do not convert `f_pi`, `f_E`, `g_(pi,E)`, their largest prime factors, or a
volcano depth directly into ECDLP bits. A conductor-related advantage enters
the ledger only through either:

- an explicit endomorphism with certified degree, formula, subgroup
  eigenvalue, usable action order and orbit structure, evaluation and
  canonicalization cost; or
- an explicit transfer path whose discovery, construction, evaluation,
  destination attack, recovery, and verification costs are all charged.

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
