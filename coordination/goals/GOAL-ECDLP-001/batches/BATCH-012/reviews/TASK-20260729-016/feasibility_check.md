# TASK-20260729-016 — independently re-derived arithmetic for EXP-YIELD-002

Reviewed object: the **committed blobs** at `f291a624610458fc7ad40b5cf174447517ce97e5`
(`experiments/EXP-YIELD-002/specification.yaml`,
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/tasks/TASK-20260729-014/criterion_feasibility_table.md`),
read with `git show <commit>:<path>`, never from the working tree.

All numbers below were recomputed in this session from
`experiments/EXP-YIELD-001/runs/RUN-YIELD-001-NULL-RANDOM-SUMSET/results.json` as it
exists at commit `2fb2bb7a111d999859612e52990eea7dc6bbac1a`. Nothing is adjudicated
by quotation.

**Probe label.** The arithmetic below was performed with a `python3` interpreter on
scratch files outside the repository. It is **UNARCHIVED AND NOT EVIDENCE**. It is a
review check on a contract, it produced no draw of any process this contract
specifies, and no conclusion of this batch may rest on it. **No repaired null was
run. Zero curve compute.** No experiment artifact was created, read into the
repository, or modified.

---

## 0. Snapshot integrity (gate R6)

| check | result |
|---|---|
| `f291a624…` resolves to a commit | PASS |
| reachable from `HEAD` = `05edc117ce8c3bcb1a7c032e2df7f80ed82f6724` | PASS (`git merge-base --is-ancestor`) |
| first parent | `b42073b6447b8503054e2e0700ed9e0af34b0719` — matches receipt |
| changed-path set | exactly 2 paths, both `A` (added); no deletions, no extras, no AppleDouble sidecar staged |
| `path_sha256` of `criterion_feasibility_table.md` | `b78dfc3b…840ae` — matches receipt |
| `path_sha256` of `specification.yaml` | `a274203c…a99c2` — matches receipt |
| working tree vs commit for the contract | byte-identical (`git diff` empty) |
| pinned input hashes vs the blobs at `2fb2bb7a` | `IN-1` `040207f8…125cd` MATCH; `IN-2` `2287b277…2aeb` MATCH |
| `yaml.safe_load` on the contract | PASS |
| plain-scalar `' #'` sweep | 0 occurrences |
| pre-registration order | **CONFIRMED against commit order.** `git ls-tree -r HEAD` shows `experiments/EXP-YIELD-002/specification.yaml` and **zero** paths under `experiments/EXP-YIELD-002/runs`. No draw of P-REPAIRED or P-ASRECORDED exists at any commit reachable from `HEAD`. |

### The disclosed whitespace-only dedent — what I could and could not verify

**NOT verifiable against Git.** The file was *added* at `f291a624`; the pre-repair
version was never committed, so no blob comparison is possible and the receipt's
byte-equality proof cannot be independently reproduced by any third party from the
repository. I record that as a limit, not as a dispute.

What I *did* verify, and what is consistent with the disclosure:

- the note's text is **1443 characters**, exactly the length the receipt states;
- `independence_note_for_the_tail_checks_and_for_CR_4` sits at indent 2 (contract
  line 976), a proper sibling of `tail_checks` (962) and `replication` (998) under
  `experiment` — which is where its name places it;
- lines 977–996 are a continuous, semantically coherent block scalar with no
  truncation or transposition;
- the file parses and carries zero plain-scalar `' #'`.

I find **no evidence of content movement** and no reason to doubt the disclosure. It
is nonetheless recorded as *verified by internal consistency*, not *verified against
a committed pre-repair blob*.

---

## 1. Cell set, de-duplication, replicate schedule (independently reproduced)

- `IN-1.cells` has **49** entries; `IN-2` reports `n_evaluable_on_measured_B = 49`
  and `n_eval_denominator = 49`. Both cross-checks pass.
- Grouping on `(k, m, B)` gives **48** distinct groups. Exactly one group has two
  members: `(k=12, m=3, B=22)` at `beta` 0.325 and 0.350, both `N=4001`,
  `C_red=1782`, `P_pred=1452.1510155838187`. **RC-C dedup 49 → 48 reproduced.**
- Arity split **29 at m=2 / 19 at m=3** reproduced.
- C-14 schedule over the 48: **37 at 100 replicates, 11 at 30, 0 at 10**; largest
  `C_red = 91922` at `T-18-3-B82`. Reproduced.
- `IN-1.replicates` equals the C-14 value at **all 49 cells** (no mismatch), so
  `sem_001 = s_001/sqrt(n_rep)` uses the same `n_rep` in both arms. Reproduced.
- All 49 `C_red` values are even. Reproduced. `C_red/2` is always an exact integer.

## 2. Per-cell arithmetic at the four INV-4-failing tuples

`T = |S_(m-2)| e^{-λ}`, `λ = C_red/N`, `sem = sd_001/sqrt(n)`.
`z_sem^cf` and `z_sd^cf` are the counterfactual statistics **under the
counterfactual as table §4 defines it** (`mu_rep = P_pred − T`), i.e. `T/sem` and
`T/sd`; `z_shift^cf = T/(sqrt(2)·sem)`.

| tuple | N | C_red | s | λ | e^{−λ} | T | sd_001 | n | sem_001 | z_sem^cf | z_sd^cf | z_shift^cf | committed z_sd |
|---|---:|---:|---:|---|---|---|---|---:|---|---:|---:|---:|---:|
| T-18-3-B16 | 261707 | 688 | 16 | 0.00262889 | 0.99737456 | 15.95799 | 1.27936 | 100 | 0.12794 | 124.734 | 12.473 | 88.200 | −12.439359 |
| T-16-3-B16 | 65633 | 688 | 16 | 0.01048253 | 0.98957222 | 15.83316 | 2.64086 | 100 | 0.26409 | 59.955 | 5.995 | 42.394 | −5.899492 |
| T-18-3-B24 | 261707 | 2312 | 24 | 0.00883431 | 0.99120460 | 23.78891 | 4.13259 | 100 | 0.41326 | 57.564 | 5.756 | 40.704 | −5.748567 |
| T-18-3-B28 | 261707 | 3668 | 28 | 0.01401567 | 0.98608209 | 27.61030 | 7.24573 | 100 | 0.72457 | 38.106 | 3.811 | 26.945 | −3.920271 |

`P_pred = N(1−e^{−λ}) + s·e^{−λ}` recomputed to full double precision at all four
agrees with the quoted `P_pred` to `0.0` absolute (703.0544452985, 700.2397316294,
2325.6064584778, 3670.0252224971). `(mu_001 − P_pred)/sd_001` reproduces the quoted
`z_vs_P_pred_single_sd` to 12 decimals at all four. **IV-2 case KA-8 is feasible and
will pass.**

## 3. Re-derivation of `E[distinct]` for P-REPAIRED (gate R1, OB-10)

Let `A = (1 − 2/N)^{C/2}`, `C* = (1 − 1/N)^{C/2}`, `s = |S_(m−2)|`.

Bin `j` is unmarked iff it is not pre-marked **and** not hit. Step 1 and step 2 use
independent randomness, so the two events are independent. For a uniform `s`-subset
of the `N` bins, `P(j not pre-marked) = 1 − s/N` for **every** `j` by exchangeability.
`N` is odd and `j ≠ N−j` for `j ≠ 0`, so one throw marks two distinct bins and
`P(throw misses j) = 1 − 2/N`, giving `P(j never hit) = A` for `j ≠ 0`. A throw with
`g = 0` marks only bin 0, so `P(0 never hit) = C*`. Linearity of expectation over the
`N` bins (no cross-bin independence is required) gives

```
E[distinct] = N − (1 − s/N)[(N−1)·A + C*]
```

**This is exactly the contract's formula. The derivation is correct and exact.**

Asymptotics. `ln A = −λ − λ/N + O(N^{−2})` and `ln C* = −λ/2 + O(N^{−1})`, so
`(N−1)A + C* = e^{−λ}(N − 1 − λ) + e^{−λ/2} + O(N^{−1})`, and with
`P_pred = N − N e^{−λ} + s e^{−λ}`,

```
E[distinct] − P_pred = (1 − s/N)·[ e^{−λ}(1 + λ) − e^{−λ/2} ] + O(N^{−1})
                     = (1 − s/N)·f(λ) + O(N^{−1})
```

**Reproduced exactly as the contract states it.** Numerically, the largest gap
between the exact `E[distinct] − P_pred` and `(1 − s/N)f(λ)` over the 48 tuples is
`3.05e−05` bins — the `O(N^{−1})` term is real and negligible.

`f` is increasing on the realised range (`f'(λ) = ½e^{−λ/2} − λe^{−λ} > 0` there) and
`f(λ) ≈ λ/2 − 5λ²/8` for small `λ`. **Reproduced.**

`f < g` for every `λ > 0`, where `g(λ) = e^{−λ/2} − e^{−λ}`: the inequality is
equivalent to `h(λ) = (2+λ)e^{−λ/2} < 2`, and `h(0) = 2` with
`h'(λ) = −(λ/2)e^{−λ/2} < 0`. **Proved independently; the contract's claim holds.**

### The two declared SEM bounds — re-derived and confirmed

| quantity | my value | contract | verdict |
|---|---|---|---|
| λ range over the 48 | 0.002208576767147994 (T-18-2-B34) … 0.495756707753721437 (T-16-3-B58) | identical | MATCH |
| max `f(λ)` in bins | 0.130625 at T-16-3-B58 | 0.13063 at T-16-3-B58 | MATCH |
| max exact process bias in bins | 0.130512 | "at most 0.131 bins" | HOLDS |
| **max process bias in SEM** | **0.07519 at T-12-2-B46** | 0.0752 at T-12-2-B46 | **MATCH** |
| **max identity-convention diff, m=2** | **0.08947 SEM at T-12-2-B62** (0.167939 bins) | 0.0895 at T-12-2-B62 | **MATCH** |
| max identity-convention diff, m=3 | 0.00043 SEM at T-12-3-B22 | "below 0.001" | HOLDS |

Both convention formulas re-derived from scratch and confirmed:

- **m = 2** (structurally exact pre-mark is bin 0, deterministic):
  `E_struct = N − (N−1)A`, so `E_struct − E_unif = (1 − 1/N)(C* − A)
  = (1 − 1/N)(e^{−λ/2} − e^{−λ}) + O(N^{−1})`. **Matches the contract.**
- **m = 3** (structurally exact pre-mark is `B/2` whole antipodal pairs among the
  `(N−1)/2` non-identity pairs, so `P(j pre-marked) = B/(N−1)` for `j ≠ 0` and `0` for
  `j = 0`): `E_struct = N − [(N−1−B)A + C*]`, so
  `E_struct − E_unif = (B/N)(A − C*) = (B/N)(e^{−λ} − e^{−λ/2}) + O(N^{−1})`.
  **Matches the contract.**

**Conclusion carried:** neither the identity-bin convention (≤ 0.0895 SEM) nor the
process bias (≤ 0.07519 SEM) can produce a 3.000-SEM excursion at any declared
tuple. The contract's binding consequence stands, and **no outcome of this
experiment may be explained by either.**

*Caveat recorded:* both derivations compare **means only**. The contract does not
quantify whether pairing the m=3 pre-marks changes the **variance** of the distinct
count. This is harmless as specified, because CR-1/CR-2 denominate on the measured
`s_rep` of the actual repaired process rather than on a modelled variance.

---

## 4. Second-order terms, per-term verdict (gate R3)

| term | largest magnitude over the 48 | could it fire a 3.000 criterion alone? |
|---|---|---|
| `(N−1)`-vs-`N` bin-count term, magnitude `(1 − e^{−λ})` | **0.2032 SEM** at T-12-2-B62 (0.02032 in single-sd units) | **NO.** 0.2032 ≪ 3.000. |
| identity bin (pre-markable and hittable), m=2 | 0.08947 SEM at T-12-2-B62 | **NO.** |
| identity bin, m=3 | 0.00043 SEM at T-12-3-B22 | **NO.** |
| odd-`C_red` rule | not realised: all 49 `C_red` even, max 91922 | **NO.** IV-4 fires and stops before any throw. |
| uniform vs actual `S_(m−2)` pre-marking | this *is* the identity-bin term at m=2 and the `B/N` term at m=3 | **NO.** |
| process bias `f(λ)` (a real bias of the specified process) | 0.07519 SEM at T-12-2-B46 | **NO.** |

**None of the five named terms can fire any criterion alone at the fixed replicate
count.** One disclosure gap: §5.4's "centred to within `0.16466` standard errors" is
the sum `0.0895 + 0.0752` of the two second-order *biases*; it does **not** bound the
`(N−1)`-vs-`N` deviation at 0.2032 SEM. That deviation is not a bias of the process
as specified (the exact formula is over `N` bins), so the sentence is not wrong — but
it is narrower than a reader will take it to be.

---

## 5. Criterion firability in both directions (gate R1) — **and a defect**

Table §4 defines the counterfactual **numerically and unambiguously**:

```
mu_rep = P_pred − T   at every declared tuple      (§4, verbatim)
```

From that definition the counterfactual statistics are **determined**:

```
counterfactual |z_sem|   = T / sem_001
counterfactual |z_sd|    = T / s_001
counterfactual |z_shift| = T / (sqrt(2)·sem_001)
```

Table §4 then asserts that these are *"exactly, the committed columns"*, i.e.
`|z_sem_001|` and `|z_sd_001|`. **That identification requires
`T = |mu_001 − P_pred|`, which is false at every tuple** — `mu_001` is a SAMPLED
committed draw carrying its own error, `T` is DETERMINED. The largest gap is
`| T − |mu_001 − P_pred| | = 2.9276 SEM` at **T-18-2-B264**
(`T = 0.8753` bins, committed residual `27.9966` bins).

§6 evaluates **CR-1 and CR-2 from `|z_sem_001|` and `|z_sd_001|`** (definition B) but
evaluates **CR-3 from `T/(sqrt2·sem_001)`** (definition A). The two definitions give
different named sets:

| | table §6/§7 (uses committed residual) | self-consistent with §4 (`mu_rep = P_pred − T`) |
|---|---:|---:|
| CR-1 counterfactual firings | **21** | **20** |
| CR-2 counterfactual firings | **4** | **5** |
| CR-3 counterfactual firings | 18 | 18 (*identical set*) |
| union / "cannot fire" complement | 21 / **27** | 20 / **28** |

Named differences, all mechanically checkable from columns the table itself prints:

| tuple | `T/sem_001` | `|z_sem_001|` | table §6 CR-1 | correct under §4 |
|---|---:|---:|---|---|
| **T-18-2-B58** | **3.1004** | 1.3106 | not listed | **fires** |
| **T-16-3-B48** | 2.7588 | **3.6289** | listed as firing | **does not fire** |
| **T-18-2-B264** | **0.0945** | **3.0220** | listed as firing | **does not fire** |

and for CR-2, **T-16-3-B22** has `T/s_001 = 3.0506 ≥ 3` yet is excluded from the
named 4 (`|z_sd_001| = 2.832`).

Section 7's own stated rule is *"at those tuples the omitted term `T` is smaller than
3.000 standard errors of the mean"*. Applying **that rule literally** gives **28**
tuples, not 27: it **adds** `T-18-2-B264` and `T-16-3-B48` and **removes**
`T-18-2-B58`. So the §7 list contradicts the §7 criterion at three named tuples.
Under `PRED-ID` — *set identity, never cardinality* — these are pre-registered sets,
and they are wrong.

The single most telling case is **T-18-2-B264**: at m=2, `s = 1`, so `T ≤ 1 bin` at
every m=2 tuple, and there `T = 0.875` bins against a committed residual of
`27.997` bins (3.022 SEM). The missing pre-marking is **32× too small** to explain
that residual. The table nevertheless counts it as a tuple where CR-1 "can fire under
the full counterfactual", which is exactly backwards: CR-1 can only fire there if
something *other than* the missing pre-marking is present.

### Firability verdicts

| rule | CAN FIRE? | can it FAIL under the counterfactual? |
|---|---|---|
| CR-1 | **CAN FIRE** at 20 (self-consistent) / 21 (as tabulated) of 48 | YES |
| CR-2 | **CAN FIRE** at 5 (self-consistent) / 4 (as tabulated) — essentially no power | YES |
| CR-3 | **CAN FIRE** at 18 of 48 (same set under both readings) | YES |
| CR-4 | **CAN FIRE**, with certainty under the all-or-nothing counterfactual (`n_neg = 48 ≥ 35`) | YES |
| IV-1a/b | CAN FIRE | — |
| IV-2 (KA-1…KA-8) | CAN FIRE; KA-8 verified feasible above | — |
| IV-4 | CAN FIRE on a hash or parity mismatch; cannot fire on the committed data | — |

**Gate R1 is met in the aggregate: the contract is falsifiable.** Under a global
counterfactual CR-1 fires at ~20 tuples and CR-4 fires with certainty, so the design
*can* fail if the diagnostic is wrong. It is the *named sets*, not the falsifiability,
that are defective.

## 6. Are 27 (28) powerless tuples fatal? — power curve

The failure mode under test is **global** (either the pre-marking is the whole story
or it is not), so per-tuple powerlessness at 27–28 tuples does not remove global
falsifiability. But the contract's claim that **CR-4 "carries the counterfactual
power at the 27 tuples"** is true only for the all-or-nothing counterfactual. Let the
repaired null still fall short by a fraction `φ` of `T` (the null-plus-bias case is
`φ = 0`), with `sem_rep = sem_001`:

| φ | E[n_neg] | P(CR-4 fires) | # tuples where E[z_sem] ≥ 3 |
|---:|---:|---:|---:|
| 0.02 | 26.66 | 0.009 | 0 |
| 0.05 | 29.22 | 0.048 | 1 |
| 0.10 | 31.71 | 0.179 | 5 |
| 0.20 | 34.46 | 0.499 | 8 |
| 0.50 | 37.97 | 0.919 | 16 |
| 1.00 | 40.72 | 0.997 | 20 |

Reading: in the regime where per-tuple criteria have no power (`φ ≤ 0.05`), **CR-4's
firing probability is at most 0.048**. CR-4 does not restore power against partial
failures; it restores power against the *complete* one. That is a scope limit to be
recorded, not a reason to withhold the run.

## 7. CR-4's independence licence (the load-bearing argument)

**The independence half of the argument is CORRECT.** Under the contract's design,
`sign(mu_rep,i − P_pred,i)` depends only on stream `i`; `P_pred,i` is a fixed constant
carrying no randomness; the seed derivation gives distinct per-tuple seeds (the
48 `(k, m, B)` triples are distinct *because* RC-C de-duplicated on exactly those
fields), so the streams are independent by construction. `OB-9`'s objection — that
the *measured curve quantities* are correlated down a `(k, m)` column — genuinely
does not transfer: those quantities enter as constants, not as random variables. The
contract's stated reason is the right reason.

**The identical-distribution half is where it is loose.** The signs are independent
but **not identically distributed**: `p_i = Φ(−bias_i/sem_i)`, so `n_neg` is
**Poisson-binomial**, not `Binomial(48, 0.5)`.

| quantity | my value | contract |
|---|---|---|
| range of `p_i` | **0.47003 … 0.49859** | "between 0.472 and 0.500" |
| `E[n_neg]` | **23.504** | 24.0 at `p = 0.5` |
| `P(n_neg ≤ 13)` under the declared bias | **0.001660** | 0.001218 (normal+cc at p=0.5) |
| `P(n_neg ≤ 13)` at `p = 0.5`, exact | 0.001044 | — |
| `P(n_neg ≥ 35)` under the declared bias | 0.000642 | 0.001218 |
| CR-4 two-sided, under the declared bias | **0.002302** | 0.002436 declared |
| CR-4 two-sided at `p = 0.5`, exact binomial | 0.002088 | 0.002436 declared (17% high) |

**"`p = 0.500` is the conservative end" is only half true.** The declared positive
bias pushes `n_neg` **down**, so it is conservative on the `n_neg ≥ 35` tail (the
counterfactual direction, as the contract says) but **anti-conservative on the
`n_neg ≤ 13` tail by a factor of 1.59** — and `n_neg ≤ 13` fires CR-4, which routes
to **MISS-STRUCTURED**. The absolute size is negligible (0.00166), and the contract's
own declared figure 0.002436 still **bounds** the true 0.002302, so **the 0.377
budget survives**. The wording, not the budget, is wrong.

## 8. Chance-alarm budget and tail constants (gate R2 / the 0.377 figure)

Numerically integrated Student-t tails, this session:

| constant | my value | contract | verdict |
|---|---|---|---|
| `P(|t_99| > 3.000)` | 0.003416 | 0.00342 | **correct** |
| `P(|t_29| > 3.000)` | 0.005499 | 0.00552 | correct to 0.4% (rounds to 0.00550) |
| `P(|Z| > 3.000)` | 0.002700 | 0.00270 | **correct** |
| CR-1 total | 0.18686 | 0.18726 | agrees |
| CR-3 total (same reference) | 0.18686 | 0.18726 | agrees |
| CR-4 | 0.00209 exact / 0.00230 under bias | 0.00244 | contract's figure bounds both |
| **TOTAL** | **0.37582** | **0.377** | **the declared 0.377 is a valid upper bound** |

The union-bound direction is right: expected exceedances ≥ P(at least one), by Markov.

**CR-2's stated tail is wrong.** The contract claims a per-tuple chance-alarm
probability "below `1e-20`". At the 37 tuples with 100 replicates,
`P(|t_99| > 30) ≈ 1.7e−51` — far below. At the **11 tuples with 30 replicates**,
`|z_sd| ≥ 3` means `|t_29| ≥ 3·sqrt(30) = 16.4317`, and
`P(|t_29| > 16.4317) ≈ 3.13e−16` — **four orders of magnitude above the stated
bound**. Still utterly negligible in the budget (11 × 3.1e−16 ≈ 3.4e−15), so this is
a disclosure error, not a budget error.

### Does the budget support MISS-MARGINAL's `[3.000, 10.000)` band?

Expected CR-1 chance exceedances over the 48 tuples (37 at 99 df + 11 at 29 df):

| threshold | expected exceedances |
|---:|---:|
| ≥ 3.0 | 1.87e−01 |
| ≥ 3.5 | 4.26e−02 |
| ≥ 4.0 | 8.92e−03 |
| ≥ 5.0 | 3.71e−04 |
| ≥ 6.0 | 1.87e−05 |
| ≥ 8.0 | 8.82e−08 |
| ≥ 10.0 | 7.26e−10 |

**The declared budget justifies a marginal band out to roughly `|z| = 4`, not to
`|z| = 10`.** A single CR-1 failure at `|z_sem| = 8` has a chance rate of `8.8e−08` —
seven orders of magnitude below the rate the budget was computed to excuse, and four
orders below the CR-4 alarm rate the contract treats as *structural*. Under the
frozen text that outcome is **MISS-MARGINAL → `inconclusive` → replicate**, and
`EV-ECDLP-008` `O-4` is left standing. That is the escape hatch: not a route by which
a miss is reported as a pass, but a route by which a **decisive structural refutation
is recorded as inconclusive**.

## 9. Are the P-MISS branches disjoint and exhaustive? — **provably not**

Contract text: MISS-MARGINAL = *"Exactly one tuple fails CR-1 with 3.000 ≤ |z_sem| <
10.000, **and or** exactly one tuple fails CR-3 with 3.000 ≤ |z_shift| < 10.000, with
CR-2 not firing at any tuple and CR-4 not firing."* The contract then asserts *"the
three are defined by disjoint conditions and their union is total."*

`and or` admits exactly two readings, and **each breaks one of the two asserted
properties**:

- **OR reading** — counterexample to **disjointness**: one CR-1 failure at
  `|z_sem| = 4.0`, three CR-3 failures all with `|z_shift| < 10`, CR-2 clean, CR-4
  clean. MISS-STRUCTURED holds (`CR-3 fails at ≥ 2`). MISS-MARGINAL also holds (the
  CR-1 clause is satisfied; CR-2 and CR-4 are clean). **Both branches fire.**
- **AND reading** — counterexample to **exhaustiveness**: one CR-1 failure at
  `|z_sem| = 4.0`, zero CR-3 failures, CR-2 clean, CR-4 clean. MISS-STRUCTURED fails
  on every disjunct. MISS-MARGINAL requires *exactly one* CR-3 failure and there are
  none. **Neither branch fires.**

The second case is not exotic: it is **the single most likely miss outcome** given
that the expected CR-1 chance exceedance count is 0.187 and CR-3's set is a strict
subset of CR-1's under the counterfactual.

Because the branch determines whether `EV-ECDLP-008` `O-4` is **superseded** or left
**undischarged**, an ambiguity here is a route to choosing the disposition after the
numbers are visible — precisely what `ST-5` forbids and cannot prevent when the text
itself is ambiguous.

## 10. `CR-3`: is the shift and the denominator right?

**The shift `T` is right.** The true expected shift is

```
E[P-REPAIRED] − E[P-ASRECORDED] = (s/N)[(N−1)A + C*] = s·e^{−λ} − (s/N)·f(λ) + O(N^{−1})
```

so the correct centring is `T − (s/N)f(λ)`. The neglected correction is at most
`(22/4001)(0.131) ≈ 7.2e−4` bins at m=3 and `≈ 3e−5` bins at m=2 — under `1e−3` SEM
everywhere. **`T = |S_(m−2)| e^{−C_red/N}` is correct to far inside tolerance.**

**The paired-difference denominator is right.** `mu_rep` and `mu_001` are draws from
independent streams (distinct arm labels ⇒ distinct seeds; BATCH-011's masters
110xxx are disjoint from BATCH-012's 120xxx). The shared quantities `N`, `C_red`,
`s`, `P_pred` are constants and contribute no variance. So
`Var(mu_rep − mu_001) = sem_rep² + sem_001²` and
`sqrt(sem_rep² + sem_001²)` is the correct scale. **Confirmed.**

**One sourcing error.** CR-3 says *"`mu_001` and `sem_001` are QUOTED from IN-1"*.
`IN-1` contains **no `sem` field at all** (grep: zero occurrences of `sem` in the
committed blob). `sem_001` is DERIVED as `s_001/sqrt(n_rep)`; only `IV-1` says so.
Under `RC-8`'s labelling rule a derived quantity may not be labelled QUOTED, and
under `ST-3` an Executor who cannot locate a QUOTED quantity in `IN-1`
unambiguously must **stop and report** — so as frozen, CR-3 obliges the Executor to
either stop or silently infer. (`IN-1.replicates` does equal the C-14 count at all 49
cells, so the inference is in fact unambiguous; the text is what is wrong.)

## 11. Seeds and determinism (gate R1, reproducibility)

| property | verdict |
|---|---|
| collision-free across the 48 tuples within an arm | **YES.** RC-C makes `(k, m, B)` unique across the 48, and those three fields are in the seed string. Low-64-bit SHA-256 collision risk ≈ `C(48,2)/2^64 ≈ 6e−17`. |
| collision-free across arms | **YES.** The arm label and the master seed both differ. |
| HIGHPREC independent of the criterion streams | **YES** (master 120501, label `HIGHPREC`), so the block that "feeds nothing" shares no randomness with the block that feeds everything. Good. |
| disjoint from BATCH-011 masters | YES, 120xxx vs 110xxx. |
| `round(beta × 1000)` well-defined | YES on the realised grid; no β lands on a `.5` boundary in double precision. |
| merged tuple drawn once, seeded from β=0.325 | YES, specified. |
| **seed derivable for the KNOWNANSWER arm** | **NO.** The seed string requires `k`, `round(beta×1000)`, `m`, `B`, `C_red`. KA-1…KA-7 are synthetic cases with `N`, `s`, `C_red` and **no** `k`, `beta`, `m` or `B`. No seed is derivable; the Executor must invent one. |
| **the without-replacement pre-mark is algorithmically determined** | **NO.** *"Choose `s` DISTINCT bins UNIFORMLY AT RANDOM WITHOUT REPLACEMENT"* fixes the distribution but not the algorithm. `rng.choice(N, s, replace=False)`, `rng.permutation(N)[:s]`, Floyd's method and rejection sampling all consume different amounts of the same stream and produce different realised numbers from the same seed. |
| numpy version pinned | NO (recorded in the manifest after the fact, not fixed in advance). |

**Consequence.** The contract's own claim — *"FULLY SPECIFIED SO THAT NOTHING IS LEFT
TO THE EXECUTOR'S JUDGEMENT AND SO THAT EVERY NUMBER IS REPRODUCIBLE FROM THIS
CONTRACT"* — is **false as frozen**. Statistical reproducibility holds; bit-exact
third-party reproduction does not. Two determinism choices are left to the Executor,
which is where `INV-4` hid last time.

## 12. Budget feasibility, independently recomputed

| quantity | my value | contract |
|---|---|---|
| main-arm byte-clears (`Σ N·n_rep` × 2 arms) | 8.05e8 | "below 1.5e9" — **holds** |
| main-arm random draws (`Σ (C_red/2)·n_rep` × 2) | **2.19e7** | "below 2e7" — **exceeded by 9.5%** |
| high-precision byte-clears | 1.70e10 | "below 1.8e10" — holds |
| high-precision draws | 7.36e7 | not stated |
| peak memory | one bool array of length ≤ 261707 (< 0.3 MB) + parsed `IN-1` | "4 GB cap not approached" — holds by orders of magnitude |
| 3 runs × 600 s | 1800 s = 0.5 h | matches `total_cpu_hours: 0.5` |

The draw-count overstatement is cosmetic (the binding cost is the array clears), but
it is a number in a frozen contract that does not hold.

## 13. `IV-1` has no power against the one scenario that matters

Suppose the committed BATCH-011 antipodal residuals are **real** rather than
sampling noise — i.e. `mu_asrec` lands at the analytic `E_asrec` while `mu_001` did
not. Then `z_comp = |E_asrec − mu_001|/(sqrt2·sem_001)` reaches 3.000 at **0 of 48
tuples**; the largest is **2.074 at T-18-2-B264**, then 1.867 at T-14-2-B118.
`IV-1a` requires **more than 2** tuples at ≥ 3.000 and therefore **does not fire**.

This is not a false-alarm hazard — it is a blind spot. `IV-1` is the gate that
anchors CR-3's comparison to the committed package, and it cannot see the single
largest anomaly in that package. It should be recorded as a limit of the anchoring,
not repaired by loosening a threshold after the fact.

## 14. RC-F: what the disclosure subtracts

`RC-A`'s parent objection `RC-F` asks for an independent session to *"re-implement
`occupancy_prediction` and the antipodal `occupancy_null` **from the contract text
alone** and reproduce the four recorded failing cells."* The contract discloses that
the **authoring Coordinator read the committed BATCH-011 driver**, and then specifies
`P-ASRECORDED` to be **identical to what that driver implements** ("THE ONLY INTENDED
DIFFERENCE … IS NONE").

Consequence, stated plainly: **`IV-1` cannot distinguish "the re-implementation is
faithful" from "the re-implementation inherited the same defect through the contract
text."** If the BATCH-011 driver carried a subtle process error, and the Coordinator
faithfully transcribed it into `P-ASRECORDED`, `IV-1` reproduces it and passes.
BATCH-012 therefore contributes **an independent re-implementation of a
Coordinator-transcribed process, not an independent re-derivation** — which is
strictly weaker than what `RC-F` asks for, and is essentially zero progress on
`RC-F`'s second route.

The contract is **honest** about this: it discloses the reading, says the process
spec is not a blind re-derivation, and forbids any card from declaring `RC-F`
discharged. **I concur with that non-discharge and add the sharper statement above.**
Note the asymmetry that partially rescues the design: the **`P-REPAIRED`** arm's
distinguishing feature — step 1 — has no analogue in the BATCH-011 driver, so the
primary arm is not transcribed from anything. It is only the *comparability anchor*
that is contaminated.

## 15. Scope, ceiling, confirmatory status (gate R5)

| check | verdict |
|---|---|
| computes any occupancy-normalised efficiency `E` | **NO** — forbidden in `admission_and_ceiling` and enforced by `IV-6`. The value `0.85` is named only as a hypothetical and excluded. |
| computes any yield ratio `R` | **NO** |
| touches any cost model | **NO**. `matched_baseline_position_RC7` is `DECLARED INAPPLICABLE` with a correct reason: the experiment solves no instance, so Pollard-rho and BSGS are not matched baselines and quoting one would be decoration. `EV-ECDLP-008` `O-11` is left unretracted and not restated. |
| un-fires or re-disposes `INV-4` | **NO** |
| declares `INV-5` either way | **NO** |
| moves a hypothesis status | **NO** — every named hypothesis is explicitly pinned. |
| claim tier | `toy`, with a correct and unusually complete scope paragraph and `correspondence: null`. |
| meets a completion criterion of GOAL-ECDLP-001 | **NO** under any outcome |
| specifies zero curve arithmetic | **YES**, exhaustively, with a forbidden-imports list and `ST-3` stop-and-report |
| `confirmatory_status` | **`exploratory_only`**, with the right basis (`RC-G`): inputs already committed ⇒ cannot be confirmatory; and it explicitly separates *pre-registration order* (a property of commit order) from *confirmatory standing* (a property of protocol stability over unseen data). **This is correct and is one of the strongest parts of the contract.** |
| no closure quorum claimed | correct |
| scope creep in the other direction (a binding condition answered in words) | **one**: `RC-F` — answered by a disclosure paragraph rather than by changing the thing required. The contract says so itself and does not claim discharge. |

## 16. `D-1` and `D-2` prophylaxis — watertight or merely stated?

- **`D-1`: watertight as a design, contingent in execution.** Keeping `status:
  review_required` / `approved_by: null` immutable and putting the determination in
  the `TASK-20260729-017` receipt plus `DEC-20260729-002` is structurally correct: an
  immutable file cannot carry a mutable determination, and the file says so in its own
  text so a later reader is not misled. It fails only if `TASK-20260729-017` does not
  actually record the determination — which is the exact failure `D-1` names. Pre-dispatch
  condition **PD-6** below makes that recording a stated obligation rather than an
  assumption.
- **`D-2` / `PRED-ID`: correctly drafted and *violated in the very file that declares
  it*.** The rule — every pre-registered expectation is a named enumerated tuple list
  evaluated on set identity, never cardinality, with `|R ∩ P|`, `|R \ P|`, `|P \ R|`
  reported — is exactly right, and its stated motivation (BATCH-011's `PC-2` matched
  eleven flips on only five of the same cells) is exactly right. But the contract's
  own pre-registered sets (§6's CR-1 21-list, §6's CR-2 4-list, §7's 27-list) are
  wrong at four named tuples under the contract's own §4 counterfactual (§5 above).
  **The prophylaxis is stated, not achieved.**

---

## 17. Gates reached

| gate | status |
|---|---|
| R1 criterion firability in both directions | **REACHED.** Falsifiable in aggregate; the named PRED-ID sets are defective. |
| R2 denominators, replicate schedule, criterion-free diagnostic block | **REACHED.** Both readings pre-registered without ambiguity (`sem_rep = s_rep/sqrt(n_rep)`, `s_rep` with `n−1` denominator, both required to pass); schedule fixed to C-14 with an explicit and correct reason for not raising it; the 10000-replicate block is labelled as feeding nothing at three separate places and executes last. Residual: CR-3's `sem_001` mis-sourced (§10). |
| R3 second-order terms, per-term | **REACHED.** None can fire alone. |
| R4 sourcing | **REACHED.** Every per-cell number traces to `IN-1` at `2fb2bb7a` or to arithmetic shown. **No figure is imported from a review report as primary, from an unarchived probe, from a recollection or from an estimate.** One mislabel (`sem_001` "QUOTED"); one number that does not hold (`< 2e7` draws); one wrong tail bound (CR-2 `< 1e−20`). |
| R5 scope and ceiling | **REACHED.** Clean in both directions except the `RC-F` item, which is disclosed. |
| R6 snapshot integrity | **REACHED**, with the named limit that the whitespace-only repair is unverifiable against Git. |
| R7 pre-dispatch conditions | **REACHED** — see `contract_review.yaml`. |
| R8 provenance and limits | **REACHED** — see `contract_review.yaml`. |

**Not reached inside the cap:** I did not re-derive the BATCH-011 `P_pred` identity at
all 49 cells (`TASK-20260729-007` did, to a maximum absolute difference of 0.0, and
`TASK-20260729-008` re-derived it from the contract text; I re-derived it at the four
INV-4-failing tuples only and confirm those four). I did not audit
`docs/task-lifecycle.md` section 5 line by line against the `RC-G` claim; I checked
that the `RC-G` text quoted in the BATCH-011 red-team report matches the contract's
`confirmatory_status_basis`, and it does. I did not review the BATCH-012
`dispatch_queue.json` `execution_gate` block beyond the `TASK-20260729-016` entry.
