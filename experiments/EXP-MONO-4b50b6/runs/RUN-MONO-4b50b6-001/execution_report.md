# RUN-MONO-4b50b6-001 — execution report

**Experiment** `EXP-MONO-4b50b6` · **Goal** `GOAL-MONO-001` · **Batch** `BATCH-003`
· **Protocol** `MONO-m3-census-1.1.0-repair-cm-gate` (frozen, red-team PASS
`RT-20260725-707`) · **Authorized by** `DEC-20260802-505759` · **Claim tier** toy

## Outcome

`outcome_id = FULL_MONODROMY_BARRIER_TOY`, computed mechanically from the
protocol's `barrier_aggregate_rule`. Every declared control passed; exit status 0.

| gate | required | measured |
|---|---|---|
| sizes with a full random panel | ≥ 3 | **4** (211, 431, 809, 1601) |
| random ordinary controls per size | ≥ 20 | **20** each, 80 total |
| every control curve inside `3·(2/√p)` | yes | **yes**, worst case `Δ/envelope = 0.135` |
| reverified exception candidates | 0 | **0** in any panel |
| CM screen scored curves (hard gate) | ≥ 8 | **22** across 10 discriminants |
| reverified CM exceptions | 0 | **0** |

Ten class-number-one discriminants were scored: `D = −7, −8, −12, −16, −19, −27,
−28, −43, −67, −163`, admitted under `CTRL-CM-ADMISSION` (prime order *not*
required). `D = −11` was offered by the panel builder but is **supersingular
at all four pinned primes** (`#E = p+1` in each case, verified), so the
protocol's `reject_supersingular` filter removed it rather than scoring it.
`D = −3` and `D = −4` are `j = 0` / `j = 1728`; the protocol quarantines them to
the automorphism artifact panel, where 3 curves were scored and excluded from
every aggregate.

## What the census actually found

The sampled census is uneventful in the way the protocol anticipated: split
frequency lands in `[0.4908, 0.5065]` across all 80 random controls, and the
largest deviation from `1/2` is `0.0092` against a pinned envelope that ranges
from `0.413` (p=211) down to `0.150` (p=1601). The margin is never worse than
7×.

The interesting part is *why* it is uneventful, and the harness measures that
directly rather than asserting it.

### 1. The cycle type is not a black box — it is a character product

`disc_T S_3(x1, x2, T) = 16 · f(x1) · f(x2)` as a polynomial identity in
`Z[x1,x2,A,B]` (contract §2 Lemma; proved from the chord formula, verified
symbolically, and checked numerically on every censused curve). So for `x1 ≠ x2`
the fibre splits **iff** `χ(f(x1)) = χ(f(x2)) ≠ 0`.

That converts the census into a closed form. With `Z = #{x : f(x) = 0}` and
`#E(F_p) = p+1−t`:

```
freq_split − 1/2  =  ( t² − 2pZ + Z² − 2p + 2Z ) / (2p²)
```

**Checked on all 105 censused curves — 0 mismatches**, to floating-point
equality. Measured `p·|Δ|` never exceeds `0.9994` when `Z = 0` and `3.9941` when
`Z = 3`, matching the contract's Corollary C bound (`< 1/p` and `< 4/p`
respectively).

The deviation is therefore **O(1/p), not O(1/√p)**. The protocol's pinned
`3·(2/√p)` envelope is loose by a factor of order `√p` — it was never wrong,
just far weaker than the truth.

### 2. No exceptional locus can exist at m = 3

The identity is universal in `(A, B)`. It holds for CM curves, for `j = 0` and
`j = 1728`, for every discriminant. So no curve at any prime can deviate from
`1/2` by as much as `4/p`. Hypothesis B of the protocol's `discrimination` block
— "an ordinary locus with systematically deviant cycle-type densities" — is
**empty at m = 3**, and that conclusion does not rest on the census. The census
confirms it; the identity establishes it.

The CM panel behaves exactly like the random panel. Its slightly larger `p·|Δ|`
is fully accounted for by `Z = 3` (full rational 2-torsion), not by complex
multiplication.

