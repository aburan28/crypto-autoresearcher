# TASK-20260804-f58d34 -- executor report (narrative deliverable; see report_markdown_note)

**Executor, BATCH-a2bb63 (batch 5 of 6), GOAL-MLKEM-004.**

SCOPE, binding on every sentence and number below. m=35, n=25, d=60, q=127, secret
centred-binomial eta=2, error rounded-Gaussian sigma=2; Stage B sieve at dimension
m+k_lat=50. ONE LWE instance (BATCH-f75059 replicate 0, seed 20260803206). TOY SCALE.
No ML-KEM break claim, no security proof, no FIPS 203 parameter set affected or
cleared, no speedup, no cost claim, no exponent moved. AGENTS.md rule 12 UNMET and
UNWAIVED, inherited: this report changes the status of no EV-MLKEM-* record and
proposes none. KN-TECH-6c0e15 is a CREATION of a superseding entry authorised by
DEC-20260804-5c9fe1 NA-3; KN-TECH-9d21c4 is untouched.

This report states OBSERVATIONS. It does not conclude that the independence heuristic
is validated or refuted. That judgement belongs to the Reviewer and the Coordinator.
states_a_conclusion: false.

## 0. Instrument rebuild, before any measurement

Rebuilt from scratch per knowledge/techniques/KN-TECH-14efa5.md into a fresh venv
/tmp/sagevenv-execf58d34 with its own gmp symlink /tmp/gmplink-execf58d34. Three
earlier venvs from other agents were present on the container; they are recorded in
the transcript and were NOT used. Verbatim transcript: rebuild_transcript.txt.
08:04:06Z -> 08:08:29Z, 263 s. Both documented fixes were required and applied:
--no-build-isolation for Cython, and the self-provided libgmp.so symlink.

  discriminator                | KN-TECH-14efa5 pins        | measured here
  shim not on sys.path         | required                   | []
  PowerSeriesRing constructs   | required                   | constructs
  BKZ.EasyParam raises         | Cannot open strategies file| reproduced
  Siever(GSO.Mat(A)) raises    | requires UinvT enabled     | reproduced
  passagemath version          | 10.8.7                     | 10.8.8
  fpylll / g6k / numpy / python| 0.6.4 / 0.1.2 / - / -      | 0.6.4 / 0.1.2 / 2.4.6 / 3.11.15

VERSION DRIFT, recorded: passagemath resolves to 10.8.8, not the 10.8.7 the entry
pins. VAL-20260804-a84239 found the same drift in an independently built venv, which
makes it environmental rather than a producer error.

DEVIATION DEV-1, recorded. The entry's two functional numbers (||b0|| 160.4 -> 130.3;
g6k db 4075) are NOT reproducible from the entry, because it does not record the basis
seed or construction. My checks used my own qary basis and returned ||b0|| 189.5 ->
125.7 (0.22 s) and a 4166-vector gauss_sieve db (1.49 s). These confirm the tools
FUNCTION; they do not confirm the pinned numbers, and I do not claim they do.

The provenance check that does bind is the research instance itself, and it reproduced
exactly: N = 17919 (archive 17919), a_x delta = 0.000e+00, Stage B N = 4253 (archive
4253). mean||x||^2 differs from the archived rep0_mean_xnorm2 by 2.2e-05; since a_x
matches to 0.0e+00 and a_x is a fixed multiple of mean||x||^2, the archived constant is
a different row set, not a different database.

## 1. T0 -- the deterministic-Y RANDDIR excess. Bookkeeping, closed.

One line changed against surrogate.py:685-688: Y becomes a deterministic function of X
instead of an independent draw.

  arm                              | y from x            | in lattice | excess  | z
  SIEVE (comparator)               | -                   | yes        | 1.2919  | 13.7
  NORMMATCH_RANDDIR_INDEP (batch 4)| independent draw    | no         | 1.0221  | 1.0
  NORMMATCH_RANDDIR_COUPLED        | normalise(R^T x)*|y|| no         | 12.9603 | 1420.6

Norms match the sieve EXACTLY, row for row: mean ||x||^2 181.4943 vs 181.4943, mean
||y||^2 129.0815 vs 129.0815.

FROZEN RULE (declared before the run): T0-CONFIRMS. Confirm band was 12.1507 +-15% =
[10.3281, 13.9733]; measured 12.9603, i.e. +6.7% from RT-20260804-37a8f2's 12.1507.
Confirmed on this program's own record, with a different R seed, a different scorer and
an independently rebuilt instrument.

