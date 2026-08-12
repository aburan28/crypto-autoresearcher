# TASK-20260803-535d15 — what the validator actually re-derived

Independent validation of `TASK-20260803-e53ce2` at snapshot commit `8cc51677`.
Verdict and per-claim status live in `report.yaml`; this file records the
derivations, in the order I did them, so a later reader can repeat them.

**Scope reminder.** Everything below concerns a dimension-60, q=127 measurement
on one LWE instance. It is not crypto-scale evidence, it says nothing about any
FIPS 203 parameter set, and it supports no ML-KEM claim. Rule 12 is UNMET and
UNWAIVED; no `EV-*` or `KN-*` status changes.

---

## 1. What I refused to take on trust

The producer's transcript, its `verify_raw.py`, and its `repro/` directory all
exist in the shared scratchpad. I read them to learn what was claimed, and then
re-derived every number with code that shares nothing with either. Where a claim
was checkable only from the committed JSON I said so; where it needed the
instrument I re-ran the instrument.

Three claims turned out to need an actual re-run, because the committed data
alone cannot settle them:

1. the lattice-membership certificate (the dual vectors are not emitted);
2. that the sieve output is a function of `A` alone;
3. content-identical reproduction.

I did all three.

---

## 2. Artifact and commit integrity

Recomputed sha256 for all six artifacts. They match `receipt.json`'s
`artifacts[]` and all six entries of the archive receipt's
`source_path_sha256` — including `receipt.json` itself, which the producer
correctly could not self-hash and which the coordinator's receipt does hash
(`d92002…7fd8`).

For each artifact, `git show 8cc51677:<path> | sha256sum` equals the worktree
hash. This is a Coordinator-committed snapshot, not a working-tree receipt.

`d2f52187` (HEAD at run time, per the transcript and `receipt.json`) is an
ancestor of `8cc51677`; the single intervening commit `abc344ac` changes one
line of `dispatch_queue.json` and no producer artifact. The transcript's
`git status --porcelain` at 18:23:46Z shows exactly one untracked path, the
task's own output directory — consistent with `dirty_tree: false` as qualified.

---

## 3. Did the instrument verification precede the measurement?

Asked directly: is the ordering shown, or asserted?

It is **shown, by two sources that agree and only one of which the producer's
recorder writes.**

The transcript records: instrument verified 18:25:33Z → smoke 18:30:30Z and
18:31:40Z → official measurement 18:31:51Z. Independently, filesystem mtimes
(which `rec.sh` does not set) give:

```
18:24:01  scratch/gmplink/            (the g6k link fix)
18:25:23  scratch/verify_instrument.py  (last edit; the 18:25:33Z run used it)
18:31:32  <task>/measure_scores.py
18:32:11  <task>/raw_scores.json, results.json
18:34:16  <task>/rebuild_transcript.txt
18:37:35  <task>/report.md
18:38:37  <task>/receipt.json
```

Every ordering the transcript asserts is reproduced by the mtimes. The honest
limit: mtimes are settable in principle, so this is strong corroboration, not
attestation. It does not matter much, because I reproduced the measurement's
content from scratch regardless.

I also re-verified the instrument myself against `KN-TECH-14efa5`, with my own
script:

```
BKZ-30 dim60 q=3329: ||b0|| 160.4 -> 130.3 in 0.31s   (recipe: 160.4 -> 130.3, 0.3s)
gauss_sieve dim50 q=3329: db = 4075 vectors in 0.95s  (recipe: 4075 in 0.94s)
gotcha 1 reproduced: RuntimeError: Cannot open strategies file.
gotcha 2 reproduced: ValueError: Siever requires UinvT enabled
```

Both recipe numbers and both documented gotchas reproduce exactly.

---

## 4. Seeds: the instance really is the recorded one

`numpy.default_rng` with the recorded seeds regenerates, exactly:

| object | seed | matches emitted |
|---|---|---|
| `A` (35×25), `s`, `e_main` | 20260803001 | yes |
| `b_main = A s + e mod q` | (recomputed) | yes |
| `b_null` | 20260803003 | yes |
| all 6 decay error vectors **and** their `b` | 20260803004 | yes |
| 16 uniform + 8 secret-distribution candidates | 20260803002 | yes |

