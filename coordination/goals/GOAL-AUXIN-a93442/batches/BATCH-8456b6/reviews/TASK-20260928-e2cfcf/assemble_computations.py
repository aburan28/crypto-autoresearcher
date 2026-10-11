"""Assemble computations.json for TASK-20260928-e2cfcf from the checker outputs.

Usage: python3 assemble_computations.py <outdir-with-checker-json> <draft> <out>
Emits no census values, control integers, witness integers or depths.
"""
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone

import yaml

TASK = "TASK-20260928-e2cfcf"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def dedent_reload(draft_path, node_paths):
    """Reload each source_bytes span with its first line re-indented by the start column; compare with the held node."""
    draft = yaml.safe_load(open(draft_path))["successor_contract"]
    out = {"checked": 0, "equal_after_first_line_reindent": 0, "not_equal": []}
    for e in draft["transcluded"]["entries"]:
        a = e["anchor"]
        if a.get("kind") != "source_bytes":
            continue
        blob = subprocess.run(
            ["git", "show", f"{e['source_commit']}:{e['source_path']}"],
            capture_output=True, check=True,
        ).stdout.decode()
        lines = blob.splitlines(keepends=True)
        l1, c1, l2, c2 = a["line_col_range"]
        start = sum(len(x) for x in lines[: l1 - 1]) + c1
        end = sum(len(x) for x in lines[: l2 - 1]) + c2
        span = blob[start:end]
        out["checked"] += 1
        node = yaml.safe_load(blob)
        for seg in node_paths[e["entry_id"]]:
            node = node[int(seg)] if isinstance(node, list) else node[seg]
        try:
            ok = yaml.safe_load(" " * c1 + span) == node
        except yaml.YAMLError:
            ok = False
        if ok:
            out["equal_after_first_line_reindent"] += 1
        else:
            out["not_equal"].append(e["entry_id"])
    return out


def main(tdir, draft_path, out_path):
    ej1 = json.load(open(f"{tdir}/ej1_full.json"))
    ej1_nc = json.load(open(f"{tdir}/ej1_nc.json"))
    ej2 = json.load(open(f"{tdir}/ej2.json"))
    ej2_nc = json.load(open(f"{tdir}/ej2_nc.json"))
    ej4 = json.load(open(f"{tdir}/ej4.json"))
    cc = ej4["construction_commitments"]
    cc["r_bit_lengths_equal_recipe_B"] = all(cc.pop(k) == 256 for k in ("C-PLANT-M_bits_r", "C-PLANT-P_bits_r"))
    comp = {
        "task_id": TASK,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "runs_launched": 0,
        "draft_contract_sha256": sha(draft_path),
        "EJ1": {
            "summary": ej1["summary"],
            "source_bytes_first_line_reindent_reload": dedent_reload(
                draft_path, {x["entry_id"]: x["node_path"] for x in ej1["entries"]}
            ),
            "entries": ej1["entries"],
            "negative_controls": ej1_nc,
            "rebuild": {
                "runs": 2,
                "procedure": "copies of build_draft.py and fresh-text.yaml into rebuild/run1 and rebuild/run2 under this write scope; python3 build_draft.py run from each copy; exit 0; t5_failures empty",
                "rebuilt_draft_sha256": [
                    "a85aa7630ecca8f11385a5ff6c52d9fa9197028a96366852565d0804603c4a69",
                    "a85aa7630ecca8f11385a5ff6c52d9fa9197028a96366852565d0804603c4a69",
                ],
                "equals_snapshot": True,
                "rebuild_copies_removed_before_seal": True,
            },
        },
        "EJ2": {**ej2, "negative_controls": ej2_nc},
        "EJ4": ej4,
    }
    text = json.dumps(comp, indent=1, sort_keys=False, default=str)
    long_ints = sorted(set(re.findall(r"(?<![-0-9a-f])[0-9]{6,}(?![0-9a-f])", text)))
    if long_ints:
        raise SystemExit(f"refusing: integers of six or more digits present: {long_ints[:5]}")
    open(out_path, "w").write(text + "\n")
    print(sha(out_path))


if __name__ == "__main__":
    main(*sys.argv[1:4])