Caveat carried forward verbatim from the red team, because it applies to my arm too: y
is real-valued and the map linear, so there is NO mod-q wrapping; the arm is in no
lattice and carries no membership certificate.

Observation: a family with no lattice membership at all separates 10.0x harder than the
certified sieve database on this program's own instrument. Nothing further is asked of
this observable in this report.

## 2. T1 -- across-candidate dependence. The batch.

Score, unchanged from every prior batch: S_k = (1/N) sum_i cos(2 pi (x_i.e +
y_i.(s-c_k))/q), ensemble = D = 4000 independent error draws over one fixed database.

### 2.1 What was predicted before the measurement

Frozen in dependence.py's pre-registration block (sections 2, 3, 5) before the build
stage ran. Under the law's assumption (I-b), wrong-candidate scores are iid, so
R_raw = I, K_eff_trail = K-1, K_eff_max = K, var_cv = 0.

Two FORCED values were derived before measuring, from an exact closed form (exact for
Gaussian e, not first order):

  Cov(S_k,S_k') = (1/N^2) [ a_k^T C a_k' + b_k^T S b_k' ],  a = cos phi, b = sin phi
  C = P.*(cosh T - 1),  S = P.*sinh T,  P_ii' = exp(-c(n_i+n_i')),  T = 2c X X^T,
  c = (1/2)(2 pi sigma/q)^2

F-1: the near-miss group's R_raw is forced to ~1 by a rank-one common mode, because
cos(phi_ik) = 1 - O(0.006) for every k. Hand-computed prediction 0.98258,
pre-registered band [0.95, 0.995].
F-2: the uniform group's R_raw is forced to ~0.
Both were declared UNINFORMATIVE in advance, before being measured.

### 2.2 The forced values, measured

  quantity                        | predicted before run       | measured (SIEVE)
  F-1 near-miss offdiag(R_raw)    | 0.98258, band [0.95,0.995] | 0.9999
  F-2 uniform offdiag(R_raw)      | ~0                         | -0.0056 (K=8), -0.0005 (K=25)

DEVIATION DEV-2, recorded. The measured 0.9999 is OUTSIDE my pre-registered band
[0.95, 0.995]. The direction and mechanism were right; the NUMBER was wrong because the
hand calculation used a diagonal approximation to C and S. The EXACT closed form, run in
the same script with no scoring, predicts +0.9999 against the measured +0.9999. I record
the band as missed rather than restating the prediction.

offdiag(R_ctr) is also FORCED -- to exactly -1/(K-1) whenever the marginal variances are
equal. Measured -0.1408 (K=8, forced -0.1429), -0.0413 (K=25, forced -0.0417). This was
found by a synthetic instrument check BEFORE any measurement, is recorded in the script's
section 1a and changelog v2, and is why ST-6 rather than offdiag(R_ctr) is the primary
observable.

### 2.3 A forced value I did NOT derive in advance

The error e is m = 35 dimensional. Every candidate's score is a function of the same
35-dimensional e, so to first order Cov(S) = J Cov(e) J^T with J of shape K x 35, and
rank(Cov) <= 35. For any K > m the correlation matrix therefore CANNOT have K equal
eigenvalues and K_eff_trail is forced below K-1. I did not derive this before the run.

It is visible as a clean dose-response in K on the uniform group, and -- the decisive
part -- THE NULL REPRODUCES IT:

  uniform group                        | K=8    | K=25   | K=512
  SIEVE, K_eff_trail / CAL-PERM        | 0.9692 | 0.9209 | 0.3571
  NULL-IIDPHASE, same                  | 0.9699 | 0.9162 | 0.3601

m = 35: the ratio is near 1 while K < m and collapses once K >> m, and the uniform-phase
null tracks the real database to 0.8%. AT K = 512 THIS STATISTIC READS NOTHING ABOUT THE
DUAL FAMILY. Any reading of the K=512 column as a property of the sieve would have been
the campaign's fifth construction-determined quantity, and it is disclosed here rather
than reported as a finding.

### 2.4 The contrast that survives the forced parts

At MATCHED K, against the NULL-IIDPHASE arm (same X, same error draws, same candidates,
Y replaced by uniform residues mod q):

