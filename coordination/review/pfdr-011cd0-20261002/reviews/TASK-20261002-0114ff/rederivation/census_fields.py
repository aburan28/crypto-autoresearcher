#!/usr/bin/env python3
"""Whitelist-guarded reader of census rows (rows.jsonl.gz). TASK-20261002-0114ff.

The ONLY code of this task that opens a rows.jsonl.gz before the seal. It obeys
rederivation/field-whitelist.yaml (sha256 checked at start-up): after
json.loads, only whitelisted paths are copied; nothing else is accessed,
printed or stored. Any whitelisted name containing a forbidden substring is
dropped from the list at start-up (forbidden_rule), so 'planted_relations' is
NOT read.

Usage: census_fields.py OUT_PREFIX ROWFILE [ROWFILE ...]
Writes OUT_PREFIX.jsonl.gz (one extracted record per line, in file order) and
OUT_PREFIX.schema.json (key NAMES only). Standard library only.
"""
import gzip
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WL_PATH = os.path.join(HERE, "field-whitelist.yaml")
WL_SHA256 = "1de823e893cae6b1858c42eac4fbc5355259e43818345a208c9f872948b72e22"

TOP = ["bits", "curve", "m", "arm", "fb", "mode", "panel", "status", "status_reason", "reason",
       "error", "terminated_by", "p", "a", "b", "N", "order", "P", "Q", "target_label",
       "target_seed", "solver_seed", "fb_size", "size", "s", "s_sub", "s_dick", "X_fix", "x_fix",
       "encoding_budget_lambda"]
CONTAINERS = ["fb", "factor_base", "base", "fb_params", "fb_describe"]
SUB = ["kind", "size", "seed", "d", "target_size", "n_tt", "n_tb", "planted_relations",
       "skipped_tuples", "logs", "note"]
FORBIDDEN = ["relations", "pairs", "r_star", "rank", "kappa", "multiplicity", "dup", "poisson"]


def allowed(name):
    n = name.lower()
    return not any(f in n for f in FORBIDDEN)


def main():
    if hashlib.sha256(open(WL_PATH, "rb").read()).hexdigest() != WL_SHA256:
        sys.exit("whitelist sha256 mismatch: refusing to read")
    top = [k for k in TOP if allowed(k)]
    sub = [k for k in SUB if allowed(k)]
    dropped = [k for k in TOP + SUB if not allowed(k)]
    out_prefix, files = sys.argv[1], sys.argv[2:]
    names_top, names_sub = {}, {}
    n = 0
    with gzip.open(out_prefix + ".jsonl.gz", "wt") as out:
        for fp in files:
            with gzip.open(fp, "rt") as fh:
                for line in fh:
                    d = json.loads(line)
                    for k in d.keys():           # NAMES only
                        names_top[k] = names_top.get(k, 0) + 1
                    rec = {}
                    for k in top:
                        if k in d and not isinstance(d[k], dict):
                            rec[k] = d[k]
                    for c in CONTAINERS:
                        if c in d and isinstance(d[c], dict):
                            sd = d[c]
                            for k in sd.keys():  # NAMES only
                                names_sub[c + "." + k] = names_sub.get(c + "." + k, 0) + 1
                            rec[c] = {k: sd[k] for k in sub if k in sd}
                    del d
                    rec["_file"] = os.path.relpath(fp, "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e")
                    out.write(json.dumps(rec, sort_keys=True) + "\n")
                    n += 1
    json.dump({"whitelist_sha256": WL_SHA256, "names_dropped_by_forbidden_rule": dropped,
               "records": n, "top_level_key_names": names_top,
               "container_subkey_names": names_sub},
              open(out_prefix + ".schema.json", "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
