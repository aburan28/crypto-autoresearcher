Independent local code review for `TASK-20261025-a58a22`. **Unpublished local draft.** The author repaired seven reported defects or specification discrepancies, and their original reproductions now reject. No remaining reproduced blocker was found in the tested software scope. The final focused suite passed **148 tests**, and **38 independent synthetic probe cases** met their expected results. This is an engineering result; scientific review, publication/custody readiness and historical gate repair are outside its scope.

The reviewer session was `/root/prym_phase_code_review`, separate from the validator author, and did not author or edit the validator, tests, producer artifacts or frozen records. The reviewer sent counterexamples to the author and independently checked the resulting final bytes. Reviewer writes are only this report and [report.json](report.json), under the assigned task directory. There were no scientific runs, credential reads, commits or pushes. The repository was on `lane/prym-rank-census`, HEAD `6fb7608d19660a6482fbbde756f613aa0da8ac04`, with pre-existing unpublished changes.

| Finding | Priority | Observed initial issue | Final disposition |
| --- | --- | --- | --- |
| F1 | P1 | Hardlink allowed a declared protected read before sealing | Repaired; independent reproduction now rejects. |
| F2 | P1 | Duplicate raw report fields were silently shadowed | Repaired; independent reproduction now rejects. |
| F3 | P2 | Duplicate bound YAML plan keys were accepted | Repaired; independent reproduction now rejects. |
| F4 | P2 | Python equality accepted a differently typed bound plan | Repaired; independent reproduction now rejects. |
| F5 | P2 | A symlink cycle escaped the consistency-error boundary | Repaired; independent reproduction now rejects. |
| F6 | P2 | Consistently future timestamps were accepted | Repaired; independent reproduction now rejects. |
| F7 | P3 | A read at the derivation boundary contradicted strict-before documentation | Repaired; independent reproduction now rejects. |

The initial software suite passed 137 tests despite those counterexamples. The repaired suite adds controls for the discovered paths. Its negative controls check the rejection reason, and the independent matrix also verifies that the phase exception preserves sibling-report blindness and rejects a stale composed plan. Valid sealed/unblind content and explicitly declared repeated reads still pass.

| Final focused command | Tests | Failures/errors |
| --- | ---: | ---: |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_review_phase_seals.py -v` | 52 | 0 |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_review_independence.py -v` | 29 | 0 |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools -p test_review_independence_addenda.py -v` | 58 | 0 |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools -p test_check_review_independence.py -v` | 9 | 0 |

The exact executed Python harnesses, all probe outcomes, initial raw observations and complete final test outputs are retained in [report.json](report.json). The runtime was Python 3.12.14 at `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3`. The repository's documented `/usr/local/bin/python3` was absent, so the four initial launches exited 127 before using this managed runtime. Bytecode writes were disabled.

Each minimal reproduction below starts from the synthetic `SealedPhaseTests` fixture in `tests/test_review_phase_seals.py`. Import it through `importlib.util.spec_from_file_location`, construct `x`, call `x.setUp()`, apply the mutation, call `x.errors()`, and finally `x.doCleanups()`. For altered bound-plan bytes, recompute `plan_sha256` in both records, rewrite the seal, update the release's `seal_sha256`, rewrite release, and refresh both boundary-event digests. The exact helper and executable mutations appear in the JSON report's `independent_probes.command`.

**F1: Hardlink allowed a declared protected read before sealing.** os.link(x.root/'producer/result.json', x.root/'inputs/alias.json'); replace phase1 input event, derivation.sources_read and attestation.sources_read with 'inputs/alias.json'; x.write_evidence(); x.errors() returned []. Path.samefile confirmed the same inode.

Expected: Reject a phase-one alias of a protected file. Repair observed: Phase-one sources with st_nlink != 1 are rejected conservatively.

Initial output:

```text
{"case": "hardlink_alias_to_protected_read_before_seal", "samefile": true, "errors": []}
```

Final check: `premature_protected_hardlink_alias` rejected; sealed review: multiply linked phase1 input could alias a protected source

**F2: Duplicate raw report fields were silently shadowed.** In json.dumps({"review_attestation":x.attestation}), replace the first '"source": "inputs/statement.json"' with '"source": "producer/result.json", "source": "inputs/statement.json"'. C._load selected the last source and C.check returned [].

