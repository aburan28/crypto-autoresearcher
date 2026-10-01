#!/usr/bin/env python3
"""EXP-GFPN-05ff43 successor stage -- PLAN WRITER for trial-plan-v2-r2.json and trial-plan-v2-a1-r2.json
(paristack PS-3; DEC-20260923-80e280 RC-4 re-pointed; solverevent SE-7 as incorporated; seedresolve SF-7;
DEC-20260924-15a77a SC-1). Started from implementation-v2-r1/r1_make_plans.py.

usage: python3 -B r2_make_plans.py --write     write both plans (after asserting RC-4 (c) equality)
       python3 -B r2_make_plans.py --check     regenerate both in memory; assert byte-identical to disk

Mechanical derivation from the FROZEN plans (never the r1 plans):
  * ids: minted-run-ids.txt holds the 42 ids minted in this stage in minting order. The first 31 are assigned to the
    31 packages of trial-plan-v2.json in plan order, the next 11 to the 11 packages of trial-plan-v2-a1.json in plan
    order. M = id_map_v2 + id_map_a1 (42 entries) must be a bijection onto fresh ids: none a v1, v2, v2-a1 or r1 id,
    none of the 82 retired ids (RC-4 (a); ST-5);
  * every JSON string value of the frozen plan that equals, or contains as a whole token matching
    RUN-GFPN-[0-9a-f]{6}, a preimage of M is rewritten with its image (union map, both plans);
  * then exactly the DECLARED KEY PATHS (below; recorded in implementation-v2-r2.md before either plan was written,
    RC-4 (b)) are added or changed;
  * RC-4 (c) equality, asserted before writing: delete the declared key paths (from the r2 plan, and from the frozen
    plan where a declared path is a CHANGED key that the frozen plan also holds); replace every image of M by its
    preimage; canonical JSON (sort_keys, separators (',', ':'), ensure_ascii false) must be byte-equal to the frozen
    plan's. The frozen plans are checked against their bound sha256 first.
"""
import argparse
import copy
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r2_common as R                                    # noqa: E402

TOKEN = re.compile(r"RUN-GFPN-[0-9a-f]{6}")
MINTED = os.path.join(HERE, "minted-run-ids.txt")

DECLARED_KEYS_V2 = ["/protocol_version", "/task_id", "/written_by_task", "/archived_by", "/repair", "/gate/regression",
                    "/id_map", "/v2_ids_never_reused", "/a1_ids_never_reused", "/retired_ids", "/ceiling_note"]
DECLARED_KEYS_A1 = ["/protocol_version", "/task_id", "/written_by_task", "/archived_by", "/repair", "/gate/regression",
                    "/id_map", "/id_map_v2", "/frozen_v2_ids_never_reused", "/a1_ids_never_reused", "/retired_ids", "/ceiling_note"]

BRANCH_EVIDENCE = ("successor-stage development checks (implementation-v2-r2.md section 9): DV-3 reproduced 'ellcard: the PARI stack "
                   "overflows (current size: 8003584; maximum size: 8003584)' at (16777291, n = 3) without the configuration; DV-2 passed "
                   "under P-A at (4111, 3), (16777291, 3) and (4111, 4) in two fresh processes each (the r2 entry's configuration up to "
                   "dispatch, SE-3 replacement included), with the RC-2 read-backs, the RC-5 Hasse and second-point checks and the RC-5 gp "
                   "cross-checks; no P-B trigger condition (i)-(iii) occurred")


# ----------------------------------------------------------------------------- mapping
def map_strings(obj, m):
    if isinstance(obj, dict):
        for k in obj:
            if TOKEN.search(k):
                raise ValueError("a JSON key carries a run id: %r" % k)
        return {k: map_strings(v, m) for k, v in obj.items()}
    if isinstance(obj, list):
        return [map_strings(v, m) for v in obj]
    if isinstance(obj, str):
        return TOKEN.sub(lambda mo: m.get(mo.group(0), mo.group(0)), obj)
    return obj


def _split(ptr):
    return [p for p in ptr.split("/") if p]


def delete_path(obj, ptr):
    parts = _split(ptr)
    cur = obj
    for p in parts[:-1]:
        if not isinstance(cur, dict) or p not in cur:
            return False
        cur = cur[p]
    if isinstance(cur, dict) and parts[-1] in cur:
        del cur[parts[-1]]
        return True
    return False


