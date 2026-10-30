# EXP-PFDR-bb0d26 analysis (REVIEW-PFDR-bb0d26-20261029)

Composed by the Coordinator under TASK-20261029-5a5213 from the three reviewer reports of
REVIEW-PFDR-bb0d26-20261029 and the hash-bound `analysis.json` of RUN-PFDR-089edc. No run was launched for
this analysis. Evidence record: EV-PFDR-07d608. Decision: DEC-20261029-01405d. Toy scope only.

## Observation

O1. Run set. There are exactly five run directories, in plan order: RUN-PFDR-e44a19 (selftest),
RUN-PFDR-4d8c71 (census-toy-main), RUN-PFDR-243425 (analyze-main), RUN-PFDR-cd03e2 (census-toy-rep) and
RUN-PFDR-089edc (analyze-final). All five were executed on 2026-10-23 at authority commit 48bd193a with a
clean tree and CPython 3.11.15. 53 of 53 receipt-named files recompute to their recorded sha256. Code and
plan hashes equal the frozen trial plan, and `implementation/` is byte-unchanged from 48bd193a to the
snapshot 1eddb474. `check.py` exits 0 on all five under 3.11.15. All 1580 distinct curves equal
`generate_prime_order_curve(bits, 8100000 + c)`. There are 6657 job records (one per planned key): 6653 ok,
4 degenerate and 0 failed_infrastructure (validator report TASK-20261029-958053, J2).

O2. Citability. DEC-20261029-5554ee rules RUN-PFDR-e44a19, RUN-PFDR-4d8c71 and RUN-PFDR-cd03e2 citable as
recorded. It rules RUN-PFDR-243425 and RUN-PFDR-089edc *scoped*, because no exact audit replay had been made
of them. In this round J1 made that replay, as an audit replay under CPython 3.11.15 (uv build,
`/root/.local/share/uv/python/cpython-3.11.15-linux-x86_64-gnu/bin/python3.11`). analyze-main,
analyze-final, selftest and census-toy-rep reproduced every measurement output byte for byte
(analysis.json sha256 95defc5b...). Only `manifest.yaml` differs, in 11 execution-provenance leaves. The
float tolerance of DEC-20261029-5554ee was never needed. The 3.13.17 control reproduced the audit's drift:
2 summary float leaves (416 and 402 ulps) and 479 analysis float leaves, all within rel 1e-9, with no
non-float leaf. The scoped ruling of DEC-20261029-5554ee stands as recorded. This analysis does not
overturn it.

O3. Kernel. A disjoint brute-force recount of 15 nonce-sampled ok jobs plus the 4 degenerate jobs covered
all three arms, bits 20/24/28, r 1/2/3, and 10 jobs with n >= 1024. Its own affine curve arithmetic
reproduced every log-GAP label set, and 838 of 838 fields equal the record (J3).

O4. Recorded reading (RUN-PFDR-089edc analysis.json, stage final):
- outcome O-NULL and headline SUPPORT_SCOPED
- calibration n 44, mean -0.26757013662385903, sd 0.9735699770654103, pass true
- fraction_valid 0.9777777777777777, flagged_cells [] and powered_cells 44
- plant_infeasible_cells [] and null_mean_anomalies []

44 cells are class null. b20-r3-n4096 is class invalid (46 of 50 curves ok), with S, M, kappa, z and
powered all null. Over the 44 powered cells:
- The largest |kappa - 1| is 0.04140 (b28-r1-n256, kappa 1.04140, ci95 [1.00996, 1.07428]).
- The lowest ci95 bound is 0.93684 (b28-r2-n512) and the highest is 1.07428 (b28-r1-n256).
- The largest |z| is 3.131 (b24-r1-n2048).
- The smallest plant_kappa is 1.28852 (b20-r2-n4096) and the smallest plant_z is 21.93 (b24-r2-n256).
- At n >= 1024, |kappa - 1| <= 0.0089 (b28-r3-n1024). At n >= 2048, it is <= 0.0025 (b28-r2-n2048).
- The secondary log-kappa slopes per (bits, r) all have |slope| <= 0.0088 (b28-r1).
- The census-toy-rep run has 0 jobs and a 0-byte jobs file, as the frozen stopping rule requires when no
  cell is flagged.

