#!/usr/bin/env python3
"""Frozen driver of EXP-PEXT-212d5c (GHS cover genus floor at n = 7; H-PEXT-d536a1).

  python3 run.py trial --run-dir DIR --run-id RUN-... --trial-id ID --plan experiments/EXP-PEXT-212d5c/trial-plan.json

Stages (trial-plan.json "stage"):
  regression  build cover_census_n7.rs; rerun the merged n = 3 (q = 3, 5, 7) and n = 5 (q = 3) censuses and require
              byte-identical curve / group / mr / derived_checks records against the vendored fixtures; check the
              abstract spectrum (spectrum.py) against the sibling derived sets (n = 3, 5) and against the (m, r) lists
              compiled into the tool (n = 7). Any difference voids the experiment (instrument defect).
  construct   the genus-7 configuration enumeration at q = 3, 5, 7.
  char2       the characteristic-2 magic-number census at N = 7 l, l = 1, 2, 3.
  census      the n = 7, q = 3 stratified structure census (STRATA_K classes per stratum plus every j in F_q class,
              with their 2-isogeny neighbour classes; every structure of every model).
  lean        lake build of lean/CoverCensusN7.lean (decide lemmas); toolchain absence is recorded, not hidden.
  analyze     analysis.json and floor-table.md from the earlier run directories (recorded values only).

Standard library plus PyYAML (manifest). rustc (edition 2021, -O) builds the tool into a temporary directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import resource
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

import yaml

EXP = "EXP-PEXT-212d5c"
HYPOTHESIS_ID = "H-PEXT-d536a1"
HERE = os.path.dirname(os.path.abspath(__file__))
EXP_DIR = os.path.dirname(HERE)
RUNS_DIR = os.path.join(EXP_DIR, "runs")
THREADS = 4
STRATA_K = 24
CONSTRUCT_Q = (3, 5, 7)
CHAR2_L = (1, 2, 3)
RUSTC_FLAGS = ["--edition", "2021", "-O"]
TOOL = "cover_census_n7.rs"
# regression arms: (name, q, n, fixture)
REGRESSION = (
    ("R-n3-q3", 3, 3, "fixtures/pilot-n3-q3-cosets.jsonl"),
    ("R-n3-q5", 5, 3, "fixtures/R1-n3-q5.jsonl"),
    ("R-n3-q7", 7, 3, "fixtures/R1-n3-q7.jsonl"),
    ("R-n5-q3", 3, 5, "fixtures/D-n5-q3-cosets.jsonl"),
)
VOLATILE = ("field", "totals")  # records carrying wall or setup seconds; every other record must match byte for byte
# derived sets of the sibling protocols (genus spectra by type), the n = 3 / n = 5 regression of spectrum.py
SIBLING_SPECTRA = {
    3: {"odd": [13, 17], "floor": {"split": 3, "Z2": 3, "odd": 13}},
    5: {"odd": [33, 97, 129], "floor": {"split": 5, "Z2": 25, "odd": 33}},
}


def _sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def code_hashes() -> dict:
    out = {}
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".lake")]
        for name in sorted(files):
            if name.endswith((".py", ".rs", ".lean", ".toml")) or name == "lean-toolchain":
                p = os.path.join(root, name)
                out[os.path.relpath(p, HERE)] = _sha256(p)
    return dict(sorted(out.items()))


def _git_commit() -> tuple:
    try:
        c = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=HERE, text=True).strip()
        d = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", HERE], cwd=HERE).returncode != 0
        return c, d
    except (OSError, subprocess.CalledProcessError):
        return None, None


def _version(cmd: list) -> str | None:
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip().splitlines()[0]
    except (OSError, subprocess.CalledProcessError, IndexError):
        return None


def build_tool(build: str) -> str:
    out = os.path.join(build, "ccn7")
    subprocess.run(["rustc", *RUSTC_FLAGS, os.path.join(HERE, TOOL), "-o", out], check=True)
    return out


def load_jsonl(path: str) -> list:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def stable_lines(path: str) -> list:
    with open(path) as f:
        return [line.rstrip("\n") for line in f if line.strip() and json.loads(line).get("rec") not in VOLATILE]


def run_tool(binary: str, args: list, out: str, err: str | None = None) -> None:
    with open(out, "w") as fo:
        if err:
            with open(err, "w") as fe:
                subprocess.run([binary, *map(str, args)], stdout=fo, stderr=fe, check=True)
        else:
            subprocess.run([binary, *map(str, args)], stdout=fo, check=True)


def rust_n7_lists() -> dict:
    """The (m, r) lists compiled into the tool's n = 7 checks, parsed from the bound source."""
    src = open(os.path.join(HERE, TOOL)).read()
    out = {}
    for name, key in (("split", "split"), ("z2", "Z2"), ("odd", "odd")):
        m = re.search(r"let %s: &\[\(u32, u32\)\] = &\[(.*?)\];" % name, src)
        out[key] = sorted([int(a), int(b)] for a, b in re.findall(r"\((\d+), (\d+)\)", m.group(1)))
    return out


