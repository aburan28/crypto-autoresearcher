"""Draw the recorded stage-0 allocator probe for EXP-BINSTD-a33de2 (RUN-BINSTD-113958).

Values are copied from the runner's stage0/preregistered-predictions.json; nothing is
recomputed. Stage 1 did not run."""
import json, pathlib
import matplotlib; matplotlib.use("svg")
import matplotlib.pyplot as plt
here = pathlib.Path(__file__).parent
d = json.loads((here / "data.json").read_text()); pr = d["allocator_probe"]
mib = 1 << 20
x = [p["size"] / mib for p in pr]
fig, ax = plt.subplots(figsize=(6, 3.4))
ax.plot(x, [p["delta_rss_bytes"] / mib for p in pr], "o-", label="recorded delta_rss")
ax.plot(x, x, ":", color="gray", label="allocation size (reference y=x)")
ax.set_xlabel("allocation size (MiB)"); ax.set_ylabel("recorded delta RSS (MiB)")
ax.set_title("RUN-BINSTD-113958 stage-0 allocator probe (n=3 sizes)"); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(here / "allocator-probe.svg")
