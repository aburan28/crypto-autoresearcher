# Validation: EXP-ECDLP-8c41d7 (m = 4, block elimination order), RUN-ECDLP-8c41d7-01 .. -04

Validator: independent of the producer; no raw artifact, specification, amendment, ledger record or research status was
changed, nothing was committed. A passed validation makes the receipt admissible evidence for the exact scope below; it
does not change the status of H-ECDLP-60de36 and it is not an ECDLP claim, a speedup claim or a promotion.

- Snapshot read: branch `claude/p256-ecdlp-factor-base-wq59m1`, HEAD `9dba3eb2b8` (2026-10-19 18:35:24Z). All run records are
  at or before `bb3da2694e`; `analyze.py` is at `ea3b5e9634`/`9dba3eb2b8`; the producer run report is `9dba3eb2b8`.
  At my first `git status` two `analyze.py` files showed as modified; they were committed (`ea3b5e9634`, `9dba3eb2b8`)
  while I was reading, and I used only the committed versions (`git status` clean for this experiment afterwards; the
  working-tree-only state was never read as evidence). `git diff bb3da2694e HEAD -- runs amendments` is empty.
- Validation id: `VAL-20261019-0cb05d` (random token; no existing occurrence found by `git grep`; the archive task should
  re-check it with `tools/allocate_id.py`, which has no `validation` record type).
- Scripts and outputs are in `scripts/`, `outputs/`, `crash_repro/`, `rerun/` next to this file. Scripts were run from
  `/tmp/claude-0/validator4/` (some default paths point there). Re-runs used at most 2 cores (one single-threaded solver
  per core); the host was shared with the sibling validator, so every re-run timing is informational only.
- Scope of what the evidence covers: m = 4 (S_5), L = 2, 3, 4, p = 263 / 4111 / 65551 (Singular) / 262271 (msolve),
  msolve 0.6.5-1build2 (`-t 1`), Singular 4.3.2, 600 s per solve, 6 instances per cell of which 1 is a degenerate planted
  target at L = 3 and at L = 4 (n = 5 non-degenerate there). `claim_tier: toy`.

## Verdict

**passed** (the receipt is admissible for the stated scope), with the concerns below. Per-check results:

| # | check | result |
|---|---|---|
| 1 | freeze and amendment discipline; manifests | PASS (low-severity concerns listed) |
| 2 | msolve crash reproduction; no completed msolve result on a defective prime | PASS, with a CONCERN: the defective range is 17 and 18 bits, not "exactly 17 bits" |
| 3 | positive control, S_5 vanishing, elim_equals_B | PASS (L = 4 control coverage is partial; see below) |
| 4 | frozen criteria re-derived independently; analyze.py replay | PASS; CONCERN on sensitivity of the L = 4 retirement clause to the 600 s cap |
| 5 | mixed-prime L = 4 cell | CONCERN: valid within each solver family only |
| 6 | sample re-run | PASS |
| 7 | reproducibility records, degenerate targets | CONCERN (no memory record; rc -9 undiagnosed; smoke run not archived) |

Frozen criteria, recomputed by my own script (check 4): **success criterion not met** (A_elim_ms below B_ms in 0 of 2 jointly
completed cells; A_elim_ms completes L = 3, B_ms completes L = 4). **Falsification criterion met** for the msolve pair
(clause 1: A at or above B in 2/2 jointly completed cells; clause 2: A_elim_ms retired at L = 4, B_ms not retired in the
grid) and for the Singular pair by clause 1 only (retirement is a tie at L = 4). This is a statement about this
instrument, scope and the 600 s cap, not a mathematical statement.

---

## 1. Freeze and amendment discipline: PASS

Evidence (`scripts/integrity.py`, `outputs/integrity.out`; git):

