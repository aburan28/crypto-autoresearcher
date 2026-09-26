# EXP-WESO-9e2d6d — implementation note (Executor, TASK-20260926-41c7e7)

Frozen protocol: `experiments/EXP-WESO-9e2d6d/specification.yaml` v1, sha256
`630a91c9792f26d3609b89cfb3e57613367c52aa29f900e74f1b381231a4e756`. Before any
file was written, I checked that this hash equals the committed bytes at
snapshot commit `3d8faa394` (`git show 3d8faa394:<path> | sha256sum`). No
separate TASK-20260926-b8e6be receipt file exists in the tree, so the snapshot
commit served as the receipt. Approval: DEC-20260926-ec2847 (AC-1..AC-8).

This note describes what the code does and every deviation. It draws no
conclusion about Heuristic 1 or HEUR-WESO-516558-2.

## 1. Environment

- PARI/GP 2.15.4, `/usr/bin/gp -> gp-2.15`, sha256
  `c9673623cad2eaa7cfe402e7b7d833f1f703689a09837026b6386aaafba6deec`. It is
  recorded in every manifest, and every worker runs it as
  `gp -q -f -D parisizemax=1G -D parisize=64M`.
- Python 3.11.15, numpy 2.4.6, sympy 1.14.0, mpmath 1.3.0, PyYAML 6.0.1. scipy
  is absent, so all statistics use numpy/mpmath or closed forms (Section 6).
- Host: 4 cores, 15 GB RAM, shared with another executor. The dispatching
  session capped this task at 3 workers.

## 2. Algebra, orders, and delta extraction (`implementation/weso.gp`)

- B_{p,inf} = (-1,-p | Q): i^2=-1, j^2=-p, k=ij. Elements are rational
  4-vectors in (1,i,j,k), and lattices are 4x4 matrices whose columns form a
  Z-basis. Canonical form: the HNF of d*B, with d the common denominator.
  `latcanon` strings are hashed with SHA-256 to give the order and ideal hashes.
- O_0 = Z<1, i, (i+j)/2, (1+k)/2> (spec). U-0 checks closure, that 1 is in
  O_0, |det Trd-Gram| = p^2, and that the P-minimum is 1.
- delta(O): Trd-Gram G of an LLL-reduced basis of O. P/pO = ker(G mod p) (a
  2-dim radical), and P = HNF(pO + lift(ker)). The Gram of Trd(x conj y)/p on
  P is integral, so x^T Gp x = 2 Nrd(x)/p. It is LLL-reduced with `qflllgram`,
  then `qfminim(Gp, Gp[1,1], 10000, 2)` enumerates every vector whose norm is
  at most the exact norm of the first LLL vector. That uses PARI's
  multiprecision Fincke-Pohst (flag 2). delta is the exact minimum of those
  vectors' exact integer norms, divided by 2. The LLL output alone is never
  taken as the minimum.
  - Stage A (RUN-WESO-aa2237) ran an earlier version that called
    `qfminim(Gp,,2,0)` (flag 0), which returns the minimum directly. Flag 0
    raised "precision too low" at 128-bit p during development, so the code
    switched to flag 2 before Stage B. Stage B re-applied the I-1 identity
    with the final code to all 1569 WISDE types: 0 mismatches
    (`raw-result.json` `I-1_recheck_final_code_additional`). The exact Stage-A
    code is preserved, hash-verified, in
    `runs/RUN-WESO-aa2237/code_snapshot/`.
- C-2 anchor: if delta > floor((p/2)^(1/3)) = `sqrtnint(p\2,3)`, the minimum
  is recomputed on the UNREDUCED P Gram with bound 2*delta (`deltarecheck`),
  and the sample is flagged (`c2` != 1). No sample in any run was flagged.
- U-2: every sampled order is checked (`isorder`: 1 is in O, closure under
  multiplication of the basis; plus |det Trd-Gram| = p^2), and the flag is
  stored per sample.
- |O^x| = number of vectors with x^T G x <= 2 from `qfminim`. PARI counts
  +/-v, so the count equals |O^x|. At p = 1019, O_0 gives 4.
- Gross lattice {x in Z + 2O : Trd x = 0}: `matkerint` of the trace map on a
  basis of Z + 2O, then an LLL-reduced Trd-Gram. Type label: bucket by the
  theta prefix `qfrep(G, p, 1)` (counts of Nrd = 1..p), then separate within
  the bucket by `qfisom`. No two WISDE types shared a label at any prime.
