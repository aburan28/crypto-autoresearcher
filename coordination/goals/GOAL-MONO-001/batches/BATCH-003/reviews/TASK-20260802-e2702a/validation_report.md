# VAL-20260802-b68edf — independent validation of RUN-MONO-4b50b6-001

**Task** `TASK-20260802-e2702a` (validator) · **Goal** `GOAL-MONO-001` · **Batch**
`BATCH-003` · **Snapshot under review** `fdb8ef8fb8966dbf22d5c4457eaa37478e265284`
· **Receipt** `coordination/goals/GOAL-MONO-001/batches/BATCH-003/archives/TASK-20260802-d49dee/snapshot-receipt.json`
· **Frozen protocol** `MONO-m3-census-1.1.0-repair-cm-gate`

**Verdict: ADMIT_WITH_QUALIFICATIONS**

Everything the run package reports as a *measurement* is correct, reproduces, and
recomputes. I re-derived the mathematics from scratch rather than accepting
`contract.md` §2, and it holds — in one respect it is stronger than the contract
claims. The qualifications are (a) two negative controls whose pinned tolerances
make their PASS verdicts carry no information, (b) one declared control with no
recorded verdict, (c) four latent protocol-fidelity gaps in the harness that were
not exercised by this run but would matter on any re-use, (d) two headline
sentences that reach past what was proved, and (e) seven curves carrying a
factually wrong `generating_subgroup_order` field.

A passed validation here means this receipt is admissible evidence at the toy
tier. It supports no ECDLP claim, demonstrates no speedup, and authorizes no
promotion.

---

## Part A — snapshot and artifact integrity

### V-1 · Snapshot commit is exact, complete and self-contained · **PASS**

**Check.** Compared the working tree, the commit `fdb8ef8f`, and the receipt's
`source_path_sha256` map, path by path.

**Measured.** `fdb8ef8f` adds exactly 13 paths — the 12 producer artifacts plus
the receipt itself — and adds nothing else. Its parent is `67c2e5bf`, matching
`dispatch_queue.json /tasks[1]/archive.parent_sha`. All 12 declared hashes agree
across three places: receipt body, blob content at `fdb8ef8f`, and the current
working tree. The receipt's own sha256 is
`f01db2bc597e185f08a1527359177516624bcc87c6eb74cbfee764ffbdac1ffe`, matching the
queue's `path_sha256` entry. `commit_sha: null` inside the receipt is correct by
construction (a commit cannot name itself) and is bound by the queue's
`archive.commit_sha` at HEAD `10eb510e`. Working tree is clean. `raw-result.json`
and `results.json` are byte-identical (same sha256), i.e. the raw/derived split is
nominal, not a transformation.

**Disposition.** Committed-snapshot requirement satisfied. This is not a
working-tree-only receipt.

### V-2 · Protocol hash chain verified end to end · **PASS**

**Check.** Recomputed sha256 of
`coordination/.../TASK-20260725-705/monodromy_protocol.yaml` on disk and compared
against (i) `run_record.yaml code.protocol_sha256`, (ii) `specification.yaml
protocol.sha256`, (iii) the BATCH-002 snapshot receipt
`TASK-20260725-706/snapshot-receipt.json`.

**Measured.** All four values are
`19f81d50dacf5049f03188e7e02c20711b361c8b8bb60b89e9437533fb9f0eb9`.

**Disposition.** The executed protocol is verifiably the artifact that carried the
independent red-team PASS `RT-20260725-707`. Confirmed as claimed.

### V-3 · Provenance and resource records · **PASS with one gap (see V-22)**

**Measured.** `command.txt` matches `run_record.command` and `manifest.code.command`
verbatim and matches `results.json args`. `code.commit`
`88c40b217e79cf3876929ad74c74ed6c58dc74bc` resolves; `mono3_census.py` does *not*
exist at that commit, which is consistent with the declared `dirty: true` rather
than contradicting it. Environment, python version (3.11.15), stdlib-only
dependency list, exit status 0, stderr empty, stdout consistent with
`aggregate.controls`. Seeds: I recomputed
`SHA-256("GOAL-MONO-001|m3|p=<p>|seed=20260725")[:8]` big-endian for all four
primes and got 9446004407123940885 / 8827759564170234372 / 8937398639074714503 /
9999823381745507876 — exactly the recorded `stream_seed` values.

`resources.peak_memory_note` says memory was **not instrumented** and declines to
substitute an estimate. That is the correct disposition under the Validator
prohibition on substituting estimates for missing measurements; I record it as a
declared missing measurement, not a defect.

---

## Part B — protocol fidelity, parameter by parameter

### V-4 · Pinned parameter walk · **no parameter differs from the frozen value**

| frozen protocol field | pinned value | implemented / recorded | verdict |
|---|---|---|---|
| `cover.m`, `degree_in_T` | 3, 2 | `--m 3`, quadratic in `T`; `--m != 3` exits 2 | match |
| `cover.explicit_S3` | `(x1-x2)^2 T^2 − 2[(x1+x2)(x1x2+A)+2B] T + [(x1x2−A)^2 − 4B(x1+x2)]` | `s3_coeffs` transcribes it literally | match |
| `curve_sampling.primes` | 211, 431, 809, 1601 | same, all four | match |
| `min_sizes` | 3 | 4 sizes run | match (exceeds) |
| `curves_per_size_min` | 20 | 20 at each of 4 primes, 80 total | match |
| `seed` / `seed_stream_rule` | 20260725, SHA-256 truncation | recomputed identically (V-3) | match |
| `curve_search.a_range_rule` | `a ∈ {0..min(p−1,64)}` | `randint(0, min(p−1,64))`; all 80 curves have `A ≤ 64` | match |
| `curve_search.b_range_rule` | `b ∈ {1..min(p−1,64)}` | `randint(1, min(p−1,64))`; all 80 have `1 ≤ B ≤ 64` | match |
| `discriminant_nonzero` | `4A³+27B² ≠ 0` | enforced | match |
| `order_computation` | exact enumeration | `#E = 1 + Z + 2S`; algebraically exact | match |
| `require_prime_order_group` (random) | true | 80/80 `order_is_prime: true` | match |
| `reject_supersingular` / `reject_anomalous` | `#E = p+1` / `#E = p` | both enforced on every panel | match |
| `exclude_j_invariants` (random) | {0, 1728} | compared **in F_p**; 0/80 leaks (V-11) | match |
| `cm_exception_screen.min_curves_total` | 8 | 22 scored | match (exceeds) |
| `cm admission_override` | prime order NOT required | applied on 22/22; all 22 are composite-order | match |
| `never_merge_into_random_controls` | true | separate `panel_id`; no CM curve in random aggregates | match |
| `automorphism_artifact_panel` | j ∈ {0,1728}, quarantined | 3 curves, excluded from every aggregate | match |
| `census.samples_per_curve` | 30000 | 30000 × 105 curves = 3 150 000 | match |
| `sample_space` / `sample_draw` | uniform `(x1,x2) ∈ F_p²`, seeded | `rng.randrange(p)` twice per draw | match |
| `degenerate_loci` (3) | x1_eq_x2, leading_coeff_zero, multiple_root | all three tallied, not dropped | match |
| `cycle_type_vocabulary` (4) | split_1_1, inert_2, ramified, degree_drop | all four reported per curve | match |
| `required_metrics` (11) | listed | all 11 present on all 105 curves; each recomputes from raw counts | match |
| `factor_base_window.W` | 4 | `--window 4` | match |
| `generator_rule` | lex-smallest affine generator | see **V-21** — deviates on 7 curves | **deviation** |
| `chebotarev_predictions.split_1_1` | 0.5 | used as the reference for `delta_split_vs_S2` | match |
| `factorization_method` | exact; toy_allowed disc+Legendre, root scan | both implemented, both used | match |
| `error_tolerance.weil_floor_formula` | `2/√p` | recomputed on all 105, exact | match |
| `full_monodromy_multiplier` | 3 | envelope `3·(2/√p)` | match |
| `full_monodromy_test` | `|Δ| ≤ 3·weil` per admitted curve | implemented per curve | match |
| `cm_screen_completion_rule` | ≥8 scored, no reverified CM exception | implemented | match |
| `barrier_aggregate_rule` (i)–(v) | see V-17 | faithful for this run; two latent gaps | match with V-18/V-19 |
| `exception_family_rate_screen` | FAMILY_RATE_ALERT at ≥1/20 | **not implemented anywhere** | **omission (V-20)** |
| `claim_boundaries.tier` | toy | asserted in 6 artifacts | match |

The three parameters *added* by the contract beyond the protocol
(`--curves-per-prime 20`, `--out`, the two INSTRUMENT-* controls) all constrain
the run further and relax nothing. `--curves-per-prime 20` is exactly
`curves_per_size_min`.