| run | started_at (Z) | authorising commit (committer time, Z) | gap | run's recorded git_head, dirty |
|---|---|---|---|---|
| 01 | 2026-10-16 01:07:14 | `6d6df97b6d` spec + trial-plan + shell (2026-10-15 23:42:03); launcher shim `290d25201f` 23:38:52 | 5111 s | `6d6df97b6d`, false |
| 02 | 2026-10-16 03:15:00 | `04a87943e2` AMD-01 + trial-plan-run02 (03:14:41) | 19 s | `04a87943e2`, false |
| 03 | 2026-10-19 16:58:51 | `d2d3f9ef29` AMD-02 + trial-plan-run03 (16:08:25) | 3026 s | `4ad12014e3` (descendant), false |
| 04 | 2026-10-19 17:41:54 | `7413b95b6a` AMD-03 + trial-plan-run04 + block_order_m4_p19.py (17:41:47) | 7 s | `7413b95b6a`, false |

- `specification.yaml`, `trial-plan.json` and `block_order_m4.py` each have exactly the freeze commits; `git diff
  6d6df97b6d..HEAD` is empty for them and for the three imported launchers (`block_order_grid.py`, `msolve_grid.py`,
  `pkm_isogeny_fb.py`, all last changed before the freeze). Every run therefore executed byte-identical launcher code
  (AMD-01/02 say "identical launcher commit"; the HEAD hash differs for RUN-03 but the launcher files do not).
- Amendments change only what they state. Diff of each `trial-plan-run0N.json` against the frozen plan: RUN-02 L list
  [2,3,4] to [3,4]; RUN-03 L list to [4]; RUN-04 L list to [4], arms to the three msolve arms, and the command (script
  `block_order_m4_p19.py`, plan path, output path). `block_order_m4_p19.py` overrides `pkm.find_prime` for (m, L) = (4, 4)
  only (prime 262271) and otherwise calls the frozen function. Specification untouched, so thresholds, criteria and
  stopping rule are as frozen. Each `command.txt` equals the `command` field of its plan (4/4).
- Manifests: all 4 `manifest.json` sha256 lists recomputed with `sha256sum`: 7, 7, 7 and 8 files, all match, no file in a run
  directory is outside its manifest. Every run-artifact and amendment file has exactly one commit (the single exception
  is below). `stdout.log` lines equal `raw-result.jsonl` rows (status, wall_s, planted flag, elim flag; 0 mismatches);
  `finished_at - started_at` = 2404 s / 3032 s vs the launcher's `elapsed_s` 2403.2 / 3031.4.
- Seeds and primes: every row's seed equals `int(sha256("EXP-ECDLP-f49f75/v1|4|L|inst")[:12], 16)`; p is the frozen-rule
  prime (263, 4111, 65551) except RUN-04 (262271, prime, p+1 = 2^7 * 2049, the (3, 6) prime of 20a588/502ae2). 0 violations.
- Non-overlap of runs on the 4 cores: 20a588-01 finished 01:07:12Z, 8c41d7-01 started 01:07:14Z; 20a588-03 finished
  16:58:51Z = 8c41d7-03 started. RUN-04 shared the host for about 6 s with the regression tests (operational-notes.txt).

Concerns (none changes a recorded number):
1. AMD-03 was filed after RUN-03's data. The exclusion of RUN-03's msolve rows is an instrument-failure exclusion that I
   reproduced independently (check 2), the rows are retained, and the amendment is committed before RUN-04's data; but
   the choice to re-run the msolve arms only (not the Singular arms, which had timed out) was made after seeing RUN-03.
2. `amendments/run_after_restart_2.sh` was edited in place after its commit (`1b1f8c2d02`: one line, 20a588 RUN-02 to RUN-03)
   and an identical `run_after_restart_3.sh` added in the same commit; both predate RUN-03's start. The scripts are not in
   the manifests, so which one ran is not recorded. Record hygiene only.
3. The smoke run ("smoke-m4", m = 4, L = 3) that "sized the grid" and informed `expected_scale` and the pre-registered
   ordinal prediction is not archived. The spec says no criterion uses it; it cannot be checked.
