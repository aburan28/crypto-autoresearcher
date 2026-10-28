#!/usr/bin/env python3
"""Independent re-implementation of the n=83 opcounts v2 analysis (sheriff SHF-20261028-0f3f64, red-team reader).

Written from cryptanalysis:experiments/koblitz-n83-opcounts-20261023/PROTOCOL.md (the frozen rule),
README.md "What is counted", and the producer's record fields. It imports nothing from the audited
clone and executes none of its code: every input is read as data (files on disk, or blobs via
`git show`).

Inputs
  --clone       /home/user/cryptanalysis (read-only; git show HEAD:<path> for off-sparse files)
  --runs-jsonl  the run's panel/runs.jsonl (off disk at HEAD: artifact-store pointer; recovered from
                git history at 5a6c233e and hash-checked against SHA256SUMS by the caller)
  --archive-runs-jsonl  run 38862448935's panel/runs.jsonl (recovered from 5569ba6e^, hash-checked)
  --out         output directory

Re-derived
  1. The frozen plan (62 rows) from PROTOCOL.md's table + the stacked schedule.json at HEAD.
  2. Row identity, validity, stdout decoding (raw_result_sha256), per-row tail fields.
  3. Identity against the archived twin: the protocol's key list AND a stricter whole-record diff
     with an explicit clock/op-count whitelist.
  4. Band units, exactly as PROTOCOL.md "The band" defines them, and a comparison with counts-v2.json.
  5. The 0 / 0.1 / 1 GAE band with exact Fractions for point estimates; the paired bootstrap
     replicated with the declared seed (to compare digits) and re-run with other seeds/draws.
  6. Red-team read-outs: crossover weight, omitted-phase sensitivity, field-op implied weight,
     memory axis, rank-seed variability from the archived K2 block.
"""
import argparse
import base64
import hashlib
import json
import random
import subprocess
from fractions import Fraction
from pathlib import Path

EXP = "experiments/koblitz-n83-opcounts-20261023"
STACKED = "experiments/koblitz-n83-stacked-20261016"
ARCH = STACKED + "/run_github_38862448935/panel"

# PROTOCOL.md "The band": kind map (written from the protocol / README text, not imported).
IC_GROUP = ["ec_add", "ec_double"]
IC_UNPRICED = [
    # root solves
    "s3_root_solves", "s3_root_solves_library",
    # root-index probes and inserts, filter queries and inserts
    "root_index_probes", "root_index_inserts", "root_filter_queries", "root_filter_inserts",
    # canonicalizations
    "canonicalizations",
    # Frobenius applications and fold rotations (README table: endomorphism class)
    "frobenius_x", "fold_rotations", "ec_frobenius",
    # relation lifts (README table lists ec_lift_x as native too)
    "relation_lifts", "ec_lift_x",
    # trivial additions
    "ec_add_trivial",
    # linear-algebra multiply-subtracts and pivot inversions, descent multiplications
    "la_mulmods", "la_inversions", "descent_mulmods",
]
IC_REPORTED = ["ec_scalar_mul", "la_row_eliminations", "field_mul", "field_sqr", "field_inv", "field_half_trace"]
FROB = ["frobenius_x", "fold_rotations", "ec_frobenius"]
RHO_GROUP = ["group_additions"]
RHO_UNPRICED = ["canonicalizations", "partition_hashes", "table_queries", "table_inserts", "failed_collisions"]
RHO_BOUNDED = ["scalar_multiplications"]
R_ORDER = 8569786107849059
WEIGHTS = [Fraction(0), Fraction(1, 10), Fraction(1)]


def git_show(clone, path):
    return subprocess.run(["git", "-C", str(clone), "show", "HEAD:" + path], check=True,
                          capture_output=True).stdout


def decode_text(text):
    """Return (record, tail, problems)."""
    problems = []
    lines = text.splitlines()
    raw_lines = [l for l in lines if l.startswith("raw_b64=")]
    if len(raw_lines) != 1:
        return None, {}, ["raw_b64 lines: %d" % len(raw_lines)]
    raw = base64.b64decode(raw_lines[0][len("raw_b64="):])
    tail = {}
    for word in lines[-1].split():
        if "=" in word:
            k, v = word.split("=", 1)
            tail[k] = v
    if tail.get("raw_result_sha256") != hashlib.sha256(raw).hexdigest():
        problems.append("raw_result_sha256 mismatch")
    return json.loads(raw), tail, problems


def record_parts(record):
    targets = [r for r in record.get("records", []) if r.get("kind") == "compact_orbit_dlp_target"]
    summaries = [r for r in record.get("records", []) if r.get("kind") == "compact_orbit_dlp_summary"]
    return targets, summaries


