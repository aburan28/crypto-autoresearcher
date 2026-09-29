# EXP-PFDR-4bfc6f -- implementation note (PRE-FLIGHT BLOCKER REPORT)

Handoff: TASK-20260903-06b269 (Coordinator -> Executor). Contract:
`experiments/EXP-PFDR-4bfc6f/specification.yaml` (status `approved`,
`approved_by: coordinator`, `approved_at: 2026-09-03`, committed in
`c57429694af615f64d2e691a0df25e1b131f4875`). Hypothesis H-PFDR-e02f3b,
proposal IDEA-20260903-751062.

**Outcome of this dispatch: `failed_infrastructure` at pre-flight.** Sage is
absent from the execution container and cannot be installed from it. The
contract (inputs.sage, invalidation rule 1, approval_note) and the handoff
(constraint 1) both say that Sage missing at dispatch is
`failed_infrastructure`, reported "without any cell being read". No run was
attempted, so no run directory exists under `runs/` (a run directory is only
written by the wrapper for an actual attempt). Nothing below is evidence about
the mechanism, the hypothesis, or any archived signal (AGENTS.md rule 5: a
crash, timeout or implementation failure is not evidence against a
mathematical hypothesis; contract invalidation rule 1).

Written by this dispatch: this file and `execution-report.yaml` only. Nothing
outside `experiments/EXP-PFDR-4bfc6f/` was touched; no record, contract,
hypothesis or archived ALPF artifact was edited; no git command that changes
state was run (read-only `git rev-parse`, `git status`, `git log`,
`git ls-files`, `git merge-base` only).

## 1. Pre-flight: contract validation

| check | result |
| --- | --- |
| `specification.yaml` status | `approved` |
| `approved_by` | `coordinator` (DEC-20260903-93862f) |
| spec committed | yes; last commit touching it `c57429694af615f64d2e691a0df25e1b131f4875` (2026-09-03 19:42:47 +0000) |
| handoff committed | yes, same commit |
| required inputs / controls / metrics / budgets / stopping rules / artifacts | all present in the contract (sections `inputs`, `controls` x10, `metrics`, `budget`, `stopping_rules` x3, `required_artifacts` x7) -- no `specification_error` |
| executing revision | HEAD `aaa7f5bb419de11734f8cba6512fdd1b3436b2a7`, branch `claude/degree-regularity-polynomial-systems-pssesi`, `git status --porcelain` empty (dirty-tree count 0) before this dispatch wrote its two files |

### Meter prerequisite (handoff constraint 1, contract inputs.meters (ii))

