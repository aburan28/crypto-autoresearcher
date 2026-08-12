# TASK-20260803-36f572 — CHECK C3: instantiate the actual model, and the closed-form counting floor

BATCH-012, GOAL-MLKEM-003. Executor. Successor to TASK-20260803-b762a1
(provider session limit; infrastructure, zero evidence value in either
direction — AGENTS.md rule 5).

**Observations only.** Nothing here concludes that Approximation 4.9 is
validated, refuted, selected or rejected. That is `/review-evidence` under
Coordinator authority. Toy tier (q=241, m=40, n=43/50, beta_sieve 41/44). **No
ML-KEM or Kyber security claim in either direction.** AGENTS.md rule 12 is
UNMET and UNWAIVED: EV-MLKEM-011, EV-MLKEM-013 and EV-MLKEM-017 keep their
status; KN-FIND-031 stays withdrawn. Zero new sampling, no network, no G6K, no
cost model.

Artifacts: `exact_region_measure.py` (the exact script run), `results.json`
(machine readable, provenance carried inside), this file.

---

## 0. Headline, stated in both directions before any qualification

**The exact region measure fits better than the surrogate at every matched
comparison, and on the whole band it fits at the counting-noise floor.**
Whole-band rms as a ratio to the closed-form Poisson floor of the same index
set: the surrogate's *best member over a free exponent* reaches 1.25x (n=43)
and 1.30x (n=50); the exact-measure model, with **one fewer free parameter and
its exponent frozen at whatever (4.10)/(4.11)/(4.24) imply**, reaches **1.04x
and 0.97x**. Three batches of whole-band misfit findings were about a
surrogate.

