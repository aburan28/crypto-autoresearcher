"""J-VAL (1): run count, statuses, attempts, from every manifest, raw-result.json
and execution.json of the EXP-PFDR-0b3699 run set (TASK-20261009-33b5cf).

Independent reader (PyYAML + json only). For each run root: the attempt
directories present; the run-root and attempt manifests' run.status, validity,
completeness, timing, code commit/dirty; raw-result.json top-level status keys;
and every execution.json beneath it (exit_code, watchdog_expired, started_at,
finished_at). Flags: a manifest status other than completed_valid, a nonzero
exit or expired watchdog, a run-root/attempt manifest disagreement on status,
an execution started before or finished after the manifest's timing span.
No seeds (deterministic).
Usage: python run_census.py <runs-dir> <out.json>
"""
import datetime as dt
import json
import os
import sys

import yaml


def ts(s):
    return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()


def main():
    runs, out = sys.argv[1], sys.argv[2]
    rep = {}
    for rid in sorted(os.listdir(runs)):
        root = os.path.join(runs, rid)
        attempts = sorted(d for d in os.listdir(root) if d.startswith("attempt-"))
        mr = yaml.safe_load(open(os.path.join(root, "manifest.yaml")))["run"]
        rr = json.load(open(os.path.join(root, "raw-result.json")))
        r = {"attempts": attempts, "root": {
            "status": mr.get("status"), "validity": mr.get("validity"),
            "completeness": mr.get("completeness"), "timing": mr.get("timing"),
            "commit": mr.get("code", {}).get("commit"), "dirty": mr.get("code", {}).get("dirty"),
            "task_id": mr.get("task_id"), "location_kind": mr.get("location_kind"),
            "has_command_key": "command" in mr.get("code", {}),
            "certificate": mr.get("result", {}).get("certificate"),
            "seeds": mr.get("seeds"),
        }, "raw_result_keys": sorted(rr.keys()),
            "raw_result_status": {k: rr[k] for k in ("status", "valid", "validity", "run_status", "counts_by_status") if k in rr}}
        flags = []
        if mr.get("status") != "completed_valid":
            flags.append(f"root status {mr.get('status')}")
        t0, t1 = ts(mr["timing"]["started_at"]), ts(mr["timing"]["finished_at"])
        r["attempt_manifests"] = {}
        for a in attempts:
            ma = yaml.safe_load(open(os.path.join(root, a, "manifest.yaml")))["run"]
            r["attempt_manifests"][a] = {"status": ma.get("status"), "timing": ma.get("timing"),
                                         "location_kind": ma.get("location_kind")}
            if ma.get("status") != mr.get("status"):
                flags.append(f"{a} status {ma.get('status')} != root {mr.get('status')}")
        execs = []
        for d, _, fs in sorted(os.walk(root)):
            if "execution.json" in fs:
                ex = json.load(open(os.path.join(d, "execution.json")))
                e = {"dir": os.path.relpath(d, root), "exit_code": ex.get("exit_code"),
                     "watchdog_expired": ex.get("watchdog_expired"),
                     "started_at": ex.get("started_at"), "finished_at": ex.get("finished_at"),
                     "commit": ex.get("git", {}).get("commit"),
                     "tracked_dirty": ex.get("git", {}).get("tracked_tree_dirty")}
                execs.append(e)
                if e["exit_code"] != 0:
                    flags.append(f"{e['dir']} exit {e['exit_code']}")
                if e["watchdog_expired"]:
                    flags.append(f"{e['dir']} watchdog expired")
                if ts(e["started_at"]) < t0 - 1e-6 or ts(e["finished_at"]) > t1 + 1e-6:
                    flags.append(f"{e['dir']} outside manifest timing")
        r["executions"] = len(execs)
        r["execution_commits"] = sorted({e["commit"] for e in execs})
        r["execution_dirty"] = sorted({str(e["tracked_dirty"]) for e in execs})
        r["execution_span"] = [min(e["started_at"] for e in execs), max(e["finished_at"] for e in execs)] if execs else None
        r["executions_nonzero_or_watchdog"] = [e for e in execs if e["exit_code"] != 0 or e["watchdog_expired"]]
        r["flags"] = flags
        rep[rid] = r
    json.dump(rep, open(out, "w"), indent=1, default=str)
    for rid, r in rep.items():
        print(rid, "attempts", r["attempts"], "status", r["root"]["status"], "| execs", r["executions"],
              "commits", r["execution_commits"], "dirty", r["execution_dirty"], "| span", r["execution_span"],
              "| timing", r["root"]["timing"], "| flags", r["flags"])


if __name__ == "__main__":
    main()
