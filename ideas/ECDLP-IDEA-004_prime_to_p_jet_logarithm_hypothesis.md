# ECDLP-IDEA-004 — Prime-to-p jet logarithm

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a lift or additive identity on anomalous controls is known behavior.

## Falsifiable hypothesis

For a generic ordinary `E/F_p` with cryptographic prime subgroup order `ell!=p`, there is
a bounded-order deformation jet and an efficiently computable, lift-choice-independent
functional `J` into an explicit `ell`-primary module such that
`J([n]R)=n J(R)` for all `R` in the subgroup and `J(P)!=0`. Evaluating `J(P)` and `J(Q)`
then recovers `x` from `Q=[x]P` with complete construction and ambiguity cost below
`ell^1/2`.

The prediction is specifically prime-to-`p`. Reproducing Smart/Semaev/Satoh–Araki on
anomalous `p`-torsion is only a positive control.

## Mechanism-new operation

Lift the curve and marked points to a fixed-order infinitesimal or Witt-vector
neighborhood, cancel lift-dependent terms with a Frobenius/deformation cocycle, and
extract an additive `ell`-primary jet coordinate. The new operation is the cancellation
that makes the coordinate canonical on prime-to-`p` torsion; merely taking a p-adic
elliptic logarithm is known and does not supply this property.

## Assumptions

1. `E(F_p)` contains `<P>` of known prime order `ell=p^(1+o(1))`, with `ell!=p`.
2. Curve and point jets of fixed order `h` can be represented with exact arithmetic and
   all lift choices recorded.
3. `J` is invariant under allowed changes of lift and computable without knowing `x`.
4. The output module has explicit `ell`-primary arithmetic and a known basis; an implicit
   module DLP is not treated as a coordinate.
5. Branch search, precision, Frobenius evaluation, and module-coordinate recovery are
   included in the cost.
6. Any scaling inferred from toy primes is heuristic and model-bound.

## Semantic fingerprint

`prime_to_p_deformation_jet | Frobenius_cocycle_cancellation | explicit_ell_primary_additive_coordinate | direct_target_descent | extends_beyond_anomalous_formal_log`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — motivates leaving the closed prime-field PDP route.
2. `ledger/H-REP-001.yaml` — distinguishes a deformation functional from a curve-model rewrite.
3. `ledger/H-ISO-001.yaml` — distinguishes the lift from a same-field isogeny-neighbor search.
4. `ledger/DEC-20260716-004.yaml` — confirms no factor-base reshaping is involved.
5. `ledger/SYNTHESIS-20260716.md` — supplies the full-cost and toy-versus-crypto boundary.

## Closest primary literature

