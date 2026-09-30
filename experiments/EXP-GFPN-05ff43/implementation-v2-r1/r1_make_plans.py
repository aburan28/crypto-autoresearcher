#!/usr/bin/env python3
"""EXP-GFPN-05ff43 stage R1 -- PLAN WRITER for trial-plan-v2-r1.json and trial-plan-v2-a1-r1.json
(addendum PS-3; DEC-20260923-80e280 RC-4).

usage: python3 -B r1_make_plans.py --write     write both plans (after asserting RC-4 (c) equality)
       python3 -B r1_make_plans.py --check     regenerate both in memory; assert byte-identical to disk

Mechanical derivation:
  * ids: minted-run-ids.txt holds the 42 ids minted in stage R1 in minting order. The first 31 are assigned to
    the 31 packages of trial-plan-v2.json in plan order, the next 11 to the 11 packages of trial-plan-v2-a1.json
    in plan order. M = id_map_v2 + id_map_a1 (42 entries) must be a bijection onto fresh ids (RC-4 (a)).
  * every JSON string value of the frozen plan that equals, or contains as a whole token matching
    RUN-GFPN-[0-9a-f]{6}, a preimage of M is rewritten with its image (union map, both plans);
  * then exactly the DECLARED KEY PATHS (below; recorded in implementation-v2-r1.md before either plan was
    written, RC-4 (b)) are added or changed;
  * RC-4 (c) equality, asserted before writing: delete the declared key paths (from the r1 plan, and from the
    frozen plan where a declared path is a CHANGED key that the frozen plan also holds); replace every image of
    M by its preimage; canonical JSON (sort_keys, separators (',', ':'), ensure_ascii false) must be
    byte-equal to the frozen plan's. The frozen plans are checked against their bound sha256 first.
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
import r1_common as R                                    # noqa: E402

TOKEN = re.compile(r"RUN-GFPN-[0-9a-f]{6}")
MINTED = os.path.join(HERE, "minted-run-ids.txt")

DECLARED_KEYS_V2 = ["/protocol_version", "/task_id", "/written_by_task", "/archived_by", "/repair", "/gate/regression",
                    "/id_map", "/v2_ids_never_reused", "/a1_ids_never_reused", "/retired_ids", "/ceiling_note"]
DECLARED_KEYS_A1 = ["/protocol_version", "/task_id", "/written_by_task", "/archived_by", "/repair", "/gate/regression",
                    "/id_map", "/id_map_v2", "/frozen_v2_ids_never_reused", "/a1_ids_never_reused", "/retired_ids", "/ceiling_note"]

RETIRED_V2_UNUSED_ADDENDUM = [  # addendum PS-3 retirement, verbatim order
    "RUN-GFPN-76420e", "RUN-GFPN-b231c1", "RUN-GFPN-a07776", "RUN-GFPN-1ad09b", "RUN-GFPN-0c7483", "RUN-GFPN-4abae0", "RUN-GFPN-9e4212",
    "RUN-GFPN-bbbbe3", "RUN-GFPN-a521dd", "RUN-GFPN-a07b6d", "RUN-GFPN-dc1d4e", "RUN-GFPN-b9207c", "RUN-GFPN-aa56bd", "RUN-GFPN-e5b90d",
    "RUN-GFPN-d2f759", "RUN-GFPN-745cad", "RUN-GFPN-aeff00", "RUN-GFPN-3db273", "RUN-GFPN-3be8a4", "RUN-GFPN-00e64b", "RUN-GFPN-c5294d",
    "RUN-GFPN-36cad2", "RUN-GFPN-11d2ad", "RUN-GFPN-fc5d58", "RUN-GFPN-8f86cc", "RUN-GFPN-e26e4b", "RUN-GFPN-9da048", "RUN-GFPN-59320d",
    "RUN-GFPN-1596f6"]
RETIRED_A1_UNUSED_ADDENDUM = ["RUN-GFPN-0d91bf", "RUN-GFPN-8c772a", "RUN-GFPN-569fd7", "RUN-GFPN-086463", "RUN-GFPN-bab146",
                              "RUN-GFPN-7dd55d", "RUN-GFPN-47aa51", "RUN-GFPN-3a70f1", "RUN-GFPN-ae4918", "RUN-GFPN-8cfac3",
                              "RUN-GFPN-6a7f35"]
USED_V2 = ["RUN-GFPN-ac4487", "RUN-GFPN-3377f1"]

BRANCH_EVIDENCE = ("stage R1 development checks (implementation-v2-r1.md): DV-3 reproduced 'ellcard: the PARI stack overflows (current "
                   "size: 8003584; maximum size: 8003584)' at (16777291, n = 3) without the configuration; DV-2 passed under P-A at "
                   "(4111, 3), (16777291, 3) and (4111, 4) in two fresh processes each, with the RC-2 read-backs, RC-5 Hasse and "
                   "second-point checks and the RC-5 gp cross-checks; no P-B trigger condition (i)-(iii) occurred")


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


def rc4c_equal(r1plan, frozen, declared, M):
    """RC-4 (c), the WRITER's implementation (DV-5 has its own, independent code path)."""
    inv = {v: k for k, v in M.items()}
    r, f = copy.deepcopy(r1plan), copy.deepcopy(frozen)
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
    if len(M) != 42 or len(set(M.values())) != 42 or set(M.values()) & (v1 | frozen) or set(M) != frozen:
        raise SystemExit("REFUSING: M is not a bijection from the 42 frozen ids onto 42 fresh ids (RC-4 (a))")
    unused_v2 = [i for i in v2_order if i not in USED_V2]
    if sorted(unused_v2) != sorted(RETIRED_V2_UNUSED_ADDENDUM) or sorted(a1_order) != sorted(RETIRED_A1_UNUSED_ADDENDUM):
        raise SystemExit("REFUSING: retirement lists differ from the addendum's PS-3 enumeration")
    return v2, a1, m2, m1, M, v2_order, a1_order