ST-6, K_eff_trail / CAL-PERM, and the real/null ratio
  group                 | K   | SIEVE  | NULL   | SUMS   | SIEVE/NULL | SUMS/NULL
  near_miss             | 8   | 0.8600 | 0.9837 | 0.9624 | 0.874      | 0.978
  near_miss             | 25  | 0.7296 | 0.9316 | 0.8783 | 0.783      | 0.943
  secret_distribution   | 25  | 0.4178 | 0.9238 | 0.4898 | 0.452      | 0.530
  uniform               | 8   | 0.9692 | 0.9699 | 0.9972 | 0.999      | 1.028
  uniform               | 25  | 0.9209 | 0.9162 | 0.9879 | 1.005      | 1.078
  uniform               | 512 | 0.3571 | 0.3601 | 0.7934 | 0.992      | 2.204

ST-5c, K_eff_max_ctr / CAL-PERM -- the effective number of independent candidates in the
sense that enters an extreme-value advantage law
  group                 | K   | SIEVE  | NULL   | SUMS   | SIEVE/NULL
  near_miss             | 8   | 0.9385 | 0.9902 | 0.7241 | 0.948
  near_miss             | 25  | 0.9007 | 0.9865 | 0.4315 | 0.913
  secret_distribution   | 25  | 0.4438 | 0.9719 | 0.2185 | 0.457
  uniform               | 8   | 0.9983 | 0.9881 | 0.9996 | 1.010
  uniform               | 25  | 0.9967 | 0.9937 | 1.0062 | 1.003
  uniform               | 512 | 0.9326 | 0.9229 | 0.9794 | 1.011

THE OBSERVATION, stated flatly and without interpretation. On this one instance, at
matched K and against a null of the same shape, the two certified valid dual families
show a reduction in both effective-candidate statistics on the candidate groups whose
phase offsets are SHORT (near-miss, secret-distribution), and NO reduction on uniform
candidates. The largest is the secret-distribution group at K=25: K_eff_max_ctr is 0.44x
the comparator for the sieve database and 0.22x for the sums family, against 0.97x for
the uniform-phase null on the same X.

DIRECTION, stated because it must be: the departure is DOWNWARD -- fewer effective
independent candidates than the law assumes. I make no claim about what that implies for
any attack, any cost, or any parameter set.

### 2.5 The departure has a closed form, computable with NO SCORING

One blocked N x N kernel pass over the x-database Gram matrix and the Y columns, 15 s,
no scoring of anything:

  group          | closed-form K_eff_trail | measured | CF ratio to K-1 | measured ratio
  near_miss K=8  | 6.052                   | 6.012    | 0.8646          | 0.8600
  near_miss K=25 | 17.480                  | 17.419   | 0.7283          | 0.7296
  uniform K=8    | 6.784                   | 6.775    | 0.9692          | 0.9692
  uniform K=25   | 22.066                  | 21.981   | 0.9194          | 0.9209

The closed form also predicts offdiag(R_raw) to four decimals (+0.9999 vs +0.9999
near-miss; -0.0003 vs -0.0005 uniform) and offdiag(R_ctr) exactly (-0.1408 vs -0.1408;
-0.0413 vs -0.0413).

So the entire across-candidate dependence structure is a deterministic functional of
(X, Y), obtainable without scoring anything. That is the fifth time this campaign has
found its observable to have a closed form.

THE DIFFERENCE FROM BATCHES 1-4, stated as an observation and not as a defence. The
batch 1-4 quantities had a value fixed by the construction WHATEVER was measured. This
functional returns the LAW'S OWN VALUE (ratio 0.999-1.011 on both statistics) for
uniform candidates OVER THE VERY SAME DATABASE and the very same error draws that give
0.45 for secret-distribution candidates. The observable therefore has demonstrated
dynamic range within one database. Whether its value is nonetheless forced for EVERY
valid dual family of EVERY such lattice is NOT SETTLED BY THIS BATCH; section 5 names
the test that would settle it.

### 2.6 Nulls, comparators, thresholds -- all declared before the run

  arm           | object removed                              | can it fail | role
  CAL-PERM      | sharing of a draw index between candidates   | NO, by cons.| CALIBRATION arm, explicitly NOT a null (mode 1)
  CAL-IID       | everything; iid normals at matched (D,K)     | no          | second calibration arm; var_cv is EXACTLY invariant under CAL-PERM
  NULL-IIDPHASE | shortness/structure of phase offsets; Y->unif| YES         | the null
  SENS-GRADED   | -                                           | -           | sensitivity demonstration, named comparator + threshold declared before run