O5. Invalid cell. Four jobs of b20-r3-n4096 are degenerate: c = 6, 30, 42 and 47. In each, the three
seeded base points satisfy a short integer relation of sup-norm 8 to 14: (5, 2, -14), (13, 9, -8),
(1, -11, 5) and (4, -8, 3). The relation forces exactly the recorded duplicate skips, so the half-box
H(3, 10) is exhausted below 4096 distinct labels (3566, 4006, 3030 and 2641). For those curves no null or
plant set was built. Every one of the 6653 ok jobs records duplicate_skips 0 (J2, J3; red team Q3).

O6. Unpreregistered dispersion of the log-GAP z (blind F1, red team O3). Over the 44 powered cells the
log-GAP z values have mean 0.175, population sd 1.262 and sum of z^2 = 71.43 on 44 (upper tail about
0.006 under independence). I recomputed 71.43 from the recorded z values of analysis.json. Six cells have
|z| > 2 against 2.0 expected: b20-r1-n4096, b20-r3-n256, b24-r1-n2048, b24-r3-n2048, b28-r1-n256 and
b28-r2-n512. The same six intervals exclude 1. The null-vs-null arms show none of this: z_cal has sum of
z^2 = 44.9 on 44 (p 0.44), and even/odd has 40.5 on 44 (p 0.62). The per-curve variance of the gap arm
matches the null (blind diagnosis: variance ratio 0.955; red team: pooled t^2 difference -0.034, CI
[-0.097, 0.029]). The excess therefore comes from cell-level shifts of mixed sign. These shifts do not
repeat across bits for the same (r, n): r1-n2048 gives z 0.46, -3.13 and -0.16 at 20, 24 and 28 bits.

O7. Controls. The planted AP read flagged under the frozen class rule in 44 of 44 powered cells; the
lowest reviewer-bootstrap lower bound is 1.2877. The A/A null (replicate 0 against 1..19) gave 0 of 44
cells flagged and 44 null; its leave-one-replicate-out version gave 0 of 880 flagged. The even/odd A/A
gave 0 of 44 flagged and 2 intermediate (b24-r1-n256, b24-r3-n256). The scaling identity (C-aa-scale)
passed in the selftest, scaling-identity:0 to :11, replayed byte-identically (red team proves_too_much;
J1).

O8. Execution proof. The run report and DEC-20261022-9aec2b record 0 verified execution proofs, with the
docs/execution-proof-chain.md milestones open.

## Comparison

C1. Blind re-derivation (TASK-20261029-e5fe6b, from the specification, the hypothesis and the job records
only) against the recorded reading (RUN-PFDR-089edc), cell by cell. Every S agrees exactly, and so does
M to the two printed decimals. kappa agrees to all six printed decimals, z and z_cal to all three, and the
class matches in every cell. The blind ci95 uses the re-deriver's own declared bootstrap seed. The
specification does not fix a seed derivation (blind U4), so ci95 endpoints are compared with a Monte Carlo
tolerance, not exactly. The largest endpoint difference is 0.0034 (b24-r2-n256 upper: 1.02189 recorded
against 1.02526 blind). That is inside the re-deriver's own spread across seed and quantile variants
(<= 0.0039), and no endpoint lies within 0.024 of the [0.90, 1.10] band, so no class can move.

