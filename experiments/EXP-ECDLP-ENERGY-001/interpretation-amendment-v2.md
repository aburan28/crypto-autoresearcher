# Interpretation Amendment V2: Exact Signed Support

## Status

`NEGATIVE RESULT`, `OBSERVATION`, `TOY-EVIDENCE`, and `MODEL-BOUND`.

This amendment changes interpretation only. It does not modify either immutable run or any raw metric.

## Red-team verdict

`REVISE interpretation; retain the frozen-configuration no-promotion outcome.`

The independent audit is preserved at:

```text
/Volumes/Volume/autolab/research/crypto_autoresearcher_exp_ecdlp_energy_001_red_team_20260717.md
SHA-256 35049235c4ddb24725b514c08af851e448be71321e8e4009ad78e94c101e6fff
```

## Exact correction

For a sign-complete base `A=+-{P_1,...,P_n}`, replacing ordered tuples by ordinary point multisets removes permutation duplication but not inverse-pair cancellation. Different multisets can share the same signed coefficient vector and therefore the same sum.

The exact fivefold supports on the frozen instances are:

| Field bits | Random | X interval | Square map | Rational union | Scalar progression |
|---:|---:|---:|---:|---:|---:|
| 15 | 456 | 456 | 376 | 456 | 41 |
| 17 | 456 | 456 | 400 | 456 | 41 |
| 19 | 2,668 | 2,668 | 2,622 | 2,668 | 61 |

Consequences:

- X interval and rational union tie the random control exactly on every frozen instance.
- Square map has lower exact support on every frozen instance.
- The sampled `5/128` rational-union result versus `4/128` random at 19 field bits is noise, not a near-signal.
- No tested coordinate set has an exact fivefold-support advantage.

For a generic dissociated sign-complete base with `n=B/2`, the finite signed-class count for five terms is

```text
D(n,5) = sum over r in {1,3,5} sum over s=1..min(n,r)
         binomial(n,s) binomial(r-1,s-1) 2^s.
```

This gives `D(4,5)=456` and `D(6,5)=2668`, exactly matching the random controls. The leading `B^5/5!` term can remain a large-`B` heuristic, but `binomial(B+4,5)` is not a validated finite model at `B in {8,12}`.

## Strongest valid result

On the three frozen curves and seeded factor bases:

1. Every non-control coordinate set lies on the forced sign-complete pair-energy floor, so none has a nontrivial pair-collision advantage.
2. No coordinate set has greater exact fivefold support than the matched random set.
3. The square-map sets have strictly smaller exact fivefold support.
4. The scalar progression demonstrates that compressed intermediate supports can destroy final expansion.

This justifies `DO_NOT_PROMOTE_FROZEN_CONFIGURATIONS`. It does not reject x intervals, square-map images, rational unions, fixed-curve preprocessing, or coordinate factor bases as families.

## Cost correction

- `RUN-ECDLP-ENERGY-001` reports exhaustive representation-census queries, not first-witness queries.
- Random-scalar construction is a structural control but not a construction-cost-matched control for coordinate x scans.
- Counter-only storage omits functional witness maps.
- The measured rho walk is an arithmetic scale/control, not an end-to-end comparable attack.
- The existing `S*T^2` values have no calibrated theorem, bit/byte units, or success convention and remain diagnostics only.

## Successor requirements

`EXP-ECDLP-RECURSIVE-001` must, before approval:

1. use exact `|mA|` support as the primary finite coverage metric;
2. compare sign-canonical and sign-complete sets;
3. stop online search at the first exact witness;
4. store functional witnesses and report their bytes;
5. add random-scalar and random-x construction controls;
6. use prime-order curves with monotone `q` and multiple seeds;
7. separate diagnostic full-support enumeration from compiler cost;
8. define every fixed-curve advice/query unit before interpreting `S*T^2`;
9. retain rank, linear algebra, and target descent as required later gates.

## Next concrete action

Finish the independent verifier and random-x control for `EXP-ECDLP-RECURSIVE-001`, then obtain a separate pre-run red-team `GO` before changing its status from `review_required`.
