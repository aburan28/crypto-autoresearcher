# Held-out graph confirmation candidate

This directory contains a candidate analyzer, pure controls, and one tooling
benchmark. It contains no graph-wide discovery or confirmation measurements.
The Coordinator must approve and freeze a runnable confirmation trial plan,
including the hashes of `confirm.py`, the exact interval implementation, the
discovery selection, and the graph schedule, before fresh confirmation data
are collected. The plan must enumerate every selected `low_x`, `mid_x`, and
`random_x` arm once, with 32,768 targets per arm.

The analyzer refuses any missing, failed, or censored arm. It binds each
supervisor receipt to the graph-attempt receipt, prepared input, independent
checker output, curve identity, target coefficient stream, graph-specific
commitment, and fixed rank prefixes. It requires the same coefficient stream
within each stratum and a fresh target root distinct from discovery. The base,
target, and verifier root hashes are shared across strata within a stage; the
commitment-file hashes differ across strata and between stages. Exact
hypergeometric intervals invert integer tails over the `r-1` nonidentity
points. With at most 294 arms and two tails per arm, the per-tail threshold
`1/(200 M)` gives at least 99% simultaneous coverage by Bonferroni. Interval
cells are write-once and digest-bound for interruption recovery.

Finalist rules are deterministic within each stratum: source, greatest and
least confirmed `low_x` useful-target counts, greatest and least confirmed
`low_x/random_x` point ratios, and lower median `low_x`. Ties use the smaller
`j`. A zero denominator with positive numerator ranks as infinity. A 0/0
ratio is undefined and excluded from ratio extrema, while its vertex remains
eligible under source and yield rules. The output retains all counts,
intervals, ratios, receipt digests, and up to six distinct `j` finalists per
stratum. A ratio's conservative interval uses the marginal simultaneous
count bounds; it is descriptive and does not independently establish an
end-to-end ECDLP speedup.

Run the pure controls with:

```sh
python3 -m unittest research/isogeny_relation_yield_scan_20261016/graph_confirmation_candidate_20261023/test_confirm.py -v
```

After a frozen plan and all receipts exist, invoke:

```sh
python3 research/isogeny_relation_yield_scan_20261016/graph_confirmation_candidate_20261023/confirm.py \
  --repo . --selection PATH --schedule PATH --plan PATH \
  --cache-dir PATH --out PATH
```

The cache and output paths must be fresh, durable destinations under the
approved write scope. The implementation benchmark is described in
[`report.md`](report.md); its synthetic observed count is a workload parameter,
not a relation-yield observation. The later complete same-point ECDLP/rho
stage remains a separate experiment.