### V-5 · CM screen composition, independently rebuilt · **PASS**

**Check.** I rebuilt the CM panel from the same 11 class-number-one
discriminants using my own code (independent modular inversion, χ-table and point
count) and compared against the recorded panel.

**Measured.** 6 / 4 / 6 / 6 curves at p = 211 / 431 / 809 / 1601 = 22, over the
discriminant union {−7, −8, −12, −16, −19, −27, −28, −43, −67, −163} — exactly ten
discriminants, exactly as the execution report states. Every rejection I
reproduced was `#E = p+1` (supersingular); no candidate was dropped for any other
reason. **D = −11 is supersingular at all four pinned primes** (`#E` = 212, 432,
810, 1602) — independently confirmed; the execution report's statement is
accurate. All 22 scored curves are ordinary, non-anomalous, labelled, and carry
`admission_override_applied: true`.

**Additional finding (positive).** **All 22 CM curves have composite order.**
Without the `CTRL-CM-ADMISSION` override the CM screen would have been *empty* at
every pinned prime, `CTRL-CM-GATE-FULL` would have failed, and
`FULL_MONODROMY_BARRIER_TOY` would have been forbidden. The BATCH-002 repair
discharging `OBJ-653-2` was therefore load-bearing in fact, not merely on paper.

**Not a gap.** The panel takes one specific twist per (D, p) rather than both.
Under the twist `x ↦ u x`, `Z` is invariant and `t ↦ ±t`; since
`Δ = (t² − 2pZ + Z² − 2p + 2Z)/(2p²)` depends on `t` only through `t²`, the split
density is exactly twist-invariant. Nothing is lost.

---

## Part C — the mathematics, re-derived independently

I did not take `contract.md` §2 on trust. Every statement below was re-derived by
me with tools that share no code with the harness.

### V-6 · Lemma `disc_T S_3 = 16 f(x1) f(x2)` · **VERIFIED SYMBOLICALLY**

**Check.** In `sympy` 1.14.0, over `Z[x1, x2, A, B]`, I transcribed the coefficients
directly from the **protocol's** `cover.explicit_S3` block (not from the harness),
formed `b² − 4ac`, and subtracted `16·f(x1)·f(x2)`.

**Measured.** `sp.expand(disc − 16 f(x1) f(x2))` is **identically 0**. Both sides
have total degree 6.

**Disposition.** The Lemma holds as a polynomial identity. Confounder `CF-NORM-S3`
is discharged universally in `(A, B)`, not merely on the four censused reference
curves.

### V-7 · The pinned polynomial really is the third Semaev polynomial · **VERIFIED (my own additional check)**

**Check.** The Lemma alone would hold for any polynomial with those coefficients;
it does not by itself establish that `S_3` is the *summation* polynomial. I
verified separately, symbolically, that with `P = (x1,y1)`, `Q = (x2,y2)` on
`y² = x³+Ax+B` and `x1 ≠ x2`, `S_3(x1, x2, T)` vanishes at both `T = x(P+Q)` and
`T = x(P−Q)`, after reducing `y1² → f(x1)`, `y2² → f(x2)`.

**Measured.** Both numerators reduce to **0**. Independently, the root product
`x(P+Q)·x(P−Q) − c/a ≡ 0`, the root sum `x(P+Q)+x(P−Q) + b/a ≡ 0`, and the chord
identity `(x(P+Q) − x(P−Q))² − 16 y1² y2²/(x1−x2)⁴ ≡ 0`.

**Disposition.** The contract's chord-formula proof sketch is correct as written,
and the object being censused is the right one. `CF-M2-SHADOW` (reusing an m=2
Legendre census) is excluded: the measured object provably depends on `S_3`, not on
`χ(f(x))` alone — though, per the Lemma, the two coincide *as a consequence*, which
is exactly the result.

### V-8 · Corollary B, by actual brute-force enumeration · **VERIFIED**

**Check.** I wrote a classifier from scratch that uses **no discriminant formula
and no Legendre symbol**: for each of the `p²` pairs `(x1,x2)` it scans all `T ∈ F_p`
and counts roots of the quadratic. I enumerated **all `p²` pairs** on nine curves
across three primes not used by the run (p = 23, 31, 37), chosen to cover
`Z ∈ {0, 1, 3}` at each prime, and compared against the closed form
`N_split = S²+N²−(p−Z)`, `N_inert = 2SN`, `N_ram = p²−(p−Z)²−Z`, `N_degdrop = p`.

**Measured.** All four counts agree **exactly** on all nine curves, e.g.
p=23, (A,B)=(1,2), Z=3: brute force (split, inert, ram, drop) = (180, 200, 126, 23),
closed form (180, 200, 126, 23), sum = 529 = 23². Every case partitions `F_p²`. The
derived expression `Δ = (t² − 2pZ + Z² − 2p + 2Z)/(2p²)` matched the enumerated
`N_split/p² − 1/2` to floating-point equality on all nine.

**Disposition.** Corollary B is confirmed by enumeration, not by re-using the
closed form. On the run's own 105 curves I additionally re-derived
`exact_enumeration.counts` from `(Z, S, N)` and matched every recorded value, and
confirmed `freq_ramified`, `freq_inert_2` and `freq_degree_drop = 1/p` against
their closed forms on all 105.

### V-9 · Corollary C, every curve in `results.json` · **VERIFIED, and the stated bounds are correct**

**Check.** For all 105 censused curves (all three panels) I recomputed
`p·|freq_split_exact − 1/2|` from `(Z, S, N, t)` and tested it against the
Z-dependent bounds and the uniform `< 4/p`. I also re-derived the bounds myself
from Hasse rather than accepting them:

- `Z = 0`: numerator `t² − 2p ∈ [−2p, 2p]` ⇒ `|Δ| ≤ 1/p`.
- `Z = 1`: numerator `t² − 4p + 3 ∈ [3−4p, 3]` ⇒ `|Δ| ≤ (4p−3)/(2p²) < 2/p`.
- `Z = 3`: numerator `t² − 8p + 15 ∈ [15−8p, 15−4p]` ⇒ `|Δ| ≤ (8p−15)/(2p²) < 4/p`.

**Measured.** Zero violations in 105 curves. Attained maxima:
`Z=0 → 0.9994/p` (p=809, A=46, B=17, t=−1, random panel);
`Z=1 → 1.6517/p` (p=211, CM panel);
`Z=3 → 3.9941/p` (p=1601, A=262, B=1242, t=−2, CM panel). Every curve satisfies
`Z ∈ {0,1,3}` and `t² ≤ 4p`. Panel maxima reproduce the manifest exactly:
random 0.9994, CM 3.9941, automorphism 3.9941.

**Disposition.** Corollary C holds, and the `Z=3` bound is nearly tight
(3.9941 against a strict bound of `4 − 15/2p = 3.9953` at p=1601). The contract's
"`Z = 1: ≤ 2/p (approx)`" hedge is unnecessary — the bound is strict — but
understating rigor is not a defect.

### V-10 · Corollary D — sound in its precise form, **overreaching in its headline** · **QUALIFY**

**What is actually proved, and I confirm it.** The identity is universal in
`(A,B)`, so for *every* `E/F_p` (`p > 3`, `4A³+27B² ≠ 0`) the exact split density
satisfies `|freq_split − 1/2| < 4/p ≤ 3·(2/√p)`. Hypothesis B of the protocol's
`discrimination` block — an ordinary locus with `abs_delta_split_vs_S2` beyond the
pinned envelope — is therefore **empty at m = 3**, independently of the census.
Correct.

**Stronger than the contract claims (my own derivation).** The contract argues
only about densities. The group-theoretic question `RQ-MONO-001` actually asks is
settled outright at m = 3: the cover is `T² + (b/a)T + (c/a)` over
`\bar F_p(x1,x2)`, and it is a genuine quadratic extension iff `16 f(x1) f(x2)` is
a non-square there. In the UFD `\bar F_p[x1,x2]`, `f` squarefree of degree 3 gives
`f(x1)f(x2) = ∏(x1−α_i)∏(x2−β_j)` with all six irreducible factors distinct and of
multiplicity exactly 1 — never a square. So the **geometric monodromy is `S_2` for
every ordinary (indeed every non-singular) curve at m = 3**, unconditionally, with
no census and no envelope. This is a stronger and cleaner statement than the one
the contract makes, and the Coordinator should prefer it.

**Where the headline overreaches.** "No exceptional locus can exist at m = 3"
(contract §2 Corollary D title; execution report §2 heading) is broader than what
is proved, in three respects:

