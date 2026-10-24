"""EXP-PFDR-bb0d26 output checker.

  check.py <run_dir> <trial-plan.json> <trial-id>     exit 0 (CHECK OK) or 3 (CHECK FAIL)
  check.py spec-consistency <specification.yaml> [--mode pre-freeze|post-freeze] [--impl-dir DIR]

Producer-written; it is not independent review and it never edits an artifact or
interprets a result. The trial check covers, per stage:

  selftest  selftest.json passes with >= 40 kernel-vs-brute checks, every recorded check
            has expected == observed, and design.json equals the design table re-derived
            from the closed-form sizing rule.
  census    every planned (cell, curve) key is present exactly once as an ok record (or a
            degenerate one) or is accounted for by a failed_infrastructure record for that
            same key; a seeded replay of up to 4 small-n jobs is recomputed field by field,
            and every set of each sampled job is recounted by brute force in Python with
            no kernel.
  analyze   per cell S, M, kappa, z, z_cal, the plant statistics, the class, the
            calibration gate, fraction_valid, the flagged list, the toy reading and the
            headline are re-derived from the jobs files. The bootstrap interval is read as
            recorded (it is the producer's seeded resampling); replication kappa, z and
            survival are recomputed from the replication jobs when they are present.

spec-consistency compares every design constant of the specification with run.py. Before the
freeze the <RUN:...> tokens and FILL_AT_FREEZE entries are expected to be unfilled; after the
freeze they must be filled and the shas must match the real files.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
import random  # noqa: E402
import re  # noqa: E402
import shutil  # noqa: E402
import statistics  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run  # noqa: E402  (same sha256-bound directory)

ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
IMPL_REL = "experiments/EXP-PFDR-bb0d26/implementation/"
SUPERVISOR_NAMES = ("launch.json", "execution-receipt.json", "command.txt", "environment.json",
                    "stdout.log", "stderr.log", "check.stdout.log", "check.stderr.log")
SMALL_N = 512            # replayed jobs are drawn from records with n <= SMALL_N
MIN_KERNEL_CHECKS = 40


class CheckFail(Exception):
    pass


def fail(msg: str) -> None:
    raise CheckFail(msg)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_jsonl(path: str) -> list[dict]:
    with open(path) as f:
        return [json.loads(ln) for ln in f if ln.strip()]


# ---------------------------------------------------------------- independent counting

def brute(labels: list[int], p: int) -> tuple[int, int]:
    """C and D by a dictionary over all pairs; shares no code with run.py or the kernel."""
    sums: dict[int, int] = {}
    for i, u in enumerate(labels):
        for v in labels[i + 1:]:
            s = (u + v) % p
            sums[s] = sums.get(s, 0) + 1
    return sum(m * (m - 1) // 2 for m in sums.values()), len(sums)


def _mean(xs):
    return sum(xs) / len(xs)


def _svar(xs):
    m = _mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def _close(a, b) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12)


# ---------------------------------------------------------------- trial check

def _paths(plan_up: dict, runs_root: str | None) -> dict:
    root = runs_root or run.RUNS_DIR
    return {k: (v if os.path.isabs(v) else os.path.join(root, v)) for k, v in plan_up.items()}


def _check_plan_entry(plan: dict, trial: dict, plan_path: str) -> None:
    """Strict (production) plan checks: the trial equals the TRIAL_TABLE entry of run.py."""
    row = next((t for t in run.TRIAL_TABLE if t["id"] == trial["id"]), None)
    if row is None:
        fail(f"trial {trial['id']} is not in run.TRIAL_TABLE")
    if plan.get("experiment_id") != run.EXP:
        fail("plan experiment_id differs")
    for key in ("stage", "block", "memory_mb", "watchdog_seconds"):
        if trial.get(key) != row[key]:
            fail(f"plan {key} {trial.get(key)!r} != {row[key]!r}")
    if sorted(trial["artifacts"]) != sorted(row["artifacts"]):
        fail("plan artifacts differ from the declared artifacts")
    if sorted(trial.get("inputs_from", {})) != sorted(row["inputs_from"]):
        fail("plan inputs_from keys differ")
    if trial.get("output") != row["output"]:
        fail("plan output differs")
    for name in trial["artifacts"]:
        if "/" in name or name in SUPERVISOR_NAMES:
            fail(f"artifact name {name} is not a flat producer name")
    if not trial.get("watchdog_reason"):
        fail("trial has no watchdog_reason")
    for argv in (trial.get("argv", []), trial.get("check_argv", [])):
        if any("bedrock" in str(x).lower() for x in argv):
            fail("an argv names a forbidden provider string")
    if "real" in trial["id"]:
        fail("a real-curve trial is outside the approved scope")


def _check_sources(plan: dict, manifest: dict | None) -> None:
    src = plan.get("source_sha256") or {}
    if not src:
        fail("plan has an empty source_sha256")
    for rel, want in src.items():
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path) or sha256_file(path) != want:
            fail(f"bound source {rel} differs from the trial plan")
        if manifest is not None and rel.startswith(IMPL_REL):
            key = rel[len(IMPL_REL):]
            got = manifest["run"]["code"]["code_sha256"].get(key)
            if got is not None and got != want:
                fail(f"manifest code_sha256 of {key} differs from the trial plan")


def check_trial(run_dir: str, plan_path: str, trial_id: str, runs_root: str | None = None,
                relaxed: bool = False) -> str:
    """Raises CheckFail. relaxed=True (unit tests only) accepts a synthetic plan and design."""
    import yaml
    with open(plan_path) as f:
        plan = json.load(f)
    trial = next((t for t in plan["trials"] if t["id"] == trial_id), None)
    if trial is None:
        fail(f"trial {trial_id} not in the plan")
    if not relaxed:
        _check_plan_entry(plan, trial, plan_path)
    for name in trial["artifacts"]:
        path = os.path.join(run_dir, name)
        if not os.path.exists(path):
            fail(f"missing artifact {name}")
        if os.path.getsize(path) == 0 and name not in trial.get("allow_empty_artifacts", []):
            fail(f"empty artifact {name}")
    with open(os.path.join(run_dir, "raw-result.json")) as f:
        raw = json.load(f)
    if (raw.get("invalid_reason") or "").startswith("failed_infrastructure: "):
        fail(f"trial recorded {raw['invalid_reason']}")
    if raw.get("trial_id") != trial_id or raw.get("run_id") != trial["run_id"] or raw.get("experiment") != run.EXP:
        fail("raw-result identity differs from the plan")
    with open(os.path.join(run_dir, "manifest.yaml")) as f:
        manifest = yaml.safe_load(f)
    mr = manifest["run"]
    if mr["id"] != trial["run_id"] or mr["trial_id"] != trial_id or mr["experiment_id"] != run.EXP:
        fail("manifest identity differs from the plan")
    if mr["code"]["trial_plan_sha256"] != sha256_file(plan_path):
        fail("manifest trial_plan_sha256 differs from the plan file")
    _check_sources(plan, manifest)
    up = _paths(trial.get("inputs_from", {}), runs_root)
    stage = trial["stage"]
    if stage == "selftest":
        _check_selftest(run_dir, relaxed)
    elif stage == "census":
        _check_census(run_dir, trial, up, relaxed)
    elif stage == "analyze":
        _check_analyze(run_dir, trial, up, relaxed)
    else:
        fail(f"unknown stage {stage}")
    return trial_id


def _design_cells(path: str, relaxed: bool) -> list[dict]:
    with open(path) as f:
        design = json.load(f)
    if not relaxed and design != json.loads(json.dumps(run.design_table())):
        fail("design.json does not re-derive from the closed-form sizing rule")
    return design["toy_cells"]


def _check_selftest(run_dir: str, relaxed: bool) -> None:
    with open(os.path.join(run_dir, "selftest.json")) as f:
        st = json.load(f)
    checks = st.get("checks", [])
    kn = [c for c in checks if c["name"].startswith("kernel-vs-brute:")]
    if not st.get("pass") or len(kn) < MIN_KERNEL_CHECKS:
        fail(f"selftest did not pass with >= {MIN_KERNEL_CHECKS} kernel-vs-brute checks")
    for c in checks:
        if c["expected"] != c["observed"] or not c["pass"]:
            fail(f"selftest check {c['name']} recorded a difference")
    for needed in ("hand-built-one-coincidence", "design-anchor-b28-n256", "design-anchor-b28-n512"):
        if not any(c["name"] == needed for c in checks):
            fail(f"selftest lacks the check {needed}")
    if sum(c["name"].startswith("scaling-identity:") for c in checks) < 12:
        fail("selftest lacks the 12 scaling-identity checks")
    if sum(c["name"].startswith("builder-vs-slow:") for c in checks) < 3:
        fail("selftest lacks the 3 builder-vs-slow checks")
    with open(os.path.join(run_dir, "design.json"), "rb") as f:
        if not relaxed and f.read() != run.design_bytes():
            fail("design.json differs byte for byte from the re-derived design table")


def _status_class(s: str) -> str:
    if s == "ok" or s == "degenerate":
        return s
    if s.startswith("failed_infrastructure"):
        return "failed"
    fail(f"unknown record status {s!r}")
    return ""


def _check_census(run_dir: str, trial: dict, up: dict, relaxed: bool) -> None:
    block = trial["block"]
    recs = load_jsonl(os.path.join(run_dir, f"toy-{block}-jobs.jsonl"))
    cells = _design_cells(up["design"], relaxed)
    cmap = {c["cell"]: c for c in cells}
    only = None
    if block == "rep":
        with open(up["flags"]) as f:
            only = set(json.load(f)["flagged_cells"])
        if only - set(cmap):
            fail("flags.json names a cell outside the design")
    planned = {(c["cell"], i) for c in cells if only is None or c["cell"] in only
               for i in range(c["n_curves"])}
    keyed: dict[tuple, dict] = {}
    failed_keys = set()
    for r in recs:
        key = (r["cell"], r["c"])
        kind = _status_class(r["status"])
        if r.get("block") != block:
            fail(f"record {key} has block {r.get('block')}")
        if kind == "failed":
            failed_keys.add(key)
            continue
        if key in keyed:
            fail(f"duplicate record for {key}")
        keyed[key] = r
        cell = cmap.get(r["cell"])
        if cell is None or (r["bits"], r["r"], r["n"]) != (cell["bits"], cell["r"], cell["n"]):
            fail(f"{key} cell fields differ from the design")
        if kind == "ok":
            if len(r["null_C"]) != run.NULL_REPS or len(r["null_D"]) != run.NULL_REPS:
                fail(f"{key} does not hold {run.NULL_REPS} null counts")
            for fld in ("gap_C", "gap_D", "plant_m", "plant_internal", "plant_C", "plant_D", "plant_feasible"):
                if r.get(fld) is None:
                    fail(f"{key} lacks {fld}")
            for fld in ("T", "enumerated", "duplicate_skips", "first", "last"):
                if fld not in (r.get("gap_meta") or {}):
                    fail(f"{key} gap_meta lacks {fld}")
            pairs = r["n"] * (r["n"] - 1) // 2
            if any(not 1 <= d <= pairs for d in r["null_D"] + [r["gap_D"], r["plant_D"]]):
                fail(f"{key} has a D outside [1, n(n-1)/2]")
    if set(keyed) - planned:
        fail("records outside the plan")
    missing = planned - set(keyed)
    unaccounted = missing - failed_keys
    if unaccounted:
        fail(f"{len(unaccounted)} planned jobs absent with no failed_infrastructure record for that key")
    small = sorted(k for k, r in keyed.items() if r["n"] <= SMALL_N)
    sample = random.Random(f"check|{run.EXP}|{block}").sample(small, min(4, len(small)))
    if not sample:
        return
    bd = tempfile.mkdtemp(prefix="bb0d26-check-")
    try:
        kernel = run.build_kernel(bd)
        for key in sample:
            rec, cell = keyed[key], cmap[key[0]]
            again = run.job(kernel, cell, block, key[1])
            a = {k: v for k, v in again.items() if k != "seconds"}
            b = {k: v for k, v in rec.items() if k != "seconds"}
            if a != b:
                bad = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
                fail(f"replay mismatch {key} fields {bad}")
            if rec["status"] == "ok":
                _brute_recount(rec, cell, block, key[1])
    finally:
        shutil.rmtree(bd, ignore_errors=True)


def _brute_recount(rec: dict, cell: dict, block: str, c: int) -> None:
    """Rebuild every set of a job with run.py's builders and recount it without the kernel."""
    E, _ = run.get_curve(cell["bits"], block, c)
    cid, p = cell["cell"], E.p
    for k in range(run.NULL_REPS):
        C, D = brute(run.null_builder(E, cell["n"], run._rng("null", block, cid, c, k)), p)
        if (C, D) != (rec["null_C"][k], rec["null_D"][k]):
            fail(f"brute-force recount mismatch of null set {k} at {(cid, c)}")
    labels, meta, st = run.gap_builder(E, cell["r"], cell["n"], run._rng("gap", block, cid, c))
    if st != "ok" or brute(labels, p) != (rec["gap_C"], rec["gap_D"]) or meta != rec["gap_meta"]:
        fail(f"brute-force recount mismatch of the log-GAP set at {(cid, c)}")
    pl, pm = run.planted_builder(E, cell["n"], run._rng("plant", block, cid, c), rec["null_C"],
                                 lambda ls: brute(ls, p)[0])
    if brute(pl, p) != (rec["plant_C"], rec["plant_D"]) or pm["m"] != rec["plant_m"] \
            or pm["internal"] != rec["plant_internal"] or pm["feasible"] != rec["plant_feasible"]:
        fail(f"brute-force recount mismatch of the planted set at {(cid, c)}")


