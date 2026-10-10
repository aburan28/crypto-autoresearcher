#!/usr/bin/env python3
"""Harvest per-attempt point-decomposition costs into ctrial.csv (+ ctrial_targets.csv).

Read-only with respect to the repository.  Every row names its source record,
the repository path it was read from, and the commit that last touched that
path (git log -1).  Literature numbers are transcribed from the in-repo copy of
the paper (inputs/SATIC-TRIMOSKA-2019/paper_fulltext.md) with line numbers.
External n=131 numbers are read from files fetched by content (sha256 checked
against EV-ICPERF-10c5fc's external_provenance block).

Censored observations are kept and marked; nothing is imputed.

Usage:  python3 harvest.py /home/user/crypto-autoresearcher
"""
import csv, gzip, hashlib, json, math, os, statistics, subprocess, sys

REPO = sys.argv[1] if len(sys.argv) > 1 else "/home/user/crypto-autoresearcher"
HERE = os.path.dirname(os.path.abspath(__file__))
FORBIDDEN = ("experiments/EXP-FROB-30006a", "experiments/EXP-QSP-70b731/runs")

_commit_cache = {}


def commit_of(path):
    assert not any(path.startswith(f) for f in FORBIDDEN), path
    if path not in _commit_cache:
        try:
            out = subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%h", "--", path],
                                 capture_output=True, text=True, timeout=60).stdout.strip()
        except Exception:
            out = ""
        _commit_cache[path] = out or "unknown"
    return _commit_cache[path]


def rp(path):
    assert not any(path.startswith(f) for f in FORBIDDEN), path
    return os.path.join(REPO, path)


def jload(path):
    with open(rp(path)) as f:
        return json.load(f)


def jsonl(path):
    with open(rp(path)) as f:
        return [json.loads(l) for l in f if l.strip()]


COLS = ["row_id", "source_record", "run_id", "branch", "commit", "path", "tier",
        "n", "m", "t", "l", "representation", "solver", "solver_config", "solver_version",
        "host", "outcome", "label", "n_obs", "n_censored", "statistic",
        "wall_s", "wall_q1_s", "wall_q3_s", "wall_min_s", "wall_max_s",
        "conflicts", "conflicts_q1", "conflicts_q3", "field_ops",
        "censored", "censor_bound_s", "include_in_fit", "notes"]

ROWS = []
TARGETS = []  # per-target values for bootstrap: row_id, value_s, conflicts, censored


def q(vals, p):
    vals = sorted(vals)
    if not vals:
        return None
    k = (len(vals) - 1) * p
    f = math.floor(k); c = math.ceil(k)
    if f == c:
        return vals[int(k)]
    return vals[f] + (vals[c] - vals[f]) * (k - f)


def add(**kw):
    row = {c: "" for c in COLS}
    row.update({k: v for k, v in kw.items() if v is not None})
    row["row_id"] = "R%04d" % (len(ROWS) + 1)
    ROWS.append(row)
    return row["row_id"]


def add_group(vals, confs=None, censored_vals=None, **kw):
    """vals: list of finished wall seconds; censored_vals: list of bounds."""
    censored_vals = censored_vals or []
    n_obs = len(vals) + len(censored_vals)
    allv = list(vals) + list(censored_vals)
    med = q(allv, 0.5) if allv else None
    # median is censored if more than half of the observations are censored
    med_cens = len(censored_vals) * 2 > n_obs if n_obs else False
    rid = add(n_obs=n_obs, n_censored=len(censored_vals), statistic="median",
              wall_s=None if med is None else round(med, 6),
              wall_q1_s=None if not allv else round(q(allv, 0.25), 6),
              wall_q3_s=None if not allv else round(q(allv, 0.75), 6),
              wall_min_s=None if not allv else round(min(allv), 6),
              wall_max_s=None if not allv else round(max(allv), 6),
              conflicts=None if not confs else q(confs, 0.5),
              conflicts_q1=None if not confs else q(confs, 0.25),
              conflicts_q3=None if not confs else q(confs, 0.75),
              censored="yes" if med_cens else ("partial" if censored_vals else "no"),
              censor_bound_s=(max(censored_vals) if censored_vals else None), **kw)
    for v in vals:
        TARGETS.append((rid, v, None, 0))
    for v in censored_vals:
        TARGETS.append((rid, v, None, 1))
    return rid


