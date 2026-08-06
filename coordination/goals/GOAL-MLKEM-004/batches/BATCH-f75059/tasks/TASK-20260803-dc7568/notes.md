# RT-20260803-4d68e0 — what I re-derived, and how

Red team of BATCH-f75059 (GOAL-MLKEM-004 batch 2 of 6), task `TASK-20260803-dc7568`.
Reviewed snapshot `e08462acade9e8399211e0c08350964b57b48d02`, archiving
`TASK-20260803-5f11b7`. Independent session. I did not produce this package and
did not repair it.

**Scope binding on everything below.** m=35, n=25, d=60, q=127, secret CB η=2,
error rounded-Gaussian σ=2, one sieve, one modulus, and — for every computation
of my own — the **single primary instance**, because that is the only instance
whose vectors were emitted. TOY SCALE. No ML-KEM break claim, no security proof,
no FIPS 203 parameter set affected or cleared, no cost claim, no speedup.
AGENTS.md rule 12 UNMET and UNWAIVED, inherited. This note changes the status of
no `EV-MLKEM-*` record and no `KN-*` entry.

## 0. Provenance of every number in this report

Nothing here is copied from the producer's transcript. I loaded
`vectors.json` (3,751,898 bytes, sha256 `7f8c545d…`, hash and byte count both
confirmed against `results.json`) and recomputed. Two read-only calls were made
to the pinned lattice-estimator at `/tmp/le` commit `3e48ef4` (clean tree
confirmed by `git status --porcelain`) inside the producer's rebuilt venv
`/tmp/sagevenv-f75059`. No sieve was run, no instrument rebuilt, `maximum_runs`
unspent.

Scripts: `/tmp/claude-0/.../scratchpad/rt{1,3,4,5,6,7,8,9}.py`. They are scratch,
not deliverables; every number they produced is quoted in `report.yaml` with the
construction that produced it.

## 1. Integrity and geometry — reproduced exactly

```
CERT violating entries: 0 of 447975      all-zero vectors: 0      distinct y rows: 17919
<||x||^2> 181.84842904179922   <||y||^2> 129.55633684915452
a_x 0.8902087199960952         a_y 0.15855537136281617
||v||^2 min 218  median 315.0  max 329  mean 311.40476589095374
```

Every digit matches `results.json`, and `||v||²` matches BATCH-d2a728, which is
what the deliberate seed reuse (D-6) predicts. The certificate is genuine and
independent of g6k.

## 2. Ingredient 1 — reproduced, and D1 re-derived from first principles

My own 2000 fresh error draws:

| decile | ⟨‖x‖²⟩ | pred (σ²=4) | measured | ratio | ratio vs exact discrete cf |
|---|---|---|---|---|---|
| 1 | 130.84 | 0.52785 | 0.52023 | 0.98557 | 0.99874 |
| 5 | 178.77 | 0.41683 | 0.40913 | 0.98153 | 0.99959 |
| 10 | 230.85 | 0.32342 | 0.31481 | 0.97337 | 0.99651 |

global ratio 0.98039 (continuous) → 0.99833 (exact discrete cf); spread across
deciles 0.0122 → 0.0035.

The producer reports 0.9838 and 1.00045–1.00327. The 0.0034 offset between our
global ratios is 0.5 of the common-mode sem between two independent 2000-draw
sets. Functional form, monotone trend and the size of the D1 improvement all
reproduce.

**D1 is Sheppard's correction, and it is not a fit.** I computed
`Var(round(N(0,2)))` exactly from the rounding probabilities: `4.083333333333334`
= σ² + 1/12 to machine precision. That gives a closed form for the offset with
**zero free parameters**:

```
ratio = exp(-(1/12)·2π²‖x‖²/q²) = exp(-a_x/(12σ_e²)) = exp(-0.018546) = 0.98162
```

