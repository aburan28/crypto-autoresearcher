"""J2b(1) sample selection, by the rule fixed in the review plan, before any count is read.

Rule (review-plan J2b attack_plan (1), card attack_plan_J2b (1)): for every (bits, r) and every n in
{1024, 2048, 4096}, the ok main record whose curve index c comes first in the order of
sha256("BATCH-924d2c|J2b|" + cell + "|" + str(c)) hex digest; plus the same rule for n in {256, 512} at
r = (bits mod 3) + 1 for each bits; 33 jobs.

Also fixes the curve-order sample of J2b(3) before any order is checked: per bits, the first 10 distinct
curve indices c in the order of the selected jobs as listed here (cells in the order bits, r, n), topped up
if fewer than 10 by c in ascending sha256("BATCH-924d2c|J2b|curves|" + str(bits) + "|" + str(c)) order over
c in [0, max n_curves at that bits) not already chosen.

Reads only cell, block, c and status of each record (no count field).
usage: python3 -I -B select_sample.py <toy-main-jobs.jsonl> <design.json> <out.json>
"""
import hashlib
import json
import sys

jobs_path, design_path, out_path = sys.argv[1:4]
with open(design_path) as f:
    design = {c["cell"]: c for c in json.load(f)["toy_cells"]}
ok = {}
for ln in open(jobs_path):
    if not ln.strip():
        continue
    r = json.loads(ln)
    key = {k: r[k] for k in ("cell", "block", "c", "status")}   # nothing else is read
    if key["block"] == "main" and key["status"] == "ok":
        ok.setdefault(key["cell"], set()).add(key["c"])


def h(cell, c):
    return hashlib.sha256(f"BATCH-924d2c|J2b|{cell}|{c}".encode()).hexdigest()


cells = []
for bits in (20, 24, 28):
    for r in (1, 2, 3):
        for n in (1024, 2048, 4096):
            cells.append(f"b{bits}-r{r}-n{n}")
    for n in (256, 512):
        cells.append(f"b{bits}-r{(bits % 3) + 1}-n{n}")
sample = []
for cell in cells:
    order = sorted(ok[cell], key=lambda c: h(cell, c))
    sample.append({"cell": cell, "c": order[0], "selection_hash": h(cell, order[0]),
                   "next_in_order": [{"c": c, "hash": h(cell, c)} for c in order[1:3]],
                   "ok_records_in_cell": len(order), "n_curves": design[cell]["n_curves"]})

curve_sample = {}
for bits in (20, 24, 28):
    chosen = []
    for s in sample:
        if s["cell"].startswith(f"b{bits}-") and s["c"] not in chosen:
            chosen.append(s["c"])
    how = ["from the selected jobs, in listed order"] * min(len(chosen), 10)
    chosen = chosen[:10]
    if len(chosen) < 10:
        cmax = max(c["n_curves"] for c in design.values() if c["bits"] == bits)
        extra = sorted((c for c in range(cmax) if c not in chosen),
                       key=lambda c: hashlib.sha256(f"BATCH-924d2c|J2b|curves|{bits}|{c}".encode()).hexdigest())
        while len(chosen) < 10:
            chosen.append(extra.pop(0))
            how.append("top-up by curves hash order")
    curve_sample[str(bits)] = [{"c": c, "source": w} for c, w in zip(chosen, how)]

out = {"rule": __doc__.split("usage:")[0].strip(), "jobs": sample, "job_count": len(sample),
       "curve_order_sample": curve_sample}
with open(out_path, "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print(len(sample), "jobs:", [(s["cell"], s["c"]) for s in sample])
print({b: [x["c"] for x in v] for b, v in curve_sample.items()})
