"""Derive a planning inventory and plot already sealed ECTD arm receipts."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
REPORT_PATH = "experiments/EXP-ECTD-0cf008/reports/run-20261016T0409Z/data.json"
PHASES = ("collector", "count", "verify", "interval")
COLORS = {"collector": "#305f91", "count": "#cb5c40", "verify": "#528b5f", "interval": "#9a68aa"}


def git(*args: str) -> bytes:
    return subprocess.check_output(("git", "-C", str(ROOT), *args))


raw = git("show", "HEAD:" + REPORT_PATH)
source = json.loads(raw)
rows = []
for trial in source["trials"]:
    if trial["status"] != "output_validated":
        continue
    tree = git("ls-tree", "-r", "-l", "HEAD", trial["run_path"]).decode()
    blob_sizes = [int(line.split("\t", 1)[0].split()[3]) for line in tree.splitlines()]
    if not blob_sizes:
        raise ValueError("validated run lacks archived blobs")
    rows.append({"trial_id": trial["trial_id"], "run_id": trial["run_id"],
                 "status": trial["status"], "target_count": trial["targets_sampled"],
                 "wall_seconds": trial["wall_seconds"],
                 "phase_wall_seconds": {phase: trial["phase_wall_seconds"][phase] for phase in PHASES},
                 "phase_peak_rss_bytes": {phase: trial["phase_peak_rss_bytes"][phase] for phase in PHASES},
                 "archive_blob_bytes": sum(blob_sizes), "archive_blob_count": len(blob_sizes)})
rows.sort(key=lambda row: row["trial_id"])
if len(rows) != 3:
    raise ValueError("expected exactly three validated archived arms")

main = {"P29": {"vertices": 2049, "bases_per_vertex": 3, "targets_per_arm": 8192},
        "P37": {"vertices": 257, "bases_per_vertex": 3, "targets_per_arm": 2048}}
for item in main.values():
    item["arms"] = item["vertices"] * item["bases_per_vertex"]
    item["target_probes"] = item["arms"] * item["targets_per_arm"]
checks = {"P29": 2048 // 8 + 1, "P37": 256 // 4 + 1}
conditional = {}
for stratum, count in checks.items():
    quota = main[stratum]["targets_per_arm"]
    conditional[stratum] = {"check_vertices": count,
        "power_x_arms": count, "transport_and_u2_arms_if_both_full_quota": 2 * count,
        "additional_target_probes_if_all_three_full_quota": 3 * count * quota}
result = {
    "schema": "ectd-discovery-capacity-planning/v1",
    "scope": "derived planning inventory and three archived observations; no new trial or speed comparison",
    "source_report_path": REPORT_PATH,
    "source_report_sha256": hashlib.sha256(raw).hexdigest(),
    "source_run_commit": source["run_commit"],
    "validated_receipts": rows,
    "main_discovery": main,
    "main_arm_total": sum(item["arms"] for item in main.values()),
    "main_target_probe_total": sum(item["target_probes"] for item in main.values()),
    "conditional_control_inventory": conditional,
    "conditional_all_arm_total": sum(item["arms"] for item in main.values()) + 3 * sum(checks.values()),
    "conditional_all_target_probe_total": sum(item["target_probes"] for item in main.values()) +
        sum(item["additional_target_probes_if_all_three_full_quota"] for item in conditional.values()),
    "ambiguity": "The draft does not explicitly assign discovery target quotas to power_x, transported-base, and u2-native check arms; conditional totals require Coordinator specification.",
    "limit": "The three validated 32768-target arms are different curves/bases, and their phase wall times do not separate fixed pair-table setup from target probing. No per-arm or campaign wall-time extrapolation is qualified.",
}
(HERE / "data.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="520" viewBox="0 0 1000 520">',
    '<rect width="1000" height="520" fill="white"/>',
    '<style>text{font-family:Arial,sans-serif;fill:#243447;font-size:13px}.grid{stroke:#dbe4ed}.axis{stroke:#526579}</style>',
    '<text x="85" y="32" font-size="19" font-weight="bold">Archived ECTD phase wall times</text>',
    '<text x="85" y="54">Three validated 32,768-target arms; log scale, seconds. Different curves and bases.</text>',
]
y = lambda value: 420 - 330 * math.log10(value) / 3
for tick in (1, 10, 100, 1000):
    parts += [f'<line class="grid" x1="110" y1="{y(tick):.1f}" x2="940" y2="{y(tick):.1f}"/>',
              f'<text x="96" y="{y(tick)+4:.1f}" text-anchor="end">{tick}</text>']
parts.append('<text x="25" y="260" transform="rotate(-90 25 260)" text-anchor="middle">Phase wall time (s, log scale)</text>')
for i, row in enumerate(rows):
    center = 235 + 300 * i
    label = row["trial_id"].replace("-", " ")
    parts.append(f'<text x="{center}" y="455" text-anchor="middle">{label}</text>')
    parts.append(f'<text x="{center}" y="474" text-anchor="middle">{row["run_id"]}</text>')
    for j, phase in enumerate(PHASES):
        value = row["phase_wall_seconds"][phase]
        x = center - 48 + 32 * j
        parts.append(f'<circle cx="{x}" cy="{y(value):.1f}" r="7" fill="{COLORS[phase]}">'
                     f'<title>{row["trial_id"]} {phase}: {value:.3f} s</title></circle>')
for j, phase in enumerate(PHASES):
    x = 160 + 180 * j
    parts.append(f'<circle cx="{x}" cy="502" r="6" fill="{COLORS[phase]}"/>')
    parts.append(f'<text x="{x+12}" y="506">{phase}</text>')
parts.append('</svg>')
(HERE / "phase_wall.svg").write_text("\n".join(parts) + "\n")
print(json.dumps({"validated_receipts": len(rows), "main_arms": result["main_arm_total"],
                  "conditional_all_arms": result["conditional_all_arm_total"]}, sort_keys=True))