| cell | curves | kappa (rec = blind, 6 dp) | z (rec = blind) | ci95 recorded | ci95 blind | max endpoint diff | class rec / blind |
|---|---|---|---|---|---|---|---|
| b20-r1-n256 | 50 | 0.999881 | -0.022 | [0.99008, 1.00967] | [0.99045, 1.00942] | 0.0004 | null / null |
| b20-r1-n512 | 50 | 0.998825 | -0.861 | [0.99589, 1.00171] | [0.99601, 1.00155] | 0.0002 | null / null |
| b20-r1-n1024 | 50 | 1.000323 | 0.966 | [0.99974, 1.00093] | [0.99973, 1.00090] | < 0.0001 | null / null |
| b20-r1-n2048 | 50 | 1.000038 | 0.455 | [0.99988, 1.00020] | [0.99988, 1.00021] | < 0.0001 | null / null |
| b20-r1-n4096 | 50 | 0.999951 | -2.321 | [0.99991, 0.99999] | [0.99991, 1.00000] | < 0.0001 | null / null |
| b20-r2-n256 | 50 | 1.003223 | 0.594 | [0.99250, 1.01391] | [0.99350, 1.01406] | 0.0010 | null / null |
| b20-r2-n512 | 50 | 0.999091 | -0.692 | [0.99663, 1.00155] | [0.99653, 1.00170] | 0.0002 | null / null |
| b20-r2-n1024 | 50 | 0.999840 | -0.481 | [0.99910, 1.00059] | [0.99910, 1.00061] | < 0.0001 | null / null |
| b20-r2-n2048 | 50 | 1.000103 | 1.212 | [0.99995, 1.00025] | [0.99994, 1.00024] | < 0.0001 | null / null |
| b20-r2-n4096 | 50 | 1.000005 | 0.232 | [0.99997, 1.00004] | [0.99997, 1.00004] | < 0.0001 | null / null |
| b20-r3-n256 | 50 | 1.014930 | 2.588 | [1.00342, 1.02576] | [1.00360, 1.02589] | 0.0002 | null / null |
| b20-r3-n512 | 50 | 1.001943 | 1.384 | [0.99940, 1.00437] | [0.99941, 1.00429] | 0.0001 | null / null |
| b20-r3-n1024 | 50 | 1.000301 | 0.881 | [0.99968, 1.00092] | [0.99969, 1.00094] | < 0.0001 | null / null |
| b20-r3-n2048 | 50 | 1.000061 | 0.713 | [0.99989, 1.00023] | [0.99988, 1.00024] | < 0.0001 | null / null |
| b20-r3-n4096 | 46 of 50 | n/a | n/a | n/a | n/a (descriptive only, never read) | n/a | invalid / invalid |
| b24-r1-n256 | 90 | 1.024647 | 1.478 | [0.99134, 1.05821] | [0.99020, 1.06015] | 0.0019 | null / null |
| b24-r1-n512 | 50 | 0.996159 | -0.717 | [0.98662, 1.00598] | [0.98631, 1.00647] | 0.0005 | null / null |
| b24-r1-n1024 | 50 | 0.998540 | -1.070 | [0.99586, 1.00122] | [0.99565, 1.00125] | 0.0002 | null / null |
| b24-r1-n2048 | 50 | 0.998889 | -3.131 | [0.99840, 0.99948] | [0.99841, 0.99944] | < 0.0001 | null / null |
| b24-r1-n4096 | 50 | 0.999901 | -1.149 | [0.99977, 1.00003] | [0.99977, 1.00003] | < 0.0001 | null / null |
| b24-r2-n256 | 90 | 0.994506 | -0.331 | [0.96428, 1.02189] | [0.96368, 1.02526] | 0.0034 | null / null |
| b24-r2-n512 | 50 | 0.995792 | -0.764 | [0.98636, 1.00486] | [0.98677, 1.00456] | 0.0004 | null / null |
| b24-r2-n1024 | 50 | 0.999717 | -0.202 | [0.99723, 1.00230] | [0.99724, 1.00203] | 0.0003 | null / null |
| b24-r2-n2048 | 50 | 0.999835 | -0.469 | [0.99916, 1.00048] | [0.99922, 1.00050] | 0.0001 | null / null |
| b24-r2-n4096 | 50 | 1.000078 | 0.907 | [0.99992, 1.00024] | [0.99991, 1.00024] | < 0.0001 | null / null |
| b24-r3-n256 | 90 | 0.986744 | -0.820 | [0.95576, 1.01651] | [0.95593, 1.01536] | 0.0012 | null / null |
| b24-r3-n512 | 50 | 1.008188 | 1.520 | [0.99814, 1.01856] | [0.99751, 1.01899] | 0.0006 | null / null |
| b24-r3-n1024 | 50 | 1.001313 | 0.937 | [0.99853, 1.00403] | [0.99858, 1.00409] | 0.0001 | null / null |
| b24-r3-n2048 | 50 | 1.000768 | 2.342 | [1.00014, 1.00143] | [1.00016, 1.00147] | < 0.0001 | null / null |
| b24-r3-n4096 | 50 | 0.999925 | -0.913 | [0.99977, 1.00009] | [0.99976, 1.00008] | < 0.0001 | null / null |
| b28-r1-n256 | 1440 | 1.041401 | 2.524 | [1.00996, 1.07428] | [1.00933, 1.07571] | 0.0014 | null / null |
| b28-r1-n512 | 89 | 1.007266 | 0.435 | [0.97429, 1.04240] | [0.97194, 1.04276] | 0.0024 | null / null |
| b28-r1-n1024 | 50 | 1.008857 | 1.648 | [0.99658, 1.01983] | [0.99626, 1.02024] | 0.0004 | null / null |
| b28-r1-n2048 | 50 | 0.999770 | -0.164 | [0.99734, 1.00215] | [0.99736, 1.00223] | 0.0001 | null / null |
| b28-r1-n4096 | 50 | 1.000386 | 1.080 | [0.99973, 1.00103] | [0.99974, 1.00107] | < 0.0001 | null / null |
| b28-r2-n256 | 1440 | 0.997842 | -0.130 | [0.96594, 1.02968] | [0.96843, 1.02836] | 0.0025 | null / null |
| b28-r2-n512 | 89 | 0.964899 | -2.170 | [0.93684, 0.99350] | [0.93616, 0.99289] | 0.0007 | null / null |
| b28-r2-n1024 | 50 | 1.002022 | 0.356 | [0.99156, 1.01196] | [0.99204, 1.01202] | 0.0005 | null / null |
| b28-r2-n2048 | 50 | 1.002449 | 1.794 | [0.99968, 1.00521] | [0.99974, 1.00527] | 0.0001 | null / null |
| b28-r2-n4096 | 50 | 0.999525 | -1.363 | [0.99880, 1.00023] | [0.99884, 1.00021] | < 0.0001 | null / null |
| b28-r3-n256 | 1440 | 1.015227 | 0.932 | [0.98272, 1.04821] | [0.98236, 1.04819] | 0.0004 | null / null |
| b28-r3-n512 | 89 | 0.983656 | -1.007 | [0.95067, 1.01655] | [0.95134, 1.01662] | 0.0007 | null / null |
| b28-r3-n1024 | 50 | 1.008900 | 1.572 | [0.99815, 1.02031] | [0.99780, 1.02012] | 0.0004 | null / null |
| b28-r3-n2048 | 50 | 0.999933 | -0.049 | [0.99795, 1.00203] | [0.99789, 1.00193] | 0.0001 | null / null |
| b28-r3-n4096 | 50 | 0.999997 | -0.009 | [0.99938, 1.00058] | [0.99944, 1.00055] | 0.0001 | null / null |

