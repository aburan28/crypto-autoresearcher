#!/usr/bin/env python3
"""EXP-SEMBIN-d9767f independent checker. Validity only, never a prediction.

    check.py RUN_DIR TRIAL_PLAN_JSON

Independent of run.py's aggregation code (nothing is imported from run.py).
It re-reads raw-result.json, instances.json and results.jsonl and
  * verifies the schema, the required fields of every instances[] row and the
    identity fields (experiment, hypothesis, trial, run, seed, plan digest);
  * recomputes per cell, from instances[] alone, r_4 with its Clopper-Pearson
    95% interval, the false-refutation count, the M_4 refutation count, the
    D_W distribution and the eliminator agreement, and compares them with
    cells[] and summary;
  * re-labels a seeded sample of >= 10 instances per cell by rebuilding the
    Boolean system from the instances.json parameters and running the
    count_chain enumerator compiled from source (count_dense for dense nulls
    with N <= 26; larger dense nulls: the recorded solutions are evaluated);
  * checks codim(W_4) == nsol on every completed SAT W_4 / W_5 job;
  * recomputes instances_canonical_sha256 and the manifest's validity claim.
Exit 0 if clean (prints VALID), 3 with one line per violation otherwise.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

IMPL = Path(__file__).resolve().parent
SCHEMA = "sembin.closure_degree.result.v1"
REQUIRED = ["instance_id", "cell", "m", "n", "k", "v_type", "family", "curve_b", "label", "nsol", "closure_kind",
            "D", "eliminator", "contains_one", "rank", "cols", "rows", "codim", "iterations", "ops_proxy",
            "wall_s", "peak_rss_mb", "censored", "elimination_faults", "evalcheck_mismatch"]
EXCLUDED = ("wall_s", "peak_rss_mb")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def binom_cdf(x: int, n: int, p: float) -> float:
    return sum(math.comb(n, i) * (p ** i) * ((1 - p) ** (n - i)) for i in range(0, x + 1))


def cp95(x: int, n: int):
    """Clopper-Pearson by bisection on the CDF (written independently of run.py)."""
    if n == 0:
        return None
    a = 0.025

    def bisect(pred):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if pred(mid):
                hi = mid
            else:
                lo = mid
        return (lo + hi) / 2
    lo = 0.0 if x == 0 else bisect(lambda p: 1 - binom_cdf(x - 1, n, p) >= a)
    hi = 1.0 if x == n else bisect(lambda p: binom_cdf(x, n, p) <= a)
    return [round(lo, 6), round(hi, 6)]


def close(a, b, tol=2e-6):
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, list):
        return isinstance(b, list) and len(a) == len(b) and all(close(x, y, tol) for x, y in zip(a, b))
    return abs(float(a) - float(b)) <= tol


class Checker:
    def __init__(self):
        self.violations: list[str] = []

    def fail(self, msg: str):
        self.violations.append(msg)

    def expect(self, cond: bool, msg: str):
        if not cond:
            self.fail(msg)


def primary_w4(rows):
    """Per UNSAT instance the W_4 row of the primary eliminator (independent above
    50,000 columns, otherwise M4RI where it completed), censored rows excluded."""
    out = {}
    for r in rows:
        if r["closure_kind"] != "W" or r["D"] != 4 or r["label"] != "UNSAT" or r["censored"] \
                or r["contains_one"] is None:
            continue
        cur = out.get(r["instance_id"])
        prefer_indep = (r["cols"] or 0) > 50000
        want = "independent" if prefer_indep else "m4ri"
        if cur is None or (r["eliminator"] == want and cur["eliminator"] != want):
            out[r["instance_id"]] = r
    return out


def main(argv) -> int:
    if len(argv) != 3:
        print("usage: check.py RUN_DIR TRIAL_PLAN_JSON", file=sys.stderr)
        return 3
    run_dir, plan_path = Path(argv[1]), Path(argv[2])
    C = Checker()
    try:
        res = json.loads((run_dir / "raw-result.json").read_text())
        inst_doc = json.loads((run_dir / "instances.json").read_text())
        rows_raw = [json.loads(l) for l in (run_dir / "results.jsonl").read_text().splitlines() if l.strip()]
        plan_bytes = plan_path.read_bytes()
        plan = json.loads(plan_bytes)
    except (OSError, ValueError) as e:
        print(f"VIOLATION: unreadable input: {e}", file=sys.stderr)
        return 3
    C.expect((run_dir / "manifest.yaml").is_file(), "manifest.yaml missing")
    C.expect(isinstance(res.get("environment"), dict) and "m4ri_available" in res.get("environment", {}),
             "raw-result.json /environment missing or without m4ri_available")
    # ---- schema and identity
    C.expect(res.get("schema") == SCHEMA, "schema is not sembin.closure_degree.result.v1")
    C.expect(res.get("experiment_id") == "EXP-SEMBIN-d9767f", "experiment_id")
    C.expect(res.get("hypothesis_id") == "H-SEMBIN-106967", "hypothesis_id")
    C.expect(res.get("plan_sha256") == sha256_bytes(plan_bytes), "plan_sha256 does not match the trial plan")
    trial = next((t for t in plan.get("trials", []) if t.get("id") == res.get("trial_id")), None)
    C.expect(trial is not None, f"trial_id {res.get('trial_id')!r} not in the plan")
    if trial:
        C.expect(res.get("run_id") == trial.get("run_id"), "run_id does not match the plan")
        argv_plan = trial.get("argv") or []
        if "--seed" in argv_plan:
            C.expect(str(res.get("seed")) == argv_plan[argv_plan.index("--seed") + 1], "seed does not match the plan argv")
        C.expect(res.get("trial_id") == inst_doc.get("trial_id") and res.get("run_id") == inst_doc.get("run_id"),
                 "instances.json identity differs from raw-result.json")
    for key in ("cells", "instances", "summary", "instances_canonical_sha256", "seed"):
        C.expect(key in res, f"missing top-level field {key}")
    rows = res.get("instances") or []
    for i, r in enumerate(rows):
        missing = [f for f in REQUIRED if f not in r]
        if missing:
            C.fail(f"instances[{i}] missing fields {missing}")
            continue
        C.expect(r["label"] in ("SAT", "UNSAT"), f"instances[{i}] label {r['label']!r}")
        C.expect(r["closure_kind"] in ("M", "W") or isinstance(r["closure_kind"], str), f"instances[{i}] closure_kind")
        C.expect(r["eliminator"] in ("m4ri", "independent"), f"instances[{i}] eliminator {r['eliminator']!r}")
        C.expect(isinstance(r["censored"], bool), f"instances[{i}] censored not boolean")
        C.expect((r["label"] == "UNSAT") == (r["nsol"] == 0), f"instances[{i}] label/nsol inconsistent")
        if r["censored"]:
            C.expect(r["contains_one"] is None, f"instances[{i}] censored job carries a contains_one value")
        elif r.get("status") == "completed":
            C.expect(isinstance(r["contains_one"], bool) and isinstance(r["rank"], int) and isinstance(r["cols"], int),
                     f"instances[{i}] completed job lacks contains_one/rank/cols")
            C.expect(r["codim"] == r["cols"] - r["rank"], f"instances[{i}] codim != cols - rank")
            C.expect(r["cols"] == sum(math.comb(r["N"], d) for d in range(r["D"] + 1)) or r["closure_kind"] not in ("M", "W"),
                     f"instances[{i}] cols != C(N,<=D)")
    canon_rows = [{k: v for k, v in r.items() if k not in EXCLUDED} for r in rows]
    C.expect(sha256_bytes(canon(canon_rows).encode()) == res.get("instances_canonical_sha256"),
             "instances_canonical_sha256 does not recompute")
    # cross-check instances[] against results.jsonl (one row per job, same verdicts)
    raw_index = {}
    for r in rows_raw:
        raw_index[(r["instance_id"], r["closure_kind"], r["D"], r["eliminator"])] = r
    C.expect(len(rows_raw) == len(rows), f"results.jsonl has {len(rows_raw)} rows, instances[] {len(rows)}")
    for r in rows:
        raw = raw_index.get((r["instance_id"], r["closure_kind"], r["D"], r["eliminator"]))
        if raw is None:
            C.fail(f"{r['instance_id']} {r['closure_kind']}_{r['D']} {r['eliminator']}: no results.jsonl row")
            continue
        if raw.get("completed"):
            C.expect(bool(raw["contains_one"]) == r["contains_one"] and int(raw["rank"]) == r["rank"],
                     f"{r['instance_id']} {r['closure_kind']}_{r['D']} {r['eliminator']}: verdict differs from results.jsonl")
    # ---- per-cell recount
    inst_by_id = {i["instance_id"]: i for i in inst_doc.get("instances", [])}
    cells = res.get("cells") or []
    summary = res.get("summary") or {}
    total_false = total_m4 = total_disagree = total_pairs = total_censored = total_codim_mismatch = 0
    for c in cells:
        key = c["cell_key"]
        crow = [r for r in rows if r.get("cell_key") == key and r.get("rep", 0) == 0]
        prim = primary_w4(crow)
        refuted = sum(1 for r in prim.values() if r["contains_one"])
        total = len(prim)
        C.expect(c.get("unsat_w4_run") == total and c.get("unsat_w4_refuted") == refuted,
                 f"{key}: r_4 counts {c.get('unsat_w4_refuted')}/{c.get('unsat_w4_run')} recount {refuted}/{total}")
        r4 = (refuted / total) if total else None
        C.expect(close(c.get("r_4"), r4), f"{key}: r_4 {c.get('r_4')} recount {r4}")
        C.expect(close(c.get("r_4_cp95"), cp95(refuted, total), 1e-4), f"{key}: CP95 {c.get('r_4_cp95')} recount {cp95(refuted, total)}")
        fr = sum(1 for r in crow if r["label"] == "SAT" and r["contains_one"])
        C.expect(c.get("false_refutations") == fr, f"{key}: false_refutations {c.get('false_refutations')} recount {fr}")
        m4 = sum(1 for r in crow if r["closure_kind"] == "M" and r["D"] == 4 and r["label"] == "UNSAT" and r["contains_one"])
        C.expect(c.get("m4_refutations") == m4, f"{key}: m4_refutations {c.get('m4_refutations')} recount {m4}")
        dw, maxd = {}, {}
        for r in crow:
            if r["label"] == "UNSAT" and r["closure_kind"] == "W" and r.get("status") == "completed":
                maxd[r["instance_id"]] = max(maxd.get(r["instance_id"], 0), r["D"])
                if r["contains_one"]:
                    dw[r["instance_id"]] = min(dw.get(r["instance_id"], 99), r["D"])
        dist = {}
        for iid in {r["instance_id"] for r in crow if r["label"] == "UNSAT"}:
            lab = str(dw[iid]) if iid in dw else (f"not_refuted_at_max_D_{maxd[iid]}" if iid in maxd else "no_completed_W")
            dist[lab] = dist.get(lab, 0) + 1
        C.expect(c.get("D_W_distribution") == dist, f"{key}: D_W distribution {c.get('D_W_distribution')} recount {dist}")
        pairs = agree = 0
        first = {}
        for r in crow:
            if r.get("status") != "completed" or r["closure_kind"] not in ("M", "W"):
                continue
            kk = (r["instance_id"], r["closure_kind"], r["D"])
            if kk in first:
                pairs += 1
                agree += first[kk]["contains_one"] == r["contains_one"] and (
                    first[kk]["contains_one"] or first[kk]["rank"] == r["rank"])
            else:
                first[kk] = r
        C.expect(c.get("eliminator_pairs") == pairs and c.get("eliminator_agreements") == agree,
                 f"{key}: eliminator agreement {c.get('eliminator_agreements')}/{c.get('eliminator_pairs')} recount {agree}/{pairs}")
        cens = sum(1 for r in crow if r["censored"])
        C.expect(c.get("censored_jobs") == cens, f"{key}: censored_jobs {c.get('censored_jobs')} recount {cens}")
        # codim == nsol on SAT W_4 / W_5
        for r in crow:
            if r["label"] == "SAT" and r["closure_kind"] == "W" and r["D"] >= 4 and r.get("status") == "completed":
                if r["codim"] != r["nsol"]:
                    total_codim_mismatch += 1
                    C.fail(f"{r['instance_id']} W_{r['D']} {r['eliminator']}: codim {r['codim']} != nsol {r['nsol']}")
        total_false += fr; total_m4 += m4; total_disagree += pairs - agree; total_pairs += pairs; total_censored += cens
    C.expect(summary.get("false_refutations") == total_false, f"summary.false_refutations {summary.get('false_refutations')} recount {total_false}")
    C.expect(summary.get("m4_refutations") == total_m4, f"summary.m4_refutations recount {total_m4}")
    C.expect(summary.get("eliminator_disagreements") == total_disagree, f"summary.eliminator_disagreements recount {total_disagree}")
    C.expect(summary.get("censored_jobs") == total_censored, f"summary.censored_jobs recount {total_censored}")
    r4_map = {c["cell_key"]: c["r_4"] for c in cells}
    C.expect(all(close(summary.get("r4_by_cell", {}).get(k), v) for k, v in r4_map.items()) and
             set(summary.get("r4_by_cell", {})) == set(r4_map), "summary.r4_by_cell differs from cells[]")
    invalid = (total_false or total_disagree or total_codim_mismatch
               or summary.get("elimination_faults") or summary.get("enumerator_disagreements")
               or summary.get("evalcheck_mismatches") or summary.get("worker_errors")
               or (summary.get("c1") and not summary["c1"].get("pass"))
               or (summary.get("c6") and not summary["c6"].get("identical")))
    C.expect((res.get("status") == "completed_invalid") == bool(invalid),
             f"raw-result status {res.get('status')!r} disagrees with the recounted invalidation rules")
    # ---- re-labelling from source on a seeded sample
    sample_seed = int(sha256_bytes(f"{res.get('run_id')}|{res.get('trial_id')}|relabel".encode())[:16], 16)
    rng = random.Random(sample_seed)
    tmp = Path(tempfile.mkdtemp(prefix="sembin-check-"))
    try:
        b = subprocess.run(["sh", str(IMPL / "build.sh"), str(IMPL), str(tmp / "build")], capture_output=True, text=True)
        if b.returncode != 0:
            C.fail(f"checker build from source failed: {b.stderr[-300:]}")
        else:
            sys.path.insert(0, str(tmp / "build"))
            import pilot_lib as L  # noqa: PLC0415
            import pilot2_lib as P  # noqa: PLC0415
            import ctypes  # noqa: PLC0415
            from array import array  # noqa: PLC0415

            def count_dense(system, cap=4096):
                ptr = array("q", [0]); masks = array("Q")
                for e in system["equations"]:
                    masks.extend(e); ptr.append(len(masks))
                sol = (ctypes.c_uint64 * cap)(); ns = ctypes.c_long(0)
                pb = (ctypes.c_long * len(ptr)).from_buffer(ptr)
                mb = (ctypes.c_uint64 * max(1, len(masks))).from_buffer(masks)
                tot = P._cc.count_dense(system["N"], len(system["equations"]), ctypes.addressof(pb),
                                        ctypes.addressof(mb), sol, cap, ctypes.byref(ns))
                return int(tot), sorted(int(sol[i]) for i in range(ns.value))

            def eq_sha(eqs):
                return sha256_bytes(canon([sorted(e) for e in eqs]).encode())

            cap = int(inst_doc.get("solution_cap", 256))
            by_cell: dict[str, list] = {}
            for inst in inst_doc.get("instances", []):
                if inst.get("rep", 0) == 0:
                    by_cell.setdefault(inst["cell_key"], []).append(inst)
            relabelled = 0
            for key in sorted(by_cell):
                pool = by_cell[key]
                pick = pool if len(pool) <= 10 else rng.sample(pool, 10)
                for inst in sorted(pick, key=lambda x: x["instance_id"]):
                    m, n, k, z = inst["m"], inst["n"], inst["k"], inst["z"]
                    basis, b, modulus = inst["basis"], inst["curve_b"], inst["modulus"]
                    fam = inst["family"]
                    if fam == "M2CTRL":
                        sysm = L.build_m2(n, k, basis, b, z, modulus)
                        cnt, bs = L.boolean_count_m2(sysm)
                        bs = sorted(bs)
                    else:
                        sysm = P.build_chain(n, k, m, basis, b, z, modulus)
                        if fam == "NULL":
                            sysm = P.support_null(sysm, inst["null_seed"])
                        elif fam == "NULL2":
                            sysm = P.dense_null(sysm, inst["null_seed"], inst["null_draw"])
                        if fam == "NULL2":
                            if sysm["N"] <= 26:
                                cnt, bs = count_dense(sysm)
                            else:
                                cnt, bs = None, None
                        else:
                            cnt, bs = P.boolean_count_chain(sysm)
                    C.expect(eq_sha(sysm["equations"]) == inst["equations_sha256"],
                             f"relabel {inst['instance_id']}: rebuilt system differs from the recorded equations digest")
                    C.expect(sysm["N"] == inst["N"], f"relabel {inst['instance_id']}: N")
                    if cnt is not None:
                        C.expect(cnt == inst["nsol"], f"relabel {inst['instance_id']}: nsol {inst['nsol']} recount {cnt}")
                        C.expect(bs[:cap] == inst["solutions"][:len(bs[:cap])],
                                 f"relabel {inst['instance_id']}: solution set differs")
                    # every recorded solution is a zero of the rebuilt system
                    for s in inst["solutions"][:cap]:
                        if any(L.eval_system(sysm["equations"], s)):
                            C.fail(f"relabel {inst['instance_id']}: recorded solution {s} does not vanish")
                            break
                    relabelled += 1
            C.expect(relabelled > 0 or not by_cell, "no instance re-labelled")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # ---- manifest consistency
    try:
        man = (run_dir / "manifest.yaml").read_text()
        C.expect(f'id: "{res.get("run_id")}"' in man, "manifest run id differs")
        C.expect(f'status: "{res.get("status")}"' in man, "manifest status differs from raw-result status")
    except OSError:
        pass
    if C.violations:
        for v in C.violations:
            print(f"VIOLATION: {v}", file=sys.stderr)
        print(f"INVALID: {len(C.violations)} violation(s)", file=sys.stderr)
        return 3
    print(f"VALID: {len(rows)} jobs over {len(inst_by_id)} instances in {len(cells)} cell(s); "
          f"false_refutations={total_false} eliminator_pairs={total_pairs} censored={total_censored}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
