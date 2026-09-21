# Red team — BATCH-a5b13c: PREREG-7 ciphertext-side noise census + block-size readout

`RT-20260814-174d78` / `TASK-20260814-c09076` / `BATCH-a5b13c` / `GOAL-MLKEM-005`.
Governed by `PREREG-7`
(`coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/tasks/TASK-20260814-d13724/prereg.md`),
notarized at commit `89bf454eaf67dffa0e9585e2bccfb4b2e2b1543c`. Reviews the lead
producer `TASK-20260814-c87a24`'s committed snapshot at commit
`6f6c0a0f645b6f762042500210d622675a15e7c1` (snapshot archive
`TASK-20260814-07bfae`, 10 declared paths). **All artifacts cited below were
read from this commit via `git show <sha>:<path>`, never from the working
tree.**

**Claim tier stays exactly DERIVATION (C1) / MEDIUM (C2), carried unchanged
from PREREG-7 and `H-MLKEM-11aabf`.** Nothing in this report is a measured
attack cost or an ML-KEM security claim. I changed no research status,
rescored no frozen hkz/HKZ-independence-lineage finding (not touched, not
re-litigated), modified no producer artifact, and made no commit.

## Inference record (AGENTS.md rule 12 disclosure)

```
requested_policy: review-adversarial
reasoning_effort: xhigh (per .claude/agents/red-team.md, role red-team's
  default_policy review-adversarial -> orchestration/model-policies.yaml)
fallback_allowed: false
degraded_allowed: false
independent_session_required: true (honoured: fresh Claude Code subagent
  invocation, independent of the Coordinator sessions that authored PREREG-7
  and of the lead producer's TASK-20260814-c87a24 session)
model_that_answered: claude-sonnet-5 (per this session's own runtime context;
  NOT independently probe-verified)
model_verified: false
model_verified_reason: >-
  AGENTS.md rule 12 is UNMET AND UNWAIVED in this goal (PREREG-7 section 7,
  restated there to bind this batch's own reviews too). No adapter probe
  receipt exists for this session; AUTORESEARCH_POLICY/AUTORESEARCH_BACKEND
  are unset.
independence_kind: PROCEDURAL, AND NEVER MODEL-LEVEL -- a fresh session,
  fresh git worktree state, own code written from scratch where claimed
  "independent"; not a claim of a different underlying model.
host_measured: >-
  hostname "vm", platform "Linux-6.18.5-fc-v20-x86_64-with-glibc2.39",
  Python 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0], 4 CPUs, 15Gi RAM.
  IDENTICAL character-for-character to the producer's own recorded
  environment.json host/python block. Very likely the same container/host
  image, recorded plainly as a property of the sandboxed execution recipe,
  not a claim of shared process state. Where this report claims bit-exact
  numeric reproduction (the census, beta figures), that reproduction is
  evidence of MECHANICAL/ARITHMETIC correctness of an independently-written
  implementation running the SAME pinned lattice-estimator commit, not
  evidence of code-level or model-level independence -- flagged once here,
  applies throughout.
estimator_commit_measured: /tmp/le, git HEAD 3e48ef421ec256afddb3e7d2249a77eab6e9ba12
  -- confirmed by this session's own `git log -1` in that clone, matching
  PREREG-7's pin exactly.
```

## Commit and change-set verification (recomputed myself, not taken on trust)

`git diff-tree --no-commit-id --name-only -r 6f6c0a0f6...` in this worktree
lists exactly the 10 paths the queue's `archive.path_sha256` block declares
(0 extra, 0 missing); parent is `4e0d3a0eb75da7240214d48b0e0c4bd24ff46307`,
matching the queue's recorded `parent_sha`. I independently `sha256sum`'d
three of the nine producer artifacts (`ciphertext_noise_census.py`,
`ciphertext_noise_readout.py`, `results_ciphertext_noise.json`), reading from
the git object database (`git show <sha>:<path>`, not the working tree), and
all three match the queue's declared `path_sha256` character-for-character.
**Every quotation of producer code, the writeup, or the results JSON in this
report is READ COMMITTED**, at `6f6c0a0f645b6f762042500210d622675a15e7c1`.
`H-MLKEM-11aabf.yaml` (an existing, pre-batch ledger record this batch does
not modify) and `tools/sage_free_estimator/` are also read committed, from
`HEAD` (`6969373c1a4ffc6b02ecad914b58b23df790e344`), a descendant of the
reviewed snapshot.

---

## claim_under_review

PREREG-7's Stage B headline: `T-CIPHNOISE-CLOSED` fires (CLOSED-ALL at
ML-KEM-512/768/1024); `beta(M0)==beta(M1)` exactly at every parameter set,
argued as a forced mathematical identity; `beta(M2)=617` at ML-KEM-1024 is
255 core-SVP bits below `beta(M0)=872`, against `H-MLKEM-11aabf`'s own
predicted 2-4 bit `minimum_effect`, in a regime with `reduced_m=236` against
base `m=n=1024`.

