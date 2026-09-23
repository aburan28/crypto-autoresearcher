#!/usr/bin/env python3
"""TASK-20260923-5f9b82 (J7): compare the sealed blind re-derivation
(TASK-20260923-7a2cd4) with RUN-CERTBIN-3b7e05, item by item, per CP-2.

Run from the repository root:
    python3 -B coordination/review/certbin-20260923-c51f07/reviews/TASK-20260923-5f9b82/checks/compare_j7.py

What it reads (archived bytes only; every file is hash-checked against its
archive receipt AND against the git blob at HEAD before use):
  - the re-deriver's directory (TASK-20260923-d04c5e receipt)
  - blind/blind-inputs.json and blind-inputs-key.json (TASK-20260923-e3b590 receipt)
  - the run files named in the card (TASK-20260923-c2e57b receipt;
    manifest_v2.yaml via the TASK-20260923-e3b590 prior_commit_bindings)
  - impl/ (TASK-20260923-c2e57b receipt), used ONLY to recompute the affine
    forms a_k of the 3 unsatisfiable references, which the run did not
    archive as a_k (it archived a0 and a_nonzero only). That is 3 archived
    instances; declared in comparison.json.
  - SUPPLEMENTARY, declared: the run's archived checkpoint
    checkpoint/p2-F-S3-D4.json.gz (inside the receipt-verified run package),
    which holds the run's RUN-TIME reference T_set content and affine forms.

What it writes: comparison.json in this task directory, and nothing else.
It never writes into impl/ (bytecode is disabled before import).
"""
import sys
sys.dont_write_bytecode = True

import datetime
import gzip
import hashlib
import json
import os
import subprocess
from fractions import Fraction

REPO = os.getcwd()
REV = "coordination/review/certbin-20260923-c51f07"
J6 = f"{REV}/reviews/TASK-20260923-7a2cd4"
ME = f"{REV}/reviews/TASK-20260923-5f9b82"
EXP = "experiments/EXP-CERTBIN-4e92d7"
RUN = f"{EXP}/runs/RUN-CERTBIN-3b7e05"
RCPT_D04 = f"{REV}/archives/TASK-20260923-d04c5e/snapshot-receipt.json"
RCPT_E3B = f"{REV}/archives/TASK-20260923-e3b590/snapshot-receipt.json"
RCPT_C2E = "coordination/design/certbin-trace-20260923-5d0b8e/archives/TASK-20260923-c2e57b/snapshot-receipt.json"

GRAN_RUN = {"T_rank": "rank", "T_set": "set", "T_strict": "strict", "T_ops": "ops"}
HASH_RUN = {"T_rank": "h_rank", "T_set": "h_set", "T_strict": "h_strict", "T_ops": "h_ops"}


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def git_blob(path):
    return subprocess.run(["git", "show", f"HEAD:{path}"], capture_output=True, check=True).stdout


def canon(o):
    return json.dumps(o, separators=(",", ":"))


def sha_canon(o):
    return hashlib.sha256(canon(o).encode()).hexdigest()


# ---------------------------------------------------------------------------
# CP-1: verify before comparing
# ---------------------------------------------------------------------------
def verify_receipt(rcpt_path, only=None):
    rc = json.load(open(rcpt_path))
    out = {"receipt": rcpt_path, "files": {}, "all_ok": True}
    for p, h in rc["path_sha256"].items():
        if only is not None and not any(p.startswith(o) for o in only):
            continue
        wt = open(p, "rb").read()
        hb = sha_bytes(git_blob(p))
        hw = sha_bytes(wt)
        ok = (hb == h == hw)
        out["files"][p] = {"receipt_sha256": h, "head_blob_sha256": hb, "working_tree_sha256": hw, "ok": ok}
        out["all_ok"] &= ok
    return out, rc


cp1 = {}
d04, rc_d04 = verify_receipt(RCPT_D04)
committed = subprocess.run(["git", "ls-tree", "-r", "--name-only", "HEAD", J6 + "/"],
                           capture_output=True, text=True, check=True).stdout.split()
d04["committed_file_set_equals_receipt_set"] = set(committed) == set(rc_d04["path_sha256"])
cp1["1_rederiver_directory_vs_d04c5e_receipt"] = {
    "n_files": len(d04["files"]), "all_hashes_equal": d04["all_ok"],
    "committed_file_set_equals_receipt_set": d04["committed_file_set_equals_receipt_set"],
    "result": "PASS" if (d04["all_ok"] and d04["committed_file_set_equals_receipt_set"]) else "FAIL",
}
seal = git_blob(f"{J6}/seal.txt").decode()
seal_hash = seal.split()[1]
rd_hash = sha_bytes(git_blob(f"{J6}/rederivation.json"))
cp1["2_seal_vs_rederivation"] = {"seal_text": seal, "sha256_rederivation_json": rd_hash,
                                 "result": "PASS" if seal_hash == rd_hash else "FAIL"}
e3b, rc_e3b = verify_receipt(RCPT_E3B)
bi = e3b["files"][f"{REV}/blind/blind-inputs.json"]
bk = e3b["files"][f"{REV}/blind-inputs-key.json"]
cp1["3_blind_inputs_vs_e3b590_receipt"] = {
    "blind_inputs": bi, "blind_inputs_key": bk,
    "receipt_extraction_blind_inputs_sha256": rc_e3b["extraction"]["blind_inputs_sha256"],
    "result": "PASS" if (bi["ok"] and bk["ok"] and bi["receipt_sha256"] == rc_e3b["extraction"]["blind_inputs_sha256"]) else "FAIL",
}
# the run package and impl/ against the run snapshot receipt (binding for the other side of the comparison)
c2e, rc_c2e = verify_receipt(RCPT_C2E)
cp1["run_package_and_impl_vs_c2e57b_receipt"] = {"n_files": len(c2e["files"]), "all_hashes_equal": c2e["all_ok"],
                                                 "result": "PASS" if c2e["all_ok"] else "FAIL"}
