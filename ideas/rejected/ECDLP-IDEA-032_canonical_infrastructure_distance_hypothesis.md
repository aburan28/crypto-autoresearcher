# ECDLP-IDEA-032 — Canonical infrastructure distance

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct birational model, reduced ideal, or infrastructure relation is not an ECDLP break.

## Falsifiable hypothesis

For a generic prime-field curve `E/F_p` with a public prime-order subgroup
`<P>` of order `N=p^(1+o(1))`, there is a deterministic, target-independent
conversion to a genus-one real quadratic function-field model with two rational
infinite places, together with a certified algorithm that reads an **absolute
infrastructure distance** from a reduced `f`-representation without walking the
regulator cycle.  After a public normalization, that distance is additive on
`<P>` and therefore turns `Q=[x]P` into one linear congruence whose construction,
period computation, ambiguity resolution, and bit memory all have exponent
strictly below `1/2` in `N`.

The claim is not that an elliptic curve has a quartic or reduced-ideal model; that
equivalence is known.  The falsifiable new claim is direct extraction of a
canonical absolute distance that is both scalar-readable and cheaper than the
infrastructure DLP.

## Mechanism-new operation

Choose, using only `(E,P,N)`, a birational quartic model
`C: v^2=f_4(u)` with two ordered rational infinite places `infinity_+` and
`infinity_-`.  Map `[R]-[O]` to a reduced real-quadratic ideal and its canonical
`f`-representation.  Apply a proposed **absolute-distance normalization**
`Delta` that combines the reduced ideal, continued-fraction correction, and
certified regulator origin to return an element of `Z/Rcal Z` satisfying

`Delta(A+B)=Delta(A)+Delta(B)`

on the image of `<P>`, without enumerating the infrastructure cycle or storing a
scalar-indexed table.  Recover `x` from `Delta(Q)=x*Delta(P) mod Rcal`.

A mere Weierstrass-to-quartic conversion, ordinary ideal reduction, alternative
continued-fraction implementation, or coordinate speedup is a duplicate of the
closed representation lane and must be merged with `H-REP-001` as a negative
control.  This idea survives only if the absolute-distance operation is proved
and bypasses the known equivalence between the two DLPs.

## Assumptions

1. `E(F_p)` contains the public subgroup `<P>` of known prime order `N`, with `Q=[x]P` and `N=p^(1+o(1))`.
2. The ordered two-infinity model and maps in both directions are deterministic, public, independent of `Q` and `x`, and succeed on a measured positive density of generic curves.
3. The infrastructure origin, regulator `Rcal`, distance corrections, and all unit data are certified without a hidden discrete-log oracle.
4. `Delta` is well defined on equivalent reduced representatives and is additive and nonzero on `<P>`; every failure or normalization branch is retained.
5. The congruence leaves at most `N^(u+o(1))` candidates and every candidate is checked on the original curve.
6. Model construction, regulator work, continued fractions, coefficient sizes, bit operations, tables, and failed instances are charged; scaling claims remain toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`two_infinity_genus_one_function_field | reduced_f_representation | certified_absolute_infrastructure_distance | additive_scalar_congruence | avoids_regulator_cycle_walk`

## Five closest ledger entries

1. `ledger/H-REP-001.yaml` — prevents a quartic or reduced-ideal representation alone from being called a new mechanism.
2. `ledger/EV-REP-001.yaml` — supplies the verified coordinate-model and branch-accounting control.
3. `ledger/DEC-20260716-001.yaml` — requires any representation follow-up to remove the measured obstruction rather than repeat a model variant.
4. `ledger/FINDING-PF-IC-001.md` — supplies the complete rho, target-descent, and memory comparison boundary.
5. `ledger/SYNTHESIS-20260716.md` — requires end-to-end scalar recovery and independent verification before promotion.

## Closest primary literature