SENS-GRADED (synthetic, known population off-diagonal exactly t), gates declared before
the run: (i) |offdiag - t| <= 0.02 for every t; (ii) K_eff_max monotone non-increasing in
t; (iii) at t=0, offdiag within 3/sqrt(D) of 0 and K_eff_max within factor 1.5 of K. ALL
THREE PASSED at both K=8 and K=25. Measured errors 0.0007-0.0069; K_eff_max at K=25 ran
24.21 -> 22.57 -> 17.84 -> 12.40 -> 7.37 -> 3.70 across t = 0 -> 0.75.

Ten known-answer controls (KAC-1..4) ran BEFORE any research number, all passed. KAC-1
checks the closed form of section 2.5 against a 400,000-draw brute-force Monte Carlo with
UNROUNDED Gaussian errors: relative max error 0.00243.

### 2.7 The frozen decision rule, and its failure

The five-branch rule (D1..D4, D0) with its exhaustiveness argument was frozen before the
run. IT EMITTED D2 ON ALL 18 FAMILY x GROUP CELLS -- INCLUDING ALL SIX NULL-IIDPHASE
CELLS.

DEVIATION DEV-3, recorded, and it is mine. As frozen, the rule scores each arm against
its own CAL-PERM comparator and never against the null. Because the forced m=35 rank
effect of section 2.3 is present in the null too, D2 fires on the null as well, and the
label therefore carries NO discriminating information. I report the rule's verdicts
verbatim in results.json and I do NOT re-score against a different rule. The real/null
contrast of section 2.4 is marked POST HOC in results.json under derived_post_hoc: the
null arm and the intent to compare it against the real arm were pre-registered, but the
RATIO statistic and its numerical reading were not, and carry no pre-declared threshold.

This is the fifth-obligation failure mode one level up: my branches exhausted the OUTCOME
SPACE OF THE STATISTIC but not the SPACE OF EXPLANATIONS FOR A D2. Exhaustiveness of a
decision rule is relative to the alternatives it can distinguish, and mine could not
distinguish "forced by the shared error dimension" from "property of the object".
KN-TECH-6c0e15 obligation 5 is written to say so.

## 3. T2 -- the adjacent-FFT-bin family, unmet since batch 3

Scored under BATCH-c45baf's admissible Stage B tuple EXACTLY as specified: m=35,
k_enum=0, k_fft=10, p in {2,3,5}, beta_sieve=50, k_lat=15. Sieve at dimension
m+k_lat=50, N = 4253, certificate 0/63,795 violating, and N matches the batch-3 archive
exactly. The tuple SERVES; no reason to depart from it arose.

The law's own correction term exp(k_fft/3 (sigma_s pi/p)^2) -- MODELED, not measured --
is 3732 (p=2), 38.68 (p=3), 3.728 (p=5). NOT identically 1, which was the condition the
card set.

  p | group          | K   | offdiag(R_raw) | ST-6 ratio | ST-5c ratio
  2 | adjacent bins  | 10  | +0.0063        | 0.8728     | 0.9641
  2 | uniform bins   | 10  | -0.0033        | 0.9087     | 0.9858
  3 | adjacent bins  | 20  | +0.0001        | 0.8073     | 0.9660
  3 | uniform bins   | 10  | -0.0009        | 0.9128     | 0.9847
  5 | adjacent bins  | 20  | -0.0059        | 0.8282     | 0.9641
  5 | uniform bins   | 10  | +0.0180        | 0.8886     | 0.9877

TWO OBSERVATIONS.
1. THE STAGE B DESIGN HAS NO COMMON MODE. offdiag(R_raw) for adjacent bins is ~0.006, not
   ~0.9999. The reason is structural: the discriminating phase is 2 pi (ahat.c)/p, and an
   adjacent bin differs by a FULL bin, so the offset is 2 pi/p -- large, not small. The
   forced common mode F-1 is a property of the AD-HOC s + unit_k near-miss family of
   batches 1, 2 and 4, and it is absent from the principled adjacent-bin family. This is
   a structural improvement in the Stage B design that had not been stated before.
2. AT MATCHED K THE EXTRA DEPARTURE IS SMALL. The only clean matched-K comparison is p=2
   (K=10 both): adjacent 0.8728 vs uniform 0.9087, i.e. 4.0% additional. Against the
   dim-60 near-miss family's 12.6% (K=8) and 21.7% (K=25) relative to its null, this is
   much weaker.