mv2 = f"{RUN}/manifest_v2.yaml"
mv2_h = sha_bytes(git_blob(mv2))
cp1["manifest_v2_vs_e3b590_prior_binding"] = {
    "sha256": mv2_h, "bound": rc_e3b["prior_commit_bindings"][mv2]["sha256"],
    "result": "PASS" if mv2_h == rc_e3b["prior_commit_bindings"][mv2]["sha256"] == sha_bytes(open(mv2, "rb").read()) else "FAIL"}
for k, v in cp1.items():
    if v["result"] != "PASS":
        raise SystemExit(f"CP-1 FAILED at {k}; refusing to compare")

# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------
rd = json.load(open(f"{J6}/rederivation.json"))
key = json.load(open(f"{REV}/blind-inputs-key.json"))
blind = json.load(open(f"{REV}/blind/blind-inputs.json"))
refs_run = json.load(open(f"{RUN}/references.json"))["F-S3"]["references"]
sizing = json.load(open(f"{RUN}/sizing.json"))["per_reference"]["F-S3"]["D4"]
haz = json.load(open(f"{RUN}/pivot-hazards.json"))["families"]["F-S3"]["D4"]
cell = json.load(open(f"{RUN}/cell-summary.json"))["families"]["F-S3"]["D4"]
curve = json.load(open(f"{RUN}/curve.json"))
oplog = {}
for line in gzip.open(f"{RUN}/F-S3-reference-oplogs-D4.jsonl.gz", "rt"):
    r = json.loads(line)
    oplog.setdefault(r["ref"], []).append(r)
tgt_run = {}
for line in gzip.open(f"{RUN}/targets-F-S3.jsonl.gz", "rt"):
    r = json.loads(line)
    if r["D"] == 4:
        tgt_run[r["idx"]] = r

REFMAP = key["references"]                       # REF-x -> U1/U2/U3/S1/S2
TGTMAP = {p: int(i) for p, i in key["targets"].items()}   # position str -> run idx

counts = {"agree": 0, "disagree": 0, "encoding_only": 0}
disagreements = []
by_item = {}


def item(scope, inst, name, rederived, run, run_source, rederived_source, eq=None, note=None, floor_ceiling=None):
    agree = (rederived == run) if eq is None else eq
    rec = {"rederived": rederived, "run": run, "agree": bool(agree),
           "run_source": run_source, "rederived_source": rederived_source}
    if note:
        rec["note"] = note
    counts["agree" if agree else "disagree"] += 1
    b = by_item.setdefault(f"{scope}:{name}", {"agree": 0, "disagree": 0})
    b["agree" if agree else "disagree"] += 1
    if not agree:
        disagreements.append({"scope": scope, "instance": inst, "item": name,
                              "rederived": rederived, "run": run})
    return rec


R4, C4 = 2924, 4048

