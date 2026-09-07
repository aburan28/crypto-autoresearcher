"""J3 (Red Team, TASK-20260906-a6b415): confirm every rho_T_8T / rho_T_16T
entry in the v2 analysis run's ci_tables.json is co-located (same JSON
object) with its frontier_tuple_item_d and CAP_2T_retention_item_f siblings
-- i.e. never reported as a bare ratio."""
import json

d = json.load(open("/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-612fb1/runs/"
                    "RUN-ECDLP-612fb1-v2-analysis-001/ci_tables.json"))
for cellkey, cell in d["cells"].items():
    for lab, entry in cell["per_T_sel"].items():
        keys = sorted(entry.keys())
        has_rho = "rho_T_8T" in keys
        has_frontier = "frontier_tuple_item_d" in keys
        has_cap = "CAP_2T_retention_item_f" in keys
        print(cellkey, lab, "rho_T_8T present:", has_rho,
              "frontier_tuple_item_d present:", has_frontier,
              "CAP_2T_retention_item_f present:", has_cap,
              "-> co-located:", has_rho and has_frontier and has_cap)