def _by_curve(recs: list[dict], cell: str, planned: int) -> dict[int, dict]:
    out: dict[int, dict] = {}
    for r in recs:
        if r["cell"] == cell and r["status"] == "ok" and 0 <= r["c"] < planned and r["c"] not in out:
            out[r["c"]] = r
    return out


def _rederive(rs: list[dict]) -> dict:
    """Independent re-derivation of the closed-form statistics of one cell (no bootstrap)."""
    rs = sorted(rs, key=lambda r: r["c"])
    S = sum(r["gap_C"] for r in rs)
    PL = sum(r["plant_C"] for r in rs)
    M = sum(_mean(r["null_C"]) for r in rs)
    V = sum(_svar(r["null_C"]) for r in rs)
    sd = math.sqrt(V * (1 + 1 / run.NULL_REPS)) if V > 0 else None
    pS = sum(r["null_C"][0] for r in rs)
    pM = sum(_mean(r["null_C"][1:]) for r in rs)
    pV = sum(_svar(r["null_C"][1:]) for r in rs)
    fm = sum(3 * math.comb(r["n"], 4) / r["p"] for r in rs)
    ev = [i for i, r in enumerate(rs) if r["c"] % 2 == 0]
    od = [i for i, r in enumerate(rs) if r["c"] % 2 == 1]
    mean_c = [_mean(r["null_C"]) for r in rs]
    return {
        "S": S, "M": M, "V": V, "kappa": S / M if M > 0 else None,
        "z": (S - M) / sd if sd else None,
        "plant_kappa": PL / M if M > 0 else None, "plant_z": (PL - M) / sd if sd else None,
        "plant_feasible_all": all(r["plant_feasible"] for r in rs),
        "z_cal": (pS - pM) / math.sqrt(pV * (1 + 1 / (run.NULL_REPS - 1))) if pV > 0 else None,
        "d_ratio": sum(r["gap_D"] for r in rs) / sum(_mean(r["null_D"]) for r in rs),
        "null_mean_over_formula": M / fm if fm > 0 else None,
        "kappa_even": sum(rs[i]["gap_C"] for i in ev) / sum(mean_c[i] for i in ev) if ev and sum(mean_c[i] for i in ev) > 0 else None,
        "kappa_odd": sum(rs[i]["gap_C"] for i in od) / sum(mean_c[i] for i in od) if od and sum(mean_c[i] for i in od) > 0 else None,
    }


