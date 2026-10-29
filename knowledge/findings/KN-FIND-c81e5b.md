---
id: KN-FIND-c81e5b
type: internal_finding
title: >-
  x-labels of proper rank <= 3 log-GAP half-boxes on toy prime-order curves (20-28 bits, n 256-4096) carry
  the pair-sum coincidence count of a uniform random label set within 5% in 44 of 45 cells. This is an h = 2
  additive statement only; relation-bearing log-GAPs are untested.
tags: [sum-product, log-gap, x-labels, additive-energy, label-sumset, coincidence-count, random-set-heuristic, heuristic-validation, null-result, toy-scale, pfdr, ecdlp]
confidence: reported
internal_refs: [EV-PFDR-07d608, DEC-20261029-01405d, H-PFDR-727bfc, EXP-PFDR-bb0d26]
proof_status: empirical_only
proof_refs:
  - experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-089edc/analysis.json
  - experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-4d8c71/toy-main-jobs.jsonl
  - experiments/EXP-PFDR-bb0d26/review/TASK-20261029-e5fe6b/cells.json
  - experiments/EXP-PFDR-bb0d26/review/TASK-20261029-958053/j3-recount.json
  - experiments/EXP-PFDR-bb0d26/review/TASK-20261029-ff0453/rt_analysis.json
claim_tier: toy
added: 2026-10-29
superseded_by: null
---

## Finding

For x-labels of **proper** (relation-free) rank-r log-GAP half-boxes the measured counts fit the random-set
law within 5%. The construction is: r in {1, 2, 3}, labels x(c_1 P_1 + ... + c_r P_r), fixed origin, one
representative per +-c, lexicographic fill, and T minimal by vector count. The tested sizes are n in {256,
512, 1024, 2048, 4096}, on generated prime-order ordinary curves of 20, 24 and 28 bits (seed 8,100,000 + c,
50 to 1440 curves per cell).

The count is the exact pair-sum coincidence count C(X) = sum over s of binom(m_s, 2), the h = 2 additive
energy. It matches the mean over 20 uniform n-subsets of the same curve's label universe, with
E[C] = 3 binom(n,4)/p (1 + O(1/p)), **within the preregistered 5% tolerance in 44 of the 45 toy cells**:

- |kappa - 1| < 0.05, with every curve-cluster bootstrap 95% interval inside [0.90, 1.10];
- the observed |kappa - 1| is at most 0.041 (b28-r1-n256), at most 0.009 at n >= 1024, and at most 0.0025
  at n >= 2048;
- the log-kappa slopes in log2 n are flat (|slope| <= 0.0088 for every bits and r).

The instrument could have seen a deviation:
- a planted label arithmetic progression reads flagged in every powered cell (plant_kappa >= 1.288);
- in the weakest powered cell, a true |kappa - 1| >= 0.079 would have read non-null with 95% probability;
- planted-type label-AP substructure is detectable from about 2 to 47 labels (a scaling estimate);
- the null-vs-null and even/odd A/A comparisons stay at nominal.

The reading was reproduced four ways:
- an exact audit replay under the recorded interpreter version (CPython 3.11.15);
- a disjoint brute-force recount of sampled jobs, using the reviewer's own curve arithmetic;
- a strictly blind re-derivation of every cell statistic and class from the job records;
- a red-team power and scope review.

**Use.** At toy scale this licenses the random-label null rate 3 binom(n,4)/p for label-sum coincidence
harvests from proper rank <= 3 GAP bases. That is the kappa = 1 input of the harvest rate in
IDEA-20261017-bbc53e. It is a null, not a lever.

## Scope and limitations

- **Additive (pair-sum, h = 2) structure only.** The finding does not exclude multiplicative, algebraic,
  polynomial, constructible, interpolation-based or source-recovery label predicates, nor structure first
  visible at h >= 3. It is **not** a closure of "label-describable" log-GAPs, and it does not reach the
  implicit-membership route of KN-OPEN-020, which stays open.
- **Proper log-GAPs only.** The census drew four relation-bearing base-point triples (all in b20-r3-n4096,
  sup-norm 8 to 14). They exhausted the half-box and were excluded unmeasured by the frozen rule. These
  are the instances most favourable to group-to-label leakage, so their absence is selection, not chance.
  Cell b20-r3-n4096 is **not assessed**.
- **Other set families are not tested:** translated boxes x(Q + cP), other fills or orders, full boxes with
  both lifts, rank >= 4, and unions of short rank-1 progressions such as the unknown-sharing base of
  IDEA-20261017-bbc53e. y-labels and other curve models are not tested either.
- **Tested sizes only.** Nothing is claimed for n outside 256-4096 or p outside 20-28 bits, for any
  standardized or deployed curve, or for any growth law. There is no asymptotic statement and no cost,
  exponent, attack or security statement.
- **The 5% tolerance, not exact randomness.** A post-hoc omnibus check of the 44 log-GAP z-scores, which
  was not preregistered, shows more dispersion than N(0,1): sum of z^2 = 71.4 on 44, p about 0.006, with six
  cells at |z| > 2. The A/A arms are calibrated. The excess comes from small cell-level shifts of mixed sign
  (at most 0.9% at n >= 1024) and is unexplained. A replication of those cells is scheduled
  (DEC-20261029-01405d NA-2).
- **Controls.** The calibration gate is weak (it passes a moderate miscalibration with probability 0.36 to
  0.40). The planted positive control is label-side structure: no control shows sensitivity to group
  structure inducing label structure.
- **Basis.** empirical_only. The evidence is one frozen run set and one producer session, with no
  fresh-curve census (the protocol replicates flagged cells only, and none was flagged). There is no
  execution proof. RUN-PFDR-243425 and RUN-PFDR-089edc carry the scoped citability of DEC-20261029-5554ee,
  ruled because no exact audit replay existed. Review round REVIEW-PFDR-bb0d26-20261029 then made an exact
  audit replay of both under CPython 3.11.15.

## Evidence

- `EV-PFDR-07d608` (evidence, strong, toy) and `DEC-20261029-01405d` (decision, `support`, scoped).
- EXP-PFDR-bb0d26 v1, runs RUN-PFDR-e44a19, RUN-PFDR-4d8c71, RUN-PFDR-243425, RUN-PFDR-cd03e2 and
  RUN-PFDR-089edc (6653 ok jobs, 1580 curves).
- Review round REVIEW-PFDR-bb0d26-20261029: validator TASK-20261029-958053, blind re-deriver
  TASK-20261029-e5fe6b and red team TASK-20261029-ff0453.
- Cheapest open falsification control: a coincidence count on the four recorded relation-bearing triples
  (DEC-20261029-01405d NA-1).