against the producer's reported −1.8% common offset, and per decile
`0.98675 … 0.97673` against my measured `0.98557 … 0.97337`. So the card's
question — principled or fitted after seeing the residual? — answers in the
producer's favour: it is a textbook correction, derivable analytically, with no
tunable quantity, and it predicts the *shape* as well as the offset.

Two things the producer got wrong about it anyway:

- The post-D1 shape correlation is reported as **+0.7571** (a sign flip). My
  independent draws give **−0.3887**. The sign is not stable between draw sets,
  so the residual trend after D1 is noise, not structure.
- §3 says the correction "shrinks at cryptographic q". It does not depend on q.
  It depends on `a_x/(12σ_e²)`, and `a_x` **grows**. See §6 below.

## 3. Ingredient 2 — reproduced, and the error bar is wrong

My own 2000 draws against the producer's:

| quantity | mine | producer |
|---|---|---|
| uniform sd across candidates | 0.005156 | 0.005184 |
| uniform ratio to √(1/2N) | 0.9779 | 0.9814 |
| secret-dist ratio | 3.996 | 3.9612 |
| near-miss ratio | 0.14289 | 0.14504 |
| correct − nm group mean | 0.002639 | 0.002658 |
| correct − best of 8 nm | 0.001522 | 0.001523 |
| P(correct first vs nm) | 0.984 | 0.986 |

`c4(16) = 0.983484`, `c4(8) = 0.965030` reproduce exactly from
√(2/(n−1))·Γ(n/2)/Γ((n−1)/2). D2 is standard, parameter-free, and applied in both
directions (it moves two of three groups *away* from unity). So D2 is not a fit
either.

**But the precision claim is wrong.** The 0.2% headline uses a per-draw sem of
0.00398 that treats error draws as the only variance source, when the 16
candidates and the database are held fixed across all 2000 draws. The batch's own
S9 gives an across-instance sd of 0.05209 (sem 0.0174), and my five independent
surrogate/candidate realisations give a realisation sd of 0.0148 on the same
quantity. The honest statement is *consistent with 1 within about 2%*, at which
point the 1.66% D2 correction is unresolvable.

## 4. The control the batch owed and did not run

`results.json → S8_nulls_P2 → NULL-V` declares `removes_object` = "the sieve
database itself — its lattice membership, its integrality, the exact 3-term
algebraic relations …" and `statistic` = "mean_i cos(2π x_i·e/q) for the correct
secret". **That statistic contains no y.** Lattice membership is the relation
`y = Aᵀx mod q`. A statistic that never reads y cannot depend on it, except
through ‖x‖, which the surrogate matches vector by vector by construction. So
with respect to three of the four objects it names, NULL-V cannot fail — the same
defect as batch 1's NULL-T, one level up.

So I applied the identical logic to the statistics that *do* read y. Three nulls,
2000 paired error draws each, five independent surrogate realisations:

- **rowperm_xy** — keep the exact multiset of x's, keep the exact multiset of
  y's, destroy only *which y is paired with which x*. Every length distribution,
  every column marginal, every entry multiset preserved. Only lattice membership
  removed.
- **randx_randy** — random directions matched to ‖x_i‖ and ‖y_i‖.
- **realx_colperm** — permute each column of Y independently across vectors,
  preserving the exact empirical marginal of every y_k.

| statistic | real | rowperm_xy | randx_randy |
|---|---|---|---|
| correct-secret sd over e | 0.088012 | 0.088012 | 0.087716 ± 0.000098 |
| near-miss sd ratio to iid | **0.142888** | **0.105408 ± 0.000991** | **0.104707 ± 0.001475** |
| correct − nm group mean | 0.002639 | 0.002582 ± 0.000006 | 0.002626 ± 0.000008 |
| correct − best of 8 nm | **0.001522** | **0.001761 ± 0.000011** | **0.001808 ± 0.000011** |
| P(correct first vs nm) | 0.984 | 0.9971 ± 0.0012 | 0.9970 ± 0.0015 |

