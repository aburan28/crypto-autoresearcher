# BINSTD f7ca97 original execution captures are missing

- **Status:** investigating
- **Kind:** provenance/access gap; no mathematical obstruction established
- **Affected work:** [TASK-20261002-d8df85](../coordination/design/TASK-20261002-d8df85/), [original run](../experiments/EXP-BINSTD-591d28/runs/RUN-BINSTD-f7ca97/manifest.yaml), [remaining ledger repair](../reports/ci-remaining-ledger-schema-20261030/README.md)
- **Next action owner:** repair session; original checkpoint custodian not yet identified
- **Last updated:** 2026-10-30

## Problem

A source-bound complete native run envelope cannot yet be supplied for the actual RUN-BINSTD-f7ca97 execution because its original command and environment captures have not been located. The ordinary-run requirement for all five capture companions still applies. This was a real execution, so the narrowly registered non-execution hand-derivation exception does not apply.

## Evidence and uncertainty

- **Observed:** the original execution receipt records `invalid_output`, process return code 0, checker return code 2, no scientific conclusion and `published: false`, from 2026-10-03T03:19:47 to 03:26:28. The original seven run files and archive receipt remain unchanged.
- **Observed:** [the archive receipt](../coordination/design/TASK-20261002-d8df85/archives/TASK-20261003-ccecf4/snapshot-receipt.json) lists seven files for this run and omits `command.txt` and `environment.json`; its sibling runs list those captures. File-history lookups for both missing paths return no commits. No ancestor artifact-manifest binding for either capture was found.
- **Observed:** the archived claim identifies session `cloud-agent-591d28-stages23`, branch `cursor/run-binstd-591d28-stages23-58c6` and worktree `/tmp/wt-run-binstd-591d28-stages23-58c6`, acquired 2026-10-03T03:18:01.
- **Derived or proved:** no valid execution source/environment can be inferred from a dispatch authority commit or a sibling's runtime captures.
- **Suspected explanation:** captures may survive in the original machine or a checkpoint; this has not been established.
- **Missing capability:** access to a genuine original capture or checkpoint bound to this run.
- **Limits:** this search does not prove the captures never existed. The run remains invalid and uncitable; no new execution, successful result, provenance waiver or source commit is inferred.

## What would unblock it

- [ ] Recover the original command and environment captures with immutable provenance binding them to this exact execution, rather than to a later sibling or rerun.
- [ ] Construct an additive source-bound native envelope using only verified original metadata; preserve invalid-output/checker-failure status and all raw bytes.
- [ ] Pass the unchanged native run/capture checks and the complete ledger sweep without expanding baselines or exceptions.

These conditions would repair archive validation only. They would not validate the scientific output, retrospectively approve a run, or establish a timing or cryptanalytic claim.

## Next discriminating step

- **Action:** locate and read the original checkpoint/machine identified above. A text question seeking its location is pending with the owner.
- **Inputs and controls:** exact original seven-file archive, claim and execution receipt; compare candidate capture identities/hashes and timestamps. Sibling captures are comparison evidence, never substitutes.
- **Execution limits and stop condition:** read-only provenance recovery; no scientific rerun is authorized by this recovery step. Stop any candidate-envelope construction when a required field lacks an actual source.
- **Outcomes:** genuine bound captures permit a reviewed additive envelope. Unrelated, incomplete or absent captures leave the requirement open. An access failure is recorded separately from absence.
- **Recheck trigger:** checkpoint location, restored original machine or new immutable capture evidence.

## Resolution and history

2026-10-30: 31 other schema errors were repaired locally while preserving this obstruction. Unresolved. Merging the administrative repair does not resolve this provenance requirement.