The blind and recorded values also agree on the remaining quantities:
- Calibration: mean -0.26757 and population sd 0.97357 against the recorded -0.26757013662385903 and
  0.9735699770654103; pass on both. No alternative the blind task tried flips the gate (U1, U5).
- Plant: min plant_kappa 1.2885 at b20-r2-n4096 and min plant_z 21.9 at b24-r2-n256, the same cells as the
  record.
- fraction_valid 44/45; outcome O-NULL and headline SUPPORT_SCOPED on both.
- E[C]: the blind task derived E[C] = C(L)(n)_4/(l)_4 exactly, which is 3 binom(n,4)/(p-2) for L = F_p and
  3 binom(n,4)/p (1 + O(1/p)) for the curve label universe. It checked this identity by exhaustive
  enumeration and measured C(L) exactly at 20 and 24 bits. The measured null mean against the formula lies
  in [0.99511, 1.00771] over the 44 cells on both sides.

C2. Against the frozen predictions:
- P1 (|kappa - 1| < 0.05 with ci95 inside [0.90, 1.10]) is met on 44 of 44 powered cells and not assessed
  at b20-r3-n4096.
- P2 (plant_kappa >= 1.15, plant_z > 4) is met on 44 of 44.
- P-detect is not met: no cell is flagged and no replication was triggered.
- The C4 calibration gate is met.
- The O-NULL rule (every valid cell null, at least 80% valid) is met at 44/45.

C3. Against the coordinator prior (coordinator-prior.yaml, frozen in commit 1eddb4740b before any reviewer
ran). Every expected reviewer finding was met:
- The 3.11.15 replay was exact. The prior's conditional tolerance branch was not needed.
- The blind ci95 is not bit-reproducible but keeps every class, as the prior expected.

Findings the prior did not anticipate:
- the cell-level over-dispersion of the log-GAP z (O6);
- the spec's flag-power sentence (L3);
- the low power of the calibration gate (L4);
- the proper-GAP selection (L2).

No stop condition of the prior fired.

C4. Against the A/A noise floor. The log-GAP arm's cross-cell dispersion (sum z^2 71.4) exceeds that of
the two A/A arms on the same cells (44.9 and 40.5). Its per-curve dispersion does not. Its kappa
deviations stay inside the 5% band, and the largest deviation at n >= 1024 is 0.9%.

## Inference

I1. On the frozen protocol, H1 of H-PFDR-727bfc holds at the preregistered 5% tolerance in 44 of the 45
toy cells. The scope is: x-labels of proper (relation-free) rank-r log-GAP half-boxes (r in {1, 2, 3},
fixed origin, one representative per +-c, lexicographic fill, T minimal by vector count), n in {256, ...,
4096}, on generated prime-order ordinary curves of 20, 24 and 28 bits (main seed block 8,100,000 + c, 50
to 1440 curves per cell). In that scope the exact pair-sum (h = 2) coincidence count matches the matched
uniform-label null within 5%, with every curve-cluster 95% interval inside [0.90, 1.10].

