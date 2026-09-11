import json
raw = json.load(open("experiments/EXP-ECDLP-6ac801/runs/RUN-ECDLP-6ac801-v3-n20-s01/raw-result.json"))
print("top keys:", list(raw.keys()))
for k, v in raw["cells"].items():
    print(k, "->", [kk for kk in v.keys()])
    break
c = raw["cells"]["a=0.062500"]
for kk, vv in c.items():
    if isinstance(vv, list):
        print(kk, "list len", len(vv), "first5", vv[:5])
    else:
        print(kk, "=", vv)
