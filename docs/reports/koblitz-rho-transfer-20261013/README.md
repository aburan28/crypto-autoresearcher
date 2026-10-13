# Koblitz rho incumbent and isogeny-transfer search

Date: 2026-10-13
Base revision: `387dd4aeba486c198913fbecc45661b6a26f8cb5`

Status: **evidence integration and derived consistency audit.** No new rho
trial, cryptographic-size solve, explicit K-163/K-283 transfer map, sealed
bound, or weak-endpoint claim was produced in this round.

## Outcome

The user's significance assessment is correct. On a NIST Koblitz subgroup,
the usable signed-Frobenius action reduces the random-map rho expectation by
`sqrt(m)` relative to the same curve's negation-only rho. That is 3.674 to
4.579 bits, or 12.77x to 23.90x fewer expected transitions, from K-163 through
K-571. This is not a rounding detail and must be the incumbent for every
isogenous-endpoint comparison.

The result does **not** establish a new weak isogenous representative. Two
existing standalone studies already test the mechanism at `m=37` and `m=41`:
the reductions broadly track `sqrt(m)`, but only the `m=41` confidence interval
contains the model value. The `m=37` estimate is about 5.8% below `sqrt(37)` and
its 90% interval excludes the model. Orbit handling reduces the wall-time gain.
In both studies, sampled lower conductor levels were negation-only and none
beat the Koblitz crater with native Frobenius. Those studies are substantial
archived observations, but they explicitly are not ledger evidence or sealed
measured bounds.

The genuinely new route is therefore not another blind isogeny search or toy
rho implementation. It is:

1. preserve and certify one explicit vertical map and dual, first on the
   existing `m=37`, degree-73 proxy;
2. compare one-time endpoint-to-Koblitz transfer against any action transported
   through the map at every walk step;
3. only then persist a K-163 degree-45641 kernel/map and extend the comparison
   to a named NIST subgroup.

## What was checked

The deterministic tool [`audit.json`](audit.json) consumes the archived
[NIST endomorphism sweep](../../../research/endosweep_nist_20261006/nist.json),
binds its SHA-256 digest, trusts its point/action check booleans, and
independently recomputes:

- the subgroup order from `N(delta)`;
- the trace/order/cofactor relation;
- `lambda^2-mu lambda+2 = 0 (mod r)`;
- `lambda^m=1` and, because each `m` is prime and `lambda!=1`, exact action
  order `m`;
- signed orbit order `2m`, conditional on the archived prime-subgroup identity;
- all three random-map expectations and the conditional endpoint crossover.

It uses `sympy.isprime` as a strong prime screen but emits no primality
certificate and does not replay the archived point arithmetic. Its scope is
therefore a derived consistency audit, not independent reproduction. The
human-readable table is [`audit.md`](audit.md).

| curve | gain beyond negation (derived bits) | transitions factor | conditional negation-only endpoint step-cost ceiling |
|:--|--:|--:|--:|
| K-163 | 3.674364 | 12.767145x | 7.8326% |
| K-233 | 3.932093 | 15.264338x | 6.5512% |
| K-283 | 4.072329 | 16.822604x | 5.9444% |
| K-409 | 4.337979 | 20.223748x | 4.9447% |
| K-571 | 4.578673 | 23.895606x | 4.1849% |

The ceiling is conditional: it applies only if negation is the endpoint's best
usable quotient. It is the maximum endpoint cost per effective transition,
relative to one fully charged native signed-Frobenius transition, that could
offset the lost orbit quotient before setup or transfer. It is not evidence
that a floor actually meets the ceiling.

## Existing measured proxy evidence

These are earlier measurements, not new runs in this PR.

- **[`m=37` study](../../../research/isogeny_volcano_rho_20261005/README.md):**
  5,000 crater-negation and 5,000 signed-Frobenius
  solves, with 136,000 verified solves across the full study. It measured
  5.73x fewer steps (90% CI [5.62, 5.84]) versus `sqrt(37)=6.08`, and a
  2.78x--2.99x wall-time gain because a Frobenius step cost 2.16x as much.
