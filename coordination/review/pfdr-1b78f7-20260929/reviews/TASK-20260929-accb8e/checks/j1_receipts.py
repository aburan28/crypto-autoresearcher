"""J1(a): every path in the f15632, 16c25d, 599b4b, 335bc4 and 0f66ef snapshot receipts
is hashed at a32e70808 (detached worktree) and compared with path_sha256; every
EXP-PFDR-1b78f7 run file bound by no receipt is listed. Also checks that no path is
bound by two receipts with different hashes (a changed archived file)."""
import hashlib, json, os, sys, collections
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
import rl  # noqa
WT = rl.WT
ARCH = "coordination/design/TASK-20260928-102217/archives"
TASKS = ["TASK-20260928-f15632", "TASK-20260929-16c25d", "TASK-20260929-599b4b", "TASK-20260929-335bc4",
         "TASK-20260929-0f66ef"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def main():
    out = {"receipts": {}, "conflicting_bindings": [], "unbound_run_files": []}
    bound = collections.defaultdict(dict)
    hashed = {}
    for t in TASKS:
        rp = os.path.join(WT, ARCH, t, "snapshot-receipt.json")
        rec = json.load(open(rl.opened(rp, f"J1(a): snapshot receipt {t}")))
        ps = rec.get("path_sha256") or {}
        res = {"paths": len(ps), "match": 0, "mismatch": [], "missing_at_a32e70808": [],
               "commit_sha": rec.get("commit_sha"), "parent_sha": rec.get("parent_sha"),
               "binding_mode": rec.get("binding_mode"), "run_ids": rec.get("run_ids"),
               "archive_artifact_paths": len(rec.get("archive_artifact_paths") or [])}
        for path, h in sorted(ps.items()):
            bound[path][t] = h
            fp = os.path.join(WT, path)
            if os.path.isdir(fp):
                res["mismatch"].append([path, "is a directory"])
                continue
            if not os.path.exists(fp):
                res["missing_at_a32e70808"].append(path)
                continue
            if fp not in hashed:
                hashed[fp] = sha(fp)
            if hashed[fp] == h:
                res["match"] += 1
            else:
                res["mismatch"].append([path, h, hashed[fp]])
        out["receipts"][t] = res
    for path, d in bound.items():
        if len(set(d.values())) > 1:
            out["conflicting_bindings"].append({"path": path, "bindings": d})
    runs = os.path.join(WT, "experiments/EXP-PFDR-1b78f7/runs")
    n_files = 0
    for root, dirs, files in os.walk(runs):
        for fn in files:
            rel = os.path.relpath(os.path.join(root, fn), WT)
            n_files += 1
            if rel not in bound:
                out["unbound_run_files"].append(rel)
    # also every other experiment file
    other_unbound = []
    for root, dirs, files in os.walk(os.path.join(WT, "experiments/EXP-PFDR-1b78f7")):
        if "/runs" in root + "/" and root.startswith(runs):
            continue
        for fn in files:
            rel = os.path.relpath(os.path.join(root, fn), WT)
            if rel not in bound:
                other_unbound.append(rel)
    out["run_files_total"] = n_files
    out["experiment_nonrun_files_unbound"] = other_unbound
    rl.log(runs, f"J1(a): hashed {len(hashed)} bound files under the worktree (every path in the five receipts) and walked runs/ ({n_files} files)")
    os.makedirs(os.path.join(W, "checks", "out"), exist_ok=True)
    with open(os.path.join(W, "checks", "out", "j1a-receipts.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    for t, r in out["receipts"].items():
        print(t, {k: (v if not isinstance(v, list) else len(v)) for k, v in r.items()})
    print("conflicting bindings:", len(out["conflicting_bindings"]), out["conflicting_bindings"][:5])
    print("run files:", n_files, "unbound:", len(out["unbound_run_files"]), out["unbound_run_files"][:20])
    print("experiment non-run files unbound:", other_unbound)


if __name__ == "__main__":
    main()