**And the exact region measure does NOT close the count>=1000 misfit.** There
the surrogate was 16.5x and 24.8x the floor. The exact model with its own
exponent is **23.9x and 23.4x**; with a free exponent added back (matching the
surrogate's parameter count) it is **13.2x and 20.1x**. Better than the
surrogate at matched parameters, still one to one and a half orders of
magnitude above the floor. The well-measured sub-band misfit survives the
substitution.

**The monotone argmin drift survives too.** The surrogate's exponent argmin
drifted 23.0 -> 18.0 (n=43) and 22.0 -> 17.0 (n=50) as noise was removed
(EV-MLKEM-2e668d C-7). Under the exact measure the analogous quantity drifts
26.0 -> 17.9 and 24.5 -> 18.6. It now *starts* at the model's own exponent
instead of below it, but it does not stabilise.

---

## 1. What was computed

### 1.1 The model, from the source's own equations

Read from `inputs/MLKEM-DUAL-SOURCES-20260802/extracts/carrier-hal-05406481/page23_approx_4_8_4_9.txt`
((4.22), (4.23), (4.24)) and from PDF page 20 of the vendored PDF ((4.9),
(4.10), (4.11)) — see section 5, ANOM-3.

    (4.22)  Pwrong ~ INT_{-inf}^{+inf} INT_0^{+inf}
                     min(1, INT_{E(T-t)} lambda(x) mu(y) d(x,y))
                     * e^{-t^2/N - (d_lsc-mu_lsc)^2/(2 sigma_lsc^2)}
                       / (pi sigma_lsc sqrt(2N))  dd_lsc dt
    (4.23)  E(T-t) := {(x,y) in R^2_+ : N * Phi_{d_lsc}(x,y) >= T-t}
    (4.24)  lambda(x) prop. x^{beta_sieve-1},  mu(y) prop. y^{n_fft-1}
    (4.10)  Phi_{d_lsc}(i,j) = Upsilon_{beta_sieve/2}((2pi/q) d_lat i)
                             * Upsilon_{n_fft/2-1}((2pi/q) d_lsc j)
    (4.11)  Upsilon_n(x) = Gamma(n+1) J_n(x)/(x/2)^n
                         = SUM_l (-1)^l (x/2)^{2l} / (l! PROD_{s=1..l}(n+s))

The (4.22) prefactor was verified to be exactly the product of the N(0,N/2)
density in t and the N(mu_lsc, sigma_lsc^2) density in d_lsc:
sqrt(pi N) * sigma_lsc * sqrt(2 pi) = pi sigma_lsc sqrt(2N). So (4.22) *is*
`E_{t,d_lsc}[min(1, W_{d_lsc}(T-t))]`.

Two exact reductions (identities, not approximations) make it cheap:

**R1.** With s = T-t: |Upsilon_n| <= 1 and Upsilon_n(0) = 1 (Poisson's
integral representation makes Upsilon_n the characteristic function of a
symmetric Beta law on [-1,1]), so E(s) is empty for s > N and is the whole
quadrant for s <= 0. Hence

    Pwrong(T) = Q(T) + INT_0^N phi(T-u) * E_d[min(1, W_d(u))] du,
    Q(T) = 0.5 erfc(T/sqrt(N)),  phi(s) = e^{-s^2/N}/sqrt(pi N).

The Q(T) term of the BATCH-009 surrogate is *recovered* here, not assumed, and
with v = ln(N/u) this is BATCH-009's v-integral verbatim with `min(1, K v^p)`
replaced by `E_d[min(1, W_d)]`.

**R2.** Substituting xi = (2pi/q) d_lat x and eta = (2pi/q) d_lsc y,

    W_d(v) = ((2pi/q) d_lat)^{-beta_sieve} ((2pi/q) d_lsc)^{-n_fft} * G(v),
    G(v) := INT_{Upsilon_a(xi) Upsilon_b(eta) >= e^{-v}, xi,eta >= 0}
                 xi^{beta_sieve-1} eta^{n_fft-1} d(xi,eta),
    a = beta_sieve/2,  b = n_fft/2 - 1 = 3.

**G depends on neither d_lat nor d_lsc.** Two consequences worth recording:

* d_lat enters only a v-independent constant that the fitted normalisation
  absorbs, so **the d_lat discrepancy between the .out headers (41.069 /
  57.889) and the Fig 4.1 caption (42.00 / 58.60) cannot affect any number in
  this run.** Recorded, not resolved.
* d_lsc enters only as d_lsc^{-n_fft}, so the (4.22) d_lsc integral — kept in
  its (4.22) position, **outside** the min — collapses to the one-dimensional
  `F(g) = INT_0^inf psi_lsc(d) min(1, g d^{-n_fft}) dd`, evaluated
  semi-analytically.

Final model, **one free parameter A**:

    Pred(T; A) = Q(T) + INT_0^N phi(T-u) * F(A * G(ln(N/u))) du.

### 1.2 G(v) is computed exactly, sign changes and all

Upsilon_n is evaluated from its own series (4.11) in **120-digit decimal
arithmetic**. Double precision cannot be used: at x = 45, n = 22 the largest
term is ~1e8 while the sum is ~1e-9, i.e. ~17 orders of cancellation. The
series was checked against the Bessel zeros it must reproduce: the computed
first two zeros of Upsilon_3 are 6.380161895923983 and 9.76102312998167
against j_{3,1} = 6.3801618959239835 and j_{3,2} = 9.7610231299817.

G(v) is layer-caked on the xi axis: for each eta the admissible xi set is
`{sign*Upsilon_a >= e^{-(v + ln|Upsilon_b(eta)|)}}`, whose x^m measure is
closed form once its endpoints are located. **The sign-matching branch (both
factors negative) is included** — precisely the structure a Gaussian surrogate
cannot have. 37 lobes of Upsilon_b and 3 of Upsilon_a are carried.

### 1.3 The four models, one quadrature, one band, one fit protocol

| id | rho(u) | free params |
|----|--------|-------------|
| M1 | min(1, K v^p), p scanned | 2 (K, p) |
| M1a | min(1, K v^p), p = (beta_sieve+n_fft)/2 frozen | 1 (K) |
| **M2** | **F(A*G(v))** — the exact model | **1 (A)** |
| M3 | F(A*G(v)^s), s scanned — the drift probe | 2 (A, s) |
| M4 | min(1, A*G(v)*mu_lsc^{-n_fft}) — exact measure, d_lsc collapsed | 1 (A) |

M3 at s = 1.00 *is* M2, identically (same rho, same protocol, same process).

Fit protocol, identical to BATCH-010's in substance: profile the single free
(log) normalisation on the index set, report the rms of the log2 residual over
that same index set, **beside the closed-form counting floor of that same
index set and as a ratio to it**.

---

## 2. Part B — the closed-form counting-noise floor, derived independently

Shipped as its own computation (`--mode floor`, runs in ~4 s and touches
nothing else) because every surviving conclusion in this goal now rests on it
and it had been computed by exactly one party.

**Derivation.** Line T of an archived Pwrong file is the pooled estimate
`Phat(T) = C_T / M` with `M = nb_iteration * q^{k_fft}` the exact number of
pooled candidate scores (q^{k_fft} candidates scored per iteration,
nb_iteration iterations). C_T is therefore recoverable exactly; recovered here
and checked (max relative deviation of value*M from an integer: 1.360e-16 for
n=43, 1.815e-16 for n=50).

The statistic this lane reports is the equal-weight rms over the band of
`r_T = log2(model_T) - log2(Phat(T))`. A **perfect** model has
`model_T = lambda_T/M` with `lambda_T = E[C_T]`, so its residual is not zero
but

    r_T = log2 lambda_T - log2 C_T,

pure counting noise. A score enters the resolved band only if its pooled count
is at least one (the band ends at the last positive score), so condition on
C >= 1. Under `C_T ~ Poisson(lambda_T)` marginally,

    floor_rms = sqrt( (1/|band|) SUM_T E[(log2 lambda_T - log2 C)^2 | C>=1] )

    E[(log2 lambda - log2 C)^2 | C >= 1]
      = (1/ln^2 2) * (1/(1-e^{-lambda}))
        * SUM_{k>=1} e^{-lambda} lambda^k/k! * (ln lambda - ln k)^2.

**Closed form. No simulation, no random numbers.** lambda_T is unknown and is
replaced by its plug-in estimate C_T.

lambda reaches 2.79e10, so above lambda = 1e5 an asymptotic branch is used.
With u = (C-lambda)/lambda and the Poisson central moments mu2 = lambda,
mu3 = lambda, mu4 = 3 lambda^2 + lambda:

    ln(1+u)^2 = u^2 - u^3 + (11/12) u^4 + O(u^5)
    E[.]      = 1/lambda - 1/lambda^2 + (11/12)(3/lambda^2) + O(lambda^-3)
              = 1/lambda + (7/4)/lambda^2 + O(lambda^-3).

The two branches were cross-checked against each other: relative agreement
4.0e-6 at lambda=1e3, 4.0e-8 at 1e4, 4.0e-10 at 1e5.

**Result (this task's own computation; no red-team number used as input):**

| file | band | n | truncated-Poisson floor | delta-method 1/(lambda ln^2 2) |
|---|---|---|---|---|
| n=43 | whole (scores 0-1802) | 1803 | **0.340570** | 0.409366 |
| n=43 | count>=10 (0-1492) | 1493 | 0.163689 | 0.154224 |
| n=43 | count>=1000 (0-851) | 852 | **0.014627** | 0.014620 |
| n=43 | count>=1e5 (0-550) | 551 | 0.001072 | 0.001072 |
| n=50 | whole (0-2309) | 2310 | **0.327569** | 0.334742 |
| n=50 | count>=10 (0-1968) | 1969 | 0.155755 | 0.147603 |
| n=50 | count>=1000 (0-1131) | 1132 | **0.015192** | 0.015185 |
| n=50 | count>=1e5 (0-635) | 636 | 0.001357 | 0.001357 |

**Agreement with the red team's C1, to every digit they published:** 0.3406 /
0.3276 whole-band truncated-Poisson, 0.4094 / 0.3347 delta-method, 0.0146 /
0.0152 count>=1000, and their count>=10 delta-method 0.1542 (n=43). The floor
now has two independent computations. The delta-method value exceeds the exact
value on the whole band (0.409 vs 0.341) and falls below it on count>=10
(0.154 vs 0.164): the delta method over-states the noise of the lambda ~ 1-2
rows and under-states it in mid-band, so **quoting the delta method as "the
floor" is not conservative in either direction** and the exact column should
be used.

---

## 3. Part A — results

Every rms is in bits; **RATIO is rms divided by the truncated-Poisson floor of
the same index set**, never by zero.

### 3.1 n=43 (q=241, m=40, n=43, beta_sieve=44, n_fft=8, N=25971)

| band | floor | M1a surrogate, p=26 frozen | M1 surrogate, p free | **M2 EXACT, 1 param** | M3 exact^s, 2 params |
|---|---|---|---|---|---|
| whole | 0.340570 | 0.705492 (2.07x) | 0.427122 @p=23.00 (1.25x) | **0.355665 (1.04x)** | 0.355665 @s=1.00 (1.04x) |
| count>=10 | 0.163689 | 0.737755 (4.51x) | 0.343388 @p=22.25 (2.10x) | **0.279823 (1.71x)** | 0.247176 @s=0.97 (1.51x) |
| count>=1000 | 0.014627 | 0.810303 (55.4x) | 0.241883 @p=20.00+ (16.5x) | **0.349477 (23.9x)** | 0.193582 @s=0.90 (13.2x) |
| count>=1e5 | 0.001072 | 0.229813 (214x) | 0.189907 @p=20.00+ (177x) | **0.205521 (192x)** | 0.065839 @s=0.69 (61.4x) |

### 3.2 n=50 (beta_sieve=41, n_fft=8, N=25970)

| band | floor | M1a surrogate, p=24.5 frozen | M1 surrogate, p free | **M2 EXACT, 1 param** | M3 exact^s, 2 params |
|---|---|---|---|---|---|
| whole | 0.327569 | 0.696882 (2.13x) | 0.427416 @p=22.25 (1.30x) | **0.317217 (0.97x)** | 0.317217 @s=1.00 (0.97x) |
| count>=10 | 0.155755 | 0.725187 (4.66x) | 0.392578 @p=21.50 (2.52x) | **0.276937 (1.78x)** | 0.276937 @s=1.00 (1.78x) |
| count>=1000 | 0.015192 | 0.828752 (54.6x) | 0.376295 @p=20.00 (24.8x) | **0.355705 (23.4x)** | 0.305665 @s=0.97 (20.1x) |
| count>=1e5 | 0.001357 | 0.786012 (579x) | 0.295559 @p=18.50+ (218x) | **0.437757 (323x)** | 0.169689 @s=0.76 (125x) |

`+` argmin sits on the edge of this run's exponent grid (p_own +/- 6).
Recorded, not hidden: the surrogate drift measured **here** is therefore a
lower bound; RT-8's wider scan reached 18.0 and 17.0. The rms *value* at the
edge is not scan-limited, only the argmin location (the red team makes the
same qualification).

M3 argmins are merged from two blocks of the same run: the gridded s-curve
(step 0.07) and the M2 point, which is s = 1.00 exactly. See ANOM-5.

### 3.3 The verdict the completion gate asks for: closes / reduces / unchanged

| band | surrogate -> exact, 1 param (frozen exponent) | surrogate -> exact, matched 2 params |
|---|---|---|
| whole | 2.07x -> **1.04x** and 2.13x -> **0.97x**: **CLOSED**; also closed against the surrogate's best-over-p (1.25x/1.30x -> 1.04x/0.97x) with one fewer parameter | same |
| count>=10 | 4.51x -> 1.71x, 4.66x -> 1.78x: **REDUCED**, not closed | 2.10x -> 1.51x, 2.52x -> 1.78x: reduced |
| **count>=1000** | 55.4x -> 23.9x, 54.6x -> 23.4x: **REDUCED, NOT CLOSED** | 16.5x -> **13.2x**, 24.8x -> **20.1x**: **REDUCED, NOT CLOSED** |
| count>=1e5 | 214x -> 192x, 579x -> 323x: reduced, not closed | 177x -> 61.4x, 218x -> 125x: reduced, not closed |

Against the specific question in the handoff — *does the exact measure close
the misfit the surrogate showed in the count>=1000 sub-band (16.5x and 24.8x)?*
— **No.** At matched parameter count it reduces it to 13.2x and 20.1x; with
the exponent frozen at the value (4.10)/(4.11)/(4.24) imply it is 23.9x and
23.4x, i.e. worse than the surrogate's two-parameter best for n=43 and about
the same for n=50. The misfit in the well-measured sub-band is not an artifact
of the Gaussian-Phi substitution.

### 3.4 Does the monotone argmin drift persist?

Effective exponent = s * (beta_sieve+n_fft)/2, directly comparable to the
surrogate's p. Grid resolution 0.07 in s = 1.8 (n=43) / 1.7 (n=50) in
effective exponent.

| | whole | count>=10 | count>=1000 | count>=1e5 |
|---|---|---|---|---|
| n=43 surrogate argmin p (this run) | 23.00 | 22.25 | 20.00+ | 20.00+ |
| n=43 surrogate argmin p (RT-8, wider grid) | 23.00 | 22.50 | 19.50 | 18.00 |
| **n=43 exact-measure effective exponent** | **26.00** | **25.22** | **23.40** | **17.94** |
| n=50 surrogate argmin p (this run) | 22.25 | 21.50 | 20.00 | 18.50+ |
| n=50 surrogate argmin p (RT-8) | 22.00 | 21.50 | 20.00 | 17.00 |
| **n=50 exact-measure effective exponent** | **24.50** | **24.50** | **23.77** | **18.62** |

**YES, the drift persists**, monotone non-increasing, over 26.0 -> 17.9 and
24.5 -> 18.6. Two differences from the surrogate's drift are on the record:

1. It **starts at the model's own exponent**. On the whole band (and, for
   n=50, on count>=10 too) the exact-measure family selects s = 1.00, i.e. the
   exponent that (4.10)/(4.11)/(4.24) actually imply. The surrogate rejected
   its own exponent 26.0 / 24.5 in favour of 23.0 / 22.25 on the very same
   band.
2. It is **flatter in the resolved mid-band**: s stays within one grid cell of
   1.00 down to count>=1000 for n=50 and within 1.5 cells for n=43, and only
   collapses in the count>=1e5 sub-band.

The exact model's single fitted parameter tells the same story directly:
log2 A = -172.247 / -172.154 / -172.219 / -174.852 (n=43) and -155.507 /
-155.443 / -155.411 / -155.760 (n=50) across the four bands. Stable to 0.1 bit
across whole -> count>=1000, then moving 2.6 (n=43) at count>=1e5.

### 3.5 RT-9's mechanism, recomputed independently

RT-9's numbers reproduce exactly. log2(Upsilon_3 / Gaussian surrogate
exp(-x^2/16)): -0.1894 at x=4, **-0.5813 at x=5**, -2.0471 at x=6, and
Upsilon_3 is **negative** at x=7 (-2.3448e-02) with its **sign change at
6.380162**. Lattice side (a=22), log2(Upsilon_22 / exp(-x^2/92)): -0.0009 at
x=4, -0.0023 at 5, -0.0047 at 6, -0.0151 at 8, -0.0806 at 12 — harmless, as
RT-9 said. (2pi/q)*mu_lsc = 0.6241 per unit j (RT-9: 0.624). Upsilon_22 first
zero 27.567944; Upsilon_20.5 first zero 25.955681.