def reg1_block(m2):
    ex_sha = R.sha256_file(R.REG1_EXCLUSION_LIST)
    return {
        "id": "REG-1",
        "rule": ("G1 (candidate_run, the r1 image of reference_run) must reproduce reference_run on its deterministic content before G2 is "
                 "admitted (addendum PS-4 regression_REG-1). Evaluated by r1_run_wrapper.py (R-7) before G2 and before every later "
                 "package of either r1 plan; a gate_required r1 package and every repaired addendum package runs only when G1-G4 are "
                 "each completed_valid with gate_pass true AND REG-1 passed. A REG-1 failure ends stage R2 at the gate before G2 and "
                 "is read as 'the repair layer is not behaviour-neutral at 4111, or the pipeline is non-deterministic', never as a result."),
        "reference_run": "RUN-GFPN-ac4487",
        "reference_receipt": os.path.relpath(R.RECEIPT_V2_PHASE_B, R.REPO),
        "reference_integrity": "every reference file read is verified against the receipt's path_sha256 first; a mismatch is fatal",
        "candidate_run": m2["RUN-GFPN-ac4487"],
        "comparator": "experiments/EXP-GFPN-05ff43/implementation-v2-r1/r1_reg1.py",
        "compared": ["(a) solver/*.ms: same file set, byte-identical",
                     "(b) raw-result.json: run_status/failure_class/gate_pass; targets, planted_targets, replaced_fresh_targets (whole, minus exclusions) and the D table; structure_checks; fixture_F1; fixture_F2a; fixture_F2b; fixture_F3; group; rescaling; curve_checks; fresh targets' k (from certificates) and x_R; certificate block; metrics minus wall_seconds",
                     "(c) certificates/*.json: same file set, equal as JSON after the declared exclusions",
                     "(d) solver/*.ms.out: byte-identical"],
        "exclusion_list": "experiments/EXP-GFPN-05ff43/implementation-v2-r1/reg1-exclusion-list.json",
        "exclusion_list_sha256": ex_sha,
        "exclusion_list_note": "declared in implementation-v2-r1.md in stage R1 before any repaired run (PS-4 (e)); its sha256 is recorded in the manifest of G2 and of every later package",
    }


