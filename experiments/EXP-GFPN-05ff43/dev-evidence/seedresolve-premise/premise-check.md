# TASK-20260924-0652ce: premise and coverage check of the DRAFT AMD-EXP-GFPN-05ff43-20260924-seedresolve

**Scope.** This is a zero-run, zero-solve development check under the card `ledger/handoffs/TASK-20260924-0652ce.yaml`, ordered by DEC-20260923-d670c6. It computes the readings PR-5, PR-1, PR-2, PR-3 and PR-4 that the DRAFT pre-declares (`pre_approval_readings`). It runs on archived bytes, with the frozen EXP-GFPN-05ff43 v2 code imported read-only.

**Observations only.**
- It decides nothing and makes no approval recommendation.
- It is not evidence about D, any quotient, H-GFPN-9a29be or HEUR-GFPN-DFLAT.
- It makes no security statement: toy public parameters, known scalars only.
- The D values and degrees below are archived harness values, re-read from archived outputs (PC-6). They are not results:
  - toy inputs at p' = 1033 (stage-R1 toy G1 package RUN-GFPN-a61a10, inside the DV-7 bundle);
  - the 36 RUN-GFPN-ac4487 fixture inputs at p' = 4111.

**What ran.**
- No msolve, gp, sage, valgrind or other solver child; no run package.
- The check installs a process guard before any frozen import. It makes `subprocess.Popen`, `os.fork`/`exec*`/`spawn*`/`system`/`popen`, `v2_solver.run_child`, `_run_child_locked` and `callgrind_instructions` raise.
- The guard recorded **0 attempts** (`premise-check.json` `guard_attempts: []`, `msolve_children_launched: 0`).

## 0. Provenance of this check

| item | value |
|---|---|
| repository HEAD at run | `f76128105f714dc852b4289a411f64bc631bd239` (branch `claude/pollard-rho-speedup-hypotheses-yu8qwp`) |
| dirty state before run | clean (`git status --porcelain --untracked-files=all` empty) |
| dirty state after run | `pc_check.py` and `premise-check.json` untracked in this write_scope; `premise-check.md` was added afterwards; nothing else |
| command | `PYTHONDONTWRITEBYTECODE=1 python3 -B experiments/EXP-GFPN-05ff43/dev-evidence/seedresolve-premise/pc_check.py --repo /home/user/crypto-autoresearcher --scratch <scratchpad>/premise0652ce/run2 --out experiments/EXP-GFPN-05ff43/dev-evidence/seedresolve-premise/premise-check.json` (cwd = repository root) |
| pc_check.py sha256 (as run) | `17095ff7be5e3f05dfd5db27713c032ff6ce0f55461ea109ed0238d1deadf4cf` |
| run window (UTC, measured around the command) | 2026-09-24T00:27:12.052179Z to 2026-09-24T00:27:14.985301Z (about 2.9 s, including archive extraction) |
| exit code | 0 |
| Python | 3.11.15 (`/usr/local/bin/python3`); python-flint 0.9.0; numpy 2.4.6 |
| randomness | none. The check uses no random number generator. It reads archived bytes only. |
| scratch | `/tmp/claude-0/-home-user/1d07255b-9852-59b9-9a33-de55220a4332/scratchpad/premise0652ce/` (both archives extracted here only, with `tarfile` `filter="data"`) |
| frozen code | `implementation-v2/v2_solver.py`, `v2_arms.py` and `v2_driver.py` (with their transitive imports) were imported read-only. The sha256 of all 12 `implementation-v2/*.py` was taken before and after, and was unchanged (`frozen_v2_code_unchanged: true`). No `__pycache__` was created under `implementation-v2/` (`pycache_under_impl_v2: false`). |
| import side effects | Checked by reading the module-level statements of `v2_driver`, `v2_solver`, `v2_arms`, `v2_common`, `v2_lift`, `v2_scoring`, `v2_verify_independent`, `v2_child` and `v2_field` before importing. The only module-level actions are constant assignments, `flint.ctx.threads = 1`, `sys.path` insertion and `ctypes.CDLL(None)` (a libc handle, not a process). No import starts a computation or a child process. |
| inference | requested_policy `executor-implementation`. The resolved binding is not provided by the session: resolved_model_id `null` (none invented). fallback_used `false`, bedrock_used `false`. No network was used by the check. |

## 1. PR-5: integrity (applied first)

All **153** checks pass (0 failures), before any reading. The full hashes of every check are in Appendix A1 and in `premise-check.json` under `PR5_integrity`.

| check | expected (source) | actual |
|---|---|---|
| (a) `amendments/v2_addendum_seedresolve.yaml` | `dc714a446a22a99fd6762196d4e6ad1b8c9e7eb3920d64cf26036f95ecadee81` (TASK-20260923-df9fab receipt `addendum_sha256`) | equal |
| (b) `amendments/v2_addendum_solverevent.yaml` | `011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f` (card PC-2 (b); df9fab `decided_draft_sha256` carries the same value) | equal |
| (c) five characterization files | TASK-20260923-683f34 receipt `path_sha256` (A1 rows 3-7) | 5 of 5 equal |
| (d) `stageR1-dv7-evidence.tar.gz` | `70b83d61bfd05fcc92208c9f2bdba58fea0e7b587a927d54141bb72ccd35bd14` (TASK-20260923-53a47d receipt; CORR-20260923-9abefc) | equal |
| (e) every RUN-GFPN-ac4487 file read | TASK-20260923-0fa03f post-run receipt `path_sha256` | 145 of 145 equal: `raw-result.json` plus the 36 each of `solver/*.ms`, `*.ms.out`, `*.ms.log` and `*.ms.err` |
| no msolve child launched | - | 0 guard attempts |

