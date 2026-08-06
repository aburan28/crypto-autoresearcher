# TASK-20260806-4810e2 (B2-B): the C1 bound, stated separately per deployment lane, at zero new compute

Executor deliverable. Observations only; no hypothesis, EV-MLKEM-\*, or KN-\*
record is declared supported, rejected, closed, validated or refuted by this
document. AGENTS.md rule 12 is UNMET and UNWAIVED, inherited. No ML-KEM break
claim; the mechanism under study is SESSION recovery, not key recovery. No
number in this document is subtracted from the in-repo `primal_bdd` margins
of 2.80 / 6.04 / 1.28 bits.

## 0. What C1 asks for, verbatim

`ledger/goals/GOAL-MLKEM-005.yaml`, `completion_criteria.items`, C1:

> A stated numeric bound, with derivation, on the dbeta -- and its core-SVP
> bit value under one NAMED cost model -- attainable by best-of-M selection
> at the M established in C2. "The attainable reduction is <= X bits, of
> which Y bits are model assumption, and X may be 0" satisfies this in full.
> Any figure depending on BKZ-profile curvature f'' must print an f''
> sensitivity table beside it and be labelled a model readout, not a
> measurement.

The convexity ceiling this document applies, also verbatim
(`ceiling_known_in_advance`):

> The gain obeys dbeta/beta ~ 0.29\*sqrt((1-rho)\*ln M / beta), so an
> exponent needs ln M = Theta(beta), i.e. roughly 2^Theta(600) ciphertexts
> under one key. And G <= log2 M holds UNCONDITIONALLY by convexity of
> f(beta) = -log2 p(beta): the single-target optimiser sets f''(beta_1) =
> -0.292, so log2 M = f(beta_M) >= f(beta_1) + f''(beta_1)(beta_M - beta_1)
> = G.

C2 (the census, `TASK-20260805-e6a153`) is the source of M for both lanes
below. Both lanes are stated **separately** and are never blended into one
number, per this task's completion gate.

## 1. Method: zero new compute

This task made **zero new BKZ reductions and zero new lattice-estimator
calls**. Every number below is quoted from one of two already-committed,
already-validated artifacts:

- `coordination/goals/GOAL-MLKEM-005/batches/BATCH-a51f91/tasks/TASK-20260805-e6a153/census.json`
  (C2, the census -- the source of M for both lanes), and
- `coordination/goals/GOAL-MLKEM-005/batches/BATCH-a51f91/tasks/TASK-20260805-9672b3/results.json`
  and `verification.json` (T3, the already-verified norm-ratio conversion
  instrument; pinned lattice-estimator revision
  `3e48ef421ec256afddb3e7d2249a77eab6e9ba12`, cost model `RC.MATZOV`, both
  used unchanged throughout this campaign).

No new `(d, beta)` point was needed for the f'' sensitivity table: T3 already
ran and independently verified a finite-difference / integer-staircase /
OLS-slope measurement at exactly the three FIPS 203 standardised parameter
sets (Kyber512, Kyber768, Kyber1024), and that is the range reused in
Section 4. See `receipt.json` for the exact hashes of every reused artifact
and an explicit confirmation that this task invoked the estimator zero
times.

## 2. Lane (a): the normative single-use lane -- R20, R21

From `census.json`:

- **R20** (SSH, `draft-ietf-sshm-mlkem-hybrid-kex-10` Sec. 6): `m_class:
  "one"`, `m: "1"`. Bounding mechanism, quoted verbatim: "generating an
  ephemeral key exchange keypair for ECDH and ML-KEM per connection is
  REQUIRED by this specification."
- **R21** (IKEv2, `draft-ietf-ipsecme-ikev2-mlkem-09` Sec. 3): `m_class:
  "one"`, `m: "1"`. Bounding mechanism, quoted verbatim: "Generating an
  ephemeral keypair and ciphertext for each ML-KEM key exchange is REQUIRED
  by this specification."

Both are normative (`REQUIRED`), per-key, and ML-KEM-specific. M = 1 in this
lane, established by C2 and restated at CX-1 in `EV-MLKEM-d146a5` as the "2
firm" rows -- not the earlier, superseded "6 fix M = 1" bucket that CX-1
corrected.

**C1 statement, lane (a):**

> The attainable reduction is <= 0 bits, of which 0 bits are model
> assumption, and X is exactly 0 -- not merely "may be" -- because
> G <= log2(M) = log2(1) = 0 by the goal record's own convexity bound.
> Equivalently: no attainable dbeta is reported below 0, i.e. best-of-M
> selection cannot reduce beta relative to the ordinary single-target BKZ
> optimum when M = 1, because a selection over one candidate is not a
> selection.

**Why Y = 0 (this bound is model-independent, not merely model-assumption-free
at RC.MATZOV):** the convexity argument only uses the *sign* of the
inequality G <= log2(M) -- it holds for any cost function f(beta) that is
convex in this sense, regardless of the numeric value assigned to f''(beta_1)
or to which of RC.MATZOV / classical core-sieve / any other named cost model
supplies that value. No curvature magnitude, and therefore no f''
sensitivity table, is needed for this lane's figure: Section 4's table does
not apply to the lane (a) bound, because the lane (a) bound does not depend
on f'' at all, only on M = 1.