# ---------------------------------------------------------------------------
# 1. EXP-ICPERF-66fd51: Trimoska's 60 shipped S_4 instances, six engines, two runs
# ---------------------------------------------------------------------------
def icperf_66fd51():
    cellmap = {"n15l5": (15, 5), "n17l6": (17, 6), "n19l6": (19, 6)}
    for run in ["RUN-ICPERF-305ca3", "RUN-ICPERF-4ec9b9"]:
        path = f"experiments/EXP-ICPERF-66fd51/runs/{run}/results.jsonl"
        rows = jsonl(path)
        groups = {}
        for r in rows:
            if r.get("engine") == "certificate" or r.get("cell") not in cellmap:
                continue
            st = r.get("status")
            if st in ("SAT", "UNSAT"):
                outcome = st
            elif st == "budget_stop_timeout":
                outcome = "censored"
            else:
                outcome = "infrastructure"
            null = r.get("config") == "default_on_null_object"
            key = (r["cell"], r["engine"], r["config"], outcome,
                   "null" if null else ("" if outcome in ("SAT", "UNSAT") else r.get("label")))
            groups.setdefault(key, []).append(r)
        for (cell, eng, cfg, outcome, lab), rs in sorted(groups.items()):
            n, l = cellmap[cell]
            vals, cens, confs = [], [], []
            degenerate = any(x["instance"] == "n15l5-8-S" for x in rs)
            for x in rs:
                c = x.get("conflicts")
                if c is None and isinstance(x.get("stats"), dict):
                    c = x["stats"].get("conflicts")
                if outcome == "censored":
                    cens.append(float(x.get("timeout_s") or x.get("wall_s")))
                elif outcome == "infrastructure":
                    continue
                else:
                    vals.append(float(x["wall_s"]))
                    if c is not None:
                        confs.append(int(c))
            if outcome == "infrastructure":
                add(source_record="EV-ICPERF-390707", run_id=run, branch="main", commit=commit_of(path),
                    path=path, tier="in_repo_run", n=n, m=3, t=1, l=l,
                    representation="S4 Weil descent (Trimoska ECICB-2024 shipped ANF/CNF/Magma)",
                    solver=eng, solver_config=cfg, host="Linux x86_64 4-CPU 15GB",
                    outcome="infrastructure", n_obs=len(rs), statistic="none", censored="n/a",
                    include_in_fit="no",
                    notes="RLIMIT_AS abort + .m2 parse error (EV-ICPERF-390707 O-3/O-4): no cost information")
                continue
            ver = {"wdsat": "WDSat (Trimoska 2024 src, rebuilt per sizing)", "cryptominisat5": "5.11.15",
                   "cadical": "1.7.3", "minisat": "2.2", "singular_std_GF2_fieldeqs": "4.3.2"}.get(eng, "")
            notes = []
            if null:
                notes.append("NULL OBJECT (shape-matched random system), not a decomposition attempt")
            if degenerate:
                notes.append("includes n15l5-8-S (degenerate, 32 roots; EV-ICPERF-390707 O-17a)")
            if outcome == "censored":
                notes.append("budget_stop_timeout: right-censored at timeout_s; label=%s" % lab)
            if eng == "wdsat" and cfg == "noncore_first":
                notes.append("deliberately bad branching order (P3b control)")
            if eng == "wdsat" and cfg == "gauss_elim":
                notes.append("-x Gaussian elimination (P4: 4-7x slower)")
            if outcome == "SAT":
                notes.append("SAT includes 1 twist-side root on n19l6-19-U (O-1)" if cell == "n19l6" else "")
            fit = "yes" if (not null and eng in ("wdsat", "cryptominisat5", "cadical", "minisat")
                            and cfg in ("default", "symmetry", "core_order", "cnf_xor", "pure_cnf")) else "no"
            add_group(vals, confs, cens, source_record="EV-ICPERF-390707", run_id=run, branch="main",
                      commit=commit_of(path), path=path, tier="in_repo_run", n=n, m=3, t=1, l=l,
                      representation=("S4 Weil descent, ANF (WDSat)" if eng == "wdsat" else
                                      "S4 Weil descent, CNF-XOR" if cfg == "cnf_xor" else
                                      "S4 Weil descent, pure CNF" if cfg == "pure_cnf" else
                                      "S4 Weil descent, Boolean ideal + field eqs"),
                      solver=eng, solver_config=cfg, solver_version=ver,
                      host="Linux x86_64 4-CPU 15GB (cloud container)", outcome=outcome, label=lab,
                      include_in_fit=fit, notes="; ".join(x for x in notes if x))


# ---------------------------------------------------------------------------
# 2. EXP-ICPERF-e21835 (repaired instrument): Macaulay2 F4 completes at n15l5
# ---------------------------------------------------------------------------
def icperf_e21835():
    path = "experiments/EXP-ICPERF-e21835/runs/RUN-ICPERF-a4a24b/results_engine.jsonl"
    for r in jsonl(path):
        if r["engine"].startswith("macaulay2"):
            add_group([float(r["wall_s"])], None, None, source_record="EV-ICPERF-433fa5",
                      run_id="RUN-ICPERF-a4a24b", branch="main", commit=commit_of(path), path=path,
                      tier="in_repo_run", n=15, m=3, t=1, l=5,
                      representation="S4 Weil descent, Boolean ideal + field eqs",
                      solver="Macaulay2 F4 (ZZ/2, grevlex, field eqs)", solver_config="repaired harness",
                      solver_version="1.22", host="Linux x86_64 4-CPU 15GB (cloud container)",
                      outcome="SAT", label="S",
                      include_in_fit="yes",
                      notes="instance %s; engine_cpu_s=%.1f; peak RSS 6.6 GiB; threaded (cpu_s %.0f > wall)" %
                            (r["instance"], r.get("engine_cpu_s") or float("nan"), r.get("cpu_s") or 0))
    # SAT-solver rows of this run are excluded: 0.25 s watchdog poll floor (EV-ICPERF-433fa5 O-7)
    add(source_record="EV-ICPERF-390707", run_id="review TASK-20260915-195b0c (O-5)", branch="main",
        commit=commit_of("ledger/evidence/EV-ICPERF-390707.yaml"),
        path="ledger/evidence/EV-ICPERF-390707.yaml", tier="review_remeasurement",
        n=15, m=3, t=1, l=5, representation="S4 Weil descent, Boolean ideal + field eqs",
        solver="Singular slimgb", solver_config="same ring/options as harness std", solver_version="4.3.2",
        host="Linux x86_64 4-CPU (same host class)", outcome="SAT", label="S", n_obs=1, n_censored=0,
        statistic="single", wall_s=167.4, censored="no", include_in_fit="yes",
        notes="one n15l5 instance (not named in record; vdim=3, gb_size=43 => SAT side); std censored at 900 s on 4 instances")


