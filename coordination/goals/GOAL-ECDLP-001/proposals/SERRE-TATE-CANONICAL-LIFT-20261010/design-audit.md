# Serre--Tate canonical-lift design audit

## Audit basis

- Idea: `IDEA-20261009-bec077`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  research status was changed.
- The proposal mixes a canonical-lift correctness check, a class-number
  survey, and a rational-approximation conjecture. Those are separate claims
  and need separate validity and interpretation paths.

## Mathematical and protocol gaps

The CM statement is not yet a runnable claim about a sampled population. For
each curve the record must compute the trace `t`, the order conductor, and the
actual endomorphism order with discriminant `D`; it must not replace the
discriminant by `t^2 - 4p` without certifying the conductor. “Random ordinary
curve” also needs a fixed sampler and distribution: sampling curves, traces,
j-invariants, and isomorphism classes gives different weights. The record
must publish the ordinary/supersingular counts and the sampling weights.

The asserted fit `h(D) = c sqrt(p)` times a slowly varying factor is a
heuristic, not a prediction with a fixed effect size. Class numbers vary with
the discriminant and conductor, and a bounded sample over three size bands
cannot establish an exponent or a uniform constant. The contract must state
the exact class-number computation, binning, robust summary, and predeclared
falsification rule. It should report `h(D)`, `|D|`, conductor, and the ratio
to the chosen reference separately, rather than infer a law from a fitted
line. The phrase “global degree `[H:Q]`” must be replaced by the precise
quantity, such as the degree of the Hilbert class polynomial or the degree of
the selected CM j-invariant over the declared base field.

The small-characteristic canonical-lift arm needs an explicit input and
certificate contract. It must identify the ordinary reduction, the chosen
Serre--Tate lift branch, the Frobenius lift or modular-polynomial equation,
the p-adic precision, and the exact Hilbert class polynomial `H_D`. A check
that `H_D(j) = 0 mod p^k` is a consistency check once the correct order and
branch are fixed; it is not evidence for the class-number fit. A Newton
failure is an algorithm or branch failure unless an independent certificate
shows that all hypotheses and precision conditions held.

The rational-approximation prediction is currently undefined and too strong.
The experiment must specify whether an approximation is `a/b` with coprime
integers, the height `max(|a|,|b|)`, the required p-adic valuation of
`j-a/b`, the embedding and precision, and the search algorithm. A
p-adic residue has trivial rational truncations, so a bound such as
`p^(k/2)` cannot be assessed without an exact approximation threshold and a
null distribution. Lattice reduction output is not a proof of nonexistence;
failure to find a candidate is censored search evidence. The control should
include random p-adic residues with matched precision and, where possible,
independently chosen ordinary lifts, while retaining the full candidate list
and search bounds.

Most importantly, the proposal never supplies an ECDLP reduction or a
load-bearing cost path. A large CM class-field degree or a short-rational-
approximation observation does not by itself alter the cost of group
operations, relation generation, or scalar recovery. The companion lane
requires the record to name the proposed map, subgroup preservation, recovery
step, and complete cost accounting. Without that bridge this is a CM/lift
control, not an ECDLP experiment.

## Required runnable contract

Before approval, split the proposal into independently valid arms and freeze:

- exact prime/curve sampling, ordinary classification, trace and conductor
  certificates;
- the class-number algorithm, discriminant/order data, bins, sample size,
  confidence or uncertainty rule, and raw per-curve table;
- the small-p modular-polynomial source and hash, Newton branch selection,
  precision, independent p-adic replay, and `H_D` certificate;
- the rational-approximation definition, height/search ceiling, valuation
  threshold, lattice parameters, matched p-adic null, and censored-search
  label;
- resource measurements for modular-polynomial construction and class-number
  computation; and
- if an ECDLP implication is retained, an explicit transfer/recovery contract
  with subgroup, map, correctness, and full-cost checks.

Every arm needs exact commands, source/dependency hashes, seeds, stdout/stderr,
raw machine-readable output, validity status, and archive handoff. A failed
Newton branch, unavailable `Phi_p`, incomplete lattice search, or missing
class-number certificate is `invalid` or `failed_infrastructure`, not a
negative result.

## Interpretation and disposition

A valid run could certify only the named canonical-lift identities, the
measured class-number table, and the bounded rational-search outcomes. It
cannot establish a uniform `sqrt(p)` law, a universal height lower bound, or
an ECDLP speedup or obstruction. Any negative statement closes only the exact
sampling, precision, and search scope.

Disposition: **keep proposed; do not approve or dispatch as one combined
experiment.** The canonical-lift identity arm may be useful as a correctness
fixture, while the class-number survey and rational-approximation search need
separate contracts. The ECDLP lane should remain unchanged unless a complete
transfer and cost model is added.

Next action: split the arms, repair the sampling and p-adic approximation
definitions, and run readiness checks independently. If the intended purpose
is only to preserve the canonical-lift identity, narrow the proposal to that
finite control and remove the class-number and ECDLP language.
