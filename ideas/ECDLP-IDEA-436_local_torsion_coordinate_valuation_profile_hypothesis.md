# ECDLP-IDEA-436 — Coordinate-valuation profile of the canonical prime-to-p torsion lift

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- Top lane: `high-risk`
- State: `proposed_unapproved_pending_review`
- Cohort: `20260809-a`
- Evidence scale: primary-literature and derivation preflight only; no experiment ran
- Contract posture: `review_required` and unapproved; the contract permits zero runs
- Scale labels: any computation is `toy`; every cost claim is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**. A non-constant `p`-adic profile is not a scalar recovery and not an ECDLP break.

## Falsifiable hypothesis

Face **F2** of the lifting taxonomy (`KN-TECH-06bb4e`) is the canonical lift of
`S ∈ E(F_p)` of prime-to-`p` order `n` to the unique `Ŝ ∈ E(Q_p)` of the same order.
`KN-TECH-73630e` closes F2 for every **group-theoretic** invariant: reduction restricted
to prime-to-`p` torsion is a group isomorphism, so the lifted instance *is* the original
instance. It explicitly leaves open the non-group-theoretic case (`KN-OPEN-3417fc`).

**H:** there is a coordinate/valuation functional on `<Ŝ>` — concretely a member of the
frozen family

```
inv_j,r(k) = v_p( x([k]Ŝ) - x([j]Ŝ) )   truncated at precision r,
```

or a fixed statistic of the precision-`r` coordinate digits of `[k]Ŝ` — that is
non-constant in `k`, **efficiently invertible**, and whose evaluation precision `r`
grows slowly enough that recovering `x` from `Q = [x]P` costs less than `n^{1/2}`
end-to-end, including all precision and query costs.

The null is that every member of the frozen family is either constant in `k`, or has
inversion cost times query count at or above `n^{1/2}`.

## Mechanism-new operation

The operation is **valuation-profile digit extraction from a canonical `p`-adic torsion
lift**. It is not a formal logarithm: no map into the formal group is taken, and the
annihilation `Ô = mÔ` that closes the classical F2 route is never performed. It is not
a ramification-filtration invariant: `ECDLP-IDEA-160` closed functorial towers and upper/lower
ramification breaks, and a valuation of a coordinate *difference* on a fixed curve over a
fixed field is neither a tower invariant nor a break number.

What survives from `KN-TECH-73630e` is a hard boundary that this record accepts up front:
the lift is **information-theoretically empty**, because `Ŝ` is a deterministic Hensel
function of `S`. So the only thing that can be claimed here is a *computational* handle —
that the `p`-adic presentation makes some separation cheap that is expensive in `F_p`. Any
version of this idea that claims new information is already refuted.

## Assumptions

1. `E/F_p` ordinary with good reduction, `p >= 3`, `n = ord(S)` with `gcd(n,p) = 1`;
   `E`, `P`, `n`, `Q`, the lift, the precision schedule, the functional family, and all
   seeds are frozen before any run.
2. The lift is target-uniform and scalar-blind: `Ŝ` is computed from `S` alone by Hensel
   lifting plus the order condition, using no torsion basis, orientation, or advice that
   depends on `x`.
3. The functional family is fixed in advance. Post-hoc selection of `(j, r)` after seeing
   the scalar is forbidden advice and scores zero.
4. Every evaluation charges its precision: `p`-adic arithmetic at precision `r` costs at
   least `r` limbs, and `r` is reported per query, not amortised away.
5. Inversion ambiguity is charged. A profile that narrows `k` to a set must charge the
   enumeration of that set and verify each candidate by `[x]P = Q`.
6. The `H`-claim is computational only; no information-gain claim is made or permitted.

## Semantic fingerprint

`canonical_prime_to_p_torsion_lift | coordinate_valuation_profile | no_formal_group_map | computational_only_handle | verified_full_scalar_recovery`

Changing precision, `p`-adic library, or lift shape is a **control**. Mapping into the
formal group at any point exits this mechanism and re-enters the closed classical F2 route.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — `KN-TECH-73630e`, face F2 is closed for group-theoretic invariants by an isomorphism argument; the direct parent of this record.
2. `inputs/ledger_inventory.json` — `KN-OPEN-3417fc`, the open coordinate-invariant question this record makes falsifiable.
3. `inputs/ledger_inventory.json` — `ECDLP-IDEA-004`, prime-to-p jet logarithm; distinct because that route is additive and killed by the annihilation this record never performs.
4. `inputs/ledger_inventory.json` — `ECDLP-IDEA-160`, nonlogarithmic ramification-break scalar digits; distinct because this record uses no tower.
5. `inputs/ledger_inventory.json` — `KN-FIND-002`, jet and endomorphism oracles are GGM-simulable with `O(1)` overhead; the gate this record must clear.

## Closest primary literature

