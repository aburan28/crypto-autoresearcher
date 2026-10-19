"""Writes table.typ from RUN-ENDO-d7cb69's recorded rows (derived values only: % = 100 x recorded fraction)."""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
rows = json.loads((HERE.parents[1] / "runs" / "RUN-ENDO-d7cb69" / "raw-result.json").read_text())["rows"]
sel = [r for r in rows if r["role"].startswith("control")] + [
    r for r in rows if r["role"] == "population" and (r["best"] or {}).get("persistent_gain", -1) > 0
    or (r["role"] == "population" and r["baseline"]["note"].startswith(("general a", "small a")))]
seen, out = set(), []
for r in sel:
    if r["name"] in seen: continue
    seen.add(r["name"]); b = r["best"]; v = r["verification"]; a = r["ascent"]
    pct = lambda x: "" if x is None else f"{100 * x:+.2f}"
    out.append([r["name"], r["role"], str(r["bits"]), r["baseline"]["kind"], f"{r['baseline']['M_eq']:.1f}",
                str(r["nodes"]), "·".join(map(str, b["path"])) if b else "–", pct(b and b["persistent_gain"]),
                pct(b and b["persistent_gain_s08"]), pct(b and b["oneshot_gain"]),
                "–" if v is None else (f"ok ({v['checked']})" if v["ok"] else "FAIL"),
                "–" if a["D_K"] is None else str(a["D_K"])])
esc = lambda s: s.replace("#", "\\#").replace("*", "\\*").replace("_", "\\_").replace("@", "\\@").replace("$", "\\$")
cells = ",\n".join(", ".join(f"[{esc(c)}]" for c in row) for row in out)
(HERE / "table.typ").write_text(
    "#table(columns: 12, inset: 3pt, stroke: 0.4pt + luma(200), align: (left, left, right, left, right, right, left, right, right, right, left, right),\n"
    "[*curve*], [*role*], [*bits*], [*best model on E*], [*E M_eq*], [*nodes*], [*path*], [*persist. %*], [*persist. % S=0.8M*], [*one-shot %*], [*verified (k)*], [*D_K*],\n"
    + cells + ")\n")
print(len(out), "rows")
