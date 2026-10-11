<!--
Placement note (dispatching session, not the re-deriver): the runtime refused
TASK-20260923-7a2cd4's own write of this file ("Subagents should return
findings as text, not write report files"). The text below is the report the
re-deriver returned in its hand-back, placed verbatim by the dispatching
session after the seal (seal.txt, 2026-09-23T20:57:16Z) and before
TASK-20260923-d04c5e. The gap is also recorded in attestation.yaml.
-->

# TASK-20260923-7a2cd4 — blind re-derivation, joint J6 (REVIEW-CERTBIN-20260923-c51f07)

- **Scope:** EXP-CERTBIN-4e92d7 spec v1, H-CERTBIN-a73f1c, RQ-CERTBIN-836ce2.
- **J6 verdict: holds.**
- **Sealed result:** `rederivation.json`, sha256 `c3332ec4583f7fba65f7ed54a2731966d49c7c078b38ad73173e23276a8f8bdb`, sealed in `seal.txt` at 2026-09-23T20:57:16Z. It has not been changed since, and there is no `-v2`.
- **Passes over the 105 inputs:** 1 of the 2 permitted.
- **Out of scope here:** no verdict on the experiment, the hypothesis or any run, and no comparison with anything I did not compute. Agreement with the run is decided by TASK-20260923-5f9b82.

## Method
Everything was built from the spec's `object` block. The code is in `code/`, and its sha256s are recorded in the pass. It uses Python 3.11.15, numpy 2.4.6, and mpmath only for one self-test cross-check.

- **Field:** F_{2^17} = F_2[t]/(t^17+t^3+1). Multiplication is implemented two independent ways: carry-less with reduction, and log/exp tables with base t. There are also trace, half-trace and square-root functions.
- **Curve:** the curve group law is written from the standard binary-curve formulas. #E follows the spec's trace rule.
- **Descended system:** S_3 is expanded literally over F_{2^17} as a product of multilinear polynomials in v_0..v_17. Equation k is the t^k coordinate.
- **Affine decomposition:** E^0 = E(0) and E^j = E(t^j) − E^0.
- **Rows:** μ is ordered by degree ascending, then sorted index tuple lexicographically. The row index is idx(μ)·17 + k, and zero rows are kept.
- **Columns:** descending degrevlex with the constant last. The order is built from a sort key and checked equal to the spec's literal comparator.
- **Solver:** the spec's column-major rule on bit-packed M_4.
- **Row pass:** a separate incremental echelon basis over Python big integers, which gives Z_4.
- **Traces:** hashed as canonical JSON with sha256. T_ops is streamed and checked byte-equal to `json.dumps`.
- **Replay:** the fixed-schedule replay runs the reference op log once over the 18 blocks M_4(E^0) and M_4(E^0..16) side by side.

**Routes to s:**
- **Route A:** root-finding in F_{2^17}. For each x_1 in V, solve a X^2 + b X + c = 0 with a = x_1^2+x_R^2, b = x_1x_R, c = x_1^2x_R^2+B, using the half-trace. It handles the degenerate a and b cases and uses no descended equations.
- **Route B:** evaluate the 17 descended equations at all 2^18 assignments.
- **Route C:** evaluate S_3 directly in the field on all of V×V, again with no descended equations.
- **B against C:** compared value by value on all 2^18 assignments, which pins the descended system exactly on every instance.

**Q7:** computed under three readings of the draw, all declared in code before any draw from S_curve. That is the only use of any specification seed.

## Commands run
Orientation and provenance, all read-only:
1. `git status`, and `git log --oneline -5`, which showed five commit subject lines.
2. `wc -l` of the process documents, and `ls` of `blind/`, which was absent.
3. `ls -d` existence checks, `git ls-files` and `git rev-parse HEAD`.
4. A ref-scan loop, which the harness refused and **did not run**.
5. `git ls-files --error-unmatch` on the card, the spec, KN-TECH and the input path; the input path is not tracked.
6. `git status --porcelain | wc -l`.
7. `git log --all --format=%H` and `--format='%H %cI' --name-status`, both restricted to the `blind/` path.
8. `git ls-remote --heads origin | wc -l`.
9. `git branch -a --contains becae035…`, `git merge-base --is-ancestor`, and `git ls-tree` on the permitted paths at both commits.
10. `git show becae035…:<input>` into the scratchpad, then `sha256sum`, `git hash-object`, `json.tool` and a `python3` structure summary.
11. Deletion of the scratchpad copy; the directory was otherwise empty. Environment probes.

Development, none of which read the input or drew from a spec seed:
12. `code/dev/dev_timing.py 2`, using dev seed 0xDE7A2C.
13. `selftests.py 12345 67891` on a synthetic curve.
14. Removal of `__pycache__` from my directory.
15. `rederive.py … --dev`, run five times. `--dev` uses synthetic instances, writes no file, and runs Q7 on the dev seed. One of these runs wrote stderr to `/tmp/claude-dev-err-7a2cd4.txt`; it was empty and deleted.
16. An inline `python3` edit that parametrizes the Q7 seed.