**Single-target reference costs (unaffected by this null result, quoted from
T3's known-answer control, `RC.MATZOV`):** Kyber512 log2(rop) =
140.1994731076207 (beta 389, d 1005); Kyber768 log2(rop) = 200.9587149140538
(beta 606, d 1420); Kyber1024 log2(rop) = 270.7236234535225 (beta 855, d
1867). These are the ordinary single-target `primal_bdd` costs -- not
adjusted by best-of-M in any way, since the adjustment is exactly 0 -- and
are recorded here only as the baseline the null result leaves untouched. They
are not subtracted from anywhere and do not enter the primal_bdd margins of
2.80 / 6.04 / 1.28 bits.

## 3. Lane (b): the count-unstated lane -- eight deployment modes

From `census.json`, the eight `deployment_mode` rows with `m_class:
"count_unstated"`:

| Row | Spec | `m` field (census) |
|---|---|---|
| R06 | RFC 9180 HPKE, recipient KEM key pair | "not stated" |
| R10 | RFC 9420 MLS + draft-ietf-mls-extensions-10, last-resort KeyPackage | "not stated as a count; bounded only by a rate-limiting SHOULD and the LeafNode Lifetime window" |
| R15 | draft-ietf-tls-esni-25, ECHConfig HPKE key | "not stated as a count; bounded only by a rotation RECOMMENDATION, and the privacy goal argues for a LARGE number of connections per config" |
| R16 | draft-connolly-cfrg-xwing-kem-10, X-Wing | "not stated" |
| R17 | draft-ietf-lamps-kyber-certificates-11, LAMPS X.509 | "not stated as a count; bounded only by the certificate validity period" |
| R18 | RFC 9629 + draft-ietf-lamps-cms-kyber-13, CMS KEMRecipientInfo | "not stated; the specification's explicit intent is 'used over and over'" |
| R19 | OASIS PKCS #11 v3.2, token object | "not stated" |
| R23 | Signal PQXDH, last-resort prekey (row's own caveat: names Kyber-1024, not FIPS 203 ML-KEM, same caveat as R22) | "not stated; 'changes periodically' ..." |

**No bound is sourceable here from either mathematics or the standards
stack.** This is not a gap this task discovered; it restates, without
extending, the normative dead end already established in
`EV-MLKEM-d146a5` (`what_is_established`, "THE NORMATIVE DELEGATION
DEAD-ENDS"): `draft-ietf-tls-hybrid-design-16` Sec. 2 delegates the reuse
bound to "any bounds in the specification of the KEM or subsequent security
analyses"; FIPS 203 states none (validator's independent full-text negative
search, `EV-MLKEM-d146a5`); and `draft-sfluhrer-cfrg-ml-kem-security-considerations-05`
Sec. 4 (R24, the second limb of the delegation per CX-2) endorses reuse "for
multiple incoming ciphertexts" without ever supplying a count. The census's
own producer refuses to read this absence as a ceiling in either direction,
twice, in its own words (`census.json`, `does_any_standardised_mode_state_M_above_2_20`):
"The absence is an absence of a stated number in both directions; it is not
a sourced ceiling and must not be read as one."

**C1 statement, lane (b):**

> No X can be honestly stated for this lane. No retrieved specification,
> and no mathematical argument available to this campaign, establishes a
> value or a ceiling for M in these eight modes. Any positive G figure
> computed here would rest entirely on a *chosen* M -- a deployment-policy
> assumption, not a mathematical result -- so no "<= X bits, of which Y bits
> are model assumption" line is filled in.

**On the illustrative-figure option, and why this task declines it:** the
card permits an illustrative figure if clearly labelled and paired with the
formula, M left free; it equally permits omitting one entirely if any choice
would be indefensible, and calls that an acceptable, arguably preferable,
outcome. This task takes the omission branch and states why. This exact
mechanism -- treating "no stated bound" as license to substitute a round
number (2^20, or any other illustrative constant) -- is the precise failure
this campaign already adjudicated and rejected once, at K1 in
`DEC-20260805-4823db`: "A rule that converts 'no number found' into 'the
number is 2^20' manufactures a bound, in the UNSAFE direction, from an
absence," and that decision's own `next_actions` bind the successor batch not
to "quote a 20-bit cap from" the census. A chosen illustrative M for these
eight modes carries the identical risk of being read downstream as an
implied plausible deployment scale, regardless of how it is labelled, so no
numeric M is substituted here. What *is* reproduced, verbatim and with M left
symbolic, is the formula itself, so a future reader who does source an M can
evaluate it without this task having chosen on their behalf:

```
dbeta/beta ~ 0.29 * sqrt((1 - rho) * ln(M) / beta)      [ceiling_known_in_advance, GOAL-MLKEM-005.yaml]
G <= log2(M)                                             [convexity bound, same source]
```

with `M` an explicit free parameter, `rho` and `beta` as used in the source
formula, and no value assigned to any of them here. See Section 4 for the
f'' sensitivity a future evaluator of this formula should apply.

## 4. The f'' sensitivity table (companion, model readout, reused from T3 at zero new compute)

Labelled **MODEL READOUT, NOT A MEASUREMENT** throughout, per this task's
card. Full machine-readable table: `fpp_sensitivity.json`. This table
applies to the *symbolic* formula in Section 3 if and when a future task
evaluates it with a sourced M; it does not apply to lane (a) (Section 2),
whose X = 0 bound is curvature-independent.

**A. What "0.292" is, and what T3 measured against it.** The goal record's
`ceiling_known_in_advance` uses 0.292 in two places: as `f''(beta_1)` in the
convexity argument, and as the leading coefficient (0.29) of the dbeta/beta
formula. T3's own results.json labels 0.292 "the card's conversion constant
(classical core-sieve exponent)" and separately measures, by OLS of the
`RC.MATZOV` estimator's own reported log2(rop) against beta across a 41-point
scan at each of the three standardised parameter sets, what `RC.MATZOV`
itself implies for that same "bits per block" quantity:

| Set | `RC.MATZOV`-measured bits/block (T3 OLS) | Nominal (ceiling_known_in_advance) | Nominal / measured | Nominal overstates by |
|---|---|---|---|---|
| Kyber512  | 0.27416443652415257 | 0.292 | 1.0650542561317073 | 6.505425613170734% |
| Kyber768  | 0.28038760002945350 | 0.292 | 1.0414155261121627 | 4.141552611216270% |
| Kyber1024 | 0.28009177919327805 | 0.292 | 1.0425154241978114 | 4.251542419781140% |

(T3 `verification.json`, check `V7_estimator_own_bits_per_block_vs_card_0292`,
reused verbatim; no new estimator call.) This is the same style of quantity
that the `0.292` / `0.29` constants play in `ceiling_known_in_advance` --
i.e. it is the SAME f'' range the card names -- but it is `RC.MATZOV`'s OLS
slope, not a literal re-derivation of `f''(beta_1)` from first principles;
this task does not re-derive the ceiling formula's exact functional
dependence on that constant, so **no propagated dbeta/beta or G figure is
computed from this ratio** -- only the input-level spread is reported, to
avoid presenting an un-derived relationship as a result.

**B. The integer-quantisation floor on any single beta readout.** T3's
staircase scan additionally shows that `RC.MATZOV`'s own beta selection is a
non-monotone integer staircase in the scaling parameter c, over the exact
40-interval grid used for A:

| Set | Anomalous (beta-falls-as-c-rises) intervals | Max anomalous drop | OLS residual sd |
|---|---|---|---|
| Kyber512  | 3 of 40 | 2 blocks | 0.494 blocks |
| Kyber768  | 2 of 40 | 2 blocks | 0.452 blocks |
| Kyber1024 | 3 of 40 | 2 blocks | 0.685 blocks |

(T3 `verification.json`, check `V5_staircase_monotonicity_corrected`,
reused verbatim -- this is the "3/2/3 anomalous pairs" finding the task card
names.) Any single-cell dbeta readout at these standardised parameter sets
carries at least this much selection noise before any curvature-sensitivity
question is even asked.

## 5. The CM-2 objection: what this bound does and does not price

`VAL-20260806-bb0559` and `RT-20260806-d008e0` both note that pricing BKZ
blocks alone does not price a full multi-ciphertext attack end to end. Named
place for the additional terms, as an explicit, unquantified line item:

```
C_total(M)  =  C_reduction(beta_M)   [priced here and by T3, under RC.MATZOV]
             + C_query(M)            [NOT quantified: obtaining M ciphertexts
                                       encapsulated under one static key]
             + C_storage(M)          [NOT quantified: holding/managing M
                                       candidate projected-error vectors or
                                       ciphertexts for the selection step]
             + C_selection(M)        [NOT quantified: the computational cost
                                       of the best-of-M selection itself]
```

This task, and T3 before it, price only `C_reduction`. `C_query`,
`C_storage` and `C_selection` are not quantified by any producer in this
campaign; each is `>= 0`. Consequently **every bit figure in this document is,
at most, a lower bound on total attacker cost from the lattice-reduction term
alone** -- a complete multi-target cost model is not attempted here. For lane
(a) this is moot in a stronger way, not merely an omission: G <= log2(1) = 0
means the multi-target mechanism these additional terms would price has no
room to operate in the first place, since M = 1 admits no selection step at
all.

## 6. Summary (both lanes, never blended)

| Lane | M | Attainable reduction (X) | Model assumption (Y) | f'' table applies | CM-2 status |
|---|---|---|---|---|---|
| (a) normative single-use: R20, R21 | 1 (firm, normative) | <= 0 bits, exactly | 0 bits | No (curvature-independent) | Moot: M=1 forecloses the multi-target terms |
| (b) count-unstated: R06, R10, R15, R16, R17, R18, R19, R23 | not sourced, either direction | not stated (no X) | not applicable (no figure) | Applies to the symbolic formula if a future task sources M | `C_reduction` only, named as a lower bound; other terms unquantified |