# ---------------------------------------------------------------------------
# Per reference
# ---------------------------------------------------------------------------
references_out = {}
tset_reconstruction = {}
for lab in ["REF-a", "REF-b", "REF-c", "REF-d", "REF-e"]:
    U = REFMAP[lab]
    rr = refs_run[U]
    r4 = rr["D4"]
    q1 = rd["Q1"]["references"][lab]
    q2 = rd["Q2"]["references"][lab]
    q3h = rd["Q3"]["hashes"]["references"][lab]
    q3c = rd["Q3"]["reference_content"][lab]
    q4 = rd["Q4"][lab]
    ir = rd["instance_records"]["references"][lab]
    sz = sizing[U]
    it = {}
    it["x_R (mapping sanity)"] = item("ref", lab, "x_R", q1["x_R"], rr["x_R"], "references.json F-S3.references.%s.x_R" % U, "Q1")
    it["degenerate"] = item("ref", lab, "degenerate", q1["degenerate"], rr["x_R"] < 512,
                            "derived: references.json x_R < 512 (the run records no per-reference degenerate flag; reference_rule excludes degenerate x_R, I-5)",
                            "Q1.degenerate")
    for route in ["s_route_A_rootfinding", "s_route_B_exhaustive_descended", "s_route_C_direct_field_enumeration"]:
        it[f"s ({route})"] = item("ref", lab, "s", q1[route], rr["s"], f"references.json {U}.s", f"Q1.{route}")
    it["arm"] = item("ref", lab, "arm", q1["arm"], rr["arm"], f"references.json {U}.arm", "Q1.arm")
    it["rank_4"] = item("ref", lab, "rank_4", q2["rank_4"], r4["rank"], f"references.json {U}.D4.rank", "Q2.rank_4")
    it["rank_4 (sizing.json)"] = item("ref", lab, "rank_4_sizing", q2["rank_4"], sz["rank"], f"sizing.json F-S3.D4.{U}.rank", "Q2.rank_4")
    it["|Z_4|"] = item("ref", lab, "Z_4", q2["Z_4_size"], r4["Z_size"], f"references.json {U}.D4.Z_size", "Q2.Z_4_size")
    it["|Z_4| (sizing.json)"] = item("ref", lab, "Z_4_sizing", q2["Z_4_size"], sz["Z_size"], f"sizing.json F-S3.D4.{U}.Z_size", "Q2.Z_4_size")
    it["one_in_R4"] = item("ref", lab, "one_in_R4", q2["one_in_R4"], r4["one_in_R"], f"references.json {U}.D4.one_in_R", "Q2.one_in_R4")

    # T_strict content: references.json and the D=4 op log
    run_strict = r4["T_strict"]
    log_pc = [[o["p"], o["c"]] for o in oplog[U]]
    it["T_strict content (references.json)"] = item("ref", lab, "T_strict_content", q3c["T_strict"] == run_strict, True,
                                                    f"references.json {U}.D4.T_strict (len {len(run_strict)})",
                                                    "Q3.reference_content.T_strict",
                                                    eq=(q3c["T_strict"] == run_strict),
                                                    note="value fields hold the content-equality boolean; lengths %d vs %d" % (len(q3c["T_strict"]), len(run_strict)))
    it["T_strict content (op log p,c)"] = item("ref", lab, "T_strict_content_oplog", True, True,
                                               "F-S3-reference-oplogs-D4.jsonl.gz ref=%s (p,c)" % U,
                                               "Q3.reference_content.T_strict", eq=(q3c["T_strict"] == log_pc))
    # T_set content: the run archives only h_set and |Z|. Reconstruct from the run's own T_strict
    # (pivot cols = sorted c_k; Z = complement of pivot rows, a theorem of the declared pivot rule,
    # see validation-report), then CONFIRM the reconstruction against the run's own h_set.
    pivcols = sorted(c for _, c in run_strict)
    prow = {p for p, _ in run_strict}
    Zrec = [i for i in range(R4) if i not in prow]
    tset_rec = [pivcols, Zrec]
    rec_hash = sha_canon(tset_rec)
    tset_reconstruction[lab] = {"run_label": U, "reconstructed_hash": rec_hash, "run_h_set": r4["h_set"],
                                "reconstruction_confirmed_by_run_hash": rec_hash == r4["h_set"]}
    it["T_set content (run content reconstructed from T_strict, confirmed by run h_set)"] = item(
        "ref", lab, "T_set_content", True, True,
        f"reconstructed from references.json {U}.D4.T_strict; sha256 equals run h_set: {rec_hash == r4['h_set']}",
        "Q3.reference_content.T_set", eq=(q3c["T_set"] == tset_rec and rec_hash == r4["h_set"]))
    # hashes
    for g in ["T_rank", "T_set", "T_strict", "T_ops"]:
        it[f"hash {g}"] = item("ref", lab, f"hash_{g}", q3h[g], r4[HASH_RUN[g]], f"references.json {U}.D4.{HASH_RUN[g]}",
                               f"Q3.hashes.references.{lab}.{g}")
    # integrity of the run side: its archived content hashes to its archived hashes
    ops_content = [[o["p"], o["c"], o["X"]] for o in oplog[U]]
    it["run self-consistency: sha256(op log) == run h_ops"] = item(
        "ref", lab, "run_oplog_hash_selfcheck", sha_canon(ops_content), r4["h_ops"],
        f"sha256 of canonical JSON of the archived op log for {U}", "(run side only)",
        note="the op log is the run's archived T_ops content; equality with the re-deriver's T_ops hash therefore compares T_ops CONTENT")
    it["run self-consistency: sha256(T_strict) == run h_strict"] = item(
        "ref", lab, "run_strict_hash_selfcheck", sha_canon(run_strict), r4["h_strict"],
        f"sha256 of canonical JSON of references.json {U}.D4.T_strict", "(run side only)")
    it["run self-consistency: sha256(rank) == run h_rank"] = item(
        "ref", lab, "run_rank_hash_selfcheck", sha_canon(r4["rank"]), r4["h_rank"], "sha256(canon(rank))", "(run side only)")
    # Q4
    sv = sz["saving"]
    run_ops_strict_log = sum(len(o["X"]) for o in oplog[U])
    it["ops_strict (sizing.json)"] = item("ref", lab, "ops_strict", q4["ops_strict"], sv["ops_strict"],
                                          f"sizing.json F-S3.D4.{U}.saving.ops_strict", "Q4.ops_strict")
    it["ops_strict (sum |X_k| over archived op log)"] = item("ref", lab, "ops_strict_oplog", q4["ops_strict"], run_ops_strict_log,
                                                              "sum of len(X) over F-S3-reference-oplogs-D4 for %s" % U, "Q4.ops_strict")
    it["ops_strict (re-deriver instance record sum_X)"] = item("ref", lab, "ops_strict_sumX", ir["D4"]["sum_X"], sv["ops_strict"],
                                                                f"sizing.json {U}.saving.ops_strict", "instance_records.D4.sum_X")
    it["ops_masked_full"] = item("ref", lab, "ops_masked_full", q4["ops_masked_full"], sv["ops_masked_full"],
                                 f"sizing.json {U}.saving.ops_masked_full", "Q4.ops_masked_full")
    it["ops_set"] = item("ref", lab, "ops_set", q4["ops_set"], sv["ops_set"], f"sizing.json {U}.saving.ops_set", "Q4.ops_set")
    ss_rd = Fraction(*q4["saving_strict_exact"])
    ss_run = Fraction(sv["ops_masked_full"], sv["ops_strict"])
    it["saving_strict (exact rational)"] = item("ref", lab, "saving_strict_exact", str(ss_rd), str(ss_run),
                                                f"sizing.json {U}: ops_masked_full/ops_strict", "Q4.saving_strict_exact")
    it["saving_strict (float as archived)"] = item("ref", lab, "saving_strict_float", q4["saving_strict"], sv["saving_strict"],
                                                   f"sizing.json {U}.saving.saving_strict", "Q4.saving_strict")
    st_rd = Fraction(*q4["saving_set_exact"])
    st_run = Fraction(sv["ops_masked_full"], sv["ops_set"])
    it["saving_set (exact rational)"] = item("ref", lab, "saving_set_exact", str(st_rd), str(st_run),
                                             f"sizing.json {U}: ops_masked_full/ops_set", "Q4.saving_set_exact")
    it["saving_set (float as archived)"] = item("ref", lab, "saving_set_float", q4["saving_set"], sv["saving_set"],
                                                f"sizing.json {U}.saving.saving_set", "Q4.saving_set")
    it["(R_4, C_4)"] = item("ref", lab, "R4_C4", [q4["R_4"], q4["C_4"]], [sz["sizes"]["full"]["rows"], sz["sizes"]["full"]["cols"]],
                            f"sizing.json {U}.sizes.full.(rows, cols)", "Q4.(R_4, C_4)")
    it["pivot_cols / R-|Z|"] = item("ref", lab, "pivcols_RminusZ", [q4["pivot_cols"], q4["R_minus_Z"]],
                                    [r4["rank"], R4 - r4["Z_size"]], f"references.json {U}.D4 rank and R_4 - Z_size", "Q4.pivot_cols, Q4.R_minus_Z")
    # cell-summary K_and_replay rank (another run artifact carrying rank)
    it["rank_4 (cell-summary K_and_replay)"] = item("ref", lab, "rank_4_cell", q2["rank_4"], cell["K_and_replay"][U]["rank"],
                                                    f"cell-summary.json F-S3.D4.K_and_replay.{U}.rank", "Q2.rank_4")
    references_out[lab] = {"run_label": U, "items": it}

