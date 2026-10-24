# Independent checker review: TASK-20261019-fcedbb

## Admission, order, and scope

I reviewed the parser fix in the exact probed Codex session `01a15783-1602-73b2-b8e5-1a18a7e52b39` (`review-adversarial`, `gpt-6-sol`, `xhigh`). The committed custody manifest and session receipt identify that session, with no fallback or degraded requirements. `CONDUCTOR_SESSION_ID=067677ef-760d-49c0-a0b1-bf7a9b786450` was populated. `conductor task claim T-4489 --project conductor --json` returned task ID `d1ca4b2e-3744-4f40-ac17-a6a6ef6fee1b`, attempt `a7fe250f-591a-43be-a406-4ec825028062`, lease `1820c661-113d-4374-92db-f189b8033bbc`, fence epoch `1`, and exactly the two output paths of this handoff. A later redundant claim returned `task already claimed`; I did not release it.

Before reading the checker or author's tests, I read the frozen original plan and derived: P1 and P2 belong to `TASK-20261019-bb87e3` (Validator); P3 and P4 belong to `TASK-20261019-02a5c2` (Red Team). I then checked source snapshot receipt `TASK-20261019-d6f5cb`: commit `14949f4bf2707e14a45d27246852e00e5227717c` is an ancestor of the checkout, and the two working source hashes equal its recorded values. I read only the declared input attestations, not original scientific reviewer reports. This review makes no judgment on their P1-P4 scientific findings.

| Source | SHA-256 |
| --- | --- |
| `tools/check_review_independence.py` | `bb4bea905fc33a7dcdba7a32c1caacb6de3b7fe2af79c657573c3ba2ea9d3015` |
| `tools/test_check_review_independence.py` | `a608d67abb6e501069144048440d339923ab5d043f5239c7b00fb915234c9698` |
| `coordination/review/icperf-prime63-m2-postrun-20261019/review-plan.yaml` | `1242a62527951bd0f2bb7f908fd2be50e85dcd79cf7a0db0dd09d69de64a29db` |
| `coordination/review/icperf-postrun-independence-tool-20261019/review-plan.yaml` | `e3bf5d195fcfc7a52879410f0b6281699945a3e0ab25ff4d4d3b3cfae4ad24c7` |
| `coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-5bfb57/archives/TASK-20261019-d6f5cb/snapshot-receipt.json` | `fc11bd01d00e60db022e22dd6562248565627b3ff99f8a7949343d47da5ab926` |

The source delta gives explicit `id` priority over `joint` and rejects empty or non-string IDs. Its focused tests cover the expected matching and refusal cases. I used the frozen original plan as the independent oracle rather than relying on those assertions.

## Executed checks

`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python3 -m unittest tools.test_check_review_independence` exited 0: `Ran 17 tests` and `OK`.

`PYTHONDONTWRITEBYTECODE=1 python3 tools/check_review_independence.py --no-addenda --plan coordination/review/icperf-prime63-m2-postrun-20261019/review-plan.yaml --reports coordination/review/icperf-prime63-m2-postrun-20261019/TASK-20261019-02a5c2/attestation.yaml coordination/review/icperf-prime63-m2-postrun-20261019/TASK-20261019-bb87e3/attestation.yaml` exited 1. It found only one nested `review_attestation` and reported `joint 'P1' ... filed no review_attestation`, the same for P2, and `blind_rederivation ... filed no review_attestation`. The sealed top-level Validator schema was not inferred as a nested review attestation.

The independent in-memory fixture loaded the frozen plan and supplied synthetic nested-attestation values for the two original owners. Baseline `C.check(plan, reports)` returned `[]`. Each row below was a fresh deep copy with one named property changed. No fixture was written to the repository.

| Mutation from passing baseline | Observed result and exact error fragment |
| --- | --- |
| P3 owner changed to Validator | REJECT: `does not claim joint 'P3'` and `claims unassigned joint 'P3'` |
| P4 ID changed to duplicate P3 | REJECT: `joint 'p3' has 2 owners` |
| P3 ID changed to P9 while text stays P3's statement | REJECT: `does not claim joint 'P9'` |
| Validator attestation removed | REJECT: `joint 'P1' ... filed no review_attestation` |
| P3 verdict entry removed | REJECT: `per-joint verdict mapping carries no entry for 'P3'` |
| Validator source list names Red Team report path | REJECT: `sources_read includes sibling artifact without an authorized blindness lift` |
| Validator sets `read_sibling_reports: true` | REJECT: `read sibling reports but is not named in blindness.lifted_for` |
| Validator source list adds the first `blind_from` path | REJECT: `read 1 blind_from path(s)` |
| Legacy text-only entries, each `joint` prefixed with its P label and `id` removed | PASS: no problems |

The exact independent fixture command was:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python3 - <<'PY'
import copy
import yaml
import check_review_independence as C
path = "coordination/review/icperf-prime63-m2-postrun-20261019/review-plan.yaml"
with open(path, encoding="utf-8") as stream:
    plan = yaml.safe_load(stream)["review_plan"]
