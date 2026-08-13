# ECDLP-IDEA-434 — Isogeny-class variation of Semaev decomposition yield

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `representation-changing`
- State: `proposed_unapproved_pending_review`
- Cohort: `20260809-a`
- Evidence scale: primary-literature motivation only; no experiment ran
- Contract posture: `review_required` and unapproved; the contract permits zero runs
- Scale labels: any computation is `toy`; every cost claim is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**. A yield difference between isogenous curves is a preprocessing constant, not an exponent change, and not an ECDLP break.

## Falsifiable hypothesis

Fix `p`, a trace `t`, and the resulting group order `N = p + 1 - t`. Let `C_t` be the
set of curves `E/F_p` in that `F_p`-isogeny class, all with the same group order and
(for ordinary `E`) the same endomorphism-algebra `Q(sqrt(t^2-4p))`. Fix one *canonical*
factor base rule applied identically to every curve — the `x`-coordinate interval
`{P : x(P) ∈ [0, B)}` for a fixed `B` — and fix `m`.

**H:** the mean `m`-th Semaev decomposition yield

```
Y(E, B, m) = Pr_{R ∈ E(F_p)} [ R decomposes as a sum of m factor-base points ]
```

is **not** constant on `C_t`; it varies across the isogeny class by a factor that
grows with `p`.

The null (`H0`) is that `Y` is an isogeny-class invariant up to sampling noise.

## Mechanism-new operation

The operation is **curve selection inside a fixed isogeny class as a preprocessing
step for relation collection**. This is not a factor-base geometry change and not a
change of group: the group order, and for ordinary curves the `F_p`-endomorphism ring
up to the volcano level, are held fixed while the *defining equation* moves along
`ell`-isogenies. `KN-FIND-007` established decomposition-yield conservation — factor-base
geometry cannot change mean yield, only redistribute it — but it was established
**at fixed curve**. Whether conservation extends across the isogeny class is a
different, unmeasured axis.

The motivation is `KN-LIT-39d9ed`: in genus 3 an isogeny moves a DLP between two
moduli strata with *different index-calculus exponents*, `Õ(q^{4/3})` and `Õ(q)`. The
genus-1 analogue of "different stratum" cannot be a different plane-model degree
(`KN-TECH-3b593f`, `KN-LIT-a45b7b` pin it at 3), so the only surviving analogue is a
difference in decomposition statistics at fixed model degree. That is exactly what
this measures.

## Assumptions

1. `E/F_p` ordinary, `N = #E(F_p)` prime or with a known large prime factor; `p`, `t`,
   `B`, `m`, the factor-base rule, and the RNG seeds are frozen before any run.
2. The isogeny class is enumerated by small-`ell` walks (Vélu) with the volcano level
   recorded, so "same class" is meaningful and the crater/level of each curve is a
   logged covariate rather than a confounder.
3. The factor-base rule is applied *identically* on every curve; any per-curve tuning
   of `B` or of the coordinate makes the comparison a factor-base-geometry experiment
   and is forbidden here.
4. Yield is estimated by the exact fibering method of `KN-FIND-008`, not by ambient
   sampling, so the estimator's resolution floor is known in advance and a null result
   is not an artefact of `1/N_samples`.
5. Isogeny-walk cost, curve-enumeration cost, and the cost of transporting the ECDLP
   instance along the isogeny are charged in full against any claimed benefit.
6. A measured yield ratio is a **constant-factor** claim unless the ratio is shown to
   grow with `p` across at least three well-separated `p`; only growth touches an exponent.

## Semantic fingerprint

`fixed_isogeny_class | fixed_group_order | canonical_factor_base_rule | decomposition_yield_measurement | curve_selection_preprocessing`

Changing `B`, the coordinate, the curve model (Edwards/Montgomery), or the symmetry
group is a **control**, not this mechanism — those are `KN-OPEN-003` and are already
covered by `KN-FIND-007`.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — `KN-FIND-007`, decomposition-yield conservation at fixed curve; this record extends that conservation claim along the isogeny-class axis.
2. `inputs/ledger_inventory.json` — `KN-OPEN-003`, do curve representations/symmetries reduce decomposition cost over prime fields; adjacent axis, representation at fixed curve.
3. `inputs/ledger_inventory.json` — `KN-OPEN-001`, does index calculus beat Pollard rho for prime-field ECDLP.
4. `inputs/ledger_inventory.json` — `KN-FIND-a1f3c2`, Semaev summation monodromy is universally `C_2^{m-2}` with no exceptional locus; the strongest prior against the hypothesis.
5. `inputs/ledger_inventory.json` — `KN-FIND-009`, endomorphism-augmented witness-lattice degeneracy is governed by short eigenvalue relations, not by `rank End(E)`.

## Closest primary literature

