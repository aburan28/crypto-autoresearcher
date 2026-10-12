"""Run driver for EXP-SDEG-85eefd protocol version 3 (one run covers all 9 fixtures).

NOT EXECUTED by the implementation task. Protocol v3 (AMD-20260928-7ce387)
splits one run across two hosts:

  --mode charged  (RunPod pod, Linux, no Sage; also works on the Mac)
      identity checks, decks, A5 oracle, B0, B1, B2, the no-Sage B2 split
      cross-check at L = 8, witness replay, rho. Up to 16 independent cell
      processes on Linux (1 elsewhere). Writes runs/<RUN-ID>/charged/.
  --mode sage     (repository Mac)
      fixture reproduction (C-1) and B2's literal FGLM cross-check at L = 8.
      Writes runs/<RUN-ID>/sage/.
  --mode merge    (repository Mac, after both parts are present)
      consistency checks across the parts, accounting audit summary, C-6
      metrics and the C-7 outcome mapping, with per-cell host provenance.
      Writes runs/<RUN-ID>/{manifest.yaml, raw-result.json, metrics.json,
      audit.json, cell_provenance.json}.
  --mode full     charged + sage + merge on one host (needs Sage).

charged and sage refuse to start unless
  * the host-aware C-9 precondition holds (hostinfo.py),
  * --admission-decision names an existing ledger/decisions/<DEC>.yaml that
    mentions EXP-SDEG-85eefd,
  * the trial plan's protocol hashes match the files on disk, and
  * their part directory does not exist yet (run records are immutable).

Usage:
  python3 driver.py --check-admission-only
  python3 driver.py --mode charged --run-id RUN-... --admission-decision DEC-... [--workers 16]
  python3 driver.py --mode sage    --run-id RUN-... --admission-decision DEC-...
  python3 driver.py --mode merge   --run-id RUN-... --admission-decision DEC-...
"""

from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import resource  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import hostinfo  # noqa: E402
from hostinfo import check_admission, parse_loadavg  # noqa: E402,F401

EXP_DIR = HERE.parent
REPO_ROOT_DEFAULT = EXP_DIR.parent.parent
PROTOCOL_VERSION = 4
ADMISSION_TARGET = "EXP-SDEG-85eefd"
MAX_WORKERS_LINUX = 16
MAX_WORKERS_OTHER = 1

EXIT_REFUSED_ADMISSION = 3
EXIT_REFUSED_DECISION = 4
EXIT_REFUSED_PLAN = 5
EXIT_REFUSED_EXISTS = 6
EXIT_PROCEDURE_DEFECT = 7
EXIT_INFRASTRUCTURE = 8
EXIT_REFUSED_HOST = 9


def admission_readings(repo_root: Path, run_volume: Path | None = None) -> dict:
    return hostinfo.admission_readings(repo_root, run_volume)


def check_decision(repo_root: Path, dec_id: str) -> tuple[bool, str]:
    """FX-1 (AMD-20260928-d3ed9e): admit only the explicitly named decision,
    and only if it is a coordinator_decision whose id matches, whose
    target_ids include EXP-SDEG-85eefd, and whose
    execution_admission.currently_admitted is exactly true."""
    import yaml
    if not dec_id or not re.fullmatch(r"DEC-\d{8}-[0-9a-f]{6}", dec_id):
        return False, f"invalid decision id {dec_id!r}"
    path = repo_root / "ledger" / "decisions" / f"{dec_id}.yaml"
    if not path.exists():
        return False, f"{path} does not exist"
    try:
        doc = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        return False, f"{path} does not parse: {e}"
    dec = doc.get("coordinator_decision") if isinstance(doc, dict) else None
    if not isinstance(dec, dict):
        return False, f"{path} has no coordinator_decision mapping"
    if dec.get("id") != dec_id:
        return False, f"{path} id {dec.get('id')!r} != {dec_id}"
    if ADMISSION_TARGET not in (dec.get("target_ids") or []):
        return False, f"{path} target_ids do not include {ADMISSION_TARGET}"
    adm = dec.get("execution_admission")
    if not isinstance(adm, dict) or adm.get("currently_admitted") is not True:
        return False, (f"{path} execution_admission.currently_admitted is "
                       f"{(adm or {}).get('currently_admitted') if isinstance(adm, dict) else adm!r}, not true")
    return True, str(path)