validator, red = "TASK-20261019-bb87e3", "TASK-20261019-02a5c2"
reports = [
    ("synthetic/validator.yaml", {"task_id": validator, "joints_owned": ["P1", "P2"],
        "verdict": {"P1": "holds", "P2": "inconclusive"},
        "sources_read": ["synthetic/public.json"], "read_sibling_reports": False,
        "blind_from_respected": True}),
    ("synthetic/red-team.yaml", {"task_id": red, "joints_owned": ["P3", "P4"],
        "verdict": {"P3": "holds", "P4": "breaks"},
        "sources_read": ["synthetic/public.json"], "read_sibling_reports": False}),
]
def run(label, mutate=None):
    p, r = copy.deepcopy((plan, reports))
    if mutate:
        mutate(p, r)
    problems = C.check(p, r)
    print(label, "PASS" if not problems else "REJECT", problems)
run("baseline")
run("wrong_owner", lambda p, r: p["joints"][2].__setitem__("assigned_to", validator))
run("duplicate_id", lambda p, r: p["joints"][3].__setitem__("id", "P3"))
run("wrong_id", lambda p, r: p["joints"][2].__setitem__("id", "P9"))
run("missing_reviewer", lambda p, r: r.pop(0))
run("missing_verdict", lambda p, r: r[1][1]["verdict"].pop("P3"))
run("sibling_source", lambda p, r: r[0][1]["sources_read"].append(
    f"coordination/review/synthetic/{red}/report.md"))
run("sibling_flag", lambda p, r: r[0][1].__setitem__("read_sibling_reports", True))
run("blind_leak", lambda p, r: r[0][1]["sources_read"].append(
    p["blind_rederivation"]["blind_from"][0]))
def legacy(p, r):
    for i, joint in enumerate(p["joints"], 1):
        joint.pop("id")
        joint["joint"] = f"P{i} -- {joint['joint']}"
run("legacy_joint_only", legacy)
PY
```

## Accepted false controls and verdicts

Two additional one-property mutations of a passing fixture returned `PASS []`. This exact command also tested a statement swap:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python3 - <<'PY'
import copy, yaml
import check_review_independence as C
with open("coordination/review/icperf-prime63-m2-postrun-20261019/review-plan.yaml", encoding="utf-8") as f:
    plan = yaml.safe_load(f)["review_plan"]
v, r = "TASK-20261019-bb87e3", "TASK-20261019-02a5c2"
reports = [
    ("synthetic/v.yaml", {"task_id":v, "joints_owned":["P1","P2"], "verdict":{"P1":"holds","P2":"holds"}, "sources_read":[], "read_sibling_reports":False, "blind_from_respected":True}),
    ("synthetic/r.yaml", {"task_id":r, "joints_owned":["P3","P4"], "verdict":{"P3":"holds","P4":"holds"}, "sources_read":[], "read_sibling_reports":False}),
]
for label, mutate in [
    ("baseline", lambda p,a: None),
    ("scalar_for_two_joints", lambda p,a: a[1][1].__setitem__("verdict","holds")),
    ("empty_full_statement", lambda p,a: p["joints"][2].__setitem__("joint","")),
    ("swapped_full_statements", lambda p,a: (p["joints"][2].__setitem__("joint",plan["joints"][3]["joint"]),p["joints"][3].__setitem__("joint",plan["joints"][2]["joint"]))),
]:
    p,a=copy.deepcopy((plan,reports))
    mutate(p,a)
    problems=C.check(p,a)
    print(label, "PASS" if not problems else "REJECT", problems)
PY
```

Its output was `baseline PASS []`, `scalar_for_two_joints PASS []`, `empty_full_statement PASS []`, and `swapped_full_statements PASS []`. The first false case changes only the Red Team `verdict`; the second changes only `joints[2].joint`; the third exchanges two text values. The scalar acceptance contradicts `_verdict_for`'s own stated single-joint allowance; the statement acceptance means the checker cannot establish that an explicit ID carries a full statement. Both behaviors predate or extend beyond the narrow source delta, but they remain in the proposed gate.

**T1: breaks.** The ID selector handles the frozen P1-P4 labels and rejects a wrong or duplicate ID, but the checker accepts an ID with no full statement and cannot bind the statement text to that ID. **T2: breaks.** The requested missing-entry, attestation, sibling, blind-source, and sealed-schema controls reject; nevertheless a two-joint reviewer can replace its per-joint verdict map with one scalar and pass. Neither break is an assessment of the original reviewer testimony.

## Limits and deviation

The checker tests declared plan and attestation fields; it cannot authenticate actual sources read, session identity, report contents, or scientific conclusions. No solver or experiment trial was run. I did not edit code, tests, plans, sealed files, queues, claims, or status. `agents/reviewer.md`, requested as a role contract, is absent in this checkout (`cat` returned `No such file or directory`); I used the available `AGENTS.md` contract and the committed task/plan and record this as a procedure deviation. The current findings block acceptance of the broad T1/T2 gate as stated; the Coordinator owns any later correction, archive, and decision.
