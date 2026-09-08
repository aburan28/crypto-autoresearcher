# Coordinator approval review

Task: `TASK-20260907-de5598`, `BATCH-484d96`. Archive owner: `TASK-20260907-72aa15`. This is the Coordinator's protocol-readiness and administrative-normalization review. It is not an independent scientific review, a run-validity attestation, or a research-result promotion.

## Finite CRT protocol

The Coordinator approves `EXP-AUXIN-684adf` for the exact finite arithmetic protocol developed under `TASK-20260907-f87818`, subject to completion of the approval archive and its declared integrity gates. The standing user authorization in AGENTS.md dated 2026-09-06 satisfies user approval. The four design drafts remain preserved in snapshot `e23c63141837b0e78e064d82be57e6ce1f93a1f2`.

The parent reports exact candidate bindings:

| Canonical artifact | SHA256 |
| --- | --- |
| `ledger/hypotheses/H-AUXIN-7c52b2.yaml` | `9278c81dfa3a19598bb90b829141221fb33a611e975213c024fa46916b375531` |
| `experiments/EXP-AUXIN-684adf/specification.yaml` | `c104c69bc7ae07509203a20226a5f3b8983b4fbda7c8002d8c4aee2959abcb41` |
| `ledger/handoffs/TASK-20260907-58fcbe.yaml` | `58b2d63127abfe5760f54656093e4c3a6bc49212de4d6afc2bddf360c786c4a8` |

The draft specification hash is `454f7f0786d7b5ef93dfb0b3b935fe55bfa3b366733d853f214775c24c0b7975`. Parent parsed comparison found only four changes in the canonical specification: `status: approved`, `approved_by: coordinator`, `frozen: true`, and `approval_decision_id: DEC-20260907-6e1311`. All scientific fields are unchanged. The hypothesis and prospective implementation handoff match their archived drafts exactly. This agent supplied the original design but has not independently read back or hashed these candidate files.

Approval covers one future arithmetic run with 26,546 declared cases at r=101 and r=241: 12,240 correct systems, 4,080 incompatible systems, 10,200 compatible wrong-target controls, 24 malformed inputs, and two zero-target boundaries. It covers the existing deterministic ordering, separate exhaustive reference, original-target scalar-equality surrogate, equal-LCM and product-rule controls, eighteen run artifact filenames, and explicit arithmetic/model/group-cost distinctions. One worker and 4 GiB are machine protection; CPU and elapsed-time estimates remain null.

The hypothesis remains proposed. Cheon's published multiple-power CRT precedent is acknowledged; no new exponent, ordinary-ECDLP attack, actual group-operation measurement, or legal sparse-supply result is approved as a finding. The separate group interface preserves the mechanism without making this calibration stand in for group execution.

`TASK-20260907-58fcbe` authorizes implementation only and has maximum_runs=0. Its implementation must be snapshotted and independently reviewed. A subsequent scientific executor handoff needs a genuinely allocated run and launch lock bound to the approved specification, executing code, review, and current claim. This approval does not supply those future records or permit a scientific launch from the implementation handoff.

The parent reports a candidate full-ledger check over 10,115 records with no new violations and 1,210 unchanged baseline violations. That is a reported no-new-violations result, not an assertion that the entire ledger is clean. The formal effect of this approval is conditional on completion of its exact archive and required no-new-violations check. Current authority, dispatch, independent-review and launch gates continue to apply; baseline debt is not waived.

## S2G administrative normalization

`DEC-20260907-012234` concerns the source-preserving alias for `RUN-ECDLP-5cad48-S2G` described by `CORR-20260907-7c08d7`. The parent reports that original source hashes and recursive preservation passed, and targeted `check_run` returned no errors for the candidate. This is administrative evidence about the source mapping and schema; it does not independently validate S2G's scientific status or historic execution provenance.

The original manifest is preserved with SHA256 `c11b099d89d7ae4b6106a2935b6df89d7d9c046f2c18c472d7dd123638025818`. Its approved v2 additive alias, `manifest.schema-20260907-7c08d7.yaml`, has SHA256 `1e22a3a7a382fe729064335810ec89e768190e3fc86aaef36b43d80cda015d9c`. The alias preserves original fields, including producer `status: valid`, no certificate, all three claim flags false, 168 rows, the overlap flag, code commit `c61b43837e973a3b25813002c3db24f06bd15262`, and dirty=false. Preserving those fields is not an endorsement of their truth or an independent execution attestation.

The six schema completions are environment, inputs, timing, result, code.command, and result.certificate.kind. Command and environment come from original companion files. Row count and wall time come from original raw results. Seeds and absolute start/end times stay null and explicitly unrecorded. Original RSS is attributed as a source observation, not a new measurement. No run is repeated. Neither an execution revision nor missing random seeds or timestamps may be reconstructed from archive metadata.

The initial proposal failed one of 72 software regression tests because the alias lacked its own `supersedes` pointer. That proposal remains immutable and is not approved. The corrected v2 adds only the required exact original path/hash pointer to the alias, with corresponding correction and registry bindings. Its proposal copies were published in parent-reported commit `5154d72cc3`. The parent reports all 72 tests in `tools.test_run_supersession` and `tools.test_run_provenance_quarantine` passed in 3.403 seconds after this change. This agent did not run those tests.

The approved correction SHA256 is `afbf78edc26617c70b8a9bcaea9aa4eb5292ba0dbf6b08aebe0bfa7d6dbcec44`; the registry candidate SHA256 is `f76754291dc9ff2f0049add8d83f8dc697406c715cbf463610f9e718b3374db0`. The registry has exactly one appended S2G binding according to the parent. `normalization-decision.yaml` records all six original hashes and the exact original/alias linkage. Its evidence is the parent's `source-audit-v2.json`, `manifest-candidate-v2.yaml`, and `correction-candidate-v2.yaml` under `coordination/design/BATCH-484d96/integrity/`.

The decision binds the parent-transmitted original and v2 candidate hashes and restricts the correction to the stated source mappings and registry addition. Original artifacts remain intact. Final archival must verify the actual correction/registry against these bindings and complete the assembled-state no-new-violations ledger check. Any changed original hash, conflicting replacement, unsupported field, or failure to preserve the original mapping is a technical defect requiring correction before acceptance; no automatic fallback is approved.

## Provenance and portfolio boundary

All source hashes, candidate comparisons, validation results, claims and archive facts in this review were transmitted by the parent control plane. This agent wrote the underlying finite design and assessed the stated candidate changes. It did not execute commands, experiments, hash computations, model probes, or independent reviews, and did not open the S2G companion files. No knowledge promotion is warranted by these approvals.

The parent-reported census of 853 pending experiments and 889 open ideas has not been adjudicated by these two decisions. Three existing reserve approvals are reused under their own records; five protocols remain owned by another Coordinator; two PFDR items remain at technical readiness. These categories must not be summed as disjoint sets or described as completion of the user's full portfolio objective.

The next authorized step is to archive the exact canonical CRT contract and the narrow S2G normalization with these decisions, complete their integrity checks, and then dispatch the eligible zero-run implementation task under its own current claim. No scientific result, hypothesis promotion, goal activation, or goal completion occurs here.
