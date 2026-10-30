#!/usr/bin/env python3
"""Proves-too-much / detection controls for reimpl_analyze.py (sheriff SHF-20261028-0f3f64).

Each control feeds the re-implementation an input whose correct verdict is KNOWN and checks that it
reaches that verdict. A pipeline that still says counts_identical, or still ranks, on these inputs
would prove too much.

  C1 truncated panel (last row dropped)                  -> gate fails
  C2 a single rank row only                              -> gate fails
  C3 one seed changed                                    -> gate fails
  C4 a duplicate row replacing the last target           -> gate fails
  C5 one cS record's target probes +1 (sha recomputed)   -> gate fails (archive identity)
  C6 positive control: every rT group_additions x 1000   -> gate fails; forced band ranks S < rT everywhere
  C7 null control: kP/cP replaced by kS/cS (P == S)      -> gate fails; forced band leaves S vs P unresolved

Usage: controls.py --clone /home/user/cryptanalysis --runs-jsonl R --archive-runs-jsonl A --work DIR --out FILE
"""
import argparse
import base64
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PANEL = "experiments/koblitz-n83-opcounts-20261023/run_github_39882571652/panel"


def rewrite(path, mutate, tail_arm=None):
    """Decode the raw record, mutate it, re-encode, and recompute raw_result_sha256 (and the tail arm)."""
    lines = path.read_text().splitlines()
    i = [k for k, l in enumerate(lines) if l.startswith("raw_b64=")][0]
    rec = mutate(json.loads(base64.b64decode(lines[i][len("raw_b64="):])))
    raw = json.dumps(rec, separators=(",", ":"), sort_keys=True).encode()
    lines[i] = "raw_b64=" + base64.b64encode(raw).decode()
    tail = []
    for w in lines[-1].split():
        if w.startswith("raw_result_sha256="):
            w = "raw_result_sha256=" + hashlib.sha256(raw).hexdigest()
        elif w.startswith("arm=") and tail_arm:
            w = "arm=" + tail_arm
        tail.append(w)
    lines[-1] = " ".join(tail)
    path.write_text("\n".join(lines) + "\n")


def run(args, name, runs_lines, panel=None, force=False):
    d = args.work / name
    d.mkdir(parents=True, exist_ok=True)
    runs = d / "runs.jsonl"
    runs.write_text("".join(l + "\n" for l in runs_lines))
    cmd = [sys.executable, "-I", str(HERE / "reimpl_analyze.py"), "--clone", str(args.clone), "--runs-jsonl", str(runs),
           "--archive-runs-jsonl", str(args.archive_runs_jsonl), "--out", str(d / "out")]
    if panel:
        cmd += ["--panel", str(panel)]
    if force:
        cmd += ["--force-band"]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(d))
    res = json.loads((d / "out" / "reimpl_result.json").read_text())
    return p.returncode, res


def copy_panel(args, name):
    dst = args.work / name / "panel"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(args.clone / PANEL, dst)
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clone", type=Path, required=True)
    ap.add_argument("--runs-jsonl", type=Path, required=True)
    ap.add_argument("--archive-runs-jsonl", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    lines = [l for l in args.runs_jsonl.read_text().splitlines() if l.strip()]
    rows = [json.loads(l) for l in lines]
    out = {}

    rc, res = run(args, "C1_truncated", lines[:-1])
    out["C1_truncated"] = {"expected": "gate fails", "exit": rc, "gate_passed": res.get("gate_passed"), "pass": rc == 1 and res.get("gate_passed") is False}

    rc, res = run(args, "C2_single_rank_row", lines[:1])
    out["C2_single_rank_row"] = {"expected": "gate fails", "exit": rc, "gate_passed": res.get("gate_passed"), "pass": rc == 1 and res.get("gate_passed") is False}

    r = [dict(x) for x in rows]
    r[9]["seed"] = r[9]["seed"] + 1
    rc, res = run(args, "C3_seed_changed", [json.dumps(x, sort_keys=True) for x in r])
    out["C3_seed_changed"] = {"expected": "gate fails", "exit": rc, "gate_passed": res.get("gate_passed"), "pass": rc == 1 and res.get("gate_passed") is False}

    r = [dict(x) for x in rows]
    dup = dict(r[58]); dup["serial"] = 62
    r[61] = dup
    rc, res = run(args, "C4_duplicate_replaces_target", [json.dumps(x, sort_keys=True) for x in r])
    out["C4_duplicate_replaces_target"] = {"expected": "gate fails", "exit": rc, "gate_passed": res.get("gate_passed"), "pass": rc == 1 and res.get("gate_passed") is False}

    panel = copy_panel(args, "C5_record_mutation")
    def bump(rec):
        for x in rec["records"]:
            if x.get("kind") == "compact_orbit_dlp_target":
                x["probes"] += 1
        return rec
    rewrite(panel / "runs/00003.stdout.txt", bump)
    rc, res = run(args, "C5_record_mutation", lines, panel=panel)
    out["C5_record_mutation"] = {"expected": "gate fails on archive identity", "exit": rc, "gate_passed": res.get("gate_passed"),
                                 "mismatches": res.get("protocol_mismatches"), "pass": rc == 1 and res.get("gate_passed") is False and
                                 any("target.probes" in m for m in res.get("protocol_mismatches", []))}

    panel = copy_panel(args, "C6_positive_rho_x1000")
    def scale(rec):
        for x in rec["records"]:
            o = x.get("outcome") or {}
            if "charges_setup_and_solve" in o:
                o["charges_setup_and_solve"]["group_additions"] *= 1000
        return rec
    for row in rows:
        if row["arm"] == "rT":
            rewrite(panel / row["stdout_file"], scale)
    rc, res = run(args, "C6_positive_rho_x1000", lines, panel=panel, force=True)
    pair = res.get("band", {}).get("pairs", {}).get("S vs rT", {})
    out["C6_positive_rho_x1000"] = {"expected": "gate fails; forced band ranks S cheaper than rT at every weight",
                                    "gate_passed": res.get("gate_passed"), "ranked": pair.get("ranked"), "cheaper": pair.get("cheaper"),
                                    "pass": res.get("gate_passed") is False and pair.get("ranked") is True and pair.get("cheaper") == "S"}

    panel = copy_panel(args, "C7_null_P_equals_S")
    by = {(x["arm"], x["point_id"]): x for x in rows}
    def as_arm(arm):
        def f(rec):
            rec["arm"] = arm
            return rec
        return f
    shutil.copyfile(panel / by[("kS", "s000")]["stdout_file"], panel / by[("kP", "s000")]["stdout_file"])
    rewrite(panel / by[("kP", "s000")]["stdout_file"], as_arm("kP"), tail_arm="kP")
    for i in range(20):
        p = "s%03d" % i
        shutil.copyfile(panel / by[("cS", p)]["stdout_file"], panel / by[("cP", p)]["stdout_file"])
        rewrite(panel / by[("cP", p)]["stdout_file"], as_arm("cP"), tail_arm="cP")
    rc, res = run(args, "C7_null_P_equals_S", lines, panel=panel, force=True)
    pair = res.get("band", {}).get("pairs", {}).get("S vs P", {})
    out["C7_null_P_equals_S"] = {"expected": "gate fails; forced band leaves S vs P unresolved (ratio 1)",
                                 "gate_passed": res.get("gate_passed"), "ranked": pair.get("ranked"),
                                 "ratios": sorted({round(c["ratio"], 12) for c in pair.get("cells", [])}),
                                 "pass": res.get("gate_passed") is False and pair.get("ranked") is False}
    args.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: (v["pass"], v.get("exit"), v.get("gate_passed")) for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    main()