def rc4c_equal(r2plan, frozen, declared, M):
    """RC-4 (c), the WRITER's implementation (DV-5 has its own, independent code path)."""
    inv = {v: k for k, v in M.items()}
    r, f = copy.deepcopy(r2plan), copy.deepcopy(frozen)
    for ptr in declared:
        delete_path(r, ptr)
        delete_path(f, ptr)
    r = map_strings(r, inv)
    a = json.dumps(r, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    b = json.dumps(f, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return a == b, R.sha256_bytes(a.encode()), R.sha256_bytes(b.encode())


# ----------------------------------------------------------------------------- inputs
def inputs():
    for path, want in ((R.PLAN_V2, R.PLAN_V2_SHA256), (R.PLAN_A1, R.PLAN_A1_SHA256)):
        got = R.sha256_file(path)
        if got != want:
            raise SystemExit("REFUSING: %s sha256 %s != bound %s" % (path, got, want))
    v2, a1 = R.load_json(R.PLAN_V2), R.load_json(R.PLAN_A1)
    ids = [x.strip() for x in open(MINTED) if x.strip()]
    v2_order = [p["run_id"] for p in sorted(v2["packages"], key=lambda p: p["order"])]
    a1_order = [p["run_id"] for p in sorted(a1["packages"], key=lambda p: p["order"])]
    if len(ids) != 42 or len(set(ids)) != 42 or len(v2_order) != 31 or len(a1_order) != 11:
        raise SystemExit("REFUSING: expected 42 distinct minted ids, 31 v2 and 11 v2-a1 packages")
    m2 = dict(zip(v2_order, ids[:31]))
    m1 = dict(zip(a1_order, ids[31:]))
    M = dict(m2, **m1)
    v1 = set(v2["v1_ids_never_reused"]) | set(a1["v1_ids_never_reused"])
    frozen = set(v2_order) | set(a1_order)
    forbidden_images = v1 | frozen | set(R.RETIRED_ALL) | set(R.USED_V2)
    if len(M) != 42 or len(set(M.values())) != 42 or set(M.values()) & forbidden_images or set(M) != frozen:
        raise SystemExit("REFUSING: M is not a bijection from the 42 frozen ids onto 42 fresh ids (RC-4 (a); ST-5)")
    unused_v2 = [i for i in v2_order if i not in R.USED_V2]
    if sorted(unused_v2) != sorted(R.RETIRED_V2_UNUSED) or sorted(a1_order) != sorted(R.RETIRED_A1_UNUSED):
        raise SystemExit("REFUSING: retirement lists differ from the paristack PS-3 enumeration")
    return v2, a1, m2, m1, M, v2_order, a1_order


def reg1_block(m2):
    ex_sha = R.sha256_file(R.REG1_EXCLUSION_LIST)
    return {
        "id": "REG-1",
        "d_branch": R.REG1_D_BRANCH,
        "rule": ("G1 (candidate_run, the r2 image of reference_run) must reproduce reference_run on its deterministic content before G2 is "
                 "admitted (paristack PS-4 regression_REG-1 as amended by the incorporated solverevent SE-4, (d) branch d-parsed by "
                 "seedresolve SF-4). Evaluated by r2_run_wrapper.py (R-7) before G2 and before every later package of either r2 plan; a "
                 "gate_required r2 package and every repaired addendum package runs only when G1-G4 are each completed_valid with "
                 "gate_pass true AND REG-1 passed. REG-1 fails if the candidate's solver-events.json is missing, does not parse or records "
                 "an SE-2 (4) consistency violation. A REG-1 failure ends R2' at the gate before G2 and is read as 'the repair layer is "
                 "not behaviour-neutral at 4111, or the pipeline is non-deterministic', never as a result."),
        "reference_run": "RUN-GFPN-ac4487",
        "reference_receipt": os.path.relpath(R.RECEIPT_V2_PHASE_B, R.REPO),
        "reference_integrity": "every reference file read is verified against the receipt's path_sha256 first; a mismatch is fatal",
        "candidate_run": m2["RUN-GFPN-ac4487"],
        "comparator": "experiments/EXP-GFPN-05ff43/implementation-v2-r2/r2_reg1.py",
        "compared": ["(a) solver/*.ms: same file set, byte-identical",
                     "(b) raw-result.json: run_status/failure_class/gate_pass; targets, planted_targets, replaced_fresh_targets (whole, minus exclusions) and the D table; structure_checks; fixture_F1; fixture_F2a; fixture_F2b; fixture_F3; group; rescaling; curve_checks; fresh targets' k (from certificates) and x_R; certificate block; metrics minus wall_seconds",
                     "(c) certificates/*.json: same file set, equal as JSON after the declared exclusions",
                     "(d) d-parsed: solver/*.ms.out of the recorded attempts: same file set; equal parse kind, header degree, eliminating-polynomial degree, square-free flag, F_p-rational solution set (as a set, v2_solver.rational_solutions) and D; no tolerance"],
        "outside_compared_sets": "solver-events.json and solver/*.ssf-attempt<k> files: listed with sha256; solver-events.json quoted in full; not exclusions",
        "exclusion_list": "experiments/EXP-GFPN-05ff43/implementation-v2-r2/reg1-exclusion-list.json",
        "exclusion_list_sha256": ex_sha,
        "exclusion_list_note": ("the r1 list X1..X17 carried verbatim (byte-identical to implementation-v2-r1/reg1-exclusion-list.json and to "
                                "implementation-v2-r1.md lines 329-372); nothing added (SE-4 (e)); X16 and X17 remain open review items"),
    }


def repair_block(plan_kind, derived_from, sha, declared):
    return {
        "paristack": {"id": R.PARISTACK_ID, "path": os.path.relpath(R.PARISTACK_PATH, R.REPO), "sha256": R.PARISTACK_SHA256,
                      "approval_decision": R.PARISTACK_APPROVAL, "conditions": R.PARISTACK_CONDITIONS,
                      "conditions_note": "RC-1..RC-13 re-pointed to r2 by DEC-20260924-15a77a; RC-6 read through CORR-20260923-111265"},
        "seedresolve": {"id": R.SEEDRESOLVE_ID, "path": os.path.relpath(R.SEEDRESOLVE_PATH, R.REPO), "sha256": R.SEEDRESOLVE_SHA256,
                        "approval_decision": R.SEEDRESOLVE_APPROVAL, "conditions": R.SEEDRESOLVE_CONDITIONS,
                        "correction": R.SEEDRESOLVE_CORRECTION,
                        "in_file_status_note": "the file reads status draft / approved_by null; the approval is the committed decision (SC-1)"},
        "solverevent": {"id": R.SOLVEREVENT_ID, "path": os.path.relpath(R.SOLVEREVENT_PATH, R.REPO), "sha256": R.SOLVEREVENT_SHA256,
                        "standing": R.SOLVEREVENT_STANDING},
        "K": R.K,
        "max_attempts_per_solve": R.K + 1,
        "spacing_s": R.SPACING_S,
        "resolve_cap": R.RESOLVE_CAP_RULE,
        "ssf_signature": "seedresolve SF-1 clauses (i)-(v)",
        "reg1_d_branch": R.REG1_D_BRANCH,
        "driver_pythonhashseed": R.DRIVER_PYTHONHASHSEED,
        "ps1_branch": R.PS1_BRANCH,
        "ps1_values": {"parisize": R.PARISIZE, "parisizemax": R.PARISIZEMAX},
        "ps1_api": R.PARI_API,
        "ps1_branch_evidence": BRANCH_EVIDENCE,
        "ps1_branch_final": "final for this protocol version (paristack PS-1 finality); changing it needs a new Coordinator decision",
        "rc2_exit_parisize_semantics": ("requested: on this host (cypari2 2.2.0, PARI 2.15.4) default(parisize) reports the configured size "
                                        "after the stack grew (successor-stage semantics probe), so the exit read-back must equal 67108864 "
                                        "exactly; parisizemax must equal 536870912 exactly"),
        "entry_point": "experiments/EXP-GFPN-05ff43/implementation-v2-r2/%s" % ("r2_entry_v2.py" if plan_kind == "v2" else "r2_entry_a1.py"),
        "resolve_wrapper": "experiments/EXP-GFPN-05ff43/implementation-v2-r2/r2_resolve.py",
        "run_wrapper": "experiments/EXP-GFPN-05ff43/implementation-v2-r2/r2_run_wrapper.py",
        "checker": "experiments/EXP-GFPN-05ff43/implementation-v2-r2/r2_check_run.py",
        "derived_from": {"plan": os.path.relpath(derived_from, R.REPO), "sha256": sha,
                         "bound_by": "phase A of TASK-20260923-0fa03f" if plan_kind == "v2" else "phase A of TASK-20260923-4ff597"},
        "derivation": "RC-4 (c): after deleting the declared key paths and applying the inverse of M, the plan equals derived_from as canonical JSON",
        "declared_key_paths": declared,
        "written_in": "the successor stage (TASK-20260923-de3a7d), implement only; no repaired run package exists",
    }


def ordered(src, changes, insert_after):
    """Rebuild src with changed values in place and new keys inserted after anchor keys (deterministic order)."""
    out = {}
    for k, v in src.items():
        out[k] = changes.get(k, v)
        for nk, nv in insert_after.get(k, []):
            out[nk] = nv
    return out


def build():
    v2, a1, m2, m1, M, v2_order, a1_order = inputs()
    reg1 = reg1_block(m2)
    retired = {"source": "DEC-20260923-c1fb69 R-1 (4); paristack PS-3 retirement; DEC-20260923-582d6b R-4; seedresolve authorization block; "
                         "DEC-20260924-15a77a SC-10; refused by r2_run_wrapper.py R-2",
               "used_v2_ids_kept_as_records_never_rerun": R.USED_V2,
               "unused_v2_ids_retired": R.RETIRED_V2_UNUSED,
               "unused_a1_ids_retired": R.RETIRED_A1_UNUSED,
               "r1_ids_retired_unused": R.RETIRED_R1,
               "n_retired": len(R.RETIRED_ALL),
               "note": "retired ids never produce a package and are reported unused in every later accounting"}
    ceiling = ("DC-7 A-7 with DEC-20260923-8b2dbf AA-5 (e): at most 48 run packages in the lineage. Existing: 2 "
               "(retired_ids.used_v2_ids_kept_as_records_never_rerun). Reserved by the r2 plans: 31 + 11 = 42. Total 2 + 31 + 11 = 44 of 48; "
               "4 unreserved. The 82 retired ids (29 v2, 11 v2-a1, 42 r1) never produce a package and do not count (seedresolve SF-7).")
    # ---- trial-plan-v2-r2.json
    p = map_strings(copy.deepcopy(v2), M)
    gate = dict(p["gate"])
    gate["regression"] = reg1
    p = ordered(p, {"protocol_version": R.PROTOCOL_V2_R2, "task_id": R.TASK_RUNS_V2,
                    "archived_by": "%s phase A (Coordinator)" % R.ARCHIVE_TASK, "gate": gate},
                {"archived_by": [("written_by_task", R.TASK_STAGE), ("repair", repair_block("v2", R.PLAN_V2, R.PLAN_V2_SHA256, DECLARED_KEYS_V2))],
                 "v1_ids_never_reused": [("v2_ids_never_reused", list(v2_order)), ("a1_ids_never_reused", list(a1_order)),
                                         ("retired_ids", retired), ("id_map", m2), ("ceiling_note", ceiling)]})
    # ---- trial-plan-v2-a1-r2.json
    q = map_strings(copy.deepcopy(a1), M)
    gate = dict(q["gate"])
    gate["regression"] = reg1
    rb = repair_block("a1", R.PLAN_A1, R.PLAN_A1_SHA256, DECLARED_KEYS_A1)
    rb["v2_gate_repointed_to"] = {"v2_blocking_packages": [m2[g] for g in v2["gate"]["blocking_packages"]], "plus": "REG-1 (d-parsed)",
                                  "addendum_blocking_package": m1[a1["gate"]["addendum_blocking_package"]],
                                  "aggregate_a1_inputs": "--v2-runs and --v2-aggregate mapped through id_map_v2; --a1-runs through id_map; "
                                                         "the repaired v2 bytes are read from the TASK-20260924-689d2f phase-B receipt (RC-8)"}
    q = ordered(q, {"protocol_version": R.PROTOCOL_A1_R2, "task_id": R.TASK_RUNS_A1, "written_by_task": R.TASK_STAGE,
                    "archived_by": "%s phase A (Coordinator)" % R.ARCHIVE_TASK, "gate": gate},
                {"archived_by": [("repair", rb)],
                 "v2_ids_never_reused": [("frozen_v2_ids_never_reused", list(v2_order)), ("a1_ids_never_reused", list(a1_order)),
                                         ("retired_ids", retired), ("id_map", m1), ("id_map_v2", m2), ("ceiling_note", ceiling)]})
    for name, plan, frozen, declared in (("trial-plan-v2-r2.json", p, v2, DECLARED_KEYS_V2), ("trial-plan-v2-a1-r2.json", q, a1, DECLARED_KEYS_A1)):
        ok, h1, h2 = rc4c_equal(plan, frozen, declared, M)
        if not ok:
            raise SystemExit("REFUSING: %s fails the RC-4 (c) equality (%s != %s)" % (name, h1, h2))
        if plan["watchdogs"] != v2["watchdogs"]:
            raise SystemExit("REFUSING: %s watchdogs differ from trial-plan-v2.json" % name)
        txt = json.dumps(plan)
        for f in R.FORBIDDEN_TASK_IDS:
            if f in txt:
                raise SystemExit("REFUSING: %s carries a forbidden task id" % name)
    return p, q, M


def render(plan):
    return json.dumps(plan, indent=1, ensure_ascii=False) + "\n"


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    a = ap.parse_args()
    p, q, M = build()
    outs = ((R.PLAN_V2_R2, render(p)), (R.PLAN_A1_R2, render(q)))
    if a.write:
        for path, txt in outs:
            if os.path.exists(path):
                raise SystemExit("REFUSING: %s exists; plans are written once" % path)
        for path, txt in outs:
            with open(path, "w") as fh:
                fh.write(txt)
            print("wrote %s sha256 %s (RC-4 (c) equality asserted)" % (os.path.relpath(path, R.REPO), R.sha256_bytes(txt.encode())))
        return 0
    bad = 0
    for path, txt in outs:
        same = os.path.exists(path) and open(path, encoding="utf-8").read() == txt
        print("%s regenerated byte-identically: %s (sha256 %s)" % (os.path.relpath(path, R.REPO), same, R.sha256_bytes(txt.encode())))
        bad += not same
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
