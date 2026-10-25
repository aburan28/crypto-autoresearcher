# Lean/Lake file reads on the external APFS volume fail intermittently with EINTR, blocking the formal gate

- **Status:** `open`
- **Kind:** access/tool limit (host filesystem behaviour); not a proof gap
- **Affected work:** `formal/targets/ic-arity-oracle-threshold-20261024.yaml`
  (`TASK-20261024-9fbb0f`, `formal/CryptoResearch/IC/ArityOracleThreshold.lean`);
  every `lake build` / `tools/verify_formal_targets.py` run on this host; the
  Lean status of IDEA-20261024-a2b05d (RQ-ECDLP-361f3a)
- **Next action owner:** unassigned (needs a host without the fault, or a root cause)
- **Last updated:** 2026-10-24

## Problem

We cannot yet record `machine_verified` for the arity/oracle-order theorem
because the repository's Lean gate (`lake build`, `lake env lean
AxiomAudit.lean`, `tools/verify_formal_targets.py`) does not run to completion
on the host that holds the checkout: Lake and `lean` report `Interrupted system
call` (EINTR, error code 4) on `open`/`read` of `.olean`, `.trace` and `.ir`
files under `formal/.lake/` on `/Volumes/SSD990-2` (APFS, PCI-Express NVMe,
mount flags `local, nodev, nosuid, journaled, noowners`). The failing file
differs on every run; the same files open and read without error from Python
(110,968 open+stat calls, 0 errors) and from `cat`.

## Evidence and uncertainty

- **Observed:** (toolchain `leanprover/lean4:v4.35.0-rc1`, Mathlib
  `7fa22735254ddf7e11f119250a9f2d0352bc7c3a`, cache `lake exe cache get`
  complete: 8536 `.olean` for 8536 Mathlib sources.)
  - `lake build` (2026-10-24, 9 min 41 s) ended `error: build failed` after
    listing Mathlib modules it tried to rebuild; `lake build --no-build`
    reports `read failed: interrupted system call (error code: 4)` on
    `Mathlib/CategoryTheory/Enriched/Limits/HasConicalProducts.trace`.
  - `lake env lean <file>` on a file importing `Mathlib.Tactic`: `failed to
    open file ... : Interrupted system call` on a different olean each run
    (`DSimpPercent.olean.private`, `Linter/Style.olean`,
    `Aesop/Forward/Substitution.olean`, `Order/OrderDual.olean`,
    `Topology/Metrizable/Basic.ir`, ...), inside and outside the Bash sandbox.
  - After the failed build `Mathlib/Logic/Basic.olean` is absent from the
    build tree while `lake exe cache get` reports it decompressed.
  - Plain `lean --threads=2` with `LEAN_PATH=$(lake env printenv LEAN_PATH)`
    on `formal/CryptoResearch/IC/ArityOracleThreshold.lean` (imports
    `Mathlib.Basic.Real.Basic` and six tactic modules) succeeds on 1 of 3
    attempts when the closure is large and on the first attempt after the
    import list was narrowed: exit 0, 0 errors, 0 `sorry`, every `#print
    axioms` line `[propext, Classical.choice, Quot.sound]`.
  - `git status` in the same checkout (19:25 PDT) printed `warning: could not
    open directory 'coordination/design/EXP-BINSTD-64f939/': Interrupted
    system call` and three more such lines, so the fault is not specific to
    Lean: any process that does not retry `EINTR` sees it on this volume.
    Python (which retries `EINTR` internally since PEP 475) and `cat` did not.
    A later `git fetch` reported `fatal: loose object 484693b3... is corrupt`
    once and succeeded on the retry; `git cat-file -t` reads the object fine.
  - `python3 tools/verify_formal_targets.py --artifact-dir <scratch>
    --build-timeout 1500` (22:26-22:40 PDT, stopped after 5 of about 90
    targets): every receipt, including targets that were `machine_verified`
    on earlier hosts (`CryptoResearch.Endosweep.AlphaAdic.*`,
    `CryptoResearch.Binstd.*`), reads `status: formalization_blocked`,
    `build_passed: False`, `blocking_reason: lake build failed`, with
    `Interrupted system call` in 4 of the 5 build logs and
    `infrastructure_failure: None`. On this host the gate's verdict measures
    the fault, not the proofs, and it would wrongly demote committed targets.
- **Derived or proved:** not established. The EINTR reaches `git` and
  Lean/Lake alike and never Python, which is consistent with a signal
  delivered to processes during slow directory/file reads on this volume and
  no `SA_RESTART` retry in the affected programs; the failure rate rises with
  the number of files opened.
- **Suspected explanation:** a signal delivered to the Lean processes while a
  slow read on the external volume is in flight, with no `SA_RESTART`
  retry; candidates are the harness's process supervision or a third-party
  file-monitoring agent on the host (CCleaner was running). Unverified.
- **Missing capability:** a host (or an internal-disk copy of `formal/.lake`,
  7.1 GB; the internal disk had 6.4 GB free) on which `lake build` completes.
- **What this evidence does not establish:** nothing about the theorem's
  correctness beyond the plain-`lean` compile; nothing about other hosts.

## What would unblock it

- [ ] `lake build` and `lake env lean AxiomAudit.lean` complete in `formal/`
      with `CryptoResearch.IC.ArityOracleThreshold` built, on any host, and
      `python3 tools/verify_formal_targets.py --artifact-dir <dir>` reports the
      target discharged.
- [ ] Or: the root cause is identified and removed on this host (one clean
      `lake build` run).

Meeting the first condition gives the target `machine_verified` (still
`needs_semantic_review = true`); it says nothing about the model hypotheses
H1-H4, which stay hypotheses.

## Next discriminating step

- **Action or proof obligation:** run the formal gate in a CI runner or on a
  checkout on an internal disk; compare `shasum` of the copied `.lake` oleans
  with the originals to show the inputs are identical.
- **Inputs and controls:** this branch; the pinned `lake-manifest.json`; the
  plain-`lean` compile log `scratch/compile.out` from this session as the
  expected result.
- **Execution limits and stop condition:** one gate run (about 10-15 min with
  a warm cache); stop on a clean pass or on the same EINTR.
- **Outcomes and next actions:** pass -> record `machine_verified` on the
  target and update IDEA-20261024-a2b05d's Lean status; same EINTR on another
  host -> the fault is in the toolchain, file an upstream report; EINTR only
  here -> host problem, keep this record open and route Lean work elsewhere.
- **Recheck trigger:** the next session that touches `formal/` on this host.

## Resolution and history

- 2026-10-24: opened during the lead-discovery session (RQ-ECDLP-361f3a).
  Unresolved.
