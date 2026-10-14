#set page(paper: "a4", margin: (x: 17mm, y: 15mm), numbering: "1")
#set text(font: "DejaVu Sans", size: 9.5pt)
#set par(leading: 0.6em)
= 250-billion campaign launch
14 October 2026. Execution observations only: the campaign is running and the
study is incomplete. No interim significance test or security verdict.

*Measured:* 150,994,944 checked point observations in 16 of 27,133 chunks;
589,824 window observations and 262,144 start draws.
Zero failures / infrastructure stops. All completed chunks passed score replay
and separate coordinate-frame checks. Snapshot: 2026-10-14T14:41:33.286299+00:00.

#image("pipeline.svg", width: 86%)
#image("progress.svg", width: 100%)
Graph: exact recorded counters, not population-rate estimates; no uncertainty
interval applies. Source: publication/launch-20261014/progress-series.json.
Within-window points are dependent; named cohorts share starts.

#pagebreak()
= Fixed scope, retention and resumption
#table(columns: (2fr, 1.3fr, 1fr), inset: 5pt,
  [Population], [Planned windows/arm or model], [Arms/models],
  [P-192 motif], [44,389,200], [3],
  [P-224 parity], [44,389,200], [3],
  [P-224 long run], [177,556,850], [3],
  [Ordinary-prime controls], [1,420,454], [125])

*Derived prospective total:* 976,562,500 windows × 256 = 250,000,000,000 point
observations; 443,892,000 start draws. Selected / published / fresh random steps;
62 R + 63 C ordinary models. All 125 model preparations checked before launch.
Primes reused; coefficients and step x matched; group/step orders unmatched.

*Locked inference:* 18 exact paired contrasts + 2 approximate field comparisons;
alpha 0.0001/20, nominal 99.99% primary family with a field-approximation caveat.
Separate 30-rate CP family, nominal at least 99.99% under independent windows;
union nominal 99.98%, subject to the approximation. No final inference yet.
Analysis runs automatically only after exact completion; no outcome-based stopping.

*Aggregate retention:* exact counts, hashes and fixed full-coordinate samples.
Most individual bit strings/scalars are not retained for later arbitrary ML.
Full compact data require approximately 60–70 GB; initial free capacity was about
550 MB, with no configured managed AWS identity. Existing data remain intact.

*Measured runtime:* 506.049 completed-chunk CPU seconds, excluding
in-flight chunks. Three worker processes were active; detached PID 1168,
parent PID 1. Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0.
Unknown model/usage metadata remain null.

*Source pushed before sampling:* #text(size: 8pt)[068797c4d5d59c9e73531f751e820c9250fe7c9a].
Runtime dirty paths were only the new publication/preparation report; scientific
source was unchanged. See runtime.json, compile.json and manifest.json in
tasks/solinas_250b/publication/launch-20261014/.

*Standalone/resumable command:* tasks/solinas_250b/README.md. The identical command
and output path resume checksum-sealed chunks. Changed source/config/storage or
corruption is refused. The machine must remain active; the run is expected to take
days. No agent is needed per batch. This is not an ECDLP-cost or speedup claim.

*Evidence:* the launch snapshot and sealed chunk records in publication/launch-20261014/;
exact public parameters and full curve UIDs in tasks/solinas_250b/inputs.json;
protocol/power records in the same task; predecessor PR 2108. Internal sources,
read in this session. No canonical mechanism graph or official status changes.
Next: fixed completion, locked final analysis and a fresh final-results report.
