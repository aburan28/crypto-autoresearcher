"""Verify prepared metadata/source bindings and write source-only receipt."""
from pathlib import Path
import hashlib
import json
import sys

TASK=Path(__file__).resolve().parent
ROOT=TASK.parents[2]
IDS=("080496","4a3f03","5a293e","6491b4","65f903","911c16")
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):
    with path.open("x") as stream:
        stream.write(json.dumps(value,indent=2,sort_keys=True)+"\n")
protected=json.loads((ROOT/"coordination/tasks/TASK-20261018-65f03a/protected-specification-sha256.json").read_text())
layouts=[]; entries=[]; preserved=[]
for suffix in IDS:
    path=TASK/"preparation"/("EXP-ECDLP-"+suffix)/"trial-layout.json"
    layout=json.loads(path.read_text())
    for name,expected in layout["source_sha256"].items():
        observed=sha(ROOT/name)
        entries.append(dict(path=name,expected=expected,observed=observed,passed=observed==expected))
    name=layout["specification"]
    actual=sha(ROOT/name)
    preserved.append(dict(path=name,expected=protected[name],observed=actual,passed=actual==protected[name]))
    layouts.append(dict(experiment_id=layout["experiment_id"],path=str(path.relative_to(ROOT)),sha256=sha(path),
        source_sha256=layout["source_sha256"],source_trial_count=2,unallocated_run_ids=True))
assert all(e["passed"] for e in entries+preserved)
assert "Ran 13 tests" in (TASK/"checks/software-controls-02.stderr").read_text()
assert (TASK/"checks/software-controls-02.stderr").read_text().strip().endswith("OK")
validation=dict(scope="Source/layout/protected-input binding only; no frozen worksheet execution",
    layout_count=6,layout_source_entries_checked=len(entries),all_passed=True,source_entries=entries,
    protected_specifications=preserved,scientific_trials_executed=0)
write(TASK/"checks/final-layout-validation.json",validation)
receipt=dict(schema="finite-worksheet-implementation-receipt/v1",task_id="TASK-20261018-993753",
    authority_handoff="ledger/handoffs/TASK-20261018-993753.yaml",authority_decision="DEC-20261018-59a33a",
    status="source_prepared_for_coordinator_review_not_scientific_trial_complete",scientific_trials_executed=0,
    canonical_plan_spec_queue_status_changes=False,commits_or_pushes_performed=False,
    layouts=layouts,shared_metadata_helper="coordination/tasks/TASK-20261018-993753/worksheet_envelope.py",
    shared_metadata_helper_sha256=sha(TASK/"worksheet_envelope.py"),
    software_validation=dict(tests_passed=13,exitcode=0,elapsed_seconds_reported_by_unittest=0.216,
        command="checks/software-controls-02.command.txt",source_manifest="checks/software-controls-02.sources.sha256",
        source_entries_rechecked=32,stdout="checks/software-controls-02.stdout",stderr="checks/software-controls-02.stderr",
        control_scope="Alternative synthetic fields/rationals and wholly mocked metadata repository; no complete frozen cell evaluated",
        warning="Existing validate_ledger.py emits a ResourceWarning for an unclosed duplicate_run_ids.yaml reader; retained, not repaired here",
        covers=["AST parsing and no scientific sibling imports","three-way synthetic arithmetic/listing agreement",
            "canonical modular x+1 values","coprime theta cancellation software fixture","control-valid false prediction accepted",
            "native minimum manifest gate with seed:null","source/output no-overwrite guards",
            "manifest parameter/invalid_reason and witness-scope tampering","typed Boolean/integer and Boolean/resource tampering",
            "separate-route dependency and changed previous-artifact rejection"]),
    runtime=dict(executable=sys.executable,python=sys.version,requested_path_exists=False,
        requested_path="/usr/local/bin/python3",pinned_3_12_8_parity_claimed=False),
    independent_implementation_boundary="Independent scientific enumerations/arithmetics and oracle modules; metadata-only common helper. Internal source review and software validation, not an external or formal scientific review.",
    source_iteration_note="checks/source-iteration-note.json",
    remaining=["Coordinator allocates/freezes exact native trial/RUN IDs and artifact-complete handoff/queue/archive scopes",
        "Source publication and native preapproval/ready admission before any scientific launch",
        "All twelve actual per-route worksheet runs, separate checks, final route agreement and frozen prediction comparisons remain unexecuted",
        "field7.denominator_mod/field13.denominator_mod in4a3f03 have no specified formula and remain unmeasured declared inputs",
        "Native seed:null acceptance versus separate JSON schema integer-only seed remains disclosed, not patched",
        "No original20-item completion, ECDLP result, speedup, formal proof or official research transition"])
write(TASK/"implementation-receipt.json",receipt)
print(json.dumps({"layouts":6,"source_entries_checked":len(entries),"protected_specs_unchanged":6,
                  "software_tests":13,"scientific_trials_executed":0,"passed":True}))
