#!/usr/bin/env python3
"""J7 (c) P-FA transfer: archived v6 attempt manifests vs the unchanged writer on scratch copies.

TASK-20261002-0114ff. Standard library plus PyYAML (parsing only).
For R12, R13, R14 attempt-1: MA = archived manifest run block (written through
finalize_attempt_v6.py), MB = manifest written now by the unchanged run_jobs.py
finalize-attempt on a scratch copy with the archived finalize-inputs.json. canon()
maps the scratch path strings (relative and absolute forms) onto the archived
attempt path. Reports the differing top-level keys, and inside 'code' the
differing sub-keys (the unchanged writer reads repository state at its fixed
REPO path, so commit / per-file status are environment, not writer, quantities).
raw-result.json is compared the same way.
"""
import json
import os
import sys

import yaml

WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e"
S = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/rv-0114ff/pfa"
REPO = "/home/user/crypto-autoresearcher"


def canon(x, maps):
    if isinstance(x, dict):
        return {canon(k, maps): canon(v, maps) for k, v in x.items()}
    if isinstance(x, list):
        return [canon(v, maps) for v in x]
    if isinstance(x, str):
        for a, b in maps:
            x = x.replace(a, b)
        return x
    return x


def main():
    out = {}
    for run in ("RUN-PFDR-011cd0-table", "RUN-PFDR-011cd0-search", "RUN-PFDR-011cd0-srch-check"):
        arch = f"experiments/EXP-PFDR-011cd0/runs/{run}/attempt-1"
        scr = f"{S}/{run}/attempt-1"
        maps = [(os.path.relpath(scr, REPO), arch), (scr, f"{REPO}/{arch}")]
        MA = yaml.safe_load(open(f"{WT}/{arch}/manifest.yaml"))["run"]
        MB = canon(yaml.safe_load(open(f"{scr}/manifest.yaml"))["run"], maps)
        diff_top = sorted(k for k in set(MA) | set(MB) if MA.get(k) != MB.get(k))
        cd = {}
        if "code" in diff_top:
            ca, cb = MA["code"], MB["code"]
            for k in sorted(set(ca) | set(cb)):
                if ca.get(k) != cb.get(k):
                    if k == "source_sha256":
                        dig = {f: (ca[k].get(f, {}).get("sha256") == cb[k].get(f, {}).get("sha256"),
                                   ca[k].get(f, {}).get("status"), cb[k].get(f, {}).get("status"))
                               for f in sorted(set(ca[k]) | set(cb[k]))}
                        cd[k] = {"all_digests_equal": all(v[0] for v in dig.values()),
                                 "status_pairs_archived_vs_now": sorted({(v[1], v[2]) for v in dig.values()})}
                    elif k == "status_porcelain_scoped":
                        cd[k] = {"archived_len": len(ca.get(k) or []), "now_len": len(cb.get(k) or [])}
                    else:
                        cd[k] = {"archived": ca.get(k), "now": cb.get(k)}
        RA = json.load(open(f"{WT}/{arch}/raw-result.json"))
        RB = canon(json.load(open(f"{scr}/raw-result.json")), maps)
        rdiff = sorted(k for k in set(RA) | set(RB) if RA.get(k) != RB.get(k))
        rsub = {}
        for k in rdiff:
            if isinstance(RA.get(k), dict) and isinstance(RB.get(k), dict):
                rsub[k] = {kk: [RA[k].get(kk), RB[k].get(kk)] for kk in set(RA[k]) | set(RB[k]) if RA[k].get(kk) != RB[k].get(kk)}
            else:
                rsub[k] = [RA.get(k), RB.get(k)]
        out[run] = {"manifest_top_level_keys_compared": len(set(MA) | set(MB)),
                    "manifest_differing_top_level_keys": diff_top,
                    "protocol_archived": MA.get("protocol"), "protocol_unchanged_writer": MB.get("protocol"),
                    "task_id_archived": MA.get("task_id"), "task_id_unchanged_writer": MB.get("task_id"),
                    "code_subkey_differences": cd,
                    "raw_result_differing_keys": rdiff, "raw_result_differences": rsub,
                    "writer_only_difference_holds": set(diff_top) <= {"protocol", "task_id", "code"} and
                    (not cd or set(cd) <= {"commit", "dirty", "status_porcelain_scoped", "source_sha256"}) and
                    cd.get("source_sha256", {}).get("all_digests_equal", True)}
    json.dump(out, open(sys.argv[1], "w"), indent=1, sort_keys=True, default=str)
    for run, v in out.items():
        print(run, "top-level diffs:", v["manifest_differing_top_level_keys"], "| code:", json.dumps(v["code_subkey_differences"], default=str)[:600],
              "| raw-result diffs:", v["raw_result_differing_keys"], json.dumps(v["raw_result_differences"], default=str)[:600])


if __name__ == "__main__":
    main()