# ---------------------------------------------------------------------------
# Q6 for the unsatisfiable references: K_exact, K_rank, a0/a_nonzero (archived),
# and the first-64 nonzero-a_k list recomputed with the archived impl/.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(REPO, EXP, "impl"))
import numpy as np  # noqa: E402
from gf2n import TableField  # noqa: E402
from macaulay import MacaulayShape, affine_basis  # noqa: E402
from elim import affine_forms, int_rank  # noqa: E402

F = TableField()
S4 = MacaulayShape(4)
assert (S4.R, S4.C) == (R4, C4)
E0, Ej = affine_basis(F, curve["B"])
planesM = np.stack([S4.build(x) for x in [E0] + Ej])


def rank_flags(avals):
    basis = {}
    out = []
    for v in avals:
        x = v
        while x:
            h = x.bit_length() - 1
            if h in basis:
                x ^= basis[h]
            else:
                basis[h] = x
                break
        out.append(bool(x))
    return out


impl_recompute = {"instances": [], "note": "impl/ recompute of the affine forms on the run's own archived D=4 op log"}
q6_out = {}
for lab in rd["Q5"]["unsat_references"]:
    U = REFMAP[lab]
    q6 = rd["Q6"]["per_reference"][lab]
    hz = haz[U]
    r4 = refs_run[U]["D4"]
    ps = [o["p"] for o in oplog[U]]
    cs = [o["c"] for o in oplog[U]]
    Xs = [np.array(o["X"], dtype=np.int64) for o in oplog[U]]
    a0, a = affine_forms(planesM, ps, cs, Xs)
    a0 = [int(x) for x in a0]
    a = [int(x) for x in a]
    impl_recompute["instances"].append({"reference": U, "x_R": refs_run[U]["x_R"], "steps": len(ps)})
    # run-side consistency: impl recompute vs the run's ARCHIVED a0 / a_nonzero / K_exact / K_rank
    run_consistency = {
        "a0_equals_pivot_hazards_a0": a0 == hz["a0"],
        "a_nonzero_equals_pivot_hazards_a_nonzero": [int(x != 0) for x in a] == hz["a_nonzero"],
        "K_exact_equals_archived": len([x for x in a if x]) == r4["K_exact"] == hz["K_exact"],
        "K_rank_equals_archived": int_rank([x for x in a if x]) == r4["K_rank"] == hz["K_rank"],
    }
    it = {}
    it["steps (len op log)"] = item("q6", lab, "steps", q6["steps"], len(ps), f"op log {U} length", "Q6.steps")
    it["K_exact (references.json)"] = item("q6", lab, "K_exact", q6["K_exact"], r4["K_exact"], f"references.json {U}.D4.K_exact", "Q6.K_exact")
    it["K_exact (pivot-hazards.json)"] = item("q6", lab, "K_exact_haz", q6["K_exact"], hz["K_exact"], f"pivot-hazards {U}.K_exact", "Q6.K_exact")
    it["K_rank (references.json)"] = item("q6", lab, "K_rank", q6["K_rank"], r4["K_rank"], f"references.json {U}.D4.K_rank", "Q6.K_rank")
    it["K_rank (pivot-hazards.json)"] = item("q6", lab, "K_rank_haz", q6["K_rank"], hz["K_rank"], f"pivot-hazards {U}.K_rank", "Q6.K_rank")
    # every step, against what the run DID archive
    rd_a0 = q6["full_affine_forms"]["a_k0"]
    rd_a = q6["full_affine_forms"]["a_k"]
    it["a_k0, all steps (pivot-hazards a0)"] = item("q6", lab, "a0_all_steps", True, True, f"pivot-hazards {U}.a0",
                                                   "Q6.full_affine_forms.a_k0", eq=(rd_a0 == hz["a0"]),
                                                   note=f"{sum(x != y for x, y in zip(rd_a0, hz['a0']))} differing steps of {len(rd_a0)}")
    it["a_k != 0, all steps (pivot-hazards a_nonzero)"] = item("q6", lab, "a_nonzero_all_steps", True, True,
                                                              f"pivot-hazards {U}.a_nonzero", "Q6.full_affine_forms.a_k",
                                                              eq=([int(x != 0) for x in rd_a] == hz["a_nonzero"]),
                                                              note=f"{sum(int(x != 0) != y for x, y in zip(rd_a, hz['a_nonzero']))} differing steps")
    it["a_k, all steps (impl/ recompute)"] = item("q6", lab, "a_k_all_steps_impl", True, True, "impl/ affine_forms on archived op log",
                                                  "Q6.full_affine_forms.a_k", eq=(rd_a == a),
                                                  note=f"{sum(x != y for x, y in zip(rd_a, a))} differing steps")
    it["steps_with_a_k_zero"] = item("q6", lab, "steps_a_zero", q6["steps_with_a_k_zero"], len(ps) - hz["K_exact"],
                                     f"len(op log) - pivot-hazards {U}.K_exact", "Q6.steps_with_a_k_zero")
    # first 64 nonzero, with rank-increment flags (run side: impl recompute)
    nzk = [k for k in range(len(a)) if a[k]][:64]
    flags = rank_flags([a[k] for k in nzk])
    run64 = [{"k": k, "a_k0": a0[k], "a_k": a[k], "increases_rank": f} for k, f in zip(nzk, flags)]
    rd64 = q6["first_64_nonzero"]
    per_step = []
    for x, y in zip(rd64, run64):
        per_step.append({"k": [x["k"], y["k"]], "a_k0": [x["a_k0"], y["a_k0"]], "a_k": [x["a_k"], y["a_k"]],
                         "increases_rank": [x["increases_rank"], y["increases_rank"]], "agree": x == y})
    for j, (x, y) in enumerate(zip(rd64, run64)):
        item("q6", lab, "first64_step", x, y, "impl/ recompute", "Q6.first_64_nonzero")
    it["first-64 nonzero-a_k list (k, a_k0, a_k, increases_rank)"] = {
        "rederived_len": len(rd64), "run_len": len(run64),
        "steps_agree": sum(s["agree"] for s in per_step), "steps_disagree": sum(not s["agree"] for s in per_step),
        "agree": all(s["agree"] for s in per_step) and len(rd64) == len(run64) == 64,
        "run_source": "impl/ affine_forms on the archived D=4 op log (the run archived a0 and a_nonzero, not a_k)",
        "rederived_source": "Q6.first_64_nonzero",
        "rank_increments_in_first_64": [sum(x["increases_rank"] for x in rd64), sum(f for f in flags)],
        "per_step": per_step,
    }
    kr = cell["K_and_replay"][U]
    it["K_exact (cell-summary.json)"] = item("q6", lab, "K_exact_cell", q6["K_exact"], kr["K_exact"],
                                             f"cell-summary F-S3.D4.K_and_replay.{U}.K_exact", "Q6.K_exact")
    it["K_rank (cell-summary.json)"] = item("q6", lab, "K_rank_cell", q6["K_rank"], kr["K_rank"],
                                            f"cell-summary F-S3.D4.K_and_replay.{U}.K_rank", "Q6.K_rank")
    q6_out[lab] = {"run_label": U, "items": it, "impl_recompute_vs_run_archived": run_consistency}

