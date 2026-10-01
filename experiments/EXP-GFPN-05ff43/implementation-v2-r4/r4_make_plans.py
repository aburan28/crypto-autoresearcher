#!/usr/bin/env python3
"""EXP-GFPN-05ff43 r4 stage -- PLAN WRITER for trial-plan-v2-r4.json and trial-plan-v2-a1-r4.json (paristack PS-3;
DEC-20260923-80e280 RC-4 re-pointed; readbackcover RB-6; launchkind RJ-8; DEC-20260924-daf670 LKA-1, LKA-3; card
R4S-5). Started from implementation-v2-r3/r3_make_plans.py.

usage: python3 -B r4_make_plans.py --write --dv2 DV2_JSON --dv3 DV3_JSON   write both plans (after the RC-4 (c) equality)
       python3 -B r4_make_plans.py --check --dv2 DV2_JSON --dv3 DV3_JSON   regenerate both in memory; assert byte-identical

DV2_JSON / DV3_JSON are the r4 stage's DV-2 and DV-3 outputs (development records); the writer REFUSES unless both
record a pass, and quotes their outcomes (never a path) in repair.ps1_branch_evidence (the branch is final, PS-1).

Mechanical derivation from the FROZEN plans (never the r1, r2 or r3 plans):
  * ids: minted-run-ids.txt holds the 42 ids minted in this stage in minting order. The first 31 are assigned to the
    31 packages of trial-plan-v2.json in plan order, the next 11 to the 11 packages of trial-plan-v2-a1.json in plan
    order. M = id_map_v2 + id_map_a1 (42 entries) must be a bijection onto fresh ids: none a v1, v2, v2-a1, r1, r2 or r3
    id, none of the 162 retired ids (RC-4 (a); R4S-5);
  * every JSON string value of the frozen plan that equals, or contains as a whole token matching
    RUN-GFPN-[0-9a-f]{6}, a preimage of M is rewritten with its image (union map, both plans);
  * then exactly the DECLARED KEY PATHS (below; recorded in implementation-v2-r4.md before either plan was written,
    RC-4 (b)) are added or changed;
  * RC-4 (c) equality, asserted before writing: delete the declared key paths (from the r4 plan, and from the frozen
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
import r4_common as R                                    # noqa: E402

TOKEN = re.compile(r"RUN-GFPN-[0-9a-f]{6}")
MINTED = os.path.join(HERE, "minted-run-ids.txt")

DECLARED_KEYS_V2 = ["/protocol_version", "/task_id", "/written_by_task", "/archived_by", "/repair", "/gate/regression",
                    "/gate/admission", "/id_map", "/v2_ids_never_reused", "/a1_ids_never_reused", "/retired_ids", "/ceiling_note"]
DECLARED_KEYS_A1 = ["/protocol_version", "/task_id", "/written_by_task", "/archived_by", "/repair", "/gate/regression",
                    "/gate/admission", "/id_map", "/id_map_v2", "/frozen_v2_ids_never_reused", "/a1_ids_never_reused",
                    "/retired_ids", "/ceiling_note"]

SITES_CC1 = {
    R.SITE_S1: {"file": "implementation-v2/v2_driver.py", "argv_line": 165, "launch_line": 166, "enclosing_function": "solve",
                "classified": True, "disposition": ("WRAPPED BY SE-3 (re-solved on the SSF signature when gb_only is false; passed "
                                                    "through when gb_only is true, SE-2 (6)); every attempt carries an RB-1 record "
                                                    "(fields (a)-(e)); every pass-through call an RL-2 record")},
    R.SITE_S2: {"file": "implementation-v2-a1/a1_health.py", "argv_line": 144, "launch_line": 147, "enclosing_function": "run_system",
                "classified": True, "disposition": "WRAPPED BY HR-3 (HR-1..HR-8); every attempt carries an RB-1 record (fields (a)-(d))"},
    R.SITE_S3: {"file": "implementation-v2/v2_driver.py line 209 -> implementation-v2/v2_solver.py lines 516-517",
                "argv_line": "implementation-v2/v2_driver.py 209", "wrapper_argv_line": "implementation-v2/v2_solver.py 516",
                "launch_line": "implementation-v2/v2_solver.py 517", "enclosing_function": "solve (of the argv line)",
                "classified": "CLASSIFIED (DEC-20260924-afdc3b R-CG; CORR-20260924-432f43 item 1)",
                "disposition": ("COVERED BY CG-2..CG-6 and CC-2..CC-5 (with VC-1, VC-3): never re-solved, recorded (CG-3, CC-4), "
                                "pre-measured (DV-17), compared by REG-1 unchanged, its consumers disposed of by CC-2 with VC-1, "
                                "counted by DV-11; its launch bound to RB-1 (e) by RJ-1 (callgrind_result_present; LKA-9)")}}

LAUNCH_KINDS = {  # RJ-4 (a): the six production call sites of v2_solver.run_child and each kind's lost-record detector
    "LK-1": {"site": "implementation-v2/v2_driver.py 101 (child_job)", "stdout_form": "child/<tag>.stdout",
             "detector": "the spec file child/<tag>.spec.json the frozen driver writes before the launch (98-99), named as argv's last element (100)"},
    "LK-2": {"site": "implementation-v2/v2_driver.py 166 (solve; S-1)", "stdout_form": "solver/<tag>.ms.log",
             "detector": "RI-1 (a): RB-1 attempt records, RL-2 pass-through records, the SE-3 event, the site counters"},
    "LK-3": {"site": "implementation-v2/v2_solver.py 517 (callgrind_instructions)", "stdout_form": "solver/<tag>.callgrind.stdout",
             "detector": "RJ-1: RB-1 (e) callgrind_result_present (a key-membership test on the returned solve result; LKA-9)"},
    "LK-4": {"site": "implementation-v2/v2_driver.py 650 (cmd_anchor_identity)", "stdout_form": "comparator/stdout.log",
             "detector": "RJ-3: raw-result.json comparator.child"},
    "LK-5": {"site": "implementation-v2-a1/a1_health.py 147 (run_system; S-2)", "stdout_form": "health/<tag>.ms.log",
             "detector": "RI-1 (a): RB-1 attempt records, the HR-3 event, the site counter"},
    "LK-6": {"site": "implementation-v2-a1/a1_pari.py 96 (curve_facts)", "stdout_form": "pari/<tag>.gp.stdout",
             "detector": "RJ-2: the pre-launch script pari/<tag>.gp (a1_pari.py 91-93), named as argv's last element (94)"}}

VALUE_TABLE = {
    "classes": {"alpha": "a reader of the result the SE-3 (S-1) or HR-3 (S-2) wrapper RETURNS, or of a value copied or derived from it",
                "beta": "a reader of a file the RECORDED attempt left under its original name (<tag>.ms, .ms.out, .ms.log, .ms.err)",
                "frozen-body": "the frozen solve() / run_system() bodies and the frozen functions they call inside the wrapped call",
                "gamma": "the approved wrapper and recorder bodies and the functions they call to implement SE-2 / SF-n / SC-11 / HR-n / CG-3 / CC-4 / RB-1 / RL-1 / RL-2 / RK-1 / RF-1 / RG-1 (VC-1 (a))",
                "epsilon": "the SE-2 event record, the RB-1 attempt records, the RL-2 pass-through records, the RL-1 launch records and every value derived from them (VC-1 (b))"},
    "values": {"V-1": "the record res['instructions_callgrind'] and its child mapping (v2_solver.py lines 519-547)",
               "V-2": "the REG-1 verdict and report (disposition CG-4, unchanged)",
               "V-3": "manifest resources.child_rlimit_as_read_back_by_getrlimit (disposition CC-3 at E2; recorded / reported at E5, E6)",
               "V-4": "the frozen checker's verdict and the r4 verdict (as frozen; CC-3 when attributable to V-3's callgrind entry; RB-4 (b), RK-3 (b))",
               "V-5": "the CG-3 records in solver-events.json (site v2_driver.solve/callgrind): record and report only (VA-6 (c))",
               "V-6": "the callgrind log files <tag>.callgrind.stdout / .stderr and the removed <tag>.callgrind.out / <tag>.cg.ms.out",
               "V-7": "integrity hashes of whole files carrying S-3 data against a recorded hash of the SAME file (VC-1 (e); VA-6 (a))"},
    "rows": {"K-1": "r2_reg1.compare (b) and its r3 / r4 copies r3_reg1.compare, r4_reg1.compare (b): disposition CG-4, unchanged",
             "K-2": "the run wrappers' collect(raw, 'rlimit_as_child_getrlimit') and the RB-2 / RL-3 collector (any r4 derivative): records only",
             "K-3": "r1_reg1.compare: retired; no r4 import from implementation-v2-r1/ (CC-5)",
             "K-4": "the copies into fixture and cell target rows (v2_driver.py lines 360, 1180): recorded copies",
             "K-5": "the frozen checker's walk and serialization test, find_solver_records (E7): no disposition needed",
             "K-6": "a1_driver.phase_b_check and its use by cmd_aggregate_a1: disposition V-7"}}


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


def rc4c_equal(r4plan, frozen, declared, M):
    """RC-4 (c), the WRITER's implementation (DV-5 has its own, independent code path)."""
    inv = {v: k for k, v in M.items()}
    r, f = copy.deepcopy(r4plan), copy.deepcopy(frozen)
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
    r1r2, r3 = set(), set()
    for path in (R.PLAN_V2_R1, R.PLAN_A1_R1, R.PLAN_V2_R2, R.PLAN_A1_R2):
        r1r2 |= {p["run_id"] for p in R.load_json(path)["packages"]}
    for path in (R.PLAN_V2_R3, R.PLAN_A1_R3):
        r3 |= {p["run_id"] for p in R.load_json(path)["packages"]}
    forbidden_images = v1 | frozen | set(R.RETIRED_ALL) | set(R.USED_V2) | set(R.USED_R3) | r1r2 | r3
    if len(M) != 42 or len(set(M.values())) != 42 or set(M.values()) & forbidden_images or set(M) != frozen:
        raise SystemExit("REFUSING: M is not a bijection from the 42 frozen ids onto 42 fresh ids (RC-4 (a); R4S-5)")
    if r1r2 != set(R.RETIRED_R1) | set(R.RETIRED_R2):
        raise SystemExit("REFUSING: the r1 / r2 plan ids differ from the retirement lists")
    if r3 != set(R.RETIRED_R3) | set(R.USED_R3) or len(R.RETIRED_R3) != 38 or len(R.RETIRED_ALL) != 162 or len(set(R.RETIRED_ALL)) != 162:
        raise SystemExit("REFUSING: the r3 plan ids differ from the 38 retired + 4 kept ids, or the retired set is not 162 distinct ids")
    unused_v2 = [i for i in v2_order if i not in R.USED_V2]
    if sorted(unused_v2) != sorted(R.RETIRED_V2_UNUSED) or sorted(a1_order) != sorted(R.RETIRED_A1_UNUSED):
        raise SystemExit("REFUSING: retirement lists differ from the paristack PS-3 enumeration")
    return v2, a1, m2, m1, M, v2_order, a1_order