(`realx_colperm` gives near-miss ratio 0.104814 ± 0.002603 — the effect is not
column-marginal heterogeneity; the per-column ⟨y_k²⟩ run 4.98–5.34 against a
uniform 5.18, and the eight perturbed coordinates are 0–7 with ⟨y_k²⟩ 5.13–5.34.)

**Reading.** The correct-secret row is a controlled null to 0.34%, which
reproduces the producer's 0.3% (their 0.088015 / 0.087785) with my own code and
my own seeds. The producer is right there and I confirm it. **Every row that
reads y is not.** The real database is 35.6% more spread across near-miss
candidates (≈38 surrogate sd) and separates the correct secret from its best
near-miss 13.6% worse (≈22 surrogate sd, and 5× the batch's own instance-to-
instance sd of 4.3e-5 on 1.571e-3). The effect survives a null that preserves
everything except membership of the dual lattice.

### 4.1 I applied the decay control to my own finding before believing it

The parameter that destroys a sampling artifact here is N. Excess
(real / rowperm) of the near-miss sd ratio:

| N′ | 500 | 2000 | 8000 | 17919 |
|---|---|---|---|---|
| excess | 1.062 | 0.987 | 1.193 | **1.354** |

The surrogate's ratio is flat at ≈0.105 across the whole range — its near-miss
spread decays exactly as 1/√N′, which is what independence predicts. The real
database's does not. That is a component of near-miss spread that **does not
decay with N**, which is precisely what the independence assumption forbids. It
is also **invisible at N′ ≤ 2000**, so the honest form of my own claim is heavily
scoped and needs CTRL-RT-9 (the 9 replicate instances) before anyone uses it.

## 5. P1 — what the impossibility actually says

`compare.py` lines 372–379:

```python
r1 = (m + k_lat == d)                # ⟺ k_enum + k_fft == 0
r2 = (k_enum + k_fft == n)           # ⟺ k_enum + k_fft == 25
if r1 and r2: admissible.append(...)
```

With `k = k_enum + k_fft` this is `if k == 0 and k == 25`. Enumerating 351 pairs
to discover that is a tautology in computational dress, and does not support
"WITH A PROOF" in an immutable commit message.

R1 is forced by the run — the sieve really did run on the full d=60 dual lattice.
**R2 is a free design choice**: the harness elected to score candidates differing
on all n coordinates. R1 alone pins `(k_enum, k_fft) = (0,0)`, and the tuple
`(m=35, 0, 0, p irrelevant by KA-3, β_bkz irrelevant by KA-5, β_sieve=60)` is
admissible. `wellposedness.md` §5 uses it, calls it R-A, and builds the length
sub-comparison on it. So the package's headline and its §5 contradict each other;
§6 states the correct, narrower thing.

**Consequence for KN-OPEN-016:** nothing here bears on whether `MATZOV.Nf` can
express a full-lattice distinguishing attack. It can — `k_lat = n`,
`k_enum = k_fft = 0` — and the estimator evaluates it. The batch found a property
of its own scoring protocol.

**And the R-A comparison is testable, which the batch denies.** I ran it:

```
lsigma_s modeled (R-A) = 24.4058   → prefactor 4.2971 → N_pred = 2.979
prefactor from correctly-instantiated measured length 8.1460 → N_pred = 5.646
measured LWE-vs-uniform distinguishing advantage: 0.402 at N'=5, 0.512 at N'=8,
                                                  0.651 at N'=16, 0.906 at N'=64
```

so Nf under-predicts the sample count by roughly 1.4×–2.7× here. My advantage is
max-over-threshold of (TPR − FPR); MATZOV's μ convention must be pinned against
Theorem 7.6 before that ratio is a number rather than an indication. But the
comparison is *makeable*, and the batch reported it impossible.