- Smith, [Isogenies and the Discrete Logarithm Problem in Genus Three](https://www.lix.polytechnique.fr/~smith/), ECC 2007 (`KN-LIT-39d9ed`) — isogeny as an exponent-moving representation change, in genus 3.
- Diem, [Index Calculus in Class Groups of Plane Curves of Small Degree](https://www.math.uni-leipzig.de/~diem/), ECC 2007 (`KN-LIT-a45b7b`) — the exponent is a function of plane-model degree, which is why the genus-1 analogue must be sought in decomposition statistics rather than in degree.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the decomposition-yield definition used here.

No checked primary source reports this measurement for prime-field ECDLP in the form
proposed here; novelty remains `novelty-unverified`.

## Complete factor-base-to-target-descent path

1. Freeze `p`, `t`, `B`, `m`, the factor-base rule, the estimator, and seeds.
2. Enumerate `C_t` by small-`ell` isogeny walks; record `j`-invariant, volcano level,
   and the `ell`-path for each curve.
3. For every curve compute `Y(E, B, m)` by exact fibering (`KN-FIND-008` method), with
   the closed-form expected count recorded before the run.
4. Test `H0` by the pre-registered statistic across the class, stratified by volcano level.
5. Repeat at three well-separated `p` and fit the growth of the max/min yield ratio.
6. If and only if the ratio grows: cost the full pipeline — enumerate, select the best
   curve, transport the instance along the isogeny, run relation collection — and
   report the end-to-end exponent against rho and BSGS.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time with constant state; BSGS costs `N^(1/2+o(1))` time and
memory. With `B = N^beta`, let isogeny-class enumeration and selection cost `N^s, N^s_m`;
per-curve yield evaluation cost `N^v`; the reciprocal decomposition yield of the
*selected* curve be `N^delta`; one relation trial cost `N^q, N^q_m`; and the linear
algebra on the relation matrix cost `N^ell, N^ell_m`. Then

`lambda = max(s, v, beta + delta + q, ell, beta)`

`mu = max(s_m, beta, q_m, ell_m)`.

These are the complete time and peak-memory exponents. Note `s` includes enumerating
the class, which is why a constant-factor yield gain cannot pay for itself.

## Likely fatal obstruction

`KN-FIND-a1f3c2` and `KN-FIND-a8990a` report that the summation cover's monodromy is
`C_2^{m-2}` in every characteristic with no exceptional locus, and that the factor-base
locus lies entirely in the totally split part. If yield is controlled by that structure,
it is a function of `(p, B, m)` and not of the curve, and `H0` holds. The most likely
outcome of this experiment is therefore a **negative result that strengthens
`KN-FIND-007` into an isogeny-class invariance statement** — which is the reason to run
it cheaply rather than the reason not to run it.

## Proof track

Prove `Y(E, B, m)` depends only on `(p, B, m)` and the isogeny class, i.e. derive
yield from summation-cover splitting statistics that are class-determined. That would
convert `KN-FIND-007` into a two-axis conservation theorem and close curve selection
as a preprocessing route permanently.

## Disproof track

Exhibit two `F_p`-isogenous curves with a yield ratio bounded away from 1 and growing
with `p`, with the volcano level controlled and the estimator's resolution floor
cleared.

## Positive and negative controls

- Positive: two curves in *different* isogeny classes with different `N`, where yield
  differences are expected and calibrate the estimator's sensitivity.
- Negative: the same curve under two different Weierstrass models (`KN-OPEN-003`
  territory) — must reproduce `KN-FIND-007` conservation.
- Estimator control: known closed-form counts per `KN-FIND-008` before any sampling.
- Baselines: rho and BSGS on every instance; a random-curve control drawn outside `C_t`.

## Quantitative promotion and falsification gates

Remains proposed and unapproved. A later approved toy preflight requires: pre-registered
statistic and resolution floor; volcano level logged; at least three `p`; and an
explicit growth fit. A constant-factor yield ratio, or any ratio not clearing the
estimator floor, falsifies this version and promotes the `KN-FIND-007` extension instead.
No outcome here is an exponent claim.

## Artifact plan

- Yield estimator specification reusing the `KN-FIND-008` fibering method: `ideas/artifacts/ECDLP-IDEA-434/yield_estimator_spec.md`
- Isogeny-class enumerator with volcano-level logging: `ideas/artifacts/ECDLP-IDEA-434/isogeny_class_enumerator.py`
- Pre-registration of the statistic, resolution floor, and seeds: `ideas/artifacts/ECDLP-IDEA-434/preregistration.md`
- Cost receipt charging enumeration and instance transport: `ideas/artifacts/ECDLP-IDEA-434/cost_analysis.md`

All artifact paths are prospective; no experiment ran.

## Interpretation boundary

Conservative, novelty-unverified, toy. The realistic best case is a bounded constant
factor in relation collection, which does not touch the exponent and is not a break.
The realistic expected case is a negative result that strengthens an existing internal
finding.

## Exactly one next executable action

1. Independent review of whether `KN-FIND-a1f3c2` / `KN-FIND-a8990a` already *determine*
   `Y` as a class invariant on paper. If they do, convert this record to a derivation
   task and do not run anything; if they do not, specify the pre-registered statistic
   and the smallest `p` triple that clears the estimator floor.