def branch_evidence(dv2_path, dv3_path):
    """The PS-1 branch evidence, quoted from this stage's DV-2 and DV-3 records (the writer refuses without both)."""
    dv2, dv3 = R.load_json(dv2_path), R.load_json(dv3_path)
    if dv2.get("pass") is not True or dv3.get("pass") is not True:
        raise SystemExit("REFUSING: DV-2 and DV-3 must both have passed on the delivered r4 configuration code before the plans are written")
    exc = ((dv3.get("record") or {}).get("call") or {}).get("exception")
    pts = sorted(dv2.get("points") or {})
    return ("r4 stage development checks on the delivered r4 configuration code (implementation-v2-r4.md section 4): DV-3 reproduced %r at "
            "(16777291, n = 3) without the configuration; DV-2 passed under P-A at %s in two fresh processes each (the r4 v2 entry's "
            "configuration up to dispatch: RC-3 redirections, the SE-3 replacement, the RL-1 launch recorder and the RL-5 install read-back, "
            "the HR-3 read-back), with the RC-2 read-backs, the RC-5 Hasse and second-point checks and the RC-5 gp cross-checks; no P-B "
            "trigger condition (i)-(iii) occurred" % (exc, ", ".join(pts)))


def reg1_block(m2):
    ex_sha = R.sha256_file(R.REG1_EXCLUSION_LIST)
    return {
        "id": "REG-1",
        "d_branch": R.REG1_D_BRANCH,
        "rule": ("G1 (candidate_run, the r4 image of reference_run) must reproduce reference_run on its deterministic content before G2 is "
                 "admitted (paristack PS-4 regression_REG-1 as amended by the incorporated solverevent SE-4, (d) branch d-parsed by "
                 "seedresolve SF-4; launchcover CG-4 unchanged; readbackfull RL-7 and readbackclose RK-6: unchanged). Evaluated by "
                 "r4_run_wrapper.py (R-7) before G2 and before every later package of either r4 plan. REG-1 fails if the candidate's "
                 "solver-events.json is missing, does not parse or records an SE-2 (4) / HR-5 consistency violation (a recording failure "
                 "included). A REG-1 failure ends R2-r4 at the gate before G2 and is read as 'the repair layer is not behaviour-neutral at "
                 "4111, or the pipeline is non-deterministic', never as a result."),
        "reference_run": "RUN-GFPN-ac4487",
        "reference_receipt": os.path.relpath(R.RECEIPT_V2_PHASE_B, R.REPO),
        "reference_integrity": "every reference file read is verified against the receipt's path_sha256 first; a mismatch is fatal",
        "candidate_run": m2["RUN-GFPN-ac4487"],
        "comparator": "experiments/EXP-GFPN-05ff43/implementation-v2-r4/r4_reg1.py",
        "compared": ["(a) solver/*.ms: same file set, byte-identical",
                     "(b) raw-result.json: run_status/failure_class/gate_pass; targets, planted_targets, replaced_fresh_targets (whole, minus exclusions) and the D table; structure_checks; fixture_F1; fixture_F2a; fixture_F2b; fixture_F3; group; rescaling; curve_checks; fresh targets' k (from certificates) and x_R; certificate block; metrics minus wall_seconds",
                     "(c) certificates/*.json: same file set, equal as JSON after the declared exclusions",
                     "(d) d-parsed: solver/*.ms.out of the recorded attempts: same file set; equal parse kind, header degree, eliminating-polynomial degree, square-free flag, F_p-rational solution set (as a set, v2_solver.rational_solutions) and D; no tolerance"],
        "outside_compared_sets": "solver-events.json (with its RB-1, RL-1 and RL-2 records) and solver/*.ssf-attempt<k> files: listed with sha256; solver-events.json quoted in full; not exclusions; REG-1 fails if solver-events.json is missing, does not parse or records a consistency violation (S-1 / S-2 events and the top-level flag; VA-6 (b))",
        "exclusion_list": "experiments/EXP-GFPN-05ff43/implementation-v2-r4/reg1-exclusion-list.json",
        "exclusion_list_sha256": ex_sha,
        "exclusion_list_note": ("X1..X17 carried verbatim (byte-identical to implementation-v2-r3/reg1-exclusion-list.json, itself "
                                "byte-identical to the r2 and r1 lists); nothing added (SE-4 (e); CG-4); X16 and X17 remain open review items"),
        "pre_declared_readings": ("launchcover CG-4 (a REG-1 (b) difference in any instructions_callgrind field FAILS REG-1 as frozen; "
                                  "G1 is never re-run; the lineage stops at an impediment) and consumercover CC-3 (a frozen-checker "
                                  "failure attributable to the callgrind child's read-back is an envelope outcome at S-3), reporting only"),
    }