**Two "measured lsigma_s" in one package.** S2's prefactor P-C uses
26.9702 = √(σ_e²⟨‖x‖²⟩) (x-block only); S6 uses
29.2737 = √(σ_e²⟨‖x‖²⟩ + σ_s²⟨‖y‖²⟩). Nf's `lsigma_s` explicitly carries
`(Xs.stddev·q)^(k_lat/(m+k_lat))`, so 29.2737 is the correct analogue. The
much-quoted "reproduction of RT's low endpoint 24.854" therefore reproduces batch
1's instantiation, not a correct one.

**The 1015× spread is manufactured.** `k_lat = n − k_enum − k_fft` is an
identity, so L3 (k_enum=n ⇒ k_lat=0) cannot pair with P-A/P-C (k_lat=n), and L1
(k_lat=n) cannot pair with P-B (k_lat=0). Eight of the twelve cells are
internally contradictory. Over consistent cells, this run's β_sieve = 60 pins
N_pred to 2.979–4.112: a factor **1.38**, not 1015.

Separately, `wellposedness.md` §5's "MATZOV's length heuristic under-predicts by
17%" has an unnamed confound: the run sieved the **unweighted** norm
‖x‖²+‖y‖², while Nf's `lsigma_s` describes the σ-weighted lattice. Sieving the
weighted norm is a design change, not a null, and part of the 17% is that.

## 6. Two crypto-scale arithmetic checks the campaign could have run

Both are seconds of arithmetic against the pinned estimator and need no sieve and
no toy instance. They are the only computations in this campaign that speak at
cryptographic parameters.

**(a) Is the Gaussian idealisation of the error benign at scale?**

| error law | a=1 | a=5 | a=18.4 | N off by, at a=18.4 |
|---|---|---|---|---|
| rounded Gaussian σ²=1.5 (*not* ML-KEM) | 0.9460 | 0.7575 | **0.3598** | **7.7×** |
| CBD η=3 (ML-KEM-512 e) | 0.9997 | 0.9922 | 0.8989 | 1.24× |
| CBD η=2 | 0.9995 | 0.9884 | 0.8513 | 1.38× |

(exact characteristic function ∏ⱼ cos^{2η}(πxⱼ/q) against exp(−a); x drawn
isotropic in dimension 500 at q=3329, which is itself a heuristic about the
x-distribution and is flagged as such.)

So the D1 correction does **not** shrink at cryptographic q — for the error law
actually used it would be a factor 7.7 on N. It is benign for ML-KEM only because
ML-KEM's error is centred binomial, whose deviation from Gaussian is quartic
rather than a variance shift. Right conclusion, wrong reason, asserted in a batch
that says it asserts no extrapolation.

**(b) How much is the untestable p-term worth?** I re-ran KA-6 independently:

```
LWE.dual_hybrid(Kyber512, RC.ADPS16):  rop 2^115.50989392, β' 395, p 5, ζ 0, t 40, N ≈ 2^81.4
```

which reproduces the producer's 2^115.5099 and the repository's documented 2^115.5.
`estimator/lwe_dual.py:619-620` sets `cost["zeta"] = k_enum` and `cost["t"] = k_fft`,
so the ML-KEM-512 optimum is `k_enum = 0, k_fft = 40, p = 5`. At that point

```
exp(k_fft/3 · (σ_s π/p)²) = 2685.7 = 2^11.39        k_fft·log p = 64.38   vs  log(1/μ) = 0.693
```

The factor this design sets identically to 1 is **11.4 bits of N** at the
parameter set the goal names, and this design's corner (`k_enum = k_fft = 0`) is
exactly the corner the estimator's optimiser never selects there. That, not
PAC-1, is the decisive argument for changing the design.

## 7. The batch-1 corrections — reproduced, and they do not overturn anything

1000 fresh uniform targets on the emitted database, my own draws:

```
rank of nominal secret within secret-distribution group: 4.949 ± 2.653 of 9   (producer 5.051 ± 2.571)
P(rank = 9, i.e. batch-1's "9 of 9")                   : 0.108               (exchangeable predicts 1/9 = 0.111)
rank within near-miss group                             : 5.006 ± 1.439, P(first) 0.005
```

