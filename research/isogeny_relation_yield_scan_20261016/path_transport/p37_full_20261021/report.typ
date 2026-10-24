#set page(paper: "us-letter", margin: 0.7in)
#set text(font: "Arial", size: 9pt)
= P37 source-base transport through edge 256
#text(size: 8pt)[Observation-only implementation control, 2026-10-22. No relation targets were collected.]

== Exact input and output
P37 over $F_81640512137$, prime group order 81640511861. Source model $y^2=x^3+46677163888x+11713815639$; 1,600 x-orbits and 3,200 signed base points. The archived walk has 256 degree-7 edges. The valid run resumed from edge 28 and wrote edges 29–256 under Conductor task T-4626. The terminal canonical model has $a=56138620881$, $b=30636729625$, $j=15565187709$. Terminal checkpoint SHA-256: `03da8071ed1639204ee415496361755855e4a3db72fa2781fc9135e5ad0aa262`.

== Recorded observations
Producer: 228 new checkpoints, 182.51 s wall, 372,129,792 bytes maximum RSS. Independent verifier: pass, 256 edges, 819,200 signed-base point images replayed, 9.94 s wall. The first lease attempt went stale; its 129 uncommitted checkpoints and logs were preserved separately and excluded from the valid chain. These timings describe path preparation on this host and make no ECDLP-cost comparison.

#figure(image("edge_times.svg", width: 100%), caption: [Saved producer time per edge, in seconds. Blue: earlier archived edges 1–28. Red: valid restarted edges 29–256. Task T-4626.])

== Remaining work
The map chain is checked under independent arithmetic replay. Native factor bases, fixed targetwise relations, useful rank, and full same-point ECDLP costs remain to be measured by an admitted experiment. Exact commands, hashes, failed-attempt record, and raw logs are in the accompanying Markdown report.
