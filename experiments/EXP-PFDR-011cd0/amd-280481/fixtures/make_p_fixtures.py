"""AMD-20261002-280481 A-3 fixture cases P1 and P2: synthetic EXP-PFDR-1b78f7-like archives
built from the toy A2 archive of fixtures/make_fixtures.py (12-14-bit curves c in {0, 1}; no
panel file, no census curve).

m = 3 and m = 5: relabelled exactly as fixture C (12 -> 30, 14 -> 32 bits).
m = 4: every A2 instance is copied to every even rung b = 12..32 (source bits 12 when b % 4 == 0,
else 14), harvest rows relabelled with it and written contiguously per instance.
  P1: at rungs 26..32 the SS harvest rows of every m = 4 instance are dropped (no SS row is
      retained, rows_emitted > 0), so (SS, 4) has no complete instance at 26-32 and every
      instance is complete at 12-24.  Expected selection {22, 24}.
  P2: the SS harvest rows of every m = 4 instance are dropped at every rung except 24, so
      exactly one rung qualifies.  Expected: P0 exits non-zero and writes no design.json.
Fixture C's bundles.jsonl, curves.jsonl.gz and fake-spec.yaml are reused unchanged."""
import gzip, json, os, shutil, sys
from collections import OrderedDict

FX, case = sys.argv[1], sys.argv[2]
src = os.path.join(FX, "A2", "runs")
dst = os.path.join(FX, case, "runs")
if os.path.exists(os.path.join(FX, case)):
    raise SystemExit(f"refusing: {FX}/{case} exists")
REL = {12: 30, 14: 32}

def read(p):
    with gzip.open(p, "rt") as fh:
        return [json.loads(l) for l in fh if l.strip()]

def write(p, recs):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with gzip.open(p, "wt") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")

def k5(r, m=None):
    # harvest rows carry "m"; instance rows carry it only through method "ic_m<m>"
    mm = r.get("m", m)
    if mm is None and str(r.get("method", "")).startswith("ic_m"):
        mm = int(r["method"][4:])
    return (r["bits"], r["curve"], mm, r["arm"], r["mode"])

# m = 3: root rows + harvest rows (as C)
for f in ("rows.jsonl.gz", "harvest-rows.jsonl.gz"):
    recs = read(os.path.join(src, "RUN-PFDR-1b78f7-census-m3", f))
    for r in recs:
        r["bits"] = REL.get(r["bits"], r["bits"])
    write(os.path.join(dst, "RUN-PFDR-1b78f7-census-m3", f), recs)

def layout(m, rows, hrows):
    sub = "RUN-PFDR-1b78f7-census-m4/merged" if m == 4 else "RUN-PFDR-1b78f7-census-m5"
    d = os.path.join(dst, sub)
    write(os.path.join(d, "rows.jsonl.gz"), rows)
    hp = os.path.join(dst, sub.split("/")[0], "attempt-1", "jobs", "all", "harvest-rows.jsonl.gz")
    write(hp, hrows)
    hmap = {json.dumps(["main", m, r["bits"], r["curve"], r["arm"], r["mode"]]): {"harvest_rows_file": hp, "sha256": None}
            for r in rows}
    json.dump({"harvest_rows_map": hmap}, open(os.path.join(d, "merge-report.json"), "w"))

# m = 5 (as C)
rows5 = read(os.path.join(src, "RUN-PFDR-1b78f7-census-m5", "rows.jsonl.gz"))
h5 = read(os.path.join(src, "RUN-PFDR-1b78f7-census-m5", "attempt-1", "jobs", "all", "harvest-rows.jsonl.gz"))
for r in rows5 + h5:
    r["bits"] = REL.get(r["bits"], r["bits"])
layout(5, rows5, h5)

# m = 4: copies at every even rung
rows4 = read(os.path.join(src, "RUN-PFDR-1b78f7-census-m4", "merged", "rows.jsonl.gz"))
h4 = read(os.path.join(src, "RUN-PFDR-1b78f7-census-m4", "attempt-1", "jobs", "all", "harvest-rows.jsonl.gz"))
by = OrderedDict()
for h in h4:
    by.setdefault(k5(h), []).append(h)
drop_rungs = set(range(26, 33, 2)) if case == "P1" else set(range(12, 33, 2)) - {24}
new_rows, new_h, dropped = [], [], 0
for b in range(12, 33, 2):
    sb = 12 if b % 4 == 0 else 14
    for r in rows4:
        if r["bits"] != sb:
            continue
        nr = json.loads(json.dumps(r)); nr["bits"] = b
        assert nr["harvest"]["SS"]["at_stop"]["rows_emitted"] > 0
        new_rows.append(nr)
        for h in by.get(k5(r, 4), []):
            if h["class"] == "SS" and b in drop_rungs:
                dropped += 1
                continue
            nh = dict(h); nh["bits"] = b
            new_h.append(nh)
layout(4, new_rows, new_h)
for f in ("bundles.jsonl", "curves.jsonl.gz", "fake-spec.yaml"):
    shutil.copy(os.path.join(FX, "C", f), os.path.join(FX, case, f))
print(json.dumps({"case": case, "m4_instances": len(new_rows), "m4_harvest_rows": len(new_h),
                  "ss_rows_dropped": dropped, "drop_rungs": sorted(drop_rungs)}))