def _class_of(d: dict, ci) -> str:
    g = run.GATES
    powered = d["M"] >= run.TARGET
    planted = bool(d["plant_feasible_all"] and d["plant_kappa"] is not None and d["plant_kappa"] >= g["plant_kappa"]
                   and d["plant_z"] is not None and d["plant_z"] > g["plant_z"])
    if not powered:
        return "inconclusive_underpowered"
    if not planted:
        return "inconclusive_plant_not_recovered"
    k, z = d["kappa"], d["z"]
    if k is not None and z is not None and abs(k - 1) >= g["flag_dev"] and abs(z) > g["flag_z"]:
        return "flagged"
    if k is not None and ci is not None and abs(k - 1) < g["null_dev"] \
            and g["null_ci_lo"] <= ci[0] and ci[1] <= g["null_ci_hi"]:
        return "null"
    return "intermediate"


def _check_analyze(run_dir: str, trial: dict, up: dict, relaxed: bool) -> None:
    final = "rep" in trial.get("inputs_from", {})
    with open(os.path.join(run_dir, trial["output"])) as f:
        an = json.load(f)
    with open(os.path.join(run_dir, "flags.json")) as f:
        flags = json.load(f)
    cells = _design_cells(up["design"], relaxed)
    main = load_jsonl(up["main"])
    rep = load_jsonl(up["rep"]) if final and os.path.exists(up["rep"]) else []
    rows = {r["cell"]: r for r in an["cells"]}
    if [r["cell"] for r in an["cells"]] != [c["cell"] for c in cells]:
        fail("analysis cells differ from the design cells")
    if an.get("stage") != ("final" if final else "main"):
        fail("analysis stage differs from the trial")
    classes, zcal = [], []
    for cell in cells:
        row = rows[cell["cell"]]
        okc = _by_curve(main, cell["cell"], cell["n_curves"])
        if len(okc) < cell["n_curves"]:
            if row["cls"] != "invalid":
                fail(f"{cell['cell']} has fewer ok records than n_curves but class {row['cls']}")
            classes.append("invalid")
            continue
        if row["cls"] == "invalid":
            fail(f"{cell['cell']} is complete but recorded invalid")
        d = _rederive(list(okc.values()))
        for key in ("S", "M", "V", "kappa", "z", "plant_kappa", "plant_z", "z_cal", "d_ratio",
                    "null_mean_over_formula", "kappa_even", "kappa_odd"):
            if not _close(d[key], row.get(key)):
                fail(f"{cell['cell']} {key} does not recompute")
        if d["plant_feasible_all"] != row["plant_feasible_all"] or row["curves"] != cell["n_curves"]:
            fail(f"{cell['cell']} plant_feasible_all or curves do not recompute")
        ci = row.get("ci95")
        if not (isinstance(ci, list) and len(ci) == 2 and ci[0] <= ci[1]):
            fail(f"{cell['cell']} ci95 is not a recorded interval")
        cls = _class_of(d, ci)
        if cls != row["cls"]:
            fail(f"{cell['cell']} class {row['cls']} != re-derived {cls}")
        if row["powered"] != (d["M"] >= run.TARGET):
            fail(f"{cell['cell']} powered flag differs")
        classes.append(cls)
        if d["M"] >= run.TARGET and d["z_cal"] is not None:
            zcal.append(d["z_cal"])
    g = run.GATES
    cal_pass = len(zcal) > 1 and g["cal_sd_lo"] <= statistics.pstdev(zcal) <= g["cal_sd_hi"] \
        and abs(statistics.fmean(zcal)) <= g["cal_mean_abs"]
    rc = an["calibration"]
    if rc["pass"] != cal_pass or rc["n"] != len(zcal):
        fail("calibration gate does not re-derive")
    if zcal and not (_close(rc["mean"], statistics.fmean(zcal)) and
                     (len(zcal) < 2 or _close(rc["sd"], statistics.pstdev(zcal)))):
        fail("calibration mean or sd does not recompute")
    valid = [c for c in classes if c in run.VALID_CLASSES]
    frac = len(valid) / len(classes)
    if not _close(frac, an["fraction_valid"]):
        fail("fraction_valid does not recompute")
    flagged = [c["cell"] for c, k in zip(cells, classes) if k == "flagged"]
    if flagged != an["flagged_cells"] or flags.get("flagged_cells") != flagged:
        fail("flagged cells do not re-derive")
    surv, pend = [], []
    cmap = {c["cell"]: c for c in cells}
    for cid in flagged:
        rr = rows[cid]["replication"]
        mine = [x for x in rep if x["cell"] == cid]
        okc = _by_curve(rep, cid, cmap[cid]["n_curves"])
        status = "not_run" if not mine else ("incomplete" if len(okc) < cmap[cid]["n_curves"] else "complete")
        if not isinstance(rr, dict) or rr.get("status") != status:
            fail(f"{cid} replication status does not re-derive ({status})")
        if status == "complete":
            d = _rederive(list(okc.values()))
            same = (d["kappa"] - 1) * (rows[cid]["kappa"] - 1) > 0
            sv = bool(same and d["z"] is not None and abs(d["z"]) > g["rep_z"]
                      and abs(d["kappa"] - 1) >= g["rep_dev"])
            if not (_close(d["kappa"], rr["kappa"]) and _close(d["z"], rr["z"])) or sv != rr["survives"]:
                fail(f"{cid} replication statistics do not recompute")
        elif rr.get("survives"):
            fail(f"{cid} survives without a complete replication")
        surv.append(bool(rr["survives"]))
        pend.append(status != "complete")
    for cid, row in rows.items():
        if cid not in flagged and row.get("replication") is not None:
            fail(f"{cid} carries a replication but is not flagged")
    outcome = run.reading(cal_pass, frac, classes, surv, pend)
    if outcome != an["outcome"]:
        fail(f"outcome {an['outcome']} != re-derived {outcome}")
    headline = run.headline_of(outcome)
    if headline != an["headline"]:
        fail(f"headline {an['headline']} != re-derived {headline}")


