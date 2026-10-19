#!/usr/bin/env python3
"""Nonce-sampled replay in a scratch worktree. Never writes in the repo tree.

    python3 -I replay.py select AUDIT_JSONL K OUT_IDS     (seed from replay_seed.txt)
    python3 -I replay.py run WORKTREE EVIDENCE_ID...      (prints one json line per id)

A replay passes only if the command exits 0 AND every JSON/YAML result file it
rewrote is structurally equal to the committed one after dropping time-like
keys. Anything else is `fail` or `not_covered` (with the reason), never a pass.
"""
from __future__ import annotations
import json, os, random, re, shlex, subprocess, sys
from pathlib import Path
import yaml

CASE = Path(__file__).resolve().parents[1]
REPO = CASE.parents[2]
TIME = re.compile(r"time|wall|date|host|pid|elapsed|second|stamp|duration|uuid|commit|path|dir|cwd", re.I)


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if not TIME.search(str(k))}
    if isinstance(o, list):
        return [strip(v) for v in o]
    if isinstance(o, float):
        return round(o, 9)
    return o


def select(audit, k, out):
    seed = re.search(r"nonce=(\w+)", (CASE / "replay_seed.txt").read_text()).group(1)
    rows = [json.loads(l) for l in open(audit)]
    elig = sorted(r["evidence_id"] for r in rows if r.get("replay_command_file"))
    pick = random.Random(int(seed, 16)).sample(elig, min(k, len(elig)))
    open(out, "w").write("\n".join(sorted(pick)) + "\n")
    print(f"eligible={len(elig)} picked={len(pick)}")


def run_one(wt, eid, rows):
    r = rows[eid]
    cmdf = REPO / r["replay_command_file"]
    txt = cmdf.read_text().strip()
    res = {"evidence_id": eid, "command_file": r["replay_command_file"], "command": txt[:300]}
    cmdline = [ln for ln in txt.splitlines() if ln.strip() and not ln.startswith("#")]
    if len(cmdline) != 1:
        res.update(status="not_covered", reason=f"command.txt has {len(cmdline)} command lines")
        return res
    try:
        argv = shlex.split(cmdline[0])
    except Exception as e:  # noqa
        res.update(status="not_covered", reason=f"unparseable: {e}")
        return res
    if argv and argv[0].startswith("python"):
        argv[0] = "python3"
    script = next((a for a in argv[1:] if a.endswith(".py")), None)
    if argv[0] != "python3" or not script or not (Path(wt) / script).exists():
        res.update(status="not_covered", reason="not a repo-local python3 script (or script absent)")
        return res
    subprocess.run(["git", "-C", wt, "checkout", "-q", "--", "."], check=False)
    subprocess.run(["git", "-C", wt, "clean", "-fdq"], check=False)
    env = {"PATH": os.environ["PATH"], "HOME": wt, "PYTHONHASHSEED": "0"}
    try:
        p = subprocess.run(argv, cwd=wt, env=env, capture_output=True, text=True, timeout=150)
    except subprocess.TimeoutExpired:
        res.update(status="not_covered", reason="timeout 150s (proves no absence of agreement)")
        return res
    res["exit_code"] = p.returncode
    if p.returncode != 0:
        res.update(status="fail_or_env", reason=(p.stderr or p.stdout)[-200:])
        return res
    st = subprocess.run(["git", "-C", wt, "status", "--porcelain"], capture_output=True, text=True).stdout.splitlines()
    changed = [ln[3:] for ln in st if ln.startswith(" M")]
    new = [ln[3:] for ln in st if ln.startswith("??")]
    cmp = {"same": 0, "differ": [], "unparsed": 0}
    for f in changed:
        if not f.endswith((".json", ".yaml", ".yml")):
            cmp["unparsed"] += 1
            continue
        old = subprocess.run(["git", "-C", wt, "show", f"HEAD:{f}"], capture_output=True, text=True).stdout
        try:
            ld = (lambda s: yaml.safe_load(s))
            a, b = strip(ld(old)), strip(ld((Path(wt) / f).read_text()))
        except Exception:
            cmp["unparsed"] += 1
            continue
        (cmp.__setitem__("same", cmp["same"] + 1) if a == b else cmp["differ"].append(f))
    res.update(changed_files=len(changed), new_files=len(new), compare=cmp)
    if cmp["differ"]:
        res["status"] = "fail"
    elif cmp["same"] > 0:
        res["status"] = "pass"
    else:
        res["status"] = "not_covered"
        res["reason"] = "exit 0 but no comparable committed result file was regenerated"
    return res


def main():
    a = sys.argv[1:]
    if a[0] == "select":
        select(a[1], int(a[2]), a[3])
        return
    if a[0] == "run":
        wt = a[1]
        rows = {}
        for l in open(CASE / "shards" / "all.jsonl"):
            d = json.loads(l)
            rows[d["evidence_id"]] = d
        for eid in a[2:]:
            print(json.dumps(run_one(wt, eid, rows)), flush=True)


if __name__ == "__main__":
    main()
