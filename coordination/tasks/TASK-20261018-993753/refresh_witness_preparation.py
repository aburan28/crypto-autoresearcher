"""Refresh unarchived source-preparation metadata after Coordinator-requested hardening.

Preserves prior prospective records. Never touches canonical plans or science.
"""
from pathlib import Path
import hashlib
import json
import shutil

TASK=Path(__file__).resolve().parent
ROOT=TASK.parents[2]
HELPER="coordination/tasks/TASK-20261018-993753/worksheet_envelope.py"
OLD="6e2e24d3bfc86f40cce64bcbf053c9f47935d1db91bc7a92d03e46ca9bb0e93d"
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
NEW=sha(ROOT/HELPER)
assert NEW=="7841908dbed9caee0ff878aeb6b3c90e1327d80071e4f22061aab1dc6f8f12ad"
def preserve(path,label):
    backup=TASK/"checks"/label
    with backup.open("xb") as stream:
        stream.write(path.read_bytes())
def replace(path,value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")
layouts=[]
for path in sorted((TASK/"preparation").glob("*/trial-layout.json")):
    layout=json.loads(path.read_text())
    assert layout["source_sha256"][HELPER]==OLD
    preserve(path,path.parent.name+".before-witness-hardening.layout.json")
    layout["source_sha256"][HELPER]=NEW
    layout["comparison_policy"]="Routea records implementations_agree:null while awaiting its separately allocated routeb run. Routeb compares both complete measurements AND canonical witness/point sets against routea, requiring its successful native dependency receipt and unchanged artifact hashes."
    replace(path,layout)
    layouts.append(dict(experiment_id=layout["experiment_id"],path=str(path.relative_to(ROOT)),sha256=sha(path),
        source_sha256=layout["source_sha256"],source_trial_count=2,unallocated_run_ids=True))
validation_path=TASK/"checks/final-layout-validation.json"
preserve(validation_path,"final-layout-validation.before-witness-hardening.json")
validation=json.loads(validation_path.read_text())
for item in validation["source_entries"]:
    if item["path"]==HELPER:
        item["expected"]=NEW
    item["observed"]=sha(ROOT/item["path"])
    item["passed"]=item["expected"]==item["observed"]
assert all(e["passed"] for e in validation["source_entries"])
replace(validation_path,validation)
receipt_path=TASK/"implementation-receipt.json"
preserve(receipt_path,"implementation-receipt.before-witness-hardening.json")
receipt=json.loads(receipt_path.read_text())
receipt["layouts"]=layouts; receipt["shared_metadata_helper_sha256"]=NEW
software=receipt["software_validation"]
software.update(tests_passed=14,elapsed_seconds_reported_by_unittest=0.261,
    command="checks/software-controls-03.command.txt",source_manifest="checks/software-controls-03.sources.sha256",
    stdout="checks/software-controls-03.stdout",stderr="checks/software-controls-03.stderr")
software["covers"].append("explicit canonical witness/point-set equality across separately recorded routes")
receipt["witness_comparison_hardening"]="checks/witness-comparison-hardening.json"
replace(receipt_path,receipt)
note=dict(scope="Final unarchived source preparation; Coordinator confirmed no canonical source plan/archive existed",
    before_helper_sha256=OLD,after_helper_sha256=NEW,
    change="Explicit separately recorded route comparison now includes canonical witnesses/point sets as required by080496, in addition to measurements and independent checker correctness",
    software_tests_passed=14,source_hash_entries_rechecked=32,layout_source_entries_checked=38,
    scientific_trials_executed=0,prior_prospective_records_preserved=True)
with (TASK/"checks/witness-comparison-hardening.json").open("x") as stream:
    stream.write(json.dumps(note,indent=2,sort_keys=True)+"\n")
print(json.dumps(dict(helper_sha256=NEW,layouts=6,software_tests=14,scientific_trials_executed=0)))