And the consequence RT-9 predicted is measured directly: **the local log-log
slope of the exact region measure is v-dependent**, not the constant
(beta_sieve+n_fft)/2 the surrogate asserts:

| v | 3 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|
| n=43, dlnG/dlnv (surrogate says 26.0) | 24.42 | 23.09 | 22.31 | 21.41 | 20.38 | 19.32 | 19.06 | 21.54 | 26.24 |
| n=50, dlnG/dlnv (surrogate says 24.5) | 22.92 | 21.57 | 20.76 | 19.83 | 18.77 | 17.88 | 18.71 | 22.83 | 27.15 |

The slope descends to ~19.1 / 17.9 and then turns back up as the second
(negative x negative) lobe pair activates. **That range, [17.9, 24.4], is the
range over which the surrogate's fitted exponent drifted.** The observation is
recorded; the inference from it is not this task's to make.

### 3.6 Which of the two departures from BATCH-009 does the work

M4 keeps the exact region measure but collapses the d_lsc integral at mu_lsc,
as BATCH-009 did. Whole band: 0.368852 (1.08x) for n=43, 0.349772 (1.07x) for
n=50, against M1a's 0.705492 / 0.696882 and M2's 0.355665 / 0.317217. So the
**exact region measure does almost all of the improvement**; retaining the
(4.22) d_lsc mixture adds a further 0.013 / 0.033 bits. In count>=1000 the
mixture matters more (0.436680 -> 0.349477 for n=43).