# ---------------------------------------------------------------------------
# 3. EXP-ICPERF-783e9e: PolyBoRi ladder at m = 2, 3, 4 (one target per cell)
# ---------------------------------------------------------------------------
def icperf_783e9e():
    path = "experiments/EXP-ICPERF-783e9e/runs/RUN-ICPERF-2f36fd/raw-result.json"
    d = jload(path)["solver_ladder"]
    for m, v in d.items():
        for c in v["cells"]:
            if "skipped" in c:
                add(source_record="EV-ICPERF-784b25", run_id="RUN-ICPERF-2f36fd", branch="main",
                    commit=commit_of(path), path=path, tier="in_repo_run", n=c["n"], m=int(m), t=1,
                    l=c["l"], representation="S_{m+1} Weil descent, Boolean (BRiAl)", solver="PolyBoRi groebner_basis",
                    solver_version="Sage 10.9", host="Linux x86_64 4-CPU (cloud container)", outcome="not_run",
                    n_obs=0, statistic="none", censored="n/a", include_in_fit="no", notes=c["skipped"])
                continue
            for arm in ("sat", "random"):
                a = c[arm]
                if a.get("timed_out"):
                    outcome = "censored"
                    vals, cens = [], [float(a.get("wall_seconds") or a.get("timeout_seconds"))]
                else:
                    outcome = "UNSAT" if a.get("unsat") else "SAT"
                    vals, cens = [float(a["groebner_seconds"])], []
                add_group(vals, None, cens, source_record="EV-ICPERF-784b25", run_id="RUN-ICPERF-2f36fd",
                          branch="main", commit=commit_of(path), path=path, tier="in_repo_run",
                          n=c["n"], m=int(m), t=1, l=c["l"],
                          representation="S_{m+1} Weil descent, Boolean (BRiAl), nvars=m*l",
                          solver="PolyBoRi groebner_basis", solver_version="Sage 10.9",
                          host="Linux x86_64 4-CPU (cloud container)", outcome=outcome,
                          label=("planted" if arm == "sat" else "random_target"),
                          include_in_fit="yes",
                          notes=("build_s=%s; one target per cell; boolean degree %s" %
                                 (a.get("build_seconds"), a.get("boolean_degree"))) +
                                ("; 180 s cap, uncharacterised (not proven hard)" if outcome == "censored" else ""))


# ---------------------------------------------------------------------------
# 4. EXP-ICI-001: crossbred (t=3) and MITM (t=4) per-PDP costs, planted targets
# ---------------------------------------------------------------------------
def ici_001():
    for run, tag in (("RUN-EXP-ICI-001-a", "primary"), ("RUN-EXP-ICI-001-f", "same-seed replicate")):
        path = f"experiments/EXP-ICI-001/runs/{run}/raw.json"
        d = jload(path)
        byn = {}
        for c in d["cells"]:
            byn.setdefault((c["n"], c["k"]), []).append(c)
        for (n, k), cs in sorted(byn.items()):
            vals, cens = [], []
            for c in cs:
                for t in c["targets"]:
                    if t.get("status") == "ok" and t.get("best"):
                        vals.append(2.0 ** t["best"]["log2_total"])
                    else:
                        cens.append(float("nan"))
            cens = [x for x in cens if x == x]
            add_group(vals, None, cens, source_record="EV-ICI-001", run_id=run, branch="main",
                      commit=commit_of(path), path=path, tier="in_repo_run", n=n, m=3, t=3, l=k,
                      representation="chained S_3 (t=3) Weil descent, Boolean",
                      solver="crossbred (guess k_fix bits + Sage GB per guess)",
                      solver_config="cost = 2^k_fix * median per-guess GB s, min over k_fix",
                      solver_version="Sage (ICI_run.sage)", host="macOS 15.6 arm64 (Sage 10.9)",
                      outcome="SAT", label="planted",
                      include_in_fit=("yes" if tag == "primary" else "no"),
                      notes=tag + "; extrapolated FULL-enumeration cost (2^k_fix guesses) so it also prices an UNSAT attempt;"
                                  " 2/216 planted targets chain-inconsistent (O1)")
    path = "experiments/EXP-ICI-001/runs/RUN-EXP-ICI-001-c/raw.json"
    d = jload(path)
    byn = {}
    for c in d["cells"]:
        byn.setdefault((c["n"], c["k"]), []).append(c)
    for (n, k), cs in sorted(byn.items()):
        vals, cens, work = [], [], []
        ttypes = set()
        for c in cs:
            if c.get("status") == "censored_budget":
                cens.extend([float(d["config"]["cell_budget_s"])] * c.get("n_targets_planned", 8))
                continue
            for t in c["targets"]:
                ttypes.add(t.get("target_type", c.get("target_type", "planted")))
                if t.get("status") == "ok":
                    vals.append(float(t["wall_s"]))
                    work.append(t["log2_work"])
        add_group(vals, None, cens, source_record="EV-ICI-001", run_id="RUN-EXP-ICI-001-c", branch="main",
                  commit=commit_of(path), path=path, tier="in_repo_run", n=n, m=4, t=4, l=k,
                  representation="chained S_3 tree, t=4 meet-in-the-middle (two lists + quadratic junction)",
                  solver="MITM list-matching (combinatorial)", solver_version="Sage (ICI_run.sage)",
                  host="macOS 15.6 arm64 (Sage 10.9)", outcome="SAT", label="/".join(sorted(ttypes)),
                  field_ops=("2^%.1f work units" % statistics.median(work)) if work else None,
                  include_in_fit="yes",
                  notes="full enumeration: cost is target-independent (prices SAT and UNSAT alike); work=2^(2k+1) exactly")