- Factorisation: PARI `factor`. It is verified (the product equals the integer
  and every factor passes `isprime`, a proof) and stored per record. The
  checker (Section 7) re-verifies every factorisation with sympy.

## 3. Sampler realisation (fixed before Stage B, unchanged in B-D)

Direct kernel sampling. For the start order O (basis B), `matunits(B,p,2,K)`
builds matrix units e11, e12, e21 of O/2^K O = M_2(Z/2^K):

1. Search small x in O whose characteristic polynomial X^2 - Trd(x)X + Nrd(x)
   has two distinct roots mod 2, and lift the roots 2-adically
   (`polrootspadic`, precision K+2).
2. Set e11 = (x - r2)/(r1 - r2) mod 2^K, an idempotent (checked).
3. Take e12 = e11 y (1 - e11) for the first basis element y that makes it
   nonzero mod 2, and e21 = lambda^-1 (1 - e11) z e11 with e12 e21 = lambda e11,
   lambda a unit.
4. Check all four matrix-unit relations mod 2^K.

A draw at walk length k takes an index in [0, 3*2^(k-1)), uniform from the
SHA-256 stream. It maps to P^1(Z/2^k) by v = (1, idx) for idx < 2^k, else
v = (2(idx - 2^k), 1). With alpha = v2 e11 - v1 e12 (matrix [[v2,-v1],[0,0]]),
the ideal is I = O alpha + 2^k O, the cyclic left ideal {M : M v = 0}.

The right order is O_R(I) = conj(I) I / 2^k. At k = 0 the draw returns O. The
same code builds O_0' (START-1, START-2): with ell = 3 and m = ceil(log_3 p) + 2,
it takes the right order of the cyclic O_0-ideal of norm 3^m whose P^1 index is
drawn from the declared seed (arm `O0PRIME`, index 0).

U-1 (p = 1019, k = 1, 2, 3):
- The sampler's support {cycideal(idx)} equals, as a set of canonical HNFs, an
  INDEPENDENT enumeration (`enumcyc`): O alpha + 2^k O over all alpha in
  O/2^k O, kept when the index is 2^(2k) and the ideal is not inside 2O. It
  uses only multiplication and HNF, with no matrix units. Counts: 3, 6, 12.
- The chi-square test on 3*10^4 draws runs on the drawn P^1 indices. The map
  from index to ideal is a bijection (support equality with no collisions), so
  this is the same test as on ideals.

## 4. Seeds and randomness (`common.py`)

- Per-draw seed = SHA-256("<master>|<stage>|<p>|<arm>|<index>") in hex, stored
  in every record. Stream block t = SHA-256(seed || t as 8-byte big-endian).
- `randbelow(n)` rejection-samples on bit-length(n-1) bits.
- Uniform floats (B-NULL multinomials, PC-2 contamination coin) take 53 bits
  per 8-byte word.
- There is no other randomness: gp's `random` is never used in any run.
- Arms: MAIN-k<k>, PC2, START1-k<k>, NULL-delta/NULL-type (B-NULL
  replicates), U1-k<k>, CLS, DET1, R1, R2, KS1, START2, PC3, NULL1, NULL2,
  SPOT, O0PRIME, PILOT, PILOT-NULL1, PILOT-NULL2.
- Records depend only on (start order, k, index), never on the worker or on
  scheduling order. DET-1 and the spot-checks compare every record field except
  `wall_s`, which cannot be byte-identical.

## 5. rho (`rho.py`)

Piecewise power series on unit intervals. R_k(xi) = rho(k - xi) =
sum a_i xi^i, with

- a_{i+1} = (b_i + i a_i) / (k (i+1)), from R_{k-1} = sum b_i xi^i;
- a_0 = b_0 - sum_{i>=1} a_i (continuity).

Coefficients are computed in mpmath at 60 digits and truncated at
1e-45 * a_1. All a_i with i >= 1 are nonnegative, so float Horner evaluation
suffers no cancellation. Valid for u <= 120.

- V-RHO-1: max error 1.1e-16 over 201 points on [1,2].
- V-RHO-2: u = 6.10191, 1/rho = 69232.05 against the source's 1/69232, a
  relative difference of 7.9e-7.
- V-RHO-3: monotone and positive on [0,100] at step 1e-3; the float and mp
  evaluations differ by at most 1.8e-16 relative.

`rho_inv` bisects. It gives u_m, and hence x_m, for TC-2 and the KS region.

## 6. Statistics (`stats.py`, `analysis.py`): realisations the spec leaves open