Expected: Reject ambiguous duplicated fields in a phased transcript before choosing a value. Repair observed: The parser inspects the decoded YAML/JSON AST and uses the unique-key loader for phased documents; CLI returns a diagnostic exit 2 on malformed reports.

Initial output:

```text
{"case": "duplicate_report_event_source_masks_premature_protected_read", "parsed_second_source": "inputs/statement.json", "errors": [], "source_key_count": 4}
```

Final check: `duplicate_raw_report_source_cli` rejected; CLI exit 2: FAIL: invalid review report: /tmp/tmpx6xa3dad/review/report.json: duplicate blind-phase directive/field source

Parser-repair follow-up: Encode the key as literal JSON "phased\\u005frelease", prepend duplicate "read_sibling_reports":true before the existing false field, then load/check. The initial repair gated strict loading on a raw-text substring; the decoded key existed but the substring did not, so this follow-up returned [].

```text
{"case": "escaped_phase_key_bypasses_whole_doc_duplicate_strictness", "raw_literal_phase_key_present": false, "decoded_phase_key_present": true, "duplicate_sibling_field_count": 2, "errors": []}
```

Final escaped-key check: `escaped_phase_key_duplicate_report_cli` rejected with CLI exit 2: FAIL: invalid review report: /tmp/tmp4glxvi71/review/report.json: duplicate YAML key: read_sibling_reports

**F3: Duplicate bound YAML plan keys were accepted.** Write yaml.safe_dump({'review_plan':old_legacy_plan}) + yaml.safe_dump({'review_plan':x.plan}) to the bound plan file, then recompute the seal/release hashes and boundary event hashes. x.errors() returned [].

Expected: Reject ambiguous bound plan mappings. Repair observed: UniqueSafeLoader rejects duplicate YAML mappings in the bound prospective plan.

Initial output:

```text
{"case": "duplicate_yaml_review_plan", "errors": [], "accepted": true, "detail": {"review_plan_keys": 2}}
```

Final check: `duplicate_bound_yaml_plan` rejected; sealed review: duplicate YAML key: review_plan

**F4: Python equality accepted a differently typed bound plan.** Keep the checked plan's required=True; write a copy with required=1 to plan.yaml; rebind seal/release hashes and boundary event hashes. on_disk == checked_plan was True and x.errors() returned [].

Expected: Bind the exact plan, including scalar types. Repair observed: _same_tree compares structure and scalar types recursively.

Initial output:

```text
{"case": "wrong_bound_plan_boolean_integer", "errors": [], "accepted": true, "detail": {"checked_required_type": "bool", "bound_required_type": "int", "python_plans_equal": true}}
```

Final check: `wrong_bound_boolean_integer_type` rejected; sealed review: checked plan differs from the bound prospective plan file

**F5: A symlink cycle escaped the consistency-error boundary.** (x.root/'loop').symlink_to('loop'); x.contract['plan_path']='loop'; x.errors() raised RuntimeError.

Expected: Return an explicit consistency error instead of an uncaught path-resolution exception. Repair observed: _path converts resolution OSError/RuntimeError into InvalidPhase.

Initial output:

```text
{"case": "symlink_loop", "exception": "RuntimeError", "message": "Symlink loop from '/tmp/tmp7vom09t4/loop'"}
```

Final check: `cyclic_symlink` rejected; sealed review: cannot resolve repository path: 'loop'

**F6: Consistently future timestamps were accepted.** Move plan, derivation, seal, release and every event timestamp to 2099 while preserving their relative order; recompute all affected hashes. x.errors() returned [].

Expected: Reject future-dated evidence relative to the checking host clock. Repair observed: _time compares each timestamp against the checking host's current UTC clock. This is a sanity check, not authentication.

Initial output:

```text
{"case": "future_2099", "errors": [], "accepted": true}
```

Final check: `consistently_future_2099` rejected; sealed review: plan.recorded_at is in the future relative to the checking host's UTC clock

**F7: A read at the derivation boundary contradicted strict-before documentation.** x.events[1]['at']=x.derivation['generated_at']; x.errors() returned [].

