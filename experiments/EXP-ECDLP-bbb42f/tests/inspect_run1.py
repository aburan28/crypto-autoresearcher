import json
from collections import Counter

d = json.load(open("experiments/EXP-ECDLP-bbb42f/runs/RUN-ECDLP-bbb42f-1/results.json"))
print("num curves processed:", len(d["per_curve_results"]))
statuses = [c["search"]["status"] for c in d["per_curve_results"]]
print(Counter(statuses))
ratios = [c["min_charged_transfer_ratio"] for c in d["per_curve_results"]]
print("ratios:", ratios[:6], "...")
bsgs_ok = [c["baseline"]["bsgs"]["certificate_verified"] for c in d["per_curve_results"]]
rho_ok = [c["baseline"]["rho"]["certificate_verified"] for c in d["per_curve_results"]]
print("bsgs cert all ok:", all(bsgs_ok), "rho cert all ok:", all(rho_ok))
anomalies = [c["anomaly"] for c in d["per_curve_results"] if c["anomaly"]]
print("anomalies:", anomalies)
nodes = [c["search"]["nodes_visited"] for c in d["per_curve_results"]]
print("nodes visited per curve:", nodes)
crater_closed = [c["search"]["crater_closed"] for c in d["per_curve_results"]]
print("crater_closed:", crater_closed)