The spec does not always say how to realise a test. The choices below were
fixed before Stage C (they are part of the analysis_freeze):

- Wilson score interval, two-sided 99% (z = 2.5758293).
- Clopper-Pearson, two-sided 99%, from beta quantiles by bisection on a
  Numerical-Recipes continued-fraction incomplete beta. T1 = S_delta/S_NULL1,
  with its interval transformed by theta -> theta/(1-theta).
- TC-2: the "upper 99% Poisson confidence bound" is the upper end of the exact
  (Garwood) two-sided 99% interval, which is the 0.995 quantile.
- Two-sample smooth-count tests (SEED-1, KS-1, START-2): pooled two-proportion
  z-test, two-sided.
- KS: exact D on the pooled support. The p-value uses the asymptotic Kolmogorov
  law with the Stephens correction. The families are Bonferroni-corrected at
  family-wise alpha 0.01, with family = {KS} plus one smooth-count test per
  admissible u.
- TC-3: Wald 99% interval for the difference of the prime fractions.
- T1 trend: OLS of ln T1 on u over admissible cells, two-sided 99% t interval.
- Smooth means ell_max < B(u) strictly (Definition 1.3), with ell_max(1) = 1.
  TC-2 counts ln ell_max < x_m.
- q99.9 floors: 99.9th percentile (numpy linear interpolation) of 1000
  replicate TVs.
- k*(p): the smallest grid k such that every grid k' >= k is
  consistent-with-mixed, at every applicable level (delta; plus Gross type at
  1019 and 4099).
- c_hat = max over the Stage-B primes of k*/log2 p. k_C = ceil(3 c_hat log2 p),
  evaluated in mpmath at 50 digits from k* and p.
- Arm tests (KS-1, START-2) and SEED-1 use the prime's admissible u (the
  N = 10^5 table).
- H-WESO-9dc201: only a descriptive histogram of ln delta / ln X_max is
  reported. No law is evaluated.

## 7. Checker (IV-4) (`checker.py`)

The checker runs in a fresh process. It recomputes, from the per-sample and
per-null FACTORISATIONS (not from the stored ell_max), every smooth count,
f_emp, the TC-2 counts, the TC-1 minimum, the SEED-2 counts, the TC-3 counts,
delta_max and the NULL-1 bit-length matching. It compares these with
raw-result.json, and it re-verifies every factorisation with sympy (the product
equals the integer; `sympy.isprime` on each factor), independently of PARI.

## 8. Files (the analysis_freeze recorded in RUN-WESO-f37773)

| file | sha256 |
| --- | --- |
| analysis.py | 16746efabe4f2a46e85f2f83caa3cc6dc5ac2cad496eb9f5548c43de0d22f402 |
| checker.py | a41949c8f9fdf619ab370e16160749a030f3d9c0053ba9db79fb02708f9195f5 |
| common.py | 8ee88432beb11186b407be7ac9ede48a16547f0d917bb0f0bfb09d66cdb37742 |
| complete_manifest.py | 2561203170c999b5fde7d74e9e4f76101306c81c8868ce6f96798f889cc96f92 |
| report.py | 94a6a8c3be7311b7a186b91b09e7dfae646d6dcd90f3c5e59aecb189eceba063 |
| rho.py | 302eca98fdc5f78ec71e94e777f084abb4859a81643ce357a57dc8a096d503ee |
| run_stage.py | ad59a8d40cafaab419a461e4bf6ee0a7bdf693f9914d17433702e76b3430aa0b |
| sampling.py | e2cbb6ed458ea714152cff8751ff61abd6b5c3534f7f32963b34476039b3d040 |
| stage_a.py | 452aa421a5a96cf3036ac6ea7d237562744bdadac26afefc2c180b1233d6d60f |
| stage_b.py | 8b68d15914a9b60b9fa0435e7f62b99b6ab4c407e914a1d5b7b6b97e5776efc5 |
| stage_c.py | 91a49b01677d8f1289ef4e52824b585b22a7b2ab8d15a60651d579ac9eb726db |
| stage_d.py | 0f8c4f44ec2b9978b1730b99b7d214eff9de826e7c3f1d292cdc28983f6a13fd |
| stats.py | a4627f0e7aacd3f439695f52f2e19bad4ab5379005d20d387bdcd8a7c40f1b82 |
| weso.gp | e8f608109ee1ffe3a7745695baab2b056807e474d850fdda875973e9358b8ef6 |