def deep_diff(a, b, path=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            p = path + "." + k if path else k
            if k not in a or k not in b:
                out.append(p + " (present in one side only)")
            else:
                out.extend(deep_diff(a[k], b[k], p))
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b) and \
            any(isinstance(x, (dict, list)) for x in a + b):
        for i, (x, y) in enumerate(zip(a, b)):
            out.extend(deep_diff(x, y, "%s[%d]" % (path, i)))
    elif a != b:
        out.append(path)
    return out


# Leaves that are allowed to differ between the counted rerun and the archived uncounted run:
# clocks, hardware counters, process/host/binary identity, and the new op_counts block.
CLOCK_TOKENS = ("_ms", "_ns", "ms_", "ns_", "timing", "rss", "hw_counts", "started_unix", "process_ns",
                "op_counts", "executable", "binary", "stderr_tail", "cold_phase", "online_ms", "setup_ms",
                "rank_attempt_ns", "phase_sum", "residual", "filter_build", "index_ms", "worker_source")


def is_clockish(path):
    leaf = path.lower()
    return leaf.endswith(".ms") or any(tok in leaf for tok in CLOCK_TOKENS)


def split(unit, group, unpriced, bounded, reported, family):
    known = set(group) | set(unpriced) | set(bounded) | set(reported)
    unknown = sorted(set(unit) - known)
    missing = sorted(k for k in set(group) | set(unpriced) | set(bounded) if k not in unit)
    if unknown or missing:
        raise SystemExit("%s unit: unknown kinds %s, missing kinds %s" % (family, unknown, missing))
    return (sum(unit[k] for k in group), sum(unit[k] for k in unpriced), sum(unit[k] for k in bounded))


