# Parallel execution receipt

25 October 2026, session `20261025T040202Z`. This report describes command outputs only; it makes no scientific verdict or performance claim. **Zero of the ten proposed scientific studies launched.** Their experiment cards have no scientific launchers. Two implemented development programs and the document build were replayed in three overlapping execution arms.

## What completed

| Component | Executions | Recorded output |
| --- | ---: | --- |
| Tagged reference | Normal, UBSan, ASan/UBSan | Each reports 13,731 assertions passed, including 2,362 tagged boundary cases |
| Fixed-window control | Normal and ASan/UBSan | Each reports 24 cases, 24 ranks, 448 margins, 24 mutations and 18 rank calibrations passed |
| Programme report build | One isolated replay | Exit 0; 14 pages; text and all 14 rendered raster hashes match the previously inspected programme |

There were five recorded command groups: three reference modes, a window group containing two builds/tests, and a report build. That represents five development binary suites plus one document build. Modes rerun the same fixtures; they are not independent scientific samples. Leak detection was explicitly disabled in ASan/UBSan commands because of the previously recorded tracing limitation. No leak-check success is claimed.

![Measured start/end overlap from the five command receipts. Times include compilation and shared host load; they are not ECDLP timings or algorithm comparisons.](timeline.pdf){width=95%}

The host exposes four CPU quota cores and a 16 GiB memory limit. Three arms ran concurrently; reference modes ran sequentially within one arm. The receipts include exact UTC intervals, wall/CPU seconds, maximum child RSS, argv and exit codes. A 120-second command watchdog protected fixed tiny development/build jobs; none timed out. The source fixtures were p=5,17,23 with prime subgroup orders 3,19,7.

An initial measurement attempt failed before any underlying program launched because `/usr/bin/time` is absent. Its stderr and exit files remain in `attempt-01/`. The successful retry used Python's standard subprocess/resource interfaces to record the existing commands; it changed no experiment or scientific admission check. Report builds emitted Fontconfig cache warnings and completed.

## What did not launch

All scientific rows have outcome **not executable**, not failed or disproved. There is no admitted experiment ID, trial launcher, scientific fixture manifest, executor queue or runbook for this programme. The exact per-track construction/implementation gaps are:

- **D, tagged response:** total gate/carry circuit, unique-wire checker, frozen rewrite grammar, EC-specific constructor and composition rule.
- **L1, prime-to-p sections:** p²/Hensel/formal-group diagnostic implementation and calibrated decoder.
- **L2, EDS/nets:** normalized recurrence and finite predictor program; target-specific nonlinear locator.
- **L3, endomorphisms:** supplied action/stratum manifest and certificate classifier; new non-generic observable.
- **L4, matchgate successor:** gate tensors, finite exact basis search, global planar/tag construction.
- **L5, radical ladder successor:** branch theorem obligation and target-local constructive invariant; existing theorem-deferred gate remains.
- **L6, reverse automata:** diagnostic observable/base, uniform state constructor and public target orientation.
- **L7, coefficients:** prefix diagnostic and cheap exact coefficient evaluator; shares D's bottleneck.
- **L8, Ax–Katz successor:** polynomial/degree/receipt audit and exact singleton residue constructor; shares D's bottleneck.
- **L9, lossy propagation:** repaired finite-r Kummer calibration, valid group/null/entropy implementation and propagation decoder.

The original IC-specific or retired proposals are not substitute launchers for the new direct successors. The [readiness inventory](readiness-inventory.md) records the inspected paths and limits. It does not claim that no related implementation exists in any branch anywhere.

The repository's [run workflow](https://github.com/aburan28/crypto-autoresearcher/blob/d75aac7361865ec8f98ca73874496410452fe208/plugins/crypto-autoresearcher-harness/skills/run/SKILL.md) states: "A needed implementation or protocol change is reported separately, not silently made during this skill." The missing programmes and mathematical constructors are reported here; no approval or ready state was fabricated.

## Reproduction and custody

Source commit: `d75aac7361865ec8f98ca73874496410452fe208`. This workspace contains selective source mirrors, not a Git checkout; source-file digests match the previously published bytes. The tagged reference SHA-256 is `6694c908abf275a2be41655cbbed6f5fcfb131a0dfb300b2027a323f9e3f2685`; the window source is `d7948445e4c7cf75e6c90417107886e935110aee4d9c903a8581b59054221a94`.

`commands.json`, `record-command.py` and `window-commands.sh` preserve invocation and capture logic. `identity.json`, `summary.json` and `rebuilt-report-raster-check.json` record identities and checks. `raw-records.json` bundles all 31 log, exit and receipt files from `logs/` and `attempt-01/` with their paths and hashes. `rebuilt-programme.pdf` is the isolated output. Reference binaries were temporary; window binaries remain local and are not uploaded to Git. This is not an admitted scientific archive.

The timeline plots recorded intervals only. No scientific trial, solver comparison, cancellation discovery, scientific transition or novelty certification was produced.