No implementation file changed after the freeze (Stages C and D check this in
`analysis_freeze_check`). The unit checks U-0..U-2, CLS-1, V-RHO-1..3 and DET-1
live inside the stage drivers (stage_b.py, stage_c.py, rho.py), not in
separate test files.

## 9. Exact commands (cwd = repository root; each run's `command.txt` holds the exact argv)

```
PYTHONDONTWRITEBYTECODE=1 python3 -B experiments/EXP-WESO-9e2d6d/implementation/run_stage.py --run-id RUN-WESO-aa2237 --stage A --watchdog 3600 -- experiments/EXP-WESO-9e2d6d/implementation/stage_a.py --cache-dir <scratchpad>/wisde_A
PYTHONDONTWRITEBYTECODE=1 python3 -B experiments/EXP-WESO-9e2d6d/implementation/run_stage.py --run-id RUN-WESO-f37773 --stage B --watchdog 43200 -- experiments/EXP-WESO-9e2d6d/implementation/stage_b.py --workers 1
PYTHONDONTWRITEBYTECODE=1 python3 -B experiments/EXP-WESO-9e2d6d/implementation/run_stage.py --run-id RUN-WESO-e65afd --stage C --watchdog 259200 -- experiments/EXP-WESO-9e2d6d/implementation/stage_c.py --max-workers 3
# Stage D (NOT RUN; SR-4 STOP, see D-11): would be
# PYTHONDONTWRITEBYTECODE=1 python3 -B experiments/EXP-WESO-9e2d6d/implementation/run_stage.py --run-id RUN-WESO-0b4b33 --stage D --watchdog 259200 -- experiments/EXP-WESO-9e2d6d/implementation/stage_d.py --max-workers 3
PYTHONDONTWRITEBYTECODE=1 python3 -B experiments/EXP-WESO-9e2d6d/implementation/complete_manifest.py --run-dir experiments/EXP-WESO-9e2d6d/runs/<RUN-ID>   # after each run
```

`<scratchpad>` = `/tmp/claude-0/-home-user/5af2d3d8-0ba3-5d96-b05f-205cb058efcf/scratchpad`.

## 10. Scratch files outside the repository (not committed)

- `<scratchpad>/wisde_A/results{1019,4099,10007,20011}.sage`: the WISDE bytes
  used by RUN-WESO-aa2237. Their hashes equal the committed values.
- `<scratchpad>/wisde/`: first ad-hoc fetch, to inspect the format; hashes
  equal. `<scratchpad>/wisde_dry/`: the fetch from the Stage-A development
  dry-run.
- `<scratchpad>/oversize/RUN-WESO-f37773/samples.jsonl.gz`: 85122367 bytes,
  sha256 `365dc151...5c83`. It is above the spec's 50 MiB size_note, so it is
  listed in that run's manifest (`artifacts_outside_repository`). The Stage-B
  command regenerates every record field exactly EXCEPT `wall_s`, because
  records are a pure function of the seeds and the frozen code. The gzip bytes
  are therefore not byte-identical on regeneration. The committed manifest
  overstated this, and the correction is in
  `runs/RUN-WESO-f37773/manifest-addendum-20260926.yaml`.
- `<scratchpad>/dryA`, `dryB`, `devB`, `dryC`, `dryD`, `mtest`, `recon`,
  `t1.gp`, `t2.gp`, `dev_stage_d.py`: development artifacts (Section 11).

## 11. Development work before the official runs (disclosed)

- Stage A: one full dry-run of stage_a.py into the scratchpad. It is
  deterministic and gave the same gate results as the official run.
- Stage B: one smoke test at 1/50 scale (`--dev-scale 50`: N_B = 200, 20
  replicates) into the scratchpad. It exercised the code path only; its
  numbers are meaningless at that N and were not used.
- Stage C/D: smoke tests on NON-FROZEN development primes only (60 and 90 bits
  for C at 1/50 scale; nextprime(2^200) with p = 3 mod 4 for D, with dummy seeds
  and N = 400). The Stage-C smoke test read a fabricated Stage-B input in
  `<scratchpad>/devB`, whose gate_G_B verdict and k* were forced so that the
  code path could run. That file is development scaffolding and is not
  evidence. No draw, factorisation or smoothness statistic was computed at
  p_64, p_96, p_128 or p_D before each prime's official sampling.
- Timing probes (sampler only, no statistics) at primes near 2^127 and 2^253,
  which are not the frozen primes.
- The `--dev-*` flags exist in stage_b.py and stage_c.py. They are not used in
  any official command.

## 12. Deviations and execution defects (all also recorded in the manifests and execution reports)