# ---------------------------------------------------------------- specification consistency

# Digests of standardized-curve domain constants (sha256 of the decimal integer). Only digests are
# stored, so no such constant appears in any bound artifact, including this file.
STD_DIGESTS = frozenset("""
1c5f65ce01e30de4314899e861bdafef288d8346b540236601a4e45a49738b79
23867dfb22358427b418b8951030a4a37803b9da376533a00dc762187633a366
2de60ca5eb7b55eefa5eeb725b8a9051d661ea37a8cb4b5a3e7bd97728c26fd0
47be6fcb455eea93dcb41bc6dfa7c77368f35b06fbe2e7b896c566a13334144c
4da9030b69fe4f935c3b3e50af329e7439a0a43fb912db43c9c0019709461702
5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9
605bea91d02c3098a684026dbcff1edc29b3751af17b031ae8c6628acfc4c78f
6bed75e10764f553945f01ba31e4df07d4ca4f1f8fdd346b6929cb4a2f540785
7902699be42c8a8e46fbbb4501726517e86b22c56a189f7625a6da49081b2451
794443ec19ef9f97f02b7f0157c0b8a83f20556936d5213da1191c60111ab330
816d5b091688e7719db27ead768a76fe9b6de8b7c338ec1bba55baaec7d42561
861bf70ef9425419cd0d9444e61ae77c946bc73d379da138512a8dbee55e7f09
""".split())

_HEX_RUN = re.compile(r"(?<![0-9A-Za-z])(?:0[xX])?([0-9a-fA-F]{40,})(?![0-9A-Za-z])")
_HEX_GROUPS = re.compile(r"(?<![0-9A-Za-z])((?:[0-9a-fA-F]{8}[ _:]){3,}[0-9a-fA-F]{8})(?![0-9A-Za-z])")
_DEC_RUN = re.compile(r"(?<![0-9A-Za-z.])(\d{50,})(?![0-9A-Za-z])")


