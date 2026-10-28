# Formal workspace build does not fit in 16 GB of RAM

- **Status:** `investigating`
- **Kind:** resource limit (observed on one 15 GiB container only); cause unknown
- **Affected work:** the `formal-workspace` proof gate
  (`tools/verify_formal_targets.py`, `.github/workflows/lean-verification.yml`,
  active as of 2026-10-28; it was disabled when this record was opened); every `autoresearch formal verify` run, which starts
  with a whole-workspace `lake build`; sheriff SHF-20261017-e4d7f6 CI1
  (`lean-verification` never built the Quotient target);
  [the 2026-10-23 rename report](../docs/reports/2026-10-23-translation-commutes-rename/report.md)
- **Next action owner:** unassigned (formal lane maintainer)
- **Last updated:** 2026-10-28

## Problem

`lake build` of `formal/` cannot finish on a 16 GB host because compiling
`CryptoResearch.Semaev.BooleanParityDegreeThreeRankCertificate` is killed out
of memory. The formal gate's first step is that build, so on such a host it
reports **every** target as not verified, whatever the target is.
`BooleanParityFiltrationCertificate` imports the module and is blocked with it.

That mattered because 16 GB is what a standard GitHub-hosted Linux runner has,
so re-enabling `lean-verification` there looked like it would fail the gate for
a reason that says nothing about any theorem.

**Correction, 2026-10-28:** that prediction did not hold. The hosted
`formal workspace (lake build + axiom audit)` job built the same module and the
whole workspace on `ubuntu-latest` and verified all 87 targets (see the
2026-10-28 entry below). The OOM is therefore seen on one container, not
established for the standard runner; why the two differ is unknown.

## Evidence and uncertainty

- **Observed:** on 2026-10-23, on Lean 4.35.0-rc1 and Mathlib `7fa22735`, with
  4 CPUs, 15 GiB RAM and no swap. The whole-workspace build was killed with
  `Lean exited with code 137` on that module after about 470 s. A retry with
  only it and its dependants left was killed the same way.
  `verify_formal_targets.py` then returned `formalization_blocked` ("lake build
  failed") for `quotient-translation-descent`. With the two modules moved out,
  the same workspace built (8,973 jobs), passed `AxiomAudit.lean` (640
  theorems) and verified that target. Logs:
  `docs/reports/2026-10-23-translation-commutes-rename/evidence/`.
- **Also observed:** the module was built and audited on 2026-10-22 on a
  different host (`docs/reports/2026-10-22-semaev-first-fall-replay/`,
  degree-three-rank evidence). That host's memory is not recorded there.
- **Derived or proved:** not established.
- **Suspected explanation (conjecture):** the file sets
  `set_option maxHeartbeats 0` and checks a large finite rank certificate by
  kernel reduction. Peak elaboration memory grows with the certificate. Peak
  RSS was not measured.
- **Missing capability:** a peak-memory measurement of the module, and a
  runner sized for it.
- **Observed, 2026-10-28, hosted runner:** `lean-verification` run
  [40713787875](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40713787875),
  job `formal workspace (lake build + axiom audit)`
  ([122905972990](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40713787875/job/122905972990)),
  head `b0e03a1620237b135d3bbf81ad826f9a9e41532c`, `ubuntu-latest`, plain
  `lake build` followed by `tools/verify_formal_targets.py`. It ran 15:13:54 to
  15:36:44 UTC, concluded `success`, and printed `87 verified, 0 not verified,
  0 infrastructure, 0 undischarged`, including
  `semaev-s3-semantic-rank-degree3-20261022` (the module that was killed here).
  Receipts: artifact `formal-verification-receipts` (ID 12828902787, 87 files).
  The same job also passed on the three earlier heads of the same PR on
  2026-10-28: `f6372f1e70` (03:35 to 03:58 UTC), `e040f506f8` (04:28 to 05:02)
  and `edd834c742` (05:15 to 05:39).
- **Not observed:** peak memory on either host, runner RAM and swap, and any
  lake or Lean thread setting that differs between the two.
- **What this evidence does not establish:** nothing about the module's
  correctness (it was audited elsewhere), nothing about any other theorem, and
  nothing about why the container and the hosted runner differ.

## What would unblock it

- [ ] `lake build` of the committed `formal/` workspace exits 0 on the host
  class the gate runs on (16 GB, or a declared larger runner), with peak RSS
  recorded. The exit-0 half is met by the hosted run of 2026-10-28; the peak-RSS
  half is not; or
- [ ] the gate builds the requested module and its closure (`lake build
  +Module`) and runs the axiom audit on a root restricted to built modules,
  and records which modules it did not build. That is a verifier change, and
  it needs its own review.

Either condition makes a gate failure mean something about the target again.
The first keeps the whole-workspace guarantee. The second weakens it to
per-target.

## Next discriminating step

- **Action:** record peak resident memory of
  `lake env lean CryptoResearch/Semaev/BooleanParityDegreeThreeRankCertificate.lean`
  (`/usr/bin/time -v`) on the hosted runner, for example in a throwaway
  workflow run, and on a host with more than 16 GB; compare runner RAM, swap
  and cgroup limit with the container that was killed.
- **Outcomes:** if it is above about 14 GB, the module needs restructuring (a
  smaller certificate per declaration, or `decide` split across lemmas) or the
  gate needs a larger runner. If it is below that, the out-of-memory kill came
  from lake's parallel scheduling, and a serialized build is the fix.
- **Recheck trigger:** any change to that module, to the toolchain pin, or to
  `lean-verification.yml` runner sizing.

## Resolution and history

- 2026-10-23: opened after the L-N9 rename build. Unresolved.
- 2026-10-28: the hosted gate passed with the whole workspace built (see
  Evidence). Status changed from `open` to `investigating`, and the claim that
  standard runners would fail is withdrawn. Kept open: the cause of the
  container OOM is unknown, no peak memory was measured anywhere, and a repeat
  on a 16 GB host could still fail. Unresolved.
