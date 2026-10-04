#!/usr/bin/env python3
"""EJ2 negative controls for TASK-20260928-e2cfcf. Each control writes a scratch
copy of the draft in scratch/ beside this file with one entry id removed from
one leaf_map row (a raw line deletion inside that row's block), runs ej2_check
on it, records the scratch sha256 and what the check reports, then removes the
scratch copy.

Usage (repository root): python3 ej2_negative_controls.py <draft.yaml> <out.json>
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ej2_check  # noqa: E402

CONTROLS = [
    ("NC-EJ2-a drop T-0011 from stated outside row typed:definitions.bins outside span BINS-EXACT",
     "  - held_leaf: typed:definitions.bins outside span BINS-EXACT\n", "- T-0011\n"),
    ("NC-EJ2-b drop T-0621 from stated whole row typed:change.D3_descriptive_bins.bin_by_status",
     "  - held_leaf: typed:change.D3_descriptive_bins.bin_by_status\n", "- T-0621\n"),
    ("NC-EJ2-c drop T-0328 from the first leaf_map row that lists it (a stated C-ORDER row)",
     None, "- T-0328\n"),
]


def drop_in_row(raw, row_header, line_tail):
    lines = raw.split("\n")
    lm = raw.index("leaf_map:")
    start_line = raw[:lm].count("\n")
    if row_header is None:
        # the first leaf_map row that lists the entry
        for i in range(start_line, len(lines)):
            if lines[i].strip() == line_tail.strip():
                del lines[i]
                return "\n".join(lines), i
        raise ValueError("entry line not found")
    hdr = raw.index(row_header, lm)
    i = raw[:hdr].count("\n") + 1
    while not lines[i].lstrip().startswith("- held_leaf:"):
        if lines[i].strip() == line_tail.strip():
            del lines[i]
            return "\n".join(lines), i
        i += 1
    raise ValueError("entry line not in row block")


def main(draft, out):
    raw = Path(draft).read_text(encoding="utf-8")
    base = ej2_check.main(draft, str(HERE / "scratch_base.json"))
    (HERE / "scratch_base.json").unlink()
    scratch = HERE / "scratch"
    scratch.mkdir(exist_ok=True)
    results = []
    for i, (label, hdr, tail) in enumerate(CONTROLS):
        mod, line = drop_in_row(raw, hdr, tail)
        p = scratch / f"nc{i}.yaml"
        p.write_text(mod, encoding="utf-8")
        r = ej2_check.main(str(p), str(scratch / f"nc{i}.json"))
        s, b = r["summary"], base["summary"]
        changed = {k: {"base": b[k], "control": s[k]} for k in s if s[k] != b[k]}
        results.append({"control": label, "deleted_line_number": line + 1,
                        "scratch_sha256": hashlib.sha256(mod.encode("utf-8")).hexdigest(),
                        "summary_fields_changed": changed, "detected": bool(changed)})
        p.unlink()
        (scratch / f"nc{i}.json").unlink()
    scratch.rmdir()
    json.dump(results, open(out, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(results, indent=1, ensure_ascii=False))
    return 0 if all(r["detected"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