1. It is a statement about *curve families* under the *uniform* `(x1,x2)`
   distribution. **Corollary E, in the same document, exhibits a locus in
   `(x1,x2)`-space — `FB × FB` off-diagonal — whose conditional split density is
   exactly 1, not 1/2.** That is a real deviation from quasirandomness, and it is
   the one that matters for relation supply. "No exceptional locus" and "here is a
   locus with density 1" sit two sections apart in the same artifact.
2. `freq_ramified = (p² − (p−Z)² − Z)/p²` *does* separate curve families by
   2-torsion (`Z ∈ {0,1,3}`) at order `2Z/p`. It is far below the pinned envelope,
   but the census reports four frequencies and the envelope tests only one.
3. The proved bound is on the **exact** density; the protocol's operational test is
   on the **sampled** density. The bridge is binomial concentration and is
   nowhere stated (see V-19 for the magnitude — it is overwhelming, but it is an
   unstated step).

**Recommended narrowing:** *"No ordinary curve at any prime has exact
`|freq_split − 1/2| ≥ 4/p`; the geometric monodromy is `S_2` universally at m = 3;
hence no exceptional **curve family** exists for the uniform split density. Loci in
`(x1,x2)`-space are a separate question and Corollary E answers it in the
negative."*

### V-11 · Corollary E — **VERIFIED BY BRUTE FORCE**, and the 1.5 / 2 distinction is handled correctly · **PASS**

**Check.** Rather than accept the algebra, I took every recorded factor base in
`results.json` (105 curves) and, for every ordered off-diagonal pair `(x1,x2)` in
`FB × FB`, classified the quadratic by **root scan over `F_p`**. I also checked
`χ(f(x))` for every window element, and recomputed
`exact_enumeration.joint_relation_proxy_rate` against my enumerated count.

**Measured.**
- **1196 ordered off-diagonal window pairs classified; 1196 split.
  `P(split | x1,x2 ∈ FB, x1 ≠ x2) = 1.000` exactly.**
- `χ(f(x)) = +1` on every window element except two automorphism-panel curves
  (p=809 A=795 B=0, p=1601 A=250 B=0) where the lex-smallest affine point is the
  2-torsion point `(0,0)`, giving `χ = 0`. Those curves have `W_eff = 1`, so they
  contribute no off-diagonal pair and the formula stays correct. **This is the
  exact caveat Corollary E's parenthetical "(no 2-torsion when the subgroup order
  is odd)" anticipates**, and it is realized only in the quarantined panel.
- Recorded `exact_joint` equals my enumerated `split_offdiag / p²` on all 105
  curves; zero mismatches.
- Ratio identity `ratio = (1 − 1/W_eff)/freq_split_exact` holds on all 105 to 1e-12.
- Over the 80 random controls the exact ratio range is **[1.4897, 1.5102]** —
  identical to the manifest and run record.
- Off-diagonal-only ratio `1/freq_split_exact` ∈ **[1.9814, 2.0711]** across all 105.

**Disposition on the 1.5-vs-2 question.** Handled correctly. The protocol's
`quasirandom_relation_prediction = freq_split·(W_eff/p)²` puts the full
`W_eff²` (diagonal included) in the denominator, while the truth is
`(W_eff² − W_eff)/p²` because the diagonal is `degree_drop`, never split. The ratio
is therefore `(1 − 1/W_eff)/freq_split`, which is `≈ 1.5` at the pinned `W_eff = 4`
and tends to `1/freq_split ≈ 2` as `W_eff` grows. Both numbers appear in the
contract, the run record and the execution report, each attached to the right
scope. No conflation.

**And it is a constant factor.** `1/freq_split` is bounded in `[1.98, 2.07]`
independently of `p`; nothing here touches an exponent. The artifacts say so
repeatedly and correctly.

---

## Part D — reproduction

### V-12 · Independent re-run reproduces the recorded results **byte for byte** · **PASS**

**Check.** I copied only `mono3_census.py` into a fresh scratch tree with the same
relative directory shape (so the recorded `args.out` string would be identical) and
executed the pinned command verbatim, on a different filesystem path, in a
separate process.

**Measured.**
- Exit status 0; stdout identical to `stdout.log` except the wall-clock number.
- Structural diff of the two JSON documents (recursive, every leaf):
  **exactly one differing leaf, `/wall_clock_seconds` (13.63 recorded vs 13.801
  mine).** 0 differences in `args`, `primes`, all 105 curve records, all
  histograms, all controls, `instrument_controls`, `aggregate`.
- Substituting `wall_clock_seconds = 13.63` into my output and re-serializing with
  the harness's own `json.dump(..., indent=1, sort_keys=True)` yields sha256
  **`9a0d8cd287c4de515251b6af8a1cb2200ca7cd975e6c5962a3dc8c3b2a89e637`** — the
  recorded hash, to the byte.

**Disposition.** The manifest's *scoped* determinism claim ("EVERY MEASURED
QUANTITY IS BYTE IDENTICAL … exactly one differing leaf, `wall_clock_seconds`") is
**accurate and now independently confirmed by a third execution**. The manifest's
own note that an earlier draft claimed unqualified byte-for-byte reproduction and
that this was corrected rather than left standing is the right disposition and is
consistent with what I observe.

---

## Part E — controls

### V-13 · All eleven reported controls, recomputed from raw results

| # | control | quantity I measured | threshold | verdict justified? |
|---|---|---|---|---|
| 1 | `CTRL-S3-IDENTITY` | 5 passed / 5 attempted at each of 4 primes; I re-evaluated all 12 recorded witnesses on the reference curves and got `S_3 = 0` exactly | ≥ 3 | **yes** (and superseded by the symbolic proof V-6, which is universal) |
| 2 | `CTRL-POS-PLANTED-SPLIT` | rate 1.0 at each prime over 396+399+399+400 = **1594** trials | == 1.0 | **yes**; note the protocol itself allows `ramified` to count as a pass, so the measured quantity is `P(split ∨ ramified)` |
| 3 | `CTRL-NEG-UNIFORM-WINDOW` | max \|obs − (W_eff/p)²\| = **1.927e-04** over 80 curves | ≤ 0.02 abs | arithmetically yes — **but see V-14, the control is inert** |
| 4 | `CTRL-NEG-SHUFFLED-WINDOW` | max \|obs − freq_split·(W_eff/p)²\| = **2.203e-04** | ≤ 0.03 abs | arithmetically yes — **but see V-14, inert** |
| 5 | `CTRL-IMON-PRODUCT-COVER` | 5-cycle rate 0.0000, 4+1 rate 0.0000 over 3938 squarefree samples | both exactly 0 | yes — **but see V-15** |
| 6 | `CTRL-IMON-RANDOM-DEG5` | 5-cycle **0.2026** (S₅ truth 1/5), 4+1 **0.2451** (S₅ truth 1/4), 3974 squarefree samples | ±0.05 / ±0.06 | **yes**, within 0.0026 and 0.0049 of the exact densities |
| 7 | `CTRL-J-EXCLUSION` | I recomputed `j` from `(A,B)` for all 80 random controls: **0** with `j ≡ 0` or `j ≡ 1728 (mod p)`; also 0 non-prime-order, 0 supersingular, 0 anomalous, 0 outside the `A,B ≤ 64` box, 0 with the CM override leaked in | 0 | **yes** |
| 8 | `CTRL-CM-ADMISSION` | 22 scored, 22/22 `admission_override_applied`, 22/22 labelled, **22/22 composite order** | all | **yes**, and load-bearing (V-5) |
| 9 | `CTRL-CM-GATE-FULL` | 22 ≥ 8 scored; **0** CM curves fail the envelope | ≥ 8 ∧ 0 exceptions | **yes**; gate uses raw rather than post-reverification failures, i.e. stricter than the protocol requires |
| 10 | `INSTRUMENT-SAMPLED-VS-EXACT` | max gap **0.00806** vs 4σ = **0.011547**; 0/105 fail | ≤ 4σ | **yes** — and this is the one control here with a *real* margin (1.43×), i.e. it could have failed |
| 11 | `INSTRUMENT-DUAL-CLASSIFIER` | **0** mismatches over 105 × 600 = **63 000** comparisons | 0 | **yes** |

Independently recomputed: 105 curves × 30000 = **3 150 000** specializations,
matching the manifest; per-curve histograms sum to `samples`; all four frequencies,
`delta_split_vs_S2`, `weil_floor_abs`, `delta_over_weil`, `passes_full_monodromy_test`,
`delta_relation_vs_quasirandom` and both degenerate counters recompute from the raw
counts with **zero** inconsistencies.

Scope note on controls 1 and 2: both are evaluated only on the **first** random
control curve at each prime (`ref = rand_curves[0]`), not per curve. The protocol
does not require per-curve evaluation, and V-6 makes control 1 redundant anyway.