def admission_block():
    return {
        "rule_RB-4": ("The r4 run wrapper admits a package that requires the repaired gate (every post-gate v2-r4 package and every "
                      "v2-a1-r4 package) only if, for EACH of G1..G4 of trial-plan-v2-r4.json: (a) raw-result run_status is "
                      "completed_valid and gate_pass is true (unchanged); AND (b) the r4 checker (the frozen v2_check_run in its own "
                      "process, RC-3 (e), plus the r4 checks), run by the wrapper at admission time on that gate package, exits 0; AND "
                      "REG-1 (d-parsed) passed (unchanged). Addendum packages 2-11 additionally require the controls_a1 image to "
                      "satisfy (a) and (b). The admitted package's manifest records gate.gate_package_checker per gate package "
                      "(command, exit status, output verbatim). A failing (b) is refused and recorded; it ends the stage at the gate. "
                      "A failing item attributable to V-3's callgrind entry is read by CC-3; any other is read as frozen (consumercover "
                      "V-4); either way the lineage STOPS at an impediment for a new Coordinator decision, and neither is ever evidence."),
        "rule_RL-4_RK-3_RF-3_RF-5": ("In addition, a package that reads, or is required to follow, another r4-lineage package is admitted "
                                     "only if that package's r4 verdict (readbackclose RK-3 (b) with failclosed RF-2 and RF-3: PASS, or "
                                     "PASS_ZL for a package that is neither a gate package nor the controls_a1 image) admits it, for the "
                                     "named reads X-03 (G1 read by REG-1 for every package after G1), X-04 (every requires entry), X-07 "
                                     "(_load_build), X-08 (_prior_cells, _condition_met), X-09 (cmd_aggregate), X-10 "
                                     "(cmd_aggregate_a1), X-11 (resolve_replacement / _resolve contingency manifests) and X-13 (RF-5); "
                                     "the manifest records gate.required_package_checker per read package. The F-4 package stays NOT "
                                     "blocking (RK-3 (d)): the requires entry naming it is admitted by R-8's existence test only and its "
                                     "verdict is recorded and gates nothing. Every other FAIL refuses the dependant as a designed stop "
                                     "(RF-3 (b)) for a new Coordinator decision; never evidence."),
        "verdict": ("PASS iff the frozen checker exits 0 and every r4 check passes (RF-3 (a): every launch record of class (A), (B) or "
                    "(C) read with RG-1 (d); raw_result_writer driver; no recorder-foreign file; no recorder gap or named gap of RL-3 as "
                    "launchkind reads it; no `undetermined` value). PASS_ZL per RK-3 (b) (i)-(v) and RF-2 (vi)-(viii). Otherwise FAIL."),
        "checker": "experiments/EXP-GFPN-05ff43/implementation-v2-r4/r4_check_run.py (run by the wrapper in its own process; the frozen checker in a separate process)"}


