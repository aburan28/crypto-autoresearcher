# Formal workspace CI ends before target audits finish

- **Status:** investigating
- **Kind:** CI resource limit; cancellation during verification
- **Affected work:** [PR #2536](https://github.com/aburan28/crypto-autoresearcher/pull/2536), [formal CI](../.github/workflows/lean-verification.yml)
- **Next action owner:** author of PR #2536; CI maintainers
- **Last updated:** 2026-10-24

## Problem

The original cold formal-workspace CI job ended before its complete target
audit within the configured 25-minute envelope. The revised 60-minute envelope
has completed successfully on the named revision below; final integration
with current main remains a separate merge requirement.

The gate must retain its workspace build, forbidden-construct and axiom checks,
every discharged target, and the existing minimum verification floor. An
interrupted run supplies no complete current-head result for merging.

## Evidence and uncertainty

- **Observed:** [Job 120769936508](https://github.com/aburan28/crypto-autoresearcher/actions/runs/40053816631/job/120769936508)
  on head `7d5448fdd292693f4d815f20653797a5d097358a` ran from
  05:16:15 to 05:41:35 UTC. Both the Lake and Mathlib caches missed.
  `lake build` ran from 05:22:40 to 05:37:48 and reported success with
  8,976 build jobs. Target auditing started at 05:37:48; thirteen receipts
  were uploaded before cancellation during the next target at 05:41:30.
  The workflow declares `timeout-minutes: 25` for this job.
- **Derived or proved:** Setup plus the completed workspace build consumed
  over 21 minutes, leaving under four minutes of the configured envelope
  for target audits. This is CI accounting, not a cryptanalytic cost claim.
- **Suspected explanation:** The cancellation aligns with the job timeout.
  The log reports cancellation rather than a failed theorem or axiom check;
  it does not independently identify a cancellation actor.
- **Missing capability:** The original run lacked a complete gate result. The
  revised gate has now completed all 84 YAML target specifications on head
  `ccee4e161768a983d3d7079cb16ba9772c5ca8f1`. The directory has 85 files
  including its README; the earlier draft incorrectly called all 85 target
  specifications. Final current-main integration checks are still needed.
- **What this evidence does not establish:** The partial receipts do not
  establish completion of the full gate or semantic fidelity of any research
  claim. No theorem, scientific result, ledger baseline, or frozen artifact is
  changed by adjusting the CI envelope.

## What would unblock it

- [x] A new current-head formal-workspace job completes every existing build
  and target audit step successfully, with its receipts retained.
- [ ] The other required and applicable current-head checks and review gates
  pass before merging PR #2536.

These conditions permit the software merge. Independent scientific review and
the existing unrelated full-corpus ledger obligations remain separate.

## Next discriminating step

- **Action or proof obligation:** Complete current-main integration and obtain
  all final-head CI and review gates before merging. Retain the validated
  60-minute envelope and all existing build/audit commands.
- **Inputs and controls:** Preserve all target specifications, proof sources,
  scope decisions, audit commands and the minimum verification floor. Retain
  the cancelled run and its partial receipts as incomplete evidence.
- **Execution limits and stop condition:** Existing CI, one 60-minute job
  watchdog; no local scientific trial, proof modification or manual rerun
  merely to obtain a passing result.
- **Outcomes and next actions:** Completion resolves this CI obstruction.
  A further interruption requires new log-based diagnosis; a target or audit
  failure remains a failed check and must not be waived.
- **Recheck trigger:** The CI run on the revised PR head finishes.

## Resolution and history

2026-10-24: Opened after reading the cancelled job's logs and timestamps.
The build succeeded, but the full gate remains incomplete. Unresolved until
the acceptance conditions above have linked evidence.

2026-10-24: [Formal job 120830553418](https://github.com/aburan28/crypto-autoresearcher/actions/runs/40074315064/job/120830553418)
on head `ccee4e161768a983d3d7079cb16ba9772c5ca8f1` succeeded with
`BUILD_WORKSPACE: true`. It ran from 10:25:16 to 11:02:59 UTC (37m43s),
completed the 8,976-job workspace build, and reported **84 verified, zero
not verified, zero infrastructure failures and zero undischarged targets**.
The receipt explicitly retains the requirement for independent semantic
review. This establishes completion of the software gate, not a new research
claim. The same head's [validate workflow](https://github.com/aburan28/crypto-autoresearcher/actions/runs/40074315130)
and [progress-fidelity workflow](https://github.com/aburan28/crypto-autoresearcher/actions/runs/40074315093)
also passed. The static count is corrected above: 84 YAML specifications plus
a README, rather than 85 specifications.

The runtime obstruction has passing evidence. This record remains investigating
until the final merged-main revision also satisfies the remaining merge gates:
the active progress-fidelity ruleset requires an up-to-date branch, and main
advanced to `6d4bfcda57fc0e9c9531404b8fb268bd0f04ec06` after the cited
revision. Earlier passing results are retained rather than reused as final-head
results. No proof, frozen scientific record, baseline or gate was weakened.
