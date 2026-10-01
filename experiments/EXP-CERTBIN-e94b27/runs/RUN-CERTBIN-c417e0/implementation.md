# RUN-CERTBIN-c417e0 implementation note (EXP-CERTBIN-e94b27, TASK-20260924-41c7be)

Written by the executor after phase 7. This file is NOT listed in
manifest.yaml `artifacts` (the manifest was written first); its sha256 is
reported in the executor hand-back instead.

## Revision and environment

- git HEAD ec215577869db85c5cae7980ae230349c257ea29 at every invocation;
  tree dirty (untracked files of this task and of the two concurrent CERTBIN
  executors, EXP-CERTBIN-3f06d1 and EXP-CERTBIN-a58c63; the full list is in
  manifest.yaml).
- Python 3.11.15, numpy 2.4.6 (already installed; no environment change was
  made by this task), PyYAML 6.0.1. One worker, OMP/OPENBLAS threads 1,
  RLIMIT_AS 3 GiB in-process. Peak RSS: phases 1-4 1.16 GB.
- Specification sha256 387c5d51...31ba, byte-identical to the
  TASK-20260924-d3a90c receipt (checked in C-SRC).

## Deviations from, and interpretations of, the frozen protocol

1. W_D iteration is semi-naive: at iteration i only the products v_j * b of
   the echelon rows whose low-degree leading monomial is NEW at iteration i are
   added (the products of the older fallen rows already lie in W^(i)). The
   iterates, dimensions, fixpoint index and first iteration containing 1 are
   identical to the literal rule (proof in impl/closure.py and impl/README.md);
   the self-test compares them against a literal plain-Python implementation.
2. C-SELF "W_D on 5 random small Boolean systems": the self-test compares every
   drawn system and keeps drawing until at least 5 are compared AND the
   compared set covers a refutation at iteration 0, a refutation at iteration
   >= 1, a planted (satisfiable) system and an unrefuted multi-iteration system
   (23 systems were compared, all matching). This is a superset of the
   specified check.
3. C-SRC is performed first inside selftest.py (writes inputs.json) and again
   by the driver before phase 1. It covers the five run files and the four
   copied source modules against the TASK-20260923-c2e57b receipt, and the
   specification against the TASK-20260924-d3a90c receipt.
4. C-NULLS "archived union support U_k": RUN-CERTBIN-3b7e05 archives only the
   per-equation SIZES of U (union_support_size_per_eq). U was recomputed from
   the curve's affine basis E^0, E^j (copied macaulay.affine_basis), its sizes
   were checked equal to the archived sizes, and every F-NULLF2 instance was
   checked to lie inside it.
5. C-VERIFIER construction agreement is computed by the verifier itself: it
   reads the engine's E_hex from instance-sets.json and compares it with its own
   reconstruction (144 curve-algebra instances, 0 disagreements).
6. C-VERIFIER negative controls: the driver (`--resume`) built 20 corrupted
   certificates from the first 20 verified certificates in file order (all are
   W_4 certificates of U62 instances), alternating "one pair removed" and "one
   k changed (k -> k+1 mod 17)" at position (i * 7919) mod |C|, and invoked the
   verifier as a subprocess. 20 of 20 were rejected.
7. EXP-CERTBIN-4e92d7/impl/oracles.py was NOT copied (the handoff permits
   gf2n.py, curve.py, macaulay.py, elim.py only). Oracles A and B were written
   fresh (impl/oracles_rc1.py). The four copied files are unchanged (empty
   diffs in impl/impl-provenance.json); macaulay.py was already general in D.
8. W_5 residual selection used the engine-REPORTED W_4 / M_5 outcomes (the
   verifier runs after all closures, per the phase order). All reported
   refutations later verified, so the selection equals the verified one.
9. The driver skips completed checkpoints with or without `--resume`.

## Development runs (disclosed)

Before the official run the executor ran, with outputs only in the session
scratchpad outside the repository:
- probes of M_4/M_5/W_4/W_5 timing on x_R = 4418 (U62 idx 27), 88878 (S62
  idx 1) and 65712 (C20 idx 5);
- the self-test several times (same seed) while developing it;
- a pipeline test with `--dev-limit 3` (the first 3 instances of every set),
  through phases 1-7.
These showed the closure outcomes of those few instances before the official
run. No selection rule, threshold, metric or code path of the decision rules
was changed after them; the code changes after them were bug fixes in the
manifest writer (trial-plan path) and in caching of the negative-control
metadata, and the self-test coverage rule in item 2.

## Unexpected or noteworthy observations (recorded, not interpreted)

- Every U62 instance has 1 in W_4 at iteration 1 (W^(1) is all of B_{<=4},
  dim 4048). Every C20 instance has 1 already in W^(0) = M_4.
- The secondary reading "ell in W_4 cap B_{<=1}" is true on 62/62, but it is
  implied by 1 in W_4 (W_4 is then everything), so it carries no separate
  information here.
- Every U62 W_4 certificate has max deg mu = 3, i.e. it is also a combination
  of M_5 rows (M_5 multipliers have degree <= 3).
- Both null sets: W_4 = M_4 (fixpoint at iteration 0, dim 2771, no
  refutation, 0/62 each), while M_5 refutes 62/62 of each null set.
- S62: final dim W_4 is 4046 (41 instances), 4044 (17), 4042 (2), 4043 (1)
  or 4040 (1), i.e. codimension 2 to 8 in B_{<=4}; no satisfiable instance is
  refuted by W_4, M_5 or W_5.
- W_5 ran on 10 S62 instances only: the U62 residual and both null residuals
  were empty.
- MR4 W_5 null rates are 0/0 (not run); their CP95 is undefined (null).

## Independence (EX-10)

The executor wrote both impl/ and verifier/. The independence is code-level
(no shared import; different reconstruction method of f_k), not author-level.
