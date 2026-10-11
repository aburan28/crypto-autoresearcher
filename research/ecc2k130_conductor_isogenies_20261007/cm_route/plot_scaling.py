# polclass (Weber f) wall time vs |D| = 7 f^2, from scale_polclass.out (one run per point, 4-core container).
import re, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
rows = [tuple(map(int, m)) for m in re.findall(r"f=(\d+) h=(\d+) \|D\|=(\d+)\s+polclass (\d+) s", open("scale_polclass.out").read())]
f, h, D, t = map(np.array, zip(*rows))
k, c = np.polyfit(np.log(D), np.log(t), 1)
Dx = np.logspace(np.log10(D.min()) - 0.1, np.log10(7 * 120871**2) + 0.1, 50)
fig, ax = plt.subplots(figsize=(6.4, 4))
ax.loglog(D, t, "o", color="#1f5fa8", label="measured (1 run each)")
ax.loglog(Dx, np.exp(c) * Dx**k, "--", color="#888888", label=f"fit t ∝ |D|^{k:.2f} (3 points)")
De = 7 * 120871**2; te = np.exp(c) * De**k
ax.loglog([De], [te], "s", mfc="none", color="#a07d1f", label=f"m=51, f=120871: extrapolated {te/3600:.1f} h")
for fi, Di, ti in zip(f, D, t): ax.annotate(f"f={fi}", (Di, ti), textcoords="offset points", xytext=(5, -10), fontsize=8)
ax.set_xlabel("|D| = 7 f²"); ax.set_ylabel("polclass(D, 1) wall time [s]")
ax.set_title("CM route cost: class polynomial over Z (PARI 2.15)", fontsize=10); ax.legend(fontsize=8); ax.grid(True, which="both", alpha=0.3)
fig.tight_layout(); fig.savefig("polclass_scaling.svg"); fig.savefig("polclass_scaling.png", dpi=120)
print(f"exponent {k:.2f}; extrapolated f=120871: {te:.0f} s = {te/3600:.1f} h")
