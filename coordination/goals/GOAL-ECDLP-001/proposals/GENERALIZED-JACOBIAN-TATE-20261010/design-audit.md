# Generalized-Jacobian/Tate-pairing design audit

## Audit basis

- Idea: `IDEA-20261009-c8433d`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  research status was changed.
- The proposed result is an equivalence/control for a known pairing transfer,
  not a new ECDLP algorithm.

## Conceptual correction

The phrase “connecting homomorphism” is not yet the map being measured. For
the displayed sequence over a finite field, the long exact sequence has a
map from `E(F_q)` to `H^1(F_q,G_m)`, and Hilbert 90 makes that target zero.
The nontrivial Tate pairing instead requires a precisely chosen torsion
divisor, a second point or divisor class, a rational function with the stated
divisor, evaluation, and reduction modulo `N`-th powers. A lift in a
generalized Jacobian followed by multiplication and reading a multiplicative
coordinate can represent that construction, but the section, quotient,
coordinate, and evaluation map must be written explicitly. The current text
does not establish that its connecting map is literally Miller's value.

The modulus also needs an exact convention. For `m = (A) + (B)`, the record
must require distinct rational points (or state the non-rational/confluent
variant), specify the generalized-Jacobian equivalence relation and extension
class, and bind the signs and ordering that identify the class with `A-B`.
Exceptional divisors, poles at `A` or `B`, and points at infinity need
defined handling. Changing the modulus changes the extension class, so a
single fixed convention is not enough unless all inputs and maps are archived.

## Pairing-domain and comparison gaps

The reduced Tate pairing is not a scalar comparison on arbitrary pairs. The
experiment must state the exact `N`, field `F_{q^k}`, torsion generator(s),
second pairing input, and quotient target

`F_{q^k}^* / (F_{q^k}^*)^N`.

Comparing raw Miller outputs for equality can report false disagreements: the
representative is defined only modulo `N`-th powers, and inversions, divisor
orientation, loop conventions, and final exponentiation produce fixed
automorphisms or powers. The proposed “one fixed convention” must therefore
be converted into an explicit quotient comparison or a declared small-group
discrete-log normalization. The archive must retain both raw values and the
normalized comparison value.

The embedding-degree assertion needs the same precision. If `l` does not
divide `q^k - 1`, the `l`-primary part of the multiplicative target is
trivial, but the statement must distinguish the target's full nonzero element
from its `l`-primary quotient. If `l` divides `q^k - 1`, nondegeneracy still
requires the right torsion, a valid second argument, and a pairing value not
annihilated by the selected quotient. A no-embedding-degree case is a
negative-control theorem only after the domain is valid; it is not evidence
that the generalized-Jacobian arithmetic is correct.

## Required instance contract

Before approval, publish an exact table for every `(q,k,l,E,N,A,B,P,Q)` row,
including:

- prime or field certificates, curve equation, nonsingularity, group order,
  and torsion certificates;
- disjointness and rationality of the modulus points, the generalized-
  Jacobian divisor/function representation, and all exceptional-case rules;
- the generalized-Jacobian lift/multiply/read-coordinate algorithm, with an
  independent implementation or derivation path;
- Miller's function, divisor convention, final exponentiation, quotient
  normalization, and the exact expected fixed automorphism;
- positive nondegenerate rows for each embedding degree and matched negative
  rows with `l` absent from `q^k - 1`;
- raw values, normalized values, pair counts, failure categories, timings,
  and complete source/dependency/seed/command receipts; and
- an archive handoff that preserves failed and exceptional rows.

The proposed “three k-values x three primes x 10^3 pairs” stopping rule is
not enough until the table fixes which primes support which `l` and curve
orders. A pair with missing torsion or an invalid divisor is `invalid`, not a
trivial pairing. A generalized-Jacobian implementation failure is
`failed_infrastructure`, not a falsification of the pairing identity.

## Interpretation and disposition

A valid result could certify agreement of two explicitly normalized
implementations on the named finite instances and confirm the expected
embedding-degree behavior. It would restate or regression-test the known
pairing transfer. It would not lower the cost of the original ECDLP unless a
separate reduction, subgroup-preservation proof, and full cost model showed a
useful target-field DLP; the proposal currently claims none.

Disposition: **keep proposed as a control and do not approve as a new
ECDLP direction until the measured map is defined precisely.** The most
useful repair is to rename the first metric as “generalized-Jacobian lift
coordinate versus reduced Tate pairing,” specify quotient normalization, and
retain the cohomological exactness statement only as background. The
embedding-degree arm may then be a small independent regression experiment.

Next action: provide the exact pairing-domain/quotient contract and a
certified positive and negative instance table, then rerun readiness. Do not
interpret a raw 100% string-equality rate as a theorem about all moduli or
all curves.