The pass:

17. `python3 -B coordination/review/certbin-20260923-c51f07/reviews/TASK-20260923-7a2cd4/code/rederive.py --repo /home/user/crypto-autoresearcher/.claude/worktrees/agent-a19a82595eec730a9 --input-commit becae035f695144b34d2a2608ec5c413db10e1b6 --out coordination/review/certbin-20260923-c51f07/reviews/TASK-20260923-7a2cd4 --pass-number 1 > …/logs/pass-1.log 2>&1`
    It exited 0 after 99.6 s wall time, with peak RSS about 402 MB.

After the seal, all read-only on my own files:
18. Seal and hash checks.
19. A heredoc summary, which the harness refused and **did not run**.
20. `t7a2cd4_review.py` in the scratchpad, used to review my own sealed file and then deleted. I never listed the scratchpad.
21. A log check, and a check that the code hashes recorded by the pass equal the files on disk. They do.

## Self-tests (BR-2)
All ran inside the pass on the **extracted** curve with this task's own seed 0x7A2CD4. **All passed.** The full records are in `rederivation.json.self_tests`.

- **Irreducibility:** gcd(t^{2^i}−t, f) = 1 for i = 1..8 and t^{2^17} ≡ t, which is a complete Rabin test because 17 is prime. A second route, trial division by all degree 1..8 polynomials, found no factor.
- **S_3 on the extracted curve:** 999 random point pairs, testing both P_1+P_2 and P_1−P_2, plus 200 doublings.
  - The group law was validated separately first: [#E]P = O on 200 points, closure on 1000 pairs, associativity on 200 triples, and the Hasse bound.
  - Negative control: a random third abscissa over 1000 samples.
  - This verifies the KN-TECH-b18366 formula against point addition.
- **Descended equations against direct F_{2^17} S_3:** 1000 random (v, x_R) with 0 mismatches. Also an exhaustive all-2^18 comparison on 4 x_R values, including x_R = 0 and x_R in V.
- **M_4 rows against a naive multiply:** 60 rows, using exponent-vector multiplication and the literal degrevlex comparator. 0 mismatches.
- **Fixture dimensions from my own construction:** 2924 × 4048 at D = 4 and 323 × 988 at D = 3, equal to C-FIX.
- **Supporting tests:**
  - field axioms and table-versus-carry-less multiplication on 10^4 samples;
  - column and row orders;
  - the packed solver against a naive implementation of the spec rule on 30 random matrices (op logs, the streamed T_ops hash against `json.dumps`, row-pass Z against naive prefix rank, and C-PASS);
  - route A against route C per x_1, including the degenerate branches;
  - Clopper–Pearson against mpmath Beta quantiles.

## Consistency checks on every one of the 105 instances (all held)
- Routes A, B and C agree, so there is no BR-3 disagreement anywhere.
- The descended values equal direct S_3 on all 2^18 assignments.
- E(r) = E^0 + Σ r_j E^j exactly.
- M_4 is linear in E.
- The pivot-column set equals the row-pass leading-column set, and |Z| = R − rank (C-PASS).
- Z equals the complement of the pivot rows.
- No nonzero unused row remains after the solver.
- No nesting violation and no hash/content disagreement.
- For each reference, the Q6 affine form at its own r is 1 at every step, direct self-replay gives all ones, and direct replay on 20 targets per reference matches the affine formula at every step.

## Ambiguities (BR-1)
There are nine, registered before the pass in `code/ambiguities.py` and embedded in `rederivation.json`. No clause was unreadable, and none was settled by looking at producer artifacts.

- **AMB-1:** the bit order of a_k. I chose bit j = r_j. This changes only Q6's integer labels; K_exact, K_rank and the rank flags are invariant.
- **AMB-2:** "leading column" means the smallest column index. Only this reading makes C-PASS a theorem, and Z_D is unaffected.
- **AMB-3:** zero rows belong to Z_D, as the definition of span forces. Whether this matters is visible in the per-instance field `zero_rows_in_M4`.
- **AMB-4:** the numpy call pattern for drawing (A, B). Three readings were pre-declared, and it affects only the optional Q7.
- **AMB-5:** M_D(E^j) is read as the construction applied to the rows of E^j. This is forced by linearity and checked on every instance.
- **AMB-6:** the internal column order of E(r) is not needed.
- **AMB-7:** T_ops flags use the hash, with content confirmed when hashes are equal.
- **AMB-8:** Clopper–Pearson is two-sided with equal tails, over this task's own classification.
- **AMB-9:** D = 4 only.

## Coverage
- Q1 and Q2 are present for all 105 instances.
- Q3 has hashes for all 105 and match flags for all 100×5 target–reference pairs and the 5×5 reference pairs, with full reference T_strict and T_set content.
- Q4 is present for the 5 references. Q5 and Q6 are present for every reference I classify unsatisfiable. Q7 is done.
- `gaps` is empty, and the route-disagreement list is empty.
- No file outside the write scope was touched, and no git write was made. The `git status` entries are all inside my directory.

## J6 verdict: holds
Every quantity Q1–Q6, plus the optional Q7, was computed from the spec text and the extracted inputs alone. All BR-2 self-tests passed, and every point with more than one reading is recorded. The alternative readings could change only Q6's integer labels (AMB-1) and the optional Q7 (AMB-4). No load-bearing clause is self-contradictory. Every identity the spec asserts that I could test held exactly on all instances: C-FIX, C-AFF, C-PASS, the nesting chain, and the saving_set identity.

## Limitations
- Independence is from the producer's code, not from the spec text. A defect that both the spec and the implementations faithfully contain would not show up as a disagreement.
- The model is the same as the executor's (D-2).
- The result covers one curve, D = 4, and the given 100-target subsample only.
- The preconditions in D-1 are unverified by me.

## Dispatch deviations reported by the re-deriver
- **D-1:** the worktree was at HEAD `9657b985e98ab9fbcb60383a526177e3fd5abdd6` (main), which did not contain `blind/blind-inputs.json`. The input was read by exact path from pushed commit `becae035f695144b34d2a2608ec5c413db10e1b6` with `git show` (blob `16082c3aad9c82f8f15d457165d770c21306d673`, sha256 `71c50924b56b58e347587bbb3a0b1eba91940f4fa79275134a0fcd10cf1e9ce9`). The spec, KN-TECH-b18366, the card, AGENTS.md, agents/validator.md and the template have identical blob ids at both commits. The re-deriver could not itself verify the receipt sha256, the --blind-history result or the lane claim.
- **D-2:** served by the session model (`fallback_used: true` under `fallback_allowed: true`); PD-R3's different-model-family preference was not met; not probe-verified.

```yaml
validation_report:
  id: null                      # not minted: this is a blind re-derivation (agents/validator.md), not a run validation
  task_id: TASK-20260923-7a2cd4
  run_ids: []                   # BR-6: zero trials; no RUN-id
  artifact_checks:
    - input read from pushed commit becae035f695144b34d2a2608ec5c413db10e1b6 (not an ancestor of worktree HEAD 9657b985); blob and sha256 recorded -- dispatch deviation D-1
    - spec/card/KN-TECH/process docs have the same git blob at HEAD and at the input commit
    - seal.txt sha256 == sha256(rederivation.json); code on disk == code hashes recorded in the pass
    - worktree clean outside write scope; no git write
  metric_recomputations:
    - Q1-Q6 (+ optional Q7) computed for every instance they cover; values only in rederivation.json
  control_checks:
    - all BR-2 self-tests passed on the extracted curve (seed 0x7A2CD4)
    - per-instance: routes A=B=C, all-2^18 value equality, C-AFF exact, M_4 linearity, C-PASS, Z = complement of pivot rows, nesting, Q6 replay self-consistency -- all held
  heuristic_validation_checks: []   # not applicable to J6 (derivability)
  cost_model_checks:
    - Q4 identity saving_set == C_4 R_4 / rank_4^2 checked as exact rationals (held for every reference)
  proof_architecture_checks: []
  verdict: passed               # SCOPE: this task's own re-derivation receipt only. J6: holds. Asserts nothing about RUN-CERTBIN-3b7e05, H-CERTBIN-a73f1c, or agreement with the run (TASK-20260923-5f9b82).
  limitations:
    - report.md not written by the task (runtime refusal); the text is in this handback for placement
    - D-1 dispatch preconditions unverifiable by me (receipt sha256, --blind-history, lane claim)
    - D-2 same model identifier as the executor; PD-R3 preference not met
    - independence is from producer code only; one curve, D = 4, 100-target subsample
  artifact_paths:
    - coordination/review/certbin-20260923-c51f07/reviews/TASK-20260923-7a2cd4/rederivation.json
    - coordination/review/certbin-20260923-c51f07/reviews/TASK-20260923-7a2cd4/seal.txt
    - coordination/review/certbin-20260923-c51f07/reviews/TASK-20260923-7a2cd4/attestation.yaml
    - coordination/review/certbin-20260923-c51f07/reviews/TASK-20260923-7a2cd4/code/
    - coordination/review/certbin-20260923-c51f07/reviews/TASK-20260923-7a2cd4/logs/pass-1.log
```

Attestation: `blind_from_respected: true`; `read_sibling_reports: false`. No outcome of EXP-CERTBIN-4e92d7 reached the re-deriver. The attestation discloses the non-outcome material it saw: the spec's coordinator_prior, the existence-only mentions in the card's must_not_read list, and five commit subject lines.
