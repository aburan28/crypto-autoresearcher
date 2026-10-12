"""J1(c): every manifest.yaml under runs/ (run roots, attempts, invocation-check, merged/)
field by field against specification.yaml required_artifacts.per_run (inference block
included); certificate blocks against counts recomputed from the rows (claimed solves =
instances with k_found / ok for rho and sweep rows; verified = k_verified). PRR-1: the
census-m3/m4 ROOT certificate format defect is known; recorded, counts checked.
Prints no A7 value (the R15 manifest's result is summarised by key names only)."""
import glob, gzip, json, os, sys
import yaml
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
import rl  # noqa
WT = rl.WT
RUNS = os.path.join(WT, "experiments/EXP-PFDR-1b78f7/runs")

REQ = {
    "run id": [("id",), ("run_id",)],
    "experiment id": [("experiment_id",)],
    "status": [("status",)],
    "validity reason": [("validity", "reason"), ("validity_reason",), ("status_reason",)],
    "code commit": [("code", "commit")],
    "dirty state": [("code", "dirty")],
    "source sha256": [("code", "source_sha256")],
    "exact command": [("code", "command"), ("command",)],
    "python version": [("environment", "python_version")],
    "numpy version": [("environment", "numpy_version")],
    "OS": [("environment", "operating_system")],
    "CPU model": [("environment", "cpu_model")],
    "inputs": [("inputs",)],
    "seeds": [("inputs", "seeds")],
    "cells": [("inputs", "cells")],
    "inference.requested_policy": [("inference", "requested_policy")],
    "inference.backend": [("inference", "backend")],
    "inference.resolved_model_id": [("inference", "resolved_model_id")],
    "inference.model_provenance": [("inference", "model_provenance"), ("inference", "provenance")],
    "inference.model_verified": [("inference", "model_verified")],
    "inference.reasoning_effort": [("inference", "reasoning_effort")],
    "inference.fallback_used": [("inference", "fallback_used")],
    "inference.degraded_requirements": [("inference", "degraded_requirements")],
    "started timestamp": [("timing", "started_at"), ("started_at",)],
    "finished timestamp": [("timing", "finished_at"), ("finished_at",)],
    "peak RSS": [("resources", "peak_rss_bytes_max_descendant"), ("resources", "peak_rss_bytes")],
    "CPU seconds": [("resources", "cpu_seconds_descendants"), ("resources", "cpu_seconds")],
    "wall seconds": [("resources", "wall_seconds"), ("timing", "wall_seconds")],
    "result.certificate": [("result", "certificate")],
}


def get(d, path):
    for k in path:
        if not isinstance(d, dict) or k not in d:
            return None, False
        d = d[k]
    return d, True


def rows_counts(dirpath):
    """claimed / verified counts from the rows file in dirpath (if any)."""
    p = os.path.join(dirpath, "rows.jsonl.gz")
    if not os.path.exists(p):
        return None
    rl.opened(p, "J1(c): certificate counts recomputed from rows")
    claimed = verified = n = 0
    for l in gzip.open(p, "rt"):
        r = json.loads(l)
        n += 1
        if r.get("status") not in (None, "completed_valid"):
            continue
        if "k_found" in r:
            if r.get("k_found"):
                claimed += 1
                verified += bool(r.get("k_verified"))
        else:  # sweep and rho rows: ok means kP = Q verified by the solver (README 1-5)
            claimed += 1
            verified += bool(r.get("ok"))
    return {"rows": n, "claimed": claimed, "verified": verified}


def main():
    out = []
    for mf in sorted(glob.glob(os.path.join(RUNS, "**", "manifest.yaml"), recursive=True)):
        rel = os.path.relpath(mf, WT)
        doc = yaml.safe_load(open(rl.opened(mf, "J1(c): manifest field check")))
        run = doc.get("run", doc)
        missing = []
        for name, alts in REQ.items():
            ok = False
            for a in alts:
                v, found = get(run, a)
                if found and v not in (None, "", [], {}) or (found and name in ("dirty state", "inference.fallback_used", "inference.model_verified") and v is not None):
                    ok = True
                    break
                if found and name == "inference.degraded_requirements":
                    ok = True
                    break
            if not ok:
                missing.append(name)
        cert, _ = get(run, ("result", "certificate"))
        inf, _ = get(run, ("inference",))
        cnt = rows_counts(os.path.dirname(mf))
        ent = {"manifest": rel, "status": run.get("status"), "missing_fields": missing,
               "certificate": cert, "rows_counts": cnt,
               "inference": {k: (inf or {}).get(k) for k in ("requested_policy", "backend", "resolved_model_id",
                                                             "model_verified", "reasoning_effort", "fallback_used",
                                                             "degraded_requirements")}}
        # certificate rule
        if isinstance(cert, dict):
            v = cert.get("verified")
            ic, iv = cert.get("instances_claimed"), cert.get("instances_verified")
            rule_ok = (v is True and ic == iv and (ic or 0) > 0) or (cert.get("kind") == "none")
            ent["certificate_rule_ok"] = bool(rule_ok)
            if cnt is not None and ic is not None:
                ent["certificate_counts_match_rows"] = (ic == cnt["claimed"] and iv == cnt["verified"])
            if not isinstance(v, bool):
                ent["certificate_verified_not_boolean"] = True
        out.append(ent)
    with open(os.path.join(W, "checks", "out", "j1c-manifests.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
    for e in out:
        c = e["certificate"] if isinstance(e["certificate"], dict) else {}
        print(e["manifest"].replace("experiments/EXP-PFDR-1b78f7/runs/", ""), "|", e["status"], "| missing:", e["missing_fields"],
              "| cert:", {k: c.get(k) for k in ("kind", "verified", "instances_claimed", "instances_verified")},
              "| rule_ok:", e.get("certificate_rule_ok"), "| counts_match_rows:", e.get("certificate_counts_match_rows"),
              "| rows:", e["rows_counts"])
    print("inference blocks:", sorted(set(json.dumps(e["inference"], sort_keys=True) for e in out)))


if __name__ == "__main__":
    main()