- D-1 (EX-10): The first WISDE fetch was an ad-hoc `curl` loop outside
  `implementation/`, run to inspect the file format. The official fetch,
  logged in `wisde_fetch_log.yaml`, is performed by stage_a.py.
- D-2: weso.gp and common.py changed after Stage A (see Section 2). The Stage-A
  code is preserved and hash-verified in `runs/RUN-WESO-aa2237/code_snapshot/`.
  I-1 was re-applied with the final code: 0 mismatches. The notes on this are
  in `runs/RUN-WESO-aa2237/manifest-addendum-20260926.yaml`. They were first
  appended to the manifest, but that manifest had already been archived
  (9018045ab), so it was restored to its committed bytes.
- D-3: `complete_manifest.py` was added during Stage B, at the Coordinator's
  request (validator schema) and before the freeze was recorded. As a result,
  the Stage-B manifest correctly shows `implementation_unchanged_during_run:
  false`. After each run, manifest.yaml is completed with run.result
  (certificate.kind none), code.commit and code.command. The wrapper's original
  is kept as `manifest_wrapper_original.yaml`. No measured value was changed.
- D-4: Stage-B samples.jsonl.gz is over 50 MiB and was moved to the scratchpad
  per the spec's size_note, with its sha256 and size recorded in the manifest.
  The Stage-B execution_report's artifact list still names it inside the run
  directory, and the manifest block supersedes that entry.
- D-5 (workers): Stage B ran on 1 worker (EX-6: only 1 worker before DET-1).
  DET-1 compared 1 worker with 3, not 4, because of the host sharing and
  the session cap. Stages C and D ran on 3 workers.
- D-6: In Stages C and D the per-sample and per-null records are split per
  prime (`samples.<label>.jsonl.gz`, `nulls.<label>.jsonl.gz`, plus
  `det1.jsonl.gz`) instead of single files. This checkpoints each prime and
  keeps every file under 50 MiB.
- D-7 (code only; Stage D was not run): FG-D needs a projected null cost. It is measured by factoring 1000
  PILOT-NULL1 and 1000 PILOT-NULL2 integers (seed D-PILOT), which are archived
  in `fg_d_pilot.jsonl.gz` and excluded from every statistic.
- D-8 (IMPLEMENTATION DEFECT, criteria layer, found during Stage C): B(u) is
  computed in double precision. At p_64 = 2^64 + 51 and u = 3, the exact
  value is B = ((p/2))^(1/9) = 128.0000000000000000393..., which is >= 128,
  but the code computed 127.99999999999997. The recorded admissible table
  therefore wrongly EXCLUDES the cell (p_64, u = 3), which the spec rule makes
  admissible.
  - Unaffected: smooth counts (no integer lies between the two values), all
    per-sample data, and every other cell and prime. The latter was checked:
    no other grid point has B within float error of 128.
  - Affected: the criteria evaluation at p_64, and the u = 3 member of the
    SEED-1, KS-1 and START-2 test families at p_64, which changes those
    families' Bonferroni size as well.
  - Handling: per the Coordinator's instruction, the frozen code was not
    changed. The execution report gives (1) the frozen code's mechanical
    outcome and (2) the reading with u = 3 admitted, derived from the
    recorded cell values, and names the quantities that need recomputation
    from the samples.
- D-9 (SR-4 ordering): `analysis.analyze_prime` computes every metric for a
  prime in one pass, including the per-prime `criteria_inputs` and the
  success/FC-H1 booleans, and applies the instrument gates afterwards. When
  SR-4 fires, those fields exist in raw-result.json but are NOT an evaluated
  criterion. Only the outcome code (FC-VOID) is the stage verdict.
- D-10 (measurement): in RUN-WESO-e65afd, manifest
  `timing.cpu_seconds_children_*` undercounts CPU. gp processes inside pool
  workers are not reaped by wait(). Wall time, peak RSS and per-sample
  `wall_s` are valid.
- D-11 (stage not run): Stage C's outcome is FC-VOID, because the NULL-2 bound
  failed at p96, u = 4.5 (ratio 2.452). The spec is internally inconsistent
  here: STAGE-D is `gated_by: gate_G_B and Stage C completed valid (any
  verdict)`, while SR-4 says "STOP", and EX-4 says "Gate failures stop as
  SR-1..SR-9 say". The Coordinator ruled that SR-4's STOP governs. Stage D was
  not run, RUN-WESO-0b4b33 is unused, and no directory was created (EX-7).
  This is a protocol stop and never evidence.
