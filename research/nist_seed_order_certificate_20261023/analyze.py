"""Summarize sealed n-1/n+1 factorization metrics without refitting features."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
RUN = HERE / "runs/certificate-20261023T1747Z"
assert (RUN / "complete.ok").read_text() == "verified\n"
verification_path = RUN / "verification.json"
rows = json.loads(verification_path.read_text())["rows"]
assert len(rows) == 41 and all(x["status"] == "verified" for x in rows)
curve_rows = [x for x in rows if x["label"] != "control"]
assert len(curve_rows) == 38

def field(name):
    if "192" in name:
        return 192
    if "239" in name:
        return 239
    if "224" in name:
        return 224
    return 256

table = []
for x in curve_rows:
    m = x["metrics"]
    table.append({"name": x["name"], "label": x["label"],
                  "curve_uid": x["curve_uid"], "field_bits": field(x["name"]),
                  "direction": "minus" if x["name"].endswith("_minus") else "plus",
                  "small_factor_bits_by_bound": {b: m["bounded"][b]["bits"] for b in ("1000", "10000", "100000", "1000000")},
                  "pocklington_size_by_bound": {b: m["bounded"][b]["pocklington_size_condition"] for b in ("1000", "10000", "100000", "1000000")},
                  "minimum_prime_power_components": m["minimum_prime_power_components"],
                  "largest_prime_at_crossing_bits": int(m["largest_prime_at_crossing"]).bit_length()})
assert not any(v for x in table for v in x["pocklington_size_by_bound"].values())

pairs = {}
for direction in ("minus", "plus"):
    per = {}
    for f in (192, 224, 239, 256):
        subset = [x for x in table if x["direction"] == direction and x["field_bits"] == f]
        pubs = [x for x in subset if x["label"] == "published"]
        omits = [x for x in subset if x["label"] == "omitted"]
        per[str(f)] = {"pairs": len(pubs)*len(omits),
                       "published_more_small_factor_bits": sum(p["small_factor_bits_by_bound"]["1000000"] > o["small_factor_bits_by_bound"]["1000000"] for p in pubs for o in omits),
                       "published_fewer_large_factor_bits": sum(p["largest_prime_at_crossing_bits"] < o["largest_prime_at_crossing_bits"] for p in pubs for o in omits)}
    pairs[direction] = per

analysis = {"verification_sha256": hashlib.sha256(verification_path.read_bytes()).hexdigest(),
            "rows": table, "within_field_pair_counts": pairs,
            "all_19_n_minus_one_F_1m_fail_pocklington_size": True,
            "all_19_n_plus_one_F_1m_fail_same_size_control": True}
(HERE / "analysis.json").write_text(json.dumps(analysis, indent=2, sort_keys=True)+"\n")

order = sorted((x for x in table if x["direction"] == "minus"),
               key=lambda x: (x["field_bits"], 0 if x["label"] == "omitted" else 1, x["name"]))
height = 80 + len(order)*30
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="780" height="{height}" viewBox="0 0 780 {height}">',
       f'<rect width="780" height="{height}" fill="white"/>',
       '<text x="20" y="27" font-family="sans-serif" font-size="20">Small proven factors of n-1, bound 1,000,000</text>',
       '<text x="20" y="47" font-family="sans-serif" font-size="12">Bits in their product; orange = omitted, blue = published. Every product remains below sqrt(n).</text>']
for i, x in enumerate(order):
    y = 64 + 30*i
    label = x["name"].replace("omitted_", "skip ").replace("published_", "pub ").replace("_minus", "")
    bits = x["small_factor_bits_by_bound"]["1000000"]
    color = "#d9843c" if x["label"] == "omitted" else "#5788c1"
    svg.append(f'<text x="20" y="{y+15}" font-family="monospace" font-size="13">{label}</text>')
    svg.append(f'<rect x="295" y="{y}" width="{bits*5}" height="19" fill="{color}"/>')
    svg.append(f'<text x="{305+bits*5}" y="{y+15}" font-family="sans-serif" font-size="13">{bits}</text>')
svg.append('</svg>')
(HERE / "smooth_bits.svg").write_text("\n".join(svg)+"\n")

dot = '''digraph Certificate {
  graph [rankdir=LR, bgcolor="white", labelloc=t,
    label="Pocklington-size proxy on 19 matched curves", fontsize=19];
  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=15];
  a [label="38 complete n-1 / n+1\\nfactorizations", fillcolor="#e1edff"];
  b [label="Every F_1M from n-1\\nis below sqrt(n)", fillcolor="#e4f4e7"];
  c [label="Published-vs-omitted\\nordering is mixed", fillcolor="#e4f4e7"];
  d [label="Original program used\\nthis certificate rule", style="dashed,rounded", fillcolor="white"];
  a -> b; a -> c; d -> c [style=dashed, label="unverified"];
}
'''
(HERE / "inference.dot").write_text(dot)
subprocess.run(["dot", "-Tsvg", str(HERE / "inference.dot"), "-o", str(HERE / "inference.svg")], check=True)
print(json.dumps(pairs, indent=2))