I2. The reading is not an artefact of an insensitive instrument:
- the planted label AP reads flagged in every powered cell;
- in the weakest powered cell (b28-r1-n512), a true homogeneous |kappa - 1| of at least 0.079 would have
  read non-null with 95% probability (red team Q1);
- the A/A comparisons do not flag above the nominal rate.

The reading is not a pipeline or interpreter artefact either. The exact 3.11.15 audit replay (J1), the
validity checks (J2), the disjoint recount (J3) and the blind re-derivation (C1) each reproduce it
independently.

I3. What the measurement closes is narrower than the specification's decision_impact.on_positive wording.
These label sets carry no label-additive (small-doubling or label-AP) structure of the kind the planted AP
represents beyond about 2 to 47 labels (red team rt_ap_bound, a scaling estimate). An additive label
predicate for these label sets is not supported at these sizes. The measurement does not show that the
sets are not "label-describable". It does not reach the unknown-sharing base of IDEA-20261017-bbc53e,
which was not tested. KN-OPEN-020 stays open.

I4. The over-dispersion of O6 is unexplained. Chance after look-elsewhere and a small cell-specific
effect below the tolerance are both compatible with the data. The evidence cannot discriminate them, and
only a replication of the |z| > 2 cells on fresh curves can. It changes no class. Support is for the 5%
tolerance and not for exact random-set behaviour.

## Limitation

L1. Toy scope only: p of 20 to 28 bits, n of 256 to 4096 and generated curves. There is no cost,
exponent, attack, real-curve, security or asymptotic statement. Nothing transfers to other p, n, curves,
coordinates (y-labels, other models), h >= 3, translated boxes x(Q + cP), other fills, rank >= 4 or
non-GAP bases. The held real-curve extension (HU-5) stays untested.

L2. Relation-bearing (improper) log-GAPs are excluded, and not at random. The four relation-bearing draws
of the census were exactly the degenerate jobs of b20-r3-n4096. They were removed unmeasured by the
frozen rule, and they are the instances most favourable to the alternative. The tested population is
proper log-GAPs. b20-r3-n4096 is not assessed. Its 46-curve descriptive kappa must never be cited as a
reading.

L3. The specification's sample_size_justification says a true 10% excess is flagged "with probability
above 0.95". That sentence is mistaken. It ignores the |kappa - 1| >= 0.10 conjunct of the flag rule; the
flag probability at a true 10% excess is about 0.50 per cell, and 80% needs about 0.100 to 0.115 (red
team O4). O-NULL is protected, because a true 10% excess reads intermediate, not null:
P(null | 0.10) <= 0.002.

L4. The C4 calibration gate is weak. At 44 cells, P(pass) is 0.40 at a true sd of 1.3 and 0.36 at a mean
shift of 0.4, and the gate tests the null arm only. It certifies gross calibration only (red team O6).

L5. The O6 dispersion test was not preregistered. Several post-hoc dispersion tests were run, so its tail
probability needs a look-elsewhere correction.

L6. There is no positive control in which group structure is known to induce label structure. The plant
is label-side structure only (red team O7).

L7. RUN-PFDR-243425 and RUN-PFDR-089edc carry the scoped citability of DEC-20261029-5554ee, which rested
on the absence of an exact audit replay. This round's J1 made one under CPython 3.11.15 (uv build; the
recorded interpreter was a GCC 13.3.0 build of the same version). Whether to rescope is a next action and
is not decided here.

L8. Page 1 of reports/run-20261023T2211Z/report.pdf prints "Commit: 98ab4496...". That is the runbook
session's opening commit, not the runs' code commit 48bd193a. The diff between the two is empty for
EXP-PFDR-bb0d26 and H-PFDR-727bfc, but a reader could take the label for the runs' commit.

L9. There is no execution proof. The docs/execution-proof-chain.md milestones are open, and nothing here is
"execution verified".

L10. Single run set and one producer session. The census was not replicated (no cell was flagged, so the
frozen protocol ran no replication). The review recounted and re-derived but ran no new census. One model
family served the producer, the reviewers and this Coordinator. Session independence is attested. Model
independence is not claimed.

L11. The J3 sample covers 15 of the 6653 ok jobs. The E[C] exact check covers 20 and 24 bits only; at 28
bits the formula rests on the O(1/p) argument. Cells at the same bits share curve sets, but the measured
cross-cell correlation is negligible (red team Q2).