The 8 near-miss candidates equal `s` with `+1` at coordinate `i mod n`, as
stated. All 33 candidates are pairwise distinct and none coincides with `s`
(the file's coincidence flags are correct). `|s|∞ = 2`, `|e|∞ = 4`, empirical
`e` sd 1.929 — the three figures in report.md §2.

This matters more than it looks: it means the committed `A` and `s` were not
substituted after the fact for anything.

---

## 5. The certificate, verified independently

`raw_scores.json` does not contain `(x, y)`, so the membership certificate is
not fully checkable from the file. What *is* checkable from the file:

> `t_i(correct)` on MAIN equals the independently emitted `x_i·e` for all
> 17,919 vectors.

That certifies `(Aᵀx − y)·s ≡ 0 (mod q)` per vector — one linear functional of
the membership residual, not the whole thing. Worth having, not sufficient.

So I re-ran the sieve. My driver builds `B = [[I_m, A],[0, q·I_n]]` from `A`,
sets the fpylll seed to 20260803005, runs `LLL.reduction`, then
`Siever(..., seed=469431436621)`, `initialize_local(0,0,60)`, `bgj1_sieve()`.
It produced **17,919 vectors in 16.76 s** (producer: 17,919 in 16.55 s).

My own certificate check, on those vectors:

```
y == A^T x (mod q):   17919 x 25 = 447975 integer entries,  0 nonzero
all-zero vectors:     0
second route: B^-1 v integral for all 17919 vectors, max deviation 1.31e-13
```

The second route is deliberately independent of the first: it tests membership
in the lattice generated by the *original, unreduced* basis, without reference
to the `y ≡ Aᵀx` form at all. The producer's "17919 checked, 0 violations" is
exact.

I also confirmed the abort path is real: `measure_scores.py` lines 241–246 dump
`aborted: true` and `sys.exit(3)` if the certificate fails; the first scoring
line is 342. Nothing scores before the certificate.

---

## 6. The secret-leakage question

This was the check that mattered most, and it has three parts.

**(a) One code path.** `phases_for_target` (lines 280–284) computes every
candidate in one vectorised expression:

```python
center_mod(X.dot(bvec)[:, None] - Y.dot(cand_matrix.T), q).T
```

The correct secret is row 0 of the same `cand_matrix`. There is no branch on
candidate index in any computation. The file's only `ci == 0` test (line 359)
decides whether a *cosine array is emitted* for decay targets; it changes no
value.

**(b) The vectors cannot know the secret — proved, not argued.** My driver runs
in a deliberately different order from the producer's: derive `A`, build the
basis, run LLL, run the sieve **to completion**, and only then draw `s`. If the
database it produces is the producer's database, then the producer's database is
a function of `A` and the fixed seeds alone.

It is. Three independent bindings:

- my `Y` equals the `y` matrix I recovered from the *committed phases*
  (§7 below), elementwise and in row order;
- my `‖v‖²`, `‖x‖²`, `‖y‖²` equal the emitted `norm2_v`, `norm2_x`, `norm2_y`;
- my `centre_mod(X·e, q)` equals the emitted `x_dot_e_main`.

**(c) The scores.** I recomputed all 33 candidate phase arrays for MAIN and all
33 for NULL — 66 arrays × 17,919 = 1,182,654 integers — with my own uniform
scorer. **Mismatches: 0.**

The near-miss candidates *are* built from `s`. That is disclosure, not leakage:
they are labelled, separately reported, and the whole point of the population.
It does have a consequence for the null's rank statistic — see defect 3.

---

## 7. Recovering the dual vectors from the phases (and what it broke)

For `(x,y) ∈ L`, `t(s') = t(s) − y·(s' − s) (mod q)`. The 32 emitted candidate
differences `s' − s` have **rank 25 = n over Z₁₂₇**, so `y` is determined
completely for every vector *from the committed JSON alone*.

Doing the elimination gives 25 solved coordinates and 7 redundant equations per
vector — **7 × 17,919 = 125,433 consistency constraints, all satisfied, zero
residuals**. The recovered `‖y‖²` equals the emitted `norm2_y` for all 17,919
vectors, and recovered entries lie in `[−9, 10]` against `q/2 = 63`.

Two things fall out.

**The null and decay controls provably reused the same vectors.** I re-derived
`y` from the NULL target's phase differences and from all six DECAY targets'.
Every one matches the MAIN-derived `y` exactly. This is a stronger check than
the producer offered: "identical dual vectors" is not asserted, it is measured
across all eight targets.

**Limitation 1 is wrong as written** (defect 1). Since `y` is recoverable and
`t(correct)` is emitted, *any* candidate secret can be scored exactly from the
JSON. I picked one the producer never scored and scored it both ways:

```
s'' = [3,1,-1,-1,-3,1,0,3,-1,-2,-1,-1,-1,0,-1,0,0,2,-3,0,3,-3,1,-2,1]
from raw_scores.json alone:      +0.174586
from the re-run sieve vectors:   +0.174586
phase arrays identical:          True
```

What *is* genuinely lost is `x`: at best 33 independent linear constraints on 35
unknowns mod q, so a reviewer cannot score a new **target** `b`, cannot get `x·e`
for a new error, and cannot check the full certificate from the file. The
producer's limitation errs conservative — it understates its own artifact — but
it is inaccurate, and the accurate version is the one that should drive the
batch-2 fix (emit `x`).

One more thing the recovery showed, which nobody claimed: **all 17,919 `y`
columns are distinct and no column's negation appears.** The database is 17,919
genuinely distinct vectors, one per ± pair. Any batch-2 effective-sample-size
argument can use `N` as-is.

---

## 8. Every reported number, recomputed

From the raw integer phases, with my own code: 72 cosine arrays (equal to
`round(cos(2πt/q), 6)` elementwise), 96 per-candidate means, 8 correct-label
means, 8 wrong mean-of-means, 8 wrong max/min/sd (ddof=1), 8 ranks, all array
lengths `= N`, every phase centred in `(−q/2, q/2]`.

**Total mismatches: 0.** The producer's "72 arrays / 96 means / 8 ranks" counts
are exact.

Both `report.md` group tables reproduce cell by cell, MAIN and NULL. `‖v‖² =
‖x‖² + ‖y‖²` holds for all 17,919. Norms 218 / 315 / 329 / 311.405 match.
`x·e` sd 25.63, range `[−63, 63]`, 76.69 % below `q/4` — all three to the digits
quoted.

Rank uses a strict `>`, so an exact tie would favour the correct label. No tie
occurs anywhere (smallest gap 3.69e−05, in the NULL), so the bias had no effect.
Flagged for batch 2, where coarser statistics could produce one.

---

## 9. The null object: right shape, three caveats

The null is of the right shape. It replaces `b` with a uniform draw and changes
nothing else, and I verified that rather than assuming it: same candidate list in
the same order, same `N`, `b_null` regenerates from its seed, no error vector
injected, and — decisively — the same recovered `y` matrix (§7).

It behaves as a null must:

```
correct-secret mean      +0.003298   (MAIN: +0.427375)
rank                     18 of 33    (MAIN: 1 of 33)
z vs pooled wrong        -0.0370     (report: -0.04)
chi^2 of phase histogram 139.4 on df=126   (MAIN: 6689.1)
per-vector mean/sem      +0.62       (MAIN: +99.21)
```

The chi-squared pair is mine, not the producer's, and it is the cleanest single
statement: under the null the phases are indistinguishable from uniform on `Z_q`;
on the real target they are nowhere near it.

Three caveats, all recorded as defects:

- The `−0.04` is a **pooled** statistic over the three populations the producer
  itself declares non-exchangeable. Group-wise the correct secret ranks 5/17 vs
  uniform (`z = +0.43`), **9/9 vs secret-distribution** (`z = −2.31`), 6/9 vs
  near-miss (`z = −0.08`). The conclusion survives every decomposition — 5/17 is
  the unconfounded one and it is mid-pack — but the number quoted is not robust
  to how the pool was built, by the producer's own criterion (defect 2).
- 8 of the 32 "wrong" candidates are `s + e_j`, i.e. near-copies of the item
  being ranked; under the null their means cluster at sd 0.00086 around the
  correct secret's +0.00330. "Rank 18 of 33" is therefore not the clean
  uniform-over-33 statistic a reader would assume (defect 3).
- One null draw. Under the null the rank is (modulo the above) uniform on 1..33,
  so a single realization cannot alone exclude a ~3 % chance of rank 1. The
  decay sweep and the within-draw statistics supply what one draw cannot, but the
  report never states the null's own resolution (defect 4).

The 9/9 result is itself an unreported observation (defect 7). It is in the safe
direction — under the null the nominal secret does *worse* than a comparison
group, which is the opposite of a leakage tell — and the numbers are visible in
the report's own table. But a 2.3σ group-level offset in a null is exactly the
kind of thing AGENTS.md rule 8 asks to be named.

---

## 10. The decay control, and an independent prediction

Reproduced exactly, monotone non-increasing over σ 0.5→16:

```
0.5 +0.949240 | 1 +0.841150 | 2 +0.427375 | 4 +0.018271 | 8 +0.004641 | 16 -0.003712 | unif +0.008977
```

The quantity that should decay does decay, and `report.md` §4.2 says so
explicitly — which is what the inventor protocol §3 asks for.

I went one step further than the package does. For fixed `x` and Gaussian `e`,

```
E[cos(2π x·e / q)] = exp(−2π² σ² ‖x‖² / q²)
```

Averaging that closed form over the **emitted** `norm2_x` array predicts, with no
reference to any score:

| σ | predicted | observed |
|---|---|---|
| 0.5 | +0.94592 | +0.94924 |
| 1 | +0.80097 | +0.84115 |
| 2 | +0.41466 | +0.42738 |
| 4 | +0.03334 | +0.01827 |
| 8 | +0.00001 | +0.00464 |
| 16 | +0.00000 | −0.00371 |

The prediction tracks the measurement across four orders of magnitude of decay.
(The residual departures are what a *rounded* rather than continuous Gaussian
should produce, largest at small σ where rounding bites hardest.) This is the
strongest single piece of evidence that the measured signal is the real
`‖x‖`-driven dual-attack score and not an artifact of the scoring code: an
artifact would not obey a functional form derived from norms it never touched.

It also means the signal is *entirely* attributable to `‖x‖`, which is why the
absence of a long-dual-vector arm (defect 5) is mitigated but not eliminated —
batch 2's target law is specifically about short vectors, and "because they are
short" is still untested against a comparator.

Note for the record: the σ=2 row in the sweep is the MAIN target, from a
different RNG stream than the five DECAY points. That is legitimate for the
correct-secret mean (which does not depend on the candidate subset) and
`report.md` labels the row "MAIN".

---

## 11. Reproduction

I re-ran the archived script with the archived seeds into a fresh directory and
diffed leaf by leaf against the committed `raw_scores.json`, hashing any array
longer than 200 elements so that every one of the ~2.5 M emitted integers is
covered.

```
leaves compared: 2942 vs 2942
DIFFERING LEAVES: 3
  .certificate.check_seconds       0.02  -> 0.022
  .targets[1].scoring_seconds      0.049 -> 0.035
  .targets[7].scoring_seconds      0.007 -> 0.006
```

Content identity holds completely. The producer's own repro differed in five
leaves, also all timings — so "five" is a timing coincidence rather than a
property (defect 6). The invariant the producer meant, "differs only in
wall-clock timing leaves", is exactly right, and the 1-byte size difference is
just `0.02` vs `0.022`.

---

## 12. Contract compliance

`states_a_finding: false`, `compared_against_assumed_law: false`. Every
occurrence of "MATZOV", "Nf" or "advantage law" in the package sits inside a
sentence declining the comparison. No `N`, no advantage, no success probability
and no cost figure appears in any output. `measure_scores.py` imports no
estimator and contains no sample-count formula.

The four "observations to check" are observations. They carry explicit
non-conclusion language — "Whether this matters for anything is unchecked",
"Unexplained; worth a look before any variance argument is made", "The sweep is
too coarse to locate that transition". There is no "we find/conclude/show" and
no "proves" anywhere in the package.

The near-miss observation's stated *mechanism* — "the phase differs by
`y_i·(s − s')` = a single coordinate of `y`, which is small for short dual
vectors" — is exactly correct; it is the identity I used to recover `y`, and the
recovered coordinates lie in `[−9, 10]` against `q/2 = 63`, which is the
quantitative content of "small".

`executor-implementation` resolves to `anthropic:claude-sonnet-5 (effort=medium)`
and no `AUTORESEARCH_*` variable is set, so the producer's `fallback_used: true`
is accurate and correctly recorded rather than silently substituted.

---

## 13. Where the validation ladder does and does not bite

`docs/inventor-protocol.md` §6 governs a *claimed improvement*. This batch claims
none — no speedup, no baseline ratio, no comparison. So the ladder is not
triggered, and the absence of a step-2 measured ratio here is **not** a failure.

That will change. When batch 2 compares against `MATZOV.Nf` it produces a claim
about a cost model, and at that point step 2 becomes mandatory and its absence
would be a `failed`. Recording it now so it is not discovered later.

Step 4 — "verify the reproducibility pointer is not a lie" — I exercised rather
than accepted: every artifact rebuilt from scratch and listed above, and the
sieve database itself rebuilt and bound to the committed phases.

Step 1 is where this batch actually sits: it isolates one assumption the
dual-attack complexity analysis rests on and measures it where measurement is
possible. That is the right rung for batch 1 of 6.

---

## 14. My own independence caveat

The task card requests `validator-independent`, an alias of `review-adversarial`.
No `AUTORESEARCH_*` is set and this session runs `claude-opus-5` — the same
condition the producer recorded, and I record it the same way rather than
silently substituting.

The consequence should be stated plainly: this validation ran in a genuinely
separate session, which satisfies `independent_session_required`, but on the
same underlying model as the producer. That is the correlated-judgement failure
mode AGENTS.md names for the closure quorum, in weakened form. It does not
affect the mechanical re-derivations above — arithmetic over 447,975 residual
entries and 125,433 consistency constraints does not care which model requested
it — but it should temper how much *independent corroboration* this report is
read as providing for the judgement calls, particularly the defect severities.

---

## 15. Bottom line

The data is real, the certificate holds, the secret is known only where it should
be, the null is of the right shape and behaves like a null, and the decay obeys a
functional form I derived independently of the package. Seven defects, all of
reporting accuracy, control scope or statistical presentation; none touches the
integrity of the measurement.

**ADMISSIBLE_WITH_DEFECTS.** Admissible as raw data for batch 2 to build on,
with defects 1–5 and 7 carried forward rather than dropped.

This says nothing about ML-KEM, demonstrates no speedup, and authorizes no
promotion.
