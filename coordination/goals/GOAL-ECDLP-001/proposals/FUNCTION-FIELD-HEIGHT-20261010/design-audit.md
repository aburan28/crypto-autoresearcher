# Function-field generator-height design audit

## Audit basis

- Idea: `IDEA-20261009-c88658`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  research status was changed.
- The proposal is a height-formula control, not an ECDLP algorithm or a
  transfer by itself.

## Immediate field and sampling defect

The listed values `p in {2^8, 2^12, 2^16, 2^20}` are not prime
characteristics. If the intended base is `F_p(t)`, they must be replaced by
explicit primes; if the intended base is `F_q(t)` in characteristic two, the
record must use `q`, specify the finite fields, and change every point-count
and height normalization accordingly. A valid experiment also needs a fixed
family of elliptic surfaces across the fields. “Reuse E1 lattices” is not
enough: reduction can change singular fibers, wild contributions, rank,
torsion, and saturation.

## Height and lattice contract

The height formula is an identity for a specified relatively minimal elliptic
surface and section, with conventions for the zero section, intersection
pairing, fiber components, and local correction terms. It does not imply that
every surface has a non-torsion section in `[chi/2, 2 chi]`. The proposed
bound needs hypotheses on the family, rank, fiber configuration, and the
existence of the section being measured. If the search finds only some
sections, its smallest value is an upper bound, not `lambda_1`; a certified
Mordell--Weil basis, torsion quotient, rank, and saturation check are required
to claim the first minimum.

The record must define whether `lambda_1` is the canonical height, its square
root, or a lattice norm, and must publish the Gram matrix in that convention.
It must compute `chi`, intersection terms, and every local correction from an
independent path. A full Gram matrix from a non-saturated or incomplete basis
cannot certify a minimum. Rank-zero and torsion-only fibers need an explicit
outcome rather than a fabricated minimum.

The comparison with `D2` Q-lifts is not matched as written. A characteristic-
`p` function field and a characteristic-zero rational family have different
height normalizations and different bad-fiber behavior. The experiment must
bind one generic family, its integral models, specialization maps, and a
common geometric-height convention before comparing slopes. Any invocation of
Lang-type lower bounds must be labeled conjectural unless the exact theorem
hypotheses and constants are supplied; it cannot serve as an observed control
without that separation.

## Statistical and ECDLP limitations

“Uncorrelated with `p`” needs a declared estimand, balanced sample design,
family identifiers, and an uncertainty procedure. A regression across four
field sizes, especially when the surfaces change with characteristic, cannot
establish independence. The proposed interval `[chi/2, 2 chi]` must be tested
per predeclared family and surface, with missing-rank and failed-saturation
rows retained. The D2 arm needs a matched number of families and a fixed
alternative model; a positive slope in a nonmatched collection is not a
function-field/Q contrast.

Finally, the proposal does not give a map from a Mordell--Weil generator on a
surface to a finite-field group operation, relation, or scalar-recovery
procedure. A height observation is not a complexity result. Any ECDLP
interpretation would require an explicit specialization or transfer,
subgroup preservation, correctness certificate, and complete costs for
constructing and using the section. Without those items, the experiment must
remain descriptive.

## Required runnable contract

Before approval, freeze:

- exact prime or finite-field rows, an integral surface family, minimal-model
  and nonsingularity certificates, and specialization maps;
- the height convention, `chi`, zero-section/intersection conventions,
  local-fiber data, and an independent formula evaluator;
- certified Mordell--Weil rank, torsion, basis saturation, Gram matrix, and
  exact `lambda_1` or an explicit upper-bound label;
- matched function-field and characteristic-zero comparison families, with a
  declared estimand and uncertainty rule;
- raw section coordinates, basis certificates, failed searches, and resource
  measurements; and
- exact commands, source/dependency hashes, seeds, stdout/stderr, validity
  status, and archive handoff.

Rows with invalid characteristic, rank ambiguity, unsaturated bases, model
failure, or incomplete section search are `invalid` or
`failed_infrastructure`, not evidence for a height law.

## Interpretation and disposition

A valid run could document height identities and measured minima or upper
bounds for the named surfaces and fields. It cannot establish
p-independence, a universal `[chi/2, 2 chi]` envelope, a theorem about
characteristic-zero heights, or an ECDLP consequence. Negative evidence closes
only the exact family, field, and certified rank scope.

Disposition: **keep proposed and do not approve as a claim-changing
experiment.** It may be narrowed to a paired height-formula regression once
the field rows, surface family, MW certificates, and comparison convention
are repaired. The ECDLP lane should remain unchanged unless a complete
specialization and cost path is added.

Next action: replace the invalid field-size list, freeze one cross-field
family, certify the Mordell--Weil lattice rather than a found-section upper
bound, and rerun readiness before dispatch.