def stage_regression(rd: str, binary: str) -> tuple:
    checks = []
    for name, q, n, fixture in REGRESSION:
        out = os.path.join(rd, f"{name}.jsonl")
        t = time.time()
        run_tool(binary, [q, n, "exhaustive", "cosets", THREADS], out)
        new, ref = stable_lines(out), stable_lines(os.path.join(HERE, fixture))
        first = next((i for i, (a, b) in enumerate(zip(new, ref)) if a != b), None)
        checks.append({"name": name, "q": q, "n": n, "fixture": fixture, "fixture_sha256": _sha256(os.path.join(HERE, fixture)),
                       "rows_new": len(new), "rows_fixture": len(ref), "identical": new == ref,
                       "first_difference_line": first, "wall_s": round(time.time() - t, 1)})
    spec = {}
    for line in subprocess.check_output([sys.executable, os.path.join(HERE, "spectrum.py"), "3", "5", "7"], text=True).splitlines():
        d = json.loads(line)
        spec[d["n"]] = d
    for n, exp in SIBLING_SPECTRA.items():
        t = spec[n]["types"]
        ok = t["odd"]["genera"] == exp["odd"] and all(t[k]["floor"] == v for k, v in exp["floor"].items())
        checks.append({"name": f"spectrum_n{n}_vs_sibling", "identical": ok,
                       "observed": {"odd": t["odd"]["genera"], "floor": {k: t[k]["floor"] for k in exp["floor"]}}, "expected": exp})
    rl = rust_n7_lists()
    t7 = spec[7]["types"]
    for key in ("split", "Z2", "odd"):
        abstract = sorted(x for x in t7[key]["m_r"])
        checks.append({"name": f"spectrum_n7_{key}_vs_tool", "identical": abstract == rl[key], "spectrum_py": abstract, "tool": rl[key]})
    checks.append({"name": "spectrum_n7_m_values", "identical": spec[7]["m_values_all"] == [1, 3, 4, 6, 7],
                   "observed": spec[7]["m_values_all"]})
    ok = all(c["identical"] for c in checks)
    with open(os.path.join(rd, "regression.json"), "w") as f:
        json.dump({"experiment": EXP, "pass": ok, "checks": checks, "spectrum": spec}, f, indent=1, sort_keys=True)
    return ok, {"regression_pass": ok, "checks": len(checks), "failed": [c["name"] for c in checks if not c["identical"]]}


def stage_construct(rd: str, binary: str) -> tuple:
    rows = []
    for q in CONSTRUCT_Q:
        out = os.path.join(rd, f"construct-q{q}.jsonl")
        run_tool(binary, [q, 7, "construct", "-", THREADS], out)
        rows.append(next(r for r in load_jsonl(out) if r["rec"] == "construct"))
    bad = [r["q"] for r in rows if r["configs_other"] != 0 or r["configs_m3_r7"] != r["configs"]]
    return not bad, {"q": [r["q"] for r in rows], "j_genus7": [r["j_genus7"] for r in rows], "j_split": [r["j_split"] for r in rows],
                     "configs_not_m3_r7_at_q": bad}


def stage_char2(rd: str) -> tuple:
    out = os.path.join(rd, "char2.jsonl")
    with open(out, "w") as f:
        subprocess.run([sys.executable, os.path.join(HERE, "char2_magic.py"), *map(str, CHAR2_L)], stdout=f, check=True)
    rows = load_jsonl(out)
    return True, {"l": [r["l"] for r in rows], "matches_prediction": [r["matches_prediction"] for r in rows],
                  "lcm_mismatches": [r["m_equals_deg_lcm_ord_b_x_plus_1_mismatches"] for r in rows]}


