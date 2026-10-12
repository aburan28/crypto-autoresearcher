# GFPN RDL-1 admission decision — DEC-20261011-94aad3

**Decision type:** procedural scheduling stop. **Evidence strength:** exact-content custody and a literal read of frozen dispatch predicates. **Claim tier:** none; this decision makes no scientific or security claim. **Scope:** `TASK-20260925-23c435` under `EXP-GFPN-05ff43`, batch `BATCH-e409ca`.

## Observation

The content-first receipt under `TASK-20261010-0fda2f` was committed at `0080cca50e6e80cea55062a57e96a33c680c1c99`. The committed verifier returned `valid: true` for 771 paths from five producer commits (G1 337, G2 319, G3 13, G4 101, report 1). It expressly leaves the old `TASK-20260925-0ed1be` Phase B incomplete. The original `execution-report-v2-r5.yaml` records G1, G2, and G4 as `completed_valid` with `gate_pass: true`. It records G3 as `failed`, `failure_class: infrastructure_error`, `gate_pass: false`. It also discloses that G4 was launched after G3 failed.

A fresh isolated r5 checker replay in the custody receipt passed G1, G2, and G4 but failed G3 with `missing artifact certificates`. The original execution report recorded G3 checker PASS. In a separate scratch control using exactly the 13 G3 source-commit files, the same checker failed without `certificates/` and passed after only an empty `certificates/` directory was added. Every tracked byte remained equal to the source commit. The raw commands, environment, hashes, exits, stdout, and stderr are in `diagnostic.json`.

## Comparison with the frozen gate

`TASK-20260925-23c435` dispatch precondition DP-2 requires the old Phase-B `post-run-receipt.json`. That file is absent; the content-first successor is a different receipt and the old Phase B remains incomplete. DP-3 requires **all four** G1–G4 runs to be `completed_valid`, have `gate_pass: true`, and exit 0 under the r5 checker, with REG-1 passed. G3's raw status and gate value fail that conjunction regardless of the scratch checker control. DP-4 also requires a separate queue revision that has not been made. The visual shows these three gates and the stopped R2b path.

The 11 frozen R2b IDs in `trial-plan-v2-a1-r5.json` are all **not_attempted**: `RUN-GFPN-ba6fbe`, `RUN-GFPN-2f652c`, `RUN-GFPN-460cbc`, `RUN-GFPN-b0461a`, `RUN-GFPN-588be4`, `RUN-GFPN-d68f02`, `RUN-GFPN-4da222`, `RUN-GFPN-027369`, `RUN-GFPN-8eaa60`, `RUN-GFPN-ad9594`, and `RUN-GFPN-ce0dfe`. The last two are contingency IDs; R-12 was never triggered.

## Inference

RDL-1's frozen dispatch rule stops R2b-r5. G4 remains a preserved package with a sequencing deviation and cannot serve as a valid post-failed-gate sample for this admission decision. The scratch result establishes that an empty directory suffices to change the checker verdict in a reconstructed copy; it does not establish the directory's production-time presence, make G3 `gate_pass` true, or satisfy DP-2.

## Limitation and next action

This decision does not score G1, G2, or G4; change `H-GFPN-9a29be` or `HEUR-GFPN-DFLAT`; or dispatch a trial or reviewer. A later claim-changing review first needs a committed review plan with independent owners for checker/package replay, comparator infrastructure, and G4 sequencing, plus blind rederivation and a known-false post-failed-gate control. The old queue and run artifacts remain immutable. The affected canonical ECDLP frontier graphs were checked: this procedural stop changes no measured bound or claim tier, so their supported content does not change.