def standard_constants_in(text: str) -> list[str]:
    """Hex or decimal literals in text that equal a standardized-curve domain constant."""
    found = []
    cands = [int(m, 16) for m in _HEX_RUN.findall(text)]
    cands += [int(re.sub(r"[ _:]", "", m), 16) for m in _HEX_GROUPS.findall(text)]
    cands += [int(m) for m in _DEC_RUN.findall(text)]
    for v in cands:
        d = hashlib.sha256(str(v).encode()).hexdigest()
        if d in STD_DIGESTS:
            found.append(d[:12])
    return found


def _walk_impl(impl_dir: str):
    for dp, dns, fns in os.walk(impl_dir):
        dns[:] = [d for d in dns if d != "__pycache__"]
        for fn in sorted(fns):
            yield os.path.join(dp, fn)


class Report:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.bad = 0

    def eq(self, name: str, spec_val, run_val) -> None:
        if spec_val == run_val:
            self.lines.append(f"OK    {name}: {run_val}")
        else:
            self.bad += 1
            self.lines.append(f"DIFF  {name}: specification {spec_val!r} != run.py {run_val!r}")

    def ok_if(self, name: str, cond: bool, why: str) -> None:
        if cond:
            self.lines.append(f"OK    {name}")
        else:
            self.diff(name, why)

    def note(self, msg: str) -> None:
        self.lines.append(f"NOTE  {msg}")

    def diff(self, name: str, why: str) -> None:
        self.bad += 1
        self.lines.append(f"DIFF  {name}: {why}")


def _num(s: str):
    s = s.replace(",", "")
    return float(s) if "." in s else int(s)


