# RT-20260804-0ff29a -- what I re-derived, in order

Red team, BATCH-a2bb63 (batch 5 of 6), GOAL-MLKEM-004. Reviewing snapshot
`82bcbbe4`, which archives `TASK-20260804-f58d34`.

SCOPE, binding on every sentence: m=35, n=25, d=60, q=127, secret CB eta=2,
error rounded-Gaussian sigma=2, ONE instance. TOY SCALE. No ML-KEM break claim,
no security proof, no FIPS 203 parameter set affected or cleared, no speedup, no
cost claim, no exponent moved. AGENTS.md rule 12 UNMET and UNWAIVED: no
EV-MLKEM-* or KN-* record changes status here and I propose no change. I did not
commit anything and wrote nothing outside my task directory.

---

## 1. What I did not take on trust

I read `report.md` last, not first. Before reading the producer's section 2.1 I
derived the score covariance myself, because if the producer's closed form is
right then the whole batch is a statement about a deterministic functional and I
needed my own version to attack it with.

Score, from the definition:

```
S_k = (1/N) sum_i cos(u_i + phi_ik),  u_i = 2 pi x_i.e / q,  phi_ik = 2 pi y_i.(s-c_k)/q
    = (1/N) [ a_k . cos(u)  -  b_k . sin(u) ],   a_ik = cos phi_ik,  b_ik = sin phi_ik
```

For `e ~ N(0, sigma^2 I_m)` the vector `u` is Gaussian with
`Cov(u_i,u_j) = (2 pi sigma / q)^2 x_i.x_j = 2c x_i.x_j`, `c = (1/2)(2 pi sigma/q)^2`.
Writing `n_i = ||x_i||^2`, `w_i = exp(-c n_i)`, `P_ij = w_i w_j`, `T_ij = 2c x_i.x_j`:

```
E cos u_i = w_i,   E sin u_i = 0
E[cos u_i cos u_j] = (1/2)[E cos(u_i-u_j) + E cos(u_i+u_j)] = P_ij cosh T_ij
E[sin u_i sin u_j] = (1/2)[E cos(u_i-u_j) - E cos(u_i+u_j)] = P_ij sinh T_ij
E[cos u_i sin u_j] = 0                                   (u -> -u symmetry)
=> Cov(cos u) = P .* (cosh T - 1) =: C,   Cov(sin u) = P .* sinh T =: S
=> Cov(S_k, S_k') = (1/N^2) [ a_k^T C a_k' + b_k^T S b_k' ]
```

This is the producer's section 2.1 term for term, including the `-1` in `C` and
the absence of a cross term. It is exact for unrounded Gaussian `e`, not first
order. I implemented it independently (blocked, `block=400`) and never used
`dependence.py`'s version.

Everything below runs on `vectors.json` + `A` with stock numpy. No g6k, no
fpylll, no producer venv.

## 2. Reproduction

**Certificates, recomputed by me from `A` and the emitted integers:**
`mod(X A - Y, q)` has 0 non-zero entries for SIEVE (447,975) and SIEVE_SUMS
(447,975). `STAGEB_LAT` carries only the 15-column lattice block so this identity
does not apply in that form; I did not check it and record the producer's
0/63,795 as unchecked by me. 447,975 + 447,975 + 63,795 = 959,745, matching the
report's total.

**Closed form (mine) against the producer's closed form, SIEVE, ST-6:**

| group | producer CF | mine |
|---|---|---|
| near_miss K=8 | 6.052 | 6.052 |
| near_miss K=25 | 17.480 | 17.480 |
| uniform K=8 | 6.784 | 6.784 |
| uniform K=25 | 22.066 | 22.066 |

**Direct scoring, my own error seed (777000111), my own scorer, my own CAL-PERM,
D=4000:**

| group | producer ST-6 | mine | producer ratio | my ratio |
|---|---|---|---|---|
| near_miss K=8 | 6.0116 | 6.0508 | 0.8600 | 0.8656 |
| near_miss K=25 | 17.4193 | 17.4521 | 0.7296 | 0.7310 |
| uniform K=8 | 6.7754 | 6.7902 | 0.9692 | 0.9714 |
| uniform K=25 | 21.9811 | 22.0393 | 0.9209 | 0.9231 |
| secret_dist K=25 | 9.9703 | 10.0648 | 0.4178 | 0.4216 |