# ---------------------------------------------------------------------------
# 5. EXP-ALBIN-* (autolab import): single planted targets, contended macOS host
# ---------------------------------------------------------------------------
def albin():
    host = "autolab macOS (CPU-contended per result md)"
    p7 = "experiments/EXP-ALBIN-007/runs/RUN-ALBIN-007-import/raw-result.json"
    # values transcribed from the archived result markdown table (byte-verified from the log by its author)
    for n, l, solve, st in [(11, 4, 0.02, "SAT"), (13, 4, 0.02, "SAT"), (17, 6, 30.3, "SAT"),
                            (19, 6, 33.3, "SAT"), (23, 8, 122.09, "censored")]:
        add_group([solve] if st == "SAT" else [], None, [solve] if st == "censored" else [],
                  source_record="EV-ALBIN-001 (EXP-ALBIN-007)", run_id="RUN-ALBIN-007-import", branch="main",
                  commit=commit_of(p7), path=p7, tier="in_repo_import", n=n, m=3, t=1, l=l,
                  representation="S4 Weil descent, CNF + native XOR, lex symmetry breaking",
                  solver="CryptoMiniSat (pycryptosat)", solver_version="pycryptosat (unpinned)", host=host,
                  outcome=st, label="planted", include_in_fit="yes",
                  notes="single target; solve seconds only (descent excluded)" +
                        ("; native time_limit 120 s => SOLVE_TIMEOUT (UNKNOWN)" if st == "censored" else ""))
    for n, l, why in [(29, 10, "descent 101.95 s hit outer cap before solve"), (31, 10, "descent 117.01 s hit outer cap before solve")]:
        add(source_record="EV-ALBIN-001 (EXP-ALBIN-007)", run_id="RUN-ALBIN-007-import", branch="main",
            commit=commit_of(p7), path=p7, tier="in_repo_import", n=n, m=3, t=1, l=l,
            representation="S4 Weil descent, CNF + native XOR", solver="CryptoMiniSat (pycryptosat)", host=host,
            outcome="not_reached", n_obs=1, statistic="none", censored="n/a (solver never started)",
            include_in_fit="no", notes=why)
    p4 = "experiments/EXP-ALBIN-004/runs/RUN-ALBIN-004-import/raw-result.json"
    for n, l, v, st in [(11, 4, 0.95, "SAT"), (13, 4, 1.46, "SAT"), (17, 6, 240.0, "censored"),
                        (19, 6, 240.0, "censored"), (23, 8, 240.0, "censored")]:
        add_group([v] if st == "SAT" else [], None, [v] if st == "censored" else [],
                  source_record="EV-ALBIN-001 (EXP-ALBIN-004)", run_id="RUN-ALBIN-004-import", branch="main",
                  commit=commit_of(p4), path=p4, tier="in_repo_import", n=n, m=3, t=1, l=l,
                  representation="S4 Weil descent, Boolean ideal (Sage)", solver="Sage Groebner (engine unnamed)",
                  host=host, outcome=st, label="planted", include_in_fit="yes",
                  notes="single target; 240 s hard cap per cell" if st == "censored" else "single target; solving degree 2")
    p9 = "experiments/EXP-ALBIN-009/runs/RUN-ALBIN-009-import/raw-result.json"
    for n, m, l, wall, desc, fin in [(11, 3, 4, 13.8, 0.72, True), (11, 4, 3, 25.8, 4.84, True), (17, 4, 4, 302.0, 148.84, False)]:
        v = wall - desc
        add_group([v] if fin else [], None, [] if fin else [v], source_record="EV-ALBIN-001 (EXP-ALBIN-009)",
                  run_id="RUN-ALBIN-009-import", branch="main", commit=commit_of(p9), path=p9,
                  tier="in_repo_import", n=n, m=m, t=1, l=l,
                  representation="S_{m+1} evaluation-descent (Mobius), Boolean", solver="msolve F4",
                  solver_version="0.9.5", host=host, outcome="SAT" if fin else "censored", label="planted",
                  include_in_fit="yes",
                  notes="wall minus descent; single target" + ("" if fin else "; msolve unfinished (matrix wall at degree 13)"))
    p10 = "experiments/EXP-ALBIN-010/runs/RUN-ALBIN-010-import/raw-result.json"
    add_group([], None, [537.9 - 236.1], source_record="EV-ALBIN-001 (EXP-ALBIN-010)", run_id="RUN-ALBIN-010-import",
              branch="main", commit=commit_of(p10), path=p10, tier="in_repo_import", n=15, m=5, t=1, l=3,
              representation="S_6 resultant evaluator + evaluation-descent", solver="msolve F4", solver_version="0.9.5",
              host=host, outcome="censored", label="planted", include_in_fit="no",
              notes="unfinished; nvars=15 < m(m-1)=20 so degree truncated (confounded cell)")