So the producer's claim is right: batch 1's `9 of 9, z = −2.31` is an ordinary
1-in-9 draw. **But `EV-MLKEM-da9e3b` OBS-6 says only that it happened and that
the package did not name it — both still true.** The observation is *explained*,
not falsified. Likewise OBS-4 already says "resampling the error gives
+0.4029 ± 0.0856"; S9's instance sd of 0.0041 is new information, not a
contradiction. The one sentence now imprecise is the `strength_note`'s universal
"every headline number carries roughly 20% unreported uncertainty".

**Recommendation: do not supersede `EV-MLKEM-da9e3b` on these two grounds.** The
card's premise that both corrections "overturn" committed content is not
supported by the records. Record them as supplements in the batch-2 evidence
record. The sentence in that record that *does* need a superseding note is OBS-2
("the 411x / N_eff = 44 inflation is therefore a controlled null"), which is
correct for the correct-secret statistic and must not be carried to any statistic
involving y.

## 8. Security-claim audit of the package and of commit `e08462ac`

I read every sentence of `report.md`, `wellposedness.md`, `results.json`'s scope
fields, `receipt.json` and the commit message, looking specifically for an ML-KEM
break, a security proof, a FIPS 203 parameter set affected or cleared, a speedup,
a cost claim, or a status change to an `EV-*`/`KN-*` record.

**None found.** The scope banners are present, first, and binding; `results.json`
carries `states_a_conclusion: false`; the commit's TOY SCALE paragraph is correct
and complete; `git_dirty: true` refers to the task's own untracked output
directory and is benign.

The overclaim in this commit is of a different kind, and it is real:

> "PAC-1 STANDS UNREFUTED … the headline observable CANNOT distinguish the sieve
> database from any vector family of the same lengths. The design cannot yet see
> what the campaign wants to see."

That is a universal negative generalised from **one statistic** (the one that
cannot see y), **one surrogate family**, and **one instance** — and §4 above
refutes it. Together with "P1 IS ANSWERED IN THE NEGATIVE, WITH A PROOF" it is
the fourth interpretive overclaim in an immutable commit message in this program,
and the first in the **pessimistic** direction. `docs/inventor-protocol.md` §4
holds a closure to a named obstruction, an argument, and forward guidance; the
argument here covers only the statistic that was measured. Premature closure is
the failure mode symmetric with overclaiming, and this is an instance of it.

## 9. What I could not check

- The 9 replicate instances (S9). Their vectors were not emitted, so every S9
  number rests on the producer's transcript. This also blocks the replication of
  my own §4 finding. Missing data stays missing.
- The step-0 rebuild, the fpylll/gauss_sieve discriminators, and all timings.
  Not re-run; the venv exists and works (I used it for KA-0/KA-3/KA-6).
- NULL-IID and the NULL-SWEEP m-sweep in detail. The N-independence half is
  corroborated by my own N′-sweep; the m-sweep was not re-run.

## 10. Verdict

`blocking_objections` — on the **conclusions**, not on the data. Everything I
could check reproduces, often to the last printed digit, and the batch is
careful, well-documented and honest about its own deviations. But its two
headline conclusions are negative results that do not meet this program's own
closure standard: PAC-1's generalisation is refuted by a control the batch owed,
and the P1 impossibility is a statement about the harness that the package itself
contradicts three pages later. Both are about to drive the decision on batches
3–6, which is why they block.

Batch 3 should **change the design, not abandon the line**: move to
`k_lat < n` with a real FFT sub-block (`k_fft > 0`, `p > 1`), which makes an
admissible Nf tuple exist, turns on the 2^11.4 adjacent-bin term, and gives the
near-miss population a principled definition. Cheapest validating check first:
emit the replicate vectors and run CTRL-RT-9.