def spec_consistency(spec_path: str, mode: str = "post-freeze", impl_dir: str | None = None,
                     root: str | None = None) -> tuple[bool, list[str]]:
    import yaml
    impl_dir = impl_dir or HERE
    root = root or ROOT
    rep = Report()
    with open(spec_path) as f:
        text = f.read()
    spec = yaml.safe_load(text)
    E = spec["experiment"]

    def get(path: str):
        cur = E
        for part in path.split("."):
            if isinstance(cur, list) and "=" in part:
                k, v = part.split("=", 1)
                cur = next(x for x in cur if isinstance(x, dict) and x.get(k) == v)
            elif isinstance(cur, list):
                cur = cur[int(part)]
            elif isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                raise KeyError(path)
        return cur

    def rx(path: str, pattern: str, name: str, cast=_num):
        try:
            s = get(path)
        except (KeyError, IndexError):
            rep.diff(name, f"missing specification field {path}")
            return None
        m = re.search(pattern, s if isinstance(s, str) else json.dumps(s))
        if not m:
            rep.diff(name, f"pattern not found in {path}")
            return None
        return tuple(cast(g) for g in m.groups())

    def val(path: str, name: str, want) -> None:
        try:
            rep.eq(name, get(path), want)
        except (KeyError, IndexError):
            rep.diff(name, f"missing specification field {path}")

    g = run.GATES
    # ---- cells
    val("inputs.curves.toy_bits", "toy_bits", list(run.BITS))
    r = rx("inputs.toy_cells.rule", r"r in \{([\d, ]+)\} x n in \{([\d, ]+)\}", "toy_cells.rule",
           lambda s: [int(x) for x in s.split(",")])
    if r:
        rep.eq("ranks (cell rule)", r[0], list(run.RANKS))
        rep.eq("ns (cell rule)", r[1], list(run.NS))
    val("inputs.toy_cells.count", "toy cell count", len(run.cells()))
    rep.eq("toy cell count product", 45, len(run.BITS) * len(run.RANKS) * len(run.NS))
    val("inputs.toy_cells.cell_id", "cell_id format", "b<bits>-r<r>-n<n>")
    rep.eq("cell_id sample", "b20-r1-n256", run.cells()[0]["cell"])
    for i, (nm, want) in enumerate((("bits", run.BITS), ("r", run.RANKS), ("n", run.NS))):
        x = rx(f"independent_variables.{i}", r"\{([\d, ]+)\}", f"independent_variables {nm}",
               lambda s: [int(v) for v in s.split(",")])
        if x:
            rep.eq(f"independent_variables {nm}", x[0], list(want))
    for i, (nm, want) in enumerate((("bits", run.BITS), ("rank_r", run.RANKS), ("set_size_n", run.NS))):
        try:
            led = get(f"variable_ledger.independent.{i}")
            rep.eq(f"variable_ledger {nm}", [led["name"], led["levels"]], [nm, list(want)])
        except (KeyError, IndexError):
            rep.diff(f"variable_ledger {nm}", "missing")
    # ---- seed blocks
    for path in ("inputs.curves.seed_rule", "replication.seed_rule"):
        x = rx(path, r"main ([\d,]+), replication ([\d,]+), selftest ([\d,]+)", f"seed blocks ({path})")
        if x:
            rep.eq(f"seed blocks ({path})", list(x),
                   [run.SEED_BLOCK["main"], run.SEED_BLOCK["rep"], run.SEED_BLOCK["selftest"]])
    val("replication.seeds", "replication.seeds", [run.SEED_BLOCK["main"], run.SEED_BLOCK["rep"], run.SEED_BLOCK["selftest"]])
    x = rx("inputs.curves.seed_rule", r"reserved range of this experiment is\s+([\d,]+) to ([\d,]+)", "reserved seed range")
    if x:
        rep.eq("seed blocks inside the reserved range", True,
               all(x[0] <= v and v + 99_999 <= x[1] for v in run.SEED_BLOCK.values()))
    # ---- null replicates
    val("variable_ledger.factors.name=null_replicates.value", "null_replicates", run.NULL_REPS)
    x = rx("objective", r"(\d+) uniformly random label sets", "null reps (objective)")
    if x:
        rep.eq("null reps (objective)", x[0], run.NULL_REPS)
    x = rx("inputs.statistics.per_cell", r"sqrt\(V \(1 \+ 1/(\d+)\)\)", "variance factor")
    if x:
        rep.eq("variance factor 1+1/B", x[0], run.NULL_REPS)
    x = rx("inputs.statistics.per_cell", r"variance factor 1 \+ 1/(\d+)\)", "z_cal variance factor")
    if x:
        rep.eq("z_cal variance factor 1+1/(B-1)", x[0], run.NULL_REPS - 1)
    x = rx("inputs.statistics.per_cell", r"\((\d+) replicates\)", "null replicates (statistics)")
    if x:
        rep.eq("null replicates (statistics)", x[0], run.NULL_REPS)
    x = rx("inputs.statistics.per_cell", r"\((\d+) resamples", "bootstrap resamples")
    if x:
        rep.eq("bootstrap resamples", x[0], run.BOOT_B)
    x = rx("inputs.statistics.per_cell", r"percentile ([\d.]+) and ([\d.]+)", "bootstrap percentiles")
    if x:
        rep.eq("bootstrap percentiles", list(x), list(run.BOOT_PCT))
    # ---- target, safety, clamp, p_ref, plant
    x = rx("inputs.statistics.powered", r"M >= (\d+)", "powered target")
    if x:
        rep.eq("powered target (statistics)", x[0], run.TARGET)
    x = rx("inputs.cell_classes.inconclusive_underpowered", r"M < (\d+)", "underpowered target")
    if x:
        rep.eq("underpowered target (class)", x[0], run.TARGET)
    x = rx("inputs.sizing", r"clamp\(ceil\(([\d.]+) x (\d+) / mu_ref\), (\d+), (\d+)\)", "sizing rule")
    if x:
        rep.eq("safety", x[0], run.SAFETY)
        rep.eq("sizing target", x[1], run.TARGET)
        rep.eq("n_curves floor", x[2], run.N_MIN)
        rep.eq("n_curves cap", x[3], run.N_MAX)
    x = rx("inputs.sizing", r"p_ref =\s+([\d.]+) x 2\^bits", "p_ref factor")
    if x:
        rep.eq("p_ref factor", x[0], run.P_REF_FACTOR)
    x = rx("inputs.sizing", r"The cap (\d+) is not\s+reached", "cap not reached")
    if x:
        rep.eq("cap statement", x[0], run.N_MAX)
        rep.eq("no cell reaches the cap", True, all(c["n_curves"] < x[0] for c in run.cells()))
    x = rx("inputs.sizing", r"bits 28,\s+n = 256 gives mu_ref about ([\d.]+) and about (\d+) curves; "
           r"bits 28, n = 512 gives about (\d+) and about (\d+) curves", "sizing anchors")
    if x:
        rep.eq("anchor n_curves b28 n256", x[1], run.n_curves(28, 256))
        rep.eq("anchor n_curves b28 n512", x[3], run.n_curves(28, 512))
        rep.eq("anchor mu_ref b28 n256", x[0], round(run.mu_ref(28, 256), 1))
        rep.eq("anchor mu_ref b28 n512", x[2], round(run.mu_ref(28, 512)))
    x = rx("inputs.sizing", r"mu_ref >= (\d+) gets (\d+) curves", "floor statement")
    if x:
        rep.eq("every cell with mu_ref >= threshold gets the floor", True,
               all(c["n_curves"] == x[1] == run.N_MIN for c in run.cells() if c["mu_ref"] >= x[0]))
    x = rx("inputs.planted_builder", r"internal\(m\) >= ([\d.]+) x", "plant fraction")
    if x:
        rep.eq("plant fraction", x[0], run.PLANT_FRACTION)
    x = rx("inputs.planted_builder", r"least integer in\s+\[(\d+), n/2\]", "plant m range")
    if x:
        rep.eq("plant m minimum", x[0], run.PLANT_M_MIN)
    val("variable_ledger.factors.name=plant_size_rule.value", "plant_size_rule", f"m least with internal >= {run.PLANT_FRACTION:.2f} x curve null mean")
    x = rx("controls.2.check", r"internal coincidences >= ([\d.]+) x", "plant fraction (C3)")
    if x:
        rep.eq("plant fraction (C3)", x[0], run.PLANT_FRACTION)
    x = rx("inputs.log_gap_builder", r"ceil\(([\d.]+) n\) \+ (\d+)", "half-box bound")
    if x:
        rep.eq("half-box factor", x[0], run.HALF_BOX_NUM / run.HALF_BOX_DEN)
        rep.eq("half-box pad", x[1], run.HALF_BOX_PAD)
    val("variable_ledger.factors.name=box_shape_and_fill_order.value", "box shape",
        f"half-box first nonzero coordinate positive, lexicographic, T least with half-box >= ceil({run.HALF_BOX_NUM / run.HALF_BOX_DEN} n) + {run.HALF_BOX_PAD}")
    # ---- plant recovery, flag, null, replication, calibration thresholds
    x = rx("inputs.cell_classes.inconclusive_plant_not_recovered", r"plant_kappa >= ([\d.]+) and plant_z > (\d+)", "plant recovery")
    if x:
        rep.eq("plant_kappa threshold", x[0], g["plant_kappa"])
        rep.eq("plant_z threshold", x[1], g["plant_z"])
    x = rx("preregistered_predictions.2.test", r"plant_kappa >= ([\d.]+) and plant_z > (\d+)", "P2")
    if x:
        rep.eq("P2 thresholds", list(x), [g["plant_kappa"], g["plant_z"]])
    x = rx("inputs.cell_classes.flagged", r"\|kappa - 1\| >= ([\d.]+) and \|z\| > (\d+)", "flagged class")
    if x:
        rep.eq("flag deviation", x[0], g["flag_dev"])
        rep.eq("flag z", x[1], g["flag_z"])
    x = rx("preregistered_predictions.1.test", r"\|kappa - 1\| >= ([\d.]+) at \|z\| > (\d+)", "P-detect")
    if x:
        rep.eq("P-detect thresholds", list(x), [g["flag_dev"], g["flag_z"]])
    x = rx("inputs.cell_classes.null", r"\|kappa - 1\| < ([\d.]+) and the bootstrap 95% interval inside \[([\d.]+), ([\d.]+)\]", "null class")
    if x:
        rep.eq("null deviation", x[0], g["null_dev"])
        rep.eq("null interval", [x[1], x[2]], [g["null_ci_lo"], g["null_ci_hi"]])
    x = rx("preregistered_predictions.0.test", r"\|kappa - 1\| < ([\d.]+) with the bootstrap 95% interval inside \[([\d.]+), ([\d.]+)\]", "P1")
    if x:
        rep.eq("P1 thresholds", list(x), [g["null_dev"], g["null_ci_lo"], g["null_ci_hi"]])
    x = rx("inputs.calibration_gate", r"sd of z_cal in \[([\d.]+), ([\d.]+)\] and \|mean of z_cal\| <= ([\d.]+)", "calibration gate")
    if x:
        rep.eq("calibration sd band", [x[0], x[1]], [g["cal_sd_lo"], g["cal_sd_hi"]])
        rep.eq("calibration mean bound", x[2], g["cal_mean_abs"])
    x = rx("controls.3.check", r"sd of z_cal in \[([\d.]+), ([\d.]+)\], \|mean\| <= ([\d.]+)", "calibration gate (C4)")
    if x:
        rep.eq("calibration (C4)", list(x), [g["cal_sd_lo"], g["cal_sd_hi"], g["cal_mean_abs"]])
    x = rx("inputs.replication_rule", r"\|z\| > (\d+) and \|kappa - 1\| >= ([\d.]+)", "replication rule")
    if x:
        rep.eq("replication z", x[0], g["rep_z"])
        rep.eq("replication deviation", x[1], g["rep_dev"])
    x = rx("inputs.toy_reading_rules.O-INVALID", r"fewer than (\d+)% of the 45 cells", "O-INVALID")
    if x:
        rep.eq("valid fraction floor", x[0] / 100, g["valid_min"])
    x = rx("inputs.toy_reading_rules.O-NULL", r"at least (\d+)% of the 45 cells", "O-NULL")
    if x:
        rep.eq("null valid fraction", x[0] / 100, g["null_valid_min"])
    # ---- classes, readings, headline
    try:
        ck = [k for k in get("inputs.cell_classes") if k not in ("order", "valid_cells")]
        rep.eq("cell class order", ck, list(run.CLASSES))
        rep.eq("valid classes", get("inputs.cell_classes.valid_cells"), "the classes " + ", ".join(run.VALID_CLASSES[:-1]) + " and " + run.VALID_CLASSES[-1])
        rk = [k for k in get("inputs.toy_reading_rules") if k not in ("field", "order")]
        rep.eq("reading rule order", rk, list(run.OUTCOMES))
        hk = [k for k in get("inputs.headline") if k not in ("field", "order", "note")]
        rep.eq("headline order", hk, ["FALSIFY_SCOPED", "NOT_EVIDENCE", "SUPPORT_SCOPED", "INCONCLUSIVE"])
        for hl, oc in (("FALSIFY_SCOPED", "O-STRUCT"), ("NOT_EVIDENCE", "O-INVALID"), ("SUPPORT_SCOPED", "O-NULL")):
            rep.eq(f"headline {hl}", get(f"inputs.headline.{hl}"), f"outcome is {oc}")
            rep.eq(f"run.py headline of {oc}", hl, run.headline_of(oc))
        rep.eq("run.py INCONCLUSIVE otherwise", "INCONCLUSIVE", run.headline_of("O-MIXED"))
    except (KeyError, IndexError):
        rep.diff("classes/readings/headline", "missing specification field")
    # ---- budget, trials, artifacts
    val("budget.maximum_workers", "workers", run.WORKERS)
    x = rx("budget.note", r"at most (\d+) worker processes", "workers (note)")
    if x:
        rep.eq("workers (note)", x[0], run.WORKERS)
    x = rx("budget.note", r"kernel timeout (\d+) s", "kernel timeout")
    if x:
        rep.eq("kernel timeout", x[0], run.KERNEL_TIMEOUT_S)
    x = rx("budget.note", r"trial memory caps ([\d/]+) MB", "trial memory caps", str)
    if x:
        rep.eq("trial memory caps", x[0], "/".join(str(t["memory_mb"]) for t in run.TRIAL_TABLE))
    val("budget.maximum_runs", "maximum_runs", len(run.TRIAL_TABLE))
    val("replication.independent_instances", "independent_instances", len(run.TRIAL_TABLE))
    val("budget.maximum_memory_gb", "maximum_memory_gb", 4)
    try:
        wc = get("budget.wall_clock_seconds_per_trial")
        rep.eq("watchdogs", wc, {t["id"]: t["watchdog_seconds"] for t in run.TRIAL_TABLE})
        trials = get("replication.trials")
        rep.eq("trial ids and stages", [(t["trial_id"], t["stage"]) for t in trials],
               [(t["id"], t["stage"]) for t in run.TRIAL_TABLE])
        se = get("stage_estimates")
        rep.eq("stage memory", [(s["trial_id"], s["memory_mb"]) for s in se],
               [(t["id"], t["memory_mb"]) for t in run.TRIAL_TABLE])
        rep.eq("depends_on chain", True, all(t["depends_on"] == ((run.TRIAL_TABLE[i - 1]["id"],) if i else ())
                                              for i, t in enumerate(run.TRIAL_TABLE)))
        tok_of = {t["trial_id"]: t["run_id"] for t in trials}
        arts: dict[str, set] = {t["trial_id"]: set() for t in trials}
        by_tok = {v: k for k, v in tok_of.items()}
        for path in get("required_artifacts"):
            m = re.match(r"experiments/EXP-PFDR-bb0d26/runs/([^/]+)/([^/]+)$", path)
            if not m:
                rep.diff("required_artifacts", f"not a flat run-directory path: {path}")
                continue
            tid = by_tok.get(m.group(1))
            if tid is None:
                rep.diff("required_artifacts", f"unknown run token in {path}")
                continue
            arts[tid].add(m.group(2))
        rep.eq("required artifacts per trial", {k: sorted(v) for k, v in arts.items()},
               {t["id"]: sorted(t["artifacts"]) for t in run.TRIAL_TABLE})
        rep.eq("no supervisor-generated artifact name", True,
               not any(n in SUPERVISOR_NAMES for v in arts.values() for n in v))
        rep.eq("no real-curve trial", True, not any("real" in t["trial_id"] for t in trials))
    except (KeyError, IndexError):
        rep.diff("budget/trials/artifacts", "missing specification field")
    # ---- freeze placeholders and bound shas
    _freeze_checks(rep, E, text, mode, impl_dir, root)
    # ---- held extension: no standardized-curve constant, no real-curve artifact
    hits = standard_constants_in(text)
    rep.ok_if("no standardized-curve constant in the specification", not hits, f"found {hits}")
    for path in _walk_impl(impl_dir):
        base = os.path.basename(path)
        if base.startswith("realcurves"):
            rep.diff("held extension", f"real-curve fixture present: {path}")
        try:
            with open(path, encoding="utf-8") as f:
                body = f.read()
        except (UnicodeDecodeError, OSError):
            continue
        h = standard_constants_in(body)
        if h:
            rep.diff("held extension", f"standardized-curve constant in {os.path.relpath(path, impl_dir)}")
    rep.eq("bound artifacts scanned", True, os.path.isdir(impl_dir))
    ok = rep.bad == 0
    rep.lines.append(f"SPEC-CONSISTENCY {'OK' if ok else 'FAIL'} ({mode}; {rep.bad} difference(s))")
    return ok, rep.lines