---

## PRIMARY FINDING (target 1) — the 255-bit M2 figure is dominated by a
## demonstrated instrument artifact, not a clean read of "removed
## compression noise"

### What I built and ran

Five probes, all under this task's `probes/` directory, none importing the
producer's `ciphertext_noise_census.py`/`ciphertext_noise_readout.py`,
against the SAME pinned `lattice-estimator` commit
(`3e48ef421ec256afddb3e7d2249a77eab6e9ba12`, already present at `/tmp/le` on
this host, confirmed at the pin). No lattice reduction anywhere — every call
is a closed-form `primal_bdd(..., red_cost_model=RC.MATZOV)` readout, matching
PREREG-7 section 5.4.

- `probes/probe1_m2_m_sweep.py` — 34-point sweep, `m` from 10 to 3000, same
  Kyber1024 `Xs=Xe=base CBD(eta1)` construction the producer's own M2 used
  (`Xs=base.Xs, Xe=base.Xe`, only `m` varied). Output:
  `probes/probe1_m2_m_sweep_output.json` (56.5 s wall clock, this host).
- `probes/probe2_m2_fine_boundary_scan.py` — fine (step-2) scan around the
  failure boundary and the `236->240` jump probe1 found, plus a 5x
  reproducibility check on `m=236`. Output:
  `probes/probe2_m2_fine_boundary_scan_output.json`.
- `probes/probe3_independent_census_and_m0m1_check.py` — from-scratch Stage A
  census + M0/M1 variance identity check (targets 2, 3, 5, 6 below). Output:
  `probes/probe3_independent_census_and_m0m1_check_output.json`.
- `probes/probe4_independent_beta_recompute.py` — closes the loop: this
  probe's own census + own variance formula fed into a fresh `primal_bdd`
  call (target 4 and target-3-of-the-completion-gate "re-run from scratch").
  Output: `probes/probe4_independent_beta_recompute_output.json`.
- `probes/probe5_single_sample_discontinuity.py` — the sharpest, cheapest
  single result: `m=233..239`, single-unit steps, ~1 CPU-second. Output:
  `probes/probe5_single_sample_discontinuity_output.json`.
- `probes/00_known_answer_control_output.txt` — independent re-run of
  `tools/sage_free_estimator/known_answer_control.py`, unmodified, in this
  session (target 4).

### Result