### 3.7 Reproduction cross-check against the archive

At BATCH-009's archived (p, log2 K_fit) this run's quadrature gives whole-band
rms **0.705494** (n=43) against BATCH-009's archived 0.705760 and BATCH-010's
exact-kink recomputation **0.705494** — agreement to the printed digits with
BATCH-010, and -0.000266 bits against BATCH-009, which is the declared clip
treatment. n=50: 0.696885 here against 0.696721 archived (+0.000163). The red
team's independent implementation reached 0.42914 at p=23.00 on the whole
band; this run gets 0.427122 at p=23.00 (delta 0.002, inside their declared v*
search resolution) and their 0.2406 at count>=1000 against this run's
0.241883. **Three implementations now agree.**

---

## 4. Controls, and what they returned

| control | outcome |
|---|---|
| Quadrature convergence | max abs delta log2 prediction between the 876-node production grid and a 2336-node refinement: **2.147e-07** (n=43), **2.185e-07** (n=50) bits. Six orders below the 0.01-bit scale of interest. |
| Region-measure grid truncation | abs Upsilon_a <= 1.31e-07 beyond xi=34 and abs Upsilon_b <= 2.02e-06 beyond eta=120, so G(v) is **exact for v <= 13.111**. F(A*G(v)) saturates to 1-1e-12 at v = 10.716 (n=43) / 10.466 (n=50). Truncation **IMMATERIAL**. |
| Integrality of recovered counts | max relative deviation of value*M from an integer: 1.360e-16 / 1.815e-16. |
| Upsilon series vs known Bessel zeros | j_{3,1} and j_{3,2} recovered to 16 digits. |
| Floor: exact sum vs asymptotic | agree to 4.0e-6 / 4.0e-8 / 4.0e-10 at lambda = 1e3 / 1e4 / 1e5. |
| Floor vs red team's C1 | every published digit matches. |
| BATCH-009/010 reproduction | see 3.7. |
| Fit-bracket edge guard | every 1-D fit self-widens its bracket if the coarse minimiser lands on an edge; no widening was triggered in the production run. |
| psi_lsc left-tail sensitivity | see ANOM-7. |
| Kernel contiguity assertion | added after ANOM-1; passes for every score in both files. |