4. `analyze.py` (the operationalisation of the criteria) is not a frozen artifact and was revised after data (first
   version `0b0ef6490f` 2026-10-16 03:29Z, merge rule `ea3b5e9634` 18:34Z, after RUN-04 finished 18:32Z). Its retirement test
   (`n_ok == 0 and n_timeout > 0`) differs from the frozen text ("every instance timed out") in the A_drl_ms L = 4 cell
   (see check 4). No pair criterion is affected; my independent derivation agrees.
5. RUN-04 started 7 s after its authorising commit; the order is bound by the recorded git_head, not by the gap.

## 2. msolve 17-bit crash: reproduced; PASS, with a range CONCERN

Standalone reproduction (`scripts/capture_systems.py`, `scripts/probe_msolve.py`, `scripts/run_crash_repro.sh`;
`crash_repro/`):

- RUN-03 L = 4 instance 0 rebuilt with the committed `block_order_m4.py` (seed 9026085432205, p = 65551, b = 37812: equal to
  the raw row). The three msolve systems (B_ms dense: S_5 + four dense degree-16 polynomials, 5 polynomials; A_drl_ms and
  A_elim_ms chain systems, 17 polynomials; hashes in `crash_repro/run03_L4_i0_p65551/SHA256SUMS`) all end in rc = -11
  (SIGSEGV): B_ms 0.021 s, A_drl_ms 0.773 s, A_elim_ms 0.015 s, against the recorded 0.0233 s, 1.0706 s, 0.0152 s.
- The same construction at p = 262271 (RUN-04 instance 0, b = 151247, equal to the raw row): B_ms and A_drl_ms were run for
  90 s and neither crashed (both timed out at 90 s with about 0.9 GB resident).
- Bit-length scan of the dense m = 4 system (L = 2; 72 primes; `crash_repro/scan_L2_i0.jsonl`, `scan2_L2_i0.jsonl`): crash
  for every prime tested with 2^16 < p < 2^18 (65539 .. 256499, 17 and 18 bits); solves for 65003, 65519 (16 bits) and for
  every prime from 262147 up (19 to 22 bits).
- A two-variable system (`x^2+y^2-1, x*y-2`) shows the same boundaries (crash at 65539 .. 262139, fine at 65519 and
  262147): `crash_repro/repro_tiny.out`. The defect does not depend on the system.

CONCERN (documentation, no result depends on it): AMD-03 and CORR-20261019-e6f65b say "exactly 17 bits (2^16 < p < 2^17)".
I find the crashing range to be 2^16 < p < 2^18, i.e. 17 AND 18 bits (131111, 136951, ..., 256499 and 262139 crash; none was
tested in AMD-03). The correction's advice that m = 2 can run "with a prime outside 2^16..2^17" would still hit 18-bit
primes, and the canary test `tools/test_pkm_isogeny_launchers.py::MsolvePrimeCrashCanary` (passes, 12/12 tests in 5.5 s,
`outputs/unittest_*.out`) only pins 70039 as the crash and 60103, 300007 as clean, so it does not cover 18 bits. The chosen
p = 262271 is 127 above 2^18 and is clean (tested here and by B_ms completing in RUN-04), so AMD-03's remedy is sound.

No completed msolve result used a defective prime (`scripts/p_bits_audit.py`, `outputs/p_bits_audit.out`; all
`raw-result.jsonl` of 502ae2, 20a588, 8c41d7, f49f75): msolve rows exist at 9, 10, 13, 16, 19 and 22 bits only, plus RUN-03's
15 rc-11 rows at 17 bits (and their 3 degenerate-target rows). There is no msolve row at 18 bits. msolve results with
status ok at 17 or 18 bits: 0. (The 17-bit completions in f49f75 are Singular-only.)

## 3. Controls: PASS

