"""J1(c) follow-up (final review): for the fields checks/j1_manifests.py flagged as missing
(cells, seeds, peak RSS, CPU seconds), search each manifest for the field under ANY key path
(key names containing 'cell', 'seed', 'rss', 'cpu') and report the paths found. Values are
printed only for rss/cpu keys; the R15 analysis manifest is reported by key paths only."""
import glob, json, os, sys
import yaml
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
import rl  # noqa
RUNS = os.path.join(rl.WT, "experiments/EXP-PFDR-1b78f7/runs")
flag = {e["manifest"]: e["missing_fields"] for e in json.load(open(os.path.join(W, "checks/out/j1c-manifests.json")))}


def walk(o, path, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            p = path + [str(k)]
            kl = str(k).lower()
            for tag in ("cell", "seed", "rss", "cpu"):
                if tag in kl:
                    acc.setdefault(tag, []).append((".".join(p), v))
            walk(v, p, acc)
    elif isinstance(o, list):
        for i, v in enumerate(o[:3]):
            walk(v, path + [f"[{i}]"], acc)


out = {}
for mf in sorted(glob.glob(os.path.join(RUNS, "**", "manifest.yaml"), recursive=True)):
    rel = os.path.relpath(mf, rl.WT)
    miss = [m for m in flag.get(rel, []) if m in ("cells", "seeds", "peak RSS", "CPU seconds")]
    if not miss:
        continue
    doc = yaml.safe_load(open(rl.opened(mf, "J1(c) follow-up: key-path search for fields flagged missing (cells/seeds/RSS/CPU)")))
    run = doc.get("run", doc)
    acc = {}
    walk(run, [], acc)
    is_analysis = "RUN-PFDR-1b78f7-analysis" in rel
    ent = {"flagged": miss, "top_level_keys": sorted(run.keys())}
    for tag, lst in acc.items():
        if tag in ("rss", "cpu") and not is_analysis:
            ent[tag] = [(p, v if isinstance(v, (int, float, str)) or v is None else type(v).__name__) for p, v in lst][:6]
        else:
            ent[tag] = [p for p, _ in lst][:8]
    out[rel.replace("experiments/EXP-PFDR-1b78f7/runs/", "")] = ent
json.dump(out, open(os.path.join(W, "checks/out/j1c-manifest-fields-followup.json"), "w"), indent=1, default=str)
for k, v in out.items():
    print(k, json.dumps(v, default=str)[:900])