---

## 5. Deviations, anomalies, and every attempt — recorded, none discarded

### Protocol deviations

**DEV-1 — `counting_floor.py` was not created.** The handoff's `deliverables`
field names it, but its `artifact_paths` declares exactly three paths and the
dispatching instruction was to deliver exactly those three and not to expand
the declared artifact set. The floor therefore ships **inside**
`exact_region_measure.py` behind its own entry point `--mode floor`, which
runs the closed-form computation alone (no model, no quadrature, no exponent
scan, ~4 s) and writes nothing. The conflict between the handoff's two fields
is reported rather than resolved unilaterally.

**DEV-2 — no `runs/<RUN-ID>/` reproduction package.**
`docs/evidence-and-reproducibility.md` asks for `manifest.yaml`,
`command.txt`, `environment.json`, `stdout.log`, `stderr.log`,
`raw-result.json`. The handoff declares three artifact paths and no `runs/`
tree, so all the required fields are carried **inside** `results.json` under
`provenance`: command, argv, cwd, script sha256, git commit + dirty state +
dirty paths + branch, environment and dependency availability, input file
sha256s, PDF sha256 (read-only, hash verified), seeds/determinism, wall clock,
**peak RSS (0.0685 GB, measurable on this host via `resource.getrusage`)**,
user/system CPU, captured stderr, an `inference` block, a `certificate` block
(`kind: none`, pure measurement run), and a `validity` block. `stdout_log`
carries the full console transcript. This closes the gap recorded twice as
BATCH-010 DEV-1 and validator D1.