- Positive control from the raw rows (`scripts/controls_from_raw.py`): every `ok` result of a planted instance has
  `planted_in_variety` true; 0 violations. Coverage: L = 2 four planted x five arms; L = 3 three planted x five arms; L = 4
  only B_ms (3 planted, 583.0 / 586.3 / 583.2 s). At L = 4 no chain arm and no Singular arm completed, so those cells have
  no positive control (nothing completed to check).
- S_5 vanishes on planted decompositions, own computation (`scripts/s5_check.py`, `outputs/s5/`): instances regenerated with
  the committed code and checked with my own code (affine EC arithmetic; Semaev S_3 from the textbook formula; S_5 =
  Res_X(S_3(x1,x2,X), Res_Y(S_3(X,x3,Y), S_3(x4,xT,Y))) by my own Sylvester-determinant mod p, not Singular, not sympy; plus a
  resultant-free sign-enumeration oracle). 13/13 non-degenerate planted instances (L=2: 4; L=3: 3; L=4 at p=65551: 3; at
  p=262271: 3): picks on the curve, x in V, chain(x) = c, sum = T; S_5(planted) = 0; oracle true. Negative control: S_5 at 6
  perturbed points per instance (78) is never zero. The producer's expanded S_5 string (what the solvers consumed) equals my
  numerical S_5 exactly at 6 random points per instance (78/78) and vanishes at the planted point (13/13). The 3 degenerate
  targets (L=3 inst 2; L=4 inst 1 at both primes) have sum of picks = point at infinity, so the `degenerate_target`
  label is correct. The repository test `test_planted_decompositions_vanish_for_m2_m3_m4` passes.
- elim_equals_B (equivalence control): recorded true on 6/6 instances at L = 2 and 5/5 at L = 3; at L = 4 there is no
  instance on which both msolve bases finished (A_elim_ms timed out on all 5), so the control is not evaluable there and
  the invalidation rule is not triggered. Indirect support for A_elim_ms at p = 262271: 20a588 (m = 3, L = 6, same prime)
  has elim_equals_B true on 6/6. My re-runs (check 6) also gave true.
- Random-target instances yield the trivial basis [1] (gb_size = 1, vdim 0) at every L and every arm that finished (L=2, 3;
  B_ms at L=4): they are no-solution instances; the planted instances carry B_ms bases of 12-14 elements at L=2, 5-15 at L=3, 15 at L=4. See check 4.

## 4. Frozen criteria re-derived; analyze.py replay: PASS; CONCERN on cap sensitivity

My script `scripts/derive_criteria.py` (written and run before opening `analyze.py`; `outputs/derive_criteria.out`) uses the
source map L=2 from RUN-01, L=3 from RUN-02, L=4 Singular arms from RUN-03 (p=65551), L=4 msolve arms from RUN-04 (p=262271),
and was cross-checked against the "later run wins" rule per (L, arm, instance): 0 mismatches. Definitions from the frozen
text: median over completed instances; jointly completed cell = both arms have a completed instance; retired = every
non-degenerate instance of the cell timed out (variants with lenient/strict definitions give identical pair verdicts).

| | L=2 | L=3 | L=4 |
|---|---|---|---|
| A_elim_ms median (ok/n) | 24.95 ms (6/6) | 12.929 s (5/5) | none: 5 timeouts, 600.09 .. 600.13 s |
| B_ms median (ok/n) | 22.00 ms (6/6) | 10.7005 s (5/5) | 582.996 s (5/5; 518.230 .. 586.271) |
| A_elim/B_ms | 1.134 | 1.208 | >= 1.02 .. 1.16 per instance (censored) |
| A_drl_ms median | 40.05 ms | 61.42 s | none: 4 timeouts + 1 rc -9 at 183.5 s |
| A_block_sg median | 113.05 ms | 344.62 s | none: 5 timeouts (p = 65551) |
| B_sg median | 48.9 ms | 70.36 s | none: 5 timeouts (p = 65551) |
| A_block_sg/B_sg | 2.312 | 4.898 | not resolved (all censored) |