`harness/macaulay_fp/` exists at a committed path; last commit touching it
`2d2083e59edab14fe4ac4a42d777b1aa5be867b8` ("tooling(TASK-20260903-ba41aa):
F_p Macaulay deficit meter harness/macaulay_fp with 52 tests and validation
note"), which is an ancestor of HEAD (`git merge-base --is-ancestor` = yes).
`python3 -m pytest tests/test_macaulay_fp.py -q` -> `52 passed in 2.21s`
(exit 0). The `TASK-20260903-ba41aa` handoff record still carries
`archived_by: null`; whether its snapshot archive receipt has verified is a
Coordinator-side fact this session cannot confirm from the working tree and is
recorded here as **not confirmed by the executor** (it is moot for this
dispatch because the Sage blocker stops the task before that gate matters).

Per-file sha256 of the meter at HEAD (would have gone into every manifest):

```
6207f0c89901ffe1ab1334257405e4b95cc48da7953afabb14eea4c8f9028bef  harness/macaulay_fp/VALIDATION.md
3f1ed1fc59f8b059fab94ba4f61716dcacefbda26f5598ec3aef79818b28630f  harness/macaulay_fp/__init__.py
b9725c1c2ac51ddd1ef250f7608047d0bc4d5e441c48ae667c3ebec037a75a62  harness/macaulay_fp/columns.py
fdf94aaedc0c3de3e7b96a3d13835227f40d8be8d782ce81b03f4c1498b5cbfa  harness/macaulay_fp/koszul.py
9f77e14f5264878ef490f1d4b4d534f04c32880733b5c1c859995997c6accd1a  harness/macaulay_fp/linalg.py
97be3005d955cb1be9079864276feba6c3542c72a6b01a5dae6b042a1dab62ea  harness/macaulay_fp/localization.py
d1ba2f75e1f479549d6e10a03b6fefb882446c957eecba0250945fe14d31937f  harness/macaulay_fp/macaulay.py
07121755f8d85d5c2bf9851276833614d45a3cfd9a7a8957874e9495e51c81be  harness/macaulay_fp/nulls.py
0490eb22e944872c2214eb7a10fd37d0641346aefdf392786533e1c66756af1e  harness/macaulay_fp/poly.py
d846300dd70893013fd6a93593d3073436555104a25598f6839d801025f47db1  harness/macaulay_fp/presentations.py
ae1d5a333782b6c29c6dfb84923c9e1f24290ca0d1709f231d8b1d1496b0288c  harness/macaulay_fp/series.py
```

## 2. Pre-flight: Sage availability (verbatim)

Executed 2026-09-03 in the execution container (Linux vm 6.18.44-fc-v24
x86_64, 4 cores shared with one other executor, Python 3.11.15, numpy 2.4.6,
sympy 1.14.0).

```
$ which sage
(no output)                       exit=1
$ sage --version
/bin/bash: line 1: sage: command not found
                                  exit=127
$ command -v sage
(no output)                       exit=1
$ python3 -c "import sage.all"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'sage'
                                  exit=1
$ which gp
(no output)                       exit=1
$ apt-cache policy sagemath
sagemath:
  Installed: (none)
  Candidate: (none)
  Version table:
$ pip index versions sagemath-standard
sagemath-standard (10.7)
Available versions: 10.7, 10.6, 10.5, 10.4, 10.3, 10.2, 10.1, 10.0, 9.8
$ pip download --no-deps -d <scratchpad>/sagedl sagemath-standard
  ... (build-isolation step for the cypari2 build dependency) ...
            running egg_info
            writing cypari2.egg-info/PKG-INFO
            writing dependency_links to cypari2.egg-info/dependency_links.txt
            writing requirements to cypari2.egg-info/requires.txt
            writing top-level names to cypari2.egg-info/top_level.txt
            error: cannot find an installation of PARI/GP: make sure that the 'gp' program is in your $PATH
            [end of output]
        note: This error originates from a subprocess, and is likely not a problem with pip.
      error: subprocess-exited-with-error
      x Getting requirements to build wheel did not run successfully.
      | exit code: 1
  note: This error originates from a subprocess, and is likely not a problem with pip.
error: subprocess-exited-with-error
x pip subprocess to install build dependencies did not run successfully.
| exit code: 1
                                  exit=1
$ pip list | grep -i -E "sage|cypari|pari|flint|gmpy|galois"
(no output)
$ command -v conda; command -v mamba; command -v micromamba
(no output)                       exit=1
```

Conclusion of the check: no Sage binary, no `sage` Python package, no PARI/GP
(the sdist build of `sagemath-standard` fails at its `cypari2` build
dependency for that reason), no apt candidate, no conda. Installing Sage is
outside this task's write scope and not achievable from this container in
any case.

## 3. Archived files that require Sage

The contract names these builders/meters to be executed **as archived,
unmodified** (contract inputs.builders; handoff constraint 5: "The archived
builders are run UNMODIFIED at seed 42 for the archived cells"). All four are
`.sage` files using Sage-only globals (`set_random_seed`, `load()`,
`PolynomialRing`, `GF`, `EllipticCurve`, `.groebner_basis()`, ...) and cannot
be executed by CPython. sha256 pinned at HEAD `aaa7f5bb`:

| file | sha256 | role in contract | Sage-only? |
| --- | --- | --- | --- |
| `experiments/EXP-ALPF-011/source/round006_exp010_validated_resweep.sage` (813 lines) | `02f9bd574320a3c01ad34f4f3ee7734eda5d03794bfe41cbaf6b5ee58ddb02f8` | THE exact e-ring / power-sum / x-ring builders (`build_S4_poly` l.197, `rewrite_S4_in_e_coords` l.215, `build_fb_constraints_e_ring` l.253, `rewrite_S4_in_powersum_coords` l.263, `build_fb_constraints_powersum` l.299, `run_sweep` l.381); the CTRL-ARCHIVE-REPRODUCTION run and every Stage 2 cell | yes (`#!/usr/bin/env sage`; `set_random_seed`, `load()`) |
| `experiments/EXP-ALPF-009/source/round005_exp008_fixeddeg_fb.sage` (1193 lines) | `539a97f4574b4e4ccce2af70fa4131199a885d25b6586ec49298e7d49ba713c8` | round005 inline-meter copy (`top_form` l.56, `macaulay_homog` l.63, `trivial_koszul` l.84, `semireg_Dreg` l.91, `meter` l.101, `validate_meter` l.128) -- Stage 1 inline-meter reconstruction source | yes |
| `experiments/EXP-ALPF-010/source/round005_exp009_crossbred.sage` (900 lines) | `6689a875c127c963c8dea974245235ed135d578eb55ffb2625e8aa9ed15af9c9` | round005 inline-meter copy (`top_form` l.220, `macaulay_homog` l.228, `trivial_koszul` l.253, `semireg_Dreg` l.260, `meter` l.271, `revalidate_meter` l.311) -- Stage 1 source | yes (`#!/usr/bin/env sage`) |
| `experiments/EXP-ALPF-013/source/round007_exp012_localization_gate.sage` (685 lines) | `5618df8c3e090d75b4349ab321e9f3ff971aa2d37be3354fcbcc8e4d9105d612` | `meter_local` l.192, `meter_gated` l.341 (localization / shrink test), `build_POSC_weil_S3` l.503, `build_synthetic_gate_POS` l.543 -- Stage 1 source and POS-C-WEIL-S3 control | yes |

Companion archived result files (read-only inputs; pinned, not executed):

```
ce1d89892dd68ffabb29c2247877657ea490a1b5905e075d8fdcbbe1c78cd54e  experiments/EXP-ALPF-011/source/round006_exp010_validated_resweep.log
04d613062342c7faf781962fbf726825ef8efc7de6bc425f70104d1070fc5da6  experiments/EXP-ALPF-011/source/round006_exp010_validated_resweep_result.json
fba2460f174a78d04f230a2348562a76b8d78e18d4152020b777d72ddf664871  experiments/EXP-ALPF-011/source/round006_exp010_validated_resweep_result.md
3f919ea0085d4d3a5577f9570b7cc10a3588e0a827b41d4683acc72668206468  experiments/EXP-ALPF-013/source/round007_exp012_localization_gate.log
99f256f0a2ff7bbc13ff918b597a857e8b17ccc3393658900aebe358b0b0c026  experiments/EXP-ALPF-013/source/round007_exp012_localization_gate_result.json
016865d1d9a0ef3b4a6ac32e1ae90bbf013039e69908da5d38a636f15ba0cffe  experiments/EXP-ALPF-013/source/round007_exp012_localization_gate_result.md
75a9e88dc6e07c8ded106b73146d13cdd34ecfdf3919a072ba927d801471758e  experiments/EXP-ALPF-009/source/round005_exp008_fixeddeg_fb.log
5e28fff1654aba05bdd2c5aa45578f958b3f1a67574efad6a06a5f368cc84bbb  experiments/EXP-ALPF-009/source/round005_exp008_fixeddeg_fb_result.json
5ec98b7cf22d4da9b051360cbb40b58e707f56f8dc290f04682d4f4ecdfe5515  experiments/EXP-ALPF-009/source/round005_exp008_fixeddeg_fb_result.md
97ec25326dda715efdb22ca8bcc182e058dd5623420b6974e650cca81ee4e0be  experiments/EXP-ALPF-010/source/round005_exp009_crossbred.log
97ec25326dda715efdb22ca8bcc182e058dd5623420b6974e650cca81ee4e0be  experiments/EXP-ALPF-010/source/round005_exp009_crossbred.stdout
f47d52186333c7d0e1dfb6dcd5ba48fe4489cc0269e2c51348cfe7be9db385d1  experiments/EXP-ALPF-010/source/round005_exp009_crossbred_result.json
52df8295792773011d85e03ecd2f270a32a8e763e75dbe9ca0c507910bc73009  experiments/EXP-ALPF-010/source/round005_exp009_crossbred_result.md
```

### Can any planned run or control be executed faithfully without Sage?

No. Reasoning against the contract's own rules, not a judgement call:

- **CTRL-ARCHIVE-REPRODUCTION (blocking)** requires the archived cells to be
  regenerated by the *unmodified* `round006_exp010_validated_resweep.sage`
  at seed 42 and read by *both* meters. The systems the meters read are
  produced by that Sage file (`build_S4_poly` calls Sage's Semaev / curve
  machinery; `set_random_seed(42)` fixes Sage's RNG for the curve and FB
  draws). A Python re-implementation of the builder would be a different
  builder and could not be called "the archived builder" (handoff
  constraint 5); the contract's F1 falsification ("the exact builders do not
  reproduce") would become untestable. Blocked.
- **Stage 1 inline-meter cross-check** (POS-A / NEG-1 / NEG-2 and the 48
  archived cells): the inline meter is a Sage-native reconstruction from the
  `.sage` sources above (contract inputs.meters (i)), and CTRL-METER-CROSSCHECK
  (blocking) requires it to run on every cell. Blocked.
- **The F_p port alone** (`harness/macaulay_fp`, pure Python) *does* run
  here, but the contract forbids reading any cell with one meter only
  (invalidation rule 3: a cell is void until both meters agree), and the
  cell inputs themselves come from the Sage builders. Running the F_p port on
  a Python-reconstructed system would be a one-meter reading of a
  non-archived object -- exactly the reconstruction the contract was written
  to replace. Not done.
- **Stage 2 ladder** (15 (|FB|, p) cells; NULL-S4, NULL-FB, CTRL-GENERIC-TWIN,
  POS-C-WEIL-S3, CTRL-TARGET-ARM with Groebner-based Q1 / vdim, the 200-target
  enumeration, the weighted-grading arm): every arm builds its system with the
  archived Sage builders and Q1 / vdim need Sage Groebner calls. Blocked; also
  gated behind the Stage 1 stopping rule, which cannot be evaluated.
- **Stage 0 (zero compute)** and **Stage 3 (zero compute)** are not blocked
  by Sage as such. They were **not started** by this dispatch because the
  contract and handoff make a missing Sage a `failed_infrastructure` outcome
  *at dispatch* "without any cell being read", and the handoff's return
  format binds all deliverables to one execution batch. `stage0-predictions.yaml`
  in particular is defined as "frozen before any run; sha256 in every
  manifest" -- writing it in a dispatch with no run and no manifest would leave
  a frozen file whose provenance the re-dispatch inherits rather than
  authors. Deferred to the re-dispatch in a Sage-capable runtime; this is an
  executor choice and is recorded as such (deviation D2 below) so the
  Coordinator can direct otherwise.

Therefore: **zero cells read, zero runs attempted, zero run directories.**

## 4. Blocked cells (by name)

Archive-reproduction run (CTRL-ARCHIVE-REPRODUCTION, 16 + 16 + 16 = 48
readings at seed 42) -- the 16 archived cells of
`round006_exp010_validated_resweep_result.json` (`cells[]`, keys `family`,
`bits`, `p`, `a`, `n_fb`), each read in reps `A_xring`, `B_ering`,
`C_powersum`:

| family | bits | p | a | |FB| |
| --- | --- | --- | --- | --- |
| structured | 13 | 4111 | 4108 (= -3) | 4, 5 |
| structured | 15 | 16417 | 16414 | 4, 5 |
| structured | 17 | 65551 | 65548 | 4, 5 |
| structured | 19 | 262271 | 262268 | 4, 5 |
| random | 13 | 7993 | 967 | 4, 5 |
| random | 15 | 25639 | 8840 | 4, 5 |
| random | 17 | 111847 | 96977 | 4, 5 |
| random | 19 | 420439 | 269089 | 4, 5 |

(The archive also carries reps `D_phi_t2`, `D_phi_t2c`; the contract does not
list them among the 48 and they are not planned.)

Stage 1 controls: POS-A, NEG-1, NEG-2 on both meters -- blocked.

Stage 2 ladder cells (one run each; all arms, curves, targets, gradings,
both meters): (|FB|, p) for |FB| in {4, 5, 6, 7, 8} x p in {13-bit archived,
17-bit new prime-order, 23-bit new prime-order} = 15 cells -- blocked, plus
any NULL-S4 escalation runs under stopping rule 2 -- not reachable.

## 5. Pre-flight observations (non-mathematical; recorded for the Coordinator)

These are things noticed while pinning inputs. None is a measurement and none
bears on M1-M4. They are listed so the re-dispatch does not rediscover them.

- **O1 (absent-file finding, confirmed at the file level).** No file named
  `round005_meter_validation*` exists anywhere under `experiments/`
  (`find experiments -name 'round005_meter_validation*'` -> nothing). It is
  referenced by `EXP-ALPF-011/source/round006_exp010_validated_resweep.sage`
  l.57/l.99, `EXP-ALPF-013/source/round007_exp012_localization_gate.sage`
  l.35/l.63, `EXP-ALPF-010/source/round005_exp009_crossbred.sage` (comments
  l.26, l.274), and by EXP-ALPF-012/-014/-025 sources. The contract already
  anticipates this (inputs.meters (i)); this dispatch confirms it without
  executing anything.
- **O2 (consequence of O1 for "run unmodified").** The archived EXP-ALPF-011
  builder does `load(METER_SRC)` inside `try/except` and **re-raises** on
  failure (l.98-104: `log("  FATAL: could not load meter: ..."); raise`).
  Run byte-for-byte unmodified, even under Sage, it aborts before
  `run_sweep()` because the meter file is absent. EXP-ALPF-013 instead
  guards with `os.path.exists(BASE_METER)` and falls back to its inline
  primitives (l.59-65). The re-dispatch will need a Coordinator ruling on
  how "unmodified" is to be satisfied for ALPF-011 (e.g. a wrapper that
  places the reconstructed meter at `METER_SRC`, or an amendment); this
  dispatch did not decide it.
- **O3 (hard-coded paths).** All four `.sage` files write logs / JSON / MD to
  the absolute directory `/Volumes/Volume/autolab/experiments/ecdlp_prime_field`
  (ALPF-011 l.56-60; ALPF-013 l.34-37; ALPF-009 l.24-27). An unmodified
  execution requires that directory to exist and be writable in the
  Sage-capable runtime, or a wrapper-level path arrangement; same ruling
  as O2.
- **O4 (archived Sage version).** The imported `environment.json` and
  `manifest.yaml` of RUN-ALPF-009/-010/-011/-013-import all carry
  `sage_version: null` (`import_mode: historical_artifact_port`,
  `source_commit: dca04ac33e9ffcfc51edb3ae7e7bd558b1962d95`). The only
  version string in the archived logs is in
  `EXP-ALPF-010/source/round005_exp009_crossbred.log` l.3:
  `sage=SageMath version 10.9, Release Date: 2026-05-04` (run started
  2026-05-30 23:13:13). The EXP-ALPF-011 log (started 2026-05-30 23:43:48,
  same day, same source commit) records **no** version string; the
  ALPF-011 builders' Sage version is therefore **not recorded**, and
  "SageMath 10.9" is the best available neighbour, not a record.
- **O5 (listing discrepancy in an archived note).**
  `experiments/EXP-ALPF-011/implementation.md` l.16 lists
  `source/round006_exp010_validated_resweep.sage.py`; that file is not in the
  working tree and not in `git ls-files`. Not edited (archived artifact);
  reported.
- **O6 (prime named by the contract versus the archive).** The contract's
  ladder (inputs.ladder) and CTRL-P-INDEPENDENCE name `p = 4079` as "the
  archived 13-bit Solinas a = -3 curve". The archived 16-cell sweep's 13-bit
  cells are `p = 4111` (structured, a = -3) and `p = 7993` (random). `4079`
  appears in the archive only in the section-8 discriminator probe
  (`round006_exp010_validated_resweep_result.md` l.208, run from
  `/tmp/exp010_ering_probe.sage`, which is not archived). Which p the
  13-bit ladder column is meant to carry -- 4079 (the probe) or 4111 (the
  sweep) -- is a question for the Coordinator before the re-dispatch; a
  protocol_amendment may be needed. This dispatch changes nothing.

## 6. Protocol deviations

- **D1 (blocker).** Sage unavailable at dispatch -> `failed_infrastructure`
  at pre-flight; no stage executed; no run attempted. Per contract
  invalidation rule 1 and handoff constraint 1 this is the prescribed
  disposition, not a departure from it; it is listed as a deviation because
  the planned runs did not happen.
- **D2 (executor choice).** Stage 0 and Stage 3 (zero-compute deliverables
  `stage0-derivation.md`, `stage0-predictions.yaml`,
  `evidence-supersession-draft.md`) were not started; see Section 3 for the
  reason. Not written: `stage0-derivation.md`, `stage0-predictions.yaml`,
  `analysis.md`, `evidence-supersession-draft.md`, `runs/`.

## 7. Inference block (as recorded in `execution-report.yaml`)

`requested_policy: executor-implementation`, `requested_reasoning_effort:
medium` (handoff). `python3 -m orchestration.adapter resolve --role executor`
-> `executor-implementation -> anthropic:claude-sonnet-5 (effort=medium)`.
The runtime's self-reported model identifier for this session is
`claude-fable-5-1`, which differs from the adapter-resolved binding. No
`AUTORESEARCH_POLICY` / `AUTORESEARCH_BACKEND` environment variables were set
in this session, so `harness/runner.py`'s manifest writer had nothing to
bind to. `model_verified: false` (no probe was run by this session);
`fallback_used` is recorded as **undeterminable by this session** (`null`),
with both identifiers stated so the Coordinator can resolve it against the
launch environment. No Bedrock; no degraded requirement was accepted by
this session.

## 8. What would unblock this contract

1. A Sage-capable runtime (SageMath binary on PATH so that `sage
   <file>.sage` runs; PARI/GP present). The archive's nearest recorded
   version is SageMath 10.9 (2026-05-04) from the EXP-ALPF-010 log; the
   ALPF-011 builders' own version is unrecorded (O4).
2. `harness/macaulay_fp` reachable in that runtime at commit
   `2d2083e59edab14fe4ac4a42d777b1aa5be867b8` or later with
   `tests/test_macaulay_fp.py` passing (52/52 here), and the
   TASK-20260903-ba41aa snapshot receipt verified.
3. A Coordinator ruling (or protocol_amendment under
   `experiments/EXP-PFDR-4bfc6f/amendments/`) on O2 / O3 (how the unmodified
   ALPF-011 builder is to be run given its fatal `load()` of the absent
   meter file and its absolute output paths) and on O6 (which 13-bit p is
   "the archived" one).
4. A fresh executor handoff; this task (`TASK-20260903-06b269`) terminates
   as `failed_infrastructure` with no run record.