**DEV-3 — departures from the BATCH-010 implementation** (DEP-1..DEP-5, stated
in full in the script docstring): the v-integral is carried in u = N e^{-v}
(exact change of variable); the clip is **not** split at a kink because M2/M3
have no kink (F is C^1) and M1/M1a are evaluated on the *same* shared nodes so
the comparison is instrument-matched (cost quantified in 3.7); the (4.22)
d_lsc integral is retained (M2/M3) and separately collapsed (M4); the free
parameter is a normalisation only; every rms is reported beside its own floor.

**DEV-4 — alpha = 2 was used and it enters nowhere.** See ANOM-2.

**DEV-5 — three execution attempts, one production run.** See below. The
handoff's `maximum_runs: 1` is respected: exactly one attempt produced
measurement output.

### Attempts

| # | outcome | classification |
|---|---|---|
| 1 | crashed in a *logging* statement (`TypeError: must be real number, not NoneType`) formatting log2(Upsilon_3/Gaussian) at x=7, where Upsilon_3 is negative. No fit ran, no artifact written. | `implementation_error`, repaired |
| 2 | ran to the first file's M1 block and **its own quadrature convergence control returned 0.26 bits**, far above tolerance. Aborted deliberately rather than allowed to finish. No artifact written. | aborted by control; surfaced ANOM-1 |
| 3 | **production run.** exit 0, wall clock 803.98 s (budget 3000 s), peak RSS 0.0685 GB (budget 4 GB), stderr empty. | `completed_valid` |