- Success criterion: not met. msolve pair: A_elim_ms below B_ms in 0/2 jointly completed cells (L=2, 3), largest completed L
  3 vs 4. Singular pair: 0/2, largest completed L 3 vs 3.
- Falsification criterion: met. msolve: clause 1 yes (A >= B in 2/2 cells), clause 2 yes (A_elim_ms retired at L=4, B_ms not
  retired within L <= 4). Singular: clause 1 yes (2/2), clause 2 no (A_block_sg and B_sg both retired at L=4; tie).
- Pre-registered ordinal prediction: A_elim_ms >= B_ms in every jointly completed cell: holds; A_drl_ms several times slower
  than A_elim_ms: 4.8x at L=3 (1.6x at L=2); A_block_sg >= B_sg and retired no later: holds (tie at L=4).
- Dynamic-range control (median A_drl/A_elim at the largest L where both complete, L=3): median of 5 per-instance ratios
  4.80 (4.55 .. 4.94); ratio of medians 4.75; >= 2, pass. The instrument resolves the order effect.
- Per-instance paired A_elim/B_ms: L=3 all five ratios above 1 (1.12 .. 1.27); L=2 five of six above 1 (instance 3 is 0.89).
- Replay of the producer's `analyze.py` (`outputs/analyze-replay/`): `summary.json` byte-identical to the committed
  `reports/run-20261016T0107Z/summary.json` (same sha256); criteria values identical to mine (ratios 1.13/1.21 and 2.31/4.90;
  largest L 3 vs 4 and 3 vs 3; retired 4 vs none and 4 vs 4; dynamic range 4.75 ratio-of-medians, 4.797 paired median).
- Robustness (`scripts/derive_variants.py`, `outputs/derive_variants.out`; added after the replay): planted-only reading
  (random targets are no-solution instances) gives identical verdicts; planted-only dynamic range 4.80.

Sensitivity of the L=4 retirement comparison to the 600 s cap. B_ms completes at L=4 at 582.996 / 586.271 / 583.2 s (planted)
and 518.230 / 528.342 s (random, no-solution); A_elim_ms exceeds 600.09 s on all five. Under a what-if cap (completed rows
relabelled timeout when wall_s exceeds the cap; informational):
- clause 2 of falsification flips to "tie" (B_ms also retired at L=4) when the cap drops below 518.2 s on the pooled
  instances, or below 583.0 s on the planted-only reading; the margin of the fastest completion under the 600 s cap is 13.6%
  pooled and 2.8% planted-only (2.3% for the slowest planted instance). A_elim_ms is only bounded from below at L=4 (ratio
  to B_ms >= 1.02 .. 1.16 per instance, median 1.03), so its true L=4 time is unresolved: a cap above 600 s could also
  remove its retirement. Informational extrapolation, not evidence: A_elim_ms needs a growth of at most 46x from L=3 to
  complete in 600 s and B_ms grew 54x; with the L=3 ratio 1.2, A_elim_ms would sit near 700 s, just past the cap.