`sd_ratio_to_iid`: mine 0.1384 / 5.5624 against the producer's 0.1382 / 5.5382.
`offdiag(R_raw)`: +0.9999 / -0.0089 / +0.9976 against +0.9999 / -0.0056 / +0.9976.

Nothing in the arithmetic is wrong. The numbers are real, and they are real on an
instrument I built and a scorer I wrote.

## 3. The controls the batch did not run

Same closed form, same candidate groups, **no scoring anywhere**. ST-6 as a ratio
to `K-1`:

| arm | near_miss K=25 | secret_dist K=25 | uniform K=25 |
|---|---|---|---|
| SIEVE (certified dual family) | **0.7283** | **0.4149** | 0.9194 |
| SIEVE_SUMS (certified dual family) | 0.8746 | 0.4891 | 0.9872 |
| NULL-IIDPHASE (the producer's null) | 0.9281 | 0.9163 | 0.9136 |
| C1 row-permuted Y (coupling destroyed) | 0.7579 | 0.4635 | 0.9292 |
| C2 random-direction X, real Y | 0.7505 | 0.4575 | 0.9176 |
| **C3 random X + iid Y, NO LATTICE AT ALL** | **0.7679** | **0.4503** | 0.9192 |
| C4 random X + Y with real column covariance | 0.7556 | 0.4517 | 0.9221 |
| C5 S-orthogonalised Y (producer's named test) | 0.9740 | 0.4275 | 0.9243 |
| C6 rank-5 X (positive control) | 0.2219 | 0.2694 | 0.4848 |

C3 has Gaussian random directions carrying the sieve's exact row norms and `Y`
iid rounded Gaussian at the sieve's entrywise sd. No `A`, no modulus, no q-ary
lattice, no dual relation, no short vector, no sieve, no coupling. It reproduces
the headline.

Extreme-value statistic (my population-level version, MVN from the closed-form
covariance, D=4000, 8 realisations, against a matched independent-column
comparator): secret-distribution ratio 0.459 (SIEVE), 0.426 (C3), 0.985 (NULL).

## 4. Why the producer's null returns 0.92 and mine returns 0.45

`NULL-IIDPHASE` replaces `Y` by uniform residues, which makes
`y_i.(s - c_k)` uniform for **every** group. The near-miss and
secret-distribution groups are defined by their offsets being short. So the null
does not ablate the family with the experiment held fixed; it deletes the
defining property of two of the three groups.

Run 2 isolates the operative variable with no lattice compute at all. Candidate
offset geometry:

| group | mean \|\|delta\|\|^2 | mean pairwise cos(delta_k, delta_k') |
|---|---|---|
| near-miss (`s + unit_k`) | 1.0 | 0.0000 |
| producer's secret-distribution | 53.2 | **+0.5562** |
| `delta = CB - CB` (same length, no shared part) | 52.2 | -0.0195 |
| `delta = u + CB` (long, shared part) | 156,182 | +0.9998 |

The +0.5562 is forced: `delta_k = s - c_k` with `c_k` iid, so every offset
carries the same `s`, and `||s||^2/(||s||^2 + E||c||^2) = 30.0/(30.0+23.2) =
0.5643`. That is arithmetic on the candidate list, not a measurement of a
lattice.

Measuring those three groups through the closed form, ST-6 ratio to `K-1`:

| candidate group | SIEVE (real) | SYNTH (no lattice) |
|---|---|---|
| producer's secret-distribution | 0.4149 | 0.5039 |
| same length, shared part removed | 0.4880 | 0.5062 |
| long offsets, shared part kept | 0.5537 | 0.5569 |

A group as far from the secret as the uniform group (`||delta||^2 = 156,182`
against the uniform group's 135,496) departs to 0.554 on the real database.
So the observable reads the candidate set.

Structural diagnostics, same run. To first order in `e`,
`dS_k/de = -(2 pi/(qN)) sum_i sin(u_i + phi_ik) x_i`, so at `e=0` the Jacobian is
`J_k ∝ X^T sin(phi_k)` and the whole dependence is the Gram matrix of `K` vectors
in `R^m`, `m = 35`. Mean `|offdiag|` of that Gram:

- near-miss 0.126, uniform 0.132 -- both at the `1/sqrt(35) = 0.169` random-direction
  scale, which is the 0.92 floor;
- secret-distribution **0.640** -- five times larger, and that is the departure.

Flat `Y` column correlation: mean `|offdiag|` 0.0087. In the `S` metric: 0.0968.

## 5. The producer's named batch-6 test, run

"Build a family with `Y` columns S-orthogonalised and re-measure." I did:
`M = B^T S B` on the 25 near-miss phase columns, `U = M^{-1/2} diag(sqrt(diag M))`
so `(YU)^T S (YU) = diag(M)` exactly (verified: mean `|offdiag|/diag` goes
0.0961 -> 0.0000), then recompute phases from `Y U` and rerun the closed form.

Result: near-miss K=25 goes **0.7283 -> 0.9740**; secret-distribution goes
**0.4149 -> 0.4275**.

It erases the group whose off-diagonal it zeroes by algebra and does not touch
the group carrying the headline. For near-miss candidates `c_k = s + unit_k` the
offset is exactly `-Y[i,k]`, so the phase columns **are** the `Y` columns; making
their `S`-Gram diagonal sets the b-part off-diagonal to zero by construction, and
a diagonal covariance has correlation matrix exactly `I`, i.e. `ST-6 = K-1`
identically. The test cannot fail in the informative direction. It is a mode-1
control by `KN-TECH-6c0e15`'s own taxonomy, proposed by the entry's own author,
one section after the entry defines mode 1.

## 6. ST-6 is one-sided

`R` is a correlation matrix, `trace R = K`, eigenvalues `>= 0`. With
`T = K - lambda_1` and `Q = sum_{j>=2} lambda_j^2`, Cauchy-Schwarz gives
`Q >= T^2/(K-1)`, so `ST-6 = T^2/Q <= K-1` always, equality iff the trailing
spectrum is flat. Any correlation of any sign lowers it. Numerical check: 0 of
2000 random correlation matrices exceeded `K-1`.

Consequence for the frozen rule: at K=8 the CAL-PERM mean is 6.9904 with sd
0.00328, so the largest attainable `z1` is `(7 - 6.9904)/0.00328 = +2.93 < 3.0`.
The `D3` branch is unreachable through the `z1` channel at K=8.

## 7. T2, and the limitation that its own file refutes

`LIM-T2` says p=3 and p=5 have no matched-K comparator. `results.json`
`T2.per_p` carries `adjacent_bins_10` at K=10 for every p, beside
`uniform_bins_10` at K=10:

| p | adjacent K=10 | uniform K=10 | ratio | extra departure |
|---|---|---|---|---|
| 2 | 0.8728 | 0.9087 | 0.960 | +4.0% |
| 3 | 0.8947 | 0.9128 | 0.980 | +2.0% |
| 5 | 0.9100 | 0.8886 | **1.024** | **-2.4%** |

ST-5c at the same matched K: 0.978, 1.015, 0.975. On the only candidate family a
dual attack actually enumerates, the departure is sign-inconsistent across
moduli and consistent with zero. The producer archived the group that refutes its
own limitation; I do not read that as concealment, but the limitation is wrong
and the conclusion drawn from it has to be corrected.

## 8. Commit-message audit, 82bcbbe4

**Security-claim audit first, because it is the thing that matters most and the
answer is clean.** I grepped the whole snapshot tree and the message for
break / broken / insecure / security level / bits of security / FIPS /
ML-KEM-512 / speedup / faster / attack cost / exponent. Every hit is inside a
non-claim disclaimer. `states_a_conclusion: false` is in `results.json`. The
scope banner is first and binding in every artifact. **There is no security
claim, and no present-indicative Coordinator conclusion about what the numbers
mean.** The rule the Coordinator adopted after batch 4 held on the thing it was
adopted for.

**It did not hold on the mechanism it used to hold it.** The message says "The
producer's words in quotes or nothing" and, twice, "verbatim". These quoted
strings appear in **no** producer artifact; their only occurrence in the
repository is inside the Coordinator's own `snapshot_receipt.json`:

- "partly forced, partly not, and I can say exactly which part"
- "it is not fixed regardless of what is measured"
- "roughly a factor 2 on the operationally relevant group"
- "not settled here"
- "The proof was correct over the statistic's range and useless over the space of
  explanations, because the m=35 artifact fires in the null too"
- "because its offsets are a full bin 2pi/p, not small"
- "served unchanged" / "definitively not 1"

The receipt's own wording is third-person Coordinator paraphrase ("The producer's
own read: PARTLY FORCED, PARTLY NOT, and **it says** exactly which part"); the
commit message renders it first-person ("**I can say** exactly which part") and
calls it verbatim. The producer's real wording differs in every case -- e.g. DEV-3
reads "my branches exhausted the OUTCOME SPACE OF THE STATISTIC but not the SPACE
OF EXPLANATIONS FOR A D2", and section 3 reads "an adjacent bin differs by a FULL
bin, so the offset is 2 pi/p -- large, not small". Some quotes are genuine:
"DOWNWARD -- fewer effective independent candidates than the law assumes" is
verbatim `report.md` section 2.4.

If instead the strings came from the executor's uncommitted chat response (DEV-5
says the narrative was also carried there), the position is worse for review, not
better: the snapshot did not archive the source of its own quotations.

Separately: "0.44x nominal for the sieve, 0.22x for a second certified dual
family". Both are ratios to CAL-PERM, not to nominal `K`. Against nominal they
are 0.532 and 0.541 -- indistinguishable, not 2:1 -- and the 0.22 arises only
because that arm's CAL-PERM comparator returned 61.9220 effective candidates out
of 25 (and 249.4537 out of 64). Third reference-model mislabel in three
consecutive commit messages, second consecutive one that enlarges the effect.

## 9. `KN-TECH-6c0e15` mode 4, judged adversarially

**Would the null-first check have caught DEV-3 prospectively? Yes.** The
`NULL-IIDPHASE` arm was pre-registered and was going to be scored regardless;
emitting `verdict_for()` on its six cells before reading any real cell costs
nothing but arm ordering and would have returned D2 six times. The entry has
earned that specific claim, which is more than its predecessor could say.

**Would catching DEV-3 have saved the batch? No.** The operative defect is that
the null removes a property of the candidate set rather than of the family --
an obligation-1 (`object_removed`/`object_preserved`) and obligation-4 (move 2,
"build the null object with the mechanism deleted") failure, both already in the
entry, neither strengthened by obligation 5. So the pattern from batch 4 repeats
exactly one level up: the new obligation fixes the previous batch's failure mode
and does not reach the current one.

**One inaccuracy now in the corpus.** Mode 4 case B states the cause of the
all-D2 result as `rank(Cov) <= m` forcing the statistic down "for any candidate
count K > m". That bound is vacuous at K=8 and K=25, where every headline cell
sits. What depresses ST-6 there is finite-`m` Gram geometry (`1/sqrt(35) = 0.169`;
measured 0.126-0.132) plus the estimator's finite-`D` bias. A reader with no
access to this campaign will take away a rank condition that does not bind in the
regime the case study is about.

**Credit.** Obligation 3 as a criterion with a named comparator, a numeric
threshold and both ends of the range exhibited is a real improvement, and
SENS-GRADED is a correct first instance (`t` recovered to 0.02 at every `t`,
`K_eff_max` 24.21 -> 3.70 monotone). The "comparator supplies both the reference
and the spread" caution demonstrably killed a manufactured ~4-sigma in the
producer's own v1. All four corrections `DEC-20260804-5c9fe1` demanded were made.

## 10. What I am not saying

- I am **not** saying the measurements are wrong. Every one reproduced, most
  twice.
- I am **not** closing this lane. The obstruction I name applies to one
  contrast. The residual (3-11% below every family-ablated control, unresolved
  because two draws of the same ablated ensemble span 0.450-0.504), the
  correlation with the correct candidate (never measured in five batches), and
  the `m`-dependence at fixed `(N, K)` (unmet since batch 4) are all open.
- I am **not** asserting an operational direction. A downward `K_eff` admits a
  cheaper-attack reading (smaller expected max over wrong candidates) and a
  harder-attack reading (near-secret candidates track the correct score). The
  package correctly claims neither; the dispatching card asserts the second, and
  that assertion is not derived anywhere.
- I have **no** security claim, no cost claim, no exponent, and no scheme scope
  statement of any kind.

## 11. Reproduction recipe for anything above

`vectors.json` + `A` + `numpy`, no g6k and no fpylll. Regenerate the candidates
with `np.random.default_rng(20260805407)` and the order in
`dependence.py:make_candidates_A(s, q=127, n=25, eta=2, 25, 512, 64)`; the null
arm with `np.random.default_rng(20260805404).integers(0,127,(17919,25))`.
Implement the covariance from section 1 above. Every control arm is one blocked
`N x N` pass, about 20 s at `N = 17919`, peak memory well under 1 GB. Total for
everything in this report: 206.2 s + 48.5 s, 2 runs against a budget of 2.

Scratchpad scripts (`rt_dep.py`, `rt_dep2.py`, `rt_out.json`) are session-local
and are **not** durable evidence; the recipe above is what binds.