Expected: Require phase-one reads to strictly precede derivation generation, as documented. Repair observed: The read comparison is now moment < generated.

Initial output:

```text
{"case": "read_at_derivation_boundary", "errors": []}
```

Final check: `exact_derivation_read_boundary` rejected; sealed review: phase1 read occurs after derivation or seal

The historical regression was also checked directly:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tools/check_review_independence.py --no-addenda --plan ledger/handoffs/TASK-20261025-5145ac.yaml --reports experiments/EXP-ECDLP-d6d8e8/reviews/TASK-20261025-5145ac/report.json
```

It exited **1**, as expected:

```text
FAIL: experiments/EXP-ECDLP-d6d8e8/reviews/TASK-20261025-5145ac/report.json: re-deriver TASK-20261025-5145ac read 6 blind_from path(s) -- experiments/EXP-ECDLP-d6d8e8/runs/RUN-ECDLP-ea49a6/, research/prym_experiment_design_20261019/implementation/independent.py, research/prym_experiment_design_20261019/implementation/projection.py, research/prym_experiment_design_20261019/implementation/relations.py, research/prym_rank_census_20261025/check_census.py, research/prym_rank_census_20261025/rank_census.py; the re-derivation is not independent of the implementation it was meant to check

1 independence problem(s) across 1 report(s)
```

No historical record was modified, and this check makes no scientific assessment.

The review binds to these final source bytes. Hashes stayed unchanged through the final suite:

| Source | SHA-256 |
| --- | --- |
| `tools/review_phase_seals.py` | `849453c6ff57d9401063e58b503600d99f85e02c3a7bd78d7b16defc90e49e83` |
| `tools/check_review_independence.py` | `76cb7ec685eada14970eef8d88280766c9fd9bdf186df82f7ec276cfd7fb3780` |
| `tests/test_review_phase_seals.py` | `3ef39b1a1a5d18248f3b42dfb4307aa61022b26cbcbb93f6819fc4d93238577f` |
| `docs/review-phase-seals.md` | `d5b4f3c32231ac9619ef08bb827b05a5fde1e4fe62f4b25287c3a5d2c2ae6ce5` |
| `tests/test_review_independence.py` | `53341b9c7f54db7bf2338cc40f241e71a9c1c875a13cf064020bf45f5a2c733d` |
| `tools/test_review_independence_addenda.py` | `91b6e68d2a72171a88a51ab4bf2cfe6644799f8d39a24304cfc51b88c62c1bba` |
| `tools/test_check_review_independence.py` | `3862f4adc97ef185c89a27500f82c9c2d8d7fb07ce5e75a4d46b26c0a6273ff5` |
| `ledger/handoffs/TASK-20261025-a58a22.yaml` | `d98db4058e362365e7634730411f01560fb15fc6f382d8eb1cb6f1dbfe73030f` |

This is an unpublished local engineering review. GitHub publication and artifact-store custody were not established; no commit, push, scientific dispatch, experiment run, gate repair or scientific-state transition is asserted.

The checker establishes consistency of the declared plan, derivation, seal/release bytes and event chronology. It does not authenticate people, session identity, actual read activity, signed time, independent archive publication or prescribed computation.

The host-clock future check rejects plainly future dates but cannot authenticate historical timestamps or prove the seal was committed before release.

Read coverage compares declared source sets. Explicit repeated events are accepted and sequenced. Removing an undisclosed repeat leaves an indistinguishable source union; missing reads omitted consistently from both declarations are not detectable. Missing unique declared source/read mismatches are rejected.

Phase-one hardlinks are conservatively rejected at validation time. Arbitrary copied or embedded protected content, prior filesystem changes, and actual input provenance require independent custody controls.

The seal hashes bind plan/derivation and seal/release records. Read events require current actual source files but do not establish their historical content at the claimed read time.

The review did not evaluate any derivation's mathematics, target labels, experiment outcomes, observation acceptance or scientific claims. Historical TASK-20261025-5145ac remains a failed independence check.

Finite synthetic controls and source inspection cannot prove absence of all bypasses. No remaining reproduced blocker was found in the tested software scope.


Provenance: internal repository sources were read directly and the recorded local commands were executed. The archive owner remains `TASK-20261025-c7c93f`; these files have no independent publication or archival attestation.