def g4(x):
    return "%.4g" % float(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clone", type=Path, required=True)
    ap.add_argument("--runs-jsonl", type=Path, required=True)
    ap.add_argument("--archive-runs-jsonl", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--panel", type=Path, default=None, help="controls only: a mutated copy of panel/")
    ap.add_argument("--force-band", action="store_true", help="controls only: compute the band even if a gate fails")
    args = ap.parse_args()
    clone = args.clone
    run_dir = clone / EXP / "run_github_39882571652"
    panel = args.panel or (run_dir / "panel")
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    report = {"inputs": {}, "checks": {}, "notes": []}

    # ---- 1. frozen plan from PROTOCOL.md + stacked schedule.json at HEAD ----
    schedule = json.loads(git_show(clone, STACKED + "/schedule.json"))
    sched_runs = [r for seg in schedule["segments"] for r in seg["runs"]]
    k1 = [r for seg in schedule["segments"] if seg["id"] == "K1" for r in seg["runs"]]
    by_arm_point = {}
    for r in sched_runs:
        by_arm_point.setdefault((r["arm"], r["point_id"]), []).append(r)
    k1_kS = [r for r in k1 if r["arm"] == "kS"]
    k1_kP = [r for r in k1 if r["arm"] == "kP"]
    assert len(k1_kS) == 1 and len(k1_kP) == 1
    plan = [
        {"serial": 1, "arm": "kS", "point_id": k1_kS[0]["point_id"], "seed": 101, "archived_serial": 42, "block": "K1"},
        {"serial": 2, "arm": "kP", "point_id": k1_kP[0]["point_id"], "seed": 101, "archived_serial": 43, "block": "K1"},
    ]
    twin_unique = True
    plan_vs_schedule = []
    if not (k1_kS[0]["serial"] == 42 and k1_kP[0]["serial"] == 43 and k1_kS[0]["seed"] == 101
            and k1_kP[0]["seed"] == 101 and k1_kS[0]["point_id"] == "s000"):
        plan_vs_schedule.append("K1 twins differ from PROTOCOL.md table")
    serial = 3
    for i in range(20):
        point = "s%03d" % i
        for arm in ("cS", "cP", "rT"):
            seed = 870000 + i if arm == "rT" else 7
            twins = by_arm_point.get((arm, point), [])
            if len(twins) != 1:
                twin_unique = False
            twin = twins[0]
            if twin["seed"] != seed:
                plan_vs_schedule.append("%s %s: schedule seed %s != protocol %s" % (arm, point, twin["seed"], seed))
            plan.append({"serial": serial, "arm": arm, "point_id": point, "seed": seed,
                         "archived_serial": twin["serial"], "block": "C"})
            serial += 1
    report["checks"]["plan_has_62_rows"] = len(plan) == 62
    report["checks"]["twin_unique_in_schedule"] = twin_unique
    report["checks"]["plan_seeds_match_schedule"] = not plan_vs_schedule
    report["plan_vs_schedule_issues"] = plan_vs_schedule

    # ---- 2. rows, order, validity ----
    rows = [json.loads(l) for l in args.runs_jsonl.read_text().splitlines() if l.strip()]
    ident = lambda r: (r.get("serial"), r.get("arm"), r.get("point_id"), r.get("seed"), r.get("archived_serial"), r.get("block"))
    report["checks"]["rows_equal_frozen_plan"] = [ident(r) for r in rows] == [ident(p) for p in plan]
    start = json.loads((panel / "runner_start.json").read_text())
    report["checks"]["runner_start_order_equals_plan"] = start["order"] == [[p["serial"], p["arm"], p["point_id"], p["seed"]] for p in plan]
    runner_stdout = [json.loads(l) for l in (run_dir / "runner-stdout.jsonl").read_text().splitlines() if l.strip()]
    report["checks"]["runner_stdout_all_valid_no_issues"] = len(runner_stdout) == 62 and all(
        r["status"] == "valid" and not r["issues"] for r in runner_stdout) and \
        [(r["serial"], r["arm"], r["point"]) for r in runner_stdout] == [(p["serial"], p["arm"], p["point_id"]) for p in plan]
    report["checks"]["rows_all_valid"] = bool(rows) and all(
        r["status"] == "valid" and not r["issues"] and r["returncode"] == 0 and not r["timed_out"] for r in rows)

    # ---- 3. decode + archive identity ----
    archive_rows = {r["serial"]: r for r in (json.loads(l) for l in args.archive_runs_jsonl.read_text().splitlines() if l.strip())}
    protocol_mismatches, strict_diffs, decode_problems = [], {}, []
    new_records, old_records = {}, {}
    scalars = {}
    for row in rows:
        text = (panel / row["stdout_file"]).read_text()
        rec, tail, probs = decode_text(text)
        if probs or rec is None:
            decode_problems.append("%s: %s" % (row["stdout_file"], probs))
            continue
        if tail.get("arm") != row["arm"] or tail.get("panel") != row["point_id"] or tail.get("verified") != "1" \
                or tail.get("issues") != "0":
            decode_problems.append("%s: tail arm/panel/verified/issues %s" % (row["stdout_file"], {k: tail.get(k) for k in ("arm", "panel", "verified", "issues")}))
        if rec.get("arm") != row["arm"] or rec.get("panel") != row["point_id"]:
            decode_problems.append("%s: record arm/panel differ from row" % row["stdout_file"])
        old_row = archive_rows[row["archived_serial"]]
        old_text = git_show(clone, ARCH + "/" + old_row["stdout_file"]).decode()
        old, old_tail, old_probs = decode_text(old_text)
        if old_probs or old is None or old_row["arm"] != row["arm"] or old_row["point_id"] != row["point_id"] \
                or old_row["status"] != "valid" or old_tail.get("arm") != row["arm"] or old_tail.get("panel") != row["point_id"]:
            decode_problems.append("archive twin %s: %s" % (old_row["stdout_file"], old_probs))
            continue
        key = (row["arm"], row["point_id"])
        new_records[key], old_records[key] = rec, old
        # Protocol key list (PROTOCOL.md pass/fail item 2)
        if row["arm"] == "rT":
            ch = [r["outcome"]["charges_setup_and_solve"] for r in rec["records"] if "charges_setup_and_solve" in (r.get("outcome") or {})]
            och = [r["outcome"]["charges_setup_and_solve"] for r in old["records"] if "charges_setup_and_solve" in (r.get("outcome") or {})]
            if len(ch) != 1 or ch != och:
                protocol_mismatches.append("rT %s charges" % row["point_id"])
            if rec["fields"].get("recovered_scalar") != old["fields"].get("recovered_scalar"):
                protocol_mismatches.append("rT %s scalar" % row["point_id"])
            scalars.setdefault(row["point_id"], set()).add(str(rec["fields"].get("recovered_scalar")))
        else:
            t, s = record_parts(rec)
            ot, os_ = record_parts(old)
            if len(t) != 1 or len(s) != 1 or len(ot) != 1 or len(os_) != 1:
                protocol_mismatches.append("%s %s: expected one target and one summary" % key)
                continue
            t, s, ot, os_ = t[0], s[0], ot[0], os_[0]
            oc = s.get("op_counts") or {}
            if oc.get("enabled") is not True or not isinstance(t.get("op_counts"), dict):
                protocol_mismatches.append("%s %s: op_counts not enabled" % key)
            for k in ("point_indices", "x_codes", "pinned_intermediates", "probes", "root_calls", "relation_checks",
                      "skipped_symmetric_states", "recovered_scalar"):
                if t.get(k) != ot.get(k):
                    protocol_mismatches.append("%s %s target.%s" % (key + (k,)))
            sk = (["rank_attempt_probes", "rank_relations_blake3", "rank_probes_total", "rank_root_calls_total",
                   "rank_attempts", "rank_relations", "rank_failures", "rank"] if row["arm"] in ("kS", "kP")
                  else ["index_digest", "stored_states", "root_table_entries"])
            for k in sk:
                if s.get(k) != os_.get(k):
                    protocol_mismatches.append("%s %s summary.%s" % (key + (k,)))
            scalars.setdefault(row["point_id"], set()).add(str(t.get("recovered_scalar")))
        # Stricter: whole-record diff with a clock whitelist
        d = [p for p in deep_diff(rec, old) if not is_clockish(p)]
        if d:
            strict_diffs["%s %s" % key] = d
    report["checks"]["stdout_decoded_and_tails_consistent"] = not decode_problems
    report["checks"]["identical_to_archived_run_protocol_keys"] = not protocol_mismatches
    report["checks"]["one_scalar_per_point"] = len(scalars) == 20 and all(len(v) == 1 for v in scalars.values())
    report["decode_problems"] = decode_problems
    report["protocol_mismatches"] = protocol_mismatches
    # Summarise strict diffs by path pattern
    patterns = {}
    for k, paths in strict_diffs.items():
        for p in paths:
            patterns.setdefault(p, []).append(k)
    report["strict_nonclock_diff_paths"] = {p: len(v) for p, v in sorted(patterns.items())}

    gate = all(report["checks"].values())
    report["gate_passed"] = gate
    if not gate and not args.force_band:
        (out / "reimpl_result.json").write_text(json.dumps(report, indent=1, sort_keys=True, default=str) + "\n")
        print(json.dumps({"gate_passed": False, "checks": report["checks"],
                          "protocol_mismatches": protocol_mismatches[:10], "decode_problems": decode_problems[:10]}, indent=1))
        raise SystemExit(1)

    # ---- 4. band units per PROTOCOL.md ----
    def ic_unit(rank_arm, cold_arm, point, include_rank_la=False, include_index_digest=False):
        _, ks = record_parts(new_records[(rank_arm, "s000")])
        _, cs = record_parts(new_records[(cold_arm, point)])
        ct, _ = record_parts(new_records[(cold_arm, point)])
        rank_stage = ks[0]["op_counts"]["phases"]["rank_stage"]
        ph = cs[0]["op_counts"]["phases"]
        parts = [rank_stage, ph["setup"], ph["linear_algebra"], ph["between_linear_algebra_and_targets"], ct[0]["op_counts"]]
        if include_rank_la:
            parts.append({k: max(0, v - ph["linear_algebra"].get(k, 0)) for k, v in ks[0]["op_counts"]["phases"]["linear_algebra"].items()})
        if include_index_digest:
            parts.append(ph["after_targets_index_digest"])
        total = {}
        for p in parts:
            for k, v in p.items():
                total[k] = total.get(k, 0) + v
        return total

    points = ["s%03d" % i for i in range(20)]
    units = {"S": {"family": "ic", "units": {p: ic_unit("kS", "cS", p) for p in points}},
             "P": {"family": "ic", "units": {p: ic_unit("kP", "cP", p) for p in points}},
             "rT": {"family": "rho", "units": {}}}
    for p in points:
        rec = new_records[("rT", p)]
        units["rT"]["units"][p] = [r["outcome"]["charges_setup_and_solve"] for r in rec["records"]
                                   if "charges_setup_and_solve" in (r.get("outcome") or {})][0]
    committed_counts = json.loads((run_dir / "analysis_v2" / "counts-v2.json").read_text())
    report["checks"]["units_equal_committed_counts_v2"] = committed_counts["arms"] == units and \
        committed_counts["reference"] == "rT" and committed_counts["r_bits"] == 53
    # targets phase vs per-target op_counts (unit uses the per-target block)
    tp_eq = all(record_parts(new_records[(a, p)])[1][0]["op_counts"]["phases"]["targets"] ==
                record_parts(new_records[(a, p)])[0][0]["op_counts"] for a in ("cS", "cP") for p in points)
    report["checks"]["cold_targets_phase_equals_target_op_counts"] = tp_eq
    # end_to_end == sum of phases (producer self-consistency)
    e2e_ok = True
    for key, rec in new_records.items():
        if key[0] == "rT":
            continue
        s = record_parts(rec)[1][0]["op_counts"]
        tot = {}
        for name, ph in s["phases"].items():
            if name == "after_targets_index_digest":  # README: "outside every interval"
                continue
            for k, v in ph.items():
                tot[k] = tot.get(k, 0) + v
        if tot != s["end_to_end"]:
            e2e_ok = False
    report["checks"]["ic_end_to_end_equals_sum_of_phases_except_index_digest"] = e2e_ok

    # ---- 5. band ----
    def parts_for(frob_as_group):
        g = IC_GROUP + (FROB if frob_as_group else [])
        u = [k for k in IC_UNPRICED if not (frob_as_group and k in FROB)]
        res = {}
        for name in ("S", "P"):
            res[name] = {p: split(units[name]["units"][p], g, u, [], IC_REPORTED, "ic") for p in points}
        res["rT"] = {p: split(units["rT"]["units"][p], RHO_GROUP, RHO_UNPRICED, RHO_BOUNDED, [], "rho") for p in points}
        return res

    bounds = [Fraction(0), Fraction(2 * (53 - 1))]
    assert R_ORDER < 2 ** 53

    def cost(pt, w, b):
        g, u, s = pt
        return Fraction(g) + Fraction(s) * b + w * Fraction(u)

    def mean_cost(P, name, w, b, idx=None):
        sel = points if idx is None else [points[i] for i in idx]
        return sum(cost(P[name][p], w, b) for p in sel) / len(sel)

    def boot(P, num, den, w, b, resamples, lo_q=0.025, hi_q=0.975):
        # float arithmetic inside the bootstrap (as a float pipeline would); exact for point estimates
        num_c = {p: float(cost(P[num][p], w, b)) for p in points}
        den_c = {p: float(cost(P[den][p], w, b)) for p in points}
        vals = sorted((sum(num_c[points[i]] for i in s) / len(s)) / (sum(den_c[points[i]] for i in s) / len(s)) for s in resamples)
        n = len(vals)
        return [vals[int(lo_q * (n - 1))], vals[int(hi_q * (n - 1))]]

    def resamples_for(seed, draws):
        rng = random.Random(seed)
        return [[rng.randrange(len(points)) for _ in points] for _ in range(draws)]

    declared = resamples_for(20261023, 10000)
    alt_a = resamples_for(1, 10000)
    alt_b = resamples_for(987654321, 40000)

    def band(frob_as_group):
        P = parts_for(frob_as_group)
        res = {"arms": {}, "gap": {}, "pairs": {}}
        for name in ("S", "P", "rT"):
            mp = [sum(Fraction(P[name][p][i]) for p in points) / 20 for i in range(3)]
            res["arms"][name] = {"mean_group": mp[0], "mean_unpriced": mp[1], "mean_bounded": mp[2],
                                 "cost": {str(w): [mean_cost(P, name, w, b) for b in bounds] for w in WEIGHTS}}
        for name in ("S", "P"):
            res["gap"][name] = {}
            for w in WEIGHTS:
                cells = []
                for b in bounds:
                    ratio = mean_cost(P, name, w, b) / mean_cost(P, "rT", w, b)
                    cells.append({"b": b, "ratio": ratio, "ci_declared": boot(P, name, "rT", w, b, declared),
                                  "ci_seed1": boot(P, name, "rT", w, b, alt_a),
                                  "ci_seed987654321_40k": boot(P, name, "rT", w, b, alt_b)})
                res["gap"][name][str(w)] = cells
        for a, c in (("S", "P"), ("S", "rT"), ("P", "rT")):
            signs, sep, cells = set(), True, []
            for w in WEIGHTS:
                for b in bounds:
                    x, y = mean_cost(P, a, w, b), mean_cost(P, c, w, b)
                    ci = boot(P, a, c, w, b, declared)
                    signs.add((x > y) - (x < y))
                    if ci[0] <= 1.0 <= ci[1]:
                        sep = False
                    cells.append({"w": w, "b": b, "ratio": x / y, "ci": ci})
            ranked = len(signs) == 1 and 0 not in signs and sep
            res["pairs"]["%s vs %s" % (a, c)] = {"ranked": ranked, "cheaper": (c if signs == {1} else a) if ranked else None,
                                                 "signs": sorted(signs), "cells": cells}
        return res, P

    main_band, P0 = band(False)
    frob_band, P1 = band(True)

    # ---- 6. red-team read-outs ----
    rt = main_band["arms"]["rT"]
    readouts = {}
    for name in ("S", "P"):
        a = main_band["arms"][name]
        # crossover weight w* with rho scalar mults at 0 and at 104 GAE
        ws = []
        for b in bounds:
            rho0 = rt["mean_group"] + rt["mean_bounded"] * b
            ws.append((rho0 - a["mean_group"]) / (a["mean_unpriced"] - rt["mean_unpriced"]))
        readouts["crossover_w_" + name] = [float(x) for x in ws]
    # rank-stage share of IC unpriced work, omitted rank-LA sensitivity
    _, ks = record_parts(new_records[("kS", "s000")])
    rank_un = split(ks[0]["op_counts"]["phases"]["rank_stage"], IC_GROUP, IC_UNPRICED, [], IC_REPORTED, "ic")
    readouts["S_rank_stage_unpriced_share"] = float(Fraction(rank_un[1]) / main_band["arms"]["S"]["mean_unpriced"])
    kla = ks[0]["op_counts"]["phases"]["linear_algebra"]
    cla = record_parts(new_records[("cS", "s000")])[1][0]["op_counts"]["phases"]["linear_algebra"]
    readouts["omitted_rank_process_la_vs_cold_la"] = {k: kla[k] - cla.get(k, 0) for k in kla if kla[k] != cla.get(k, 0)}
    unitsLA = {p: ic_unit("kS", "cS", p, include_rank_la=True) for p in points}
    PLA = {p: split(unitsLA[p], IC_GROUP, IC_UNPRICED, [], IC_REPORTED, "ic") for p in points}
    readouts["S_gap_w1_with_rank_LA_added"] = float(sum(cost(PLA[p], 1, 0) for p in points) / sum(cost(P0["rT"][p], 1, 0) for p in points))
    unitsID = {p: ic_unit("kS", "cS", p, include_index_digest=True) for p in points}
    PID = {p: split(unitsID[p], IC_GROUP, IC_UNPRICED, [], IC_REPORTED, "ic") for p in points}
    readouts["S_gap_w1_if_index_digest_phase_were_charged"] = float(sum(cost(PID[p], 1, 0) for p in points) / sum(cost(P0["rT"][p], 1, 0) for p in points))
    # Field-op implied weight: field cost of IC unpriced work per unpriced op, in units of one ec_add
    # (generic affine add: 1 inv, 2 mul, 1 sqr per README). Inversion priced at I field mults, I in {10, 1};
    # squaring and half-trace priced at s, h mults. Group-op field cost subtracted using the README's formulas.
    S0 = units["S"]["units"]["s000"]
    fm, fs, fi, fh = S0["field_mul"], S0["field_sqr"], S0["field_inv"], S0["field_half_trace"]
    adds, dbls = S0["ec_add"], S0["ec_double"]
    implied = {}
    for I in (1, 10, 20):
        for sq in (Fraction(0), Fraction(1, 2), Fraction(1)):
            for h in (Fraction(0), Fraction(83, 2)):
                def fc(m, s_, i_, h_):
                    return m + sq * s_ + I * i_ + h * h_
                total = fc(fm, fs, fi, fh)
                group_part = fc(2 * adds + 2 * dbls, adds + 2 * dbls, adds + dbls, 0)
                per_add = fc(2, 1, 1, 0)
                native_part = total - group_part
                unpriced = split(S0, IC_GROUP, IC_UNPRICED, [], IC_REPORTED, "ic")[1]
                implied["I=%d,sqr=%s,halftrace=%s" % (I, sq, h)] = float(Fraction(native_part) / per_add / unpriced)
    readouts["implied_w_from_field_ops_S_s000"] = implied
    readouts["implied_w_range"] = [min(implied.values()), max(implied.values())]
    # Memory axis (records): IC stored states/root-table bytes/peak RSS vs rho table entries/payload/peak RSS
    cs = record_parts(new_records[("cS", "s000")])[1][0]
    rho_tbl = [new_records[("rT", p)]["records"][0]["outcome"]["table_entries"] for p in points]
    rho_payload = [new_records[("rT", p)]["records"][0]["outcome"]["table_payload_lower_bound_bytes"] for p in points]
    readouts["memory"] = {
        "cS_stored_states": cs["stored_states"], "cS_root_table_entries": cs["root_table_entries"],
        "cS_root_table_bytes": cs["root_table_bytes"],
        "peak_rss_bytes": {k: new_records[(k, "s000")]["fields"]["peak_rss_bytes"] for k in ("kS", "kP", "cS", "cP")},
        "rT_peak_rss_bytes_s000": new_records[("rT", "s000")]["records"][0]["peak_rss_bytes"],
        "rT_table_entries_mean": sum(rho_tbl) / 20, "rT_table_payload_bytes_mean": sum(rho_payload) / 20,
    }
    # Rho matching: ideal sqrt(pi r / (2*166)) vs observed mean group additions
    import math
    ideal = math.sqrt(math.pi * R_ORDER / (2 * 166))
    readouts["rho_ideal_steps_sqrt_pi_r_over_332"] = ideal
    readouts["rho_mean_group_additions_over_ideal"] = float(rt["mean_group"]) / ideal
    readouts["rho_S_mean_group_additions_over_sqrt_r"] = float(rt["mean_group"]) / math.sqrt(R_ORDER)
    readouts["rho_recorded_ideal_steps"] = new_records[("rT", "s000")]["records"][0]["outcome"]["ideal_steps"]
    # Rank-seed variability: archived K2 (kS s001 seed 102, serial 116) against K1 (seed 101, serial 42)
    k2 = archive_rows[116]
    k2rec, _, _ = decode_text(git_show(clone, ARCH + "/" + k2["stdout_file"]).decode())
    k2s = record_parts(k2rec)[1][0]
    k1s = record_parts(new_records[("kS", "s000")])[1][0]
    readouts["rank_seed_variability"] = {
        "K1_seed101_rank_probes_total": k1s["rank_probes_total"], "K2_seed102_rank_probes_total": k2s["rank_probes_total"],
        "ratio_K2_over_K1": k2s["rank_probes_total"] / k1s["rank_probes_total"],
        "K1_rank_root_calls": k1s["rank_root_calls_total"], "K2_rank_root_calls": k2s["rank_root_calls_total"],
        "archived_serial_116": [k2["arm"], k2["point_id"], k2["seed"], k2["status"]]}
    # Sensitivity of the S gap to the K2 rank stage, scaling every rank-stage kind by the probe ratio (approximation)
    sc = Fraction(k2s["rank_probes_total"], k1s["rank_probes_total"])
    readouts["S_gap_w01_w1_if_rank_stage_scaled_to_K2_probes"] = [
        float((main_band["arms"]["S"]["mean_group"] + w * (main_band["arms"]["S"]["mean_unpriced"] + (sc - 1) * rank_un[1])) /
              (rt["mean_group"] + w * rt["mean_unpriced"])) for w in (Fraction(1, 10), Fraction(1))]
    # Factor-base construction bound: X = 427.524 ms (replay host) at the EPYC 9V45 rT step 175.95 ns
    # (baselines.json open item for the rank-finder run) -> at most this many GAE if all of X were group adds
    x_gae = 427.524e-3 / 175.95e-9
    readouts["factor_base_X_as_GAE_upper_bound"] = x_gae
    readouts["S_gap_w0_if_X_all_group_adds"] = float((main_band["arms"]["S"]["mean_group"] + Fraction(x_gae)) / rt["mean_group"])
    # Amortised reading (not evidence): IC online-only cost per target vs rho per target
    on = [split(record_parts(new_records[("cS", p)])[0][0]["op_counts"], IC_GROUP, IC_UNPRICED, [], IC_REPORTED, "ic") for p in points]
    readouts["cS_online_only_mean"] = {"group": sum(o[0] for o in on) / 20, "unpriced": sum(o[1] for o in on) / 20}
    fixed = main_band["arms"]["S"]["mean_unpriced"] - Fraction(sum(o[1] for o in on), 20)
    readouts["S_fixed_unpriced_per_cold_unit"] = float(fixed)

    # ---- outputs ----
    def jsonable(o):
        if isinstance(o, Fraction):
            return float(o)
        if isinstance(o, dict):
            return {str(k): jsonable(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [jsonable(v) for v in o]
        return o
    report["band"] = jsonable(main_band)
    report["band_frobenius_as_group"] = jsonable(frob_band)
    report["readouts"] = jsonable(readouts)

    # Compare with committed opcounts_result-v2.json (full precision) and band-v2.md (digits)
    committed = json.loads((run_dir / "analysis_v2" / "opcounts_result-v2.json").read_text())
    cmp = []
    for label, mine, theirs in (("band", main_band, committed["band"]), ("frob", frob_band, committed["band_frobenius_as_group"])):
        for name in ("S", "P", "rT"):
            ta = theirs["arms"][name]
            for mk, tk in (("mean_group", "mean_group_ops"), ("mean_unpriced", "mean_unpriced_native_ops"), ("mean_bounded", "mean_bounded_scalar_muls")):
                cmp.append((label, name, tk, float(mine["arms"][name][mk]), ta[tk]))
            for w in WEIGHTS:
                for j in range(2):
                    cmp.append((label, name, "cost[%s][%d]" % (w, j), float(mine["arms"][name]["cost"][str(w)][j]), ta["cost_gae"]["%g" % float(w)][j]))
        for name in ("S", "P"):
            for w in WEIGHTS:
                for j in range(2):
                    m = mine["gap"][name][str(w)][j]
                    t = theirs["gap_to_reference"][name]["%g" % float(w)][j]
                    cmp.append((label, name, "ratio[%s][%d]" % (w, j), float(m["ratio"]), t["ratio"]))
                    cmp.append((label, name, "ci_lo[%s][%d]" % (w, j), m["ci_declared"][0], t["ci95"][0]))
                    cmp.append((label, name, "ci_hi[%s][%d]" % (w, j), m["ci_declared"][1], t["ci95"][1]))
        for pair in theirs["pairs"]:
            k = "%s vs %s" % tuple(pair["arms"])
            cmp.append((label, k, "ranked", mine["pairs"][k]["ranked"], pair["ranked"]))
            if pair["ranked"]:
                cmp.append((label, k, "cheaper", mine["pairs"][k]["cheaper"], pair["cheaper"]))
            for cm, ct in zip(mine["pairs"][k]["cells"], pair["cells"]):
                cmp.append((label, k, "pair_ratio[%s][%s]" % (cm["w"], cm["b"]), float(cm["ratio"]), ct["ratio"]))
                cmp.append((label, k, "pair_ci_lo[%s][%s]" % (cm["w"], cm["b"]), cm["ci"][0], ct["ci95"][0]))
                cmp.append((label, k, "pair_ci_hi[%s][%s]" % (cm["w"], cm["b"]), cm["ci"][1], ct["ci95"][1]))
    worst = 0.0
    bad = []
    for row in cmp:
        a, b = row[3], row[4]
        if isinstance(a, bool) or isinstance(b, bool) or isinstance(a, str) or isinstance(b, str):
            if a != b:
                bad.append(row)
            continue
        rel = abs(a - b) / max(abs(b), 1e-300)
        worst = max(worst, rel)
        if rel > 1e-12:
            bad.append(row)
    report["compare_committed_v2"] = {"values_compared": len(cmp), "max_relative_difference": worst,
                                      "over_1e-12": [list(map(str, r)) for r in bad]}
    report["checks"]["band_equals_committed_v2_to_1e-12"] = not bad
    report["checks"]["committed_v2_checks_all_true"] = all(committed["checks"].values()) and committed["verdict"] == "counts_identical" and committed["mismatches"] == []

    # markdown in the committed layout, to diff digits against band-v2.md
    def md(res):
        L = ["| arm | mean group ops | mean unpriced native ops | cost w=0 | cost w=0.1 | cost w=1 |"]
        for name in ("S", "P", "rT"):
            a = res["arms"][name]
            def cell(w):
                lo, hi = a["cost"][str(w)]
                return g4(lo) if lo == hi else "%s-%s" % (g4(lo), g4(hi))
            L.append("| %s | %s | %s | %s | %s | %s |" % (name, g4(a["mean_group"]), g4(a["mean_unpriced"]), cell(WEIGHTS[0]), cell(WEIGHTS[1]), cell(WEIGHTS[2])))
        L.append("| gap to rT | w=0 | w=0.1 | w=1 |")
        for name in ("S", "P"):
            cells = []
            for w in WEIGHTS:
                cells.append(" / ".join("%s [%s, %s]" % (g4(c["ratio"]), g4(c["ci_declared"][0]), g4(c["ci_declared"][1])) for c in res["gap"][name][str(w)]))
            L.append("| %s | %s |" % (name, " | ".join(cells)))
        for k, v in res["pairs"].items():
            L.append("- %s: %s" % (k, ("%s cheaper at every weight" % v["cheaper"]) if v["ranked"] else "unresolved (signs %s)" % v["signs"]))
        return "\n".join(L) + "\n"
    (out / "reimpl_band.md").write_text("# main band\n" + md(main_band) + "\n# Frobenius at 1 GAE\n" + md(frob_band))
    (out / "reimpl_result.json").write_text(json.dumps(report, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({"checks": report["checks"], "compare": {k: v for k, v in report["compare_committed_v2"].items() if k != "over_1e-12"},
                      "n_over": len(report["compare_committed_v2"]["over_1e-12"])}, indent=1))


if __name__ == "__main__":
    main()