At the SAME Kyber1024 "clean" noise (`Xs=Xe=CBD(eta1)`, no compression term
— exactly M2's own noise construction), sweeping only `m`:

| `m` | `beta` | note |
|---|---|---|
| 10–216 | **no finite-cost configuration found** (`rop=inf`, `beta` key absent from the returned `Cost` — a `KeyError`, not a wrong number) | |
| 218 | 867 | first finite reading, close to key-side (855) |
| 219–236 | 788, 759, …, 558 (min), …, **617** (producer's own `m=236`) | chaotic, non-monotone, range ~558–899 |
| **236 → 237** | **617 → 908** | **+291 bits for Δm = +1 (0.1% of n=1024)** |
| 238–~800 | 899 → 856, smooth monotone decline | well-behaved regime |
| ≥850 | 855 (saturates, matches key-side exactly) | |

The sharpest single number: `probes/probe5_single_sample_discontinuity_output.json`
— `beta(m=236)=617`, `beta(m=237)=908`, **Δbeta = 291 for Δm = 1**. Re-run
five times at `m=236` (`probe2`), the value is perfectly deterministic
(`617` every time) — this is not measurement noise, it is a genuinely
non-smooth, reproducible *function shape* in `m`.

**Mechanism, source-verified, not merely observed.** `estimator/lwe_primal.py`
line 230-234 (`PrimalUSVP.__call__`): when `params.Xs <= params.Xe` (true
here — Kyber's `Xs`/`Xe` are both `CBD(eta1)`, so `<=` holds by equality),
the code applies the Bai–Galbraith embedding-enlargement trick,
`m_internal = params.m + params.n`. The subsequent `d`-optimizer
(`local_minimum(max(params.n, cost["beta"]), stop=cost["d"] + 1)`, line 284)
is **hard floored at `d >= params.n = 1024` regardless of how small the
original `m` is** — the search grid the scalar bisection walks becomes
extremely cramped when `params.m << params.n`, and the 1-D
`local_minimum`/`cost_simulator` optimizer (a bounded scalar search, not a
convex one) lands on different local optima a few units of `m` apart. This
is exactly the mechanism that would produce: total failure below a
threshold (no configuration in the collapsed search range), then a chaotic
band immediately above it, then a smoothing-out once `m` is large enough
that the search range is no longer degenerate — which is precisely what was
measured.

**Documented validity range for `m` relative to `n`, checked directly in the
source (task's own explicit ask): there is none for this attack path.**
`grep -rn "InsufficientSamplesError" estimator/*.py` shows `lwe_dual.py`,
`lwe_guess.py`, and `lwe_bkw.py` each raise it when the sample count is
insufficient for THEIR OWN success condition. `lwe_primal.py`/`lwe_parameters.py`
raise it only for `m < 1` (`LWEParameters.normalize`, line 55-56) — there is
**no lower bound check tied to `n`** anywhere in the `primal_usvp`/`primal_bdd`
call graph. `reduced_m=236` against `n=1024` is not flagged, warned about, or
rejected by the instrument in any way; it silently returns a number from deep
inside the demonstrated chaotic band.

### Plain answer to the task's direct question

**I do not think the 255-bit figure is a genuine finding about ciphertext-side
noise structure. I think it is dominated by an artifact of feeding
`primal_bdd` a sample-starved instance (`m=236` vs `n=1024`, ~23%) in a
regime its own `d`/`beta` optimizer is demonstrably not well-behaved in** —
reproducible, but non-smooth to the point of a 291-bit swing for a one-sample
change in `m`. This is not a rejection of `H-MLKEM-11aabf`'s directional
claim (M2 < M0 is itself forced by construction: dropping noisy coordinates
cannot increase attacker difficulty on the *retained* coordinates' own noise
level) — it is a rejection of trusting **this specific magnitude** as a
"2 to 4 core-SVP bit" vs. "255 bit" distinction. The producer's own writeup
already flags this exact ambiguity in prose ("this task does not conclude
whether the 255-bit figure represents a sound security-relevant effect...
or is dominated by a different, much larger effect intrinsic to feeding
`primal_bdd` a sample count far below the base scheme's own `m=n`"); this
report converts that flagged-but-unresolved ambiguity into a **measured,
reproducible, mechanistically-explained** finding in the second direction.
**Where this goes against the producer's own T-CIPHNOISE-CLOSED headline: it
does not overturn CLOSED (M2's beta is still far below key-side's 855 either
way, and F(b) genuinely did not fire at the producer's own m=236), but it
means the specific "255 bits, ~2 orders of magnitude beyond prediction"
figure PREREG-7 licenses citing under T-CIPHNOISE-CLOSED's own "cite the
exact number" clause should not be read as a stable measurement of the
mechanism `H-MLKEM-11aabf` describes.**

### Cheapest falsification of this headline, with cost

`probes/probe5_single_sample_discontinuity.py`: 7 `primal_bdd` calls,
< 1 CPU-second, already run. Re-running it is the cheapest possible check;
it already falsifies "beta responds smoothly to sample count near `m=236`."

---

## FINDING 2 (target 2) — `beta(M0)==beta(M1)` is a genuine, independently
## reproduced identity — AND it is a PREREG-7 protocol-design degeneracy,
## not a producer execution defect

### Independent reproduction

`probes/probe3_independent_census_and_m0m1_check.py` builds its own
`compress_d`/`decompress_d`/centering, its own fibre census, and its own
mixture-variance formula (`E[X^2] = Σ p_c · E[X^2|c]`) — no import of the
producer's `build_m0`/`build_m1`. Result, at **both** `d_u=10` and `d_u=11`:

```
d_u=10: M0 variance = M1 variance = 10240000/11082241 EXACTLY
d_u=11: M0 variance = M1 variance = 4264448/11082241  EXACTLY
```

Then `probes/probe4_independent_beta_recompute.py` feeds these independently
computed variances into a fresh `primal_bdd` call and gets `beta(M0)=404,
633, 872` for Kyber512/768/1024 — **matching the producer's reported figures
exactly**, and (trivially, given the identity) matching `beta(M1)` too. This
is **REPLICATED**, not single-source: two independent code paths (producer's,
mine), same pinned instrument, same numbers.

### Is it forced, and by what, exactly?

Yes — and the mechanism is not merely "the census happens to make it so."
PREREG-7 section 3.2 specifies M1 as: build the class-conditional mixture,
then **"the estimator is fed a single effective distribution constructed as
this properly class-weighted mixture."** Given that M0's own construction is
literally "convolve `Xe` with the population-average (i.e., unconditionally
mixed) compression-error distribution," and the classes M1 conditions on
**partition** the full population, the two constructions are the same
probability distribution by the law of total variance/expectation applied to
a mixture over a partition — independent of what the actual class
probabilities or per-class distributions are. **No execution of PREREG-7's
literal M1 specification, however careful, could have produced a different
number from M0.** This is not a coincidence of `q=3329`'s specific fibre
counts; my independent check confirms the identity holds at BOTH `d_u=10`
(767×3/257×4 partition) and `d_u=11` (767×1/1281×2 partition) — two
structurally different partitions, same forced equality — which is exactly
what the algebraic argument predicts and a coincidence-based account would
not.

### The deeper point: this is a PREREG-7 design defect, not a producer defect

`H-MLKEM-11aabf`'s own `predictions` field states, unambiguously: **"beta(M1),
beta(M2) relative to beta(M0) at ML-KEM-1024 ... a reduction of 2 to 4
core-SVP bits"** and **"at ML-KEM-512/768 ... under 1 bit."** Read literally,
this predicts M1 alone should show a nonzero (if small) reduction. Given
PREREG-7 section 3.2's own instruction to feed M1 to the estimator as **one
combined distribution**, and given the pinned estimator's own `Xe` cost path
being **variance-only** (independently confirmed: `grep`-ing
`estimator/lwe_primal.py`'s call graph for every `Xe.` use shows only
`Xe.stddev`, no pmf, no higher moment — the producer's own section-1
obligation-4(a) finding, which I did not need to re-derive since it is a
direct, checkable source-grep, not a probability calculation), **there was no
way for M1, as PREREG-7 §3.2 specifies it, to ever produce a number different
from M0** — the identity is forced before any measurement, by the
specification plus the instrument's own variance-only cost path, not by
anything about `q=3329`'s fibre structure. `H-MLKEM-11aabf`'s own
falsification-condition list (`F(a)`–`F(d)`) has **no condition that fires**
when M1's own stated `minimum_effect` (nonzero, 2–4 bits / under 1 bit) fails
to materialize — only `F(b)` (M2-specific) is checked. The measured M1 effect
(exactly 0 bits, not "2 to 4" or "under 1 as a nonzero floor") is a strict
miss against the hypothesis's own stated prediction, and nothing in PREREG-7
or `H-MLKEM-11aabf` was built to notice this. **I flag this as a
methodological finding for this goal, in the same spirit as (not the same
lane as, and not restating) this goal's own prior instrument-design confounds
`KN-FIND-d29ece`/`KN-FIND-7ffdd0`: a noise-heterogeneity hypothesis that
specifies "feed the estimator one combined distribution" for a
per-coordinate-heterogeneous construction has, by that specification alone,
already collapsed the heterogeneous model to the homogeneous one before any
data is measured — C2's "three declared noise models" are, in the instrument
this campaign has pinned, effectively TWO distinguishable readouts (M0≡M1;
M2 distinct only via dimension change), not three.** A future hypothesis
wanting to test genuine per-coordinate noise heterogeneity against this
estimator would need either a different attack construction (e.g. a
row-rescaling/whitening technique, which is a real, different technique from
mixture-then-convolve, and which this pinned estimator's `LWEParameters` API
does not expose either) or an instrument extension — this is forward
guidance, not a closure of the noise-heterogeneity question itself.

### Where this control is a genuine null-object check, and where it over-delivers

The task's own suggested null control (§ completion gate) was: confirm M1 and
M0 are numerically much *closer* at ML-KEM-512/768 than at ML-KEM-1024,
matching the hypothesis's own "under 1 bit vs 2-4 bit" prediction gradient. I
built this control (`probe3`'s `target2` section) and it does NOT show a
gradient — it shows **exact equality at both**, which is a stronger
(degenerate) version of "closer," and directly explains why: the identity's
proof does not depend on which `d_u` or which specific class split is used,
only on the classes partitioning the population, which holds identically at
every `d`. Reporting the queue's suggested control's actual outcome plainly,
even though it is a *stronger* finding than what was asked for: the intended
discriminating gradient does not exist because the underlying quantity is
never gradient-shaped — it is a step function fixed at exactly zero
everywhere M1, as specified, could ever apply.

### Cheapest falsification, with cost

Re-run `probes/probe3_independent_census_and_m0m1_check.py`
(< 1 CPU-second, pure stdlib, no estimator/network needed) at any other `d`
value the census computes (4, 5, 12) — the identity is a two-line algebraic
consequence of a partition-preserving mixture, so it will hold at every `d`;
I did not find a counterexample and do not expect one to exist. The
falsifiable claim here is not "is the identity true" (it withstood the
check) but "could PREREG-7's own M1 specification ever have shown otherwise"
— that is settled by reading PREREG-7 §3.2's own text (zero compute, already
done above).

---

## FINDING 3 (target 3) — Stage A census independently reproduced exactly

`probes/probe3_independent_census_and_m0m1_check.py`'s `target3_*` section,
own from-scratch `compress_d`/`decompress_d` (own re-implementation of
`round_half_up`, not copied from the producer's file), all 3329 residues:

```
d_u=11: {1: 767, 2: 1281}  -- matches producer AND H-MLKEM-11aabf.predictions exactly
d_u=10: {3: 767, 4: 257}   -- matches producer AND H-MLKEM-11aabf.predictions exactly
```

Both `target3_matches_producer_and_prereg7` flags are `true`. **REPLICATED.**
I also independently confirmed `d=12`: every one of the 3329 fibres is a
singleton, and the raw (uncentered) `x - Decompress_12(Compress_12(x))` is
`0` for every one of the 3329 residues — `probes/`'s
`target5_d12_raw_vs_centered_check.distinct_raw_x_minus_rt_values == [0]`.

### Cost

< 1 CPU-second (pure stdlib, 3329-residue loop × 5 `d` values).

---

## FINDING 4 (target 4) — key-side baseline independently re-verified,
## unmodified

Two independent methods, both in this session:

1. **Re-run of the pinned, unmodified control**:
   `probes/00_known_answer_control_output.txt` — fresh invocation of
   `tools/sage_free_estimator/known_answer_control.py`, this session,
   result: `Kyber512 beta=389, Kyber768 beta=606, Kyber1024 beta=855`,
   `primal_bdd` delta `0.00e+00` against the archived Sage reference for
   Kyber512/768 (Kyber1024 has no archived Sage reference, matching the
   harness's own documented scope). **Matches the producer's R-CN-OUT-0
   transcript character-for-character.**
2. **A second, independent call**, in `probes/probe4_independent_beta_recompute.py`,
   calling `primal_bdd(schemes.KyberXXX, red_cost_model=RC.MATZOV)` directly
   (not via the known-answer-control script): `beta_key_side_independent =
   389, 606, 855` — identical.

**REPLICATED via two independent methods**, neither recomputed under any
modified model, matching PREREG-7 §3.1's own instruction that this figure is
"READ, not recomputed."

---

## FINDING 5 (target 5) — the two disclosed protocol deviations

### The FIPS 203 fetch and quoted excerpt

Confirmed independently: `inputs/MLKEM-DUAL-SOURCES-20260802/fips203_selected_text.txt`
and `extracts/fips203/front_matter.txt` (read from `HEAD`,
`6969373c1a4ffc6b02ecad914b58b23df790e344`) carry only FIPS 203's front
matter/abstract; `grep -rl "Compress" inputs/MLKEM-DUAL-SOURCES-20260802/`
returns **zero hits** anywhere in the committed corpus. The producer's claim
that the committed corpus lacked the needed passage is confirmed, not merely
trusted.

I then performed **my own, second, independent fetch** of
`https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf` (not the
producer's cached copy) and ran `pdftotext -layout` on it myself, in this
session. Independently extracted text, section 2.3 and section 4.2.1:

```
⌈𝑥⌋   The rounding of 𝑥 to the nearest integer. If 𝑥 = 𝑦 + 1/2 for some
       𝑦 ∈ ℤ, then ⌈𝑥⌋ = 𝑦 + 1.

Compression and decompression. Recall that 𝑞 = 3329, and that the bit
length of 𝑞 is 12. For 𝑑 < 12, define
    Compress_d : Z_q -> Z_2d,  x |-> round((2^d/q)*x) mod 2^d
    Decompress_d : Z_2d -> Z_q, y |-> round((q/2^d)*y)
Division and rounding in the computation of these functions are performed
in the set of rational numbers. Floating-point computations shall not be
used.
```

**This matches the producer's quoted excerpt in `ciphertext_noise_writeup.md`
word-for-word and symbol-for-symbol** (verified by direct comparison, not
paraphrase). The producer's reading (round-half-up, ties broken upward;
coincides with round-half-away-from-zero on the non-negative domain used
here) is correct and matches FIPS 203's own text exactly. **No mismatch
found — this claim withstands the check.**

**A minor, non-load-bearing observation worth recording plainly**: FIPS 203
also states, immediately after the definitions, "decompression followed by
compression preserves the input" — i.e. `Compress_d(Decompress_d(y)) = y`
for `y ∈ Z_{2^d}` (the *codeword*-first direction) — and separately notes
that the reverse (`Decompress_d(Compress_d(x)) = x` for `x ∈ Z_q`, the
*residue*-first direction the census actually measures) is only
approximately true for large `d`, never claimed exact. The producer's census
correctly measures the residue-first direction and does not conflate it with
FIPS 203's own (different, always-exact) codeword-first guarantee; I checked
this distinction directly since conflating the two would be an easy,
plausible-looking error, and did not find it made anywhere in the producer's
artifacts.

### The centering-bug fix — checked for recurrence elsewhere

Read `ciphertext_noise_census.py` and `ciphertext_noise_readout.py` in full.
`centered_delta`/`centered` is used consistently in **both** `build_m0`'s
`compression_error_distribution` and `build_m1`'s `compression_error_by_class`
(the only two places compression-error variance is computed) — `grep -n "x -
rt\|centered_delta"` on both files shows the fix applied at every variance
site. `build_m2_kyber1024` uses `base.Xe` directly (no delta computation at
all — correct, since M2's construction is "noise = Xe alone" by the singleton
identity, not a delta computation).

**One place still uses the raw, uncentered `x - rt`**: `ciphertext_noise_census.py`'s
`mutual_information_delta_bin_d12` (line 133, `deltas.append(x - rt)`), which
does **not** call `centered_delta`. I checked whether the same class of bug
could be lurking here too — independently, in `probes/probe3_...py`'s
`target5_d12_raw_vs_centered_check`: at `d=12`, every one of the 3329 fibres
is a singleton (by the census itself, `2^12=4096 > q=3329`), so
`Decompress_12(Compress_12(x)) = x` **exactly**, for every `x`, with **zero**
exceptions — meaning the raw difference is identically `0` and centering it
changes nothing (`centered(0) = 0`). **Confirmed by direct, independent
computation (not merely asserted): the one remaining uncentered-subtraction
site cannot be affected by the wraparound bug, because it only ever
evaluates to `0` at `d=12`.** No recurrence of the bug found.

### Cost

FIPS 203 fetch + extract: ~10 s (network + `pdftotext`), already run. Grep
for other uncentered sites: < 1 s. `d=12` exactness re-check: < 1 s
(subsumed in probe3's run).

---

## FINDING 6 (target 6) — the null control at ML-KEM-512/768

`probes/probe3_...py`'s `target6_null_control_d10_singleton_count`:
independently recomputed `d_u=10` fibre census, singleton count = **0**,
confirmed forced by the census (not an unexplored construction choice —
`767×3 + 257×4 = 3329` with every fibre size ≥ 3, so no size-1 fibre can
exist at `d_u=10` under this exact partition). `M2_NOT_APPLICABLE_is_forced_by_census:
true`. **REPLICATED.**

---

## objections

1. **[PRIMARY]** `beta(M2)=617`/the 255-bit gap sits inside a demonstrated,
   reproducible, non-smooth region of `primal_bdd`'s own `m`-response
   (probes 1/2/5); trusting this specific magnitude as a measurement of
   "removed compression noise" is not supported by the evidence, even though
   the *direction* (M2 < M0) is not in dispute.
2. `beta(M0)==beta(M1)` is correct and forced, but the force comes from
   PREREG-7 §3.2's own "single effective distribution" instruction interacting
   with the pinned estimator's variance-only `Xe` cost path — a protocol
   design degeneracy that means C2 tested two distinguishable models, not
   three, and `H-MLKEM-11aabf`'s own M1-specific prediction ("2-4 bits" /
   "under 1 bit") is unfalsifiable-as-stated and was silently missed (0 bits
   measured) without any `F()` condition noticing.
3. `H-MLKEM-11aabf`'s own `HEUR-MLKEM-11aabf-1.random_model_justification`
   flags "whether the conversion instrument correctly propagates a
   reduced/reweighted noise vector into a block-size estimate" as "an
   instrument question, not a modelling one" — this report converts that
   flagged-but-untested risk into a demonstrated, reproducible failure mode
   in the specific regime (`m<<n`) M2 exercises.

## required_controls

- [DONE, this report] `m`-sweep control bracketing `reduced_m=236` at fixed
  clean Kyber1024 noise (probes 1, 2, 5).
- [DONE, this report] Null control: 0 singletons at `d_u=10`, forced
  (probe 3, target 6).
- [DONE, this report] Independent from-scratch census, M0/M1 identity check,
  and independent `primal_bdd` recomputation of every headline `beta`
  (probes 3, 4).
- [NOT DONE, recommended if this lane continues] A control at a DIFFERENT
  base scheme/dimension (e.g. a synthetic `n=256` or `n=512` LWE instance with
  a comparably-sized `m<<n` reduction) to check whether the chaotic-band
  width and location scale with `n`, or are an `n=1024`-specific numerical
  coincidence of this estimator build. Cost: ~5-10 minutes, same instrument,
  no new dependency — cheap, not run here because it is outside this task's
  named targets and PREREG-7's own scope (ML-KEM-512/768/1024 exactly).

## counterexample_or_mutation

`probes/probe5_single_sample_discontinuity.py`: `m=236 -> beta=617`,
`m=237 -> beta=908`. A one-sample mutation of the M2 sample count — nothing
about the underlying cryptographic hardness — flips the reading from
"255 bits below M0" to "36 bits ABOVE M0" (908 > 872), which would have fired
`F(b)` (`HEUR-MLKEM-11aabf-1`'s own falsification condition) had the
producer's `reduced_m` computation landed on 237 rather than 236. This is
the cheapest, sharpest demonstration that the specific magnitude reported is
not a stable function of the underlying object.

## baseline_comparison

Not applicable in the form the role contract's default language names
(Pollard-rho/BSGS/ECDLP-specialized baseline): this batch is an LWE/lattice
cost-model readout under FIPS 203/ML-KEM, not an ECDLP experiment, and
PREREG-7 §7 explicitly scopes it to `primal_bdd`/`RC.MATZOV` only (declared
gap G-4, not a defect). The applicable "baseline" this batch actually uses is
the existing, already-known-answer-controlled key-side `beta` figures
(389/606/855), which I independently re-verified twice (Finding 4). The
**closest specialized baseline this batch does NOT test**, worth naming
explicitly per the role contract's spirit: `dual_hybrid(fft=True)`, which the
harness's own known-answer control already exercises and controls
(agreement ~3e-13) but which PREREG-7 never invokes for M0/M1/M2 — the
literature (and this harness's own README) does not establish that
`primal_bdd` dominates `dual_hybrid` in the reduced-sample-count regime M2
constructs, and the chaotic-band finding above raises the possibility that a
different attack path might behave more smoothly under `m<<n`. This is a
scope observation, not a defect — PREREG-7 §7/G-4 declares this out of scope
explicitly, and I do not fault the producer for honoring a frozen protocol's
declared scope.

## heuristic_challenges

- `HEUR-MLKEM-11aabf-1`'s `random_model_justification` argues the
  singleton/doublet conditioning is "structural, not a random-object
  appeal," and correctly identifies the one open risk as "whether the
  conversion instrument correctly propagates a reduced/reweighted noise
  vector into a block-size estimate... an instrument question." This report
  supplies exactly the missing instrument-level check the heuristic's own
  text calls for, and the answer, in the specific regime M2 exercises, is
  negative: the instrument does not propagate a reduced sample count
  smoothly near `m=236`.
- `HEUR-MLKEM-11aabf-1`'s stated `falsification_condition` (`beta(M2) >=
  beta(M0)` at ML-KEM-1024) is well-posed and did not fire at the producer's
  own `m=236` — but Finding 1 shows it is one unit of `m` away from firing,
  which is not itself a falsification (the falsification condition is
  defined at the actual computed `reduced_m`, and PREREG-7 does not license
  moving it after the fact) but is a material fact about how close the
  reported "NOT FIRED" verdict sits to the opposite reading.

## cost_model_challenges

- No o(1)/polylog overhead applies here (this is not an asymptotic claim);
  the relevant "hidden constant" is the `nn` (nearest-neighbour-cost variant)
  tunable inside `RC.MATZOV`, which the producer already identified,
  source-verified, and swept (K-sensitivity table, `ciphertext_noise_writeup.md`
  R-CN-OUT-2) — I did not re-run this sweep (outside my primary targets,
  budget spent on the M2 instability finding instead) but the producer's own
  disclosure that they do not assert `nn` is what `H-MLKEM-11aabf`'s prose
  calls "K" is an honest, correctly-scoped disclosure, not an overclaim.
- Per-attempt-cost-vs-total-expected-cost bookkeeping does not apply: this
  batch reports no attack success probability or attempt count anywhere —
  it is a `beta`/`rop` readout only, correctly never described as a measured
  attack cost (PREREG-7 §7, `H-MLKEM-11aabf.interpretation_limits`, both
  checked and both honored throughout the producer's writeup).

## reduction_and_scope_challenges

`H-MLKEM-11aabf.interpretation_limits` states this hypothesis "does not
touch and does not contradict GOAL-MLKEM-005's proven convexity ceiling
G <= log2 M" and is "unrelated to best-of-M ciphertext selection." The
producer's writeup and `ciphertext_noise_writeup.md`'s closing section both
restate this scope limit verbatim and do not exceed it anywhere I found. No
reduction chain is claimed by `H-MLKEM-11aabf` (`reduction_chain.corollaries:
[]`), so no reduction-instantiation check applies here.

## proof_architecture_challenges

Not applicable — `H-MLKEM-11aabf.proof_search_map.not_applicable_reason` is
correctly marked `not_applicable` (this is a closed-form census plus a
labelled instrument readout, not a proof-search construction), and PREREG-7
§0.1 independently checks this against `docs/inventor-protocol.md` section 8
rather than assuming it. I re-checked this classification and agree: there is
no bottleneck-reproduction, observation-collision, quantifier-order, or
method-ceiling structure to audit in either C1 or C2.

## narrowest_supported_statement

Stage A's exact census (767/1281 at `d_u=11`; 767/257 at `d_u=10`) is
independently REPLICATED and stands on its own, regardless of anything else
in this report (PREREG-7 §6, unaffected by any Stage B finding). The
key-side `beta` figures (389/606/855) are independently REPLICATED via two
methods. `beta(M0)==beta(M1)` is independently REPLICATED and is correctly
described as forced — but the force comes from PREREG-7's own M1
specification colliding with the pinned estimator's variance-only cost path,
not from a substantive finding about ciphertext-side noise heterogeneity;
C2, as actually executable against this pinned instrument, tests two
distinguishable models (M0≡M1, and M2), not three. `beta(M2)=617` is
independently REPLICATED as an ARITHMETIC fact (feeding `primal_bdd` exactly
this construction at exactly `m=236` deterministically returns 617) but is
NOT supported as a stable or trustworthy measurement of "the effect of
removing compression noise" — the same construction one sample away returns
908, and the function is provably chaotic in the surrounding region, with no
validity-range guard in the instrument to have warned against using it. The
`T-CIPHNOISE-CLOSED` verdict itself (ciphertext-side worse than key-side at
all three parameter sets) is supported and does not depend on trusting the
255-bit magnitude specifically: even the noisiest reading found in the
chaotic band (`beta=558` at `m=222`) remains far below `beta(key-side)=855`,
so CLOSED would fire under any value in the explored range. **What is NOT
supported is the specific "255 bits, ~2 orders of magnitude beyond
`H-MLKEM-11aabf`'s predicted 2-4 bit floor" characterization as a measurement
of the hypothesized mechanism**, and any downstream use of "255 bits" as a
citable figure (e.g. in a knowledge-promotion write-up) should carry this
report's finding alongside it.

## next_concrete_action

Before any knowledge-promotion or citation of the specific "255 bits"/"617"
M2 figure: either (a) find or construct a lattice-cost instrument/attack path
for the `m<<n` regime that is documented as valid there (none is currently
pinned in this campaign), or (b) reformulate M2 to avoid the extreme
under-determined regime — e.g. test whether a LESS aggressive dimension
reduction (a partial-drop, keeping some doublet coordinates with their own
higher noise rather than an all-or-nothing keep/drop) lands in the smooth
region (`m >= ~240` in this specific case) and still shows a directional gain,
which would be a strictly more defensible number than the current one. This
is a new, separately-commissioned measurement under PREREG-7's own declared
forward boundary (§3.6) — not licensed by this report or by PREREG-7 alone.

## artifact_paths

All under this task's `write_scope`
(`coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/reviews/TASK-20260814-c09076/`),
listed explicitly per declared gap G-1, for the Coordinator's ledger archive
to extend `TASK-20260814-c09076`'s declared path set with:

```
red_team_report.md
probes/00_known_answer_control_output.txt
probes/probe1_m2_m_sweep.py
probes/probe1_m2_m_sweep_output.json
probes/probe1_m2_m_sweep_stderr.log
probes/probe2_m2_fine_boundary_scan.py
probes/probe2_m2_fine_boundary_scan_output.json
probes/probe2_m2_fine_boundary_scan_stderr.log
probes/probe3_independent_census_and_m0m1_check.py
probes/probe3_independent_census_and_m0m1_check_output.json
probes/probe3_stderr.log
probes/probe4_independent_beta_recompute.py
probes/probe4_independent_beta_recompute_output.json
probes/probe4_stderr.log
probes/probe5_single_sample_discontinuity.py
probes/probe5_single_sample_discontinuity_output.json
probes/probe5_stderr.log
```

17 paths (this file + 16 probe artifacts). All `.py` probes are re-executable
as-is with `PYTHONPATH=tools/sage_free_estimator/shim:<pinned-lattice-estimator-clone>
python3 -B probes/<name>.py` from the repository root (probes 1, 2, 4, 5) or
with no dependency at all (probe 3, pure stdlib); commands and pin used are
recorded inline in this report and in each probe's own docstring.

---

## Single-source vs. replicated — explicit summary

| claim | status |
|---|---|
| Stage A census (767/1281 at d_u=11; 767/257 at d_u=10) | **REPLICATED** (independent from-scratch code, probe3) |
| d=12 gate / I(delta;bin)=0 | **REPLICATED** (probe3) |
| beta(key-side) = 389/606/855 | **REPLICATED** (two independent methods: probe 00 rerun, probe4) |
| beta(M0)=beta(M1) exactly, all 3 sets | **REPLICATED** (probe3's variance identity; probe4's beta recompute for M0) |
| beta(M2)=617 at reduced_m=236 | **REPLICATED as an arithmetic fact** (probe4); its INTERPRETATION as a stable measurement is the primary objection above, not merely single-source-doubted but actively counter-evidenced |
| M2's beta is chaotic/non-monotone for m near 236 | **NEW finding, this report, this session** (probes 1, 2, 5) — not previously reported anywhere in the producer's artifacts, though the producer's own writeup flagged the *possibility* in prose without measuring it |
| FIPS 203 rounding-convention quote accuracy | **REPLICATED via a second, independent network fetch** (this session's own `curl`+`pdftotext`, not the producer's cached copy) |
| No InsufficientSamplesError-style guard exists for m<n in primal_usvp/primal_bdd | **NEW, source-verified this session** (grep of estimator/*.py) |
| Centering-bug fix applied consistently, no recurrence at d=12 | **REPLICATED/verified this session** (code read + probe3's exactness check) |
| Null control: 0 singletons at d_u=10 | **REPLICATED** (probe3) |
| PREREG-7 §3.2's M1 specification forces M0≡M1 regardless of census content | **Derived here from PREREG-7's own text + the producer's own section-1-obligation-4a source-grep finding (which I did not need to re-derive independently, since it is a direct, checkable code-search result, not a probabilistic claim)** |
