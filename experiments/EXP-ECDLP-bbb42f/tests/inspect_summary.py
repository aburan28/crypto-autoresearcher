import json

d = json.load(open("experiments/EXP-ECDLP-bbb42f/results/summary.json"))
print(json.dumps(d["primary_metrics"], indent=2)[:2000])
print("---runs---")
for k, v in d["runs"].items():
    print(k, {kk: vv for kk, vv in v.items() if kk not in ("outcomes", "configs")})