def _count_fill(node) -> int:
    if isinstance(node, dict):
        return sum(_count_fill(v) for v in node.values())
    if isinstance(node, list):
        return sum(_count_fill(v) for v in node)
    return 1 if node == "FILL_AT_FREEZE" else 0


def _freeze_checks(rep: Report, E: dict, text: str, mode: str, impl_dir: str, root: str) -> None:
    tokens = re.findall(r"<RUN:([A-Za-z0-9-]+)>", text)
    fills = _count_fill(E)       # scalar entries only; the prose mention in freeze_fills is not an entry
    want_tokens = [t["id"] for t in run.TRIAL_TABLE]
    sha_files = {"vendor/curve.py": os.path.join(impl_dir, "vendor", "curve.py"),
                 "fixtures/kat.json": os.path.join(impl_dir, "fixtures", "kat.json")}
    if mode == "pre-freeze":
        rep.note(f"pre-freeze: {len(tokens)} <RUN:...> occurrence(s) and {fills} FILL_AT_FREEZE entr(ies) "
                 "expected-unfilled")
        if tokens:
            rep.eq("pre-freeze token names", sorted(set(tokens)), sorted(want_tokens))
    elif mode == "post-freeze":
        rep.ok_if("no unfilled <RUN:...> token", not tokens, f"{len(tokens)} token occurrence(s) remain")
        rep.ok_if("no unfilled FILL_AT_FREEZE entry", fills == 0, f"{fills} entr(ies) remain")
        ids = [t.get("run_id") for t in E["replication"]["trials"]]
        rep.ok_if("five distinct minted run ids",
                  len(ids) == 5 and len(set(ids)) == 5 and all(re.fullmatch(r"RUN-[A-Z0-9]+-[0-9a-f]{6}", str(i)) for i in ids),
                  f"run ids {ids}")
    else:
        rep.diff("mode", f"unknown mode {mode}")
        return
    srcs = {f["path"]: f.get("sha256") for f in E["inputs"]["implementation_sources"]["files"]}
    vb, kb = E["input_bindings"]["vendor_curve_py"], E["input_bindings"]["known_answer_fixture"]
    pairs = [("sources vendor/curve.py", srcs.get("vendor/curve.py"), sha_files["vendor/curve.py"]),
             ("sources fixtures/kat.json", srcs.get("fixtures/kat.json"), sha_files["fixtures/kat.json"]),
             ("input_bindings vendor_curve_py", vb.get("sha256"), sha_files["vendor/curve.py"]),
             ("input_bindings known_answer_fixture", kb.get("sha256"), sha_files["fixtures/kat.json"])]
    for name, spec_sha, path in pairs:
        if spec_sha == "FILL_AT_FREEZE":
            if mode == "post-freeze":
                rep.diff(name, "still FILL_AT_FREEZE after the freeze")
            continue
        real = sha256_file(path) if os.path.exists(path) else None
        rep.eq(f"sha256 {name}", spec_sha, real)
    commit = vb.get("upstream_commit")
    if commit == "FILL_AT_FREEZE":
        if mode == "post-freeze":
            rep.diff("upstream_commit", "still FILL_AT_FREEZE after the freeze")
        return
    if not re.fullmatch(r"[0-9a-f]{40}", str(commit)):
        rep.diff("upstream_commit", f"not a 40-hex commit id: {commit!r}")
        return
    up_path = vb.get("upstream_path", "src/crypto_autoresearcher/index_calculus/curve.py")
    try:
        blob = subprocess.run(["git", "show", f"{commit}:{up_path}"], cwd=root, capture_output=True, check=True).stdout
        rep.eq("vendor/curve.py equals the upstream file at upstream_commit",
               hashlib.sha256(blob).hexdigest(), sha256_file(sha_files["vendor/curve.py"]))
    except (OSError, subprocess.CalledProcessError):
        rep.note("upstream_commit could not be resolved with git here; the sha256 binding was still checked")


def main(argv: list[str]) -> int:
    if argv and argv[0] == "spec-consistency":
        import argparse
        ap = argparse.ArgumentParser(prog="check.py spec-consistency")
        ap.add_argument("spec")
        ap.add_argument("--mode", choices=("pre-freeze", "post-freeze"), default="post-freeze")
        ap.add_argument("--impl-dir")
        a = ap.parse_args(argv[1:])
        ok, lines = spec_consistency(a.spec, a.mode, a.impl_dir)
        print("\n".join(lines))
        return 0 if ok else 1
    if len(argv) != 3:
        print("usage: check.py <run_dir> <trial-plan.json> <trial-id> | spec-consistency <specification.yaml>")
        return 2
    try:
        tid = check_trial(argv[0], argv[1], argv[2])
    except CheckFail as e:
        print("CHECK FAIL:", e)
        return 3
    except (OSError, KeyError, ValueError, TypeError, json.JSONDecodeError) as e:
        print(f"CHECK FAIL: unreadable or malformed input ({type(e).__name__}: {e})")
        return 3
    print("CHECK OK", tid)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
