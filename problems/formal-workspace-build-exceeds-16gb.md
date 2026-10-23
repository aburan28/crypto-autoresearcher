# Formal workspace build does not fit in 16 GB of RAM

- **Status:** `open`
- **Kind:** resource limit (observed); cause inside the module unknown
- **Affected work:** the `formal-workspace` proof gate
  (`tools/verify_formal_targets.py`, `.github/workflows/lean-verification.yml`,
  currently disabled); every `autoresearch formal verify` run, which starts
  with a whole-workspace `lake build`; sheriff SHF-20261017-e4d7f6 CI1
  (`lean-verification` never built the Quotient target);
  [the 2026-10-23 rename report](../docs/reports/2026-10-23-translation-commutes-rename/report.md)
- **Next action owner:** unassigned (formal lane maintainer)
- **Last updated:** 2026-10-23

## Problem

`lake build` of `formal/` cannot finish on a 16 GB host because compiling
`CryptoResearch.Semaev.BooleanParityDegreeThreeRankCertificate` is killed out
of memory. The formal gate's first step is that build, so on such a host it
reports **every** target as not verified, whatever the target is.
`BooleanParityFiltrationCertificate` imports the module and is blocked with it.

That matters because 16 GB is what a standard GitHub-hosted Linux runner has.
Re-enabling `lean-verification` on standard runners would then fail the gate
for a reason that says nothing about any theorem.

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
- **What this evidence does not establish:** nothing about the module's
  correctness (it was audited elsewhere), and nothing about any other theorem.

## What would unblock it

- [ ] `lake build` of the committed `formal/` workspace exits 0 on the host
  class the gate runs on (16 GB, or a declared larger runner), with peak RSS
  recorded; or
- [ ] the gate builds the requested module and its closure (`lake build
  +Module`) and runs the axiom audit on a root restricted to built modules,
  and records which modules it did not build. That is a verifier change, and
  it needs its own review.

Either condition makes a gate failure mean something about the target again.
The first keeps the whole-workspace guarantee. The second weakens it to
per-target.

## Next discriminating step

- **Action:** run `/usr/bin/time -v lake env lean
  CryptoResearch/Semaev/BooleanParityDegreeThreeRankCertificate.lean` on a
  host with more than 16 GB and record the maximum resident set size.
- **Outcomes:** if it is above about 14 GB, the module needs restructuring (a
  smaller certificate per declaration, or `decide` split across lemmas) or the
  gate needs a larger runner. If it is below that, the out-of-memory kill came
  from lake's parallel scheduling, and a serialized build is the fix.
- **Recheck trigger:** any change to that module, to the toolchain pin, or to
  `lean-verification.yml` runner sizing.

## Resolution and history

- 2026-10-23: opened after the L-N9 rename build. Unresolved.