def check_plan(plan: dict) -> tuple[bool, list]:
    import fixtures
    want = {"specification_sha256": fixtures.sha256_file(fixtures.SPECIFICATION),
            "amendment_sha256": fixtures.sha256_file(fixtures.AMENDMENT),
            "amendment_v3_sha256": fixtures.sha256_file(fixtures.AMENDMENT_V3),
            "amendment_v4_sha256": fixtures.sha256_file(fixtures.AMENDMENT_V4),
            "fixtures_sha256": fixtures.sha256_file(fixtures.FIXTURE_JSON),
            "fixture_generator_sha256": fixtures.sha256_file(fixtures.FIXTURE_GEN)}
    bad = [k for k, v in want.items() if plan["protocol"].get(k) != v]
    if plan.get("protocol_version") != PROTOCOL_VERSION:
        bad.append(f"plan protocol_version {plan.get('protocol_version')} != {PROTOCOL_VERSION}")
    if fixtures.sha256_file(fixtures.FIXTURE_JSON) != fixtures.FROZEN_JSON_SHA256:
        bad.append("frozen fixture JSON hash differs from AMD-20260926-3479cf")
    return not bad, bad


# ------------------------------------------------------------------ provenance
class Tee:
    def __init__(self, stream, path):
        self.stream, self.fh = stream, open(path, "a", buffering=1)

    def write(self, s):
        self.stream.write(s)
        self.fh.write(s)

    def flush(self):
        self.stream.flush()
        self.fh.flush()