def repair_block(plan_kind, derived_from, sha, declared):
    b = {
        "addendum_id": R.REPAIR_ID,
        "addendum_path": os.path.relpath(R.REPAIR_PATH, R.REPO),
        "addendum_sha256": R.REPAIR_SHA256,
        "approval_decision": R.REPAIR_APPROVAL,
        "conditions": R.REPAIR_CONDITIONS,
        "ps1_branch": R.PS1_BRANCH,
        "ps1_values": {"parisize": R.PARISIZE, "parisizemax": R.PARISIZEMAX},
        "ps1_api": R.PARI_API,
        "ps1_branch_evidence": BRANCH_EVIDENCE,
        "ps1_branch_final": "final for this protocol version (addendum PS-1 finality); changing it needs a new Coordinator decision",
        "rc2_exit_parisize_semantics": ("requested: on this host (cypari2 2.2.0, PARI 2.15.4) default(parisize) reports the configured size "
                                        "after the stack grew (stage R1 semantics probe), so the exit read-back must equal 67108864 exactly; "
                                        "parisizemax must equal 536870912 exactly"),
        "entry_point": "experiments/EXP-GFPN-05ff43/implementation-v2-r1/%s" % ("r1_entry_v2.py" if plan_kind == "v2" else "r1_entry_a1.py"),
        "run_wrapper": "experiments/EXP-GFPN-05ff43/implementation-v2-r1/r1_run_wrapper.py",
        "checker": "experiments/EXP-GFPN-05ff43/implementation-v2-r1/r1_check_run.py",
        "derived_from": {"plan": os.path.relpath(derived_from, R.REPO), "sha256": sha,
                         "bound_by": "phase A of TASK-20260923-0fa03f" if plan_kind == "v2" else "phase A of TASK-20260923-4ff597"},
        "derivation": "RC-4 (c): after deleting the declared key paths and applying the inverse of M, the plan equals derived_from as canonical JSON",
        "declared_key_paths": declared,
        "written_in": "stage R1 (TASK-20260923-a681f9), implement only; no repaired run package exists",
    }
    return b


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
    retired = {"source": "DEC-20260923-c1fb69 R-1 (4); addendum PS-3 retirement; refused by r1_run_wrapper.py R-2",
               "used_v2_ids_kept_as_records_never_rerun": USED_V2,
               "unused_v2_ids_retired": RETIRED_V2_UNUSED_ADDENDUM,
               "unused_a1_ids_retired": RETIRED_A1_UNUSED_ADDENDUM,
               "note": "retired ids never produce a package and are reported unused in every later accounting"}
    ceiling = ("DC-7 A-7 with DEC-20260923-8b2dbf AA-5 (e): at most 48 run packages across v2, v2-a1 and r1. Existing: 2 "
               "(retired_ids.used_v2_ids_kept_as_records_never_rerun). Reserved by the r1 plans: 31 + 11 = 42. Total 2 + 31 + 11 = 44 of 48; 4 unreserved. "
               "The 40 retired unused ids never produce a package and do not count (addendum PS-3 ceiling).")
    # ---- trial-plan-v2-r1.json
    p = map_strings(copy.deepcopy(v2), M)
    gate = dict(p["gate"])
    gate["regression"] = reg1
    p = ordered(p, {"protocol_version": R.PROTOCOL_V2_R1, "task_id": R.TASK_R2,
                    "archived_by": "%s phase A (Coordinator)" % R.ARCHIVE_TASK, "gate": gate},
                {"archived_by": [("written_by_task", R.TASK_R1), ("repair", repair_block("v2", R.PLAN_V2, R.PLAN_V2_SHA256, DECLARED_KEYS_V2))],
                 "v1_ids_never_reused": [("v2_ids_never_reused", list(v2_order)), ("a1_ids_never_reused", list(a1_order)),
                                         ("retired_ids", retired), ("id_map", m2), ("ceiling_note", ceiling)]})
    # ---- trial-plan-v2-a1-r1.json
    q = map_strings(copy.deepcopy(a1), M)
    gate = dict(q["gate"])
    gate["regression"] = reg1
    rb = repair_block("a1", R.PLAN_A1, R.PLAN_A1_SHA256, DECLARED_KEYS_A1)
    rb["v2_gate_repointed_to"] = {"v2_blocking_packages": [m2[g] for g in v2["gate"]["blocking_packages"]], "plus": "REG-1",
                                  "addendum_blocking_package": m1[a1["gate"]["addendum_blocking_package"]],
                                  "aggregate_a1_inputs": "--v2-runs and --v2-aggregate mapped through id_map_v2; --a1-runs through id_map; "
                                                         "the repaired v2 bytes are read from the TASK-20260923-b53550 phase-B receipt (RC-8)"}
    q = ordered(q, {"protocol_version": R.PROTOCOL_A1_R1, "task_id": R.TASK_R2B, "written_by_task": R.TASK_R1,
                    "archived_by": "%s phase A (Coordinator)" % R.ARCHIVE_TASK, "gate": gate},
                {"archived_by": [("repair", rb)],
                 "v2_ids_never_reused": [("frozen_v2_ids_never_reused", list(v2_order)), ("a1_ids_never_reused", list(a1_order)),
                                         ("retired_ids", retired), ("id_map", m1), ("id_map_v2", m2), ("ceiling_note", ceiling)]})
    for name, plan, frozen, declared in (("trial-plan-v2-r1.json", p, v2, DECLARED_KEYS_V2), ("trial-plan-v2-a1-r1.json", q, a1, DECLARED_KEYS_A1)):
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
    outs = ((R.PLAN_V2_R1, render(p)), (R.PLAN_A1_R1, render(q)))
    if a.write:
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