# ---------------------------------------------------------------------------
# SUPPLEMENTARY (declared): the run's RUN-TIME reference summaries in the archived
# checkpoint p2-F-S3-D4.json.gz (part of the receipt-verified run package, not named
# in the card's file list). It carries the run's actual T_set content (row-pass Z)
# and its run-time affine forms a_k, so the T_set and a_k comparisons do not rest
# only on a reconstruction or on a post-hoc impl/ recompute.
# ---------------------------------------------------------------------------
ck = json.load(gzip.open(f"{RUN}/checkpoint/p2-F-S3-D4.json.gz", "rt"))
ck_refs = {r["label"]: r for r in ck["refs"]}
ck_out = {"source": f"{RUN}/checkpoint/p2-F-S3-D4.json.gz", "pid": ck.get("pid"), "per_reference": {}}
for lab in ["REF-a", "REF-b", "REF-c", "REF-d", "REF-e"]:
    U = REFMAP[lab]
    c = ck_refs[U]
    q3c = rd["Q3"]["reference_content"][lab]
    e = {}
    e["checkpoint hashes equal references.json hashes (run-internal)"] = item(
        "ckpt", lab, "ckpt_hashes_selfcheck", [c[h] for h in ("h_rank", "h_set", "h_strict", "h_ops")],
        [refs_run[U]["D4"][h] for h in ("h_rank", "h_set", "h_strict", "h_ops")], "references.json", "checkpoint (run side only)")
    e["T_set content (run-time row-pass Z)"] = item(
        "ckpt", lab, "T_set_content_runtime", True, True, f"checkpoint refs[{U}].T_set", "Q3.reference_content.T_set",
        eq=(q3c["T_set"] == c["T_set"]),
        note="pivot cols %s; Z %s" % ("equal" if q3c["T_set"][0] == c["T_set"][0] else "DIFFER",
                                      "equal" if q3c["T_set"][1] == c["T_set"][1] else "DIFFER"))
    e["T_strict content (run-time)"] = item("ckpt", lab, "T_strict_runtime", True, True, f"checkpoint refs[{U}].T_strict",
                                            "Q3.reference_content.T_strict", eq=(q3c["T_strict"] == c["T_strict"]))
    if lab in rd["Q6"]["per_reference"]:
        f6 = rd["Q6"]["per_reference"][lab]["full_affine_forms"]
        e["a_k, all steps (run-time forms_a)"] = item("ckpt", lab, "a_k_runtime", True, True, f"checkpoint refs[{U}].forms_a",
                                                      "Q6.full_affine_forms.a_k", eq=(f6["a_k"] == c["forms_a"]))
        e["a_k0, all steps (run-time forms_a0)"] = item("ckpt", lab, "a_k0_runtime", True, True, f"checkpoint refs[{U}].forms_a0",
                                                        "Q6.full_affine_forms.a_k0", eq=(f6["a_k0"] == c["forms_a0"]))
    ck_out["per_reference"][lab] = {"run_label": U, "items": e}