LIMITATION LIM-T2, recorded. At p=3 and p=5 the adjacent-bin family has K=20 and the only
uniform group scored at that design has K=10 or K=256. Since the forced m-rank effect
makes the statistic strongly K-dependent, THOSE TWO ROWS HAVE NO MATCHED-K COMPARATOR AND
I DO NOT COMPARE THEM. A uniform group at K=20 was not scored; that is a design gap in my
T2 and it is mine.

## 4. Deviations, limitations and unexpected observations, in one place

DEV-1  KN-TECH-14efa5's two functional numbers are not reproducible from the entry (no
       basis seed recorded). Tools confirmed functional; pinned numbers not confirmed.
       Version drift to passagemath 10.8.8.
DEV-2  My hand-computed forced value F-1 (0.98258, band [0.95, 0.995]) was MISSED:
       measured 0.9999. The exact closed form in the same run predicts 0.9999. Band
       recorded as missed, not restated.
DEV-3  My frozen decision rule emitted D2 on all 18 cells including all six null cells and
       therefore does not discriminate. Verdicts reported verbatim; the real/null contrast
       is marked POST HOC.
DEV-4  (pre-run, recorded in the script's changelog) Three defects in my own design were
       caught by synthetic instrument checks BEFORE any measurement run and fixed there:
       offdiag(R_ctr) forced to -1/(K-1) with a zero-spread comparator (mode 1); scoring
       z1/z2 against asymptotic K-1 and K which manufactured a ~4-sigma departure out of
       genuinely iid data; and var_cv being exactly invariant under CAL-PERM (mode 1
       again). Changelog v1->v2->v3.
DEV-5  The runtime harness refused the file-write tool for report.md; the narrative
       deliverable is carried in results.json (report_markdown) and in the executor's
       response. No content dropped, nothing outside write_scope touched.
LIM-1  ONE instance, toy scale, d=60, q=127. No replication across instances.
LIM-2  The ensemble is error draws over one FIXED database. The complementary ensemble --
       independent databases at fixed error -- was not measured.
LIM-T2 No matched-K uniform comparator for the p=3 and p=5 adjacent-bin rows.
LIM-3  The closed form is exact for GAUSSIAN e; the run uses a ROUNDED Gaussian. KAC-1
       bounds the resulting disagreement at 0.24% on a synthetic instance.
UNEXPECTED  The secret-distribution group's marginal sd_ratio_to_iid is 5.5382, i.e. 5.5x
       ABOVE the iid prediction, where the near-miss group is 0.1382, i.e. 7.2x below.
       Both groups are "short-offset". Recorded; not explained here.

## 5. What would settle what this batch could not

Named because a partial reading owes forward guidance, not because I am recommending a
batch:
1. Whether the section-2.4 departure is forced for EVERY valid dual family: construct a
   dual family whose Y columns are deliberately orthogonalised in the S-metric and
   re-measure. The closed form makes the prediction free.
2. Vary d at fixed N and K -- the red team's RC-5, still untested -- which is also the
   only direction in which the forced m-rank effect of section 2.3 can be separated from
   the rest.
3. Replicate across instances. Everything here is a single draw.

## 6. Explicit non-claims

- No ML-KEM break. No attack implemented, run, or claimed. No speedup.
- No security proof and no security claim in either direction.
- No FIPS 203 parameter set affected or cleared. Toy scale, AGENTS.md rules 4 and 7.
- The independence heuristic is NEITHER validated NOR refuted here. A measured departure
  on one toy instance is a measurement, not a verdict on a heuristic.
- No cost claim, no exponent moved, no Nf recomputed or corrected.
- No lane closed or opened. No EV-MLKEM-* or KN-* status change.
- The membership certificates certify VECTORS. No discrete-log solve and no factor-base
  relation is claimed: solve_claim_certificate = none.

## 7. Artifacts

All under coordination/goals/GOAL-MLKEM-004/batches/BATCH-a2bb63/tasks/TASK-20260804-f58d34/:
rebuild_transcript.txt, dependence.py, vectors.json, results.json, receipt.json; plus
knowledge/techniques/KN-TECH-6c0e15.md.

vectors.json carries the raw integers of all three families, so every certificate is
checkable from the snapshot alone with stock numpy and no g6k, no fpylll and no
dependence.py. I ran that check: 0 violating of 959,745 entries in int64, and 0 of 150
exact-bigint rows.
