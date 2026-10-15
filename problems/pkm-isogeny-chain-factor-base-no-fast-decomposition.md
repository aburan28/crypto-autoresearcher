# No fast decomposition solver for the PKM 2-isogeny-chain factor base (P-256 route)

- **Status:** `open`
- **Kind:** empirical bottleneck; missing algorithm (no known solver exploits the chain); proof gap (no degree-of-regularity bound)
- **Affected work:** [EXP-ECDLP-f49f75](../experiments/EXP-ECDLP-f49f75/specification.yaml), [H-ECDLP-60de36](../ledger/hypotheses/H-ECDLP-60de36.yaml), GOAL-ECDLP-001, RQ-ECDLP-001
- **Next action owner:** unassigned (Coordinator to rank against GOAL-ECDLP-001 work)
- **Last updated:** 2026-10-15

## Problem

We cannot establish a sub-generic ECDLP route for P-256 through the factor base
B = {(u, v) in E(F_p) : Phi_x(u) = x(Phi(R))}, Phi a chain of 44 Velu
2-isogenies from E0: y^2 = x^3 + x (p = 3 mod 4, 2^96 | p+1), because no
algorithm is known that decomposes a random point T = P1 + ... + P6 over B in
~O(|B|) time, and at toy scale the chain encoding makes Groebner decomposition
*slower*, not faster, than structureless encodings of the same set.

The proposal (user, 2026-10-15) needs |B| ~ N^(1/6), O(|B|) relations each
costing ~O(|B|), and ~O(|B|^2) linear algebra, for ~N^(1/3) total. The
construction is public (no secret) and the fibre is simply x(R + <K>), a coset
of a cyclic subgroup of E0(F_p); E0 and P-256 have different group orders, so
no F_p-isogeny carries E0's group structure to P-256's addition law.

## Evidence and uncertainty

- **Observed:** EXP-ECDLP-f49f75 (RUN-ECDLP-f49f75-01/-02; RUN-03 pending, Singular 4.3.2
  std/slimgb + fglm, 600 s timeout, 6 instances per cell). At every jointly
  completed cell (m = 2, L = 3..7; m = 3, L = 3, 4; m = 2, L = 8..11 re-running as RUN-03 under AMD-02) the chain encoding is
  slower than the dense encoding of the same x-set, and the gap grows with L
  (std: 2x at m = 2, L = 3 to 287x at L = 7; 35x at m = 3, L = 4). The chain arm
  times out on every instance at m = 3, L = 5 while the dense same-set and
  random-set arms complete. Dense same-set and random-set costs are
  indistinguishable: the set's isogeny origin is invisible to the solver.
  Meet-in-the-middle enumeration is orders of magnitude cheaper than every
  Groebner arm at every cell. See the review report under
  `experiments/EXP-ECDLP-f49f75/reports/`.
- **Derived or proved:** the fibre equals x(R + <K>), |fibre| = 2^L
  (verified by assertion in the launcher at every instance). Generic-group
  lower bound: any ~N^(1/3) decomposition must use non-generic structure.
- **Suspected explanation:** conjecture: the L auxiliary variables per point
  raise the number of variables from m to m*L without lowering the
  degree of regularity, so Buchberger/F4-type solving pays for the extra
  variables; nothing in the chain interacts with Semaev's S_{m+1}.
- **Missing capability:** an F4/F5 solver (msolve, Magma) was not available in
  the container; only Singular std/slimgb were run. m >= 4 and the P-256
  parameters (m = 6, L = 44) are far beyond any arm here.
- **What this evidence does not establish:** that no solver or no different
  modelling of the chain (e.g. Weil-descent-style, SAT, or a hybrid) can
  exploit it; anything about m = 6; anything about P-256 security.

## What would unblock it

- [ ] A decomposition algorithm that, on a frozen toy grid like EXP-ECDLP-f49f75
  (same seeds, planted-decomposition control at 100%), solves the chain-encoded
  m = 3 system faster than the dense same-set and random-set controls in >= 80%
  of cells and completes a larger L than both, under the same instrument.
- [ ] Or a proof/heuristic bound on the degree of regularity of the chain +
  S_{m+1} system that is independent of L, checked against measured first-fall
  degrees.

Either would show the chain carries usable structure; neither alone gives an
N^(1/3) P-256 attack (relation independence, m = 6 success probability,
linear algebra and S_7 construction remain).

## Next discriminating step

- **Action or proof obligation:** repeat the m = 3 grid with an F4 solver
  (msolve) and record first-fall / regularity degrees, to rule out
  instrument dependence.
- **Inputs and controls:** amendments/trial-plan-run02.json seeds; arms A, B, C,
  E; planted control.
- **Execution limits and stop condition:** same 600 s timeout and stopping rule.
- **Outcomes and next actions:** chain still slower -> close this route for
  GOAL-ECDLP-001; chain faster -> scale to m = 4 with a medium-tier protocol;
  instrument failure -> record, not evidence.
- **Recheck trigger:** msolve or Magma becomes available in the environment, or
  a new modelling of the chain constraints is proposed.

## Resolution and history

- 2026-10-15: opened from EXP-ECDLP-f49f75. Unresolved.
