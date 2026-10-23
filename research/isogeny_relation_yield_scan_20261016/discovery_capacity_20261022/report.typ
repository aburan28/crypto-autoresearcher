#set page(paper: "us-letter", margin: 0.65in)
#set text(font: "Arial", size: 9pt)
= Graph-wide discovery capacity and admission gap
#text(size: 8pt)[Planning assessment, 2026-10-22. Derived inventory and archived observations only; no new scientific trial.]

== Fixed inventory and open quota
The prospective P29/P37 schedule has 2,049 and 257 vertices. Three native bases on every vertex give *6,918 mandatory discovery arms* and *51,935,232 target probes*: P29 has 6,147 arms at 8,192 targets each; P37 has 771 arms at 2,048 each. Check indices add 257 P29 and 65 P37 vertices. If `power_x`, transported, and `u=2` arms each receive the full discovery quota, the conditional inventory is *7,884 arms* and *58,650,624 probes*. The draft does not explicitly fix those check-arm quotas; the Coordinator must do so before admission.

A machine-readable plan now binds the 6,918 main rows to exact archived models and generators, base rules and quotas. Independent point arithmetic checked all 2,306 generator identities and group-order multiplications. Main-arm SHA-256: `bf436f6a3df707b799cb738ed0522aa2a0fa68e921afd6d8099bf929d94105ef`. This plan has no seed or target points and is unapproved.

== Three archived 32,768-target observations
P29 E2 native (`RUN-ECTD-c769f1`) recorded 68.37 s wall; P29 E3 native (`RUN-ECTD-f395a9`) 77.68 s; P37 floor `u=2` native (`RUN-ECTD-26d06d`) 952.04 s. These are different curves and bases in a separate 20-arm study. The graph shows their measured collector, count, replay, and interval phase times in seconds. Pair-table setup and target probing were not separated, so no full-scan runtime is inferred.

#figure(image("phase_wall.svg", width: 100%), caption: [Archived phase wall times on a logarithmic seconds axis. Three output-validated records at 32,768 targets each; run IDs are shown under the marks.])

== Next gate
Freeze the check-arm quotas and implementation/seed commitments, then obtain a runnable Coordinator-approved collector contract. The configured Coordinator backend remains unavailable in the current adapter probe. The graph's native yield, useful rank, and full same-point ECDLP costs remain unmeasured. Source paths, exact derived counts, receipt values, and limits are in the accompanying Markdown report and data file.