### 3. The relation-rate independence assumption is false — by a factor of 2

Every element of a factor base `FB = {x(rG)}` is the x-coordinate of an
`F_p`-rational point, so `χ(f(x)) = +1` on `FB`. By the identity, the fibre over
`(x1, x2) ∈ FB²` with `x1 ≠ x2` **always splits**:

```
P(split | x1, x2 ∈ FB, x1 ≠ x2) = 1        (not freq_split ≈ 1/2)
```

`CTRL-POS-PLANTED-SPLIT` measures exactly this and returns rate `1.0` over
**1594 trials across all four primes, without a single exception**.

The protocol's `quasirandom_relation_prediction = freq_split · (W_eff/p)²`
therefore understates the joint proxy by `1/freq_split ≈ 2` on the off-diagonal.
Including the `x1 = x2` degree-drop diagonal at `W_eff = 4`, the exact ratio is
`(W_eff²−W_eff)/W_eff² ÷ freq_split = 0.75/0.4966 ≈ 1.5`, and the harness
measures `[1.4897, 1.5102]` across all 80 curves.

**This is a constant factor and it moves no exponent.** It is a correction to a
*planning model*, not an attack improvement, and it confers no advantage over
Pollard rho. In hindsight it is unsurprising: index-calculus relation search over
a factor base of rational points never faces the "does the fibre split" question,
because it solves for rational points by construction. Modelling that split as an
independent `1/2` was over-pessimistic by exactly `2`.

## Instrument integrity

- **Two independent classifiers** (discriminant+Legendre vs. root scan) were
  cross-checked on 600 samples per curve, 63 000 comparisons in total:
  **0 disagreements**.
- **Sampled vs. closed form** agreed on every curve; worst gap `0.00806` against
  a 4σ tolerance of `0.01155`.
- **`CTRL-IMON-PRODUCT-COVER`**: the degree-5 product cover `g₂·g₃` produced
  **zero** 5-cycles and **zero** 4+1 patterns — the harness demonstrably detects
  a non-full group.
- **`CTRL-IMON-RANDOM-DEG5`**: random monic quintics gave 5-cycle rate `0.2026`
  (target `0.2 ± 0.05`) and 4+1 rate `0.2451` (target `0.25 ± 0.06`).
- **`CTRL-S3-IDENTITY`**: ≥ 3 point-addition identities verified per prime.
- **Zero reverifications** were required because zero exception candidates arose;
  the reverification path is implemented and is recorded as unexercised rather
  than as absent.

## A defect this run found in itself

The first draft of the harness compared the reduced `j`-invariant against the
**integer** `1728` in three places. `1728` reduces to `40`, `4`, `110` and `127`
at the four pinned primes, so a `j = 1728` curve would have been admitted into
the random panel as generic at *every* pinned prime, and `CTRL-J-EXCLUSION` would
have passed while failing to do its job.

Found by producer self-audit before the recorded run and fixed
(`is_extra_automorphism_j` compares in `F_p`). The discarded pre-fix run was
checked and happened to contain no leaked curve, but the check was unsound, so
the recorded run is the post-fix one. Recorded rather than quietly dropped.

## What this does not say

- **Nothing about m ≥ 4.** `deg_T S_m = 2^{m−2} ≥ 4` there, no analogous
  discriminant factorization is claimed, and `KN-OPEN-009` remains **fully open**
  for `m ≥ 4`. The identity closes the `m = 3` case only.
- **Nothing about crypto-scale ECDLP.** Largest prime tested is 1601 (11 bits).
- **Nothing about ECDLP hardness in either direction.** No hypothesis status
  changes, no claim tier moves, and no attack advantage is claimed or implied.
- The `m = 3` identity is an **elementary consequence of the chord-and-tangent
  addition law** and is not claimed as new mathematics. What this program
  contributes is the observation that it settles `KN-OPEN-009` at `m = 3` and
  invalidates the quasirandom relation model the frozen protocol was going to
  feed `GOAL-ICEX-001`.