# ---------------------------------------------------------------------------
# 6. EXP-SEMBIN-c2c312 / -7e1371: msolve on Semaev-2015 chained S_3 systems
# ---------------------------------------------------------------------------
def sembin_msolve():
    seen = set()
    path = "experiments/EXP-SEMBIN-c2c312/runs/RUN-SEMBIN-b6eb9f/results-table.json"
    rows = jload(path)
    groups = {}
    for r in rows:
        if r.get("n") is None:
            continue
        st = r.get("f4_status")
        if st == "unreached_declared":
            continue
        seen.add(r.get("system_sha256"))
        if st == "completed":
            outcome = "SAT" if (r.get("quotient_dimension") or 0) > 0 else "UNSAT"
        else:
            outcome = "censored"
        key = (r["n"], r["m"], r["t"], r["k"], outcome, r.get("B_mode"), st)
        groups.setdefault(key, []).append(r)
    for (n, m, t, k, outcome, bm, st), rs in sorted(groups.items(), key=str):
        vals = [float(x["f4_wall_s"]) for x in rs if outcome != "censored"]
        cens = [float(x["f4_wall_s"]) for x in rs if outcome == "censored"]
        add_group(vals, None, cens, source_record="EV-SEMBIN-c6e9ad", run_id="RUN-SEMBIN-b6eb9f", branch="main",
                  commit=commit_of(path), path=path, tier="in_repo_run", n=n, m=m, t=t, l=k,
                  representation="Semaev-2015 chained S_3 (eq.5), Boolean, B_mode=%s" % bm,
                  solver="msolve F4", solver_version="msolve (pinned in run env)",
                  host="Linux x86_64 4-CPU 16GB (cloud container)", outcome=outcome, label=str(bm),
                  include_in_fit="yes" if t == m else "no",
                  notes=("status=%s; " % st) + ("SAT = quotient_dimension>0" if outcome != "censored" else "censored (cap)") +
                        ("" if t == m else "; t != m (window system), not a plain m-decomposition"))
    path = "experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-9bb990/results-table.json"
    rows = jload(path)
    for r in rows:
        if r.get("instrument") != "f4_trace_msolve" or r.get("status") == "unreached_declared":
            continue
        if r.get("family") != "chained_S3_eq5" or r["m"] == 2:
            continue
        if r.get("system_sha256") in seen:
            continue
        st = r.get("status")
        if st == "completed":
            outcome = "UNSAT" if r.get("ideal_is_unit") else "SAT"
            vals, cens = [float(r["wall_s"])], []
        else:
            outcome = "censored"
            vals, cens = [], [float(r["wall_s"])]
        add_group(vals, None, cens, source_record="EV-SEMBIN-702d1d", run_id="RUN-SEMBIN-9bb990", branch="main",
                  commit=commit_of(path), path=path, tier="in_repo_run", n=r["n"], m=r["m"], t=r.get("t"), l=r["k"],
                  representation="Semaev-2015 chained S_3 (eq.5), Boolean, B_mode=%s" % r.get("B_mode"),
                  solver="msolve F4", solver_version="msolve (run env)", host="Linux x86_64 4-CPU (cloud container)",
                  outcome=outcome, label=r.get("B_mode"), include_in_fit="yes",
                  notes="status=%s; instance %s" % (st, r.get("instance_id")))


