# Rename `translation_descends_iff_two_torsion` → `translation_commutes_iff_two_torsion` — 2026-10-23

**Status:** formal maintenance, closing sheriff finding L-N9 (case
`research/sheriff/SHF-20261017-e4d7f6`). No experiment was launched, no
hypothesis or claim changed status, and the theorem's statement and proof are
unchanged. Independent semantic review of the target is still pending, as it
was before.

## What changed

- `formal/CryptoResearch/Quotient/TranslationDescent.lean`: the theorem is now
  `CryptoResearch.Quotient.translation_commutes_iff_two_torsion`. It proves
  that τ_T commutes with ι_S = [-1] ∘ τ_S iff 2•T = 0. Descent through the
  degree-2 quotient is the prose fibre argument of
  `research/THM_QUOTIENT_DESCENT1.md` and is not formalized. The docstring no
  longer says "descends"; the header says why the name changed. The two
  `first | … | (…; abel)` fallbacks, whose second branch was never reached
  (unused-tactic and unreachable-tactic linter warnings at lines 39 and 44),
  are removed; the first branch is kept.
- `formal/targets/quotient-translation-descent.yaml`: `theorem_name` updated.
  The file name and `task_id` (`TASK-20261016-4c779c`) are unchanged:
  `tools/verify_formal_targets.py` keys receipts on the spec file stem, and the
  task id is cited by immutable records.
- `research/THM_QUOTIENT_DESCENT1.md`: the Status line and "Formal target"
  block give the new name (with `former_name`), and a dated 2026-10-23
  correction is appended. The 2026-10-17 correction, which quotes the old name,
  is left as written.
- No file under `docs/` outside the dated reports named the theorem.

Not edited (immutable, or dated evidence), still naming the old theorem:
`ledger/decisions/DEC-20260920-11b44c.yaml` (mints the formal goal under the
old name), the sheriff cases `SHF-20261016-3caa6f` and `SHF-20261017-e4d7f6`,
and the dated verification logs and receipt under
`docs/reports/2026-10-20-formal-validation/` and the four
`docs/reports/2026-10-21-*` reports. The former name is recorded in the
theorem's docstring, the target's comment and the research note, so a reader
following any of those records lands on the renamed declaration.

## Environment

- Lean `4.35.0-rc1` (commit `86c6347c75e3`), Lake `5.0.0-src+86c6347`, via
  elan 4.2.4; `formal/lean-toolchain` = `leanprover/lean4:v4.35.0-rc1`
  (SHA-256 `5699bbbd…`).
- Mathlib `7fa22735254ddf7e11f119250a9f2d0352bc7c3a` from the committed
  `formal/lake-manifest.json` (SHA-256 `3adfcdc0…`), used unchanged. Nothing
  ran `lake update`, so `./formal/setup.sh` was not run: it re-resolves the
  pin. Its other steps were run by hand.
- Host: 4 CPUs, 15 GiB RAM, no swap, and a disk allowance too small for both
  the full checkout and the Mathlib cache. `experiments/` was removed from the
  working tree with a sparse checkout to make room. That changes nothing
  committed. The two experiment directories cited by target specs were kept.

## Commands and results

```bash
curl -sSfL https://elan.lean-lang.org/elan-init.sh | sh -s -- -y --default-toolchain none
elan toolchain install leanprover/lean4:v4.35.0-rc1
cd formal && lake exe cache get              # pinned Mathlib oleans
python3 tools/rebuild_formal_root.py --workspace formal
cd formal && lake build CryptoResearch.Quotient.TranslationDescent   # before the rename
cd formal && lake build                                              # after
cd formal && lake env lean ../docs/reports/2026-10-23-translation-commutes-rename/evidence/PrintAxiomsTranslationCommutes.lean
cd formal && lake env lean AxiomAudit.lean
python3 tools/verify_formal_targets.py --targets-dir <dir holding only quotient-translation-descent.yaml> --artifact-dir <receipts>
python3 -m pytest -q tests/test_formal_targets.py tests/test_verify_formal_targets.py
```

1. **Before the rename**, the module built on the pin
   ([transcribed log](evidence/before-rename-build.log); 603 jobs, exit 0).
   That build raised the four linter warnings named in L-N9 (unused tactic and
   never-executed tactic at 39:8 and 44:8).
2. **After the rename**, the whole-workspace `lake build`
   ([log](evidence/formal-build.log)) built
   `CryptoResearch.Quotient.TranslationDescent` with no warnings (`✔`, not
   `⚠`). It failed on an unrelated module:
   `CryptoResearch.Semaev.BooleanParityDegreeThreeRankCertificate` was killed
   with exit 137 (out of memory). A retry with only the unbuilt modules left
   ([log](evidence/formal-build-retry.log)) was killed the same way. That
   module and `BooleanParityFiltrationCertificate`, which imports it, were
   built on 2026-10-22 on another host
   (`docs/reports/2026-10-22-semaev-first-fall-replay/`). This host cannot
   compile them; see
   [the problem record](../../../problems/formal-workspace-build-exceeds-16gb.md).