# ---------------------------------------------------------------------------
# Convention checks behind the ambiguity table
# ---------------------------------------------------------------------------
from stats import clopper_pearson as impl_cp  # noqa: E402
cp_conv = {}
for lab in rd["Q5"]["unsat_references"]:
    for g in ["T_rank", "T_set", "T_strict"]:
        pr = rd["Q5"]["per_reference"][lab][g]
        run_ci = impl_cp(pr["count"], pr["n"])
        cp_conv[f"{lab}.{g}"] = {"x": pr["count"], "n": pr["n"], "rederived_cp95": pr["clopper_pearson_95"],
                                 "impl_stats_clopper_pearson": run_ci,
                                 "max_abs_diff": max(abs(a - b) for a, b in zip(pr["clopper_pearson_95"], run_ci))}
zero_rows = {"references": {l: rd["instance_records"]["references"][l]["D4"]["zero_rows_in_M4"] for l in REFMAP},
             "targets_with_zero_rows": [p for p, v in rd["instance_records"]["targets"].items() if v["D4"]["zero_rows_in_M4"]]}

AMBIGUITY_TABLE = [
    {"id": "AMB-1", "rederiver": "a_k integer: bit j = coefficient of r_j (LSB = r_0)",
     "run": "same: impl/elim.py:150-158 affine_forms sets bit (j-1) from plane j = M(E^{j-1}); impl/engine.py eval_forms parity(r & a) with r = x_R",
     "same_resolution": True, "evidence": "a_k integers equal at every step for all 3 unsatisfiable references (impl recompute AND run-time checkpoint forms_a)"},
    {"id": "AMB-2", "rederiver": "leading column = smallest column index",
     "run": "same: impl/elim.py:84-88 row_pass lead = lowest set bit of the lowest nonzero word",
     "same_resolution": True, "evidence": "affects only C-PASS; both report C-PASS true on every compared instance"},
    {"id": "AMB-3", "rederiver": "zero rows belong to Z_D",
     "run": "same: impl/elim.py:74-75 appends an all-zero row to Z",
     "same_resolution": True, "evidence": "MOOT at this cell: zero_rows_in_M4 = 0 on all 105 instances (see zero_rows census), so the reading was never exercised"},
    {"id": "AMB-4", "rederiver": "curve draw call pattern: R1 two scalar integers(0, 2^17) calls (primary), R2 and R3 also computed",
     "run": "trial-plan I-1: A = integers(0, 2^17) then B = integers(0, 2^17), B = 0 redrawn and counted; impl/families.py:27-50 draw_curve (a B = 0 draw restarts the (A, B) pair)",
     "same_resolution": True, "evidence": "R1 is I-1. All three readings reproduce curve.json; the first draw was accepted with no rejection, so the rejection branch of either reading was not exercised"},
    {"id": "AMB-5", "rederiver": "M_D(E^j) = the construction applied to the rows of E^j (linearity checked)",
     "run": "same: impl/macaulay.py:118-122 E^j = E(t^j) XOR E^0; impl/driver.py:244-257 planes = [M(E^0), M(E^0'), ..., M(E^16)]",
     "same_resolution": True, "evidence": "a_k0 and a_k agree at every step"},
    {"id": "AMB-6", "rederiver": "column order of E(r) not needed",
     "run": "E's 172 columns in mu order (impl/macaulay.py EQ_MONS; trial-plan I-7 uses it for F-AFF only)",
     "same_resolution": True, "evidence": "no compared quantity depends on it"},
    {"id": "AMB-7", "rederiver": "T_ops match by hash, content confirmed when equal",
     "run": "trial-plan I-17 (content decides, hash cross-checked); impl/engine.py:133-140 ops by hash then X content; set by hash then content (118-119); strict by content",
     "same_resolution": True, "evidence": "the encodings coincide (all 4 hashes equal on all 105 instances), so hash inequality implies content inequality; all 2000 target flags agree"},
    {"id": "AMB-8", "rederiver": "Clopper-Pearson two-sided, equal tails, alpha/2 per tail, over its own classification",
     "run": "impl/stats.py:43-48 clopper_pearson, alpha/2 per tail (equal-tailed exact); run records CP on the full arm, not on the subsample",
     "same_resolution": True, "evidence": "impl clopper_pearson reproduces the Q5 intervals (see cp_convention); classifications agree on all 100 targets"},
    {"id": "AMB-9", "rederiver": "D = 4 only", "run": "the run covers D in {3, 4}; only D = 4 is compared (PD-R4)",
     "same_resolution": True, "evidence": "scope, not a reading"},
]

# ---------------------------------------------------------------------------
# Reference-vs-reference flags (extra; derived from the run's archived hashes)
# ---------------------------------------------------------------------------
rr_out = {}
for a_lab in REFMAP:
    for b_lab in REFMAP:
        for g in ["T_rank", "T_set", "T_strict", "T_ops"]:
            run_eq = refs_run[REFMAP[a_lab]]["D4"][HASH_RUN[g]] == refs_run[REFMAP[b_lab]]["D4"][HASH_RUN[g]]
            rdv = rd["Q3"]["match_flags_reference_vs_reference"][a_lab][b_lab][g]
            rr_out.setdefault(f"{a_lab}~{b_lab}", {})[g] = item("refref", f"{a_lab}~{b_lab}", g, rdv, run_eq,
                                                              "equality of references.json D4 hashes", "Q3.match_flags_reference_vs_reference")

