import json
from collections import Counter

d = json.load(open("experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-3/results.json"))
statuses = Counter(c["search"]["status"] for c in d["per_curve_results"])
nodes = [c["search"]["nodes_visited"] for c in d["per_curve_results"]]
crater_closed = [c["search"]["crater_closed"] for c in d["per_curve_results"]]
print("statuses:", statuses)
print("nodes:", nodes)
print("crater_closed:", crater_closed)
bsgs_ok = all(c["baseline"]["bsgs"]["certificate_verified"] for c in d["per_curve_results"])
rho_ok = all(c["baseline"]["rho"]["certificate_verified"] for c in d["per_curve_results"])
print("bsgs_ok:", bsgs_ok, "rho_ok:", rho_ok)
anomalies = [c["anomaly"] for c in d["per_curve_results"] if c["anomaly"]]
print("anomalies:", anomalies)