### V-14 · `CTRL-NEG-UNIFORM-WINDOW` and `CTRL-NEG-SHUFFLED-WINDOW` are inert as pinned · **QUALIFY — this is the flagged risk, and it is real**

**Check.** Compared each control's absolute tolerance against the magnitude of the
quantity it is supposed to bound.

**Measured.**
- Uniform: expected rates `(W_eff/p)²` range **6.242e-06 … 3.594e-04**. Tolerance
  0.02 is **55.7×** the largest of them. The control passes for **any** observed
  rate in `[0, 0.0204]` — including an observed rate of exactly 0, i.e. a window
  matcher that never fires at all. It would catch only a catastrophic error at
  p = 211 (an `x1 ∈ FB ∨ x2 ∈ FB` bug gives ≈ 0.038 > 0.0204 there) and would miss
  the identical bug at p = 431, 809 and 1601.
- Shuffled: expected rates **3.079e-06 … 1.820e-04**; tolerance 0.03 is **164.8×**
  the largest. **48 of 80 curves observed exactly zero hits in 30000 draws.** Per
  curve the statistic is Poisson with mean ≈ 4 at p=211 falling to ≈ 0.07 at
  p=1601. There is no per-curve power to detect anything.

**Disposition.** The PASS verdicts are arithmetically correct and faithfully
implement the frozen protocol — the tolerances are the *protocol's* pins, not an
executor relaxation, so this is **not** a fidelity failure by the run. But under
`docs/inventor-protocol.md` §3 a control that cannot fail is not a control. Both
verdicts should be read as **"not evaluated"** rather than "passed", and neither
should be cited as evidence for anything. This is a defect in the frozen protocol
that BATCH-002 red-team review did not catch, and it should be carried forward as
a protocol correction, not attributed to this run.

### V-15 · The null-object test the run should have reported — I ran it · **the signal survives, decisively**

**Why.** The one positive statistical signal in this package is
`joint_relation_proxy_rate` exceeding `quasirandom_relation_prediction`. Per
inventor-protocol §3 a signal is an artifact until measured against a null object
of the same shape. The harness *has* the right null object — `rng.sample(range(p),
W_eff)`, a uniformly random subset of `F_p` of identical size, scored by the same
classifier on the same 30000 draws — but only compares it against the inert
tolerance of V-14, never as a ratio, and never pooled. So I pooled it.

**Measured** (80 random controls, 2 400 000 pooled draws):

| window | observed hits | protocol quasirandom prediction | ratio | z |
|---|---|---|---|---|
| **real** `FB` | **218** | 142.36 | **1.531** | **+6.34** |
| **null** (random subset, same size) | **104** | 142.36 | **0.731** | — |

Against the *mechanism-specific* predictions: the real window's Corollary-E
prediction (every off-diagonal pair splits) is 214.29 — observed/predicted =
**1.017**. The null window's independence prediction
(`freq_split × off-diagonal density`) is 106.77 — observed/predicted = **0.974**,
`z = −0.27`.

**Disposition.** The excess is present on the structured object and **absent on the
null object of the same shape**, at exactly the magnitude Corollary E predicts. The
quantity that should decay to the independence value when the structure is removed
does decay to it. This is a clean pass of the controls-before-belief obligation —
but the credit belongs to my recomputation, not to the run package, which reports
these numbers only through a tolerance that could not fail. Recommend the
Coordinator cite this table rather than the `CTRL-NEG-*` PASS flags.

Note also that Corollary E does not actually *rest* on a statistic: it is a proved
identity, brute-force verified in V-11 over all 1196 off-diagonal window pairs, and
directly witnessed by `CTRL-POS-PLANTED-SPLIT` (1594/1594). The §3 concern is
therefore about reporting hygiene, not about whether the claim is real.

### V-16 · `CTRL-IMON-*` validates a code path disjoint from the census classifier · **QUALIFY**

**Check.** Traced which functions produced each measurement.

**Measured.** Both IMON controls exercise `ddf_pattern` (distinct-degree
factorization over `F_p`, ~90 lines of polynomial arithmetic). Every one of the
3 150 000 census specializations is classified by `classify_primary`
(discriminant + Legendre) and cross-checked by `classify_secondary` (root scan).
**`ddf_pattern` shares no code with either.** Separately, `CTRL-IMON-PRODUCT-COVER`
tests a mathematically forced outcome: the irreducible-degree multiset of a
`deg 2 × deg 3` product is the union of the two factors' multisets, so `[5]` and
`[1,4]` are unreachable by construction. The control can only fail if `ddf_pattern`
hallucinates.