def stage_census(rd: str, binary: str) -> tuple:
    out = os.path.join(rd, "census-n7-q3.jsonl")
    run_tool(binary, [3, 7, f"strata:{STRATA_K}", "cosets", THREADS], out, os.path.join(rd, "census-progress.log"))
    recs = load_jsonl(out)
    tot = next(r for r in recs if r["rec"] == "totals")
    dc = next(r for r in recs if r["rec"] == "derived_checks")
    mism = tot["mismatches"]
    return mism == 0, {"models_total": tot["models_total"], "picked": tot["picked"], "strata": tot["strata"],
                       "mismatches": mism, "violations": dc["violations"], "structures_per_model": tot["structures_per_model"]}


def stage_lean(rd: str) -> tuple:
    log = os.path.join(rd, "lean-build.log")
    lake = shutil.which("lake") or (os.path.expanduser("~/.elan/bin/lake") if os.path.exists(os.path.expanduser("~/.elan/bin/lake")) else None)
    if not lake:
        with open(log, "w") as f:
            f.write("lake not found on PATH or in ~/.elan/bin; Lean lemmas not built\n")
        res = {"status": "toolchain_unavailable", "built": False}
    else:
        work = tempfile.mkdtemp(prefix="pext-lean-")
        try:
            for name in ("CoverCensusN7.lean", "lakefile.toml", "lean-toolchain"):
                shutil.copy(os.path.join(HERE, "lean", name), work)
            p = subprocess.run([lake, "build"], cwd=work, capture_output=True, text=True)
            with open(log, "w") as f:
                f.write(p.stdout + p.stderr)
            text = p.stdout + p.stderr
            src = open(os.path.join(HERE, "lean", "CoverCensusN7.lean")).read()
            bad = [w for w in ("sorry", "native_decide") if re.search(r"\b%s\b" % w, src.split("-/", 1)[1])]
            axioms = re.findall(r"'([^']+)' (depends on axioms: \[[^\]]*\]|does not depend on any axioms)", text)
            custom = [a for a, s in axioms if any(x not in ("propext", "Quot.sound", "Classical.choice")
                                                  for x in re.findall(r"[\w.]+", s.split("[", 1)[1]) if "[" in s)]
            res = {"status": "built" if p.returncode == 0 else "build_failed", "built": p.returncode == 0,
                   "returncode": p.returncode, "axioms": dict(axioms), "forbidden_tokens": bad, "custom_axioms": custom}
        finally:
            shutil.rmtree(work, ignore_errors=True)
    with open(os.path.join(rd, "lean.json"), "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)
    ok = res["status"] in ("built", "toolchain_unavailable") and not res.get("forbidden_tokens") and not res.get("custom_axioms")
    return ok, res


def stage_analyze(rd: str, up: dict) -> tuple:
    import analyze  # same bound directory
    an = analyze.analyze(up)
    with open(os.path.join(rd, "analysis.json"), "w") as f:
        json.dump(an, f, indent=1, sort_keys=True)
    with open(os.path.join(rd, "floor-table.md"), "w") as f:
        f.write(analyze.floor_table_md(an))
    return True, {"headline": an["headline"], "predictions": {k: v["outcome"] for k, v in an["predictions"].items()},
                  "valid": an["valid"], "invalid_reasons": an["invalid_reasons"]}


def cmd_trial(a: argparse.Namespace) -> int:
    t0 = time.time()
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(a.plan) as f:
        plan = json.load(f)
    trial = next(t for t in plan["trials"] if t["id"] == a.trial_id)
    assert trial["run_id"] == a.run_id, "run id does not match the plan"
    rd = a.run_dir
    os.makedirs(rd, exist_ok=True)
    up = {k: (v if os.path.isabs(v) else os.path.join(RUNS_DIR, v)) for k, v in trial.get("inputs_from", {}).items()}
    build = tempfile.mkdtemp(prefix="pext-build-")
    status, reason, summary, code = "completed_valid", None, {}, 0
    try:
        stage = trial["stage"]
        binary = build_tool(build) if stage in ("regression", "construct", "census") else None
        if stage == "regression":
            ok, summary = stage_regression(rd, binary)
        elif stage == "construct":
            ok, summary = stage_construct(rd, binary)
        elif stage == "char2":
            ok, summary = stage_char2(rd)
        elif stage == "census":
            ok, summary = stage_census(rd, binary)
        elif stage == "lean":
            ok, summary = stage_lean(rd)
        elif stage == "analyze":
            sys.path.insert(0, HERE)
            ok, summary = stage_analyze(rd, up)
        else:
            raise ValueError(f"unknown stage {stage}")
        if not ok:
            status, code = "invalid_measurement", 1
            reason = f"{stage}: instrument check failed (see raw-result.json summary); no later trial is read as evidence"
        with open(os.path.join(rd, "raw-result.json"), "w") as f:
            json.dump({"experiment": EXP, "trial_id": a.trial_id, "run_id": a.run_id, "attack_claimed": False,
                       "summary": summary, "invalid_reason": reason}, f, indent=1, sort_keys=True)
    except Exception as e:  # recorded as failed_infrastructure, never a metric
        status, reason, code = "failed", f"failed_infrastructure: {type(e).__name__}: {e}", 1
        with open(os.path.join(rd, "raw-result.json"), "w") as f:
            json.dump({"experiment": EXP, "trial_id": a.trial_id, "run_id": a.run_id, "attack_claimed": False,
                       "summary": {}, "invalid_reason": reason}, f, indent=1)
    finally:
        shutil.rmtree(build, ignore_errors=True)
    commit, dirty = _git_commit()
    ru_c, ru_s = resource.getrusage(resource.RUSAGE_CHILDREN), resource.getrusage(resource.RUSAGE_SELF)
    manifest = {"run": {
        "id": a.run_id, "experiment_id": EXP, "hypothesis_id": HYPOTHESIS_ID,
        "task_id": plan.get("task_id"), "trial_id": a.trial_id, "role": "executor",
        "recorded_at": started[:10], "status": status, "attack_claimed": False,
        "validity": {"status": status, "reason": reason or "run.py recorded no invalidation; check.py "
                     "and independent review decide validity", "failure_class": None},
        "code": {"commit": commit, "dirty": dirty, "branch": None,
                 "command": shlex.join(getattr(sys, "orig_argv", None) or [sys.executable, *sys.argv]), "code_sha256": code_hashes(),
                 "trial_plan_sha256": _sha256(a.plan), "working_directory": os.getcwd()},
        "environment": {"host": platform.node(), "operating_system": platform.platform(),
                        "python_version": sys.version.split()[0], "rustc_version": _version(["rustc", "--version"]),
                        "processor_count": os.cpu_count(), "source": "manifest.yaml /run/environment"},
        "inputs": {"curve_id": None, "seed": 20261012,
                   "parameters": {"trial_id": a.trial_id, "stage": trial["stage"], "inputs_from": trial.get("inputs_from", {}),
                                  "plan": a.plan, "rustc_flags": RUSTC_FLAGS, "threads": THREADS, "strata_k": STRATA_K,
                                  "construct_q": list(CONSTRUCT_Q), "char2_l": list(CHAR2_L)}},
        "timing": {"started_at": started, "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "wall_seconds": round(time.time() - t0, 3)},
        "resources": {"peak_rss_bytes": int(max(ru_c.ru_maxrss, ru_s.ru_maxrss) * 1024),
                      "cpu_seconds": round(ru_c.ru_utime + ru_c.ru_stime + ru_s.ru_utime + ru_s.ru_stime, 3)},
        "result": {"metrics": {"raw_result": "raw-result.json"} if code == 0 else {},
                   "valid": status == "completed_valid", "invalid_reason": reason, "raw_result": "raw-result.json",
                   "certificate": {"kind": "none", "verified": True, "verifier": "no-claim",
                                   "note": "exact structural counts (cover genus by branch data) on toy fields; no curve over F_q "
                                           "is built, no transfer, discrete logarithm, cost or speedup is claimed"}},
        "artifacts": [n for n in trial["artifacts"] if n != "manifest.yaml"],
    }}
    with open(os.path.join(rd, "manifest.yaml"), "w") as f:
        yaml.safe_dump(manifest, f, sort_keys=False)
    return code


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("trial")
    s.add_argument("--run-dir", required=True)
    s.add_argument("--run-id", required=True)
    s.add_argument("--trial-id", required=True)
    s.add_argument("--plan", required=True)
    s.set_defaults(f=cmd_trial)
    a = ap.parse_args()
    sys.exit(a.f(a))


if __name__ == "__main__":
    main()