def repair_block(plan_kind, derived_from, sha, declared, evidence):
    amds = R.repair_amendments()
    for k in R.REPAIR_KEYS:
        amds[k]["path"] = os.path.relpath(R.REPAIR_PATHS[k], R.REPO)
    amds["paristack"]["conditions_note"] = "RC-1..RC-13 re-pointed to r4 by DEC-20260924-daf670 LKA-3 (DEC-20260924-e52eec VA-3 re-pointed); RC-6 read through CORR-20260923-111265"
    amds["seedresolve"]["conditions_note"] = "SC-1..SC-11 re-pointed to r4 (DEC-20260924-e52eec VA-3 as LKA-3 re-points it)"
    amds["valueclose"]["conditions_note"] = "VA-1..VA-12 re-pointed to r4 by readbackcover's reading_rule and DEC-20260924-daf670 LKA-3"
    amds["launchkind"]["in_file_status_note"] = ("the paristack, seedresolve, solverevent, healthresolve, launchcover, consumercover, "
                                                 "valueclose, readbackcover, readbackfull, readbackclose, failclosed, childend, gapattr, "
                                                 "attcount and launchkind files read status draft / approved_by null; the approvals are the "
                                                 "committed decisions (LKA-1)")
    return {
        "amendments": amds,
        "rules": {"RB": ["RB-%d" % i for i in range(1, 9)], "RL": ["RL-%d" % i for i in range(1, 9)], "RK": ["RK-%d" % i for i in range(1, 8)],
                  "RF": ["RF-%d" % i for i in range(0, 9)], "RG": ["RG-%d" % i for i in range(1, 10)], "RH": ["RH-%d" % i for i in range(1, 9)],
                  "RI": ["RI-%d" % i for i in range(1, 7)], "RJ": ["RJ-%d" % i for i in range(1, 9)]},
        "approval": {"decision": R.LAUNCHKIND_APPROVAL, "conditions": R.LAUNCHKIND_CONDITIONS},
        "corrections": R.CORRECTIONS,
        "bound_hashes_seventeen": {os.path.relpath(p, R.REPO): h for p, h in R.BOUND_HASHES},
        "K": R.K,
        "max_attempts_per_call": R.K + 1,
        "spacing_s": R.SPACING_S,
        "resolve_cap": R.RESOLVE_CAP_RULE,
        "ssf_signature": "seedresolve SF-1 clauses (i)-(v); at a1_health.run_system as healthresolve HR-2 applies them",
        "reg1_d_branch": R.REG1_D_BRANCH,
        "sites": SITES_CC1,
        "launch_kinds_RJ-4": LAUNCH_KINDS,
        "unreachable_sites": ("U-1..U-5 (consumercover CC-1): v1 implementation/run_wrapper.py lines 23/36 and 98, "
                              "implementation/symmetrize.py lines 392/399, and the two review-scratch k5k7 scripts; listed, not a bar; "
                              "no r4 file imports or executes them"),
        "dv17_R": R.DV17_R,
        "value_table": VALUE_TABLE,
        "driver_pythonhashseed": R.DRIVER_PYTHONHASHSEED,
        "ps1_branch": R.PS1_BRANCH,
        "ps1_values": {"parisize": R.PARISIZE, "parisizemax": R.PARISIZEMAX},
        "ps1_api": R.PARI_API,
        "ps1_branch_evidence": evidence,
        "ps1_branch_final": "final for this protocol version (paristack PS-1 finality); changing it needs a new Coordinator decision",
        "rc2_exit_parisize_semantics": ("requested: on this host (cypari2 2.2.0, PARI 2.15.4) default(parisize) reports the configured size "
                                        "after the stack grew (r4 semantics probe), so the exit read-back must equal 67108864 exactly; "
                                        "parisizemax must equal 536870912 exactly"),
        "entry_point": "experiments/EXP-GFPN-05ff43/implementation-v2-r4/%s" % ("r4_entry_v2.py" if plan_kind == "v2" else "r4_entry_a1.py"),
        "resolve_wrappers": "experiments/EXP-GFPN-05ff43/implementation-v2-r4/r4_resolve.py (SE-3 at v2_driver.solve; HR-3 at a1_health.run_system; RB-1; RL-2; CG-3 recording; the single event writer)",
        "launch_recorder": "experiments/EXP-GFPN-05ff43/implementation-v2-r4/r4_recorder.py (RL-1 at v2_solver.run_child with RK-1, RF-1, RG-1, RG-4 (a))",
        "recorder_gaps": "experiments/EXP-GFPN-05ff43/implementation-v2-r4/r4_gaps.py (RL-3 as launchkind's reading_rule words it; LKA-10)",
        "run_wrapper": "experiments/EXP-GFPN-05ff43/implementation-v2-r4/r4_run_wrapper.py",
        "checker": "experiments/EXP-GFPN-05ff43/implementation-v2-r4/r4_check_run.py",
        "launch_form_RB-8": ("( setsid -w python3 -B <r4 wrapper> <RUN-ID> > <out> 2>&1 < /dev/null; echo \"wrapper_exit=$?\" >> <out> ) &, "
                             "recorded verbatim with the status; no outer guard (no timeout, ulimit, nice, taskset or wrapper script)"),
        "GFPN_V2_CAP_BYTES": "unset in every wrapper environment (DEC-20260924-daf670 LKA-11 (d), LKA-13); the r4 wrapper and entries record whether it is set",
        "derived_from": {"plan": os.path.relpath(derived_from, R.REPO), "sha256": sha,
                         "bound_by": "phase A of TASK-20260923-0fa03f" if plan_kind == "v2" else "phase A of TASK-20260923-4ff597"},
        "derivation": "RC-4 (c): after deleting the declared key paths and applying the inverse of M, the plan equals derived_from as canonical JSON",
        "declared_key_paths": declared,
        "written_in": "the r4 stage (TASK-20260924-d91a96), implement only; no repaired run package exists",
    }


