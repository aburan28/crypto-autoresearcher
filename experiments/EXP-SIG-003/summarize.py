# EXP-SIG-003 summarizer: aggregates all run receipts into summary.json
# (machine-readable link table + controls + the deficit/extra identity check).
import json
from pathlib import Path

EXP = Path("/Volumes/Volume/crypto-autoresearcher/experiments/EXP-SIG-003")

cells = {}
for run_dir in sorted((EXP / "runs").glob("RUN-EXP-SIG-003-*")):
    raw_p = run_dir / "raw.json"
    if not raw_p.exists():
        continue
    raw = json.loads(raw_p.read_text())
    if raw.get("kind") == "determinism_compare":
        cells.setdefault("determinism", []).append({
            "run": run_dir.name, "run_a": raw["run_a"], "run_b": raw["run_b"],
            "identical": raw["identical"]})
        continue
    c = raw.get("cell")
    if not c:
        continue
    key = (c["n"], c["seed"], c["arm"])
    entry = {
        "run": run_dir.name, "status": c.get("status"),
        "standard": c.get("filter", {}).get("standard"),
        "nb": c.get("nb"),
        "wall_seconds": raw.get("wall_seconds"),
        "controls": c.get("controls"),
    }
    for D in ("D3", "D4", "D5"):
        if D in c:
            r = c[D]
            entry[D] = {k: r[k] for k in
                        ("nrows", "ncols", "rank", "sr_pred", "deficit",
                         "kernel_dim", "rankK", "extra")}
    if "v3_multiples_at_D4" in c:
        entry["residual_4"] = c["v3_multiples_at_D4"]["residual_new_at_D4"]
        entry["rank_v3mod_K4"] = c["v3_multiples_at_D4"]["rank_mod_K4"]
    if "link" in c:
        entry["link"] = c["link"]
    cells.setdefault("by_cell", {})[str(key)] = entry

# identity check: deficit_5 = extra_5 + rankK5_sem - rankK5_null
identity = []
by = cells.get("by_cell", {})
for (n, seed), sem in [((12, 2), "12,2"), ((15, 1), "15,1"), ((12, 2026), "12,2026")]:
    sem_e = by.get(str((n, seed, "sem")))
    null_e = by.get(str((n, seed, "null")))
    if sem_e and null_e and "D5" in sem_e and "D5" in null_e:
        rhs = sem_e["D5"]["extra"] + sem_e["D5"]["rankK"] - null_e["D5"]["rankK"]
        identity.append({
            "n": n, "seed": seed,
            "deficit_5": sem_e["D5"]["deficit"],
            "extra_5": sem_e["D5"]["extra"],
            "rankK5_sem": sem_e["D5"]["rankK"],
            "rankK5_null": null_e["D5"]["rankK"],
            "identity_rhs": rhs,
            "identity_holds": sem_e["D5"]["deficit"] == rhs,
        })
cells["deficit_extra_identity"] = identity

out = EXP / "summary.json"
out.write_text(json.dumps(cells, indent=1) + "\n")
print("wrote", out)
for k, e in sorted(cells.get("by_cell", {}).items()):
    l = e.get("link") or {}
    print(k, e.get("status"), "std=%s" % e.get("standard"),
          "D5def=%s extra=%s A3=%s A4=%s resid5=%s cov=%s" % (
              (e.get("D5") or {}).get("deficit"), l.get("extra_5"),
              l.get("A3"), l.get("A4"), l.get("residual_5"),
              l.get("coverage_vs_deficit")))
for i in identity:
    print("identity n=%d seed=%d: deficit=%d rhs=%d holds=%s" % (
        i["n"], i["seed"], i["deficit_5"], i["identity_rhs"], i["identity_holds"]))