# ---------------------------------------------------------------------------
# 7. EXP-CERTBIN m=2 degree-capped Macaulay per attempt (cell mean only)
# ---------------------------------------------------------------------------
def certbin():
    specs = [("experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/cell-summary.json", "EV-CERTBIN-6c3e0a",
              "RUN-CERTBIN-3b7e05", lambda d: [("", d["families"]["F-S3"])]),
             ("experiments/EXP-CERTBIN-3f06d1/runs/RUN-CERTBIN-6d92b5/cell-summary.json", "EXP-CERTBIN-3f06d1 (no EV on main)",
              "RUN-CERTBIN-6d92b5", lambda d: [(c, d["cells"][c]["families"]["F-S3"]) for c in sorted(d["cells"])])]
    for path, ev, run, sel in specs:
        d = jload(path)
        for cname, fam in sel(d):
            for D in ("D3", "D4"):
                x = fam[D]
                per = x["wall_seconds"] / x["N_targets"]
                add(source_record=ev, run_id=run, branch="main", commit=commit_of(path), path=path,
                    tier="in_repo_run", n=17, m=2, t=1, l=9, representation="S_3 Weil descent (regime A, field eqs)",
                    solver="Macaulay matrix rank, degree %s (M4RI)" % D, solver_config=("curve " + cname).strip(),
                    host="Linux x86_64 4-CPU 16GB", outcome="MIXED",
                    label="unsat %d / sat %d" % (x["arm_sizes"]["unsat"], x["arm_sizes"]["sat"]),
                    n_obs=x["N_targets"], n_censored=0, statistic="mean (cell wall / N_targets)",
                    wall_s=round(per, 6), censored="no", include_in_fit="no",
                    notes="m=2 only; capped-degree rank, not a full solve (M_4 leaves ~16% of UNSAT unrefuted; W_4 refutes all, EV-CERTBIN-4a9d2f)")


# ---------------------------------------------------------------------------
# 8. Trimoska-Ionica-Dequen AFRICACRYPT 2020 (ePrint 2019/313), in-repo transcription
# ---------------------------------------------------------------------------
LIT = "inputs/SATIC-TRIMOSKA-2019/paper_fulltext.md"
LIT_HOST = "Intel Xeon E5-2640 2.40GHz (authors' MatriCS platform)"
# (table, lines, solver, config, l, n, sat_rt, sat_conf, unsat_rt, unsat_conf, n_obs_note)
T2 = [
    ("Magma F4 (grevlex)", "", 6, 17, 207.220, None, 142.119, None),
    ("Magma F4 (grevlex)", "", 6, 19, 215.187, None, 155.765, None),
    ("Magma F4 (grevlex)", "", 7, 19, 3854.708, None, 2650.696, None),
    ("Magma F4 (grevlex)", "", 7, 23, 3128.844, None, 2286.136, None),
    ("Magma F4 (grevlex)", "", 8, 23, "MEM", None, "MEM", None),
    ("Magma F4 (grevlex)", "", 8, 26, "MEM", None, "MEM", None),
    ("MiniSat", "CNF", 6, 17, 62.702, 408189, 270.261, 1463309),
    ("MiniSat", "CNF", 6, 19, 229.055, 1778377, 388.719, 2439933),
    ("MiniSat", "CNF", 7, 19, 406.918, 1919565, 6777.431, 25180492),
    ("MiniSat", "CNF", 7, 23, 12945.613, 61610582, 13260.586, 59289671),
    ("MiniSat", "CNF", 8, 23, 8027.974, 63384411, "TO", None),
    ("MiniSat", "CNF", 8, 26, "TO", None, "TO", None),
    ("CryptoMiniSat", "CNF-XOR + Prop.1 order", 6, 17, 15.673, 61812, 62.396, 260843),
    ("CryptoMiniSat", "CNF-XOR + Prop.1 order", 6, 19, 14.128, 53767, 64.563, 259688),
    ("CryptoMiniSat", "CNF-XOR + Prop.1 order", 7, 19, 176.463, 484098, 843.367, 2077747),
    ("CryptoMiniSat", "CNF-XOR + Prop.1 order", 7, 23, 300.021, 638152, 1012.412, 2070190),
    ("CryptoMiniSat", "CNF-XOR + Prop.1 order", 8, 23, 1700.949, 2420937, 11959.938, 16756106),
    ("CryptoMiniSat", "CNF-XOR + Prop.1 order", 8, 26, 3000.831, 4179236, 14412.193, 16783213),
    ("WDSat", "CNF-XOR + Prop.1 order (no symmetry breaking)", 6, 17, 0.601, 49117, 3.851, 254686),
    ("WDSat", "CNF-XOR + Prop.1 order (no symmetry breaking)", 6, 19, 0.470, 38137, 3.913, 255491),
    ("WDSat", "CNF-XOR + Prop.1 order (no symmetry breaking)", 7, 19, 9.643, 534867, 44.107, 2073089),
    ("WDSat", "CNF-XOR + Prop.1 order (no symmetry breaking)", 7, 23, 9.303, 477632, 47.347, 2067168),
    ("WDSat", "CNF-XOR + Prop.1 order (no symmetry breaking)", 8, 23, 68.929, 2646071, 525.057, 16666331),
    ("WDSat", "CNF-XOR + Prop.1 order (no symmetry breaking)", 8, 26, 185.480, 6261107, 533.607, 16684378),
]
T3 = [  # complete WDSat with symmetry breaking, 100 runs per cell
    (6, 17, .220, 17792, .605, 43875), (6, 19, .243, 19166, .639, 44034),
    (7, 19, 2.205, 130062, 6.859, 351353), (7, 23, 3.555, 189940, 7.478, 350257),
    (8, 23, 29.584, 1145966, 81.767, 2800335), (8, 26, 39.214, 1426216, 85.822, 2803580),
    (9, 37, 447, 10557129, 1048, 22396994), (9, 47, 609, 12675174, 1167, 22381494),
    (9, 59, 611, 11297325, 1327, 22390211), (9, 67, 677, 11608420, 1430, 22388053),
    (10, 47, 5847, 95131900, 11963, 179019409), (10, 59, 6849, 97254458, 13649, 179067171),
    (10, 67, 6530, 88292215, 14555, 179052277), (10, 79, 7221, 86174432, 16294, 179043408),
    (11, 59, 64162, 727241718, 135801, 1432191354), (11, 67, 70075, 741222864, 145357, 1432183842),
    (11, 79, 61370, 599263451, 161388, 1432120827), (11, 89, 85834, 736610196, 175718, 1432099666),
]
T4_EXTRA = [  # appendix Table 4, variants not already in Table 2
    ("CryptoMiniSat", "CNF-XOR, solver order", 6, 17, 133.983, 775948, 363.513, 1709971),
    ("CryptoMiniSat", "CNF-XOR, solver order", 6, 19, 560.080, 3396192, 1172.740, 5726372),
    ("CryptoMiniSat", "CNF-XOR, solver order", 7, 19, 1210.612, 5713259, 10258.351, 26079224),
    ("CryptoMiniSat", "CNF-XOR, solver order", 7, 23, 3637.032, 12159752, 19857.454, 47086152),
    ("CryptoMiniSat", "CNF-XOR, solver order", 8, 23, 9846.554, 18509058, "TO", None),
    ("CryptoMiniSat", "CNF-XOR, solver order", 8, 26, 6905.477, 13269631, "TO", None),
    ("WDSat", "Prop.1 + Gaussian elimination (WDSatGE)", 6, 17, 9.193, 48178, 56.718, 253123),
    ("WDSat", "Prop.1 + Gaussian elimination (WDSatGE)", 6, 19, 7.041, 36835, 58.876, 252799),
    ("WDSat", "Prop.1 + Gaussian elimination (WDSatGE)", 7, 19, 169.629, 528383, 736.863, 2062232),
    ("WDSat", "Prop.1 + Gaussian elimination (WDSatGE)", 7, 23, 159.101, 473223, 779.432, 2060501),
    ("WDSat", "Prop.1 + Gaussian elimination (WDSatGE)", 8, 23, 1290.702, 2630567, 9124.361, 16639322),
    ("WDSat", "Prop.1 + Gaussian elimination (WDSatGE)", 8, 26, 3404.765, 6231289, 9623.677, 16636122),
]