- Silverman, [The Four Faces of Lifting for the Elliptic Curve Discrete Logarithm Problem](https://www.math.brown.edu/johsilve/), ECC 2007 (`KN-LIT-6935a1`) — isolates face F2 and states that no efficient method is known to solve ECDLP in `E(Q_p)` without moving into the formal group.
- Silverman, [The Arithmetic of Elliptic Curves](https://doi.org/10.1007/978-0-387-09494-6), formal-group and good-reduction chapters — supplies the torsion-freeness of the formal group used by `KN-TECH-73630e`.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://doi.org/10.1007/3-540-68339-9_18) — the generic-group bound the simulability gate is measured against.

No checked primary source reports a scalar-sensitive, efficiently invertible
coordinate-valuation profile on prime-to-`p` torsion lifts; `novelty-unverified`.

## Complete factor-base-to-target-descent path

1. Freeze `E, P, n, Q`, the lift, the precision schedule, the functional family, and the verifier.
2. Prove the lift construction uses no scalar-labelled advice.
3. On **known-scalar** samples `[r]P`, evaluate the frozen family and fit its exact
   transformation law under `[k]`. Fit nothing post hoc.
4. Prove or measure non-constancy in `k` at fixed precision `r`, and measure how `r` must
   grow with `n` to retain non-constancy.
5. Prove a typed inversion with bounded ambiguity: `inv(k) -> ` candidate set of known size.
6. Apply the identical frozen procedure to `Q`, or to a masked `Q + [t]P`.
7. Remove the mask, enumerate the residual candidates, and accept only `x` with `[x]P = Q`.
8. Report precision, per-query cost, ambiguity, attempts, time, and peak memory against
   rho and BSGS.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time with constant state; BSGS costs `N^(1/2+o(1))` time and memory.
Let lift setup cost `N^a, N^a_m`; the precision needed for non-constancy be `r = N^rho_r`,
so one query costs `N^q` with `q >= rho_r`; the reciprocal density of informative queries be
`N^delta`; final ambiguity `N^u`; and reconstruction algebra `N^ell, N^ell_m`. Then

`lambda = max(a, delta + q, ell, u + q)`

`mu = max(a_m, q_m, u, ell_m)`.

These are the complete time and peak-memory exponents. Promotion requires
`lambda, mu <= 0.45`.

## Likely fatal obstruction

Two, either of which is fatal on its own:

- **Precision growth.** Separating `[k]Ŝ` from `[j]Ŝ` `p`-adically requires precision
  comparable to the number of digits that distinguish them; the expected behaviour is
  `rho_r` at or above `1/2`, which alone forces `lambda >= 1/2` before any density term.
- **GGM simulability.** By `KN-FIND-002` the closely related jet family is GGM-simulable
  with `O(1)` overhead. If the valuation profile is likewise simulable from generic group
  operations, it is closed at exponent `1/2` by `KN-FIND-b7e091`-style argument without
  any experiment. **This must be checked first.**

## Proof track

Exhibit one frozen functional, prove a non-constant scalar transformation law that does
not factor through any additive map killed by `n`, prove non-simulability in the generic
group model, bound `rho_r` strictly below `1/2`, and give a typed reconstruction with
`lambda, mu <= 0.45`.

## Disproof track

Prove the family is GGM-simulable; or prove every member is constant on `<Ŝ>`; or prove
`rho_r >= 1/2`; or derive either complete exponent at or above `0.5`.

## Positive and negative controls

- Positive: a curve and `n` where a *known* `p`-adic separation exists (e.g. anomalous
  `#E(F_p) = p`, where the Smart/SSSA attack applies) — the instrument must detect it.
  This case is explicitly outside the ordinary target regime and is a calibration only.
- Negative: random profiles with the same precision budget and no scalar dependence.
- Advice control: any variant seeded with a torsion orientation, charged as forbidden.
- Baselines: rho, BSGS, known-scalar, and masked-target controls on every instance.

## Quantitative promotion and falsification gates

Remains proposed and unapproved. **The GGM-simulability check is a gate, not a step**: if
the functional family is simulable, this record is rejected without running anything. Past
that gate, a toy preflight requires exact known-scalar prediction on frozen curves, a
measured `rho_r` fit across at least three `n`, zero false digits, complete ambiguity
charging, and formal `lambda, mu <= 0.45`. Constancy, simulability, `rho_r >= 1/2`,
orientation advice, or any exponent at or above `0.5` falsifies this version.

## Artifact plan

- Generic-group simulability gate memo for the valuation-profile family (non-run producer evidence): `ideas/artifacts/ECDLP-IDEA-436/ggm_simulability_gate.md`
- Frozen functional-family and precision schedule: `ideas/artifacts/ECDLP-IDEA-436/profile_spec.md`
- Fixtures and independent verifier: `ideas/artifacts/ECDLP-IDEA-436/fixtures.json` and `ideas/artifacts/ECDLP-IDEA-436/independent_verifier.py`
- Cost receipt charging precision per query: `ideas/artifacts/ECDLP-IDEA-436/cost_analysis.md`

All artifact paths are prospective; no experiment ran.

## Interpretation boundary

High-risk and novelty-unverified. `KN-TECH-73630e` already establishes that this route
can offer at most a computational handle and never new information, so even full success
would be a restructuring of known data, requiring independent replication before any
status change. All finite evidence would be toy.

## Exactly one next executable action

1. Produce the GGM-simulability gate memo for the coordinate-valuation family and either
   recommend scoped rejection under `KN-FIND-002` / `KN-FIND-b7e091`, or state precisely
   which operation of the profile is not simulable by a generic group oracle. Do not
   implement or time any `p`-adic arithmetic.