3. **Theorem-scoped axioms** ([log](evidence/print-axioms.log)):
   `'CryptoResearch.Quotient.translation_commutes_iff_two_torsion' depends on
   axioms: [propext]`. This matches the 2026-10-17 sheriff build of the old
   name.
4. **Unmodified gate**: `verify_formal_targets.py` on this target
   ([log](evidence/target-verification-full-workspace.log),
   [receipt](evidence/receipts/quotient-translation-descent.full-workspace.json))
   returned `formalization_blocked`, "lake build failed": its first step is
   the whole-workspace build, which fails on the out-of-memory module above.
   The verifier classifies that as not verified, not as an infrastructure
   failure. It says nothing about this theorem.
5. **Scoped gate**: the two Semaev modules were moved out of the workspace for
   one run, then restored byte-identically (`git status` clean afterwards). The
   generated root then imported 41 modules instead of 43. In that run:
   - `lake build`: [8,973 jobs, exit 0](evidence/formal-build-scoped.log);
   - `lake env lean AxiomAudit.lean` (`#audit_project`):
     [`axiom audit: 640 theorem(s), all standard axioms only`](evidence/axiom-audit-scoped.log);
   - `verify_formal_targets.py`: [1 verified, 0 not verified, 0
     infrastructure](evidence/target-verification-scoped.log), status
     `machine_verified` and "target axiom audit passed"
     ([receipt](evidence/receipts/quotient-translation-descent.scoped.json):
     source commit `6f5e60b54bfa`, theorem SHA-256 `359a5ced…`, task spec
     SHA-256 `12fa5950…`).
6. `pytest tests/test_formal_targets.py tests/test_verify_formal_targets.py`:
   **261 passed**. A first run had 6 failures, all
   from target specs whose `source` lived under the sparse-excluded
   `experiments/`; they passed once those two directories were restored to the
   working tree.

## Boundary

These checks establish that the renamed declaration is kernel-accepted on the
pin and depends on `propext` only. They also establish that 640 theorems in
the workspace, minus the two out-of-memory Semaev modules, pass the project
axiom audit. They do not re-verify those two modules on this host. They do not
formalize the commutation-to-descent step. They do not supply the pending
independent semantic review. The `lean-verification` workflow is still
disabled, so no hosted CI built this.

## 2026-10-28 addendum: hosted gate result and merge

The sections above record what was true on 2026-10-23 and stay as written. Two
of their statements are now out of date.

- **`lean-verification` is no longer disabled.** The workflow is `active` (last
  updated 2026-10-23 17:37 PDT), so the Boundary section's "still disabled, so
  no hosted CI built this" no longer holds.
- **The full gate has now run, on a hosted runner.** Item 4 above could not
  complete on the 15 GiB container because the whole-workspace `lake build`
  was OOM-killed. The hosted job `formal workspace (lake build + axiom audit)`
  of `lean-verification` run
  [40713787875](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40713787875)
  ([job 122905972990](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40713787875/job/122905972990))
  ran the same plain `lake build` and then `tools/verify_formal_targets.py` on
  `ubuntu-latest` at PR head `b0e03a1620237b135d3bbf81ad826f9a9e41532c` (the
  PR #2496 head with `main` at `6e86a2ddeb` merged in), 15:13:54 to 15:36:44
  UTC. It concluded `success` with:

  ```
  verified   quotient-translation-descent  (CryptoResearch.Quotient.translation_commutes_iff_two_torsion)
  87 verified, 0 not verified, 0 infrastructure, 0 undischarged
  OK: 87 target(s) machine-verified (independent semantic-fidelity review still required).
  ```

  The 87 receipts are in the run's `formal-verification-receipts` artifact (ID
  12828902787, 87 files). The same job also passed on the three earlier heads of
  the PR the same day (`f6372f1e70`, `e040f506f8`, `edd834c742`).

PR #2496 merged on 2026-10-28 at 15:43:48 UTC as merge commit
`cdd2150922211f180ab3d8c3f3b248356c78f025`, after 19 of 19 checks passed on the
head. The `main` ruleset requires its three checks to be strict, so earlier
merge attempts on heads that were behind `main` were refused with "3 of 3
required status checks are expected" (HTTP 405); nothing was bypassed.

Still not established: independent semantic review of the target (pending, as
before), the commutation-to-descent step (prose only), and why the whole
workspace builds on the hosted runner but not in the 15 GiB container (see
`problems/formal-workspace-build-exceeds-16gb.md`, now `investigating`). This
report's local receipts are not replaced by the hosted ones: the local scoped
receipt covers 41 of 43 modules, the hosted receipt covers the whole workspace.