def literature():
    c = commit_of(LIT)
    common = dict(source_record="KN-LIT-92b022 (ePrint 2019/313, AFRICACRYPT 2020)", run_id="", branch="main",
                  commit=c, tier="literature_transcribed", m=3, t=1, host=LIT_HOST,
                  representation="S4 Weil descent (Trimoska generator), Koblitz y^2+xy=x^3+x^2+1")

    def emit(table, lines, solver, cfg, l, n, rt, conf, outcome, nobs, fit):
        if rt in ("MEM", "TO"):
            add(path=f"{LIT} {lines}", n=n, l=l, solver=solver, solver_config=cfg, outcome="censored",
                label=outcome, n_obs=nobs, n_censored=nobs, statistic="mean (paper)", censored="yes",
                censor_bound_s=(36000.0 if rt == "TO" else ""), include_in_fit="no",
                notes=f"{table}: " + (">200GB memory limit" if rt == "MEM" else ">10 hours timeout"), **common)
        else:
            add(path=f"{LIT} {lines}", n=n, l=l, solver=solver, solver_config=cfg, outcome=outcome,
                n_obs=nobs, n_censored=0, statistic="mean (paper)", wall_s=rt, conflicts=conf,
                censored="no", include_in_fit=fit, notes=f"{table}; reported, not reproduced", **common)

    for (s, cfg, l, n, srt, sc, urt, uc) in T2:
        emit("Table 2", "L751-794", s, cfg, l, n, srt, sc, "SAT", 10, "yes")
        emit("Table 2", "L751-794", s, cfg, l, n, urt, uc, "UNSAT", 10, "yes")
    for (l, n, srt, sc, urt, uc) in T3:
        emit("Table 3", "L821-842", "WDSat", "complete: Prop.1 order + m! symmetry breaking", l, n, srt, sc, "SAT", 100, "yes")
        emit("Table 3", "L821-842", "WDSat", "complete: Prop.1 order + m! symmetry breaking", l, n, urt, uc, "UNSAT", 100, "yes")
    for (s, cfg, l, n, srt, sc, urt, uc) in T4_EXTRA:
        emit("Table 4", "L915-972", s, cfg, l, n, srt, sc, "SAT", 10, "yes")
        emit("Table 4", "L915-972", s, cfg, l, n, urt, uc, "UNSAT", 10, "yes")
    slide = "inputs/SATIC-TRIMOSKA-2019/cp2020_slide_benchmark.md"
    for s, srt, sc, urt, uc in [("Groebner (Magma)", 229.3, None, 229.4, None), ("MiniSat", 239.7, 1840190, 517.0, 3433304),
                                ("Glucose", 189.2, 1527158, 274.8, 2056575), ("MapleLCMDistChronoBT", 655.1, 4035131, 918.7, 5378945),
                                ("CaDiCaL", 43.6, 254194, 141.3, 629869), ("CryptoMiniSat", 331.8, 1791188, 707.9, 3416526),
                                ("WDSat", 0.6, 48438, 3.8, 255698)]:
        for outcome, rt, cf in (("SAT", srt, sc), ("UNSAT", urt, uc)):
            add(source_record="KN-LIT-102cdb (CP 2020 slides)", run_id="", branch="main", commit=commit_of(slide),
                path=slide, tier="literature_transcribed", n=19, m=3, t=1, l=6,
                representation="S4 Weil descent (51 vars / 52 eqs)", solver=s, solver_config="slide table",
                host=LIT_HOST + " (assumed same platform)", outcome=outcome, n_obs="", statistic="mean (slide)",
                wall_s=rt, conflicts=cf, censored="no", include_in_fit="no",
                notes="single (l,n) cell; duplicates Table 2 family at l=6,n=19 for WDSat/MiniSat")