def ordered(src, changes, insert_after):
    """Rebuild src with changed values in place and new keys inserted after anchor keys (deterministic order)."""
    out = {}
    for k, v in src.items():
        out[k] = changes.get(k, v)
        for nk, nv in insert_after.get(k, []):
            out[nk] = nv
    return out


def build(dv2_path, dv3_path):
    v2, a1, m2, m1, M, v2_order, a1_order = inputs()
    evidence = branch_evidence(dv2_path, dv3_path)
    reg1 = reg1_block(m2)
    adm = admission_block()
    retired = {"source": "DEC-20260923-c1fb69 R-1 (4); paristack PS-3 retirement; DEC-20260923-582d6b R-4; DEC-20260924-15a77a SC-10; "
                         "DEC-20260924-bea197 R-8; DEC-20260924-1ce186 R-5; readbackcover RB-6 (c); DEC-20260924-daf670 LKA-3; refused by "
                         "r4_run_wrapper.py R-2",
               "used_v2_ids_kept_as_records_never_rerun": R.USED_V2,
               "used_r3_gate_ids_kept_as_records_never_rerun_never_reused": R.USED_R3,
               "unused_v2_ids_retired": R.RETIRED_V2_UNUSED,
               "unused_a1_ids_retired": R.RETIRED_A1_UNUSED,
               "r1_ids_retired_unused": R.RETIRED_R1,
               "r2_ids_retired_unused": R.RETIRED_R2,
               "r3_ids_retired_unused": R.RETIRED_R3,
               "n_retired": len(R.RETIRED_ALL),
               "note": "retired ids never produce a package and are reported unused in every later accounting"}
    ceiling = ("DC-7 A-7 with DEC-20260923-8b2dbf AA-5 (e): at most 48 run packages in the lineage, counted over the run directories of "
               "all TEN plans (frozen v2 and v2-a1, both r1, both r2, both r3, both r4). Existing: 6 (retired_ids.used_v2_ids_kept_as_records_never_rerun and "
               "retired_ids.used_r3_gate_ids_kept_as_records_never_rerun_never_reused). Reserved by the r4 plans: 31 + 11 = 42. Total 6 + 31 + 11 = 48 of 48; no slack: a contingency "
               "id is used only under R-12. The 162 retired ids (29 v2, 11 v2-a1, 42 r1, 42 r2, 38 r3) never produce a package and do not "
               "count (readbackcover RB-6 (e); DEC-20260924-daf670 LKA-13).")
    # ---- trial-plan-v2-r4.json
    p = map_strings(copy.deepcopy(v2), M)
    gate = dict(p["gate"])
    gate["regression"] = reg1
    gate["admission"] = adm
    p = ordered(p, {"protocol_version": R.PROTOCOL_V2_R4, "task_id": R.TASK_RUNS_V2,
                    "archived_by": "%s phase A (Coordinator)" % R.ARCHIVE_TASK, "gate": gate},
                {"archived_by": [("written_by_task", R.TASK_STAGE), ("repair", repair_block("v2", R.PLAN_V2, R.PLAN_V2_SHA256, DECLARED_KEYS_V2, evidence))],
                 "v1_ids_never_reused": [("v2_ids_never_reused", list(v2_order)), ("a1_ids_never_reused", list(a1_order)),
                                         ("retired_ids", retired), ("id_map", m2), ("ceiling_note", ceiling)]})
    # ---- trial-plan-v2-a1-r4.json
    q = map_strings(copy.deepcopy(a1), M)
    gate = dict(q["gate"])
    gate["regression"] = reg1
    gate["admission"] = adm
    rb = repair_block("a1", R.PLAN_A1, R.PLAN_A1_SHA256, DECLARED_KEYS_A1, evidence)
    rb["v2_gate_repointed_to"] = {"v2_blocking_packages": [m2[g] for g in v2["gate"]["blocking_packages"]], "plus": "REG-1 (d-parsed)",
                                  "addendum_blocking_package": m1[a1["gate"]["addendum_blocking_package"]],
                                  "aggregate_a1_inputs": "--v2-runs and --v2-aggregate mapped through id_map_v2; --a1-runs through id_map; "
                                                         "the repaired v2 bytes are read from the TASK-20260924-4a47e5 phase-B receipt "
                                                         "(RC-8 re-pointed; VC-6 (c)); a failure of that check is read by V-7",
                                  "phase_b_receipt": os.path.relpath(R.RECEIPT_R4_PHASE_B, R.REPO)}
    q = ordered(q, {"protocol_version": R.PROTOCOL_A1_R4, "task_id": R.TASK_RUNS_A1, "written_by_task": R.TASK_STAGE,
                    "archived_by": "%s phase A (Coordinator)" % R.ARCHIVE_TASK, "gate": gate},
                {"archived_by": [("repair", rb)],
                 "v2_ids_never_reused": [("frozen_v2_ids_never_reused", list(v2_order)), ("a1_ids_never_reused", list(a1_order)),
                                         ("retired_ids", retired), ("id_map", m1), ("id_map_v2", m2), ("ceiling_note", ceiling)]})
    for name, plan, frozen, declared in (("trial-plan-v2-r4.json", p, v2, DECLARED_KEYS_V2), ("trial-plan-v2-a1-r4.json", q, a1, DECLARED_KEYS_A1)):
        ok, h1, h2 = rc4c_equal(plan, frozen, declared, M)
        if not ok:
            raise SystemExit("REFUSING: %s fails the RC-4 (c) equality (%s != %s)" % (name, h1, h2))
        if plan["watchdogs"] != v2["watchdogs"]:
            raise SystemExit("REFUSING: %s watchdogs differ from trial-plan-v2.json" % name)
        if R.forbidden_ids_in_text(json.dumps(plan)):
            raise SystemExit("REFUSING: %s carries a forbidden task id" % name)
    return p, q, M


def render(plan):
    return json.dumps(plan, indent=1, ensure_ascii=False) + "\n"


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    ap.add_argument("--dv2", required=True)
    ap.add_argument("--dv3", required=True)
    a = ap.parse_args()
    p, q, M = build(a.dv2, a.dv3)
    outs = ((R.PLAN_V2_R4, render(p)), (R.PLAN_A1_R4, render(q)))
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