- **[`m=41` replication](../../../research/isogeny_volcano_rho_m41_20261006/README.md):**
  3,000 solves in each crater arm and 24,000 verified
  solves across the full study. It measured 6.36x fewer steps (95% CI
  [6.20, 6.53]) versus `sqrt(41)=6.40`, and about a 3.0x wall-time gain.

Both are standalone studies, not ledger evidence or sealed measured bounds.

Both studies also compared sampled conductor levels with the same solver and
group. Their lower levels were statistically equivalent to crater
negation-only steps within the studies' declared margins, and no tested curve
beat crater plus native Frobenius. This is bounded evidence at `m=37,41`, not
a theorem or measurement at K-163.

The quantitative view [`rho-discount.svg`](rho-discount.svg) separates the
derived NIST factors from the archived proxy measurements. Its editable source
is [`plot.py`](plot.py).

![Derived NIST discounts and archived proxy measurements](rho-discount.png)

## Transfer logic: the control that matters

Let `phi:E->E'` have degree `d` coprime to subgroup order `r`, where `E` is
the Koblitz representative. On the endpoint subgroup one can test

`T = [d^(-1) mod r] o phi o tau o dual(phi)`.

If all constituents are defined, this is a global morphism, while the proved
automorphism property concerns its restriction to the selected subgroup. It
is not the degree-preserving rational conjugate `phi tau phi^(-1)` and is not
an automorphism of the ambient curve.

But `T` may be the wrong operational strategy. For an ECDLP supplied on `E'`,
the attacker can map the generator and target through the dual once, solve on
`E` with native signed Frobenius, then recover and verify on `E'`. A per-step
transported action must beat this one-time transfer route. Conversely, an
ECDLP already supplied on the Koblitz source stays there unless the endpoint
has a separately cheaper complete attack.

The diagram [`transfer-gates.svg`](transfer-gates.svg), from editable
[`transfer-gates.dot`](transfer-gates.dot), marks verified structure, model
comparisons, and missing maps separately.

![K-163 vertical-transfer decision graph](transfer-gates.png)

## Vertical and horizontal paths by family

### K curves

The named K curves have `D_K=-7`, explicit native `tau`, and `f_E=1`; their
large `f_pi` records the index of `Z[pi]`, not an automatic ECDLP discount.
The maximal order has class number one, so its horizontal class action is
trivial up to isomorphism. Horizontal cycles on nonmaximal floors are a
different question and were not searched here for advantageous endpoint
predicates.

- K-163 has archived endpoint-producing conductor-45641 and conductor-82153
  constructions. The archive retains endpoint coefficients and level checks,
  but no replayable point map, kernel polynomial, dual, exceptional set, or
  subgroup transfer certificate.
- K-283 has a conductor-1697 census implementation whose own README says it
  has not been executed through the canonical run entry point and constructs
  no source-to-floor map.
- An endpoint coefficient outside `F_2` makes absolute Frobenius a map to a
  conjugate curve, not a native endpoint self-action. The conjugate orbit alone
  does not grant a `sqrt(m)` quotient to a walk on one endpoint.

The precise missing-map obligation is tracked in
[`problems/koblitz-vertical-isogeny-maps-not-persisted.md`](../../../problems/koblitz-vertical-isogeny-maps-not-persisted.md).

### P curves

The archived NIST sweep has `f_pi=1` for P-192, P-256, P-384 and P-521, so
there are no conductor-changing vertical edges in those classes. P-224 has
`f_pi=3`. Current code enumerates its four rational degree-3 kernels and
codomains but does not implement a point evaluator, dual, subgroup recovery,
or graph closure. That blocker is recorded separately in
[`problems/p224-degree3-point-maps-not-certified.md`](../../../problems/p224-degree3-point-maps-not-certified.md).

This does not erase ordinary parameter-size conclusions: P-192 has roughly a
96-bit generic group-work exponent, and P-224 roughly 112 bits, before a
declared success constant. Whether that is called weak depends on the frozen
threshold; it is not evidence of a special isogenous representative.
For P-192/P-256/P-384/P-521, `f_pi=1` closes only the vertical conductor axis;
horizontal class-group walks and representative-specific endpoint predicates
remain open and were not enumerated in this round. P-224 likewise still needs
its degree-3 component and horizontal/descending edge labels certified.

