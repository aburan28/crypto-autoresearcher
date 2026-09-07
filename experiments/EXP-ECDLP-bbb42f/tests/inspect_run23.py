import json
from collections import Counter

for run in ("RUN-ECDLP-bbb42f-2", "RUN-ECDLP-bbb42f-3"):
    d = json.load(open(f"experiments/EXP-ECDLP-bbb42f/runs/{run}/results.json"))
    statuses = Counter(c["search"]["status"] for c in d["per_curve_results"])
    nodes = [c["search"]["nodes_visited"] for c in d["per_curve_results"]]
    bsgs_ok = all(c["baseline"]["bsgs"]["certificate_verified"] for c in d["per_curve_results"])
    rho_ok = all(c["baseline"]["rho"]["certificate_verified"] for c in d["per_curve_results"])
    anomalies = [c["anomaly"] for c in d["per_curve_results"] if c["anomaly"]]
    print(run, "statuses:", statuses, "nodes:", nodes, "bsgs_ok:", bsgs_ok, "rho_ok:", rho_ok, "anomalies:", anomalies)
