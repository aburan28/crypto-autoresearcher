# SNFS-G3 design audit

## Audit basis

- Idea: `IDEA-20261009-b6d31b`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run, no
  hypothesis or experiment status was changed, and no approval or dispatch is
  issued by this record.
- Related contract: `EXP-ECDLP-3e8403`.

The proposal asks whether generalized-Mersenne/Solinas-shaped number fields
can improve bounded-height point coverage or produce rank and height effects
useful to the SNFS field-lift route. The question is potentially worthwhile,
but the submitted contract does not yet distinguish its executable work from
the existing bounded-box experiment or define certificates for its stronger
arithmetic claims.

## Overlap and novelty

`EXP-ECDLP-3e8403` already covers the principal proposed measurement shape:
lifting a curve into an SNFS-associated field, bounded coefficient-box search,
degree variation, matched random-field comparisons, residue coverage, and
re-verification of reduced points. A second experiment that repeats those
measurements for Solinas-shaped polynomials would duplicate the existing
coverage/degree-ladder lineage rather than establish a new mechanism.

The Solinas or generalized-Mersenne field family is a legitimate new input
family. Two possible successor questions are also distinct if they are made
explicit and separately certified:

1. a preregistered field-invariant analysis asking whether root discriminant
   predicts a specified coverage or point-level outcome under matched fields;
2. an actual number-field Mordell--Weil descent asking for certified rank
   bounds, independent points, and canonical heights.

Neither distinction is present sufficiently in the current proposal. Adding a
discriminant column to the existing bounded-box output is post-hoc analysis,
not a new experiment. A bounded search that finds points is not a descent
certificate, and its output cannot by itself establish rank gain, independence,
minimal height, or completeness below a height threshold.

## Load-bearing gaps

### Field and curve definition

The contract uses `E(K_f)` and `rank E(K_f)-rank E(Q)` without defining the
characteristic-zero curve. A curve `E/F_p` does not determine a unique curve
over `Q` or `K_f`. The successor must choose either a fixed global curve
`E_0/Q` with a certified degree-one reduction prime, or an explicitly defined
curve over `K_f` produced by a fixed coefficient-lifting rule. The comparison
group must then be stated consistently; otherwise the proposed rank delta is
undefined.

Each field instance needs reproducible certificates for irreducibility, the
maximal order, power-order index, field discriminant, root discriminant,
signature, the integral basis, the selected degree-one prime and residue map,
and the required unramified/good-reduction conditions. The polynomial
discriminant is not a substitute for the maximal-order field discriminant.

### Rank, descent, and height

An executable descent specification must state the method, lower and upper
rank bounds, torsion handling, saturation or index handling, independent-point
certificates, and the policy for conditional analytic evidence. A list of
found points is a lower-bound observation at most.

It must also define the height: canonical versus naive/projective, normalization
by field degree, the Weierstrass model, finite-place and denominator terms, and
the relation between coefficient-box size and canonical height. “Minimal new
point” requires a complete relevant lattice search or a certified lower bound;
the first point returned by a bounded search is only an observed upper bound.

### Coverage and controls

The successor must separate distinct reduced points, distinct reduced
`x`-coordinates, independent relation vectors, held-out target coverage, and
relation yield per unit of field-search work. `x(P)=x(-P)`, and reduced
membership does not establish target access or relation utility.

Random controls must use the same `p`, the same reduced curve, the same degree,
the same lift rule, and a declared matching policy for coefficient height,
irreducibility, maximal-order index, signature, root discriminant, splitting,
and any relevant regulator/unit or class-group effects. Otherwise field shape
is confounded with prime, curve, or basis effects.

Root discriminant may be a prespecified covariate only in a matched design. The
analysis must account for degree, signature, maximal-order index, polynomial
versus field discriminant, coefficient or power-basis distortion, regulator and
unit rank, class number, splitting/ramification at the reduction prime, and
curve-model height. A null regression would close only that matched statistical
question, not the broader claim that field arithmetic is irrelevant.

## Feasibility and readiness

The proposed degree range and descent/class-group/height workload are not
supported by a runnable implementation contract. The first gate should be a
small certificate-producing pilot at degrees 3 and 4, with one fixed prime and
curve and a narrowly matched field set. Degrees 7, 8, and 12 should not enter a
main claim until the pilot demonstrates field construction, maximal-order
certification, descent output, independence/saturation handling, and
reproducible height calculations.

The repair is runnable only when the repository readiness check reports the
repaired successor as ready, for example:

```text
python3 tools/newest_experiments.py --experiment <repaired-successor-id>
```

The returned `execution_state` must be `ready`; a design-only record or an
implementation that cannot produce the named certificates remains
`review_required` and is not approvable under the execution gate.

## Claim ceiling

A positive result could establish only a finite-scale difference for the
declared Solinas field family, curve model, prime, height convention, controls,
and certificate set. It would not establish an asymptotic coverage exponent,
an ECDLP algorithm, a general rank phenomenon for generalized-Mersenne fields,
or transfer to deployed parameters. A negative result would close only the
tested fields, degrees, curves, height bounds, and descent scope; it would not
close all low-weight polynomials or all lifts.

## Disposition and next action

Disposition: **keep proposed; medium priority conditional on redesign; do not
approve or create a second experiment alongside `EXP-ECDLP-3e8403`.** The idea
becomes high-priority only after it demonstrates a genuine field-family delta
and a runnable, certificate-producing contract.

The next action is a repair/successor specification that separates (a) matched
root-discriminant/invariant regression from (b) actual Mordell--Weil descent,
defines the global or number-field curve, fixes the same-prime controls, and
starts with a degree-3/4 field-certificate pilot. The repaired contract must
name its exact artifacts, seeds, stopping rules, failure/infrastructure
outcomes, and point/relation coverage metrics before it can be considered for
approval.