# ---------------------------------------------------------------------------
# Per target
# ---------------------------------------------------------------------------
targets_out = {}
for pos, idx in sorted(TGTMAP.items(), key=lambda kv: int(kv[0])):
    t = tgt_run[idx]
    q1 = rd["Q1"]["targets"][pos]
    q2 = rd["Q2"]["targets"][pos]
    q3h = rd["Q3"]["hashes"]["targets"][pos]
    mf = rd["Q3"]["match_flags_target_vs_reference"][pos]
    it = {}
    it["x_R (mapping sanity)"] = item("tgt", pos, "x_R", q1["x_R"], t["x_R"], f"targets-F-S3 idx={idx} D=4 x_R", "Q1")
    it["degenerate"] = item("tgt", pos, "degenerate", q1["degenerate"], t["degenerate"], "targets.degenerate", "Q1.degenerate")
    for route in ["s_route_A_rootfinding", "s_route_B_exhaustive_descended", "s_route_C_direct_field_enumeration"]:
        it[f"s ({route})"] = item("tgt", pos, "s", q1[route], t["s"], "targets.s", f"Q1.{route}")
    it["arm"] = item("tgt", pos, "arm", q1["arm"], t["stratum"], "targets.stratum", "Q1.arm")
    it["rank_4"] = item("tgt", pos, "rank_4", q2["rank_4"], t["rank"], "targets.rank", "Q2.rank_4")
    it["one_in_R4"] = item("tgt", pos, "one_in_R4", q2["one_in_R4"], t["one_in_R"], "targets.one_in_R", "Q2.one_in_R4")
    it["|Z_4|"] = item("tgt", pos, "Z_4", q2["Z_4_size"], t["Z_size"], "targets.Z_size", "Q2.Z_4_size")
    for g in ["T_rank", "T_set", "T_strict", "T_ops"]:
        it[f"hash {g}"] = item("tgt", pos, f"hash_{g}", q3h[g], t[HASH_RUN[g]], f"targets.{HASH_RUN[g]}", f"Q3.hashes.targets.{g}")
    it["run self-consistency: sha256(rank) == run h_rank"] = item("tgt", pos, "run_rank_hash_selfcheck",
                                                                  sha_canon(t["rank"]), t["h_rank"], "sha256(canon(rank))", "(run side only)")
    flags = {}
    for lab, U in REFMAP.items():
        for g in ["T_rank", "T_set", "T_strict", "T_ops"]:
            flags[f"{lab}({U}).{g}"] = item("tgt", pos, f"match_{g}", mf[lab][g], t["refs"][U]["match"][GRAN_RUN[g]],
                                           f"targets.refs.{U}.match.{GRAN_RUN[g]}", f"Q3.match_flags_target_vs_reference.{pos}.{lab}.{g}")
    it["match_flags"] = flags
    targets_out[pos] = {"run_idx": idx, "items": it}

# ---------------------------------------------------------------------------
# Subsample retention identity: run's per-target flags vs Q5 counts
# ---------------------------------------------------------------------------
q5 = rd["Q5"]
run_unsat_pos = [pos for pos, idx in sorted(TGTMAP.items(), key=lambda kv: int(kv[0]))
                 if tgt_run[idx]["stratum"] == "unsat" and not tgt_run[idx]["degenerate"]]
ret_out = {"unsat_target_positions": item("q5", "subsample", "unsat_positions", q5["nondegenerate_unsat_target_positions"],
                                          run_unsat_pos, "targets.stratum == unsat (positions 10..1000 step 10)",
                                          "Q5.nondegenerate_unsat_target_positions"),
           "n": item("q5", "subsample", "n", q5["n_nondegenerate_unsat_targets"], len(run_unsat_pos), "count", "Q5.n")}
for lab in q5["unsat_references"]:
    U = REFMAP[lab]
    for g in ["T_rank", "T_set", "T_strict", "T_ops"]:
        cnt = sum(1 for pos in run_unsat_pos if tgt_run[TGTMAP[pos]]["refs"][U]["match"][GRAN_RUN[g]])
        pr = q5["per_reference"][lab][g]
        ret_out[f"{lab}({U}).{g}"] = item("q5", lab, f"retention_{g}", [pr["count"], pr["n"]], [cnt, len(run_unsat_pos)],
                                          f"count of targets.refs.{U}.match.{GRAN_RUN[g]} over the run's unsat subsample",
                                          f"Q5.per_reference.{lab}.{g}")
# The re-deriver's Q5 set is also listed against the run's reference classification
ret_out["unsat_reference_set"] = item("q5", "subsample", "unsat_refs", sorted(REFMAP[l] for l in q5["unsat_references"]),
                                      sorted(k for k, v in refs_run.items() if k != "modal" and v["arm"] == "unsat"),
                                      "references.json arm == unsat", "Q5.unsat_references (mapped)")

# ---------------------------------------------------------------------------
# Q7
# ---------------------------------------------------------------------------
q7 = rd["Q7"]
q7_out = {}
for rdg, res in q7["results"].items():
    q7_out[rdg] = {
        "A": item("q7", rdg, "A", res["A"], curve["A"], "curve.json A", f"Q7.results.{rdg}.A"),
        "B": item("q7", rdg, "B", res["B"], curve["B"], "curve.json B", f"Q7.results.{rdg}.B"),
        "#E": item("q7", rdg, "order", res["order"], curve["order"], "curve.json order", f"Q7.results.{rdg}.order"),
        "h": item("q7", rdg, "h", res["h"], curve["h"], "curve.json h", f"Q7.results.{rdg}.h"),
        "q": item("q7", rdg, "q", res["q"], curve["q"], "curve.json q", f"Q7.results.{rdg}.q"),
        "rejected draws": item("q7", rdg, "rejected", res["draws"] - 1, curve["draws_rejected"], "curve.json draws_rejected",
                               f"Q7.results.{rdg}.draws - 1"),
    }

# ---------------------------------------------------------------------------
# Floor / ceiling census (CP-4)
# ---------------------------------------------------------------------------
def census(values):
    s = sorted(set(json.dumps(v) for v in values))
    return s if len(s) <= 6 else f"{len(s)} distinct values"