# ---------------------------------------------------------------------------
# 9. External n = 131 panel (aburan28/crypto @50ea716, bound by sha256 in EV-ICPERF-10c5fc)
# ---------------------------------------------------------------------------
EXT_SHA = {"solver_10_summary.json": "fc28f1ebd770f69da840c2ffc0cb68cab9372d6953227c035641fe44e9ac3ada",
           "solver_12_summary.json": "7ebd8b2531cbc2bee976f063ef4019428f2a8bcf67d5ad4a3453a95703dd2a2f",
           "solver_13_summary.json": "48af9b0a98d3f0cc394416a0fd554d2a5e1da5a391491d8d9313d6284c244fbb"}


def external():
    base = os.path.join(HERE, "external")
    for fn, sha in EXT_SHA.items():
        p = os.path.join(base, fn)
        if not os.path.exists(p):
            print("missing external", fn, file=sys.stderr)
            return
        got = hashlib.sha256(open(p, "rb").read()).hexdigest()
        assert got == sha, (fn, got)
    common = dict(source_record="EV-ICPERF-10c5fc (external, content-bound)", branch="aburan28/crypto",
                  commit="50ea716", tier="external_sha256_bound", m=3, t=1, n=131,
                  host="external session; Python ONB arithmetic; pycryptosat 5.15.0")
    d = json.load(open(os.path.join(base, "solver_10_summary.json")))
    for g in d["groups"]:
        att = g["attempted"]; per = g["all_phase_seconds"] / att
        ok = g["resolved_within_budget"] == att
        outcome = ("SAT" if g["stratum"] == "known_decomposable" else "UNSAT") if ok else "censored"
        fo = (g["field_api_operations"] / att) if g.get("field_api_operations") else None
        fam = {"quadratic-optimized": "Riemann-Roch L(4O) oracle (quadratic-optimized)",
               "quadratic-image": "Riemann-Roch L(4O) oracle (quadratic-image)",
               "s4-symmetric": "Semaev S4 via SAT (pycryptosat)", "chained-s3": "chained S3 via SAT (pycryptosat)"}[g["variant"]]
        add(path="research/nagao_relations/solver_10/summary.json", run_id="solver_10", n_obs=att,
            n_censored=att - g["resolved_within_budget"], l=g["d"], solver=fam,
            solver_config=f"mode={g['mode']}", outcome=outcome,
            label=g["stratum"], statistic="mean (all_phase_seconds / attempted)",
            wall_s=None if not ok else round(per, 3), censored="no" if ok else "yes",
            censor_bound_s=None if ok else round(per, 3), field_ops=None if fo is None else round(fo),
            representation=("Riemann-Roch L(4O) encoding" if "quadratic" in g["variant"] else "Weil descent to F_2"),
            include_in_fit="no",
            notes=("UNSAT stratum = uniform target (decomposition essentially impossible at m*d<<131)"
                   if g["stratum"] == "uniform" else "planted decomposable target") +
                  ("" if ok else "; NONE resolved within the per-configuration budget: per-attempt cost >= bound"), **common)
    d = json.load(open(os.path.join(base, "solver_13_summary.json")))
    for pnt in d["points"]:
        for which, key in (("Riemann-Roch quadratic-image oracle", "mean_rr_ops"), ("pair enumeration (null object)", "mean_pair_ops")):
            add(path="research/nagao_relations/solver_13/summary.json", run_id="solver_13", n_obs="", l=pnt["d"],
                solver=which, solver_config="complete enumeration (budget sized to finish)", outcome="MIXED",
                label="|F|=%d" % pnt["factor_base_points"], statistic="mean field ops per attempt",
                field_ops=pnt[key], censored="no", representation="factor base F in L(4O) / pairs over F",
                include_in_fit="yes", notes="field ops weight add=mul=sqr, inversions expanded (solver_12 limits)", **common)


def main():
    icperf_66fd51(); icperf_e21835(); icperf_783e9e(); ici_001(); albin(); sembin_msolve(); certbin()
    literature(); external()
    with open(os.path.join(HERE, "ctrial.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(ROWS)
    with open(os.path.join(HERE, "ctrial_targets.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["row_id", "value_s", "conflicts", "censored"]); w.writerows(TARGETS)
    print(len(ROWS), "rows;", len(TARGETS), "per-target values")


if __name__ == "__main__":
    main()
