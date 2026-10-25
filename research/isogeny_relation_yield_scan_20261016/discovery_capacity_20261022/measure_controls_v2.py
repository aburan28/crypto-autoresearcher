"""Correct the conditional control inventory without changing v1 planning data."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
old_path = HERE / "data.json"
old = json.loads(old_path.read_text())
if old["main_arm_total"] != 6918 or old["main_target_probe_total"] != 51935232:
    raise ValueError("main discovery inventory differs")

controls = ["power_x", "graph_transported_source_low_x", "u2_native_low_x", "u2_transport_oracle"]
strata = {}
for stratum, checks in (("P29", 257), ("P37", 65)):
    quota = old["main_discovery"][stratum]["targets_per_arm"]
    strata[stratum] = {"check_vertices": checks, "targets_per_full_quota_arm": quota,
                       "proposed_distinct_controls": controls,
                       "three_control_arms": checks * 3,
                       "four_control_arms": checks * 4,
                       "three_control_target_probes": checks * 3 * quota,
                       "four_control_target_probes": checks * 4 * quota}
three_arms = old["main_arm_total"] + sum(x["three_control_arms"] for x in strata.values())
four_arms = old["main_arm_total"] + sum(x["four_control_arms"] for x in strata.values())
three_probes = old["main_target_probe_total"] + sum(x["three_control_target_probes"] for x in strata.values())
four_probes = old["main_target_probe_total"] + sum(x["four_control_target_probes"] for x in strata.values())
if (three_arms, four_arms, three_probes, four_probes) != (7884, 8206, 58650624, 60889088):
    raise ValueError("conditional control arithmetic differs")
result = {"schema": "ectd-discovery-control-inventory/v2",
          "status": "prospective_unapproved",
          "v1_data_sha256": hashlib.sha256(old_path.read_bytes()).hexdigest(),
          "correction": "v1's three-control scenario did not separately enumerate the u2 transported-base oracle from the graph-transported source base",
          "main_arms": old["main_arm_total"], "main_target_probes": old["main_target_probe_total"],
          "strata": strata,
          "three_control_scenario": {"meaning": "power_x, graph-transported source base, and u2 native base each run at full discovery quota; coordinate transport checked without a separate full-quota arm",
                                     "arms": three_arms, "target_probes": three_probes},
          "four_control_scenario": {"meaning": "all four named controls each run as a separate full-quota arm",
                                    "arms": four_arms, "target_probes": four_probes},
          "admission_gap": "Coordinator must fix whether the u2 transported-base oracle is a full-quota collector arm and fix every check-arm quota before approval; neither scenario is an observed workload or an approved schedule"}
(HERE / "control-inventory-v2.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps({"three_control_arms": three_arms, "four_control_arms": four_arms,
                  "three_control_probes": three_probes, "four_control_probes": four_probes}, sort_keys=True))