- Falsification clause 1 and the non-success of the success criterion do not depend on the cap while L=2 and L=3 still complete
  (every L=3 msolve solve is at most 13.4 s, every L=3 Singular solve at most 349.9 s, so any cap of at least 14 s resp.
  350 s leaves both cells unchanged). The falsification verdict is therefore robust, but
  its second clause and the "B_ms completes a larger L than A_elim_ms" statement are knife-edge statements about the cap.
  L=2 is a 3 ms difference at process-start scale (paired CI of the producer's supplementary bootstrap includes 1);
  my re-run reproduces A > B in 6/6 pairs there.
- A timeout is not negative mathematical evidence: only the capped, measured comparisons at L=2 and L=3 are uncensored.

Operationalisation differences found (no effect on the pair criteria): (a) A_drl_ms at L=4 is 4 timeouts + 1 kill (rc -9);
under the frozen text ("every instance timed out") it is not retired; `analyze.py` (`criteria.json` `retired_at`) and the
figure's x marks ("x = all timed out") count it as retired. The run report's text states the rc -9 correctly. (b) The figure titles the cells "n = 6" while L = 3 and L = 4 have
n = 5 non-degenerate instances. (c) The merge in `analyze.py` copies row-level fields (`p`, `b`, `elim_equals_B`) from the
earliest run's row only; per-arm `p_bits` are correct, and no later run had an `elim_equals_B`, so nothing is lost here.

## 5. Mixed-prime L = 4 cell: CONCERN (valid within each solver family only)

- RUN-03 (Singular arms) and RUN-04 (msolve arms) have identical per-instance seeds but different primes, so b, the chain,
  the factor base and the targets differ (checked: b = 37812 vs 151247 etc.). The Singular arms and the msolve arms do not
  share instances at L = 4. Within a family the arms share instances: A_elim_ms, A_drl_ms, B_ms on RUN-04's five non-degenerate
  instances at p = 262271; A_block_sg and B_sg on RUN-03's five at p = 65551.
- Report-able at L=4: (i) msolve pair on shared instances (B_ms completes in 518 .. 586 s; A_elim_ms >= 600 s); (ii) Singular
  pair on shared instances (both >= 600 s on all five, a tie that carries no ordering information).
- Not report-able: any L=4 contrast between solver families (e.g. "msolve completes the dense system, Singular does not"):
  it confounds solver, prime (65551 vs 262271, 4 times apart) and instances. At L=3 on identical instances B_sg/B_ms is
  6.6x, and the 54x L=3 to L=4 growth of B_ms alone puts B_sg near 3800 s, so the Singular timeouts are expected anyway.
- Could the p change bias the msolve A/B comparison? Probe (`scripts/prime_ratio_L3.py`, `rerun/prime_ratio_L3.jsonl`; same shape
  m=4, L=3, one planted instance per prime, committed code with only the prime patched): A_elim_ms / B_ms = 10.95/10.18 s
  (13 bits), 11.35/10.17 (16 bits), 12.03/10.92 (19 bits), 11.99/10.55 (22 bits); ratio 1.08, 1.12, 1.10, 1.14; elim_equals_B
  true on all. Prime size changes neither cost nor ratio by more than about 7% at this shape (single instance per prime,
  informational). The 2-adic valuation of p+1 (2^7 at 262271 vs 2^4 at 65551) was not probed.
- The frozen rule keeps p near 2^(mL); 262271 is 4x that scale. Random targets already give the trivial basis [1] at every
  L under the frozen primes, so the prime change does not alter the kind of instance. Planted B_ms bases have 15 elements.
- The producer's table labels the primes per row; the figure puts both primes in one L=4 column without saying so. Any
  summary that says "at L=4 ..." should name the solver family and prime.

## 6. Sample re-run: PASS

`scripts/rerun_one.py` and the committed launcher (`rerun/`; informational timings): m=4 L=2 instances 0-5, arms A_elim_ms,
B_ms, A_block_sg, B_sg (via `block_order_m4.py --workers 2`), and L=3 instance 0 (one process per core). Deterministic
fields (seed, kind, p, p_bits, b, status, planted_in_variety, f4_max_deg, gb_size, vdim, gb_maxdeg, elim_equals_B):
174 compared, 0 mismatches. Timings, re-run vs recorded: L=2 within 0.96 .. 1.07x (instance 0); L=3 instance 0: B_ms 10.11 vs 10.70
s, A_block_sg 349.06 vs 344.82 s, B_sg 68.88 vs 70.36 s; A_elim_ms 22.08 vs 13.04 s in the first re-run because I had pinned it
to a core shared with the sibling validator's job for its first ~20 s (my error, disclosed); clean repeats on a free core:
10.94 s, 11.85 s, 12.45 s (A_elim/B_ms in the same process 1.19 and 1.18). A > B holds in 6/6 L=2 pairs and for L=3
instance 0 in every repeat. Recorded timings were taken with 4 concurrent workers; a single-process rerun is up to ~15%
faster for A_elim_ms. The direction and the order of magnitude reproduce; I did not re-run L = 4.

## 7. Reproducibility records, degenerate targets: CONCERN

Present and consistent: command.txt, environment.json (python 3.13.16, platform, 4 cpus, msolve 0.6.5-1build2, Singular 4.3.2,
git_head, git_dirty), manifest.json with sha256 of every file, started_at / finished_at (RUN-03, -04), termination.txt for the two
interrupted runs (finished_at intentionally absent, matches), stderr.log empty (hash of the empty file), per-row seeds and
primes, per-arm status and timings, the 4-worker setting in the command, one solver process per worker (`-t 1`).

Missing or weak (limitations, not invalidating):
- No peak-memory or RSS record per solve although the budget names 12 GB; the A_drl_ms rc -9 (killed, 183.5 s, RUN-04 instance 4)
  has no recorded cause (no dmesg / OOM evidence). Informational probe (`crash_repro/run04_L4_i4_p262271/rss_A_drl_i4.out`):
  the same A_drl_ms system (L=4, instance 4, p=262271) run alone for 200 s holds 925 MB from 40 to 100 s, then grows to 3.3 GB by
  160 s and 3.4 GB at 200 s. Four such processes ran concurrently in RUN-04 (instances 0, 2, 3, 4 all in their A_drl_ms phase
  at the time), i.e. about 13 to 14 GB against the 12 GB budget on a 16 GB host: an out-of-memory kill is plausible but
  unproven. If so, the A_drl_ms L=4 outcome is an infrastructure event, not a timeout; it does not enter either pair criterion.
- The CPU model/RAM are in the run report, not in environment.json; sympy version (used by `isprime`) and the shell launch
  scripts' hashes are not recorded; which launch script ran RUN-03 is not recorded.
- The pre-freeze smoke run is not archived (check 1, concern 3). No receipt `reports/` review report exists yet (this validation
  is an input to it).
- The launcher's stopping rule tests `status == "timeout"` for every row, so a cell with a degenerate row never triggers it;
  L = 4 is the last cell, so nothing was skipped here, but the frozen stopping rule does not fire in such cells.
- No null-object control for the structure of V at m = 4: the random-set arm C of 502ae2 is not in this experiment's frozen contract.
  The relevant matched null here is the dense same-set arm B: the A_elim/B_ms ratio is 1.13 then 1.21 (and >= 1.03 at L = 4), the
  opposite of a growing advantage; the report states no expectation for how the ratio should move with L.

Degenerate targets: three planted instances (L=3 inst 2; L=4 inst 1 at p=65551 and at p=262271) have sum of the four picks equal to the
point at infinity (confirmed with my own arithmetic). They are recorded as `degenerate_target` for all arms, not silently dropped,
and reduce n to 5 at L = 3 and L = 4 (3 planted + 2 random); the frozen specification does not anticipate this and `analyze.py`
excludes them from medians and retirement.

Heuristic-validation and cost-model checks: not applicable (no Dickman/de Bruijn-type prediction, no cost table; wall time is not a
bound and no `ECBND` record is claimed). The pre-registered ordinal prediction is in the frozen spec before the first data and is
matched. Per `docs/inventor-protocol.md` section 6 this run is itself the scaled-down measured ratio against the baseline (step 2) and
the ratio is adverse (>= 1); no speedup is claimed, step 3 does not apply, step 4 (reproducibility) was exercised by rebuilding systems from
scratch (hashes in `crash_repro/`).

## Scope of any statement built on this receipt

Toy scale: m = 4, L = 2..4, p up to 19 bits, 5 or 6 instances per cell, msolve 0.6.5 and Singular 4.3.2 single-threaded, 600 s per solve,
one fixed variable order per arm. The measured, uncensored comparisons are L = 2 and L = 3. L = 4 gives only capped observations
(and mixes two primes across solver families). Nothing here transfers to m = 6, to P-256, to other solvers or other block orders.