### Anomalies

**ANOM-1 (found by a control, and the reason attempt 2 was aborted).** In this
task's own implementation, `build_u_nodes` returned nodes that were **not
sorted in u**: Gauss-Legendre roots come out descending inside each panel.
`build_kernel` keeps only nodes with (T-u)^2/N < 120 and `predict` addresses
them as one contiguous slice of rho — valid only under monotone node order.
For every score with T > sqrt(120*N) = 1612 the kept set had a gap, and the
rho slice misaligned by a few positions. Effect: up to **0.44 bits** of error
confined to T >~ 1700, ~1e-9 bits elsewhere; the whole-band rms was inflated
by 0.013 bits (n=43: 0.369045 -> 0.355665). Fixed by sorting the nodes, and a
runtime assertion now raises if the kept set is ever non-contiguous again.
**This defect is local to this task's code; BATCH-010's script does not use
sparse slice addressing and is not affected.** The number reported in attempt
2's console (M2 whole-band 0.369045) is superseded by 0.355665 and is recorded
here rather than deleted.

**ANOM-2 — alpha has no locus in the wrong-guess chain.** The handoff
instructs "at alpha = 2" and alpha = 2 is recorded as used, but alpha appears
in **none** of (4.10), (4.11), (4.22), (4.23), (4.24). On PDF page 23 all four
occurrences of alpha are inside (4.19), i.e. Approximation 4.8, the
**good**-guess threshold; the document-wide scan puts alpha on pages 8, 9, 13,
15, 16, 23, 24, 25, 28, 32, 33, 36. Setting alpha = 2 changes no number in
this run. RT-10's identification of alpha = 2 from (4.19) against the archived
Pgood median (ratio 1.0048) is neither reproduced nor disputed here — it is
simply not load-bearing for C3. Reported as a disagreement with the handoff
premise rather than silently adopted or silently dropped.

**ANOM-3 — the dispatching message's claim about the extracts is wrong; the
handoff's is right.** The launching instruction said (4.10)/(4.11) "are on PDF
page 20, which **is** among the extracts". The extract directory
`inputs/MLKEM-DUAL-SOURCES-20260802/extracts/carrier-hal-05406481/` contains
exactly `page23_...`, `page25_...`, `page26_...`, `page27_...`, `page37_...`
and `pdf_metadata.json` — **no page 20**. The handoff body states correctly
that "the extract set omits it". (4.10)/(4.11) were therefore read from the
vendored PDF, opened read-only via BATCH-011's committed `extract_pages.py`,
sha256 verified as
083b142256eecaebfa72dfccf847151b2175666a3979cef4e7383376757b8005. Nothing was
written to the PDF or to the extract directory.

**ANOM-4 — the n=50 whole-band rms is *below* its plug-in floor (0.97x), and
0.94x under the psi_lsc-truncation variant.** This is not "better than
perfect". Two reasons, both recorded: (i) the floor uses the plug-in
lambda_T = C_T, itself noisy for the many lambda ~ 1-3 rows that dominate the
whole-band statistic (121 rows carry count <= 2 for n=43); (ii) the fitted
normalisation absorbs the mean residual. The honest reading is that the
whole-band statistic is **at** the floor to within the floor's own plug-in
uncertainty, and that the whole band cannot discriminate models at better than
~1x the floor. n=43 whole-band is 1.04x.