def git_state(repo_root: Path) -> dict:
    def g(*a):
        r = subprocess.run(["git", "-C", str(repo_root), *a], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    status = g("status", "--porcelain")
    return {"commit": g("rev-parse", "HEAD"), "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": None if status is None else bool(status),
            "status_porcelain": (status or "").splitlines()[:200],
            "is_git_checkout": status is not None}


def implementation_hashes() -> dict:
    import fixtures
    impl = {p.name: fixtures.sha256_file(p) for p in sorted(HERE.glob("*.py"))}
    impl["semaev_polys.json"] = fixtures.sha256_file(HERE / "semaev_polys.json")
    return impl


def sage_version() -> str | None:
    import fixtures
    if not Path(fixtures.SAGE).exists():
        return None
    return subprocess.run([fixtures.SAGE, "--version"], capture_output=True, text=True).stdout.strip()


def _env_bool(name):
    v = os.environ.get(name)
    if v is None or not v.strip():
        return None
    return v.strip().lower() in ("1", "true", "yes", "on")


def _env_list(name):
    v = os.environ.get(name)
    if v is None:
        return None
    v = v.strip()
    if not v:
        return []
    try:
        out = json.loads(v)
        if isinstance(out, list):
            return [str(x) for x in out]
    except ValueError:
        pass
    return [x.strip() for x in v.split(",") if x.strip()]


def inference_block() -> dict:
    """FX-5: inference provenance from the launch environment only. Unset
    variables stay null (resolved model 'unverified'); nothing is filled in."""
    env = os.environ.get
    model = env("AUTORESEARCH_RESOLVED_MODEL_ID") or env("AUTORESEARCH_MODEL_ID")
    return {"requested_policy": env("AUTORESEARCH_REQUESTED_POLICY") or env("AUTORESEARCH_POLICY") or None,
            "backend": env("AUTORESEARCH_BACKEND") or None,
            "runtime": env("AUTORESEARCH_RUNTIME") or None,
            "resolved_model_id": model or "unverified",
            "model_verified": _env_bool("AUTORESEARCH_MODEL_VERIFIED") is True,
            "reasoning_effort": env("AUTORESEARCH_REASONING_EFFORT") or None,
            "fallback_allowed": _env_bool("AUTORESEARCH_FALLBACK_ALLOWED"),
            "fallback_used": _env_bool("AUTORESEARCH_FALLBACK_USED"),
            "fallback_reason": env("AUTORESEARCH_FALLBACK_REASON") or None,
            "degraded_allowed": _env_bool("AUTORESEARCH_DEGRADED_ALLOWED"),
            "degraded_requirements": _env_list("AUTORESEARCH_DEGRADED_REQUIREMENTS"),
            "independent_session": _env_bool("AUTORESEARCH_INDEPENDENT_SESSION"),
            "source": "AUTORESEARCH_* environment variables at launch; unset -> null / 'unverified'"}


INFERENCE_KEYS = ("requested_policy", "resolved_model_id", "reasoning_effort", "fallback_used",
                  "degraded_requirements")


def environment(with_sage: bool) -> dict:
    return {"host": hostinfo.host_identity(sage_version() if with_sage else None),
            "implementation_sha256": implementation_hashes(),
            "inference": inference_block()}


def peak_rss_bytes() -> int:
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r if sys.platform == "darwin" else r * 1024


def children_peak_rss_bytes() -> int:
    r = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    return r if sys.platform == "darwin" else r * 1024


def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class Part:
    """One host's part of a run: its own manifest, command, environment and logs."""

    def __init__(self, args, part_dir: Path, mode: str, readings, decision_path, plan, dry, with_sage):
        import yaml
        self.yaml = yaml
        self.dir = part_dir
        self.dir.mkdir(parents=True)
        self.t0 = time.time()
        self._out, self._err = sys.stdout, sys.stderr
        sys.stdout = Tee(sys.__stdout__, part_dir / "stdout.log")
        sys.stderr = Tee(sys.__stderr__, part_dir / "stderr.log")
        (part_dir / "command.txt").write_text(" ".join([sys.executable] + sys.argv) + "\n")
        self.env = environment(with_sage)
        (part_dir / "environment.json").write_text(json.dumps(self.env, indent=1))
        import fixtures
        self.manifest = {
            "run_id": args.run_id, "experiment_id": "EXP-SDEG-85eefd",
            "protocol_version": PROTOCOL_VERSION, "part": mode,
            "admission_decision": args.admission_decision, "admission_decision_path": decision_path,
            "protocol": plan["protocol"], "trial_plan_sha256": fixtures.sha256_file(args.plan),
            "git": git_state(Path(args.repo_root)), "source_commit_declared": args.source_commit,
            "host": self.env["host"], "admission_readings_C9": readings,
            "implementation_sha256": self.env["implementation_sha256"],
            "seeds": {"namespace": None, "label_rules": "see labels.py and trial plan"},
            "started_at": _now(), "status": "running", "validity": None,
            "inference": self.env["inference"],
            **{k: self.env["inference"][k] for k in INFERENCE_KEYS},
            "smoke_dry_run": dry,
        }
        self.write()

    def write(self):
        self.manifest["peak_rss_bytes"] = peak_rss_bytes()
        self.manifest["children_peak_rss_bytes"] = children_peak_rss_bytes()
        self.manifest["wall_seconds"] = round(time.time() - self.t0, 3)
        (self.dir / "manifest.yaml").write_text(self.yaml.safe_dump(self.manifest, sort_keys=False))

    def finish(self, status, reason, code=0):
        self.manifest["status"] = status
        self.manifest["validity"] = {"status": status, "reason": reason}
        self.manifest["ended_at"] = _now()
        self.write()
        if code:
            print(f"STOP [{status}]: {reason}", file=sys.stderr)
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stdout, sys.stderr = self._out, self._err
        return code


def _selection(plan, dry):
    import decks as decks_mod
    import labels
    ns = labels.SMOKE_NS if dry else labels.FROZEN_NS
    n_pl = dry["per_deck"] // 2 if dry else decks_mod.N_PLANTED
    n_rd = dry["per_deck"] - n_pl if dry else decks_mod.N_RANDOM
    cells = [c for c in plan["cells"] if not dry or c["fixture"] in dry["fixtures"]]
    rhos = [r for r in plan["rho"] if not dry or r["fixture"] in dry["fixtures"]]
    return ns, n_pl, n_rd, cells, rhos


# ------------------------------------------------------------------ charged part
def _schedule(specs, workers, on_result, stop_flag):
    """Run task specs with at most `workers` processes, each task in its own
    fresh process. No new task starts
    once stop_flag() is true. Results are handed to on_result as they arrive;
    callers sort before aggregating, so outputs do not depend on the order."""
    import celltask
    import multiprocessing as mp
    from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
    ctx = mp.get_context("spawn")
    pending = list(specs)
    # FX-4: one fresh spawn process per task (max_tasks_per_child=1), also
    # when workers == 1, so a task's ru_maxrss is that task's own peak RSS.
    with ProcessPoolExecutor(max_workers=workers, mp_context=ctx, max_tasks_per_child=1) as ex:
        running = {}
        while pending or running:
            while pending and len(running) < workers and not stop_flag():
                s = pending.pop(0)
                running[ex.submit(celltask.run_task, s)] = s
            if not running:
                break
            done, _ = wait(list(running), return_when=FIRST_COMPLETED)
            for f in done:
                s = running.pop(f)
                try:
                    res = f.result()
                except Exception as e:  # noqa: BLE001  (worker died, e.g. OOM kill)
                    res = {"kind": s["kind"], "error": "worker_failure", "detail": f"{type(e).__name__}: {e}"}
                on_result(s, res)


def _cell_cost_key(c):
    return (-c["L"], c["fixture"], c["deck"])  # heaviest first: better packing, same results


def run_charged(args, readings, decision_path, plan, dry) -> int:
    import audit
    import cellrun
    ns, n_pl, n_rd, cells, rhos = _selection(plan, dry)
    part = Part(args, Path(args.runs_dir) / args.run_id / "charged", "charged", readings,
                decision_path, plan, dry, with_sage=False)
    part.manifest["seeds"]["namespace"] = ns
    part.manifest["workers"] = args.workers
    part.manifest["memory_limit_bytes_per_process"] = 8 * 2 ** 30
    part.manifest["certificate"] = {"kind": "witness_replay_and_A5_oracle"}
    for sub in ("identity", "cells", "rho"):
        (part.dir / sub).mkdir()
    part.write()

    all_ids = [q["query_id"] for c in plan["cells"] for q in c["queries"]]
    audit_ids = sorted(audit.select(all_ids, ns)) if not dry else None
    fixtures_sel = sorted({(c["L"], c["seed"], c["fixture"]) for c in cells})

    # phase 1: identity checks (C-3) -- any failure stops the run
    ident_specs = [{"kind": "identity", "task_id": f"identity-{fid}", "L": L, "seed": s, "ns": ns,
                    "n_tuples": 1000, "out": str(part.dir / "identity" / f"{fid}.json")}
                   for L, s, fid in fixtures_sel]
    ident_res = {}
    _schedule(ident_specs, args.workers, lambda s, r: ident_res.__setitem__(s["task_id"], r), lambda: False)
    part.manifest["identity_checks"] = {k: ident_res[k] for k in sorted(ident_res)}
    part.write()
    bad = [k for k, r in ident_res.items() if r.get("error") or not r.get("passed")]
    if bad:
        errs = [k for k in bad if ident_res[k].get("error")]
        if errs:
            return part.finish("failed_infrastructure", f"identity task errors: {errs}", EXIT_INFRASTRUCTURE)
        return part.finish("procedure_defect", f"S3/S4/S5 identity failure (C-3): {bad}", EXIT_PROCEDURE_DEFECT)

    # phase 2: cells and rho, in parallel
    specs = []
    for c in sorted(cells, key=_cell_cost_key):
        ids = [q["query_id"] for q in c["queries"]]
        specs.append({"kind": "cell", "task_id": c["cell_id"], "L": c["L"], "seed": c["seed"],
                      "deck": c["deck"], "ns": ns, "n_planted": n_pl, "n_random": n_rd,
                      "audit_ids": [] if audit_ids is None else [i for i in ids if i in set(audit_ids)],
                      "watchdog_s": args.watchdog_seconds,
                      "out": str(part.dir / "cells" / f"{c['cell_id']}.json")})
        if dry:  # smoke: audit every query (op logs kept in memory, receipts checked)
            specs[-1]["audit_ids"] = [f"L{c['L']}-s{c['seed']}-{c['deck']}-{k}-{j:02d}"
                                      for k, n in (("planted", n_pl), ("random", n_rd)) for j in range(n)]
    for r in rhos:
        specs.append({"kind": "rho", "task_id": f"rho-{r['fixture']}", "L": r["L"], "seed": r["seed"],
                      "ns": ns, "n_targets": dry["rho_targets"] if dry else r["n_targets"],
                      "out": str(part.dir / "rho" / f"{r['fixture']}.json")})
    results, stop_reason = {}, []

    def on_result(s, r):
        results[s["task_id"]] = r
        tag = r.get("error") or ("defects" if r.get("defects") else "ok")
        print(f"task {s['task_id']} done: {tag}", flush=True)
        if r.get("error"):
            stop_reason.append((s["task_id"], r["error"], r.get("detail")))
        elif r.get("defects"):
            stop_reason.append((s["task_id"], "procedure_defect", r["defects"][:3]))
        if args.after_cell_cmd and s["kind"] in ("cell", "rho"):
            env = dict(os.environ, SDEG_TASK=s["task_id"], SDEG_TASK_FILE=s["out"], SDEG_PART_DIR=str(part.dir))
            pr = subprocess.run(args.after_cell_cmd, shell=True, env=env, capture_output=True, text=True)
            print(f"after-cell hook {s['task_id']}: rc={pr.returncode}", flush=True)
        part.write()

    _schedule(specs, args.workers, on_result, lambda: bool(stop_reason))

    cell_res = [results[k] for k in sorted(results) if results[k].get("kind") == "cell" and not results[k].get("error")]
    rho_res = [results[k] for k in sorted(results) if results[k].get("kind") == "rho" and not results[k].get("error")]
    records = sorted((rec for c in cell_res for rec in c["records"]),
                     key=lambda x: (x["query_id"], x["backend"]))
    opcounts = sorted((row for c in cell_res for row in c["opcounts"]), key=lambda x: (x["query_id"], x["backend"]))
    ob = cellrun.canonical_opcounts_bytes(opcounts)
    (part.dir / "opcounts.json").write_bytes(ob)
    receipts = sorted((a for c in cell_res for a in c["audit_receipts"]),
                      key=lambda a: (a.get("query_id", ""), a.get("backend", "")))
    n_scored = sum(c["n_scored"] for c in cell_res)
    n_agree = sum(c["n_agree"] for c in cell_res)
    b2 = sorted((q for c in cell_res for q in c["b2"]), key=lambda x: x["query_id"])
    summary = {
        "run_id": args.run_id, "part": "charged", "namespace": ns,
        "host": part.env["host"], "implementation_sha256": part.env["implementation_sha256"],
        "cells": {c["cell_id"]: {k: c[k] for k in ("fixture", "L", "deck", "n_queries", "defects",
                                                   "stopped_on_defect", "n_scored", "n_agree",
                                                   "witnesses_verified", "witnesses_checked",
                                                   "b2_split_checked", "b2_split_mismatches", "seconds",
                                                   "pid", "peak_rss_bytes")}
                  for c in cell_res},
        "task_errors": {k: v for k, v in sorted(results.items()) if v.get("error")},
        "tasks_not_started": sorted(s["task_id"] for s in specs if s["task_id"] not in results),
        "records": records, "b2": b2, "rho": rho_res,
        "oracle_agreement": (n_agree / n_scored) if n_scored else 0.0, "n_scored": n_scored,
        "witnesses_verified": all(c["witnesses_verified"] for c in cell_res),
        "accounting_audit": {"n": len(receipts), "accepted": sum(1 for a in receipts if a["accepted"])},
        "b2_split": {"n_checked_cells": sum(1 for c in cell_res if c["b2_split_checked"]),
                     "mismatches": sorted(m for c in cell_res for m in c["b2_split_mismatches"])},
        "opcounts_sha256": _sha_bytes(ob),
        "sage_imported": "sage" in sys.modules or any(m.startswith("sage.") for m in sys.modules),
    }
    (part.dir / "audit.json").write_text(json.dumps(receipts))
    (part.dir / "charged-result.json").write_text(json.dumps(summary, default=str, sort_keys=True))
    part.manifest["opcounts_sha256"] = summary["opcounts_sha256"]
    part.manifest["summary"] = {k: summary[k] for k in ("oracle_agreement", "n_scored", "witnesses_verified",
                                                         "accounting_audit", "b2_split", "tasks_not_started",
                                                         "sage_imported")}
    if summary["task_errors"]:
        kinds = {v["error"] for v in summary["task_errors"].values()}
        st = "resource_exhaustion" if kinds == {"resource_exhaustion"} else "failed_infrastructure"
        return part.finish(st, f"task errors: {sorted(summary['task_errors'])}", EXIT_INFRASTRUCTURE)
    if any(c["defects"] for c in cell_res):
        return part.finish("procedure_defect", str(stop_reason[:3]), EXIT_PROCEDURE_DEFECT)
    return part.finish("completed", "charged part complete")


# ------------------------------------------------------------------ sage part
def fglm_selection(plan, dry, fglm_per_cell) -> dict:
    """Queries for the literal FGLM cross-check: every query of a |V| <= 4
    L = 8 cell and the first `fglm_per_cell` queries of every other L = 8 cell
    (OQ-5 ruling). Decks and targets are regenerated deterministically here
    (plain Python; no charged count is used)."""
    import decks as decks_mod
    import fixtures
    ns, n_pl, n_rd, cells, _ = _selection(plan, dry)
    out = {}
    for c in cells:
        if c["L"] != 8:
            continue
        fx = fixtures.fixture(c["L"], c["seed"])
        deck = decks_mod.build_all(fx, ns)[c["deck"]]
        qs = decks_mod.targets(fx, deck, ns, n_pl, n_rd)
        take = qs if deck.size <= 4 else qs[:fglm_per_cell]
        e = out.setdefault(c["fixture"], {"p": fx["p"], "a": fx["a"], "b": fx["b"], "queries": []})
        for qd in take:
            e["queries"].append({"query_id": qd["query_id"], "deck": c["deck"], "V": deck.V,
                                 "xR": None if qd["R"] is None else qd["R"][0], "methods": ["fglm"]})
    return out


def run_sage(args, readings, decision_path, plan, dry) -> int:
    import fixtures
    import semaev
    if not Path(fixtures.SAGE).exists():
        print(f"REFUSED: sage mode needs {fixtures.SAGE}", file=sys.stderr)
        return EXIT_REFUSED_HOST
    ns = _selection(plan, dry)[0]
    part = Part(args, Path(args.runs_dir) / args.run_id / "sage", "sage", readings, decision_path, plan,
                dry, with_sage=True)
    part.manifest["seeds"]["namespace"] = ns
    rep = fixtures.reproduce(part.dir / "fixture_reproduction.json")
    part.manifest["fixture_reproduction"] = rep
    part.write()
    if not rep["byte_identical"]:
        return part.finish("procedure_defect", "fixture reproduction mismatch (C-1)", EXIT_PROCEDURE_DEFECT)
    sel = fglm_selection(plan, dry, args.b2_fglm_per_cell)
    results = {}
    for fid in sorted(sel):
        inp = dict(sel[fid], semaev_file=str(semaev.POLY_FILE))
        ip, op = part.dir / f"b2_fglm_input_{fid}.json", part.dir / f"b2_fglm_output_{fid}.json"
        ip.write_text(json.dumps(inp))
        pr = subprocess.run([fixtures.SAGE, "-python", str(HERE / "sage_b2_crosscheck.py"), str(ip), str(op)],
                            capture_output=True, text=True)
        (part.dir / f"b2_fglm_{fid}.stdout").write_text(pr.stdout)
        (part.dir / f"b2_fglm_{fid}.stderr").write_text(pr.stderr)
        res = json.loads(op.read_text())["results"] if pr.returncode == 0 and op.exists() else []
        by = {r["query_id"]: r for r in res}
        for q in inp["queries"]:
            f = by.get(q["query_id"], {}).get("fglm", {})
            results[q["query_id"]] = {
                "fixture": fid, "deck": q["deck"], "V": q["V"], "xR": q["xR"], "returncode": pr.returncode,
                "radical_degree": f.get("radical_degree"), "eliminant_degree": f.get("eliminant_degree"),
                "roots_sha256": _sha_bytes(",".join(map(str, f["roots"])).encode()) if "roots" in f else None,
                "error": f.get("error") if f else "no result", "seconds": f.get("seconds")}
        part.write()
    summary = {"run_id": args.run_id, "part": "sage", "namespace": ns, "host": part.env["host"],
               "implementation_sha256": part.env["implementation_sha256"],
               "fixture_reproduction": rep, "fglm": dict(sorted(results.items())),
               "fglm_per_cell": args.b2_fglm_per_cell}
    (part.dir / "sage-result.json").write_text(json.dumps(summary, default=str, sort_keys=True))
    errs = [k for k, v in results.items() if v["radical_degree"] is None]
    if errs:
        return part.finish("failed_infrastructure", f"FGLM errors on {errs[:5]}", EXIT_INFRASTRUCTURE)
    return part.finish("completed", "sage part complete")


# ------------------------------------------------------------------ merge
def merge(args, plan, dry) -> int:
    import yaml

    import analysis
    import fixtures
    run_dir = Path(args.runs_dir) / args.run_id
    if (run_dir / "manifest.yaml").exists():
        print("REFUSED: merged manifest exists (run records are immutable)", file=sys.stderr)
        return EXIT_REFUSED_EXISTS
    paths = {k: run_dir / k / f"{k}-result.json" for k in ("charged", "sage")}
    missing = [k for k, p in paths.items() if not p.exists()]
    if missing:
        print(f"REFUSED: merge needs completed parts; missing {missing}", file=sys.stderr)
        return EXIT_REFUSED_EXISTS
    ch = json.loads(paths["charged"].read_text())
    sg = json.loads(paths["sage"].read_text())
    mans = {k: yaml.safe_load((run_dir / k / "manifest.yaml").read_text()) for k in ("charged", "sage")}
    problems = []
    for k, m in mans.items():
        if m.get("status") != "completed":
            problems.append(f"{k} part status {m.get('status')}")
        if m.get("run_id") != args.run_id:
            problems.append(f"{k} part run_id {m.get('run_id')}")
    if mans["charged"].get("trial_plan_sha256") != mans["sage"].get("trial_plan_sha256"):
        problems.append("trial plan differs between parts")
    if mans["charged"].get("admission_decision") != mans["sage"].get("admission_decision"):
        problems.append("admission decision differs between parts")
    if ch["namespace"] != sg["namespace"]:
        problems.append("label namespace differs between parts")
    impl_diff = sorted(k for k in set(ch["implementation_sha256"]) | set(sg["implementation_sha256"])
                       if ch["implementation_sha256"].get(k) != sg["implementation_sha256"].get(k))
    if impl_diff:
        problems.append(f"implementation differs between hosts: {impl_diff}")
    if ch.get("sage_imported"):
        problems.append("sage was imported in the charged process")
    b2 = {q["query_id"]: q for q in ch["b2"]}
    fglm_cmp = []
    for qid, f in sorted(sg["fglm"].items()):
        c = b2.get(qid)
        row = {"query_id": qid, "sage_radical_degree": f["radical_degree"],
               "b2_degree": c and c["elim_degree"], "V_equal": bool(c) and c["V"] == f["V"],
               "xR_equal": bool(c) and c["xR"] == f["xR"],
               "degree_match": bool(c) and c["elim_degree"] == f["radical_degree"],
               "root_set_match": bool(c) and c["roots_sha256"] == f["roots_sha256"]}
        fglm_cmp.append(row)
    fglm_ok = all(r["degree_match"] and r["root_set_match"] and r["V_equal"] and r["xR_equal"] for r in fglm_cmp)
    split_ok = not ch["b2_split"]["mismatches"]
    audit_ok = ch["accounting_audit"]["n"] > 0 and ch["accounting_audit"]["accepted"] == ch["accounting_audit"]["n"]
    repro_ok = bool(sg["fixture_reproduction"]["byte_identical"])
    metrics = analysis.compute_metrics(ch["records"])
    oc = analysis.outcome(metrics, ch["oracle_agreement"], ch["witnesses_verified"])
    cells_dir = run_dir / "charged" / "cells"
    provenance = {
        "charged_host": ch["host"], "sage_host": sg["host"],
        "cells": {cid: {"host": ch["host"]["hostname"], "container_id": ch["host"].get("container_id"),
                        "part": "charged", "pid": c["pid"],
                        "file_sha256": fixtures.sha256_file(cells_dir / f"{cid}.json")
                        if (cells_dir / f"{cid}.json").exists() else None}
                  for cid, c in sorted(ch["cells"].items())},
        "fglm_checks": {qid: {"host": sg["host"]["hostname"], "part": "sage"} for qid in sorted(sg["fglm"])},
        "fixture_reproduction": {"host": sg["host"]["hostname"], "part": "sage"},
    }
    (run_dir / "cell_provenance.json").write_text(json.dumps(provenance, indent=1, sort_keys=True))
    (run_dir / "metrics.json").write_text(json.dumps({"metrics": metrics, "outcome_mapping_C7": oc}, default=str))
    raw = {"records": ch["records"], "rho": ch["rho"], "oracle_agreement": ch["oracle_agreement"],
           "n_scored": ch["n_scored"], "witnesses_verified": ch["witnesses_verified"],
           "accounting_audit": ch["accounting_audit"], "b2_split": ch["b2_split"],
           "b2_fglm_crosscheck": fglm_cmp, "fixture_reproduction": sg["fixture_reproduction"],
           "opcounts_sha256": ch["opcounts_sha256"], "outcome_mapping_C7": oc,
           "merge_problems": problems}
    (run_dir / "raw-result.json").write_text(json.dumps(raw, default=str))
    (run_dir / "audit.json").write_text((run_dir / "charged" / "audit.json").read_text())
    if problems or not repro_ok:
        status, reason = "invalid_measurement", problems + ([] if repro_ok else ["fixture reproduction"])
    elif not audit_ok or not split_ok or not fglm_ok:
        status, reason = "invalid_measurement", (f"accounting audit ok={audit_ok}; B2 split ok={split_ok}; "
                                                 f"B2 FGLM ok={fglm_ok}")
    else:
        status = "completed_valid" if oc["outcome"] != "procedure_defect" else "procedure_defect"
        reason = oc["procedure_defects"]
    manifest = {
        "run_id": args.run_id, "experiment_id": "EXP-SDEG-85eefd", "protocol_version": PROTOCOL_VERSION,
        "admission_decision": mans["charged"].get("admission_decision"),
        "parts": {k: {"dir": k, "status": m.get("status"), "host": m.get("host"),
                      "started_at": m.get("started_at"), "ended_at": m.get("ended_at"),
                      "wall_seconds": m.get("wall_seconds"), "git": m.get("git"),
                      "source_commit_declared": m.get("source_commit_declared"),
                      "admission_readings_C9": m.get("admission_readings_C9"),
                      "manifest_sha256": fixtures.sha256_file(run_dir / k / "manifest.yaml")}
                  for k, m in mans.items()},
        "merge_host": hostinfo.host_identity(None), "merged_at": _now(),
        "merge_git": git_state(Path(args.repo_root)),
        "trial_plan_sha256": mans["charged"].get("trial_plan_sha256"), "protocol": plan["protocol"],
        "opcounts_sha256": ch["opcounts_sha256"], "smoke_dry_run": dry,
        "certificate": {"kind": "witness_replay_and_A5_oracle"},
        "status": "completed", "validity": {"status": status, "reason": reason},
        "outcome_C7": oc["outcome"], "inference": inference_block(),
        "parts_inference": {k: m.get("inference") for k, m in mans.items()},
    }
    manifest.update({k: manifest["inference"][k] for k in INFERENCE_KEYS})
    (run_dir / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))
    print(json.dumps({"validity": manifest["validity"], "outcome_C7": oc["outcome"],
                      "fglm_checks": len(fglm_cmp), "fglm_ok": fglm_ok}, default=str))
    return 0


