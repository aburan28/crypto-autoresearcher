# Endomorphism and isogeny-loop supplement

Read this with [`AGENTS.md`](../AGENTS.md),
[`audit-curve`](../.claude/skills/audit-curve/SKILL.md),
[`transfer`](../.claude/skills/transfer/SKILL.md), and
[`KN-TECH-6a2ef9`](../knowledge/techniques/KN-TECH-6a2ef9.md).

This file creates no authority, scientific state transition, execution entry
point, or mandatory preflight. Generic correspondence identity, map typing,
subgroup preservation, complete-cost accounting, controls, exploration
boundaries, and reporting remain governed by `transfer`. Curve-weakness
verdicts remain governed by `audit-curve`. This supplement adds only the
closed-loop and GLV/GLS obligations specific to endomorphism arithmetic.

## Closed-loop certificate

Apply the transfer obligations to every edge before treating a path as an
endomorphism.

1. Retain every map `phi_i:E_i -> E_(i+1)`, its exact degree, kernel or formula,
   field of definition, exceptional inputs, coordinate conversions, and
   correctness certificate.
2. A closed path needs an explicit endpoint isomorphism
   `iota:E_n -> E_0` over the declared working field. Matching
   `j`-invariants alone does not certify closure there because the endpoints
   may be twists. If individual maps live over an extension, an
   `F_q`-endomorphism claim needs a descent certificate for the composite.
3. Certify that
   `Phi = iota o phi_(n-1) o ... o phi_0`
   is a group endomorphism and retain its exact degree. Non-backtracking in an
   isogeny graph does not establish either closure or non-scalarity.
4. For an isogeny `phi`, retain the dual-composition control
   `hat(phi) o phi = [deg(phi)]`. Do not count this forced scalar composition
   as a new endomorphism discovery, although its arithmetic may still be
   benchmarkable when requested.
5. For a scalar map `[n]`, `deg([n]) = n^2`. Therefore, after closure and map
   correctness are certified, a closed endomorphism of nonsquare degree is
   nonscalar. Square degree supplies no converse.

## Subgroup action and scalar decomposition

For the named cyclic subgroup `G = <P>` of order `r`:

1. Prove that `Phi` preserves `G`; equal ambient group orders do not establish
   preservation.
2. Prove the actual action `Phi(P) = [lambda]P`. A
   characteristic-polynomial root alone is only a candidate eigenvalue;
   identify which root acts whenever more than one action is compatible with
   the polynomial.
3. Verify the reconstruction congruence, for example
   `k = k_0 + k_1 lambda (mod r)`, and the corresponding point identity
   against reference scalar multiplication. Retain coefficient bounds, the
   reduced kernel-lattice basis, decomposition cost, map cost, and conversion
   cost. A lattice determinant alone does not certify short coefficients.
4. Repeated powers of one endomorphism do not automatically create additional
   independent decomposition dimensions. State the applicable endomorphism
   algebra and independent relations. Ordinary elliptic endomorphism algebras
   are quadratic; supersingular, higher-dimensional, and combined-map claims
   require their own applicable construction and compatible maps.

## Candidate evaluation

Within the authorized family and budget:

- compare direct evaluation with factored evaluation through explicit maps;
- include applicable mixed-degree ideal-class relations and alternative curve
  models instead of restricting the search to powers of one prime-degree step;
- distinguish geometric degree from evaluation cost: composition degree is a
  product, while sequential evaluation charges the edge costs and every field,
  normalization, and coordinate conversion;
- label modeled and measured costs separately;
- deduplicate the same mathematical map as a discovery, but retain
  cost-distinct formulas and factorizations as separate implementations; and
- require a verified applicability record before using a published family as a
  baseline or claiming that a bounded search covered it.

A high expanded degree does not by itself make a factored map expensive, and a
low degree does not establish a speedup.

## Benchmark and claim boundary

Freeze the strongest validated baseline available inside the declared
dependencies, hardware, side-channel policy, and workload; disclose any
stronger known baseline that could not be run.

Separate Variable-base, fixed-base, batch, and multi-scalar multiplication.
Keep secret-scalar constant-time code separate from public-scalar
variable-time code. Use paired scalars and record decomposition, maps, group
work, conversions, setup reuse, verification, dispersion, and failures.

Check the identity, boundary scalars, subgroup inputs, exceptional
denominators, and coordinate conversions. Exhaustive toy checks and held-out
full-size cases support implementation correctness but do not replace
universal map certificates. Timing measurements do not establish constant-time
behavior.

Faster computation of `[k]P` for known `k` does not establish faster recovery
of unknown `k` from `P` and `[k]P`. Preserve measured arithmetic improvements,
but require a separate reduction and complete attack-cost record before making
an ECDLP work-factor claim.

## Source pointers

Respect each source record’s stated verification boundary.

- `recalled`: Dimitri Koshelev and Antonio Sanso, *Endomorphisms for Faster
  Cryptography on Elliptic Curves of Moderate CM Discriminants*,
  ePrint 2024/1985, <https://eprint.iacr.org/2024/1985>. This is a discovery
  pointer until a retrieved or knowledge record verifies the applicable claim.
- `kb`: `KN-LIT-390`, Benjamin Smith, *Easy scalar decompositions for efficient
  scalar multiplication on elliptic curves and genus 2 Jacobians*. Its
  knowledge entry defines the verified scope.
- `recalled`: Explicit-Formulas Database,
  <https://hyperelliptic.org/EFD/>. Formula assumptions remain to be checked
  against the selected model; operation counts are not wall-time measurements.