fc = {}
fc["target degenerate flag"] = census([t["items"]["degenerate"]["run"] for t in targets_out.values()])
for g in ["T_rank", "T_set", "T_strict", "T_ops"]:
    fc[f"target match flags {g} (all 5 refs)"] = census([v["run"] for t in targets_out.values()
                                                         for kk, v in t["items"]["match_flags"].items() if kk.endswith("." + g)])
fc["target one_in_R4, sat arm"] = census([t["items"]["one_in_R4"]["run"] for t in targets_out.values() if t["items"]["arm"]["run"] == "sat"])
fc["target one_in_R4, unsat arm"] = census([t["items"]["one_in_R4"]["run"] for t in targets_out.values() if t["items"]["arm"]["run"] == "unsat"])
fc["reference K_rank (unsat refs)"] = census([q6_out[l]["items"]["K_rank (references.json)"]["run"] for l in q6_out])
fc["(R_4, C_4)"] = census([references_out[l]["items"]["(R_4, C_4)"]["run"] for l in references_out])
fc["Q5 retention counts T_set/T_strict/T_ops"] = census([ret_out[k]["run"][0] for k in ret_out if k.split(".")[-1] in ("T_set", "T_strict", "T_ops")])
fc["target rank_4"] = census([t["items"]["rank_4"]["run"] for t in targets_out.values()])
fc["target |Z_4|"] = census([t["items"]["|Z_4|"]["run"] for t in targets_out.values()])
fc["target s"] = census([t["items"]["s (s_route_A_rootfinding)"]["run"] for t in targets_out.values()])

SELF_TYPES = {"ref:run_oplog_hash_selfcheck", "ref:run_strict_hash_selfcheck", "ref:run_rank_hash_selfcheck",
              "tgt:run_rank_hash_selfcheck", "ckpt:ckpt_hashes_selfcheck"}
MAP_TYPES = {"ref:x_R", "tgt:x_R"}
EXTRA_TYPES = {k for k in by_item if k.startswith("refref:") or (k.startswith("ckpt:") and k not in SELF_TYPES)}
categories = {}
for k, v in by_item.items():
    cat = ("run_self_consistency (run side only, not a comparison)" if k in SELF_TYPES else
           "mapping_sanity (x_R equality under the key)" if k in MAP_TYPES else
           "supplementary (beyond CP-2: reference-vs-reference flags, run-time checkpoint content)" if k in EXTRA_TYPES else
           "cp2_comparison (re-derivation vs run)")
    cc = categories.setdefault(cat, {"agree": 0, "disagree": 0})
    cc["agree"] += v["agree"]
    cc["disagree"] += v["disagree"]

out = {
    "schema": "certbin.j7_comparison.v1",
    "task_id": "TASK-20260923-5f9b82",
    "joint": "J7",
    "review_id": "REVIEW-CERTBIN-20260923-c51f07",
    "run_id": "RUN-CERTBIN-3b7e05",
    "rederivation": {"task_id": "TASK-20260923-7a2cd4", "sha256": rd_hash},
    "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "head_commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
    "command": "python3 -B " + ME + "/checks/compare_j7.py",
    "key_mapping": {"references": REFMAP, "targets": "position p -> run idx p (identity; blind-inputs-key.json)",
                    "target_map_is_identity": all(int(p) == i for p, i in TGTMAP.items())},
    "cp1": cp1,
    "verification_computation_declaration": {
        "archived_instances_recomputed": [x["reference"] for x in impl_recompute["instances"]],
        "count": len(impl_recompute["instances"]),
        "what": "impl/ (archived, receipt-verified) affine_forms on the run's own archived D=4 op log, to obtain a_k, which the run did not archive; also its consistency with the run's archived a0, a_nonzero, K_exact, K_rank",
        "trials": 0,
        "supplementary_read": "run checkpoint/p2-F-S3-D4.json.gz reference summaries (read only; no computation beyond equality)",
        "hash-only recomputations (no elimination)":"sha256 of canonical JSON of archived run content (T_strict, op log, rank, reconstructed T_set) for 5 references and rank for 100 targets",
    },
    "references": references_out,
    "t_set_reconstruction": tset_reconstruction,
    "unsat_reference_affine_replay": q6_out,
    "supplementary_run_time_checkpoint": ck_out,
    "ambiguities_vs_run_resolution": AMBIGUITY_TABLE,
    "cp_convention": cp_conv,
    "zero_rows_census_rederived": zero_rows,
    "reference_vs_reference_flags_extra": rr_out,
    "targets": targets_out,
    "subsample_retention_identity": ret_out,
    "q7_curve": q7_out,
    "floor_ceiling_census_run_values": fc,
    "summary": {"items_agree": counts["agree"], "items_disagree": counts["disagree"],
                "by_category": categories,
                "per_item_type": by_item, "disagreements": disagreements},
}
with open(f"{ME}/comparison.json", "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print(json.dumps({"cp1": {k: v["result"] for k, v in cp1.items()}, "agree": counts["agree"],
                  "disagree": counts["disagree"], "n_disagreements": len(disagreements)}, indent=1))
for k, v in by_item.items():
    print(k, v)
print("cp_convention max diff:", max(v["max_abs_diff"] for v in cp_conv.values()))
print("zero rows:", zero_rows)
print("t_set reconstruction:", {k: v["reconstruction_confirmed_by_run_hash"] for k, v in tset_reconstruction.items()})
print("impl recompute vs run archived:", {k: v["impl_recompute_vs_run_archived"] for k, v in q6_out.items()})
print("floor/ceiling census:")
for k, v in fc.items():
    print(" ", k, v)
if disagreements:
    print("DISAGREEMENTS:")
    for d in disagreements[:50]:
        print(" ", json.dumps(d)[:300])