**Disposition.** `contract.md` §4 ("the harness is shown able to *detect* a
non-full group before any `S_2` agreement is trusted") and execution report
("the factorization harness demonstrably detects a non-full group") state an
implication that does not hold for the instrument that produced the census. The
IMON controls are legitimate borrowed sanity checks on a *different* routine. The
census classifier is instead validated by the dual code path (63 000 comparisons),
the closed form (105 curves, 0 mismatches), and — now — my independent brute-force
enumeration (V-8, V-11). Substantively the instrument is sound; the sentence
should be narrowed.

### V-17 · `CTRL-CLAIM-WORDING` is declared but has no recorded verdict · **GAP (discharged here)**

**Check.** `specification.yaml controls` declares ten protocol controls including
`CTRL-CLAIM-WORDING`. Its `success_criterion` requires "every declared control
reporting pass/fail alongside the quantity it measured".

**Measured.** `CTRL-CLAIM-WORDING` appears in **neither** `results.json
aggregate.controls` (11 keys, listed above) **nor** `run_record.yaml controls`
(11 entries) **nor** `stdout.log`. It is the one declared control with no verdict
anywhere in the run package.

**Disposition.** Partly defensible — it is a human/machine *audit* control and the
audit is the reviewer's job, not the harness's — but the specification declares it
without saying so, and the success criterion is therefore not fully met by the run
package alone. **I discharge it here**: see V-23. The Coordinator should record the
verdict as validator-supplied rather than run-supplied.

---

## Part F — outcome computation

### V-18 · `aggregate_outcome` faithfully implements `barrier_aggregate_rule` for this run · **PASS**

**Check.** I recomputed the entire outcome from the raw per-curve records, in my
own code, following the protocol text rather than the harness.

**Measured.**
(i) sizes with ≥ 20 admitted random controls = **4** (≥ 3 required);
(ii) random-panel curves failing `full_monodromy_test` = **0**;
(iii) exception candidates after reverification = **0** (`exception_reverification: []`);
(iv) instrument + admission gate (S3 ∧ planted ∧ IMON ∧ sampled-vs-exact ∧
dual-path ∧ CM-admission ∧ j-audit) = **True**;
(v) CM hard gate: 22 ≥ 8 scored, 0 CM envelope failures = **satisfied**.

**Independently recomputed outcome = `FULL_MONODROMY_BARRIER_TOY` = recorded
outcome.** The branch order is correct: instrument/admission failure →
`SCOPED_PROTOCOL_NO_GO`; exceptions → `EXCEPTIONAL_LOCUS_TOY`; < 3 full sizes →
`SCOPED_PROTOCOL_NO_GO`; CM screen < 8 → `RANDOM_PANEL_CALIBRATION_TOY`; else
`FULL`. The `RANDOM_PANEL_CALIBRATION_TOY` fallback matches
`qualified_non_closure_when_cm_unavailable`. The CM hard gate is a genuine gate,
not a rubber stamp — with the override removed it would have fired (V-5).

**`FULL_MONODROMY_BARRIER_TOY` is the correct emission** under the frozen rule.

### V-19 · The pinned `full_monodromy_test` could not have failed · **QUALIFY (not a defect, but the outcome_id carries no discriminating information)**

**Check.** Compared the pinned envelope against both the binomial noise floor and
the exact bound of Corollary C.

**Measured.** Binomial σ at n = 30000 is 0.002887. A sampled failure requires:

| p | envelope `3·(2/√p)` | fluctuation needed |
|---|---|---|
| 211 | 0.4131 | **143.1 σ** |
| 431 | 0.2890 | **100.1 σ** |
| 809 | 0.2109 | **73.1 σ** |
| 1601 | 0.1500 | **51.9 σ** |

and the *exact* `|Δ|` is bounded by `4/p` ≤ 0.019 at p=211 and ≤ 0.0025 at p=1601 —
i.e. 22× to 60× inside the envelope before sampling even begins.

**Disposition.** Clauses (i)–(iii) of `barrier_aggregate_rule` were structurally
guaranteed to pass once Corollary B is true; the only way they could have failed is
an instrument fault. So `FULL_MONODROMY_BARRIER_TOY` here certifies *instrument
integrity plus CM-screen completion*, not a discriminating measurement. The
execution report says almost exactly this ("uneventful in the way the protocol
anticipated … the interesting part is *why*"), which is honest. But when this
outcome is fed to `GOAL-ICEX-001` under `icex_feed.outcome_packages`, the feed must
carry the *identity* (Corollaries B–E), not the envelope agreement, as the load
bearing content — **and it must carry Corollary E, which invalidates the very
`relation_rate_input` that the `FULL_MONODROMY_BARRIER_TOY` package prescribes**
(`chebotarev_S2_split · (W_eff/p)²`). Emitting `FULL` and then feeding ICEX the
prescribed quasirandom proxy would propagate a model this run has disproved by a
factor of 1.5–2.

### V-20 · Four latent protocol-fidelity gaps in the harness · **not exercised by this run; must be fixed before any re-use**

None of these changed a single number in `results.json`, because each governs a
path that was never taken (0 exceptions, 0 control failures). Each is nonetheless a
real divergence from the frozen protocol.

1. **The reverification verdict is computed and then ignored.** `main()` runs
   `reverify_exception` on every envelope-failing curve and stores a `disposition`
   of `failed_infrastructure` / `admitted_exception_candidate` /
   `not_an_exception_after_reverification` — but `aggregate_outcome` branches on the
   *raw* `passes_full_monodromy_test` flags and never reads `disposition`. Under the
   protocol's `exceptional_locus_rule` an exception must be **reverified**, and
   `reverification_rule` says a code-path mismatch is
   "`failed_infrastructure` / invalid, **never exceptional evidence**". As written
   the harness would emit `EXCEPTIONAL_LOCUS_TOY` on a curve whose reverification
   said `failed_infrastructure`. That inverts AGENTS.md rule 5 and protocol
   `inconclusive_or_no_go`. **Highest-severity latent gap.**
2. **`CTRL-NEG-UNIFORM-WINDOW` and `CTRL-NEG-SHUFFLED-WINDOW` sit outside the
   outcome gate.** They enter `all_controls_pass` (and so the exit status) but not
   the `if not (...)` branch that selects `SCOPED_PROTOCOL_NO_GO`. Their
   `fail_disposition` is `invalid_or_failed_infrastructure`, so a failure should
   forbid `FULL` under clause (iv). As written the harness would print `FULL` with
   exit status 1.
3. **`exception_family_rate_screen` / `FAMILY_RATE_ALERT` is not implemented.** The
   string appears nowhere in the harness or the results. It is a pinned secondary
   screen; vacuous here (0 exceptions) but absent, not satisfied.
4. **`CTRL-S3-IDENTITY` and `CTRL-POS-PLANTED-SPLIT` are collapsed into one
   boolean** (`ctrl_pass`) and that single value is written to both reported control
   keys. The collapse is conservative — it can only turn a pass into a fail, never
   the reverse — so no false PASS is possible, but the two reported verdicts are not
   independently derived.

### V-21 · `generating_subgroup_order` is factually wrong on 7 of 105 curves · **DEFECT (no effect on any measurement)**

**Check.** For every curve I reconstructed the base point the harness actually uses
(`base = (order/ℓ)·G`, `ℓ` the largest prime factor, with the `base is None`
fallback) and computed its true order by repeated addition.

**Measured.** On 7 curves the fallback branch fires because the lex-smallest affine
point `G` does not generate `E(F_p)`, and the code then records
`generating_subgroup_order = #E(F_p)` while the base point's true order is much
smaller:

| panel | p | (A,B) | label | `#E` | recorded | **true ord(base)** | `W_eff` |
|---|---|---|---|---|---|---|---|
| CM | 211 | (180,120) | D=−12 | 196 | 196 | **28** | 4 |
| CM | 211 | (39,26) | D=−27 | 225 | 225 | **45** | 4 |
| CM | 211 | (167,41) | D=−28 | 224 | 224 | **32** | 4 |
| CM | 431 | (407,415) | D=−28 | 400 | 400 | **80** | 4 |
| auto | 211 | (0,103) | j=0 | 183 | 183 | **3** | 1 |
| auto | 809 | (795,0) | j=1728 | 820 | 820 | **2** | 1 |
| auto | 1601 | (250,0) | j=1728 | 1600 | 1600 | **2** | 1 |

On the other 15 composite-order CM curves the recorded value is correct.

Two consequences. (a) The protocol's pinned `generator_rule` — "smallest
lexicographic affine **generator of a maximal prime-order subgroup**" — is not
followed on those 7 curves: 28, 45, 32, 80, 3, 2, 2 are not prime-order subgroups
(the last two are, but 3 and 2 are not "maximal"). (b) The recorded field is simply
false, and `logging_required` names `cm_label_or_discriminant` and the protocol
text requires "record subgroup order with the curve log".

**Impact: none on any reported measurement or on the outcome.** `sub_order` is
logged and never used in a computation; `W_eff` and the window derive from `base`
itself, whose x-coordinates are genuinely x-coordinates of rational points, so
Corollary E survives (verified by brute force in V-11); and neither the CM gate nor
the relation-rate reading (scoped to the 80 prime-order random controls, where the
fallback never fires) depends on it.

**Disposition.** Under AGENTS.md rule 4 this must be **superseded by a Coordinator
correction record, not repaired in place**. I have not touched the artifact.

---

## Part G — claim discipline

### V-22 · Claim-tier and scope audit · **PASS**

- **Toy tier.** `claim_tier: toy` in `specification.yaml`, `manifest.yaml`,
  `contract.md` and the snapshot receipt. `field_bits: 11` is correct
  (1024 ≤ 1601 < 2048). "No extrapolation to 256-bit ECDLP" appears in 6 artifacts.
  `admissible_toward_closure_quorum: false` in the authorizing decision;
  `manifest.claim_boundaries` states "Not admissible toward the AGENTS.md rule 13
  closure quorum". Nothing in the package asserts above the toy tier.
- **`m ≥ 4` exclusion.** Present and correctly worded in `specification.yaml`,
  `contract.md` §6, `manifest.yaml`, `run_record.yaml` and `execution_report.md` —
  five artifacts, each stating `deg_T S_m = 2^{m−2} ≥ 4`, no analogous
  factorization claimed, `KN-OPEN-009` **fully open** there. I found no statement
  anywhere in the package that reaches beyond `m = 3`. Correct: the factorization
  `disc = 16 f(x1)f(x2)` is specific to the degree-2 fibre and has no `m ≥ 4`
  analogue in evidence.
- **The `3·(2/√p)` envelope.** Called a protocol pin and explicitly "not a
  theorem" / "never a theorem" in `contract.md` (2×), `specification.yaml` and
  `run_record.yaml`. "Theorem-backed" is used only for the Chebotarev 1/2
  prediction (`KN-LIT-039`) and for Corollary B's exact equality — the latter being
  legitimate, since I verified that identity symbolically (V-6) and by enumeration
  (V-8). No occurrence of "Chebotarev forces" or equivalent. `CF-ENVELOPE-OVERREAD`
  is not triggered.
- **Novelty statement.** `contract.md` §2: "This is an elementary consequence of
  the chord-and-tangent addition law and is **not** claimed as new mathematics";
  execution report repeats it and scopes the program's contribution to "the
  observation that it settles `KN-OPEN-009` at `m = 3`". **Accurate.** My own
  derivation in V-7 confirms the identity falls straight out of the chord formula;
  it is textbook-adjacent. The protocol's own `novelty_status: adaptation` is
  consistent.
- **No attack claim.** `certificate.kind: none` with an explicit rationale (no
  solve, no discrete log, no relation is claimed) — correct under
  `docs/claims-and-verification.md`; there is nothing here for a certificate to
  certify. "Confers no advantage over Pollard rho" is stated in three artifacts and
  is right: a constant factor 1.5–2 on a relation-rate *planning model* moves no
  exponent.

### V-23 · `CTRL-CLAIM-WORDING` — validator-supplied verdict: **PASS**

Discharging the control that V-17 found unreported. I audited every claim-bearing
sentence in `contract.md`, `specification.yaml`, `manifest.yaml`, `run_record.yaml`
and `execution_report.md` against `claim_boundaries.forbids`. All nine forbidden
categories are respected. Two sentences reach past what is proved and should be
narrowed before the language is reused in an evidence record or knowledge item —
**Corollary D's "no exceptional locus can exist at m = 3"** (V-10) and **"the
factorization harness demonstrably detects a non-full group"** (V-16). Neither is a
tier violation; both are precision failures.

### V-24 · Two labelling errors in the execution report, both conservative · **MINOR**

**Measured.** The outcome table row reads "every control curve inside `3·(2/√p)` |
yes, worst case `Δ/envelope = 0.135`". The recorded 0.1354 is
`delta_over_weil = |Δ| / (2/√p)`, i.e. `Δ` over the **Weil floor**, not over the
envelope. `Δ/envelope` is **0.0451**. Correspondingly, "the margin is never worse
than 7×" and `run_record.measurements.sampled_census` "inside the pinned
`3·(2/√p)` envelope with at least a 7× margin" describe the margin against the
Weil floor; the margin against the **envelope** is **22.2×**.

**Disposition.** The error understates the run's own margin, so it cannot inflate
any claim. Still a mislabel in an immutable artifact; record as a correction, do not
repair.

### V-25 · The symbolic verification is asserted with no receipt in the package · **GAP (discharged here)**

`contract.md` §2 states "Verified symbolically (`sympy.expand`, difference
identically `0`)" and `environment.json` notes "sympy was used once, outside this
run … it is not imported by the driver". No command, script, output or hash for
that verification is preserved anywhere in the run package. Under the artifact
policy an asserted computation should carry its receipt.

**Disposition.** The assertion is **true** — I reproduced it independently in V-6
from the protocol's own coefficient text, and the difference is identically zero —
so this is a completeness gap, not a fabrication. It is discharged by this report,
which now *is* the receipt.

---

## Part H — independence and inference provenance

### V-26 · Independence limitation, stated rather than papered over

`dispatch_queue.json` sets this task's `inference.policy: review-adversarial`,
`independent_session_required: true`, `fallback_allowed: true`, with
`authorized_fallback_models` = [`gpt-5.6-sol-xhigh`, `gpt-5.6-terra-medium`,
`claude-sonnet-5-thinking-high`, `claude-4.6-opus-high-thinking`,
`cursor-grok-4.5-high-fast`].

**Actual model I ran as: `claude-opus-5`.** That identifier is **not** in the
authorized fallback list, and it is **the same resolved model the producer
recorded** (`RUN-MONO-4b50b6-001` manifest: `resolved_model_id: claude-opus-5`,
`fallback_used: true`, `model_verified: false`). So:

- `fallback_used: true`, and the resolved model is outside the declared authorized
  set — recorded, not silently substituted.
- The session is independent (separate subagent context, no access to the
  producer's reasoning) but the **model is not**. Producer and validator judgements
  here are correlated by construction. This is exactly the failure mode AGENTS.md
  rule 13 guards against for goal closure, and while nothing in this batch is
  admissible toward that quorum, the Coordinator should weight this report
  accordingly and should not treat it as model-independent confirmation.
- **Mitigation, and why I think the report still carries weight:** the load-bearing
  checks here are not judgement calls. The symbolic identity, the brute-force
  enumeration over `p²` pairs on nine curves, the 1196-pair window enumeration, the
  byte-level reproduction, and the pooled null-object table are all mechanical and
  independently re-runnable by anyone with any model. The commands are in this
  report's `artifact_paths` section.
- `model_verified: false` throughout: no `orchestration.adapter doctor --probe`
  confirmation exists in this harness.

---

## Findings summary

| id | finding | severity | affects this run's numbers? |
|---|---|---|---|
| V-1 … V-3 | snapshot, hash chain, provenance all exact | — | — |
| V-4 · V-5 | pinned parameter walk: no parameter differs from the frozen value; CM screen rebuilt independently | — | — |
| V-6 … V-9 | Lemma, Semaev-identity, Corollary B (brute force), Corollary C (105 curves) all verified | — | — |
| V-10 | Corollary D sound but headline overreaches; the true statement is stronger (monodromy is `S_2` universally) | qualify | no |
| V-11 | Corollary E verified by brute force, 1196/1196; 1.5-vs-2 handled correctly | — | — |
| V-12 | independent re-run reproduces the recorded sha256 exactly | — | — |
| V-13 | all 11 reported controls recompute | — | — |
| V-14 | two negative controls inert (55.7× and 164.8× the quantity bounded; 48/80 zero-hit) | **qualify** | no (verdicts correct but uninformative) |
| V-15 | validator-supplied pooled null-object test: signal 1.531 on the real window, 0.974 on the null | — | strengthens |
| V-16 | IMON controls validate a code path disjoint from the census classifier | qualify | no |
| V-17 | `CTRL-CLAIM-WORDING` declared, no verdict recorded | gap | no |
| V-18 | outcome recomputed independently; `FULL_MONODROMY_BARRIER_TOY` correct | — | — |
| V-19 | the pinned test could not have failed (51.9σ–143.1σ); ICEX feed must carry the identity, not the envelope | **qualify** | no |
| V-20 | four latent fidelity gaps (reverification verdict ignored; window controls outside the gate; FAMILY_RATE_ALERT absent; two controls collapsed) | **defect, unexercised** | no |
| V-21 | `generating_subgroup_order` false on 7/105 curves | **defect** | no |
| V-22 · V-23 | claim tier, `m ≥ 4`, envelope wording, novelty all accurate; CLAIM-WORDING discharged PASS | — | — |
| V-24 | `Δ/envelope` mislabelled (0.135 vs 0.045); "7× margin" is 22× | minor | no |
| V-25 | symbolic verification asserted without a receipt; discharged by V-6 | gap | no |
| V-26 | validator resolved to the same model as the producer, outside the authorized fallback list | **limitation** | — |

## Obligations recommended to the Coordinator (I do not perform them)

1. **Correction record** (new ID, superseding — never an in-place edit) covering
   V-21 (7 false `generating_subgroup_order` values) and V-24 (the `Δ/envelope`
   mislabel).
2. **Narrow two sentences** before any evidence record, knowledge item or ICEX feed
   reuses them: Corollary D's headline (V-10) and the IMON reading (V-16).
3. **Protocol correction for BATCH-004+**: the `CTRL-NEG-*` absolute tolerances
   (V-14) and the four harness gaps in V-20, above all the ignored reverification
   verdict. These belong to the protocol and the harness, not to this run.
4. **If this feeds `GOAL-ICEX-001`**: the `FULL_MONODROMY_BARRIER_TOY` package's
   prescribed `relation_rate_input` (`chebotarev_S2_split · (W_eff/p)²`) is exactly
   the model Corollary E disproves. Do not propagate it unamended (V-19).
5. **Prefer the stronger statement** from V-10: at `m = 3` the geometric monodromy
   is `S_2` for every non-singular curve because `16 f(x1) f(x2)` is not a square in
   `\bar F_p(x1,x2)`. That closes `RQ-MONO-001` at `m = 3` outright, without an
   envelope and without a census — while `KN-OPEN-009` stays fully open for
   `m ≥ 4`.

---

```yaml
validation_report:
  id: VAL-20260802-b68edf
  task_id: TASK-20260802-e2702a
  goal_id: GOAL-MONO-001
  batch_id: BATCH-003
  run_ids: [RUN-MONO-4b50b6-001]
  experiment_ids: [EXP-MONO-4b50b6]
  snapshot_commit: fdb8ef8fb8966dbf22d5c4457eaa37478e265284
  protocol_version: MONO-m3-census-1.1.0-repair-cm-gate
  protocol_sha256: 19f81d50dacf5049f03188e7e02c20711b361c8b8bb60b89e9437533fb9f0eb9

  artifact_checks:
    - check: snapshot commit adds exactly the 13 declared paths and nothing else
      result: pass
    - check: all 12 producer hashes agree across receipt / commit blob / working tree
      result: pass
    - check: receipt rides inside its own archive commit with commit_sha null; queue records fdb8ef8f
      result: pass
    - check: parent_sha 67c2e5bf matches the queue archive block
      result: pass
    - check: protocol sha256 matches disk AND the BATCH-002 snapshot receipt (TASK-20260725-706)
      result: pass
    - check: command.txt == run_record.command == manifest.command == results.json args
      result: pass
    - check: execution-time commit 88c40b21 resolves; driver absent there, consistent with dirty=true
      result: pass
    - check: per-prime RNG stream seeds recomputed from the pinned SHA-256 rule
      result: pass (4/4 exact)
    - check: peak memory recorded as un-instrumented rather than estimated
      result: pass (declared missing measurement)
    - check: raw-result.json and results.json are byte-identical
      result: noted (raw/derived split is nominal)

  metric_recomputations:
    - metric: disc_T S_3 - 16 f(x1) f(x2)
      method: sympy 1.14.0 expand over Z[x1,x2,A,B], coefficients taken from the protocol text
      result: identically 0
    - metric: S_3(x1,x2,x(P±Q))
      method: symbolic substitution with y1^2 -> f(x1), y2^2 -> f(x2)
      result: 0 for both roots; root sum/product and chord identity residuals 0
    - metric: Corollary B exact counts
      method: brute-force root scan over all p^2 pairs, 9 curves, p in {23,31,37}, Z in {0,1,3}
      result: all four counts exact on 9/9; partition to p^2 exact; delta formula exact
    - metric: Corollary C bound
      method: recomputed p*|delta_exact| on all 105 censused curves; bounds re-derived from Hasse
      result: 0 violations; maxima 0.9994 (Z=0), 1.6517 (Z=1), 3.9941 (Z=3) against 1/2/4
    - metric: Corollary E conditional split probability
      method: brute-force root scan of every ordered off-diagonal FB x FB pair, all 105 curves
      result: 1196/1196 split; P(split | FB^2, x1!=x2) = 1.000
    - metric: exact ratio measured/quasirandom, 80 random controls
      result: [1.4897, 1.5102] reproduced exactly; identity (1-1/W_eff)/freq_split holds on 105/105
    - metric: off-diagonal ratio 1/freq_split_exact
      result: [1.9814, 2.0711] over 105 curves - the "factor ~2" is accurate
    - metric: all 11 protocol required_metrics, per curve, from raw histogram counts
      result: 0 inconsistencies over 105 curves
    - metric: total specializations classified
      result: 3150000 confirmed (105 x 30000)
    - metric: aggregate_outcome
      method: reimplemented from the protocol text against raw per-curve records
      result: FULL_MONODROMY_BARRIER_TOY - agrees with the recorded outcome_id
    - metric: full byte-level reproduction
      method: pinned command re-executed in an isolated tree
      result: exactly one differing leaf (wall_clock_seconds); substituting it reproduces sha256 9a0d8cd2...

  control_checks:
    - id: CTRL-S3-IDENTITY
      measured: 5 passed / 5 attempted at each of 4 primes; 12 recorded witnesses re-evaluated to S_3=0
      threshold: ">= 3"
      verdict: pass (justified; superseded by the universal symbolic proof)
    - id: CTRL-POS-PLANTED-SPLIT
      measured: rate 1.0 over 1594 trials (396/399/399/400)
      threshold: "== 1.0"
      verdict: pass (justified; protocol allows ramified to count, so quantity is P(split or ramified))
    - id: CTRL-NEG-UNIFORM-WINDOW
      measured: max |obs - (W_eff/p)^2| = 1.927e-04; expected rates 6.2e-06 .. 3.6e-04
      threshold: "<= 0.02 absolute (55.7x the largest quantity bounded)"
      verdict: pass_but_inert - passes for any observed rate in [0, 0.0204], including 0
    - id: CTRL-NEG-SHUFFLED-WINDOW
      measured: max gap 2.203e-04; expected 3.1e-06 .. 1.8e-04; 48/80 curves observed exactly zero hits
      threshold: "<= 0.03 absolute (164.8x the largest quantity bounded)"
      verdict: pass_but_inert - no per-curve statistical power
    - id: CTRL-IMON-PRODUCT-COVER
      measured: 5-cycle 0.0000, 4+1 0.0000 over 3938 squarefree samples
      threshold: both exactly 0
      verdict: pass (outcome is mathematically forced; tests only that ddf_pattern does not hallucinate)
    - id: CTRL-IMON-RANDOM-DEG5
      measured: 5-cycle 0.2026 (S_5 truth 0.2), 4+1 0.2451 (S_5 truth 0.25), 3974 squarefree samples
      threshold: "+-0.05 / +-0.06"
      verdict: pass (justified)
    - id: CTRL-J-EXCLUSION
      measured: j recomputed from (A,B) for all 80 random controls; 0 with j = 0 or 1728 mod p
      threshold: "0"
      verdict: pass (justified; the SELF-1 fix comparing j in F_p is real and load-bearing)
    - id: CTRL-CM-ADMISSION
      measured: 22 scored, 22/22 override applied and labelled, 22/22 composite order
      threshold: all scored CM curves
      verdict: pass (justified and load-bearing - without the override the screen would be empty)
    - id: CTRL-CM-GATE-FULL
      measured: 22 scored (>= 8); 0 CM curves outside the envelope
      threshold: ">= 8 and 0 reverified exceptions"
      verdict: pass (justified; uses raw rather than post-reverification failures, i.e. stricter)
    - id: INSTRUMENT-SAMPLED-VS-EXACT
      measured: max gap 0.00806 vs 4 sigma = 0.011547; 0/105 fail
      threshold: 4 binomial sigma
      verdict: pass (justified; the only control here with a real margin, 1.43x)
    - id: INSTRUMENT-DUAL-CLASSIFIER
      measured: 0 mismatches over 63000 comparisons
      threshold: "0"
      verdict: pass (justified)
    - id: CTRL-CLAIM-WORDING
      measured: NO VERDICT RECORDED ANYWHERE IN THE RUN PACKAGE
      threshold: claim_wording_audit_pass
      verdict: not_reported_by_run - discharged as PASS by this validator (V-23), with two sentences flagged for narrowing
    - id: VALIDATOR-SUPPLIED-NULL-OBJECT
      measured: pooled over 2400000 draws - real window 218 hits vs 142.36 quasirandom prediction (ratio 1.531, z=+6.34); null window 104 hits vs 106.77 independence prediction (ratio 0.974, z=-0.27)
      threshold: signal must vanish on a null object of the same shape
      verdict: pass - the excess is present only on the structured object, at exactly the Corollary E magnitude

  proof_architecture_checks:
    - check: baseline fixture - the closed form reproduces enumerated counts exactly, not approximately
      result: pass (9 curves fully enumerated at p=23,31,37; 105 curves reproduced from (Z,S,N))
    - check: quantifier fidelity - the identity is universal in (A,B), not per-curve
      result: pass (verified symbolically over Z[x1,x2,A,B], not numerically per curve)
    - check: observation collisions bound to enumerated scope
      result: pass (window claim enumerated over all 1196 off-diagonal pairs, not sampled)
    - check: method ceiling and nearby-object control
      result: partial - the shuffled window is the right nearby/null object but the run never scores it as a ratio; supplied by the validator
    - check: strictness witness for the claimed improvement
      result: not_applicable - no improvement, speedup or attack advantage is claimed

  heuristic_validation_checks:
    - check: pre-registered prediction
      result: pass - the Chebotarev(S_2) 1/2 prediction and the 3*(2/sqrt p) envelope are pinned in a protocol frozen 2026-07-25 and red-team-PASSed before this execution; Corollaries B-E were derived by the producer during implementation and are stated as derivations, not as fitted predictions, and I re-derived them independently
    - check: sample integrity - sample size, seeds, procedure in the manifest; statistics recomputed from raw
      result: pass - 30000/curve, master seed 20260725, per-prime SHA-256 stream all recorded and recomputed; every reported statistic recomputed from raw counts
    - check: correspondence validity
      result: not_applicable - no substitute-sampling correspondence is used; the census samples the object directly
    - check: scale binding
      result: pass - largest prime 1601 (11 bits), recorded as a limitation in 6 artifacts; no crypto-scale reading anywhere
    - check: cost-unit honesty / cost bookkeeping
      result: not_applicable - no concrete cost table, no per-attempt-cost x inverse-success-probability claim, no asymptotic claim is made

  scaled_down_ladder_checks:
    note: >-
      docs/inventor-protocol.md section 6 governs a claimed improvement that cannot
      be executed at the scale where it would matter. NO IMPROVEMENT, SPEEDUP OR
      ATTACK ADVANTAGE IS CLAIMED BY THIS RUN, in any artifact, and the ladder
      therefore does not apply. The one quantitative correction (Corollary E, a
      factor 1.5-2 on a relation-rate planning model) is explicitly labelled a
      constant that moves no exponent, is proved rather than extrapolated, and is
      verified by exhaustive enumeration rather than projected.

  defects:
    - id: D-1
      severity: latent_high
      statement: aggregate_outcome ignores reverify_exception's disposition; would emit EXCEPTIONAL_LOCUS_TOY on a curve whose reverification returned failed_infrastructure
      exercised_by_this_run: false
    - id: D-2
      severity: latent_medium
      statement: CTRL-NEG-UNIFORM-WINDOW and CTRL-NEG-SHUFFLED-WINDOW are outside the outcome gate although barrier_aggregate_rule clause (iv) requires all instrument controls to pass
      exercised_by_this_run: false
    - id: D-3
      severity: latent_low
      statement: exception_family_rate_screen / FAMILY_RATE_ALERT is pinned by the protocol and implemented nowhere
      exercised_by_this_run: false
    - id: D-4
      severity: low
      statement: CTRL-S3-IDENTITY and CTRL-POS-PLANTED-SPLIT are collapsed into one boolean written to both reported keys (conservative; cannot produce a false pass)
      exercised_by_this_run: true
    - id: D-5
      severity: medium
      statement: generating_subgroup_order records #E instead of the true base-point order on 7 of 105 curves (4 CM, 3 automorphism); the pinned generator_rule for composite-order curves is not followed on those 7
      exercised_by_this_run: true
      affects_any_reported_measurement: false
    - id: D-6
      severity: low
      statement: execution_report labels delta_over_weil (0.1354) as "Delta/envelope"; the true Delta/envelope is 0.0451 and the envelope margin is 22.2x, not 7x
      exercised_by_this_run: true
      direction: conservative (understates the run's own margin)
    - id: D-7
      severity: low
      statement: the sympy verification asserted in contract.md section 2 has no preserved command, script or output in the run package; discharged by this report's independent reproduction
      exercised_by_this_run: true

  limitations:
    - Toy primes 211-1601 (11 bits). Nothing here is crypto-scale evidence, and nothing extrapolates to 256-bit ECDLP.
    - Scoped to m = 3, where deg_T S_3 = 2. KN-OPEN-009 remains fully open for m >= 4; the discriminant factorization has no m >= 4 analogue in evidence.
    - The pinned full_monodromy_test could not have failed (51.9 to 143.1 sigma). FULL_MONODROMY_BARRIER_TOY certifies instrument integrity plus CM-screen completion, not a discriminating measurement.
    - Two of the eleven reported control verdicts (CTRL-NEG-UNIFORM-WINDOW, CTRL-NEG-SHUFFLED-WINDOW) carry no information at the pinned tolerances and must not be cited as evidence.
    - Corollary D's headline "no exceptional locus can exist at m = 3" is broader than what is proved; the precise statements are sound.
    - The validator resolved to claude-opus-5, the same model as the producer and outside this task's authorized_fallback_models. Session independence yes; model independence no.
    - No probe verification of any model identifier exists in this harness (model_verified false throughout).
    - Peak memory was not instrumented by the producer and is not reconstructible from the artifacts.
    - This report verifies evidence admissibility only. It decides nothing about hypothesis status, goal status, ECDLP hardness, or promotion, and is not admissible toward the AGENTS.md rule 13 closure quorum.

  verdict: passed
  verdict_label: ADMIT_WITH_QUALIFICATIONS

  inference:
    requested_policy: review-adversarial
    resolved_model_id: claude-opus-5
    reasoning_effort: null
    fallback_used: true
    fallback_within_authorized_list: false
    authorized_fallback_models: [gpt-5.6-sol-xhigh, gpt-5.6-terra-medium, claude-sonnet-5-thinking-high, claude-4.6-opus-high-thinking, cursor-grok-4.5-high-fast]
    model_verified: false
    independent_session: true
    independent_model: false
    note: >-
      Recorded, not silently substituted. Producer and validator resolved to the
      same model; the Coordinator must not treat this report as model-independent
      confirmation. Every load-bearing check in it is mechanical and re-runnable by
      any model from the commands recorded below.

  artifact_paths:
    - coordination/goals/GOAL-MONO-001/batches/BATCH-003/reviews/TASK-20260802-e2702a/validation_report.md

  artifacts_examined:
    - experiments/EXP-MONO-4b50b6/contract.md
    - experiments/EXP-MONO-4b50b6/specification.yaml
    - experiments/EXP-MONO-4b50b6/mono3_census.py
    - experiments/EXP-MONO-4b50b6/runs/RUN-MONO-4b50b6-001/manifest.yaml
    - experiments/EXP-MONO-4b50b6/runs/RUN-MONO-4b50b6-001/run_record.yaml
    - experiments/EXP-MONO-4b50b6/runs/RUN-MONO-4b50b6-001/execution_report.md
    - experiments/EXP-MONO-4b50b6/runs/RUN-MONO-4b50b6-001/results.json
    - experiments/EXP-MONO-4b50b6/runs/RUN-MONO-4b50b6-001/raw-result.json
    - experiments/EXP-MONO-4b50b6/runs/RUN-MONO-4b50b6-001/command.txt
    - experiments/EXP-MONO-4b50b6/runs/RUN-MONO-4b50b6-001/environment.json
    - experiments/EXP-MONO-4b50b6/runs/RUN-MONO-4b50b6-001/stdout.log
    - experiments/EXP-MONO-4b50b6/runs/RUN-MONO-4b50b6-001/stderr.log
    - coordination/goals/GOAL-MONO-001/batches/BATCH-002/tasks/TASK-20260725-705/monodromy_protocol.yaml
    - coordination/goals/GOAL-MONO-001/batches/BATCH-002/archives/TASK-20260725-706/snapshot-receipt.json
    - coordination/goals/GOAL-MONO-001/batches/BATCH-003/archives/TASK-20260802-d49dee/snapshot-receipt.json
    - coordination/goals/GOAL-MONO-001/batches/BATCH-003/dispatch_queue.json
    - coordination/goals/GOAL-MONO-001/batches/BATCH-003/BATCH-003-OPENING.md
    - ledger/decisions/DEC-20260802-505759.yaml
    - ledger/questions/RQ-MONO-001.yaml
    - knowledge/open-problems/KN-OPEN-009.md

  reproduction_of_this_validation:
    - "sha256sum coordination/goals/GOAL-MONO-001/batches/BATCH-002/tasks/TASK-20260725-705/monodromy_protocol.yaml   # expect 19f81d50..."
    - "git show --name-status fdb8ef8f   # expect exactly 13 added paths"
    - "mkdir -p /tmp/repro/experiments/EXP-MONO-4b50b6/runs/RUN-MONO-4b50b6-001 && cp experiments/EXP-MONO-4b50b6/mono3_census.py /tmp/repro/experiments/EXP-MONO-4b50b6/ && cd /tmp/repro && python3 experiments/EXP-MONO-4b50b6/mono3_census.py --primes 211 431 809 1601 --seed 20260725 --samples 30000 --window 4 --m 3 --curves-per-prime 20 --protocol-version MONO-m3-census-1.1.0-repair-cm-gate --out experiments/EXP-MONO-4b50b6/runs/RUN-MONO-4b50b6-001/results.json"
    - "python3 -c \"import sympy as sp; x1,x2,A,B=sp.symbols('x1 x2 A B'); a=(x1-x2)**2; b=-2*((x1+x2)*(x1*x2+A)+2*B); c=(x1*x2-A)**2-4*B*(x1+x2); f=lambda z: z**3+A*z+B; print(sp.expand(b**2-4*a*c-16*f(x1)*f(x2)))\"   # expect 0"
    - "brute force: enumerate all p^2 pairs at p in {23,31,37} classifying by root scan over T; compare to (S^2+N^2-(p-Z), 2SN, p^2-(p-Z)^2-Z, p)"
    - "window enumeration: for every curve in results.json, classify every ordered off-diagonal pair of factor_base.window by root scan; expect all split"
```

---

## Verdict

# ADMIT_WITH_QUALIFICATIONS

`RUN-MONO-4b50b6-001` is an **admissible research receipt at the toy tier**.

What earns the admission: the snapshot is exact and self-consistent; the executed
protocol is provably the reviewed one; the run reproduces to the byte under an
independent third execution; every reported metric recomputes from raw counts; the
outcome `FULL_MONODROMY_BARRIER_TOY` recomputes from the frozen
`barrier_aggregate_rule` including the CM hard gate; and the mathematics in
`contract.md` §2 — which I re-derived symbolically and by exhaustive enumeration
rather than accepting — holds, with Corollary D's underlying content actually being
stronger than the contract claims. The claim-tier, `m ≥ 4` and envelope-wording
discipline is clean throughout, and the novelty statement ("elementary consequence
of the chord formula, not new mathematics") is accurate.

What the qualifications are: two of the eleven reported control verdicts are inert
at their pinned tolerances and must not be cited as evidence; one declared control
had no recorded verdict and is discharged only by this report; four latent
protocol-fidelity gaps in the harness — above all an ignored reverification verdict
that could turn an infrastructure failure into "exceptional evidence" — must be
fixed before the harness is re-used; seven curves carry a false
`generating_subgroup_order`; two headline sentences reach past what was proved; and
the validator ran on the same model as the producer.

None of the qualifications changes a reported number, flips a control verdict, or
alters the emitted `outcome_id`, which is why this is `ADMIT_WITH_QUALIFICATIONS`
rather than `REVISE`. All of them require correction records rather than repairs.

**This admission means the receipt may be cited as evidence. It does not support an
ECDLP claim, does not demonstrate a speedup, does not authorize promotion, does not
change any hypothesis or goal status, and is not admissible toward the AGENTS.md
rule 13 closure quorum.**

*Validator: `TASK-20260802-e2702a` · report `VAL-20260802-b68edf` · resolved model
`claude-opus-5` · 2026-08-02. Handed to `TASK-20260802-32e4bf` for the ledger
archive; no ledger record, producer artifact or shared file was modified by this
task.*