**ANOM-5 — the M3 exponent grid does not contain s = 1.00.** The grid is
0.55..1.25 in steps of 0.07. But M3 at s = 1.00 *is* M2 by construction
(identical rho, identical protocol, same process), so the merged argmins in
3.4 read two blocks of the **same** run and introduce no new computation. The
`argmin` field inside `results.json` for M3 is the *gridded* argmin and does
not include the s = 1.00 point; section 3.4 states the merged value. Flagged
so the two are not read as inconsistent.

**ANOM-6 — three of eight surrogate sub-band argmins sit on this run's
exponent-grid edge** (p_own +/- 6, chosen to bound cost). The drift measured
here is therefore a **lower bound**; RT-8's wider scan reached 18.0 / 17.0.
Flag recorded per band in `results.json` as `at_grid_edge`.

**ANOM-7 — (4.22)'s deep tail is governed by psi_lsc near d_lsc -> 0.** As
written, (4.22) integrates d_lsc over (0,+inf) against a *normal* density, so
F(g) at small g behaves as psi_lsc(0) * g^{1/n_fft}: the model's prediction at
large T is controlled by the left tail of a normal approximation to a decoding
distance, where that approximation has no physical support (P(d_lsc <= 0) =
6.97e-13 / 2.50e-13, left out because (4.22) integrates from 0). The literal
reading is the primary result. A declared sensitivity variant truncating
psi_lsc below mu-4sigma gives whole-band 0.322072 (0.95x) / 0.306417 (0.94x)
and count>=1000 0.354771 (24.25x) / 0.359356 (23.65x) — **the count>=1000
verdict is unchanged under either reading**, which is the point that matters.

**ANOM-8 — residual sign structure of the exact model, whole-band fit
(n=43).** Mean residual +0.106 bits, min -0.364, max +1.328. The large
positive excursion sits at small T; the residual profile in `results.json`
shows +0.139 at T=0, +0.467 at T=270, +0.264 at T=540, -0.174 at T=810,
-0.190 at T=1080, +0.158 at T=1350, +0.191 at T=1620. So the exact model
retains a systematic S-shaped shape residual of +/-0.3-0.5 bits in the
well-measured region — which is exactly what the 23.9x count>=1000 ratio is
measuring. n=50 mean +0.083, min -0.332, max +1.347.

---

## 6. Boundaries

* Two archived toy files only (q=241, m=40, n=43 and n=50), resolved band
  only. Raw undivided score scale; no k_fft alignment applied.
* Nothing is fitted, anchored, compared or extrapolated past the last positive
  score (1802 / 2309). Printed zeros above it are absence of measurement.
* RT-11 stands and bounds everything above: the resolved band ends at roughly
  15 percent of the operating threshold (median F(solution) = 11964.5 against
  last measured score 1802). **No region in this archive is the
  security-relevant region.**
* The normalisation is fitted to the very data being compared. This is a
  **shape** comparison with one free scale; no absolute-level statement is
  tested, and RT-12's observation that a mechanism can hide inside the fitted
  normalisation applies to A exactly as it applied to K.
* Establishes nothing about ML-KEM security in either direction, nothing about
  Carrier et al.'s Kyber cost figures, and nothing about Table 5.1.
* One execution, one implementation, no replication. The floor now has two
  independent computations; the exact-measure model has one.
* `dominated_by`: n/a — no attack is advanced and no cost frontier is
  occupied. `sota_delta`: zero.

---

## 7. Reproduction

```
cd /home/user/crypto-autoresearcher
python3 coordination/goals/GOAL-MLKEM-003/batches/BATCH-012/tasks/TASK-20260803-36f572/exact_region_measure.py --mode all
python3 coordination/goals/GOAL-MLKEM-003/batches/BATCH-012/tasks/TASK-20260803-36f572/exact_region_measure.py --mode floor
```

git commit at run time `43978a6cdf4ab629c8b5fa5450bf165ea7b1877c`, branch
`claude/harness-findings-repo-yyzt1x`, working tree dirty only in this task's
own untracked directory. Python 3.11.15, Linux-6.18.5-x86_64-with-glibc2.39.
**No numpy, scipy or mpmath on this host** — the (4.11) series, the Bessel
zeros, the Gauss-Legendre nodes and the Poisson sums are all computed by the
script itself. No random number is drawn anywhere; no seed is required; the
result is a deterministic function of the archived bytes and the constants in
`results.json -> numerical_controls`.