- Semaev, [Evaluation of discrete logarithms in a group of p-torsion points](https://doi.org/10.1090/S0025-5718-98-00887-4), gives the anomalous p-primary boundary.
- Satoh and Araki, [Fermat Quotients and the Polynomial Time Discrete Log Algorithm](https://doi.org/10.14992/00009878), independently exploits anomalous curves.
- Smart, [The discrete logarithm problem on elliptic curves of trace one](https://research-information.bris.ac.uk/en/publications/the-discrete-logarithm-problem-on-elliptic-curves-of-trace-one/), is the closest cryptanalytic lift.
- Borger and Gurney, [Canonical lifts of families of elliptic curves](https://arxiv.org/abs/1608.05912), supplies nearby canonical-lift geometry but not the claimed ECDLP coordinate.

The checked literature does not provide a nonzero prime-to-`p` jet coordinate of the
stated kind. That is not a novelty proof; novelty remains unverified.

## Complete factor-base-to-target-descent path

Here the factor-base replacement is an explicit basis of the proposed `ell`-primary jet module.

1. Construct the frozen order-`h` lift of `E`, its Frobenius lift, and a canonical family of
   point lifts; retain the choice parameters.
2. Derive the jet cocycle and quotient out every lift-change direction proved irrelevant.
3. Evaluate `J(P)` and express it in the explicit module basis; reject the instance if the
   coordinate is zero or basis extraction invokes a hidden DLP.
4. Evaluate `J(Q)` using the identical lift rule and precision, including every ambiguity.
5. Solve the linear module equation `J(Q)=x J(P)` for `x mod ell`; if multiple coordinates
   survive, enumerate and charge them.
6. Descend the candidate back to the original finite-field curve and verify `[x]P=Q`.

## Full rho/BSGS cost model

Let jet/curve construction cost `ell^c`, one canonical point evaluation cost `ell^e`,
reciprocal probability of obtaining an unambiguous nonzero coordinate `ell^delta`, module
coordinate recovery cost `ell^u`, and stored precision/state `ell^s`.

- Pollard rho: `ell^(1/2+o(1))` group operations and constant state.
- BSGS: `ell^(1/2+o(1))` time and memory.
- Frozen lift and cocycle construction: `ell^(c+o(1))`.
- Expected usable evaluations: `ell^(e+delta+o(1))`.
- Module solve and ambiguity resolution: `ell^(u+o(1))`.
- Final verification is exponent-zero scalar multiplication.

The proposed time exponent is `lambda=max(c,e+delta,u)` and memory exponent is `mu=s`.
Precision growing linearly in `ell`, enumeration of `ell^delta` lifts, or a module DLP of
order `ell` restores at least the generic boundary and must be charged.

## Likely fatal obstruction

For good reduction, the formal-group kernel is pro-`p`, while reduction is injective on
prime-to-`p` torsion. The p-adic logarithm therefore has no nonzero `ell`-primary signal
when `ell!=p`. Any apparent coordinate is expected either to vanish, depend on arbitrary
lift error containing `x`, or move the DLP into an implicit order-`ell` module. Higher jet
precision alone does not alter this structural obstruction.

## Proof track

Construct `J` functorially, prove lift-choice cancellation and additivity on the full
prime subgroup, prove `J(P)!=0`, exhibit an explicit module basis, and bound
`lambda<1/2` without anomalous assumptions.

## Disproof track

Prove every finite-order deformation functional factors through the pro-`p` formal group
or vanishes on prime-to-`p` torsion; exhibit two allowed lifts giving different `J`; or
show module-coordinate extraction is equivalent to the original DLP.

## Positive and negative controls

- Positive control: anomalous curves with `#E(F_p)=p`, where the established p-primary
  attack must be reproduced exactly.
- Positive instrumentation control: a synthetic additive dual-number group with an
  explicit nonzero jet coordinate.
- Negative control: ordinary curves with matched `p` but prime subgroup `ell!=p`.
- Lift-choice control: independently perturb every admissible coefficient and point lift.
- Circularity control: record all accesses and reject any code path using known toy logs.

## Quantitative promotion and falsification gates

Test all ordinary and anomalous curves in preregistered families at 10–28-bit primes,
orders `h=1,2,3,4`, at least 200 prime-to-`p` subgroups per size, and every admissible lift
choice through 18 bits. Promotion requires all of:

- 100% reproduction of anomalous controls;
- a lift-invariant, nonzero `ell`-primary coordinate on at least 95% of ordinary test
  subgroups at the two largest sizes;
- exact additivity on 10,000 random triples per subgroup with zero failures;
- upper 95% bounds `c<=0.20`, `e+delta<=0.30`, `u<=0.30`, hence `lambda<=0.30`;
- zero use of a table or implicit DLP of size `ell^0.30` or larger.

Falsify the scoped hypothesis if `J` vanishes on all prime-to-`p` torsion through the
exhaustive boundary, changes under an admissible lift, fails one exact additivity check,
or coordinate extraction requires a lower 95% exponent `>=0.50`. A lift implementation
failure is not mathematical evidence.

## Artifact plan

- Planned specification: `ideas/artifacts/ECDLP-IDEA-004/preflight_spec.yaml`
- Planned derivation: `ideas/artifacts/ECDLP-IDEA-004/jet_cocycle.md`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-004/jet_log_preflight.sage`
- Planned runs: `ideas/artifacts/ECDLP-IDEA-004/runs/<run-id>/`
- Planned lift-choice data: `ideas/artifacts/ECDLP-IDEA-004/runs/<run-id>/lifts.jsonl`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-004/analysis.md`

## Interpretation boundary

This is a high-risk, toy, heuristic, model-bound, novelty-unverified hypothesis. Passing
the anomalous control is expected and says nothing about generic curves. Even a correct
ordinary toy coordinate must clear lift invariance, explicit-module, full-cost, scaling,
and independent-review gates before any cryptanalytic claim.

## Exactly one next executable action

1. Derive and exhaustively evaluate the order-one lift-error cocycle on the preregistered anomalous and ordinary 10–18-bit control curves.
