# Prospective prime63 m=2 diagnostic output contract

**Status:** additive engineering source; no experiment approval, scientific launch, or ECDLP claim. This directory does not change the approved `EXP-ICPERF-515ae3` plan, `RUN-ICPERF-eb0d88`, or its independent checker.

## Exact gap and source boundary

The [frozen trial plan](../../experiments/EXP-ICPERF-515ae3/trial-plan.json) requires `manifest.yaml` and `raw-result.json`. The [published run](../../experiments/EXP-ICPERF-515ae3/runs/RUN-ICPERF-eb0d88/execution-receipt.json) retained the diagnostic receipt and raw archive, but its launcher did not emit those top-level files. The standard supervisor recorded `invalid_output`; its independent raw checker returned `integrity_pass` on narrower predicates. [The problem record](../../problems/icperf-prime63-m2-output-contract-mismatch.md) keeps the two classifications distinct.

`contract.py` is a pure-Python bridge for a **fresh-ID successor**. It reads a finished diagnostic receipt, the supervisor's launch/environment/command files, and the raw archive. It checks run, trial, plan, claim-owner/epoch, launch hash, fixed four-cell schedule, expected injected monitor fault, terminal classifications, archive hash, and timestamps. It then creates the two required files with exclusive writes. `verify_outputs` recomputes their exact canonical bytes and rejects missing or changed outputs. The `manifest.yaml` payload is JSON, which is valid YAML and passes the repository run-schema checker in the no-solver fixture.

The bridge never calls Sage, enumerates roots, approves a trial, or verifies a mathematical certificate. It records `verification_status: pending_independent_checker` and `certificate.kind: none`. A fresh successor checker must run this byte check **and** an independent exact polynomial/base/sign/full-point check before accepting a certificate. A nonzero child exit is recorded as infrastructure failure; time and resource censors remain explicit.

## Recorded stage boundary

| Stage | RUN-ICPERF-eb0d88 observation | New bridge effect |
| --- | --- | --- |
| Monitor-null control | Expected `unreadable_live_root` injection | Confirms the control's receipt identity |
| Coset m=2 | `timeout_censored` at 600 seconds in Gröbner phase | Preserves classification only |
| Random m=2 | `timeout_censored` at 600 seconds in root enumeration | Preserves classification only |
| Small-x m=2 | `timeout_censored` at 600 seconds in root enumeration | Preserves classification only |
| Standard supervisor | `invalid_output` because required top-level files were absent | Emits schema-valid prospective files in a separate fixture |

These are separate planted targets on the archived short-Weierstrass prime-field curve with `p = 9223372021248595841`, subgroup order `r = 9223372018953067627`, base size 475 per arm, and arity two. The resource plot and full receipts are in the [run report](../../experiments/EXP-ICPERF-515ae3/reports/run-20261019T2113Z/report.md). No measured end-to-end cost, natural relation yield, useful rank, linear algebra, target reconstruction, or matched rho value comes from this engineering change. Prime-field behavior does not transfer to Koblitz or ordinary-binary curves without separate evidence.

## No-solver checks

Run `python3 -m unittest research/icperf_prime63_m2_output_contract_20261019/test_contract.py -v` from the repository root. The tests use a synthetic four-cell receipt and, when materialized, the exact archived diagnostic receipt copied into a temporary directory. They check censored and canned-positive structural outputs, the standard `manifest.yaml` schema, byte tampering, absent archive, wrong authority, an unattempted cell without a reason, a nonzero child exit, and preservation of the historical missing files. The archived run is only read. The additional review regressions reject absent authority, empty owners/identities, malformed plan digests, and non-integer or non-positive epochs before any output is written. The captured [validation log](validation.log) retains the original eight-test result; its unrelated `ResourceWarning` comes from the existing ledger validator used for the manifest-schema check.

## Prospective integration gate

1. A fresh-ID launcher with hash-bound source and inputs must call `write_outputs` after its diagnostic receipt is sealed. It must not add files to `RUN-ICPERF-eb0d88`.
2. A fresh-ID independent checker must call `verify_outputs`, validate every raw member and phase trace, and check each claimed root as an exact full-point relation. Negative controls must reject changed or missing top-level files and forged certificates.
3. The Coordinator must freeze the exact successor plan, source closure, controls, limits, and handoffs, obtain `experiment_preapproval.py --packet` with `approvable: true`, archive approval under the standing authorization, and verify the ordinary selector is `ready` before any new scientific call.
4. Even a valid output contract would only validate run custody. A separately approved solver/formulation test is needed to see whether one checked witness can be extracted under a fixed cap. Natural relations, useful rank, full cold/online IC cost and matched rho remain downstream obligations.
