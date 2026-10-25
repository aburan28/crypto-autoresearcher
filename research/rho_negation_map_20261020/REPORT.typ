#set page(paper: "a4", margin: 2cm)
#set text(size: 10pt)
#set table(stroke: 0.4pt)
= The negation map in `index_calculus.rho` (2026-10-20)

*Change.* `pollard_rho` used to walk on points ($A = 1$, $approx sqrt(pi N slash 2)$ steps). It now walks on ${X, -X}$ by default ($A = 2$, $approx sqrt(pi N slash 4)$), with the Wiener–Zuccherato look-ahead and a 16-point short-cycle escape by doubling, the same guards as crypto's matched reference. Look-ahead and escape additions are counted in `walk_ops`. `--rho-walk plain` (`negation=False`) is the old walk, bit-identical on 15 checked instances. Rows record `rho_walk`.

*Why.* A plain-walk rho is about $sqrt(2)$ too slow as a reference and flatters IC by $sqrt(2)$ (crypto audit X02/X03).

#figure(image("figures/negation_vs_plain.svg", width: 100%), caption: [`measure.py`, seed 20261020: 8 prime-order curves × 16 planted logs per size, both walks on each instance with the same seed; 1,280/1,280 verified. Right: ratio of mean `walk_ops`, 95% cluster bootstrap over curves.])

#table(columns: 8, align: right,
  [bits], [pairs], [neg / $sqrt(N)$], [/floor], [plain / $sqrt(N)$], [/floor], [plain/neg [95%]], [wall p/n],
  [16], [128], [0.991], [1.118], [1.435], [1.145], [1.448 [1.309, 1.608]], [1.024],
  [20], [128], [1.092], [1.232], [1.253], [0.999], [1.147 [0.978, 1.346]], [0.934],
  [24], [128], [1.124], [1.269], [1.478], [1.180], [1.315 [1.194, 1.418]], [0.981],
  [28], [128], [1.011], [1.140], [1.464], [1.168], [1.449 [1.285, 1.622]], [1.101],
  [32], [128], [1.069], [1.207], [1.525], [1.217], [1.426 [1.332, 1.519]], [1.085],
  [*all*], [640], [1.057], [1.193], [1.431], [1.142], [*1.353 [1.281, 1.425]*], [1.081],
)

- The pooled saving is 1.353; $sqrt(2)$ is at the top of the interval. The negation walk is 1.19× its floor and plain is 1.14×, so about 4% of $sqrt(2)$ is lost. The look-ahead accounts for 2.6% of additions and escapes for 0.07%.
- Table size (`jumps.py`, 384 solves each at 24–32 bits): r = 20, 32 and 64 give 1.183, 1.201 and 1.150× floor (s.e. 0.03). No clear difference; r stays 20.
- Wall time (descriptive, interpreted Python, shared VM): 1.08× pooled.
- Not changed: `harness/rho.py` and `harness/walk.py`. Companion study: aburan28/crypto `research/rho_negation_audit_20261020/` (ecbench `rho.negation` 1.371 [1.257, 1.491]; `volcano-rho` fixed the same way).