# ------------------------------------------------------------------ main
def _max_workers() -> int:
    return MAX_WORKERS_LINUX if hostinfo.host_kind() == "linux" else MAX_WORKERS_OTHER


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("charged", "sage", "merge", "full"), default="full")
    ap.add_argument("--run-id")
    ap.add_argument("--admission-decision")
    ap.add_argument("--plan", default=str(HERE / "trial-plan-v2.json"))
    ap.add_argument("--repo-root", default=str(REPO_ROOT_DEFAULT))
    ap.add_argument("--runs-dir", default=str(EXP_DIR / "runs"))
    ap.add_argument("--workers", type=int, default=1,
                    help=f"independent cell processes (charged part): <= {MAX_WORKERS_LINUX} on Linux, 1 elsewhere")
    ap.add_argument("--source-commit", default=None,
                    help="repository commit the implementation was synced from (hosts without a git checkout)")
    ap.add_argument("--after-cell-cmd", default=None,
                    help="shell command run after each cell/rho task (env SDEG_TASK, SDEG_TASK_FILE, "
                         "SDEG_PART_DIR), e.g. a copy-back; failures are logged, never fatal")
    ap.add_argument("--watchdog-seconds", type=int, default=3600)
    ap.add_argument("--b2-fglm-per-cell", type=int, default=1,
                    help="literal FGLM on the first N queries of each L=8 cell with |V|>4 (all when |V|<=4)")
    ap.add_argument("--check-admission-only", action="store_true")
    ap.add_argument("--smoke-dry-run", action="store_true",
                    help="implementation check only: smoke namespace, L8-s1, few queries, output confined "
                         "to implementation/smoke/; admission readings recorded but not enforced")
    ap.add_argument("--dry-per-deck", type=int, default=4)
    ap.add_argument("--dry-rho-targets", type=int, default=2)
    args = ap.parse_args(argv)
    repo_root = Path(args.repo_root)
    readings = admission_readings(repo_root, Path(args.runs_dir))
    ok, reasons = check_admission(readings)
    if not 1 <= args.workers <= _max_workers():
        print(f"REFUSED: --workers {args.workers} outside 1..{_max_workers()} on {hostinfo.host_kind()}",
              file=sys.stderr)
        return EXIT_REFUSED_HOST
    if args.mode == "sage" and args.workers != 1:
        print("REFUSED: sage part runs with one worker", file=sys.stderr)
        return EXIT_REFUSED_HOST
    dry = None
    if args.smoke_dry_run:
        smoke_root = (HERE / "smoke").resolve()
        runs = Path(args.runs_dir).resolve()
        if smoke_root not in runs.parents and runs != smoke_root:
            print("REFUSED: --smoke-dry-run output must be under implementation/smoke/", file=sys.stderr)
            return EXIT_REFUSED_PLAN
        if not args.run_id or not args.run_id.startswith("DRYRUN-"):
            print("REFUSED: --smoke-dry-run needs --run-id DRYRUN-...", file=sys.stderr)
            return EXIT_REFUSED_EXISTS
        dry = {"fixtures": ["L8-s1"], "per_deck": args.dry_per_deck, "rho_targets": args.dry_rho_targets,
               "admission_readings_not_enforced": {"ok": ok, "reasons": reasons}}
        decision_path = "smoke-dry-run (no admission decision)"
    else:
        print(json.dumps({"admission_readings_C9": readings, "admitted_by_precondition": ok,
                          "reasons": reasons}, indent=1))
        if args.mode != "merge" and not ok:
            print("REFUSED: C-9 machine-protection precondition not met", file=sys.stderr)
            return EXIT_REFUSED_ADMISSION
        if args.check_admission_only:
            return 0
        if not args.run_id or not re.fullmatch(r"RUN-[A-Za-z0-9._-]+", args.run_id):
            print("REFUSED: --run-id RUN-... required", file=sys.stderr)
            return EXIT_REFUSED_DECISION
        dok, decision_path = check_decision(repo_root, args.admission_decision)
        if not dok:
            print(f"REFUSED: admission decision: {decision_path}", file=sys.stderr)
            return EXIT_REFUSED_DECISION
    plan = json.loads(Path(args.plan).read_text())
    if not dry:
        pok, bad = check_plan(plan)
        if not pok:
            print(f"REFUSED: trial plan hashes do not match protocol files: {bad}", file=sys.stderr)
            return EXIT_REFUSED_PLAN
    run_dir = Path(args.runs_dir) / args.run_id
    parts = {"charged": ["charged"], "sage": ["sage"], "merge": [], "full": ["charged", "sage"]}[args.mode]
    for p in parts:
        if (run_dir / p).exists():
            print(f"REFUSED: {run_dir / p} exists (run records are immutable)", file=sys.stderr)
            return EXIT_REFUSED_EXISTS
    if args.mode in ("merge",) or args.mode == "full":
        if (run_dir / "manifest.yaml").exists():
            print("REFUSED: merged manifest exists (run records are immutable)", file=sys.stderr)
            return EXIT_REFUSED_EXISTS
    if "charged" in parts:
        code = run_charged(args, readings, decision_path, plan, dry)
        if code:
            return code
    if "sage" in parts:
        code = run_sage(args, readings, decision_path, plan, dry)
        if code:
            return code
    if args.mode in ("merge", "full"):
        return merge(args, plan, dry)
    return 0


if __name__ == "__main__":
    sys.exit(main())
