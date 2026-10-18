"""Layout only: plots values recorded in raw/scan/summary.json and raw/receipt-card-0N.json."""
import json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
S = json.load(open("raw/scan/summary.json"))
reasons = S["ecdlp_and_named_by_reason"]
order = sorted(reasons.items(), key=lambda kv: kv[1])
runs = []
for n, (rid, label) in zip(range(2, 6), [("RUN-ICPERF-943efa", "EXP-ICPERF-e467a5\nprice-ratio\nidentity"),
        ("RUN-PFDR-936605", "EXP-PFDR-ca5e01\nselftest"), ("RUN-XEDN-132272", "EXP-XEDN-0c0182\nprimary\nseed-20261016"),
        ("RUN-XEDN-f4d646", "EXP-XEDN-0c0182\nreplicate\nseed-20261017")]):
    r = json.load(open(f"raw/receipt-card-0{n}.json"))["commands"]
    runs.append((rid, label, r[1]["exit_code"], r[2]["exit_code"], r[1]["seconds"], r[2]["seconds"]))
json.dump({"reasons": reasons, "runs": runs}, open("report/graph-data.json", "w"), indent=1)
fig, (a, b) = plt.subplots(1, 2, figsize=(13, 5.6), gridspec_kw={"width_ratios": [1.25, 1]})
cols = ["#2a9d8f" if k in ("runnable", "partial") else "#8d99ae" for k, _ in order]
a.barh([k for k, _ in order], [v for _, v in order], color=cols)
for i, (k, v) in enumerate(order): a.text(v + 4, i, str(v), va="center", fontsize=9)
a.set_xlabel("contracts (count, N = %d ECDLP-class or named, at HEAD %s)" % (sum(reasons.values()), S["head"][:9]))
a.set_title("First blocking gate per contract (measured by scan)", fontsize=11)
a.set_xlim(0, 430)
x = range(len(runs)); w = 0.38
b.bar([i - w / 2 for i in x], [r[4] for r in runs], w, label="run command", color="#264653")
b.bar([i + w / 2 for i in x], [r[5] for r in runs], w, label="check command", color="#e9c46a")
for i, r in enumerate(runs):
    b.text(i - w / 2, r[4] + 0.02, "exit %d" % r[2], ha="center", fontsize=8)
    b.text(i + w / 2, r[5] + 0.02, "exit %d" % r[3], ha="center", fontsize=8)
b.set_xticks(list(x)); b.set_xticklabels([r[1] for r in runs], fontsize=7)
b.set_ylabel("wall seconds (descriptive, shared 4-vCPU host, n=1 each)")
b.set_title("Replica runs: exit codes and wall time", fontsize=11); b.legend(fontsize=8)
b.set_ylim(0, 1.0)
fig.suptitle("Blind-spot 18: frozen ECDLP contracts. 3 of 1029 runnable; 4 trials run, all exit 0 (run and check).\n"
             "Cards CARD-BLINDSPOT-18-01..05, commit e4b1f0d13. Level L0 host, replica records under raw/ (deviation D1).", fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.92))
fig.savefig("report/graph.svg"); fig.savefig("report/graph.png", dpi=150)