### B curves

The archived sweep has `f_pi=1` for B-163, B-233, B-283 and B-409, excluding
conductor-changing vertical edges. B-571 remains unresolved in that artifact.
The B curves do not inherit a native Koblitz `tau` action merely because they
share a binary field degree. They are useful same-field/null controls, not
surrogates for the K curve baseline.
For B-163 through B-409, `f_pi=1` excludes conductor-changing vertical edges
but does not exclude horizontal class-group moves. No horizontal endpoint
search was performed here; B-571 remains unresolved even on the conductor
axis in the archived sweep.

### sect113r1

sect113r1 is not a speculative isogeny weakness: a published FPGA computation
already solved its ECDLP, as summarized by `KR-RHO-2480c6`. Its approximately
113-bit subgroup gives only about a 56-bit generic square-root scale. It is a
published solved target; a `weak` verdict still requires a declared threshold
that exceeds the reported attack cost. Under such a threshold the cause is
class-wide subgroup size, not a newly discovered conductor endpoint. This
round did not perform a new sect113r1 run or freeze that threshold.

## Confidence and verdict gates

Algebraic identities need exact certificates, not p-values. Runtime and walk
claims need paired evidence. The accompanying protocol requires identical
targets/seeds and randomized blocks, retains failures and timeouts, and uses
paired bootstrap intervals; multi-endpoint claims require hierarchical
resampling and multiplicity correction. Full-size NIST runs can measure fixed
walk/canonicalization/map throughput, but cannot be reported as completed
ECDLP solves.

The labels remain:

- exact orbit/action plus formulas: usable structural rho discount;
- one endpoint with a fully charged below-threshold attack:
  `WEAK_REPRESENTATIVE_EXISTS`;
- a complete below-threshold map/solve/recovery path from the named source:
  `SOURCE_TRANSFER_WEAK`;
- uniform public coverage or a certified class invariant: `CLASS_WEAK`;
- bounded null results only: `NO_WEAKNESS_FOUND_WITHIN_SCOPE`;
- missing maps, failed controls, or excessive censoring: `INDETERMINATE`.

No new weak-curve label is assigned to a NIST K/P/B isogenous endpoint here.
sect113r1 is a published solved target and would qualify under a declared
threshold above the reported attack cost; this threshold-free report assigns
it no new verdict.

## Next experiment

Use the protocol in
`docs/experiments/koblitz-isogeny-rho-transfer.md`. The first implementation
target should be the existing `m=37` degree-73 edge, not K-163:

1. modify the endpoint-producing GP path to retain a map/kernel witness;
2. construct and verify the dual and both compositions;
3. verify subgroup preservation and planted-log recovery;
4. compare one-time transfer, native source `tau`, endpoint negation, and the
   transported-action diagnostic;
5. only after those gates pass, persist the K-163 degree-45641 kernel and add a
   big-integer rho/transition backend.

Any new quantitative advantage requires a matched `claims/*.json` record and
independent verification. This report deliberately creates no such claim from
model arithmetic or the unpromoted standalone studies.

## Sources and limits

Primary internal artifacts inspected:

- `research/endosweep_nist_20261006/nist.json` and its report;
- `experiments/EXP-BINSTD-7100ec/stage0/c2-rho-table.json` and its reviewed
  C2/C3 arithmetic;
- the linked `m=37` and `m=41` full-volcano rho study directories;
- `research/ecc2k130_conductor_isogenies_20261007/`;
- `tools/isogeny_class_screen.py` and its tests;
- `knowledge/frontiers/ecdlp/generic-rho/KR-RHO-2480c6.yaml`.

This search did not independently reopen every primary publication, replay
the standalone raw solves, execute the K-283 census, produce an explicit map,
or run a horizontal predicate search across the P/B classes or nonmaximal K
floors. The report preserves those boundaries rather than treating absence of
a map or an unsearched horizontal endpoint as absence of a weakness.