- Paulus and Rück, [Real and imaginary quadratic representations of hyperelliptic function fields](https://doi.org/10.1090/S0025-5718-99-01066-2), develops the relevant reduced ideal representations.
- Stein, [Equivalences between elliptic curves and real quadratic congruence function fields](https://doi.org/10.5802/jtnb.191), establishes the nearby genus-one DLP equivalence and is therefore the principal circularity boundary.
- Fontein, [The infrastructure of a global field of arbitrary unit rank](https://arxiv.org/abs/0809.1685), formalizes infrastructures and `f`-representations as group-like computational objects.

These sources establish the representation and infrastructure machinery, not a
sub-square-root absolute-distance readout.  This proximity check is not an
exhaustive novelty search; novelty remains unverified.

## Complete factor-base-to-target-descent path

Here the replacement for a factor base is a certified infrastructure origin and
period coordinate; there is no relation-collection phase.

1. Freeze `(E,P,N)`, construct the ordered two-infinity model `C`, and certify the birational maps and Jacobian identification with `E`.
2. Construct the reduced-ideal arithmetic, canonical `f`-representation rules, infrastructure origin, regulator `Rcal`, and correction law without using `Q`, `x`, or a scalar table.
3. Map `[P]-[O]` and `[Q]-[O]` independently to reduced `f`-representations and retain every normalization branch.
4. Compute certified absolute distances `d_P=Delta(P)` and `d_Q=Delta(Q)` directly from those representations, verifying representative independence and the public addition law.
5. Solve `d_P*X=d_Q mod Rcal`, retain all solutions induced by `gcd(d_P,Rcal)` and normalization ambiguity, and reject the instance if the list exceeds its preregistered bound.
6. Map every surviving integer to `Z/NZ` and accept only the unique `x` satisfying `[x]P=Q` on the original `E/F_p`.

## Full rho/BSGS cost model

Let reciprocal model-applicability density be `N^zeta`; model and birational-map
construction cost `N^c`; coefficient/field representation overhead `N^phi`;
infrastructure and regulator construction `N^r`; reduced-representative cost
`N^kappa`; direct absolute-distance extraction `N^a`; congruence work `N^q`;
residual candidate count `N^u`; per-list verification contribution `N^v`; and
other bit storage `N^s`.  These are total bit-operation and bit-memory exponents,
not uncharged field-operation labels.

- Pollard rho: `N^(1/2+o(1))` time and negligible memory.
- BSGS: `N^(1/2+o(1))` time and `N^(1/2+o(1))` memory.
- Proposed time exponent:
  `lambda=max(zeta+c,phi,r,kappa,a,q,u+v)`.
- Proposed bit-memory exponent:
  `mu=max(s,phi,u)`.

All continued-fraction steps, regulator traversal, unit representations,
certificates, failed model attempts, and any origin table are included.  An
`N^(1/2-o(1))` regulator walk, absolute-distance search, candidate list, or table
kills promotion even if ideal reduction itself is polynomial time.

## Likely fatal obstruction

In a real quadratic infrastructure, the reduced ideal gives a location only up
to the same global distance problem that defines the infrastructure DLP.  Local
continued-fraction reductions expose relative corrections, not a free absolute
coordinate.  The known genus-one equivalence strongly suggests that determining
`Delta(R)` from a point is exactly as hard as determining its elliptic discrete
logarithm; alternatively the regulator coordinate may be nonadditive, trivial on
`<P>`, or computable only after an order-`N` walk or table.

## Proof track

Construct the target-independent model and `Delta`, prove representative
independence and exact additivity on `<P>`, prove `Delta(P)` generates an
`N`-divisible component of `Z/Rcal Z`, give certificates for `Rcal` and every
correction, and bound all terms in `lambda` and `mu` strictly below `1/2` without
an infrastructure walk or scalar-indexed preprocessing.

## Disproof track

Reduce absolute-distance extraction to the elliptic or infrastructure DLP; prove
that the distance projection is nonadditive or has trivial kernel/image on the
prime-order subgroup; exhibit model-dependent origins that cannot be normalized
without knowing a logarithm; or show that regulator, walk, table, ambiguity, or
bit-size exponent is at least `1/2`.

## Positive and negative controls

- Positive instrumentation control: synthetic cyclic infrastructures whose absolute distances and regulator are planted and hidden from the extraction code.
- Positive correctness control: exhaustive prime-order curves small enough to enumerate every point and every reduced representative after the run.
- Representation control: several independently chosen quartic models of the same `(E,P)` plus the ordinary Weierstrass representation.
- Negative algorithmic control: standard baby-step/giant-step in the infrastructure with its full walk and memory charged.
- Circularity control: dependency tracing rejects use of known logs, scalar-indexed tables, target-selected origins, or exhaustive infrastructure positions.
- Genericity control: ordinary random prime-order curves are reported separately from curves selected for unusually small regulator or coefficients.

## Quantitative promotion and falsification gates

Use at least 100 generic prime-order curves per size from 10 through 26 bits, with
three deterministic two-infinity constructions where available.  Promotion to a
larger scaling experiment requires all of the following:

- zero incorrect scalar outputs and zero uncertified regulator or birational-map outputs;
- model success on at least 90% of preregistered generic instances at each of the two largest sizes;
- exact additivity on every exhaustive small instance and at least 10,000 held-out random additions, with identical normalized distances across all valid models;
- no origin walk or table larger than `N^0.20`, and upper 95% bounds `r<=0.30`, `a<=0.35`, `u<=0.10`, `lambda<=0.45`, and `mu<=0.45`;
- an explicit proof that the extraction code never queries or reconstructs an infrastructure DLP through its certificates.

Falsify the scoped hypothesis if `Delta` is not well defined and additive, is zero
on the subgroup, changes irreconcilably with the model, requires a known scalar,
or if the lower 95% bound for any complete time or bit-memory bottleneck reaches
`0.50`.  Inability to implement a certified model is infrastructure failure, not
by itself a mathematical negative.

## Artifact plan

- Planned contract: `ideas/contracts/ECDLP-EXP-CONTRACT-032_infrastructure_distance_preflight.yaml`
- Planned specification: `ideas/artifacts/ECDLP-IDEA-032/preflight_spec.yaml`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-032/infrastructure_distance.sage`
- Planned instance manifest: `ideas/artifacts/ECDLP-IDEA-032/instances.jsonl`
- Planned runs: `ideas/artifacts/ECDLP-IDEA-032/runs/<run_id>/`
- Planned distance certificates: `ideas/artifacts/ECDLP-IDEA-032/runs/<run_id>/distance_certificates.jsonl`
- Planned cost fits: `ideas/artifacts/ECDLP-IDEA-032/runs/<run_id>/costs.tsv`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-032/analysis.md`

## Interpretation boundary

This proposal is toy, heuristic, model-bound, conservative, and
novelty-unverified.  A valid quartic conversion, reduced ideal, regulator, or
additive identity on planted data is not a breakthrough.  Without certified
absolute-distance extraction and complete generic scalar recovery below both
rho and BSGS in time and bit memory, the result is only a representation control
and must be merged with the occupied representation lane.

## Exactly one next executable action

1. Implement the exhaustive 10–18-bit two-infinity conversion and reduced-ideal preflight, then test whether absolute distance can be recovered from each canonical `f`-representation without an infrastructure walk or known-log table.