Additional consistency checks, not required by PR-5:
- **Characterization logs match solves.jsonl.** All 9 characterization logs used (C-1a#247-#250 and C-2#95-#99) have `.ms.log` and `.ms.err` sha256 equal to `log_sha256` and `err_sha256` in `solves.jsonl`. Each record's `output_sha256` equals the output it is used for (`log_bytes_match_jsonl: true`, 9 of 9).
- **Archived logs match their packages.** For every log taken from a package, the frozen classification recomputed here equals the package's own recorded `outcome`, `D` and `substitution_failures` for that tag:
  - RUN-GFPN-ac4487: 36 tags;
  - toy world B: 36 tags;
  - toy world A: 36 tags, including the world-A event record `degenerate_parametrisation`, "eliminating polynomial degree 63 != quotient dimension 64 ...".

  Every such argv ends `-P 1` (gb_only false).

## 2. PR-1: substitution premise

### PR-1 (a): the .ms round trip, 72 inputs

`write_msolve_input(tmp, names, p, eqs)` was called on `(names, p, eqs) = v2_driver._parse_ms_file(f)`, and `tmp` was compared with `f` byte for byte.

- **Inputs, 72 in total:**
  - 36 toy inputs of the world-B toy G1 package: `stageR1/dv7/toy/world_B/exp/runs/RUN-GFPN-a61a10/solver/*.ms`, p' = 1033, including the event input `fx_reg0_torsion_S3_norm.ms`, sha256 `541b57b904e0c16956f9ea4615a32f1aaaae1cdfe7ca9c3b767f3b5f22d537c8`;
  - the 36 `RUN-GFPN-ac4487/solver/*.ms`, p' = 4111.
- **Adapter: none.** `_parse_ms_file` returns `(list[str], int, list[dict[tuple[int, ...], int]])`, which is exactly the representation `write_msolve_input` consumes. The triple is passed unchanged. The code, as it appears in `pc_check.py`:

```python
names, p, eqs = D_._parse_ms_file(f)
# ADAPTER: none. _parse_ms_file returns (list[str], int, list[dict[tuple[int,...], int]]), which is the
# representation write_msolve_input(path, names, p, eqs) consumes; the triple is passed unchanged.
tmp = os.path.join(rt_dir, setname + "__" + stem + ".ms")
wi = A.write_msolve_input(tmp, names, p, eqs)
b0, b1 = open(f, "rb").read(), open(tmp, "rb").read()
```

**Result: 72 of 72 byte-identical. 0 mismatches, so there is no first differing byte offset to report.**

Every parsed coefficient lies in [1, p - 1]. `write_msolve_input` dropped 0 zero equations on every input. For every input, the driver's own record agrees:
- its `input.n_zero_equations_dropped` is 0 (ac4487 `raw-result.json`; toy world B `raw-result.json`);
- its `input.sha256`, which `solve()` computes right after writing the file (v2_driver.py line 163), equals the archived file's sha256.

The 36 world-A toy `.ms` are byte-identical to the 36 world-B toy `.ms`. The per-input table is Appendix A2.

### PR-1 (b): code reading

Line numbers are against the frozen `implementation-v2/` files, and the quoted lines are in `premise-check.json` `code_quotes`.

1. **`v2_driver.solve` writes the .ms from the same `(names, p, eqs)` it substitutes into. CONFIRMED.**
   - Line 158 is the signature `def solve(ctx, names, eqs, tag, ...)`, and line 159 sets `p = ctx._p`.
   - Line 162 writes the file: `wi = A.write_msolve_input(inp, names, p, eqs)`.
   - Line 196 substitutes: `nfail = sum(1 for s in sols if not V.substitute(eqs, s, p))`. Line 204 applies the same substitution to the recorded `solutions`.
   - `eqs`, `names` and `p` are the same local objects throughout. Nothing between lines 162 and 196 rebinds or mutates them:
     - `write_msolve_input` only reads `eq.items()` (v2_arms.py line 697, `sorted(...)`);
     - `run_child` (line 166) does not receive `eqs`;
     - line 195 passes `len(names)` only.
   - Line 195 calls `rational_solutions(payload, p, len(names))` with the same `p`.
2. **`write_msolve_input` drops only identically-zero equations and writes coefficients as given. CONFIRMED, with one precision.**
   - v2_arms.py lines 691-710 cover the whole function.
   - Line 698 (`if c == 0: continue`) skips zero-coefficient TERMS inside an equation. This does not change the polynomial.
   - Lines 702-704 drop an equation only when no non-zero term remains (`if not terms: dropped += 1; continue`), that is, an identically-zero equation. Substitution into a dropped equation contributes 0, so it vanishes at every point.
   - Line 701 writes the coefficient as given: `f"{c}*{mono}"` or `f"{c}"`, with no reduction.
   - Lines 697 and 700 affect only term order and monomial spelling. The exponent vector is written through `zip(names, a)`.
3. **`v2_solver.substitute` reduces modulo p. CONFIRMED.**
   - Lines 473-485.
   - Line 481 is `t = t * pow(x, e, p) % p`, line 482 is `s = (s + t) % p`, and lines 483-484 return False on a non-zero residue.
   - A constant term enters as `t = c` (line 478) and is reduced at line 482.

**Can a system constructor place a coefficient outside [0, p) in `eqs`? No, on every path to `solve()` in v2_driver.py.**
- `descend` (v2_arms.py lines 678-688) sets `eq[monos[i]] = int(col[i]) % p` (line 686). Every `A.system_for_target` system (v2_arms.py line 717) and every raw-grid system (v2_driver.py line 142) comes from `descend`.
- `rq_relation_equation` builds its values with `% p` (v2_arms.py lines 647 and 649) and returns only the non-zero ones (line 650). `system_for_target` appends it at line 721.
- The anchor comparator system comes from `_parse_ms_file` (v2_driver.py line 704), which reduces `% p` and drops zeros (lines 606-607). It is also a gb_only solve (line 711).

`descend` can hold a coefficient equal to 0, if `col[i]` is a multiple of p. Line 698 skips it when writing, and it adds 0 in `substitute`, so the written system and the substituted system are the same polynomials.

**Whether it would matter.** Even an out-of-range coefficient would be written as given (line 701) and reduced modulo p by `substitute` (lines 481-482). The substituted system would then equal the written system modulo p, provided msolve reads integer coefficients modulo the declared characteristic. That msolve behaviour is not checked here and is not needed, because no path produces such a coefficient.

**PR-1 finding:** (a) holds for all 72 inputs. (b) finds no system difference other than dropped zero terms and zero equations.

## 3. PR-2: coverage

### The set O (draft `output_set_O`)

**Default-flag solves.** A solve is default-flag when `solves.jsonl` records `flags: []`, which covers classes C-1a, C-1b, C-1c and C-2. The C-3c classes carry `-c 0` or `-c 1`. An output is in O if at least one default-flag solve produced it. The outputs seen only under C-3c are excluded as not default-flag: the empty output `e3b0c442…` of the 12 raw ac4487 inputs under `-c 1`. The index `distinct-outputs/index.json` maps each output sha256 to the labels of its solves.

**O has 75 distinct (input, output) byte strings:**
- **event, 3:**
  - world B, from the bundle, `201812d4…`; it is also the default-flag modal output, 996 of 1000 C-1a/C-1b solves;
  - world A, from the bundle, `d2878f4f…`;
  - mode B `ec54fd15…`, C-1a#247-#250.
- **toy35, 35:** one default-flag output per input, 100 of 100 C-1c solves each. Each is byte-identical to the world-B and world-A package outputs of the same stem.
- **ac4487, 37:**
  - the 36 archived `RUN-GFPN-ac4487/solver/*.ms.out`. Each is also the default-flag modal output of its input: 100 of 100 C-2 solves, except `fx_reg1_S3_rescaled` at 95 of 100;
  - mode C `7e283c28…`, C-2#95-#99 on `fx_reg1_S3_rescaled`.

**Logs.** Each output is classified with the log of a solve that produced exactly those bytes. Where more than one such log was archived, it was classified with every one of them. All logs agree for all 75 outputs (`all_logs_agree: true`).
- The world-B event output uses the world-B package log.
- World A uses the world-A package log.
- Mode B uses the four C-1a#247-#250 logs in `distinct-outputs.tar.gz` `logs/`.
- Mode C uses the five C-2#95-#99 logs there.
- Each toy35 output uses the world-B and the world-A package logs of its stem, whose `.ms.out` bytes are identical.
- Each archived ac4487 output uses its `RUN-GFPN-ac4487/solver/` log.

**Classification.** Each output is classified exactly as `v2_driver.solve` lines 170-206:
- log text = `.ms.log` + "\n" + `.ms.err` + "\n" (lines 170-175);
- `parse_msolve_log`, `parse_msolve_param`, `rational_solutions(payload, p, nvars)`;
- `n_sub_fail` against `_parse_ms_file` of that output's input (line 196);
- `classify_solve`;
- D as lines 199-206 record it;
- then SF-1 clauses (i)-(v).

`classify_solve` receives `rec = {"outcome": <archived run_child outcome>}`, taken from the package `raw-result.json` or from `solves.jsonl`. It is `ok` for every log used, and it is the only field of `rec` that `classify_solve` reads (v2_solver.py line 490).

**Modal output and parsed comparison.**
- **Modal output.** Following `char_msolve.py` lines 557-568, the modal output of an input is the most frequent `output_sha256` over its default-flag, ok-exited solves, with ties going to the smallest sha256 (no tie occurred).
- **SE-4 (d) parsed comparison.** It compares parse kind, header degree, eliminating degree, square-free flag, the sha256 of the sorted F_p-rational solution set, and D (solverevent lines 326-331; `char_msolve.py` `parsed_key`).
- **D convention.** Here D is the D the driver would record WITH substitution computed. The characterization used `n_sub_fail = 0`.

The per-output table with every field PC-4 lists is Appendix A3. Its column "#rat. sol." counts the parsed F_p-rational solutions. "kept" counts those that pass substitution, which the driver would record (line 204).

### Instances of interest

| input | output | log(s) | outcome / reason | n_sub_fail | D (driver) | elim deg / sq-free | rational solutions (parsed) | SSF | parsed == modal |
|---|---|---|---|---|---|---|---|---|---|
| event `fx_reg0_torsion_S3_norm` (p' = 1033) | world B `201812d43b7c7a9dab2c8a1270e2a9a022a671ccb4992775aa1e431b48ef0569` (modal) | bundle world_B package | ok | 0 | 64 | 64 / true | (685, 1001, 911), (822, 543, 295); set sha256 `611489e3…` | none | (is modal) |
| event | world A `d2878f4f2b276162c78fd8b7fb31ae2fbc0a04984222a344fed047fef9cf07da` | bundle world_A package | degenerate_parametrisation / "eliminating polynomial degree 63 != quotient dimension 64 (the minimal polynomial is not square-free: non-radical ideal)" | 0 | undefined | 63 / true | (685, 1001, 911) | **(ii)** | false |
| event | mode B `ec54fd1520eafb2216fc1c6606db5f660b8867f8d176631b9da950acf10248ee` | C-1a#247, #248, #249, #250 (all four agree) | degenerate_parametrisation / "2 parsed solution(s) fail substitution into the descended system" | **2** | undefined | 64 / true | (305, 278, 911), (1004, 160, 295); set sha256 `254892d9…`; 0 of 2 satisfy the system | **(iv)** | false |
| ac4487 `fx_reg1_S3_rescaled` (p' = 4111) | archived `3b232b2b6557c13f66b535c876249edc85c0bdaa117390b05d426d12752a15f2` (modal) | RUN-GFPN-ac4487 solver/ | ok | 0 | 64 | 64 / true | none (empty set) | none | (is modal) |
| ac4487 `fx_reg1_S3_rescaled` | mode C `7e283c2834f024429d50347a1cfb42d560b4eaf1b5643a818c96c9e58cb45f06` | C-2#95, #96, #97, #98, #99 (all five agree) | ok | 0 | 64 | 64 / true | none (empty set) | none | **true** |

### Readings PR-2 (a)-(e), as the draft words them

- **(a)** "ec54fd15… (mode B) must have SSF clause (iv)."
  - **Observed:** clause (iv) on each of the 4 logs. Outcome degenerate_parametrisation, reason "2 parsed solution(s) fail substitution into the descended system", n_sub_fail = 2.
  - **Holds.**
- **(b)** "d2878f4f… (mode A) must have SSF clause (ii)."
  - **Observed:** clause (ii). Outcome degenerate_parametrisation, reason "eliminating polynomial degree 63 != quotient dimension 64 (…)", n_sub_fail = 0.
  - **Holds.**
- **(c)** "Every output in O whose SE-4 (d) parsed comparison differs from its input's modal output must have the SSF signature."
  - **Observed:** exactly 2 outputs of O differ from their input's modal output in the parsed comparison: world A `d2878f4f…` (clause (ii)) and mode B `ec54fd15…` (clause (iv)).
  - Every other output of O compares equal to its modal output: 73 outputs, including mode C `7e283c28…`. 72 of them are themselves modal.
  - No output was incomparable.
  - **Holds** (2 of 2 instances carry the signature).
- **(d)** "Every archived RUN-GFPN-ac4487 output must classify ok, with substitution_failures 0 and D equal to the D that RUN-GFPN-ac4487/raw-result.json records for that tag."
  - **Observed:** 36 of 36 classify ok, with n_sub_fail 0 and D equal to the raw-result D. The D values are 64, 384 or 16 by arm, archived values re-read.
  - The recorded outcome, substitution_failures and n_rational_solutions also agree for all 36.
  - Table: Appendix A4. **Holds.**
- **(e)** "7e283c28… (mode C) must classify ok with substitution_failures 0."
  - **Observed:** ok, n_sub_fail 0 on each of the 5 logs. D = 64, the eliminating polynomial has degree 64 and is square-free, and the rational solution set is empty.
  - **Holds.**
- **Other outputs in O with the SSF signature** (the draft's "any other output ... is recorded"): **none.** No output in O is positive_dimensional. The string "[coefficients of linear form are randomly chosen]" appears in none of the 117 logs classified. msolve's positive-dimension wording appears in none.

These are the readings as computed. What follows from them is the approval act's reading (DEC-20260924-15a77a, reserved), not this check's.

## 4. PR-3: code facts

Line numbers are against the frozen `implementation-v2/` files.

- **(i) Substitution is computed for every gb_only-false solve whose child exited ok and whose output parses as param. CONFIRMED** (v2_driver.py lines 184-197):
  - line 184 returns early only for `refused_to_start`, which is not an ok exit;
  - line 187 returns early only if `gb_only`;
  - lines 190-191 initialise `nfail = 0`;
  - line 192 gates on `rec["outcome"] == "ok"`, line 193 parses, line 194 gates on `kind == "param"`, and line 196 computes `nfail` over all parsed solutions;
  - line 197 passes `nfail` to `classify_solve`.

  No other path skips it.
- **(ii) The four classify_solve reason sites and their strings. CONFIRMED** (v2_solver.py lines 488-508):
  - line 498: `"eliminating polynomial is not square-free"` (square-free test at line 497);
  - lines 501-502: `"eliminating polynomial degree %s != quotient dimension %s (the minimal polynomial is not square-free: non-radical ideal)"` (test at line 500);
  - line 505: `"msolve reports square-free part degree %s != quotient dimension %s"` (test at line 504);
  - line 507: `"%d parsed solution(s) fail substitution into the descended system"` (test `if n_sub_fail` at line 506);
  - line 508: `return "ok", None`.

  The positive_dimensional returns are at lines 493 and 495, and the non-ok child passthrough at lines 490-491. The SF-1 prefixes and suffix match these strings exactly. Clause (ii) matches on the prefix "eliminating polynomial degree ". Clause (iv) matches on the suffix "parsed solution(s) fail substitution into the descended system".
- **(iii) Every call site of solve() and its gb_only value. CONFIRMED.** The list equals `summary.json` lines 942-999 (9 sites). A search of the `implementation-v2/`, `implementation-v2-a1/` and `implementation-v2-r1/` Python files finds no other call:
  - v2_driver.py line 358 (fixture), gb_only false;
  - line 565 (fixture4), false;
  - line 693 (anchor), **true**;
  - line 711 (anchor comparator), **true**;
  - line 786 (ctl_identity), false;
  - line 787 (ctl_rawx), false;
  - line 841 (ctl_planted), false;
  - line 1174 (cells), false;
  - implementation-v2-a1/a1_driver.py line 166 (`D.solve`, ctl_a1_planted), false.
- **(iv) The per-cell no-measurement watchdog is evaluated only between targets. CONFIRMED** (v2_driver.py lines 1141-1154).
  - The only evaluation is line 1149, at the top of the `for t in targets:` loop (line 1141), before the target's construction and `solve()` (line 1174): `if wd.get("per_cell_no_measurement_watchdog_s") and not per_D and time.time() - t_cell > ...`.
  - No other reference to `per_cell_no_measurement_watchdog_s` exists in the three implementation trees except plan and toy-plan construction (v2_make_trial_plan.py lines 35-40, a1_toy.py lines 171-172, r1_toy.py lines 120-121).
  - The per-target bound is the `timeout_s` passed to `run_child` (line 166).
- **(v) After solve() returns, .ms.log and .ms.err remain in solver/, and _retain (lines 217-231) removes at most the .ms and the .ms.out. CONFIRMED.**
  - `_retain` removes `inp` (the `.ms`, line 221, when not retained or larger than 50 MiB) and `out` (the `.ms.out`, line 227, when larger than 50 MiB).
  - No code in v2_driver.py or v2_solver.py removes a `.ms.log` or `.ms.err`. The removals are at v2_driver.py lines 144, 211, 221 and 227, and v2_solver.py line 549.
  - Precision, not a discrepancy: `solve()` itself also removes `<tag>.cg.ms.out` (line 211, the callgrind re-solve's output), and `callgrind_instructions` removes its `callgrind.out` file (v2_solver.py line 549). Neither is the `.ms`, `.ms.out`, `.ms.log` or `.ms.err` of the solve.

## 5. PR-4: log availability

All **75 of 75** outputs in O had a log of a solve that produced exactly those bytes. **Gaps: none.** Both the mode-A output and the mode-B output have logs: the bundle world_A package, and C-1a#247-#250.

## 6. Observations, discrepancies of citation, and unexpected findings (recorded; none is a stop)

1. **Citation range.** The draft's PR-1 (a) cites `_parse_ms_file` as v2_driver.py lines 582-604. The function spans lines **582-608**: the `% p` reduction is at line 606, zero dropping at 607 and `return` at 608. The code read is unchanged. Only the cited range is short.
2. **Terms as well as equations.** `write_msolve_input` skips zero-coefficient terms (v2_arms.py line 698) as well as identically-zero equations (lines 702-704). See PR-1 (b) 2.
3. **Supplementary diagnostic reproduced.** The characterization's supplementary diagnostic (`characterization.md` section 10), whose premise it left unchecked, gave mode B as 0 of 2 solutions satisfying the system and world A as 1 of 1. This check reproduces both, with the premise now checked by PR-1 (a).
4. **World A and world B inputs identical.** All 36 toy `.ms` files are byte-identical between the world-A and world-B packages.
5. **Pre-existing byte code in the v1 tree.** A gitignored `experiments/EXP-GFPN-05ff43/implementation/__pycache__/` (v1 tree) exists. Its newest file is dated 2026-09-23T03:17:31Z, which predates this task. This check does not import from `implementation/`, and it created no byte code anywhere. It is recorded, not touched.
6. **DP-5 and the runs directory.** `experiments/EXP-GFPN-05ff43/runs/` lists 50 package directories. This check created none and wrote nothing there. It did not re-audit DP-5's classification of those directories as v1 packages plus RUN-GFPN-ac4487 and RUN-GFPN-3377f1.

## 7. Deviations and disclosures

1. **Reads before the formal PR-5 step.** The card's PC-2 puts integrity before any reading. Before hashing, this Executor had:
   - listed the member names and sizes of the DV-7 bundle (`tar -tzv`);
   - listed `RUN-GFPN-ac4487/` and its `solver/` directory;
   - read the four receipts that PR-5 checks against.

   No archived content was read as a result before the hashes were checked. The hashes were first checked by hand (`sha256sum`, and a receipt comparison over 335 ac4487 receipt entries, 0 mismatches). They were then checked again as the first step of `pc_check.py` (153 checks, 0 failures). After the hand check and before the script, `characterization.md` sections 9-13, `summary.json` lines 930-1000, `char_msolve.py` lines 300-360 and 550-570, and the `solves.jsonl` schema were read to build O and the modal rule.
2. **Dry run.** One complete dry run of `pc_check.py`, with the same script bytes, wrote only to scratch (`.../premise0652ce/run1/premise-check.json`). Its output equals the final output except for the scratch path (`run1` vs `run2`). The file in the write_scope is the output of the final run. The script was edited once before the dry run, to correct the quoted line numbers, and not after it.
3. **Orientation extraction.** Before the script existed, both archives were also extracted once by hand into scratch (`.../premise0652ce/dv7`, `.../premise0652ce/distinct`), for orientation. Nothing was extracted into the repository.
4. **Rendered tables.** The appendix tables of this file were rendered from `premise-check.json` by a scratch helper, `.../premise0652ce/render.py`, sha256 `4b1b8a15b9c0f25fcba18bdcf5a3d6167fc418d187e7e7104625a0e9bdb0d06a`, which is not archived. The narrative sections were written by hand from the same JSON. The JSON is authoritative.
5. **Child record.** `classify_solve` was given `rec = {"outcome": <archived run_child outcome>}`, not a live child record (see section 3). This is the one field `classify_solve` reads (v2_solver.py line 490).
6. **Context read.** The dispatch prompt asked for AGENTS.md to be read before writing. This Executor did not load AGENTS.md. The runtime binding for this subagent says not to load it by default, and it defers to `docs/agent-runtime-core.md` and `agents/executor.md`, which were read (the former after the script run, before this file was written). No detailed AGENTS.md policy was needed for this zero-run check.
7. **No stop condition fired.** PC-2 integrity passed, and PC-1 scope was kept: no solver child, no run package, and writes only inside `experiments/EXP-GFPN-05ff43/dev-evidence/seedresolve-premise/`.

## 8. Tested scope and transfer

- **Tested scope:**
  - archived msolve 0.6.5 outputs and logs (Ubuntu 0.6.5-1build2, `-t 1`, frozen v2 argv `-v 2 -t 1 -f … -o … -P 1`);
  - toy EcGFp5-shaped systems at p' = 1033 (36 inputs of the stage-R1 toy G1 package);
  - the 36 RUN-GFPN-ac4487 fixture systems at p' = 4111 (n = m = 3);
  - known scalars only.
- **Transfer:** nothing here transfers to p' = 262151, 16777291 or 1073741831, or to p = 2^64 - 2^32 + 1. The check measures no solver behaviour. It re-classifies archived bytes with frozen code.

## Artifacts

- `experiments/EXP-GFPN-05ff43/dev-evidence/seedresolve-premise/pc_check.py`, the check script as run (sha256 above);
- `experiments/EXP-GFPN-05ff43/dev-evidence/seedresolve-premise/premise-check.json`, machine-readable, and authoritative for every value here;
- `experiments/EXP-GFPN-05ff43/dev-evidence/seedresolve-premise/premise-check.md`, this file. Its hash is reported in the Executor's return.

---

## Appendices

### A1. Integrity checks (PR-5), full hashes

| # | check | path | expected (receipt) | actual | pass |
|---|---|---|---|---|---|
| 1 | PR-5(a) seedresolve draft == TASK-20260923-df9fab addendum_sha256 | `experiments/EXP-GFPN-05ff43/amendments/v2_addendum_seedresolve.yaml` | `dc714a446a22a99fd6762196d4e6ad1b8c9e7eb3920d64cf26036f95ecadee81` | `dc714a446a22a99fd6762196d4e6ad1b8c9e7eb3920d64cf26036f95ecadee81` | True |
| 2 | PR-5(b) superseded draft | `experiments/EXP-GFPN-05ff43/amendments/v2_addendum_solverevent.yaml` | `011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f` | `011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f` | True |
| 3 | PR-5(c) characterization file | `experiments/EXP-GFPN-05ff43/dev-evidence/solver-characterization/char_msolve.py` | `a99e9e1cc5f6995c3b56e07c9f9efdca182a140b699ac35ef9debb478e407ac8` | `a99e9e1cc5f6995c3b56e07c9f9efdca182a140b699ac35ef9debb478e407ac8` | True |
| 4 | PR-5(c) characterization file | `experiments/EXP-GFPN-05ff43/dev-evidence/solver-characterization/characterization.md` | `1ec128ca8601a777885d49089c64e9ce47fc2183cae3a13dddb157faa1a2c0fb` | `1ec128ca8601a777885d49089c64e9ce47fc2183cae3a13dddb157faa1a2c0fb` | True |
| 5 | PR-5(c) characterization file | `experiments/EXP-GFPN-05ff43/dev-evidence/solver-characterization/distinct-outputs.tar.gz` | `05a0817173b7335535ba825c0a0ba813faa3659f83bc6ed7592cdc44b9424994` | `05a0817173b7335535ba825c0a0ba813faa3659f83bc6ed7592cdc44b9424994` | True |
| 6 | PR-5(c) characterization file | `experiments/EXP-GFPN-05ff43/dev-evidence/solver-characterization/solves.jsonl` | `eb9e3c446ac1bcc08a74e2ff1baea439d8d4084c89df6b0dcacd5d4e443ea644` | `eb9e3c446ac1bcc08a74e2ff1baea439d8d4084c89df6b0dcacd5d4e443ea644` | True |
| 7 | PR-5(c) characterization file | `experiments/EXP-GFPN-05ff43/dev-evidence/solver-characterization/summary.json` | `66c5c39600a268ba3a308f22cf426e699f75e68736ef2a8768dc821ea92cbb48` | `66c5c39600a268ba3a308f22cf426e699f75e68736ef2a8768dc821ea92cbb48` | True |
| 8 | PR-5(d) DV-7 bundle | `experiments/EXP-GFPN-05ff43/dev-evidence/stageR1-dv7/stageR1-dv7-evidence.tar.gz` | `70b83d61bfd05fcc92208c9f2bdba58fea0e7b587a927d54141bb72ccd35bd14` | `70b83d61bfd05fcc92208c9f2bdba58fea0e7b587a927d54141bb72ccd35bd14` | True |
| 9 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/raw-result.json` | `1a7cf0be66c497f711e35c136e4f03dea668c5c7e649c21ff9490b6b1cd9b32d` | `1a7cf0be66c497f711e35c136e4f03dea668c5c7e649c21ff9490b6b1cd9b32d` | True |
| 10 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_S3.ms` | `7d12649723025d584b260c29b8aeb16e5d694d29c56c26ca79eb07cab54a7834` | `7d12649723025d584b260c29b8aeb16e5d694d29c56c26ca79eb07cab54a7834` | True |
| 11 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_S3.ms.err` | `ba6e73fc0aaf4b2bc650b8b9886b991fcf7060a5cad8424aa5e1b734cd9fd13f` | `ba6e73fc0aaf4b2bc650b8b9886b991fcf7060a5cad8424aa5e1b734cd9fd13f` | True |
| 12 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_S3.ms.log` | `deb61f8142cc20100b6d2bf23f22dbe532f46ad00f1635f69a3abc7232d92f61` | `deb61f8142cc20100b6d2bf23f22dbe532f46ad00f1635f69a3abc7232d92f61` | True |
| 13 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_S3.ms.out` | `60a4cd6e4607259325080b558c7e01a27e61509d74ba382d33e13ab299afc9cf` | `60a4cd6e4607259325080b558c7e01a27e61509d74ba382d33e13ab299afc9cf` | True |
| 14 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_S3_rescaled.ms` | `2158ff2bb4f1d9beebf7f7333b68b44cf9d9661dd7e23a43db0b5bae604c609c` | `2158ff2bb4f1d9beebf7f7333b68b44cf9d9661dd7e23a43db0b5bae604c609c` | True |
| 15 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_S3_rescaled.ms.err` | `06fc9a2146c04c9e72e83ff70aaafc50d7cba5ce09da03f2394f4df600ff55ab` | `06fc9a2146c04c9e72e83ff70aaafc50d7cba5ce09da03f2394f4df600ff55ab` | True |
| 16 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_S3_rescaled.ms.log` | `987e942cdec7d234da1ad5114c55d335c71ac154947adca4b3a6a14b35e9d012` | `987e942cdec7d234da1ad5114c55d335c71ac154947adca4b3a6a14b35e9d012` | True |
| 17 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_S3_rescaled.ms.out` | `efb50e2ef8c6553e46d3aaa4b7422a9aa2aa996292d0ac77736ddcd0d4a474af` | `efb50e2ef8c6553e46d3aaa4b7422a9aa2aa996292d0ac77736ddcd0d4a474af` | True |
| 18 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_raw_u.ms` | `43dd963b11cd14c1bc07d591d82bb79ec1f7e83b14becfb6de0fe77aa28867c3` | `43dd963b11cd14c1bc07d591d82bb79ec1f7e83b14becfb6de0fe77aa28867c3` | True |
| 19 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_raw_u.ms.err` | `1216da09661c4ad00560e9c7b380ee2c41cf32e79ae5732a21678e13874750dc` | `1216da09661c4ad00560e9c7b380ee2c41cf32e79ae5732a21678e13874750dc` | True |
| 20 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_raw_u.ms.log` | `321117ae5e842612b04640ffd5f9506e06d0d190003496f6629ca47d44a05c70` | `321117ae5e842612b04640ffd5f9506e06d0d190003496f6629ca47d44a05c70` | True |
| 21 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_raw_u.ms.out` | `913635c67f3d3d1a2606e39552302a14dad741b3588c96f88fab96ccc692eeb4` | `913635c67f3d3d1a2606e39552302a14dad741b3588c96f88fab96ccc692eeb4` | True |
| 22 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_raw_x.ms` | `947425ed55808afcedb0b81c5d5b932719bca7d1270336a615efe031e5ae922d` | `947425ed55808afcedb0b81c5d5b932719bca7d1270336a615efe031e5ae922d` | True |
| 23 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_raw_x.ms.err` | `f21233387df4351a3969f887059d06ee80933625943310348a41434963f0cc6d` | `f21233387df4351a3969f887059d06ee80933625943310348a41434963f0cc6d` | True |
| 24 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_raw_x.ms.log` | `705f689645996e20047ebc1f41d32a8d1a5ee2b0b3faa358450e34cd478ec68b` | `705f689645996e20047ebc1f41d32a8d1a5ee2b0b3faa358450e34cd478ec68b` | True |
| 25 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_raw_x.ms.out` | `7dc2c544bc5d015fcda4041b343c2282498394ee01fc434b909ac0b1674ebddb` | `7dc2c544bc5d015fcda4041b343c2282498394ee01fc434b909ac0b1674ebddb` | True |
| 26 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_torsion_S3_norm.ms` | `fcb93aa7dfa0b15a71294052c5a2cea43299f11efe75a40911995da83e777a8e` | `fcb93aa7dfa0b15a71294052c5a2cea43299f11efe75a40911995da83e777a8e` | True |
| 27 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_torsion_S3_norm.ms.err` | `1e2c4e4774519dba400dda79b986d4b958391f86f5e42c27b135740122ccad98` | `1e2c4e4774519dba400dda79b986d4b958391f86f5e42c27b135740122ccad98` | True |
| 28 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_torsion_S3_norm.ms.log` | `cda428f32ec17e38ca1b60239b05c61e00d59f855025d538d04102126e31d7bc` | `cda428f32ec17e38ca1b60239b05c61e00d59f855025d538d04102126e31d7bc` | True |
| 29 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_torsion_S3_norm.ms.out` | `efb572acc1a06f1f27c0eb6394affe8b5512d4577e8f22cbe6a640fd435f84f9` | `efb572acc1a06f1f27c0eb6394affe8b5512d4577e8f22cbe6a640fd435f84f9` | True |
| 30 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_torsion_S3_rq.ms` | `8f6e0ded976b97e87ce35082d5d66c6311b019c49c5b1269f973be6c19414f23` | `8f6e0ded976b97e87ce35082d5d66c6311b019c49c5b1269f973be6c19414f23` | True |
| 31 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_torsion_S3_rq.ms.err` | `5a08c3ede29184b58d283bb52332b61e32c0870636a9a9a4145a0923f80e12ff` | `5a08c3ede29184b58d283bb52332b61e32c0870636a9a9a4145a0923f80e12ff` | True |
| 32 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_torsion_S3_rq.ms.log` | `6bc19f36592c1e81e6ba3171688ca6d6cd7c90ab64e43e847d3006c437e8537f` | `6bc19f36592c1e81e6ba3171688ca6d6cd7c90ab64e43e847d3006c437e8537f` | True |
| 33 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh1_torsion_S3_rq.ms.out` | `7a89173a15d12c5b12dd96287ca8ddd27fb1d11a10dcfb43e7dcce1f55f529d8` | `7a89173a15d12c5b12dd96287ca8ddd27fb1d11a10dcfb43e7dcce1f55f529d8` | True |
| 34 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_S3.ms` | `bb8ef96744594a2d6e2a51b6367263c720008d17c9f466b48b87525c64b39e55` | `bb8ef96744594a2d6e2a51b6367263c720008d17c9f466b48b87525c64b39e55` | True |
| 35 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_S3.ms.err` | `10f845579b62de665660b57d8d206cce971d8e5562b4d21eaa8502f1ad6b858e` | `10f845579b62de665660b57d8d206cce971d8e5562b4d21eaa8502f1ad6b858e` | True |
| 36 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_S3.ms.log` | `d09d067b26213a3264a99866c504e39480ad58e0ebeefecf3532ede1dd06b59f` | `d09d067b26213a3264a99866c504e39480ad58e0ebeefecf3532ede1dd06b59f` | True |
| 37 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_S3.ms.out` | `eca772970934e5a5119c9f4a12552806996c04a5ac08f494b2558aec3872a064` | `eca772970934e5a5119c9f4a12552806996c04a5ac08f494b2558aec3872a064` | True |
| 38 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_S3_rescaled.ms` | `2eb8e24e8a163ff97b9fa3c306998c44d9a8152c41cfd98185ba644f5793cae1` | `2eb8e24e8a163ff97b9fa3c306998c44d9a8152c41cfd98185ba644f5793cae1` | True |
| 39 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_S3_rescaled.ms.err` | `d79759b0a129fb3453fa9e3c1eafc37bd3077711bd586875f8a6c1050deff8b4` | `d79759b0a129fb3453fa9e3c1eafc37bd3077711bd586875f8a6c1050deff8b4` | True |
| 40 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_S3_rescaled.ms.log` | `c14ba4cbcdbc8ed9be82013d566ad6d3a31f23d3c3001751b048982addbba72b` | `c14ba4cbcdbc8ed9be82013d566ad6d3a31f23d3c3001751b048982addbba72b` | True |
| 41 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_S3_rescaled.ms.out` | `ac26fa0bd1d18e170df2dc7f9e2cc870777bec1eaf6bfb94d1751abb1a551905` | `ac26fa0bd1d18e170df2dc7f9e2cc870777bec1eaf6bfb94d1751abb1a551905` | True |
| 42 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_raw_u.ms` | `b7b2a6269f85f3d3968c996dfba1cc824a9077e0044b54d8b695e468533a3758` | `b7b2a6269f85f3d3968c996dfba1cc824a9077e0044b54d8b695e468533a3758` | True |
| 43 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_raw_u.ms.err` | `71a65517cb87fc90d28f2e9e3b0dfeb0f7d7614c007ad9dcb837e70bf7ff4423` | `71a65517cb87fc90d28f2e9e3b0dfeb0f7d7614c007ad9dcb837e70bf7ff4423` | True |
| 44 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_raw_u.ms.log` | `898924343afac66de1aa14f9998f9c50c27457f4074e0575881a9cc5f3df02f0` | `898924343afac66de1aa14f9998f9c50c27457f4074e0575881a9cc5f3df02f0` | True |
| 45 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_raw_u.ms.out` | `12c4b747e3b2a426cd041c3df4c75abee4a3f543d280ab7b8b86392636e6a9e0` | `12c4b747e3b2a426cd041c3df4c75abee4a3f543d280ab7b8b86392636e6a9e0` | True |
| 46 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_raw_x.ms` | `7d4465a6e457c18a2ab511888ee44d87ad5a53126a82f754c5fa1a7dcbdd7f65` | `7d4465a6e457c18a2ab511888ee44d87ad5a53126a82f754c5fa1a7dcbdd7f65` | True |
| 47 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_raw_x.ms.err` | `4c1e3fd6769f1536cfbac9a0a0f6a29432e02564509d4362cce982193fae0b1b` | `4c1e3fd6769f1536cfbac9a0a0f6a29432e02564509d4362cce982193fae0b1b` | True |
| 48 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_raw_x.ms.log` | `94e933aaba38667b061c78e7b18089a8da2f24a93a3a12bb1103f955464e4eb2` | `94e933aaba38667b061c78e7b18089a8da2f24a93a3a12bb1103f955464e4eb2` | True |
| 49 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_raw_x.ms.out` | `7a3c217d2f436c65f8f4e0ae846486fb39cc56d23a8deebb50fee746ce13da31` | `7a3c217d2f436c65f8f4e0ae846486fb39cc56d23a8deebb50fee746ce13da31` | True |
| 50 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_torsion_S3_norm.ms` | `c7ebc3e951644871dd9ea333805b2dfb88089136a85d67ea892c882a4b389773` | `c7ebc3e951644871dd9ea333805b2dfb88089136a85d67ea892c882a4b389773` | True |
| 51 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_torsion_S3_norm.ms.err` | `82505c45397a995ea5e508509ea80efce09c2afc2fd213f88b7561dca08e0f20` | `82505c45397a995ea5e508509ea80efce09c2afc2fd213f88b7561dca08e0f20` | True |
| 52 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_torsion_S3_norm.ms.log` | `a0ca6672d30a7c1a74461266daaaf6777597f2aa2c295dcf1dfe8d33bac530ff` | `a0ca6672d30a7c1a74461266daaaf6777597f2aa2c295dcf1dfe8d33bac530ff` | True |
| 53 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_torsion_S3_norm.ms.out` | `2ebac156e566bc1d677176160a288dff485291b267280096ad88d7923815ea42` | `2ebac156e566bc1d677176160a288dff485291b267280096ad88d7923815ea42` | True |
| 54 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_torsion_S3_rq.ms` | `184262615a97ff4ec716d2082e97ac10b04519a66006136f3c13f38a87b78d1d` | `184262615a97ff4ec716d2082e97ac10b04519a66006136f3c13f38a87b78d1d` | True |
| 55 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_torsion_S3_rq.ms.err` | `cdfadf817fe12856f21152192635ef8e07e82562c1a6714eeac9a4fb24228a22` | `cdfadf817fe12856f21152192635ef8e07e82562c1a6714eeac9a4fb24228a22` | True |
| 56 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_torsion_S3_rq.ms.log` | `c5745221c4affe7a69902031ebc3747283824385c8600b414f680b8c3baf19de` | `c5745221c4affe7a69902031ebc3747283824385c8600b414f680b8c3baf19de` | True |
| 57 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_fresh2_torsion_S3_rq.ms.out` | `b564bab4afdff3fc1b82867cf514b98e062cad47435c5ba8fa26c9cb4fdf6a71` | `b564bab4afdff3fc1b82867cf514b98e062cad47435c5ba8fa26c9cb4fdf6a71` | True |
| 58 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_S3.ms` | `4e8e6c6cbe03ad41bf51b6e8a2cc58312c9863ab39d717bdf5ea673551cc026f` | `4e8e6c6cbe03ad41bf51b6e8a2cc58312c9863ab39d717bdf5ea673551cc026f` | True |
| 59 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_S3.ms.err` | `4f09d285199d8eb32c9cbebc22edc29bb0df3053d6009de95d1b00e4379150a1` | `4f09d285199d8eb32c9cbebc22edc29bb0df3053d6009de95d1b00e4379150a1` | True |
| 60 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_S3.ms.log` | `690db383889e5d0dab8909d9fe6fbf68cf41aa0921d21e9b3fed37f88bc1930e` | `690db383889e5d0dab8909d9fe6fbf68cf41aa0921d21e9b3fed37f88bc1930e` | True |
| 61 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_S3.ms.out` | `5a5c3ade3fade8acf12e33e0a7dfb7a603f6412f32518ea54e3ce56913c07dd4` | `5a5c3ade3fade8acf12e33e0a7dfb7a603f6412f32518ea54e3ce56913c07dd4` | True |
| 62 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_S3_rescaled.ms` | `6f275c5559a38f1e2b7d80b508b0724dac4ed67cf30ccc478463d21fe13de86c` | `6f275c5559a38f1e2b7d80b508b0724dac4ed67cf30ccc478463d21fe13de86c` | True |
| 63 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_S3_rescaled.ms.err` | `d79759b0a129fb3453fa9e3c1eafc37bd3077711bd586875f8a6c1050deff8b4` | `d79759b0a129fb3453fa9e3c1eafc37bd3077711bd586875f8a6c1050deff8b4` | True |
| 64 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_S3_rescaled.ms.log` | `2d97420ec9fda699a576e2ba96f7f4ae99319cb781cc62c97bf041ac0cf33de8` | `2d97420ec9fda699a576e2ba96f7f4ae99319cb781cc62c97bf041ac0cf33de8` | True |
| 65 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_S3_rescaled.ms.out` | `e0b8706cb48594fa3f12e17e7979416404e27500091c34cd0b462a3d0ac95c94` | `e0b8706cb48594fa3f12e17e7979416404e27500091c34cd0b462a3d0ac95c94` | True |
| 66 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_raw_u.ms` | `d98d178e8b9352641ab66882547bb181a9e2b001ab1462c165929c09a2d05185` | `d98d178e8b9352641ab66882547bb181a9e2b001ab1462c165929c09a2d05185` | True |
| 67 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_raw_u.ms.err` | `2adfa742b061b5c29711c559b6fa79f88c97041b4b00ff61a8b4f1c78c4503b0` | `2adfa742b061b5c29711c559b6fa79f88c97041b4b00ff61a8b4f1c78c4503b0` | True |
| 68 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_raw_u.ms.log` | `b511b4bb4ffc50271e8fd6ca01484017ef104f7a8bbbb374a4ad29367c439c3c` | `b511b4bb4ffc50271e8fd6ca01484017ef104f7a8bbbb374a4ad29367c439c3c` | True |
| 69 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_raw_u.ms.out` | `fa43416ce9f92ff8f786242cab468295ba5434a3cb8ca404a5ee56ef6c4e0dd9` | `fa43416ce9f92ff8f786242cab468295ba5434a3cb8ca404a5ee56ef6c4e0dd9` | True |
| 70 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_raw_x.ms` | `dfb3c7a35bc2a0f45b731c59286006b515f6c0865e72795f6c8c405a56bc7385` | `dfb3c7a35bc2a0f45b731c59286006b515f6c0865e72795f6c8c405a56bc7385` | True |
| 71 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_raw_x.ms.err` | `6f67bf963af6526dc2e0eea854759725727859848ca8a2c310006730f8b358a8` | `6f67bf963af6526dc2e0eea854759725727859848ca8a2c310006730f8b358a8` | True |
| 72 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_raw_x.ms.log` | `65250b36c678a79350a00afd181be1a883f03f00d34d804d69cd86d3bff129d5` | `65250b36c678a79350a00afd181be1a883f03f00d34d804d69cd86d3bff129d5` | True |
| 73 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_raw_x.ms.out` | `4979535ed24c467ad728e2cc02a4db146b1f675ed4770ef5b38ff26380c6a87d` | `4979535ed24c467ad728e2cc02a4db146b1f675ed4770ef5b38ff26380c6a87d` | True |
| 74 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_torsion_S3_norm.ms` | `f08e9c7715fcc5125b2e6ef452ac934dc01faf6cfb8a86f2902e889795daba6c` | `f08e9c7715fcc5125b2e6ef452ac934dc01faf6cfb8a86f2902e889795daba6c` | True |
| 75 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_torsion_S3_norm.ms.err` | `d79759b0a129fb3453fa9e3c1eafc37bd3077711bd586875f8a6c1050deff8b4` | `d79759b0a129fb3453fa9e3c1eafc37bd3077711bd586875f8a6c1050deff8b4` | True |
| 76 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_torsion_S3_norm.ms.log` | `005f4c1b50aa6a9388ab2dc36fc9a45c49c86cb2d6447151528f4120bafea9f0` | `005f4c1b50aa6a9388ab2dc36fc9a45c49c86cb2d6447151528f4120bafea9f0` | True |
| 77 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_torsion_S3_norm.ms.out` | `4b64be0be57b1998517596d551497c8471c9316d45d023e39d86390a87347cdb` | `4b64be0be57b1998517596d551497c8471c9316d45d023e39d86390a87347cdb` | True |
| 78 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_torsion_S3_rq.ms` | `7e9521ae3d7ee4662fd1bb7ee60c4e71b871c9427b734623dc7f0c2bcd39aab8` | `7e9521ae3d7ee4662fd1bb7ee60c4e71b871c9427b734623dc7f0c2bcd39aab8` | True |
| 79 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_torsion_S3_rq.ms.err` | `cdfadf817fe12856f21152192635ef8e07e82562c1a6714eeac9a4fb24228a22` | `cdfadf817fe12856f21152192635ef8e07e82562c1a6714eeac9a4fb24228a22` | True |
| 80 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_torsion_S3_rq.ms.log` | `7b1bd39e5ec1f1df34af1ea738859631113af5e76916e5ba041e6d90d0d5f292` | `7b1bd39e5ec1f1df34af1ea738859631113af5e76916e5ba041e6d90d0d5f292` | True |
| 81 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted0_torsion_S3_rq.ms.out` | `88f25f454f5270af5b8126d00131e673fce14b1d8870252ee311af3fe7f779dc` | `88f25f454f5270af5b8126d00131e673fce14b1d8870252ee311af3fe7f779dc` | True |
| 82 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_S3.ms` | `f5f19484a913a5f2686c9acce0934119d6a89b2690844095511b4a4efa52e50f` | `f5f19484a913a5f2686c9acce0934119d6a89b2690844095511b4a4efa52e50f` | True |
| 83 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_S3.ms.err` | `10f845579b62de665660b57d8d206cce971d8e5562b4d21eaa8502f1ad6b858e` | `10f845579b62de665660b57d8d206cce971d8e5562b4d21eaa8502f1ad6b858e` | True |
| 84 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_S3.ms.log` | `ad94f64df5d79a137ce356c9afd970c8185313be40ed267b2cc363a12d087234` | `ad94f64df5d79a137ce356c9afd970c8185313be40ed267b2cc363a12d087234` | True |
| 85 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_S3.ms.out` | `d697a8abefa7732512558046b0049fc85abfd8ca25333e81b58db4efd1d7a199` | `d697a8abefa7732512558046b0049fc85abfd8ca25333e81b58db4efd1d7a199` | True |
| 86 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_S3_rescaled.ms` | `c67e713504390fdc14594bcf0aa284b89ce58c2e7f57b9f464c6cbd93c6a04a0` | `c67e713504390fdc14594bcf0aa284b89ce58c2e7f57b9f464c6cbd93c6a04a0` | True |
| 87 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_S3_rescaled.ms.err` | `82505c45397a995ea5e508509ea80efce09c2afc2fd213f88b7561dca08e0f20` | `82505c45397a995ea5e508509ea80efce09c2afc2fd213f88b7561dca08e0f20` | True |
| 88 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_S3_rescaled.ms.log` | `dc2571e21669c96ef1dba58f94d689753b70c09adc7b457d0651c975e8fd12ae` | `dc2571e21669c96ef1dba58f94d689753b70c09adc7b457d0651c975e8fd12ae` | True |
| 89 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_S3_rescaled.ms.out` | `811679d46e3b0ff196a915edd119479a67247e1ae5c579dd5409b0b8fa1dd770` | `811679d46e3b0ff196a915edd119479a67247e1ae5c579dd5409b0b8fa1dd770` | True |
| 90 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_raw_u.ms` | `a5cc1a5c2a346c7374afe6a0fc2254fc0cf9e77eea2585c1d1a144b8bff2794d` | `a5cc1a5c2a346c7374afe6a0fc2254fc0cf9e77eea2585c1d1a144b8bff2794d` | True |
| 91 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_raw_u.ms.err` | `ea4b2e30c1969048fcba9c399845df3bb7bd2a530ba3eabdf66f4538e3681137` | `ea4b2e30c1969048fcba9c399845df3bb7bd2a530ba3eabdf66f4538e3681137` | True |
| 92 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_raw_u.ms.log` | `1f58855a073a0aa55678c3369d18f86491603cc43f0a4eb36fe37ecfbdc6692b` | `1f58855a073a0aa55678c3369d18f86491603cc43f0a4eb36fe37ecfbdc6692b` | True |
| 93 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_raw_u.ms.out` | `e2560125e6aaabe22bff55f9335cdf00c23d320059be38751ae4fed8ddae4485` | `e2560125e6aaabe22bff55f9335cdf00c23d320059be38751ae4fed8ddae4485` | True |
| 94 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_raw_x.ms` | `95a9bb67b687dca01b00e3019eda8c51798135e5f7d4207a740d3e47324d00e2` | `95a9bb67b687dca01b00e3019eda8c51798135e5f7d4207a740d3e47324d00e2` | True |
| 95 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_raw_x.ms.err` | `eb255723629713d6fb2c9321224cc3b61f4fdb661b8c54641f3d061457566a3f` | `eb255723629713d6fb2c9321224cc3b61f4fdb661b8c54641f3d061457566a3f` | True |
| 96 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_raw_x.ms.log` | `f47d4cae21312f6c76e12ceddb7bcd7ab03712c8a13c65f1ee713ce713f9b0d6` | `f47d4cae21312f6c76e12ceddb7bcd7ab03712c8a13c65f1ee713ce713f9b0d6` | True |
| 97 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_raw_x.ms.out` | `a8d0557e35dd8e65716eb2476e39f68bfb4bbd21296a3de6d889b68366443612` | `a8d0557e35dd8e65716eb2476e39f68bfb4bbd21296a3de6d889b68366443612` | True |
| 98 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_torsion_S3_norm.ms` | `283daef201f55cbb482e5684d8108a93848cac930761521ad0ad3f2a08d20446` | `283daef201f55cbb482e5684d8108a93848cac930761521ad0ad3f2a08d20446` | True |
| 99 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_torsion_S3_norm.ms.err` | `c5f5935ddd9522e081ecb4883afea819bc083aacd6913f3f9e0194f7a377862a` | `c5f5935ddd9522e081ecb4883afea819bc083aacd6913f3f9e0194f7a377862a` | True |
| 100 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_torsion_S3_norm.ms.log` | `f0c7c4363c64ba97351f4eb935e4a64322da576a58005b7ec66a3acde6837a06` | `f0c7c4363c64ba97351f4eb935e4a64322da576a58005b7ec66a3acde6837a06` | True |
| 101 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_torsion_S3_norm.ms.out` | `aaadd08c36eb7f577dcd5bd5c650d39c58d78536f2cd546ec295480a13e107d2` | `aaadd08c36eb7f577dcd5bd5c650d39c58d78536f2cd546ec295480a13e107d2` | True |
| 102 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_torsion_S3_rq.ms` | `d50db2ef1eb758a2d4ba94deb472494726798146857a03382ce5380af6e37138` | `d50db2ef1eb758a2d4ba94deb472494726798146857a03382ce5380af6e37138` | True |
| 103 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_torsion_S3_rq.ms.err` | `cdfadf817fe12856f21152192635ef8e07e82562c1a6714eeac9a4fb24228a22` | `cdfadf817fe12856f21152192635ef8e07e82562c1a6714eeac9a4fb24228a22` | True |
| 104 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_torsion_S3_rq.ms.log` | `b29605c0947abafc273ba1432f97dd30c8c179b8f04c1bba725325cd2f10ae6d` | `b29605c0947abafc273ba1432f97dd30c8c179b8f04c1bba725325cd2f10ae6d` | True |
| 105 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_planted1_torsion_S3_rq.ms.out` | `4a2ffb7100cc81cda0ad321f870c436d792c7aa7bcfc89a05ffa4d68ce741a35` | `4a2ffb7100cc81cda0ad321f870c436d792c7aa7bcfc89a05ffa4d68ce741a35` | True |
| 106 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_S3.ms` | `196cbb9e36871b4c5836db73a7cd169c3ebad99e46908ad572e7d387e9e138ea` | `196cbb9e36871b4c5836db73a7cd169c3ebad99e46908ad572e7d387e9e138ea` | True |
| 107 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_S3.ms.err` | `89abb77396cea534da500d5eceab31e7506cf7c31cafb5f9a858fdc916ca527a` | `89abb77396cea534da500d5eceab31e7506cf7c31cafb5f9a858fdc916ca527a` | True |
| 108 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_S3.ms.log` | `cb0800a12c1d710ea00a8fd8e875f716ae6a7a42d4f8898df080586d6ee645e0` | `cb0800a12c1d710ea00a8fd8e875f716ae6a7a42d4f8898df080586d6ee645e0` | True |
| 109 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_S3.ms.out` | `53293037cd7354f974b11d01ce909733b57df7fe1478ca4c25e152ed5f2ddfca` | `53293037cd7354f974b11d01ce909733b57df7fe1478ca4c25e152ed5f2ddfca` | True |
| 110 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_S3_rescaled.ms` | `71113e0928d1993c8e07581766ff057608d7f8b20269b3040455fc4a22bb80bc` | `71113e0928d1993c8e07581766ff057608d7f8b20269b3040455fc4a22bb80bc` | True |
| 111 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_S3_rescaled.ms.err` | `2cf878924c403b5a25e4d7d00b11fa4ef5d61e762cdc8d9090bd1510901ccff8` | `2cf878924c403b5a25e4d7d00b11fa4ef5d61e762cdc8d9090bd1510901ccff8` | True |
| 112 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_S3_rescaled.ms.log` | `25f9f6c492a2daa89b24250de409a944376c798070d49cc161408133b3730a20` | `25f9f6c492a2daa89b24250de409a944376c798070d49cc161408133b3730a20` | True |
| 113 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_S3_rescaled.ms.out` | `6ea8b0e8d7fc75a29a7f3cd2d54150f0ce4d469745cd5ae6eb252dcf0eb0c7f5` | `6ea8b0e8d7fc75a29a7f3cd2d54150f0ce4d469745cd5ae6eb252dcf0eb0c7f5` | True |
| 114 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_raw_u.ms` | `d02799791d70942ed98dc02453534361649a7dfae4858e7247b2f01fb3a4e125` | `d02799791d70942ed98dc02453534361649a7dfae4858e7247b2f01fb3a4e125` | True |
| 115 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_raw_u.ms.err` | `1ffa2b9344134cf78306f6381f75c95d685997da90c4ff3197e6500eaaa23be2` | `1ffa2b9344134cf78306f6381f75c95d685997da90c4ff3197e6500eaaa23be2` | True |
| 116 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_raw_u.ms.log` | `e31030f2300f0a848529202d67dbebee48da594dd57d84ba8c3192de1dbad714` | `e31030f2300f0a848529202d67dbebee48da594dd57d84ba8c3192de1dbad714` | True |
| 117 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_raw_u.ms.out` | `728ecf36505ecee018f828d3b19827920f9d8479db13b0845d1eb986ca079a62` | `728ecf36505ecee018f828d3b19827920f9d8479db13b0845d1eb986ca079a62` | True |
| 118 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_raw_x.ms` | `b773e44b385cfa494c12f55649f1120613019088dd7e989959209d56d17215b1` | `b773e44b385cfa494c12f55649f1120613019088dd7e989959209d56d17215b1` | True |
| 119 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_raw_x.ms.err` | `f8d6cd8c254cf525573edcbe7039cf782b108b6b7f75e922aa71080dddd28997` | `f8d6cd8c254cf525573edcbe7039cf782b108b6b7f75e922aa71080dddd28997` | True |
| 120 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_raw_x.ms.log` | `d683c29e8813ba5ca7fb2db32102ad1626bc54e5f4efda255ca0b0366bb558eb` | `d683c29e8813ba5ca7fb2db32102ad1626bc54e5f4efda255ca0b0366bb558eb` | True |
| 121 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_raw_x.ms.out` | `a87355d97a2f48702cffbba36beed08523bb28ffef2b0a139c7d39278adddd61` | `a87355d97a2f48702cffbba36beed08523bb28ffef2b0a139c7d39278adddd61` | True |
| 122 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_torsion_S3_norm.ms` | `1e2a011db35e862fea3b7303038d154624e4dbc855e561ee21e769a6ccf64ec6` | `1e2a011db35e862fea3b7303038d154624e4dbc855e561ee21e769a6ccf64ec6` | True |
| 123 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_torsion_S3_norm.ms.err` | `82505c45397a995ea5e508509ea80efce09c2afc2fd213f88b7561dca08e0f20` | `82505c45397a995ea5e508509ea80efce09c2afc2fd213f88b7561dca08e0f20` | True |
| 124 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_torsion_S3_norm.ms.log` | `d4a06791e0dd2bf3cc6c3bfee8f12aa55486e47c983f25e399c97697982a372f` | `d4a06791e0dd2bf3cc6c3bfee8f12aa55486e47c983f25e399c97697982a372f` | True |
| 125 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_torsion_S3_norm.ms.out` | `606fc541d777720d9cc9992a67618ef71f922154f864b9643a7f78eea7d3e3c0` | `606fc541d777720d9cc9992a67618ef71f922154f864b9643a7f78eea7d3e3c0` | True |
| 126 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_torsion_S3_rq.ms` | `0fa15ed30cee8af4076607bd2df6ddc0c0ce47cf9471569a0bbc7a777e7ae1f0` | `0fa15ed30cee8af4076607bd2df6ddc0c0ce47cf9471569a0bbc7a777e7ae1f0` | True |
| 127 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_torsion_S3_rq.ms.err` | `d2dcc3321e30f0848a5f70651f65d4d5f4d82e16ef3eba9657ec58425435d33c` | `d2dcc3321e30f0848a5f70651f65d4d5f4d82e16ef3eba9657ec58425435d33c` | True |
| 128 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_torsion_S3_rq.ms.log` | `4783923b73b1a73d0e9fad15a42915b024a405015fff205565f8cc50f4dd88f0` | `4783923b73b1a73d0e9fad15a42915b024a405015fff205565f8cc50f4dd88f0` | True |
| 129 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg0_torsion_S3_rq.ms.out` | `43b940e706031a9c2b1e9a041dbaecbf0d9013deab86e5489dbbda2c8f6e27f9` | `43b940e706031a9c2b1e9a041dbaecbf0d9013deab86e5489dbbda2c8f6e27f9` | True |
| 130 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_S3.ms` | `b83cce3a4d18d2d101b6b57e7ee82bf550cc8cde307b5ac755fdac883e8bd606` | `b83cce3a4d18d2d101b6b57e7ee82bf550cc8cde307b5ac755fdac883e8bd606` | True |
| 131 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_S3.ms.err` | `82505c45397a995ea5e508509ea80efce09c2afc2fd213f88b7561dca08e0f20` | `82505c45397a995ea5e508509ea80efce09c2afc2fd213f88b7561dca08e0f20` | True |
| 132 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_S3.ms.log` | `6fc891b482d41af3cde71990f52f3dd3275a0c1f10083bcf7e339032a07224a0` | `6fc891b482d41af3cde71990f52f3dd3275a0c1f10083bcf7e339032a07224a0` | True |
| 133 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_S3.ms.out` | `1f2628d960a8e77cc256f5156b415aa50d7a90b2d3c79b5da9a022a135ecf36b` | `1f2628d960a8e77cc256f5156b415aa50d7a90b2d3c79b5da9a022a135ecf36b` | True |
| 134 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_S3_rescaled.ms` | `e6ff2e124af08866c2e2a715f530ae2d1f224ab921293c16bc87fcfdca4b8c0e` | `e6ff2e124af08866c2e2a715f530ae2d1f224ab921293c16bc87fcfdca4b8c0e` | True |
| 135 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_S3_rescaled.ms.err` | `c5f5935ddd9522e081ecb4883afea819bc083aacd6913f3f9e0194f7a377862a` | `c5f5935ddd9522e081ecb4883afea819bc083aacd6913f3f9e0194f7a377862a` | True |
| 136 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_S3_rescaled.ms.log` | `742821610f98ff6dbc298c0a8d23d9fa0a1862743befa6571400cf7b1f419a41` | `742821610f98ff6dbc298c0a8d23d9fa0a1862743befa6571400cf7b1f419a41` | True |
| 137 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_S3_rescaled.ms.out` | `3b232b2b6557c13f66b535c876249edc85c0bdaa117390b05d426d12752a15f2` | `3b232b2b6557c13f66b535c876249edc85c0bdaa117390b05d426d12752a15f2` | True |
| 138 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_raw_u.ms` | `51919b6faf5359e67f4c77597b56632cd6a08eda3c295d658e7ba4c576e7a22b` | `51919b6faf5359e67f4c77597b56632cd6a08eda3c295d658e7ba4c576e7a22b` | True |
| 139 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_raw_u.ms.err` | `dd4d51f9493b3f4ccaa501a626cd25a781ae9cd5a2719150a5491545b29c918d` | `dd4d51f9493b3f4ccaa501a626cd25a781ae9cd5a2719150a5491545b29c918d` | True |
| 140 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_raw_u.ms.log` | `fefc9f966b33e7a666f1f2a208c8b4c44b49a01f79b55cdb8796d5191010e926` | `fefc9f966b33e7a666f1f2a208c8b4c44b49a01f79b55cdb8796d5191010e926` | True |
| 141 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_raw_u.ms.out` | `e57c788f1f63c4cab8ff56a6795b451b2dc9e3e5e792951fee9e16899f73af33` | `e57c788f1f63c4cab8ff56a6795b451b2dc9e3e5e792951fee9e16899f73af33` | True |
| 142 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_raw_x.ms` | `c591c8225d32245e99e13770ee11961f8ce1eac9fb25be9284c748e348374ad1` | `c591c8225d32245e99e13770ee11961f8ce1eac9fb25be9284c748e348374ad1` | True |
| 143 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_raw_x.ms.err` | `ace90558090c737a8f434cb1e8a687a64a1d38a602923146ece58de054cb2e25` | `ace90558090c737a8f434cb1e8a687a64a1d38a602923146ece58de054cb2e25` | True |
| 144 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_raw_x.ms.log` | `18006e231a9d14b52f9e0829d43533c6ec5bbfafc1989eb76426cb89e9d8e7da` | `18006e231a9d14b52f9e0829d43533c6ec5bbfafc1989eb76426cb89e9d8e7da` | True |
| 145 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_raw_x.ms.out` | `5f44e62678ce87698fd3455ae9509713c194caa703829b25b91c484e6ad63733` | `5f44e62678ce87698fd3455ae9509713c194caa703829b25b91c484e6ad63733` | True |
| 146 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_torsion_S3_norm.ms` | `d9c3da3dd38b39e91852eba0f47b59abb5d149f61fa593051475be097c59f0cf` | `d9c3da3dd38b39e91852eba0f47b59abb5d149f61fa593051475be097c59f0cf` | True |
| 147 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_torsion_S3_norm.ms.err` | `d57d54180e8217b87650154e71a2a393197c8ad913f9b3e416bdb2130139a783` | `d57d54180e8217b87650154e71a2a393197c8ad913f9b3e416bdb2130139a783` | True |
| 148 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_torsion_S3_norm.ms.log` | `33e85056f666518b6574514468971801dbcd883ce3533c0ee3962023525d6273` | `33e85056f666518b6574514468971801dbcd883ce3533c0ee3962023525d6273` | True |
| 149 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_torsion_S3_norm.ms.out` | `efc90355062318d531bd6f411513e5988cb24d6b94dd2f3ab53035d70882e807` | `efc90355062318d531bd6f411513e5988cb24d6b94dd2f3ab53035d70882e807` | True |
| 150 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_torsion_S3_rq.ms` | `930b137142c664a628ea699bd1875c9a37208f54c971537226dbec48d14ccd78` | `930b137142c664a628ea699bd1875c9a37208f54c971537226dbec48d14ccd78` | True |
| 151 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_torsion_S3_rq.ms.err` | `cdfadf817fe12856f21152192635ef8e07e82562c1a6714eeac9a4fb24228a22` | `cdfadf817fe12856f21152192635ef8e07e82562c1a6714eeac9a4fb24228a22` | True |
| 152 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_torsion_S3_rq.ms.log` | `1006d7e2a7a5e9f3ce1729d8da83c7e290e9aaab1b19f16750c7ee2280a178b8` | `1006d7e2a7a5e9f3ce1729d8da83c7e290e9aaab1b19f16750c7ee2280a178b8` | True |
| 153 | PR-5(e) RUN-GFPN-ac4487 file read | `experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/solver/fx_reg1_torsion_S3_rq.ms.out` | `840f544d9da36243a573c4810188d27c47f7bb56f3cd7b4aac11a7501594299b` | `840f544d9da36243a573c4810188d27c47f7bb56f3cd7b4aac11a7501594299b` | True |

### A2. PR-1 (a) round trip, per input (72)

| set | stem | input sha256 | bytes | p | eqs | terms | byte-identical | first diff | driver-recorded input sha256 equal | zero eqs dropped (write / driver record) |
|---|---|---|---|---|---|---|---|---|---|---|
| toy_worldB_G1 | fx_fresh1_S3 | `cea3502048836b80ea283cb1525167305ed2f79c6721c3a85a1437e831383fcb` | 1088 | 1033 | 3 | 99 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_fresh1_S3_rescaled | `509d3a2aa6d307d55ed7cb72551620bf5bfb5b70ff92b5d2fed607a57581567b` | 1085 | 1033 | 3 | 99 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_fresh1_raw_u | `b485a53872d58faabe932a77c825661dedfee32fab57847bf38c3b10385d5207` | 5467 | 1033 | 3 | 367 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_fresh1_raw_x | `d4f5c058f2646fc1fafa74de8fd7b3e3732ac61ec4e8229f161545cd1b796bd2` | 5461 | 1033 | 3 | 367 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_fresh1_torsion_S3_norm | `e4e472a36fb268870a1dca6d83ff26dc4afa89f21fee2991d78b5ea3d468f75d` | 1122 | 1033 | 3 | 103 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_fresh1_torsion_S3_rq | `96352e9634c7749c2e8c58c99c7afd6b993309eb2c465b1dea322fc8595bf1d8` | 414 | 1033 | 4 | 49 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_fresh2_S3 | `df38bd2ec5e26c4ed7240f805edd047d89ecb41524c5b77d8289cbb8e69824ef` | 1109 | 1033 | 3 | 101 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_fresh2_S3_rescaled | `9f3283bbb9dae2def6ec6e28aadc49a66e37125f535bdcbd1bbd92ed9b8790a7` | 1115 | 1033 | 3 | 101 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_fresh2_raw_u | `1ae3b80c33bbded52930ca01ea42c652cdbfc34b197b526d2ec7b35c7f7ef4c9` | 5478 | 1033 | 3 | 367 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_fresh2_raw_x | `753be6b875776c7d25a337ecb96a6df8b9bcb9af941afd008b85e4ea1b412e63` | 5419 | 1033 | 3 | 367 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_fresh2_torsion_S3_norm | `a6442d00e40f2978443a40624ad28b8be1ae281a55a549fea1cece11e3a9190e` | 1136 | 1033 | 3 | 103 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_fresh2_torsion_S3_rq | `b39c9cfed68b9ac859717b51c249a09e9ef87146a83a88dc3b1e55420b827b6a` | 416 | 1033 | 4 | 49 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_planted0_S3 | `f938a2fb6b4e3f7174c733f89b6e1f1df63f13fbb62e32ac0c6e52a16f0e3029` | 1109 | 1033 | 3 | 101 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_planted0_S3_rescaled | `81cd4d233c07a536dc213c87d38cede430159dcc585aaf749f71cce923cff9ac` | 1106 | 1033 | 3 | 101 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_planted0_raw_u | `c0a6e6d35dc3f319fe354fa5bcb7c0fcc898428586b132be4fdb5c335aa9cb39` | 5415 | 1033 | 3 | 367 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_planted0_raw_x | `0c6c4fb6871d766d3cfc9cff71a577de0fdf399bf6217f07a1813bb44e765bf9` | 5442 | 1033 | 3 | 367 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_planted0_torsion_S3_norm | `af2375fc7222fb1d1dbf446dfe934f20d6e090992a932e00f9a3347ce361fbd6` | 1141 | 1033 | 3 | 103 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_planted0_torsion_S3_rq | `f977ac598f3d91940d926b964fe69e4a1cb0113731efe105f6a04031d98c5aab` | 417 | 1033 | 4 | 49 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_planted1_S3 | `c5615ee416e2822b066b836cf04c9dccff9416e714c32fb0f57bb2834af42c7e` | 1107 | 1033 | 3 | 101 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_planted1_S3_rescaled | `82af52d40642d4a8d709fd9afcf21087b5afd4d6ea4d15406476f7644b7a8e0f` | 1113 | 1033 | 3 | 101 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_planted1_raw_u | `e2dee5c5ff14592228fe2baa397ee82fe0c8a7cf88e26bd428173bb5ceceb6c0` | 5410 | 1033 | 3 | 367 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_planted1_raw_x | `f85b7832d93efc526aa542990e6799c99359e0030aa709562c1d62f3b123b0b5` | 5451 | 1033 | 3 | 367 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_planted1_torsion_S3_norm | `1d803ea0eb4cc209268168b911f0e7e4fa8483b2f3aa439a09a9bc570cf718ea` | 1135 | 1033 | 3 | 103 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_planted1_torsion_S3_rq | `9f744e44d24dfbb00522989a9ba70f089894f0546c3e66dba63b0a15fa1eb67d` | 417 | 1033 | 4 | 49 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_reg0_S3 | `4bd492fcc86c25db7169471f7a2ba285d681403e623c7686cdc8b30c6977f13b` | 1117 | 1033 | 3 | 101 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_reg0_S3_rescaled | `d9ca088cc49d4910473e7649038f00609cf77afdaa99cc853a8ac8974be42eeb` | 1109 | 1033 | 3 | 101 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_reg0_raw_u | `76b4463494308acebd54d55767d67499a0a1062e8f8034dcfdfa7206df0e88d2` | 5078 | 1033 | 3 | 343 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_reg0_raw_x | `5633532ed88dba1738cd32c84f8f1d166f56909c7418c94867d59536dc5b6bc4` | 5079 | 1033 | 3 | 343 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_reg0_torsion_S3_norm | `541b57b904e0c16956f9ea4615a32f1aaaae1cdfe7ca9c3b767f3b5f22d537c8` | 1129 | 1033 | 3 | 103 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_reg0_torsion_S3_rq | `9c0f96f4bb7499c5ec4bb6e690c2816c6a75240a6df631d2235bd2119da412a6` | 418 | 1033 | 4 | 49 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_reg1_S3 | `e6f463b43cad858c695b1e79f6fa00193335c0f3e3ac5c964232eaaca5069062` | 1110 | 1033 | 3 | 101 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_reg1_S3_rescaled | `0df006eef0b9c7d19662d7cc2df67cdb6c993a2b1af6c6aad0169df26686d0ac` | 1113 | 1033 | 3 | 101 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_reg1_raw_u | `a2798724ca895b98d1fbd6d0b24202e1bf36639402212e7da2a93e80e398c796` | 5445 | 1033 | 3 | 367 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_reg1_raw_x | `d719fbd40f665c766136710c575200526c37e887e12b735def048e61d4aacced` | 5433 | 1033 | 3 | 367 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_reg1_torsion_S3_norm | `8013002bb71238536c92e70ccff2fbeed98c4835e80f47ed00bcb12800152e15` | 1135 | 1033 | 3 | 103 | True | None | True | 0 / 0 |
| toy_worldB_G1 | fx_reg1_torsion_S3_rq | `39039f7ab0ac0bf4e8658a1961480d9ba8cb42a54480013990b32c9b643d7303` | 419 | 1033 | 4 | 49 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_fresh1_S3 | `7d12649723025d584b260c29b8aeb16e5d694d29c56c26ca79eb07cab54a7834` | 1189 | 4111 | 3 | 101 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_fresh1_S3_rescaled | `2158ff2bb4f1d9beebf7f7333b68b44cf9d9661dd7e23a43db0b5bae604c609c` | 1203 | 4111 | 3 | 101 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_fresh1_raw_u | `43dd963b11cd14c1bc07d591d82bb79ec1f7e83b14becfb6de0fe77aa28867c3` | 5768 | 4111 | 3 | 367 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_fresh1_raw_x | `947425ed55808afcedb0b81c5d5b932719bca7d1270336a615efe031e5ae922d` | 5769 | 4111 | 3 | 367 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_fresh1_torsion_S3_norm | `fcb93aa7dfa0b15a71294052c5a2cea43299f11efe75a40911995da83e777a8e` | 1212 | 4111 | 3 | 103 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_fresh1_torsion_S3_rq | `8f6e0ded976b97e87ce35082d5d66c6311b019c49c5b1269f973be6c19414f23` | 454 | 4111 | 4 | 49 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_fresh2_S3 | `bb8ef96744594a2d6e2a51b6367263c720008d17c9f466b48b87525c64b39e55` | 1196 | 4111 | 3 | 101 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_fresh2_S3_rescaled | `2eb8e24e8a163ff97b9fa3c306998c44d9a8152c41cfd98185ba644f5793cae1` | 1194 | 4111 | 3 | 101 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_fresh2_raw_u | `b7b2a6269f85f3d3968c996dfba1cc824a9077e0044b54d8b695e468533a3758` | 5751 | 4111 | 3 | 367 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_fresh2_raw_x | `7d4465a6e457c18a2ab511888ee44d87ad5a53126a82f754c5fa1a7dcbdd7f65` | 5752 | 4111 | 3 | 367 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_fresh2_torsion_S3_norm | `c7ebc3e951644871dd9ea333805b2dfb88089136a85d67ea892c882a4b389773` | 1213 | 4111 | 3 | 103 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_fresh2_torsion_S3_rq | `184262615a97ff4ec716d2082e97ac10b04519a66006136f3c13f38a87b78d1d` | 454 | 4111 | 4 | 49 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_planted0_S3 | `4e8e6c6cbe03ad41bf51b6e8a2cc58312c9863ab39d717bdf5ea673551cc026f` | 1194 | 4111 | 3 | 101 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_planted0_S3_rescaled | `6f275c5559a38f1e2b7d80b508b0724dac4ed67cf30ccc478463d21fe13de86c` | 1197 | 4111 | 3 | 101 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_planted0_raw_u | `d98d178e8b9352641ab66882547bb181a9e2b001ab1462c165929c09a2d05185` | 5758 | 4111 | 3 | 367 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_planted0_raw_x | `dfb3c7a35bc2a0f45b731c59286006b515f6c0865e72795f6c8c405a56bc7385` | 5753 | 4111 | 3 | 367 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_planted0_torsion_S3_norm | `f08e9c7715fcc5125b2e6ef452ac934dc01faf6cfb8a86f2902e889795daba6c` | 1216 | 4111 | 3 | 103 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_planted0_torsion_S3_rq | `7e9521ae3d7ee4662fd1bb7ee60c4e71b871c9427b734623dc7f0c2bcd39aab8` | 450 | 4111 | 4 | 49 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_planted1_S3 | `f5f19484a913a5f2686c9acce0934119d6a89b2690844095511b4a4efa52e50f` | 1190 | 4111 | 3 | 101 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_planted1_S3_rescaled | `c67e713504390fdc14594bcf0aa284b89ce58c2e7f57b9f464c6cbd93c6a04a0` | 1194 | 4111 | 3 | 101 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_planted1_raw_u | `a5cc1a5c2a346c7374afe6a0fc2254fc0cf9e77eea2585c1d1a144b8bff2794d` | 5729 | 4111 | 3 | 367 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_planted1_raw_x | `95a9bb67b687dca01b00e3019eda8c51798135e5f7d4207a740d3e47324d00e2` | 5694 | 4111 | 3 | 367 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_planted1_torsion_S3_norm | `283daef201f55cbb482e5684d8108a93848cac930761521ad0ad3f2a08d20446` | 1215 | 4111 | 3 | 103 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_planted1_torsion_S3_rq | `d50db2ef1eb758a2d4ba94deb472494726798146857a03382ce5380af6e37138` | 454 | 4111 | 4 | 49 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_reg0_S3 | `196cbb9e36871b4c5836db73a7cd169c3ebad99e46908ad572e7d387e9e138ea` | 1187 | 4111 | 3 | 101 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_reg0_S3_rescaled | `71113e0928d1993c8e07581766ff057608d7f8b20269b3040455fc4a22bb80bc` | 1202 | 4111 | 3 | 101 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_reg0_raw_u | `d02799791d70942ed98dc02453534361649a7dfae4858e7247b2f01fb3a4e125` | 5766 | 4111 | 3 | 367 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_reg0_raw_x | `b773e44b385cfa494c12f55649f1120613019088dd7e989959209d56d17215b1` | 5749 | 4111 | 3 | 367 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_reg0_torsion_S3_norm | `1e2a011db35e862fea3b7303038d154624e4dbc855e561ee21e769a6ccf64ec6` | 1199 | 4111 | 3 | 103 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_reg0_torsion_S3_rq | `0fa15ed30cee8af4076607bd2df6ddc0c0ce47cf9471569a0bbc7a777e7ae1f0` | 455 | 4111 | 4 | 49 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_reg1_S3 | `b83cce3a4d18d2d101b6b57e7ee82bf550cc8cde307b5ac755fdac883e8bd606` | 1187 | 4111 | 3 | 101 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_reg1_S3_rescaled | `e6ff2e124af08866c2e2a715f530ae2d1f224ab921293c16bc87fcfdca4b8c0e` | 1193 | 4111 | 3 | 101 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_reg1_raw_u | `51919b6faf5359e67f4c77597b56632cd6a08eda3c295d658e7ba4c576e7a22b` | 5738 | 4111 | 3 | 367 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_reg1_raw_x | `c591c8225d32245e99e13770ee11961f8ce1eac9fb25be9284c748e348374ad1` | 5728 | 4111 | 3 | 367 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_reg1_torsion_S3_norm | `d9c3da3dd38b39e91852eba0f47b59abb5d149f61fa593051475be097c59f0cf` | 1219 | 4111 | 3 | 103 | True | None | True | 0 / 0 |
| RUN-GFPN-ac4487 | fx_reg1_torsion_S3_rq | `930b137142c664a628ea699bd1875c9a37208f54c971537226dbec48d14ccd78` | 454 | 4111 | 4 | 49 | True | None | True | 0 / 0 |

### A3. PR-2 per-output classification of O (75), primary log shown; every log of an output agrees

| # | input key | output sha256 | log used (primary) | logs | outcome | reason | n_sub_fail | D (driver) | parse | elim deg | sq-free | #rat. sol. | kept | solution-set sha256 | SSF | modal? | parsed == modal |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | event/fx_reg0_torsion_S3_norm | `201812d43b7c7a9dab2c8a1270e2a9a022a671ccb4992775aa1e431b48ef0569` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_reg0_torsion_S3_norm | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 2 | 2 | `611489e3aa0054455a1b788668029fae72ba0bd574378d88d753e41f2073e879` | none | True | True |
| 2 | event/fx_reg0_torsion_S3_norm | `d2878f4f2b276162c78fd8b7fb31ae2fbc0a04984222a344fed047fef9cf07da` | bundle toy world_A RUN-GFPN-a61a10 solver/fx_reg0_torsion_S3_norm | 1 (agree) | degenerate_parametrisation | eliminating polynomial degree 63 != quotient dimension 64 (the minimal polynomial is not square-free: non-radical ideal) | 0 | None | param | 63 | True | 1 | 0 | `b8e8eebbf673b8e2d65fb0791d4f2c7e076cc04ef8d672b8851498411c5f5250` | ii | False | False |
| 3 | ac4487/fx_fresh1_S3 | `60a4cd6e4607259325080b558c7e01a27e61509d74ba382d33e13ab299afc9cf` | RUN-GFPN-ac4487 solver/fx_fresh1_S3 | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 3 | 3 | `026e643d1ad8fd6a4766703bc5830e555a7a1e99658b3452c1714493b55c64ba` | none | True | True |
| 4 | ac4487/fx_fresh1_S3_rescaled | `efb50e2ef8c6553e46d3aaa4b7422a9aa2aa996292d0ac77736ddcd0d4a474af` | RUN-GFPN-ac4487 solver/fx_fresh1_S3_rescaled | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 6 | 6 | `38e1a2fbe5d96084f77717bfb7a0f7865d637eb4802e4057083b173b09790568` | none | True | True |
| 5 | ac4487/fx_fresh1_raw_u | `913635c67f3d3d1a2606e39552302a14dad741b3588c96f88fab96ccc692eeb4` | RUN-GFPN-ac4487 solver/fx_fresh1_raw_u | 1 (agree) | ok | - | 0 | 384 | param | 384 | True | 24 | 24 | `e78bc3a18e7147ab13576d0026923196785c5c10de0b2fc9b43be7094ca36e95` | none | True | True |
| 6 | ac4487/fx_fresh1_raw_x | `7dc2c544bc5d015fcda4041b343c2282498394ee01fc434b909ac0b1674ebddb` | RUN-GFPN-ac4487 solver/fx_fresh1_raw_x | 1 (agree) | ok | - | 0 | 384 | param | 384 | True | 6 | 6 | `d57c6b6595470e430c8f3a8c6631f136739388857c94e02a42c08ef2f5e740bb` | none | True | True |
| 7 | ac4487/fx_fresh1_torsion_S3_norm | `efb572acc1a06f1f27c0eb6394affe8b5512d4577e8f22cbe6a640fd435f84f9` | RUN-GFPN-ac4487 solver/fx_fresh1_torsion_S3_norm | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 2 | 2 | `a28b1e932ae772cfedd6b421e27bacbf80dfdaf60ddab4bb1ccb1c90f842018f` | none | True | True |
| 8 | ac4487/fx_fresh1_torsion_S3_rq | `7a89173a15d12c5b12dd96287ca8ddd27fb1d11a10dcfb43e7dcce1f55f529d8` | RUN-GFPN-ac4487 solver/fx_fresh1_torsion_S3_rq | 1 (agree) | ok | - | 0 | 16 | param | 16 | True | 2 | 2 | `44b87d4f932f1fdbfa41c732b185d0a90d9c3e938129dab0a4bb703b9313daee` | none | True | True |
| 9 | ac4487/fx_fresh2_S3 | `eca772970934e5a5119c9f4a12552806996c04a5ac08f494b2558aec3872a064` | RUN-GFPN-ac4487 solver/fx_fresh2_S3 | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 10 | ac4487/fx_fresh2_S3_rescaled | `ac26fa0bd1d18e170df2dc7f9e2cc870777bec1eaf6bfb94d1751abb1a551905` | RUN-GFPN-ac4487 solver/fx_fresh2_S3_rescaled | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 2 | 2 | `3b396bd78865fda167dd818c7a90bdd890d646b0602c1a3e331d572602d7b6cf` | none | True | True |
| 11 | ac4487/fx_fresh2_raw_u | `12c4b747e3b2a426cd041c3df4c75abee4a3f543d280ab7b8b86392636e6a9e0` | RUN-GFPN-ac4487 solver/fx_fresh2_raw_u | 1 (agree) | ok | - | 0 | 384 | param | 384 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 12 | ac4487/fx_fresh2_raw_x | `7a3c217d2f436c65f8f4e0ae846486fb39cc56d23a8deebb50fee746ce13da31` | RUN-GFPN-ac4487 solver/fx_fresh2_raw_x | 1 (agree) | ok | - | 0 | 384 | param | 384 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 13 | ac4487/fx_fresh2_torsion_S3_norm | `2ebac156e566bc1d677176160a288dff485291b267280096ad88d7923815ea42` | RUN-GFPN-ac4487 solver/fx_fresh2_torsion_S3_norm | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 14 | ac4487/fx_fresh2_torsion_S3_rq | `b564bab4afdff3fc1b82867cf514b98e062cad47435c5ba8fa26c9cb4fdf6a71` | RUN-GFPN-ac4487 solver/fx_fresh2_torsion_S3_rq | 1 (agree) | ok | - | 0 | 16 | param | 16 | True | 2 | 2 | `68877ab335cfe7121efc3a47b9f89c9922f8fa4d137dbcb6e0a70fbfc1c6b60a` | none | True | True |
| 15 | ac4487/fx_planted0_S3 | `5a5c3ade3fade8acf12e33e0a7dfb7a603f6412f32518ea54e3ce56913c07dd4` | RUN-GFPN-ac4487 solver/fx_planted0_S3 | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 16 | ac4487/fx_planted0_S3_rescaled | `e0b8706cb48594fa3f12e17e7979416404e27500091c34cd0b462a3d0ac95c94` | RUN-GFPN-ac4487 solver/fx_planted0_S3_rescaled | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 8 | 8 | `d571b5a0191d666abd33f3cb8a5f6679a858697344d948aaa564cda89f1d98f4` | none | True | True |
| 17 | ac4487/fx_planted0_raw_u | `fa43416ce9f92ff8f786242cab468295ba5434a3cb8ca404a5ee56ef6c4e0dd9` | RUN-GFPN-ac4487 solver/fx_planted0_raw_u | 1 (agree) | ok | - | 0 | 384 | param | 384 | True | 48 | 48 | `05194d39a3a830a677f525cff6b39cf3efb771a149eb43b4be67bc8a99e576c4` | none | True | True |
| 18 | ac4487/fx_planted0_raw_x | `4979535ed24c467ad728e2cc02a4db146b1f675ed4770ef5b38ff26380c6a87d` | RUN-GFPN-ac4487 solver/fx_planted0_raw_x | 1 (agree) | ok | - | 0 | 384 | param | 384 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 19 | ac4487/fx_planted0_torsion_S3_norm | `4b64be0be57b1998517596d551497c8471c9316d45d023e39d86390a87347cdb` | RUN-GFPN-ac4487 solver/fx_planted0_torsion_S3_norm | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 20 | ac4487/fx_planted0_torsion_S3_rq | `88f25f454f5270af5b8126d00131e673fce14b1d8870252ee311af3fe7f779dc` | RUN-GFPN-ac4487 solver/fx_planted0_torsion_S3_rq | 1 (agree) | ok | - | 0 | 16 | param | 16 | True | 2 | 2 | `2ca639e2d3bb3e730df5fd24440077c3ce79e44f98f296322c1200add276a6d3` | none | True | True |
| 21 | ac4487/fx_planted1_S3 | `d697a8abefa7732512558046b0049fc85abfd8ca25333e81b58db4efd1d7a199` | RUN-GFPN-ac4487 solver/fx_planted1_S3 | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 22 | ac4487/fx_planted1_S3_rescaled | `811679d46e3b0ff196a915edd119479a67247e1ae5c579dd5409b0b8fa1dd770` | RUN-GFPN-ac4487 solver/fx_planted1_S3_rescaled | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 4 | 4 | `2a7aea4c2acbcbf5e6de5c47606251bb53680d31847bdbe0c6760711a273cb03` | none | True | True |
| 23 | ac4487/fx_planted1_raw_u | `e2560125e6aaabe22bff55f9335cdf00c23d320059be38751ae4fed8ddae4485` | RUN-GFPN-ac4487 solver/fx_planted1_raw_u | 1 (agree) | ok | - | 0 | 384 | param | 384 | True | 24 | 24 | `1ee30dd209bda4fa0483b641ab97ea9f89664b57e465e4988e7c5a6bbdab13fb` | none | True | True |
| 24 | ac4487/fx_planted1_raw_x | `a8d0557e35dd8e65716eb2476e39f68bfb4bbd21296a3de6d889b68366443612` | RUN-GFPN-ac4487 solver/fx_planted1_raw_x | 1 (agree) | ok | - | 0 | 384 | param | 384 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 25 | ac4487/fx_planted1_torsion_S3_norm | `aaadd08c36eb7f577dcd5bd5c650d39c58d78536f2cd546ec295480a13e107d2` | RUN-GFPN-ac4487 solver/fx_planted1_torsion_S3_norm | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 26 | ac4487/fx_planted1_torsion_S3_rq | `4a2ffb7100cc81cda0ad321f870c436d792c7aa7bcfc89a05ffa4d68ce741a35` | RUN-GFPN-ac4487 solver/fx_planted1_torsion_S3_rq | 1 (agree) | ok | - | 0 | 16 | param | 16 | True | 1 | 1 | `b3ed1e965a6c2ac6997f0c3af9b684f1ea8ff704c131bb0277870aff079d3062` | none | True | True |
| 27 | ac4487/fx_reg0_S3 | `53293037cd7354f974b11d01ce909733b57df7fe1478ca4c25e152ed5f2ddfca` | RUN-GFPN-ac4487 solver/fx_reg0_S3 | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 1 | 1 | `595d50aa3f9dcc447214e6900cc3c0bda6d5a267c24c888a49decec9aefe537f` | none | True | True |
| 28 | ac4487/fx_reg0_S3_rescaled | `6ea8b0e8d7fc75a29a7f3cd2d54150f0ce4d469745cd5ae6eb252dcf0eb0c7f5` | RUN-GFPN-ac4487 solver/fx_reg0_S3_rescaled | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 29 | ac4487/fx_reg0_raw_u | `728ecf36505ecee018f828d3b19827920f9d8479db13b0845d1eb986ca079a62` | RUN-GFPN-ac4487 solver/fx_reg0_raw_u | 1 (agree) | ok | - | 0 | 384 | param | 384 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 30 | ac4487/fx_reg0_raw_x | `a87355d97a2f48702cffbba36beed08523bb28ffef2b0a139c7d39278adddd61` | RUN-GFPN-ac4487 solver/fx_reg0_raw_x | 1 (agree) | ok | - | 0 | 384 | param | 384 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 31 | ac4487/fx_reg0_torsion_S3_norm | `606fc541d777720d9cc9992a67618ef71f922154f864b9643a7f78eea7d3e3c0` | RUN-GFPN-ac4487 solver/fx_reg0_torsion_S3_norm | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 1 | 1 | `11f1e3689a48c94b041a5df22060feb80d06e9b80539cc5a79b847f32c72b921` | none | True | True |
| 32 | ac4487/fx_reg0_torsion_S3_rq | `43b940e706031a9c2b1e9a041dbaecbf0d9013deab86e5489dbbda2c8f6e27f9` | RUN-GFPN-ac4487 solver/fx_reg0_torsion_S3_rq | 1 (agree) | ok | - | 0 | 16 | param | 16 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 33 | ac4487/fx_reg1_S3 | `1f2628d960a8e77cc256f5156b415aa50d7a90b2d3c79b5da9a022a135ecf36b` | RUN-GFPN-ac4487 solver/fx_reg1_S3 | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 34 | ac4487/fx_reg1_S3_rescaled | `3b232b2b6557c13f66b535c876249edc85c0bdaa117390b05d426d12752a15f2` | RUN-GFPN-ac4487 solver/fx_reg1_S3_rescaled | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 35 | ac4487/fx_reg1_S3_rescaled | `7e283c2834f024429d50347a1cfb42d560b4eaf1b5643a818c96c9e58cb45f06` | characterization C-2#95 (distinct-outputs.tar.gz logs/) | 5 (agree) | ok | - | 0 | 64 | param | 64 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | False | True |
| 36 | ac4487/fx_reg1_raw_u | `e57c788f1f63c4cab8ff56a6795b451b2dc9e3e5e792951fee9e16899f73af33` | RUN-GFPN-ac4487 solver/fx_reg1_raw_u | 1 (agree) | ok | - | 0 | 384 | param | 384 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 37 | ac4487/fx_reg1_raw_x | `5f44e62678ce87698fd3455ae9509713c194caa703829b25b91c484e6ad63733` | RUN-GFPN-ac4487 solver/fx_reg1_raw_x | 1 (agree) | ok | - | 0 | 384 | param | 384 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 38 | ac4487/fx_reg1_torsion_S3_norm | `efc90355062318d531bd6f411513e5988cb24d6b94dd2f3ab53035d70882e807` | RUN-GFPN-ac4487 solver/fx_reg1_torsion_S3_norm | 1 (agree) | ok | - | 0 | 64 | param | 64 | True | 2 | 2 | `fca08975f40a8534729fd8bf1bb6cdc0a0980ef7a871e7da166e151fdb5556c4` | none | True | True |
| 39 | ac4487/fx_reg1_torsion_S3_rq | `840f544d9da36243a573c4810188d27c47f7bb56f3cd7b4aac11a7501594299b` | RUN-GFPN-ac4487 solver/fx_reg1_torsion_S3_rq | 1 (agree) | ok | - | 0 | 16 | param | 16 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 40 | event/fx_reg0_torsion_S3_norm | `ec54fd1520eafb2216fc1c6606db5f660b8867f8d176631b9da950acf10248ee` | characterization C-1a#247 (distinct-outputs.tar.gz logs/) | 4 (agree) | degenerate_parametrisation | 2 parsed solution(s) fail substitution into the descended system | 2 | None | param | 64 | True | 2 | 0 | `254892d948106519d8e42592b9505565460b86a41de3ebe74a01db0ac779e6ab` | iv | False | False |
| 41 | toy35/fx_fresh1_S3 | `0b826a955bf88e8b0fc53b330f8a2d1ae387dddf170cc1585f687882b198808f` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_fresh1_S3 | 2 (agree) | ok | - | 0 | 64 | param | 64 | True | 1 | 1 | `036c039bb54f04dbdf42ae80a1908b7dedcb08c5472cf16c94e5d69299f275ed` | none | True | True |
| 42 | toy35/fx_fresh1_S3_rescaled | `cd0ea21d0d43a66c47dcd863678bcd7c8fc8226ae09cc2c252a80a74828170f9` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_fresh1_S3_rescaled | 2 (agree) | ok | - | 0 | 64 | param | 64 | True | 3 | 3 | `7874f6f24d8b9154a72d8ffcef53c96e096973fa0ea2349594edbeac3a38a8ed` | none | True | True |
| 43 | toy35/fx_fresh1_raw_u | `a260a14727f5fb0aee47022d38e3a951599051a29a49a071d049563f689461b8` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_fresh1_raw_u | 2 (agree) | ok | - | 0 | 384 | param | 384 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 44 | toy35/fx_fresh1_raw_x | `441286fd1641a103156bf5a3a3d6893634a59579d842a84e1a192d623febe258` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_fresh1_raw_x | 2 (agree) | ok | - | 0 | 384 | param | 384 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 45 | toy35/fx_fresh1_torsion_S3_norm | `b9d29cb8c0e323c8a8297b993be4d1ea3e976ad3892f53e4951748edf2b82994` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_fresh1_torsion_S3_norm | 2 (agree) | ok | - | 0 | 64 | param | 64 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 46 | toy35/fx_fresh1_torsion_S3_rq | `d4b7d575a576020e28d74b8144c12b8228ec6fb9287aac38be465ab5eacd23ec` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_fresh1_torsion_S3_rq | 2 (agree) | ok | - | 0 | 16 | param | 16 | True | 2 | 2 | `bff0a2324cc209cde220fa20469d50030d785f063a064b0ce19c437b3c624ce9` | none | True | True |
| 47 | toy35/fx_fresh2_S3 | `c64559085efbb499c0f21ab3bd6ea2411399628ab78e9f471e130e92b59b35c5` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_fresh2_S3 | 2 (agree) | ok | - | 0 | 64 | param | 64 | True | 2 | 2 | `d4e8fc09e0e053149dddecfcbd1398f366324b96f5711f3d2daeeb6d18d51683` | none | True | True |
| 48 | toy35/fx_fresh2_S3_rescaled | `92fae595920502891cb6d2081af4fe6f25863b315d2de1466da6f2e78f1b171f` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_fresh2_S3_rescaled | 2 (agree) | ok | - | 0 | 64 | param | 64 | True | 2 | 2 | `ebb3a2f5b3be5a50798d538e32b8c002aeb748a3d69a008a2c589eb48122e880` | none | True | True |
| 49 | toy35/fx_fresh2_raw_u | `658094488ecd881eaba88a89256b06dab3ec9404d82f42683c1fdbd88ae7e559` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_fresh2_raw_u | 2 (agree) | ok | - | 0 | 384 | param | 384 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 50 | toy35/fx_fresh2_raw_x | `8ff2d23f552c3b08d0859bf723435b71e5149c3fb48bf6915b8300ccc47a073b` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_fresh2_raw_x | 2 (agree) | ok | - | 0 | 384 | param | 384 | True | 6 | 6 | `a09d6b84bb5dfd25d0e9d1dcd18a95d715c5dd70ec8f3b730ba809d2c89aa7ac` | none | True | True |
| 51 | toy35/fx_fresh2_torsion_S3_norm | `474178c25c8394eb8650bf155889d27ff0bfc63444394588318afd90d7b885b0` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_fresh2_torsion_S3_norm | 2 (agree) | ok | - | 0 | 64 | param | 64 | True | 1 | 1 | `3653b53fa51fa6d4b513ec253261fe0b00013b2583a28e17deb617a805bc1144` | none | True | True |
| 52 | toy35/fx_fresh2_torsion_S3_rq | `332ee8496348c73fce55fcdcfd7e32398581d0b95ebbacd807ecca9b4bd63a76` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_fresh2_torsion_S3_rq | 2 (agree) | ok | - | 0 | 16 | param | 16 | True | 1 | 1 | `77c5ed2a439faf69539bc5f004d81fc2a6fe223242adf92aca2153a40b5dd1eb` | none | True | True |
| 53 | toy35/fx_planted0_S3 | `12337eae105636c6f0ff11a8fe925cbedb2fd9bd35c0cacc4b95f8cd4c20422e` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_planted0_S3 | 2 (agree) | ok | - | 0 | 64 | param | 64 | True | 3 | 3 | `bf85f62024946ce691bc452655de55fd9f8f74e5cfc8b678ea7b0bc09917c571` | none | True | True |
| 54 | toy35/fx_planted0_S3_rescaled | `5ade3f32ffa1eadf33af4c7ed9eb465161ff0d630f729c8881c565c85c62edd5` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_planted0_S3_rescaled | 2 (agree) | ok | - | 0 | 64 | param | 64 | True | 4 | 4 | `447615f8c0b95df8ecd1ab1795b094aa8a63ff5c812d1e8caca1c1068344abcc` | none | True | True |
| 55 | toy35/fx_planted0_raw_u | `7b2d971242c22d94207cf14205d39a5252e38c83a81784e68da19cb515b87026` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_planted0_raw_u | 2 (agree) | ok | - | 0 | 384 | param | 384 | True | 24 | 24 | `836e8872167ad4a395c211bc2d8191054860a592a18a1c68d54eb66d6d964571` | none | True | True |
| 56 | toy35/fx_planted0_raw_x | `3c9855ee4ad2ec8e75cec4833c67e9c12c21f40ad604dc4c70cc708dfa87b7c7` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_planted0_raw_x | 2 (agree) | ok | - | 0 | 384 | param | 384 | True | 6 | 6 | `f084528a4ddbd47676e97833fe82e743f6334da47a716b6e407ce66b53d43edf` | none | True | True |
| 57 | toy35/fx_planted0_torsion_S3_norm | `4a2734dc2c2f335c91fffb5967bbe33b9939a5235dc81301f2fcea2c04a85248` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_planted0_torsion_S3_norm | 2 (agree) | ok | - | 0 | 64 | param | 64 | True | 1 | 1 | `d924008476275813b5bb30e72d685135d9daf5ed8a3aa85f533f39687c00ae0e` | none | True | True |
| 58 | toy35/fx_planted0_torsion_S3_rq | `49eb0b2170e78082e0f215c53ed7c81fb171fd0254fa55f1883c2a7515bc9356` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_planted0_torsion_S3_rq | 2 (agree) | ok | - | 0 | 16 | param | 16 | True | 1 | 1 | `6e0b9380b0703cc4321dc777ef33faec84ab260f9c8bec68d287bb7856896eed` | none | True | True |
| 59 | toy35/fx_planted1_S3 | `9d782351728a9c7010c2a2ee39e621d42a6ef1f75f9583ffe204f412a9055fd5` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_planted1_S3 | 2 (agree) | ok | - | 0 | 64 | param | 64 | True | 1 | 1 | `ba0b7bad4c2e25977ca15c9b8ddfd572366383ccacbd9908ba50ef67828f2b57` | none | True | True |
| 60 | toy35/fx_planted1_S3_rescaled | `bc2f6065bfc155817c55593e06efe83283c76deffbfa63db0e77064d9989e4b2` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_planted1_S3_rescaled | 2 (agree) | ok | - | 0 | 64 | param | 64 | True | 4 | 4 | `45979ca411c7c8d024559d60a82fc149a3a998d2b0234e26467c51b0d82e0bbb` | none | True | True |
| 61 | toy35/fx_planted1_raw_u | `a58b0f283ef5a1ced6897707bae96394bd62929044d165b9486d8f5ce3b28677` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_planted1_raw_u | 2 (agree) | ok | - | 0 | 384 | param | 384 | True | 24 | 24 | `76458e8d80d33d1782d8ff04b203f99fda02b9d397693c131db400f1b67331a2` | none | True | True |
| 62 | toy35/fx_planted1_raw_x | `b9bc99f4a96c79d47f913b1e9bdab921a7335348511158260dad51d8e618ae8e` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_planted1_raw_x | 2 (agree) | ok | - | 0 | 384 | param | 384 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 63 | toy35/fx_planted1_torsion_S3_norm | `b6a14a7a31ce7fd31c1a3f63f29e8045a8840c4e607df8cb14a4f948080eac10` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_planted1_torsion_S3_norm | 2 (agree) | ok | - | 0 | 64 | param | 64 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 64 | toy35/fx_planted1_torsion_S3_rq | `1f2b7f6c1bd94f0136fd8d8776fbdba4579ea3ca587f87ac60bdc584a418e2cf` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_planted1_torsion_S3_rq | 2 (agree) | ok | - | 0 | 16 | param | 16 | True | 1 | 1 | `74f36f7f77415262ac91dcf93af4dc1b8a9c93ee247f40a4fb478d18b5de8a56` | none | True | True |
| 65 | toy35/fx_reg0_S3 | `b7c2aec257a4fffd5dc25b54f3bff2e0160cd31141ca407fb5f31f4b96192be7` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_reg0_S3 | 2 (agree) | ok | - | 0 | 64 | param | 64 | True | 1 | 1 | `3b752aa099d29d625a820e06cd4774ece63ba147e8744cfa67a9a41ffcbee358` | none | True | True |
| 66 | toy35/fx_reg0_S3_rescaled | `ade0308b662b0dda9b3b8dbba5f3f6e417de495c9bb76bf1480787e1f1c7ff92` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_reg0_S3_rescaled | 2 (agree) | ok | - | 0 | 64 | param | 64 | True | 3 | 3 | `851bfcf46325d1d4abf0bc89dfaf8dcd133c1e785e28142e0aab016a962ff008` | none | True | True |
| 67 | toy35/fx_reg0_raw_u | `78ce47f76a789d2c94ae5ae660b26cf86dc6d38f1c19d0b01e356554bb55677b` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_reg0_raw_u | 2 (agree) | ok | - | 0 | 384 | param | 384 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 68 | toy35/fx_reg0_raw_x | `84c80057e5146ce4d129015b1e7fbe49bddb2e5d5aa0a8689d0c792dc4fe5f39` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_reg0_raw_x | 2 (agree) | ok | - | 0 | 384 | param | 384 | True | 6 | 6 | `e0a08eafe499769e53412b5fd92c939f7ba9b00391c52c6d5084b58b7ded9430` | none | True | True |
| 69 | toy35/fx_reg0_torsion_S3_rq | `4baa667bbef5d9f6a730dcf49c406d172503122f9723817e80684f49c1c8b2b2` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_reg0_torsion_S3_rq | 2 (agree) | ok | - | 0 | 16 | param | 16 | True | 2 | 2 | `60daa21e3bbd9016c25bf771cb542225ec0e1982442e190f034f8973e71647ae` | none | True | True |
| 70 | toy35/fx_reg1_S3 | `c6ffbdf1146238410dc091cdc83131ba6a9beeb88c79de63856c8d0815cd76cf` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_reg1_S3 | 2 (agree) | ok | - | 0 | 64 | param | 64 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 71 | toy35/fx_reg1_S3_rescaled | `6e005f1b4b378e022bf1246ec9aa676993289c3379ef27df7e1b0644fc36c4ea` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_reg1_S3_rescaled | 2 (agree) | ok | - | 0 | 64 | param | 64 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 72 | toy35/fx_reg1_raw_u | `4a0aacd842bdc525ebdb3fadcda72b5f24a0716562beab55fca7e63b4b5f6d3a` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_reg1_raw_u | 2 (agree) | ok | - | 0 | 384 | param | 384 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 73 | toy35/fx_reg1_raw_x | `a6187802ea6fed6dd2d653d000e7edbe48a0e9ac549fb6f0d309effbfa74c112` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_reg1_raw_x | 2 (agree) | ok | - | 0 | 384 | param | 384 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |
| 74 | toy35/fx_reg1_torsion_S3_norm | `64f7fe95d895cd7db4ca7ac01cbbf9946ab9a8e2f3e586bcee74605f4eff4cd9` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_reg1_torsion_S3_norm | 2 (agree) | ok | - | 0 | 64 | param | 64 | True | 1 | 1 | `b6f44352374fe6278116017944d190be6857b274240c63c579267b3d53894a48` | none | True | True |
| 75 | toy35/fx_reg1_torsion_S3_rq | `4bdba858f22099c35f9d3806141438043835b3645f914a87f4cc701ddcf10093` | bundle toy world_B RUN-GFPN-a61a10 solver/fx_reg1_torsion_S3_rq | 2 (agree) | ok | - | 0 | 16 | param | 16 | True | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | none | True | True |

### A4. PR-2 (d): the 36 archived RUN-GFPN-ac4487 outputs against raw-result.json

| tag | output sha256 | outcome | n_sub_fail | D (this check) | D (raw-result.json) | raw-result outcome / substitution_failures | #rat. sol. (this / raw-result) | holds |
|---|---|---|---|---|---|---|---|---|
| fx_fresh1_S3 | `60a4cd6e4607259325080b558c7e01a27e61509d74ba382d33e13ab299afc9cf` | ok | 0 | 64 | 64 | ok / 0 | 3 / 3 | True |
| fx_fresh1_S3_rescaled | `efb50e2ef8c6553e46d3aaa4b7422a9aa2aa996292d0ac77736ddcd0d4a474af` | ok | 0 | 64 | 64 | ok / 0 | 6 / 6 | True |
| fx_fresh1_raw_u | `913635c67f3d3d1a2606e39552302a14dad741b3588c96f88fab96ccc692eeb4` | ok | 0 | 384 | 384 | ok / 0 | 24 / 24 | True |
| fx_fresh1_raw_x | `7dc2c544bc5d015fcda4041b343c2282498394ee01fc434b909ac0b1674ebddb` | ok | 0 | 384 | 384 | ok / 0 | 6 / 6 | True |
| fx_fresh1_torsion_S3_norm | `efb572acc1a06f1f27c0eb6394affe8b5512d4577e8f22cbe6a640fd435f84f9` | ok | 0 | 64 | 64 | ok / 0 | 2 / 2 | True |
| fx_fresh1_torsion_S3_rq | `7a89173a15d12c5b12dd96287ca8ddd27fb1d11a10dcfb43e7dcce1f55f529d8` | ok | 0 | 16 | 16 | ok / 0 | 2 / 2 | True |
| fx_fresh2_S3 | `eca772970934e5a5119c9f4a12552806996c04a5ac08f494b2558aec3872a064` | ok | 0 | 64 | 64 | ok / 0 | 0 / 0 | True |
| fx_fresh2_S3_rescaled | `ac26fa0bd1d18e170df2dc7f9e2cc870777bec1eaf6bfb94d1751abb1a551905` | ok | 0 | 64 | 64 | ok / 0 | 2 / 2 | True |
| fx_fresh2_raw_u | `12c4b747e3b2a426cd041c3df4c75abee4a3f543d280ab7b8b86392636e6a9e0` | ok | 0 | 384 | 384 | ok / 0 | 0 / 0 | True |
| fx_fresh2_raw_x | `7a3c217d2f436c65f8f4e0ae846486fb39cc56d23a8deebb50fee746ce13da31` | ok | 0 | 384 | 384 | ok / 0 | 0 / 0 | True |
| fx_fresh2_torsion_S3_norm | `2ebac156e566bc1d677176160a288dff485291b267280096ad88d7923815ea42` | ok | 0 | 64 | 64 | ok / 0 | 0 / 0 | True |
| fx_fresh2_torsion_S3_rq | `b564bab4afdff3fc1b82867cf514b98e062cad47435c5ba8fa26c9cb4fdf6a71` | ok | 0 | 16 | 16 | ok / 0 | 2 / 2 | True |
| fx_planted0_S3 | `5a5c3ade3fade8acf12e33e0a7dfb7a603f6412f32518ea54e3ce56913c07dd4` | ok | 0 | 64 | 64 | ok / 0 | 0 / 0 | True |
| fx_planted0_S3_rescaled | `e0b8706cb48594fa3f12e17e7979416404e27500091c34cd0b462a3d0ac95c94` | ok | 0 | 64 | 64 | ok / 0 | 8 / 8 | True |
| fx_planted0_raw_u | `fa43416ce9f92ff8f786242cab468295ba5434a3cb8ca404a5ee56ef6c4e0dd9` | ok | 0 | 384 | 384 | ok / 0 | 48 / 48 | True |
| fx_planted0_raw_x | `4979535ed24c467ad728e2cc02a4db146b1f675ed4770ef5b38ff26380c6a87d` | ok | 0 | 384 | 384 | ok / 0 | 0 / 0 | True |
| fx_planted0_torsion_S3_norm | `4b64be0be57b1998517596d551497c8471c9316d45d023e39d86390a87347cdb` | ok | 0 | 64 | 64 | ok / 0 | 0 / 0 | True |
| fx_planted0_torsion_S3_rq | `88f25f454f5270af5b8126d00131e673fce14b1d8870252ee311af3fe7f779dc` | ok | 0 | 16 | 16 | ok / 0 | 2 / 2 | True |
| fx_planted1_S3 | `d697a8abefa7732512558046b0049fc85abfd8ca25333e81b58db4efd1d7a199` | ok | 0 | 64 | 64 | ok / 0 | 0 / 0 | True |
| fx_planted1_S3_rescaled | `811679d46e3b0ff196a915edd119479a67247e1ae5c579dd5409b0b8fa1dd770` | ok | 0 | 64 | 64 | ok / 0 | 4 / 4 | True |
| fx_planted1_raw_u | `e2560125e6aaabe22bff55f9335cdf00c23d320059be38751ae4fed8ddae4485` | ok | 0 | 384 | 384 | ok / 0 | 24 / 24 | True |
| fx_planted1_raw_x | `a8d0557e35dd8e65716eb2476e39f68bfb4bbd21296a3de6d889b68366443612` | ok | 0 | 384 | 384 | ok / 0 | 0 / 0 | True |
| fx_planted1_torsion_S3_norm | `aaadd08c36eb7f577dcd5bd5c650d39c58d78536f2cd546ec295480a13e107d2` | ok | 0 | 64 | 64 | ok / 0 | 0 / 0 | True |
| fx_planted1_torsion_S3_rq | `4a2ffb7100cc81cda0ad321f870c436d792c7aa7bcfc89a05ffa4d68ce741a35` | ok | 0 | 16 | 16 | ok / 0 | 1 / 1 | True |
| fx_reg0_S3 | `53293037cd7354f974b11d01ce909733b57df7fe1478ca4c25e152ed5f2ddfca` | ok | 0 | 64 | 64 | ok / 0 | 1 / 1 | True |
| fx_reg0_S3_rescaled | `6ea8b0e8d7fc75a29a7f3cd2d54150f0ce4d469745cd5ae6eb252dcf0eb0c7f5` | ok | 0 | 64 | 64 | ok / 0 | 0 / 0 | True |
| fx_reg0_raw_u | `728ecf36505ecee018f828d3b19827920f9d8479db13b0845d1eb986ca079a62` | ok | 0 | 384 | 384 | ok / 0 | 0 / 0 | True |
| fx_reg0_raw_x | `a87355d97a2f48702cffbba36beed08523bb28ffef2b0a139c7d39278adddd61` | ok | 0 | 384 | 384 | ok / 0 | 0 / 0 | True |
| fx_reg0_torsion_S3_norm | `606fc541d777720d9cc9992a67618ef71f922154f864b9643a7f78eea7d3e3c0` | ok | 0 | 64 | 64 | ok / 0 | 1 / 1 | True |
| fx_reg0_torsion_S3_rq | `43b940e706031a9c2b1e9a041dbaecbf0d9013deab86e5489dbbda2c8f6e27f9` | ok | 0 | 16 | 16 | ok / 0 | 0 / 0 | True |
| fx_reg1_S3 | `1f2628d960a8e77cc256f5156b415aa50d7a90b2d3c79b5da9a022a135ecf36b` | ok | 0 | 64 | 64 | ok / 0 | 0 / 0 | True |
| fx_reg1_S3_rescaled | `3b232b2b6557c13f66b535c876249edc85c0bdaa117390b05d426d12752a15f2` | ok | 0 | 64 | 64 | ok / 0 | 0 / 0 | True |
| fx_reg1_raw_u | `e57c788f1f63c4cab8ff56a6795b451b2dc9e3e5e792951fee9e16899f73af33` | ok | 0 | 384 | 384 | ok / 0 | 0 / 0 | True |
| fx_reg1_raw_x | `5f44e62678ce87698fd3455ae9509713c194caa703829b25b91c484e6ad63733` | ok | 0 | 384 | 384 | ok / 0 | 0 / 0 | True |
| fx_reg1_torsion_S3_norm | `efc90355062318d531bd6f411513e5988cb24d6b94dd2f3ab53035d70882e807` | ok | 0 | 64 | 64 | ok / 0 | 2 / 2 | True |
| fx_reg1_torsion_S3_rq | `840f544d9da36243a573c4810188d27c47f7bb56f3cd7b4aac11a7501594299b` | ok | 0 | 16 | 16 | ok / 0 | 0 / 0 | True |
