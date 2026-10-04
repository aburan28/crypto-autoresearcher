# Review report — TASK-20260930-40470a

**Per-joint verdicts.** These are the only verdicts. No whole-goal verdict is given, and the Coordinator
composes.

| joint | verdict | one-line reason |
|---|---|---|
| J1: derivational soundness of the no-go | **CONCUR** | The group-law derivation holds at every m. Two scope corrections are required (distinctness; degree drop on S_{m-1}(x_1..x_{m-1}) = 0). |
| J2: scope honesty (widened) | **DISSENT** | D-5/N-2 of DEC-20260810-2f86db, carried by the goal head, license "the D-4 swapped statistic is dead at m=3" on a check that holds identically. The count it would condemn varies. |
| J3: adequacy for criterion (c) | **DISSENT** (as recorded) | It inherits the J2 defect, and it lacks the `obstruction` block that AGENTS.md's closure standard (in force since 2026-08-14) requires. Both can be cured in the composed decision with no runs. |
| J4: adequacy of H-MONO-ebd400 / EV-MONO-e9dc3b for criterion (a) | **DISSENT** | On KN-OPEN-009's ordered base the m=4 monodromy is V_4 for every curve; "within stated error" failed as pre-registered; adoption would contradict DEC-20260802-a51c82 N-2 and DEC-20260904-dd58c3's scope statement. |
| proves-too-much | D-1 stops at the locus boundary on both objects | D-5 makes the illegitimate transfer (J2 O-1). |
| blind re-derivation | agrees with OBS-5 in substance | m=3 and m=4 (m=5 at random), on my own S_4. blind_from was not opened. |

- Card: `TASK-20260930-40470a` (GOAL-MONO-001, BATCH-44adf9, claim epoch 1, owner coordinator-portfolio-3811)
- Plan: `REVIEW-MONO-20260930-40470a` (authoritative copy inline in `ledger/handoffs/TASK-20260930-40470a.yaml`; extraction `coordination/review/mono-20260930-44adf9/review-plan.yaml`)
- Role / binding: validator / `validator-breakthrough`; requested policy `review-breakthrough`, effort `max`
- Snapshot read: branch `claude/coordinate-mono-20260930`, HEAD `d771721ac052bce33dc302e6aa2d1d804a1c5db0`, working tree clean at start
- Write scope: `coordination/goals/GOAL-MONO-001/review/TASK-20260930-40470a/` — only `review_report.md` and `s4_construction/computations.json` are written
- Zero runs. No `RUN-*` directory. Nothing under `experiments/` is touched.
- Claim tier ceiling: toy. Nothing here is an ECDLP result and no security estimate moves.

## Bound object digests (sha256 of the file at HEAD d771721ac052; git blob prefix)

| sha256 | blob | path |
|---|---|---|
| d45cc8d57ce699134bfbcc193d5a13303ab6f0f07e54f77b12d899c142d37d6e | 59b625668b2a | ledger/handoffs/TASK-20260930-40470a.yaml |
| b15571cedc3a30c5ea74a98096e302f1db280d68ecb517dbd8bc63b4fed8319d | 8f29fcd37c00 | coordination/review/mono-20260930-44adf9/review-plan.yaml |
| 79f839c703a034c90d8b2531e24c1a0ba90ab397fcc6e495534bbe05d782c5d6 | 58d2144435d2 | coordination/goals/GOAL-MONO-001/batches/BATCH-44adf9/dispatch_queue.json |
| 56df5c181efe823b000cf16fc6a63d06c2a642360ee1b6b09c9e2b5db7008b25 | a49ea535c87c | ledger/decisions/DEC-20260930-3a0b7b.yaml |
| 82e3bd17fa8a29413d0a396b115dd76d174f41dabcd70710e97b39acdacd530f | 14ccf6576d9e | ledger/handoffs/TASK-20260904-50755f.yaml |
| 11a9104650ec694dff201f2b707c98daf2084b95a83eade96a628d892f176586 | 8a547ba5b2a4 | ledger/decisions/DEC-20260810-2f86db.yaml |
| 22689dba3de9260f8483aeff485d21a9f89335bb47edd4f7a94abd8628486e58 | 90f63f59df88 | ledger/decisions/DEC-20260802-a51c82.yaml |
| 0b2201523f36b33a17cf4cd9e88e5c154f857a3e58eb1dc773902dd64e4b16b1 | fca8254ca188 | ledger/decisions/DEC-20260904-67cde4.yaml |
| 800cc22c89e366082e5ce632c16637df7e83ba358a0e31bb79ee7c94d56463ac | 392c50aff2b0 | ledger/evidence/EV-MONO-a0a89c.yaml |
| dea9f092bafd327200813fc94a652c764976993765139b906841e6ad36fe47f2 | 55fe800d6a6d | ledger/goals/GOAL-MONO-001/goal.yaml |
| 52e0c92126846a124e61fc8a3a1899c3ea5d04adad328833336bde5286a3bc71 | 744cba2c60f2 | ledger/goals/GOAL-MONO-001/checkpoints/BATCH-003.yaml |
| 5e91cf5a7d3627ecb39cf68c2ae3c26915d7d1b5b4586c3e6b0b91af68c88f53 | 7fe7eac2c1bc | ledger/corrections/CORR-20260802-1d8384.yaml |
| 9bd70982b6cd53bffeb04de6b733a950ad48ffa2ad57caee12ffa2282bdf8c06 | 994ab12299d4 | ledger/questions/RQ-MONO-001.yaml |
| a067376754ac37d670ac69744e63d2f52a5aa22df05a613ad965b9bc63647643 | 9c07e8557ba6 | knowledge/open-problems/KN-OPEN-009.md |
| c7d48577d6c950ddeea2508d54fa2c98692b24d2bcb735a327fce26f491e1be8 | 328f47f6d278 | ledger/decisions/DEC-20260904-dd58c3.yaml |
| f5f1b40e732e354acc45c5c64836e0f91dc79dccb7919dd7e4a619221288c33b | 733b075cb52c | ledger/evidence/EV-MONO-e9dc3b.yaml |
| 86b9ea0d7275b9fcfeb5cb05ae87f63912847363f6b0d59a0ec723426ab6b779 | 2a99b947a5eb | ledger/hypotheses/H-MONO-ebd400.yaml |
| 5ae435471d99b2326a45a0660106d0d7927fb1e9b6a994be4eac921401de6c53 | 49192f5f9709 | ledger/corrections/CORR-20260904-33fbf3.yaml |
| a028c8bb749097e9adb3421a28c0d632adde51e6772a528cc18a261e4134c107 | eca05bcfc4e7 | experiments/EXP-MONO-0e6e8f/specification.yaml |
| 0f0ac7cf3bda5e25bcb198b20b4fec7e630e835ef3835957974973ee30b7d5f1 | f4540e1cfa8a | experiments/EXP-MONO-0e6e8f/execution_report.yaml |
| 2789cae0b33c1efb6b0c947e9126e13097377d44e6bfa38961d7658958402290 | b41d600e7ae4 | ledger/decisions/DEC-20260905-021e6e.yaml |
| 5bfb29c78644156f0c87d38f3e9b4fbcd915c5644e5f67c066f53733dccafcec | b7880cb33c12 | knowledge/findings/KN-FIND-edd62c.md |
| 06f2ddd8b24ddb4da13c380d9f44b07085bcb010548fdddd6fa7842586deccc0 | 35f6c6994065 | knowledge/findings/KN-FIND-19f5ea.md |
| 5537cecc4b6bd6adc76fbeb2c516461b4fd21021d0acdde1731779120938cd26 | e4c9211b495d | AGENTS.md |
| 5b615a9581a2b476f96d4c6baa4b77227c5dac5a200fdf8e58947c67b988eb3f | 5a2fe9254769 | templates/research-records.md |
| d338e507320062b4911fbf36d3b4708a505f14a8322502f6523c17ad0a3acf3e | 19b908afc338 | docs/inventor-protocol.md |
| 08f1144225ab702cb5feb206c53d0ca5e5fa71d80a8fa2734a3d851951597122 | a702d1ad498a | agents/validator.md |
| d298dba57405bc7db7e6883de2e3060d47059617b57aea1eb6d0251bba671db9 | e91cdb78d69e | .claude/agents/validator-breakthrough.md |
| 40b3de73fc177d2f7e419ebdba02ff87949a6ff9e830edd2015c99351d4f145f | 2e1bbf867e18 | docs/claims-and-verification.md |

## Procedure (declared before the work was done)

1. Read the card, the plan extraction, the queue card, and the role contracts (AGENTS.md, agents/validator.md, .claude/agents/validator-breakthrough.md, docs/claims-and-verification.md, docs/inventor-protocol.md, the review-attestation part of templates/research-records.md).
2. Blind re-derivation FIRST, before opening any producer record (EV-MONO-a0a89c, DEC-20260810-2f86db and the rest are opened only after the derivation and the S_4 computations are written). The derivation starts from the plan's statement of the quantity, the group law, and the defining property of Semaev polynomials.
3. Build S_3 and S_4 myself (two independent constructions), and check m=3 and m=4 on random factor-base tuples, exhaustively on one small curve, and on constructed degeneracies.
4. Then read the producer and later records and do J1 (compare), the proves-too-much control, J2, J3, J4.
5. Blind_from paths (`experiments/EXP-MONO-4b50b6/`, `coordination/goals/GOAL-MONO-001/batches/BATCH-003/`) are never opened; no repository-wide search is run that could print their content.

**Procedure as executed.** Differences from the declared procedure, all additive:

- **(a) Blind section written first, as planned.** The blind section below was written, and its
  computations run and embedded, before any producer record was opened. It is left exactly as written
  then. It marks the Semaev citation `recalled`; I later retrieved and read that paper (J1), so its
  provenance is now `retrieved`.
- **(b) Two curves, not one.** The exhaustive m = 4 check ran on two curves, C1 and the plan-named C2,
  rather than one.
- **(c) One script after the producer records.** Only ptm.py (the proves-too-much control, the D-5
  identity, and the curve-free group computation for J4) was written after the producer records were
  read.
- **(d) Shared scratchpad; my files moved.** The session scratchpad is shared with the launching session
  and held files I did not create. I listed their names once and never opened them. I moved my own files
  into a subdirectory and re-ran every blind step there. The outputs were byte-identical except for
  wall-clock fields.
- **(e) The census was not recomputed** (J4 instruction).
## Blind re-derivation (done FIRST; written before any producer record was opened)

**What was re-derived.** The plan's `blind_rederivation.quantity`: for m = 3 and m = 4, the F_p-root
multiset of S_m(x_1..x_{m-1},T) on the factor-base locus equals { x(sum eps_i P_i) } and has size
2^{m-2} with multiplicity. The only inputs were the plan's statement of the quantity and its parameter
note, the group law, and the textbook definition of summation polynomials. When this section was
written, I had opened only the card, the plan extraction, the queue card and the role and contract
documents. No producer record had been opened (EV-MONO-a0a89c, DEC-20260810-2f86db and the rest came
later), and no blind_from path has been opened at any point.

### Derivation

Setting: p > 3 prime, E: y^2 = x^3 + ax + b over F_p, K = algebraic closure. x: E -> P^1 has degree 2,
x(O) = infinity and x(-P) = x(P). S_2 = x_1 - x_2,
S_3(x_1,x_2,x_3) = (x_1-x_2)^2 x_3^2 - 2((x_1+x_2)(x_1x_2+a)+2b) x_3 + (x_1x_2-a)^2 - 4b(x_1+x_2), and
S_m = Res_X(S_{m-1}(x_1..x_{m-2},X), S_3(x_{m-1},x_m,X)). Two facts are used. The defining property is
that for x_i in K, S_m(x_1..x_m) = 0 iff there are P_i in E(K) with x(P_i) = x_i and sum P_i = O. The
degree fact is deg_{x_i} S_m = 2^{m-2}. Both come from Semaev, "Summation polynomials and the discrete
logarithm problem on elliptic curves", IACR ePrint 2004/031, and that citation is **recalled**: a
pointer, not support. For m = 3 and 4 I verify both below by construction and computation, so the
m = 3, 4 conclusions do not rest on the recollection.

Fix P_1..P_{m-1} in E(F_p), affine, with x_i = x(P_i), and put f(T) = S_m(x_1..x_{m-1},T) in F_p[T].
The sign classes are the eps in {+1,-1}^{m-1} with eps_1 = +1. There are 2^{m-2} of them, since
x(sum eps_i P_i) is invariant under eps -> -eps. Write Q_eps = sum eps_i P_i, which lies in E(F_p), and
n_O = #{eps : Q_eps = O}.

1. **Sign sums are roots.** If Q_eps != O, the m points eps_1P_1..eps_{m-1}P_{m-1}, -Q_eps have
   x-coordinates x_1..x_{m-1}, x(Q_eps) and sum to O. So f(x(Q_eps)) = 0.
2. **Exhaustion as a set, over K.** Suppose f(t) = 0 with t in K. The "only if" direction gives points
   P'_i with x(P'_i) = x_i, and the only such points are +/-P_i. It also gives P'_m with x(P'_m) = t and
   sum P' = O. So P'_m = -Q_eps for some eps, with Q_eps != O because t is affine. Every root of f in K
   is therefore some x(Q_eps), and every such value is in F_p. Also f is not identically 0, since
   otherwise every t in K would be a root. **So f splits completely over F_p.**
3. **Multiplicity, which is the exhaustion direction the prior flags.** Consider generic P on E^{m-1}.
   - The 2^{m-2} functions r_eps = x o sigma_eps are pairwise distinct. The reason: r_eps = r_eps'
     forces sum (eps_i -/+ eps'_i) P_i to be identically O, which is impossible unless eps = +/-eps',
     because [2] != 0.
   - Each r_eps is a root (step 1).
   - deg_T S_m = 2^{m-2}.

   Hence S_m(x_1..x_{m-1},T) = L * prod_eps (T - r_eps), with L = LC_T S_m. For m = 3 this identity is
   checked symbolically modulo the curve equations, with L = (x_1-x_2)^2. For m = 4 it follows from
   Res(F,G) = lc(F)^{deg G} prod_{F(u)=0} G(u):

   S_4(x_1,x_2,x_3,T) = (x_1-x_2)^4 S_3(u_+,x_3,T) S_3(u_-,x_3,T), with u_+/- = x(P_1 +/- P_2).

   Applying the m = 3 formula to each factor gives

   (x_1-x_2)^4 (u_+ - x_3)^2 (u_- - x_3)^2 prod_{+/-,+/-} (T - x(P_1 +/- P_2 +/- P_3)).

   **Specialization.** Take a generic curve germ gamma through the base point. Along it, r_eps has a
   pole exactly when Q_eps = O. Write g = S_m(x(gamma(t)),T) = c(t) * prod_bad (1 - T/r_eps) *
   prod_good (T - r_eps). Content is multiplicative (Gauss), and g mod t = f is not 0, so v(c) = 0.
   Therefore **f = c(0) * prod_{eps: Q_eps != O} (T - x(Q_eps)), with c(0) != 0.**

**Result.** On the factor-base locus, at every m where the two recalled facts hold (proved here for
m = 3, 4 by construction):

- (i) f = c * prod_{eps: Q_eps != O} (T - x(Q_eps)) with c != 0, and f splits completely over F_p.
- (ii) deg f = 2^{m-2} - n_O.
- (iii) The root multiset of f is { x(Q_eps) : Q_eps != O }. Each value's multiplicity is the number of
  sign classes that share it.
- (iv) Homogenized to a binary form of degree 2^{m-2}, the root multiset in P^1 is exactly
  { x(Q_eps) } over all 2^{m-2} classes, with infinity = x(O) counted n_O times. Every root is
  F_p-rational.
- (v) Frobenius fixes every root, so the Frobenius cycle type is trivial on every fibre over the locus.
  On a generic fibre (squarefree, full degree) it is 1^{2^{m-2}}.
- (vi) The degree drops (n_O > 0) exactly on S_{m-1}(x_1..x_{m-1}) = 0, that is, where the base tuple
  itself carries a signed relation to O. This rests on two identities: LC_T S_3 = S_2^2 and
  LC_{x_4} S_4 = S_3(x_1,x_2,x_3)^2, both verified symbolically.
- (vii) Two sign classes collide, x(Q_eps) = x(Q_eps'), iff Q_eps = +/-Q_eps'. That holds iff some
  signed partial sum over a nonempty index set is 2-torsion or O. Cases include P_i = +/-P_j,
  2-torsion P_i, and P_i + P_j in E[2].

**Two corrections to the statement as the plan words it:**

- **B-1.** "Exactly 2^{m-2} values" fails for distinctness wherever (vii) holds.
- **B-2.** "Size 2^{m-2} with multiplicity" is true only in P^1, or off the sublocus in (vi). On that
  sublocus the affine root count of f is 2^{m-2} - n_O, and it falls as low as 0. At m = 4 that happens
  when P_1, P_2, P_3 are the three nonzero 2-torsion points: f is then a nonzero constant (16 on C1,
  578 on C5).

Neither correction touches splitting, membership in the sign set, or the triviality of Frobenius.

### Own S_4 construction (code and output in `s4_construction/computations.json`)

- **Route A:** sympy 1.14.0 `resultant(S_3(x_1,x_2,X), S_3(x_3,x_4,X), X)` over Z[a,b,x_1..x_4].
  **Route B:** PARI 2.15.4 `polresultant`, a code base disjoint from sympy. The two agree **exactly**:
  the difference is the zero polynomial.
- S_4 has 540 terms over Z[a,b] and content 1. It has degree 4 in each x_i and total degree 12 in x. It
  is symmetric under all 24 permutations of x_1..x_4. LC_{x_4} S_4 = S_3(x_1,x_2,x_3)^2 holds exactly.
- sha256 of the canonical term list: `dcd2d3508a2bc9e0c398cd7985510363a9fb071f58194e4ce140e177e0ed8c67`.
- S_3 is symmetric with degree 2 in each variable, and LC_{x_3} S_3 = (x_1-x_2)^2.
- The m = 3 product formula (x_1-x_2)^2 (T - x(P_1+P_2))(T - x(P_1-P_2)) = S_3(x_1,x_2,T) holds
  identically modulo y_i^2 = x_i^3 + a x_i + b.
- For the extra m = 5 check, S_5(x_1..x_4,T) is the formal-degree 6x6 Sylvester determinant computed by
  PARI `matdet`. It was unit-tested against sympy `resultant` on 3 tuples and agreed.

### Parameters and instances

| curve | p | a | b | #E(F_p), own = PARI | E[2](F_p) | use |
|---|---|---|---|---|---|---|
| C1 | 101 | -7 | 6 | 96 | full (x = 1, 2, 98) | exhaustive m=3 (2,401 ordered pairs), m=4 (117,649 ordered triples), degeneracies |
| C2 | 211 | 3 | 8 | 204 | one point (x = 46) | exhaustive m=3 (10,404 ordered pairs), m=4 (182,104 unordered triples; S_4 is symmetric); random FB |
| C3 | 1009 | 473 | 415 (seeded) | 1005 | none | random FB |
| C4 | 1999 | 1291 | 1494 (seeded) | 2000 | one point | random FB |
| C5 | 1009 | -7 | 6 | 1056 | full (x = 1, 2, 1006) | random FB, degeneracies |

C2 is the curve the plan names as the producer's. I used it only as one of five curves, for
comparability. The random factor base is FB = { affine P in E(F_p) : x(P) < ceil(p/3) }. The exhaustive
runs cover every affine rational x-value, so they contain every factor base on C1 and C2.

Every tuple was checked for five things:

- f splits into linear factors over F_p, which means no root lies outside F_p even over K.
- The root multiset from FLINT factorization equals the sign-sum multiset from my own group law.
- deg f = 2^{m-2} - n_O.
- The exact polynomial identity f = lc(f) * prod_{Q_eps != O} (T - x(Q_eps)) holds in F_p[T].
- On every random and degenerate tuple, a disjoint cross-check agrees: PARI `elladd` for the group law
  and PARI `factormod` for factorization. My group law also matches PARI `elladd` on the full 96 x 96
  addition table of C1, with 0 mismatches.

### Results (all raw outputs in `computations.json`)

| set | m | tuples | pass | generic fibre (squarefree, full degree) | full degree, repeated root | degree drop |
|---|---|---|---|---|---|---|
| C1 exhaustive | 3 | 2,401 | 2,401 | 2,070 | 282 | 49 (exactly the x_1 = x_2 pairs) |
| C1 exhaustive | 4 | 117,649 | 117,649 | 71,328 | 41,853 | 4,468 |
| C2 exhaustive | 3 | 10,404 | 10,404 | 10,100 | 202 | 102 |
| C2 exhaustive (unordered) | 4 | 182,104 | 182,104 | 158,432 | 20,204 | 3,468 |
| random FB, C2/C3/C4/C5 | 3 | 4 x 100 | 400 | 388 | 6 | 6 |
| random FB, C2/C3/C4/C5 | 4 | 4 x 100 | 400 | 367 | 31 | 2 |
| random FB, C2/C3/C4/C5 (extra) | 5 | 4 x 25 | 100 | 74 | 21 | 5 |

- **Zero failures in every set.** For m = 4 random factor-base tuples, the plan requires at least 20;
  400 were run, 25 per curve for C3 and C4 are listed in raw form, and every one was PARI-cross-checked.
- **Where the category counts come from.** The large repeated-root share on C1 is expected, because
  C1 has full rational 2-torsion and p is small. The degree-drop counts are the tuples on
  S_{m-1}(x_1..x_{m-1}) = 0.

**Degeneracies (J1(c)), constructed on C1 and on C5 with identical outcomes.** In every case f splits
completely over F_p, the root multiset equals the sign-sum multiset, deg f = 4 - n_O, the exact identity
holds, and PARI agrees.

| instance (m=4 unless stated) | deg f | n_O | roots (C1) |
|---|---|---|---|
| P_2 = P_1, or P_2 = -P_1 (the same x-tuple) | 4 | 0 | x(P_3) double, plus x(2P_1 +/- P_3) |
| P_1 2-torsion | 4 | 0 | two double roots |
| coincident sum P_1+P_2 = T (T nonzero 2-torsion) | 4 | 0 | one double root x(T+P_3) |
| coincident sum x_2 = x_3 | 4 | 0 | x(P_1) double |
| P_1 = P_2 = P_3 | 4 | 0 | x(P_1) triple, x(3P_1) |
| x_1 = x_2 = x(T), T 2-torsion | 4 | 0 | x(P_3) with multiplicity 4 |
| signed sum = O: P_3 = -(P_1+P_2) | **3** | 1 | 3 simple roots |
| x_1 = x_2 and P_3 = 2P_1 | **3** | 1 | x(2P_1) double, x(4P_1) |
| two signed sums = O: P_1+P_2 = T, P_3 = T | **2** | 2 | one double root |
| P_1, P_2, P_3 = the three nonzero 2-torsion points | **0** | 4 | none (f = 16) |
| m=3: x_1 = x_2 | **1** | 1 | x(2P_1) |
| m=3: P_1 2-torsion; or P_1, P_2 distinct 2-torsion | 2 | 0 | one double root |
| m=3: x_1 = x_2 = x(T), T 2-torsion | **0** | 2 | none (f = (3e^2+a)^2 = 16) |

**What happens to multiplicity and to the statistic.** A multiplicity is exactly the number of sign
classes that share a value. Frobenius is the identity on every root in every instance. A fibre is
excluded from being "generic" (squarefree and full degree) only by B-1 or B-2, and whether the frozen
instrument discards such fibres cannot be checked blind, because the instrument lies under blind_from.

**Blind_from statement.** I did not open, list, grep, import or otherwise read any path under
`experiments/EXP-MONO-4b50b6/` or `coordination/goals/GOAL-MONO-001/batches/BATCH-003/`, before or
after this section was written. No repository-wide search was run. The code was written in this session
from the definitions above. `blind_from_respected: true`.

## Exact scope of the claims under review (restated)

- **Route (c) object.** DEC-20260810-2f86db `closed_at_scope`: "The generic-fibre Frobenius cycle-type
  census, in the frozen instrument form of EXP-MONO-4b50b6, AS A PROBE OF INDEX-CALCULUS RELATION RATE,
  at every m."
  - It is grounded in EV-MONO-a0a89c OBS-5.
  - Scope: prime fields F_p with p > 3, E: y^2 = x^3 + Ax + B nonsingular, the ordered base
    (x_1..x_{m-1}), and every m >= 3. The general-m part is by derivation.
  - The empirical corroboration uses toy primes only.
  - There is no solver and no budget. Claim tier: toy.
- **Route (a) candidate.** H-MONO-ebd400 / EV-MONO-e9dc3b (DEC-20260904-dd58c3): "full S_4 monodromy at
  m=4 over the symmetric base, at toy scale, on 4 curves at 2 primes".
  - The census is EXP-MONO-0e6e8f (p = 101, 1009; C1/C2 exhaustive over F_101^3, C3/C4 100,000
    draws each). Claim tier: toy.
- Neither is an ECDLP result, and no security estimate moves.

## J1 — derivational soundness of the no-go — verdict: **CONCUR** (with two required scope corrections)

**Method.**

- The blind re-derivation came first (section above). Only then did I compare it with the producer's
  wording: EV-MONO-a0a89c OBS-5 and DEC-20260810-2f86db D-1.
- I attacked the exhaustion direction first. On two curves I fully factored every factor-base-locus
  fibre over F_p and checked the exact identity f = lc(f) * prod (T - x(Q_eps)), so every root in the
  algebraic closure, with multiplicity, is accounted for.
- I then checked completeness, exactness and the constructed degeneracies (J1(a)-(c)).
- The general-m step rests on Semaev's Theorem 1, which I **retrieved and read**
  (https://eprint.iacr.org/2004/031.pdf, 5 Feb 2004, sha256 `1cab0ae6…c7d6`, provenance `retrieved`,
  verified_by TASK-20260930-40470a). It states:
  - the defining property, in both directions;
  - symmetry and degree 2^{n-2} in each variable;
  - f_n = f_{n-1}^2 X_n^{2^{n-2}} + ..., i.e. the leading coefficient in X_n is f_{n-1}^2.

**What was built and computed.** Everything is in `computations.json`.

- S_3 and S_4 were built by two disjoint routes. The m = 3, 4 checks were exhaustive on C1 and C2, and
  the random factor-base checks ran at m = 3, 4, 5 on four curves.
- The degeneracies of J1(c) were constructed on C1 and C5.
- Symbolic identities: LC_{x_4} S_4 = S_3(x_1,x_2,x_3)^2 and LC_{x_3} S_3 = (x_1-x_2)^2.

**Findings.**

- **(a) Completeness holds.** Every factor-base-locus fibre tested splits into linear factors over F_p,
  so no root lies outside F_p even over the algebraic closure. Coverage:
  - m = 4: 117,649 ordered triples on C1 and 182,104 unordered triples on C2 (all rational x-values,
    so every factor base on those curves), plus 400 random factor-base triples (at least 20 were
    required), every one cross-checked with PARI;
  - m = 3: 2,401 + 10,404 exhaustive pairs and 400 random;
  - m = 5: 100 random.

  Zero failures.
- **(b) Exactness with multiplicity holds** in this precise form: f = c * prod_{eps: Q_eps != O}
  (T - x(Q_eps)), with c != 0. No root lies outside the sign-sum set. A root's multiplicity equals the
  number of sign classes that share its value.
- **(c) Degeneracies (P_i = +/-P_j, 2-torsion P_i, coincident sums, signed sums equal to O).** In every
  instance f splits completely and Frobenius is the identity on every root. They lead to two
  corrections of the wording:
  - **SC-1 (distinctness; the case the prior anticipated).** "2^{m-2} values" are not distinct when some
    signed partial sum is 2-torsion or O. Multiplicities of 2, 3 and 4 were observed. This is a scope
    correction under the plan's own carve-out.
  - **SC-2 (degree drop; not anticipated by the plan).** Take the sublocus S_{m-1}(x_1..x_{m-1}) = 0,
    where the base tuple itself carries a signed relation sum eps_i P_i = O. There
    deg_T f = 2^{m-2} - n_O, down to 0:
    - f is a nonzero constant when P_1, P_2, P_3 are the three nonzero 2-torsion points (m = 4), or
      when x_1 = x_2 is a 2-torsion x-value (m = 3);
    - the missing roots sit at T = infinity = x(O), which is F_p-rational in P^1;
    - the leading-coefficient law behind this is Semaev's Theorem 1, and I verified it symbolically at
      m = 3, 4.

    The producer's own m = 3 statement carried the needed qualifier: OBS-4 says "x1 != x2", which is
    exactly this sublocus at m = 3. OBS-5 and D-1 drop it when they generalize ("2^{m-2} values
    matching deg_T S_m"). The later m = 4 lane states the precise form (EXP-MONO-0e6e8f execution
    report, Stage-0 checks 0c/0d): "Q_e's roots are exactly the finite sign-class sums" and
    "deg_T Q_e = 4 - #(sign classes summing to O)".
- **Effect on the statistic: none.**
  - On every factor-base-locus fibre, Frobenius fixes every root, affine and at infinity. On every
    generic fibre (squarefree, full degree) the cycle type is exactly 1^{2^{m-2}}.
  - The frozen instrument sorts degree-drop and ramified fibres into their own strata (EV-MONO-a0a89c
    OBS-3: N_degdrop, N_ramified), so the generic-fibre statistic never sees them.
  - The corrected wording still matters to anyone who counts fibres, because at toy primes the
    non-generic share of the factor-base locus is not small: 46,321 of 117,649 on C1 (39%) and 23,672 of
    182,104 on C2 (13%).
- **"At every m".** This is derivational. Its load-bearing external facts are now `retrieved` rather
  than recalled. The producer's records attribute it to "the group law" and cite no source for the
  defining property. The computational corroboration covers m = 3, 4 exhaustively on two curves and
  m = 5 at random.
- **A strengthening, not required by J1.** Off the factor-base locus, the cycle type of every
  *generic* ordered-base fibre is fixed by the quadratic characters chi(f(x_i)) at every m (the
  delta-rule under proves-too-much below: 0 disagreements on 967,678 generic fibres).
  - So, fibre by fibre, the instrument reads nothing but those characters.
  - The curve can still enter at O(1/p) through *which* fibres are non-generic and so excluded. Compare
    the #E[4] fine structure that KN-FIND-edd62c records on the symmetric base. That is not a
    relation-rate reading either.
  - The no-go therefore does not depend on the census being evaluated on the factor-base locus.

**Breaking-artifact assessment.**

- Clause 1 (fails to split): not found.
- Clause 2 (a root outside the sign-vector set): not found.
- Clause 3 (root count differs from 2^{m-2} with multiplicity): **met literally by SC-2** for the affine
  count on the proper closed sublocus S_{m-1} = 0.

I classify SC-2 as a scope correction, not a break, for four reasons:

- it leaves splitting, sign-set membership and the triviality of Frobenius intact;
- counted in P^1, the root multiset is exactly the 2^{m-2} values x(sum eps_i P_i), with multiplicity;
- the frozen instrument already separates these fibres into their own stratum;
- the prior gives the same reasoning for distinctness: it "would weaken the wording but not the no-go".

**This classification is my judgement**, because the plan's carve-out names only distinctness. A
composer who reads clause 3 literally turns J1 into a DISSENT on wording only, and adopting the
corrected statement below cures it.

**Corrected statement (to be carried into any closure or knowledge wording).**

- Setting: p > 3, E/F_p nonsingular, P_1..P_{m-1} in E(F_p) affine, and x_i = x(P_i).
- Then S_m(x_1..x_{m-1},T) = c * prod_{eps in {+1,-1}^{m-1}, eps_1 = +1, sum eps_i P_i != O}
  (T - x(sum eps_i P_i)), with c in F_p^*.
- It splits completely over F_p.
- Its degree is 2^{m-2} minus the number of sign classes whose sum is O. It is exactly 2^{m-2} iff
  S_{m-1}(x_1..x_{m-1}) != 0.
- Counted in P^1, its roots are the 2^{m-2} values x(sum eps_i P_i) with multiplicity, where
  x(O) = infinity.
- Frobenius fixes every root, so the cycle type is 1^{2^{m-2}} on every generic fibre over the
  factor-base locus.

**Verdict: CONCUR.** The no-go is derivationally sound: on the factor-base locus the generic-fibre cycle
type is identically 1^{2^{m-2}}, at every m where Semaev's Theorem 1 applies (every m >= 3, char != 2, 3).
The wording must adopt SC-1 and SC-2.

**Reading declaration (J1).**

- The card, the plan extraction and the queue card, read before the blind derivation.
- After the blind section was written:
  - EV-MONO-a0a89c (OBS-3, OBS-4, OBS-5, boundaries);
  - DEC-20260810-2f86db (D-1, limitations);
  - DEC-20260802-a51c82 (D-4);
  - EXP-MONO-0e6e8f/execution_report.yaml (Stage-0 checks 0c, 0d; used only for the precision
    comparison);
  - Semaev 2004 (retrieved).
- Code: s4_build.py, fb_checks.py, degeneracies.py, t5.py, ptm.py (object 1).

## Proves-too-much control (both named objects)

D-1's argument, as recorded, has four steps:

1. The roots of S_m(x_1..x_{m-1},T) are x(sum eps_i P_i).
2. If every P_i is F_p-rational, every sum eps_i P_i is F_p-rational.
3. So every root lies in F_p and the fibre splits completely.
4. So the cycle-type statistic is constant.

**Object 1: a generic base tuple (x_i in F_p, not required to be x-coordinates of F_p-points). The
argument stops at step (2).**

- Step (1) holds for any x_i: the P_i then lie in E(F_p^2).
- Step (2) fails exactly at the locus boundary. If f(x_i) is a non-square, P_i lies on the quadratic
  twist and Frob(P_i) = -P_i.
- Carrying the argument on honestly gives Frob(sum eps_i P_i) = sum eps_i delta_i P_i, with
  delta_i = chi(f(x_i)). So Frobenius permutes the sign classes by eps -> eps*delta.
- Hence on a generic fibre the cycle type is 1^{2^{m-2}} iff delta = +/-(1..1). Otherwise it is a
  fixed-point-free involution. I call this the **delta-rule**.
- The argument therefore proves the delta-rule, not constancy, and the statistic varies. Measured
  against full factorization over F_p:

| set | tuples | generic fibres | cycle types seen (generic) | delta-rule agrees / disagrees |
|---|---|---|---|---|
| C2 (p=211) m=3, all of F_p^2 | 44,521 | 43,890 | 1+1: 21,872; 2: 22,018 | 43,890 / 0 |
| C1 (p=101) m=4, all of F_p^3 | 1,030,301 | 824,256 | 1^4: 176,544; 2+2: 647,712 | 824,256 / 0 |
| C3 (p=1009) m=4, 50,000 random | 50,000 | 49,806 | 1^4: 12,501; 2+2: 37,305 | 49,806 / 0 |
| C4 (p=1999) m=4, 50,000 random | 50,000 | 49,726 | 1^4: 12,316; 2+2: 37,410 | 49,726 / 0 |

A consequence used in J2 and J4 (reviewer derivation, confirmed above):

- On the **ordered base** (x_1..x_{m-1}), the monodromy of the S_m cover is the regular elementary
  abelian group (Z/2)^{m-2}, for every nonsingular curve.
- At m=4 that group is V_4. Among 923,788 generic m=4 fibres, not one showed a transposition, a
  3-cycle or a 4-cycle.

**Object 2: the D-4 swapped statistic (fix T = x(R), count factor-base-rational points on the
T-fibre). The argument transfers to Frobenius, not to the count.**

Setup: fix R in E(F_p) and x_2..x_{m-1} in V, where V is the set of factor-base x-values.

- By the symmetry of S_m (Semaev's Theorem 1), the roots in x_1 are x(R +/- P_2 +/- ... +/- P_{m-1}),
  and all of them are rational.
- So D-1's argument **does** carry over to a swapped *Frobenius* statistic, which is identically trivial
  on the factor-base locus:
  - C3 m=3: 52,710 / 52,710 swapped fibres split completely;
  - C2 m=3: 3,366 / 3,366;
  - C2 m=4: 111,078 / 111,078.
- It does **not** carry over to the D-4 statistic, which is a count of factor-base points on the
  T-fibre. "Every root lies in F_p" says nothing about membership in V, a thin subset of F_p, and that
  membership is what the count measures.

N(R) = the number of ordered factor-base tuples on the fibre over x(R). It varies:

| curve / m | factor base | x(R) values | N(R) min..max (mean) | distinct values | roots in V per swapped fibre |
|---|---|---|---|---|---|
| C3 p=1009, m=3 | x < 200, #V = 105 | 502 | 24..68 (43.72) | 41 | 0: 33,020; 1: 17,435; 2: 2,255 |
| C2 p=211, m=3 | x < 71, #V = 33 | 102 | 8..30 (21.03) | 17 | 0: 1,572; 1: 1,443; 2: 351 |
| C2 p=211, m=4 | x < 71, #V = 33 | 102 | 693..1470 (1359.62) | 74 | 0..4 |

- N(R) was computed two independent ways, from polynomial roots in V and from group-law sign sums. The
  two agree for every R on all three sets.
- The argument stops exactly at the step "rational" => "in the factor base", which does not follow.
- **D-1 does not condemn its named successor.** D-5, a separate provision of the same decision, does
  make the illegitimate transfer; see J2 O-1.

**Failure signature.** It is not triggered for D-1 on either object. Both objects fall outside what
D-1 proves, and the stopping steps are named above: step (2) for object 1, and the step from rational
to factor-base membership for object 2.

## J2 — scope honesty (widened) — verdict: **DISSENT** (narrow; the cure is named)

**Method.**

- The proves-too-much control above.
- A symbolic check of D-5's transport identity (ptm.py, sympy).
- A line-by-line overreach audit of DEC-20260810-2f86db and the goal head, plus the grounding evidence
  record EV-MONO-a0a89c. I looked for readings that close the relation-rate half, condemn the D-4
  statistic, or close any statistic other than the generic-fibre cycle type.
- A staleness audit against the later records: DEC-20260904-dd58c3, H-MONO-ebd400, EV-MONO-e9dc3b,
  EXP-MONO-0e6e8f, KN-FIND-edd62c, KN-FIND-19f5ea, DEC-20260905-021e6e, DEC-20260930-3a0b7b and the
  current goal head.

**What holds (no overreach).** The following are honest and narrow:

- `closed_at_scope`;
- `not_closed` (the relation-rate question; the imprimitivity half; the D-4 swap);
- `limitations` ("It is not a no-go for the relation-rate question, for KN-OPEN-009 as a whole, or for
  any other statistic");
- D-2's deliberate refusal of DEC-20260802-a51c82 N-1's broader phrase;
- "No m >= 4 census in that form is authorized".

The m=4 symmetric-base census (EXP-MONO-0e6e8f) is a monodromy census, not the rejected relation-rate
instrument form. The no-go neither licenses it nor forbids it. I found no reading of DEC-20260810-2f86db
that closes the relation-rate half or any statistic other than the generic-fibre cycle type.

**Overreach findings.**

- **O-1 (produces the breaking artifact, at m=3): D-5 + N-2, carried by the goal head.**
  - The goal head says: "the D-4 direction swap remains an UNTESTED proposal gated on its D-5 m=3
    collapse check".
  - D-5 says: "if the transport holds, the swapped route is dead at m=3 and only m >= 4 remains open for
    it".
  - N-2 says: "If YES, the swapped statistic collapses at m=3 exactly as the original did and only
    m >= 4 remains for that route - report the collapse as the result."
  - **The transport holds identically.** disc_{x2} S_3(x1,x2,T0) - 16 f(x1) f(T0) = 0 as a polynomial,
    checked symbolically. It is forced by the symmetry of S_3, which D-5 itself names.
  - **The consequent is false for the statistic D-4 and N-2 define**, "the count of FB-rational points
    on the fibre of the projection to the T-line at fixed T = x(R)":
    - on the factor-base locus chi(f(x_1) f(x(R))) = +1 identically (52,710 / 52,710 pairs on C3);
    - yet N(R) ranges over 24..68, taking 41 distinct values on C3, and over 8..30 on C2.
  - What the transport governs is a swapped *Frobenius* statistic. That statistic is trivial on the
    factor-base locus for the same reason as D-1. The count is a different thing.
  - Followed as written, the record would therefore declare the D-4 successor dead at m=3, on a check
    that cannot fail. That is the premature-closure failure mode of docs/inventor-protocol.md §4.
  - Label: **overreach (condemns the D-4 swapped statistic at m=3).**
  - Cure: a Coordinator correction that supersedes D-5's disposition and N-2's directive. It should
    record three things: the transport holds trivially; it shows only that a swapped Frobenius or
    cycle-type statistic is trivial on the factor-base locus; and the factor-base-point count is not
    condemned at m=3 or at any m.
- **O-2 (grounding record; neutralized in the decision).**
  - EV-MONO-a0a89c's `inference` says "the relation-supply half of KN-OPEN-009 is answered at EVERY m by
    the group law". That reads as closing the relation-rate half.
  - DEC-20260810-2f86db D-2 narrows it explicitly, but no correction record supersedes the evidence
    sentence, and DEC-20260930-3a0b7b cites EV-MONO-a0a89c.
  - Label: overreach, neutralized by D-2. Any closure decision that cites EV-MONO-a0a89c must carry
    D-2's narrowing explicitly.
- **O-3 (goal head).**
  - IMP-2 `what_is_blocked` says "NOT a blocker on GOAL-MONO-001's own already-closed criteria".
  - No completion criterion has been adopted as met by any committed decision (DEC-20260930-3a0b7b).
    DEC-20260904-dd58c3 and DEC-20260905-021e6e both record `completion_criteria_met: []`.
  - Label: overreach (misstates criterion status). It is not about a statistic, but it could mislead a
    closure composer.
- **O-4 (later records; outside the no-go).**
  - DEC-20260904-dd58c3 next_action (3) says "no exceptional locus at this arity". The goal head's
    `next_action_2026_09_04` says "DECISIVELY CONFIRMED, closing the m=4 imprimitivity sub-thread".
  - Both go beyond their cited evidence, a census on 4 curves at 2 primes.
  - The statement is true for the symmetric base by the group-law derivation in J4, which no committed
    record I read states.
  - Label: overreach relative to the cited evidence, not relative to the truth.

**Transfer test (breaking-artifact clause 3).**

- D-1's argument structure transfers to a swapped Frobenius statistic, which is trivial, and not to the
  swapped count, which varies. So there is no demonstration that D-1 transfers to "the swapped
  statistic" as D-4 defines it.
- D-1 in fact supports more than the record claims: by the symmetry of S_m, *every* Frobenius
  cycle-type statistic on *any* coordinate projection is trivial on the factor-base locus. That is an
  underclaim, and it constrains how a D-4 instrument must be built: as a count, not a cycle type.

**Staleness, which later records or this review make out of date.** Each item is an underclaim unless
labelled otherwise.

- **S-1.** D-3 and the goal head's `next_action` say the "imprimitivity half ... stays LIVE and
  non-degenerate at m >= 4".
  - This is stale at m=4 on the symmetric base, where H-MONO-ebd400 and DEC-20260904-dd58c3 settled it.
  - On the **ordered base**, the parameter space KN-OPEN-009 states, the group law gives monodromy
    (Z/2)^{m-2} for every nonsingular curve, imprimitive at every m >= 4. Source: object 1 plus the
    curve-free group computation.
  - On the symmetric base, the group law gives (Z/2)^{m-2} ⋊ S_{m-1}, of order 2^{m-2}(m-1)!:
    - S_4 at m=4;
    - imprimitive at m = 5 and 7;
    - primitive but proper at m=6 (orders 24, 192, 1920, 23040 for m = 4..7).
  - Label: underclaim.
  - A precision note, not a no-go finding: DEC-20260904-dd58c3's limitation says the "same lemma ...
    H-MONO-93bc4d proved gives a PROPER, imprimitive subgroup of Sym(2^{m-2})" for m >= 5. If that
    refers to the symmetric base, it is inaccurate at m=6, where the group is proper but primitive. If
    it refers to the ordered base, it is correct. H-MONO-93bc4d is outside my read scope.
- **S-2.** EV-MONO-a0a89c's boundaries say "OBS-1, OBS-2, OBS-3 and OBS-6 are m=3 ONLY ... no analogue
  at m >= 4".
  - The group law supplies the analogue at every m: the delta-rule, with 0 disagreements on 967,678
    generic fibres. On every generic fibre, the ordered-base census reads only the quadratic characters
    of f(x_i).
  - Label: underclaim. It strengthens the no-go.
- **S-3.** D-1/OBS-5's "2^{m-2} values matching deg_T S_m" is less precise than EXP-MONO-0e6e8f's
  Stage-0 checks 0c/0d. See J1 SC-1/SC-2. Label: wording.
- **S-4.** DEC-20260810-2f86db's `knowledge_promotion` intends to split KN-OPEN-009 into "a still-open
  imprimitivity question at m >= 4". This is stale for the same reasons as S-1, and it matters to the
  supersession that composition item C-4 describes. Label: underclaim.
- **S-5.** D-10 says "GOAL-MONO-001 has no hypothesis record".
  - That is no longer true. H-MONO-ebd400 carries goal_id GOAL-MONO-001, and DEC-20260905-021e6e
    moves two further MONO hypotheses in this goal's thread. The head's `active_hypothesis_ids` is
    still [].
  - Label: factual staleness. A closure must not move H-MONO-ebd400.
- **S-6.** Procedural staleness:
  - D-8 and the IMP-1 `clears_when` require a "model-INDEPENDENT review from a second inference
    backend". DEC-20260930-3a0b7b R-2 superseded that requirement.
  - The goal head's "fresh budget grant from GOAL-PATH-001" is superseded by the unlimited ECC budget
    (head IMP-1.budget_half_cleared_20260904).
  - "paused" and "STILL BLOCKED ON REVIEW" are read under rule 10 as impediments.
- **S-7.** RQ-MONO-001's title is scoped to m=3, as EV-MONO-e9dc3b and CORR-20260904-33fbf3 already
  flag. Label: housekeeping.

**Verdict: DISSENT.** It rests on **O-1 alone**, which produces the breaking artifact "the D-4 swapped
statistic is condemned" at m=3.

- The core scope statements of the no-go (D-1, D-2, `closed_at_scope`, `not_closed`, `limitations`) are
  honest. I do not dissent from them.
- O-2 to O-4 and S-1 to S-7 are recorded findings, but none of them is the ground of the dissent.
- The cure for O-1 is named above. It needs no new runs.

**Reading declaration (J2).**

- DEC-20260810-2f86db (all); ledger/goals/GOAL-MONO-001/goal.yaml (all); EV-MONO-a0a89c (all).
- DEC-20260802-a51c82; DEC-20260904-dd58c3; H-MONO-ebd400; EV-MONO-e9dc3b.
- EXP-MONO-0e6e8f specification and execution report; CORR-20260904-33fbf3.
- KN-FIND-edd62c; KN-FIND-19f5ea; DEC-20260905-021e6e; DEC-20260930-3a0b7b.
- KN-OPEN-009; RQ-MONO-001.
- Code: ptm.py.

## J3 — adequacy for criterion (c) — verdict: **DISSENT** (as recorded; the cure needs no runs)

**Method.** I built the quote trail and checked the commit status of the record in git metadata only
(`git log`/`git merge-base` on the named paths). No new mathematics is needed beyond J1 and J2.

**Quote trail.**

| requirement | where it is met, quoted |
|---|---|
| Criterion (c), goal.yaml `completion_criteria` | "Committed decision that either (a) ..., or (b) ..., or (c) a scoped instrument/protocol no-go is recorded." |
| committed Coordinator decision | DEC-20260810-2f86db, `decided_by: coordinator`, `decision: reject_scoped`. First committed in 07cff851d on 2026-08-10, unmodified since, and contained in origin/main. |
| scoped | `closed_at_scope`: "The generic-fibre Frobenius cycle-type census, in the frozen instrument form of EXP-MONO-4b50b6, AS A PROBE OF INDEX-CALCULUS RELATION RATE, at every m." |
| instrument/protocol | `decision_note`: "WHAT IS REJECTED IS THE INSTRUMENT, NOT THE QUESTION." |
| no-go | D-1: "That is a genuine no-go for the instrument, and it is a no-go by derivation". |
| recorded | D-9: "(c) is satisfied when a scoped instrument no-go 'is recorded'. This decision RECORDS the no-go - as a Coordinator proposal whose adoption as official closure is gated on the rule-12 review". |
| consistent with DEC-20260802-a51c82 N-2 | N-2 reasoned only about (a): "criterion (a) required a census deciding full-versus-exceptional and the census was shown non-discriminating". D-6 records that (c) was never examined. There is no contradiction. |
| no hypothesis-status change | D-10 and `changes_no_hypothesis_status: true`. Closure under (c) moves no hypothesis; H-MONO-ebd400 stays `supported` (see S-5). |
| nothing beyond toy | D-10: "The claim tier ceiling stays toy"; `is_not_a_cryptanalytic_result: true`. |
| derivation versus measurement | docs/claims-and-verification.md ("Refutation artifacts") ranks a derivation note above empirical-only. So a no-go "recorded" by derivation is admissible, and D-6/D-9's reading holds on this point. |

**Gaps.** These make the record, **as it stands**, inadequate.

- **G-1 (inherits J2 O-1).** The J3 plan asks: "Is the no-go scoped (J2)?"
  - Not as recorded. The decision that would become the criterion-(c) object also carries D-5 and N-2,
    and those condemn the D-4 successor at m=3.
  - Adopting it unamended would carry that into the closure. It would also carry it into the
    KN-OPEN-009 supersession, which composition item C-4 says must land together with the closure.
- **G-2 (closure standard).** Neither DEC-20260810-2f86db nor EV-MONO-a0a89c carries an `obstruction`
  block.
  - AGENTS.md says: "Obstructions are measured ... The named obstruction is recorded as the `obstruction`
    block ... Prose alone does not satisfy the closure standard ... Every such block carries a
    `resource_check`".
  - templates/research-records.md says `obstruction` is "required ... on any record closing a lane".
  - Both rules entered the contract on **2026-08-14 (ee9e24659)**, four days *after* the no-go was
    committed. The no-go was therefore compliant when written. A closure adopted now is bound by them,
    and under that reading of "recorded" the no-go is recorded only as prose: a verdict, not a datum.
  - The block can be supplied without new mathematics:
    - `statement`: "generic-fibre Frobenius on factor-base-locus fibres is the identity";
    - `quantity`: the fraction of generic factor-base-locus fibres with non-trivial Frobenius;
    - `value`: exactly 0, by derivation;
    - `measured_by`: 0/1196 at m=3 in RUN-MONO-4b50b6-002 V4, as quoted in EV-MONO-a0a89c;
    - `scope`: J1's corrected statement;
    - `resource_check`: the D-4 direction swap *is* the resource reading, provided the D-5 correction
      lands first.
- **G-3 (minor; not a gap in (c)).** D-6 through D-9 frame closure as gated on a "model-independent"
  review. DEC-20260930-3a0b7b R-2 supersedes that framing, and C-10 requires the disclosure that this
  review is independent by session and role, not by model.

**Verdict: DISSENT** on adequacy **as recorded**, on grounds G-1 and G-2.

- Both can be cured inside the composed decision, with no new runs:
  - correct D-5 and N-2 (the J2 cure);
  - record the `obstruction` block with its `resource_check`;
  - carry J1's corrected statement.
- Once those are in place, I find nothing else in the quote trail that fails criterion (c).

**Reading declaration (J3).**

- goal.yaml; DEC-20260810-2f86db; DEC-20260802-a51c82; EV-MONO-a0a89c; DEC-20260930-3a0b7b.
- AGENTS.md ("Inventor protocol", "Goal closure quorum — SUSPENDED", "Goals are never paused");
  templates/research-records.md (Evidence schema, review plan, review attestation);
  docs/claims-and-verification.md; docs/inventor-protocol.md §4.
- Git metadata for these paths: DEC-20260810-2f86db, AGENTS.md, templates/research-records.md,
  DEC-20260904-dd58c3, EV-MONO-e9dc3b, H-MONO-ebd400, EV-MONO-a0a89c.

## J4 — adequacy of H-MONO-ebd400 / EV-MONO-e9dc3b for criterion (a) — verdict: **DISSENT**

**Method.**

- A quote-match of criterion (a) and the goal objective against EV-MONO-e9dc3b, H-MONO-ebd400, the
  EXP-MONO-0e6e8f specification and execution report, CORR-20260904-33fbf3 and DEC-20260904-dd58c3.
- **The census was not re-run or recomputed.** Every EXP-MONO-0e6e8f number below is quoted.
- Two reviewer inputs feed this joint:
  - the ordered-base cycle types of proves-too-much object 1;
  - a curve-free permutation-group computation over sign classes (ptm.py).
- Neither of these samples the symmetric base or re-runs EXP-MONO-0e6e8f.

**Texts compared.**

- Criterion (a): "the census agrees with full symmetric/wreath monodromy within stated error".
- The objective: "Decide KN-OPEN-009 at toy scope via a frozen Chebotarev/monodromy census protocol:
  full monodromy (barrier for relation-rate attacks) versus an exceptional locus with deviant rates."
- KN-OPEN-009's statement: "For the m-th Semaev summation cover over the parameter space of
  (x_1,...,x_{m-1}) ...".

**Reviewer derivation used below (derivation tier; in no committed record I read).**

Setting: K is the algebraic closure of F_p, with p > 3 and E nonsingular.

- **Symmetric base (m=4).**
  - Let x_1, x_2, x_3 be the roots of the generic cubic g(X) = X^3 - e_1X^2 + e_2X - e_3 over
    F = K(e_1,e_2,e_3).
  - The f(x_i) are squarefree polynomials in distinct variables, so no product of a nonempty subset of
    them is a square. Hence Gal(K(x_i,y_i)/F) = Z/2 wr S_3, of order 48.
  - By J1's product formula, the four roots of Q_e(T) = S_4(x_1,x_2,x_3,T) are x(P_1 +/- P_2 +/- P_3).
  - An element (delta, sigma) acts on these roots as an affine map on the sign classes F_2^3/<111>:
    delta gives the translation and sigma the linear part.
  - The image is AGL(2,2), which is S_4 of order 24, with kernel {+/-1}. The curve-free computation
    gives order 24 = |Sym(4)| at m=4.
  - So **the monodromy is S_4 for every nonsingular curve**, geometric and arithmetic alike. The census
    could not have found a proper subgroup.
  - The same argument gives (Z/2)^{m-2} ⋊ S_{m-1} for general m. The group orders 192, 1920 and 23040
    at m = 5, 6, 7 confirm that the kernel is {+/-1}.
- **Ordered base.** Gal(K(x_i,y_i)/K(x_1..x_{m-1})) = (Z/2)^{m-1}, and its image on the roots is
  (Z/2)^{m-2}, acting regularly. At m=4 that is **V_4**. Object 1 found only 1^4 and 2+2 among 923,788
  generic m=4 fibres.
- EXP-MONO-0e6e8f's own OBS-1 is consistent with this; I quote it, not recompute it:
  - the g-split block (base points whose x_i are all in F_p, i.e. the ordered base's F_p-points) lands
    in 1^4 or 2+2, except 12,429 instances in 2+1+1;
  - the same report records 14,963 ramified instances in class 2+1+1 pooled;
  - by the delta-rule, a squarefree, full-degree g-split fibre cannot be 2+1+1.

**The five questions.**

1. **Must "the census" be the EXP-MONO-4b50b6 instrument?**
   - No, textually. The objective says "a frozen Chebotarev/monodromy census protocol", and
     EXP-MONO-0e6e8f is frozen and approved (`frozen: true`, approved 2026-09-04). That alone is not a
     break.
   - But the objective ties the census to deciding KN-OPEN-009, whose cover is posed over the
     **ordered** base (x_1..x_{m-1}). EXP-MONO-0e6e8f censuses the **symmetric** base (e1,e2,e3), which
     is a different cover.
2. **Does m=4 on 4 curves at 2 primes meet "within stated error"?** No.
   - The only pre-registered error statement for a distributional comparison is M3: "Chi-square
     consistent with full S_4 density ... at conventional significance".
   - It failed:

     | curve | chi-square (df 4) |
     |---|---|
     | pooled | 2447.84 |
     | C1 | 1175.81 |
     | C2 | 1765.88 |
     | C4 | 12.13 (above the 0.05 critical value 9.49) |
     | C3 | 4.38 (the only pass) |

   - CORR-20260904-33fbf3 withdrew M3 as a wrong-null design defect: "NOT carried forward as evidence
     of any kind".
   - The exact finite-p null was derived **after** the data were seen. Against it, C1 still stands at
     **171.67 (df 4)**, with the residual attributed post hoc to an identified stratum of 2,459
     instances.
   - So no distributional agreement within a pre-stated error exists. What exists is an exact group
     identification (M1), for which "within stated error" is vacuous.
3. **Is "agrees with full ... monodromy" met by exhaustive identification rather than a distributional
   fit?**
   - The identification is sound group theory: a 4-cycle and a 3-cycle force S_4. It establishes S_4
     for the symmetric-base cover.
   - By the derivation above, that result is **forced by the group law for every curve**. So "no
     exceptional locus at this arity" is true by derivation, not by the census on 4 curves.
   - On KN-OPEN-009's stated ordered base, however, the m=4 monodromy is **V_4 for every curve**. A
     census there does *not* agree with full symmetric/wreath monodromy. The group is universally
     smaller, which is neither branch of the goal's dichotomy.
4. **Does CORR-20260904-33fbf3 affect the headline?**
   - It leaves the M1 headline (the group identity) untouched.
   - It removes the pre-registered distributional leg, which is exactly the "within stated error" leg
     of (a). So it matters for (a).
5. **Does the m=3 non-discrimination (DEC-20260802-a51c82 D-2) conflict with adopting (a)?** Yes.
   - N-2 ruled (a) unmet at m=3, although the m=3 census emitted FULL_MONODROMY_BARRIER_TOY (agreement
     with full S_2 within its envelope). The reason given: "the census was shown non-discriminating". It
     could not have failed (D-2).
   - At m=4 on the symmetric base, the outcome is equally forced (item 3).
   - Adopting (a) at m=4 while N-2 stands is therefore inconsistent. It would need N-2 to be superseded,
     with a stated reason why a forced m=4 outcome counts when a forced m=3 outcome did not.

**Other committed statements an adoption of (a) would have to supersede.**

- DEC-20260904-dd58c3's `scope_statement` says "Does not close KN-OPEN-009 ... Does not extend to
  m != 4". The same decision records `completion_criteria_met: []` and `closure_authorized: false`.
  The goal's objective is "Decide KN-OPEN-009".
- **An unresolved tension, not an independent ground.** DEC-20260810-2f86db N-3 (repeating
  DEC-20260802-a51c82 N-3) says: "No new census of any statistic may be dispatched before these [five
  OI-1 repairs] are carried."
  - On 2026-09-04 the goal head recorded those repairs as "still outstanding"
    (IMP-1.budget_half_cleared_20260904).
  - EXP-MONO-0e6e8f was approved and run on that same date, on the EXP-MONO-815525 harness, and does
    not mention them.
  - My inputs do not say whether the repairs were carried, or were judged inapplicable to that harness.

**Verdict: DISSENT.** The breaking artifact is met in both of its forms.

- **Readings of criterion (a) or the objective that the m=4 result does not satisfy:**
  - (i) KN-OPEN-009's ordered-base cover, where the m=4 monodromy is V_4 for every curve;
  - (ii) distributional agreement within a pre-stated error, where the pre-registered test failed and
    was withdrawn.
- **Committed statements that adopting (a) would contradict:**
  - DEC-20260802-a51c82 N-2's reading of (a);
  - DEC-20260904-dd58c3's scope statement and its empty `completion_criteria_met`.

What route (a) does establish, within its own scope: full S_4 monodromy at m=4 over the symmetric base,
and by derivation this holds for every nonsingular curve with p > 3. For the composer's information, not
as a verdict: the monodromy question behind KN-OPEN-009 is settled uniformly in the curve by the group
law, on both bases and at every m. That is a derivation-type determination, not a census agreement
within stated error.

**Reading declaration (J4).**

- goal.yaml; KN-OPEN-009; RQ-MONO-001.
- H-MONO-ebd400; EV-MONO-e9dc3b; DEC-20260904-dd58c3; CORR-20260904-33fbf3.
- experiments/EXP-MONO-0e6e8f/specification.yaml and execution_report.yaml.
- DEC-20260802-a51c82; DEC-20260810-2f86db (N-3); CORR-20260802-1d8384 (OI-1).
- Code: ptm.py (object 1 and J4_group_structure).

## validation_report and independent_recomputation

```yaml
validation_report:
  id: null        # not minted; this report is identified by its task and archived by TASK-20260930-a72623
  task_id: TASK-20260930-40470a
  run_ids: []     # zero runs; the objects reviewed are committed records
  artifact_checks:
    - DEC-20260810-2f86db present at HEAD d771721ac052; first committed 07cff851d (2026-08-10); unmodified since; ancestor of origin/main.
    - EV-MONO-a0a89c (d6be8fa54, 2026-08-02), and DEC-20260904-dd58c3 / EV-MONO-e9dc3b / H-MONO-ebd400 (dfa3c2d31, 2026-09-06), are ancestors of origin/main.
    - Every declared input is committed at HEAD and the tree was clean at start (sha256 table above).
    - No obstruction block exists on DEC-20260810-2f86db or EV-MONO-a0a89c (J3 G-2).
  metric_recomputations:
    - OBS-5 root-set statement at m=3 and m=4 — RECOMPUTED. It agrees in substance, with the wording corrections SC-1 and SC-2 (J1).
    - 193/193 (TASK-20260802-1b4130 O-9, m=4, p=211) — NOT recomputed as that artifact, which lies under blind_from and was not opened. Superseded in coverage: 182,104/182,104 unordered triples on the same curve, and 117,649/117,649 on C1.
    - 1196/1196 (RUN-MONO-4b50b6-002 V4, m=3) — NOT recomputed as that artifact. Covered by exhaustive m=3 on C1 (2,401) and C2 (10,404).
    - OBS-1 identity disc_T S_3 = 16 f(x1) f(x2) — RECOMPUTED symbolically; holds.
    - D-5 transport disc_{x2} S_3(x1,x2,T0) = 16 f(x1) f(T0) — RECOMPUTED symbolically; holds identically.
    - EXP-MONO-0e6e8f M1/M2/M3 numbers — NOT recomputed; the plan forbids it for J4. Quoted as recorded.
    - CORR-20260904-33fbf3 exact-null chi-squares (0.23, 0.73, 171.67) — NOT recomputed; quoted.
  control_checks:
    - Proves-too-much object 1 (generic tuples) — control PASSES for D-1. It stops at step (2); the delta-rule held on 967,678 generic fibres with 0 disagreements.
    - Proves-too-much object 2 (the D-4 count) — control PASSES for D-1. It stops at "rational" => "in the factor base". It FAILS for D-5 (J2 O-1).
    - Null object — generic tuples act as the null object for the factor-base-locus statistic. The statistic varies there (1^4 versus 2+2), so its constancy on the factor-base locus is a genuine locus effect, not an instrument artifact.
  heuristic_validation_checks: []   # not applicable: no heuristic-conditional claim is under review
  cost_model_checks: []             # not applicable: no complexity, speedup or cost claim (DEC-20260810-2f86db D-10); nothing to charge, no baseline ratio exists or is claimed
  proof_architecture_checks:
    - Baseline fixture. My S_3 equals Semaev's f_3 (retrieved Theorem 1). My S_4 equals the resultant recursion by two routes. The LC law reproduces Theorem 1 at m=3 and m=4.
    - Quantifier order. The corrected J1 statement quantifies as: for all m >= 3, for all nonsingular E/F_p with p > 3, for all affine P_i in E(F_p). It is uniform and needs no witness. The producer's "every prime" must read "every prime p > 3" (Theorem 1 requires char != 2, 3).
    - Observation collision. The Frobenius cycle type is constant across values of R whose factor-base counts differ (object 2). So it cannot identify relation supply, which supports the no-go. The symmetric-base m=4 census is constant across all curves (forced S_4), which bears on J4.
    - Method ceiling and nearby object. The group-law method reaches Frobenius statistics only. It cannot reach factor-base counts (object 2), which is why D-4 survives D-1.
    - Strictness witness and interface preservation — not applicable (no improvement or reduction claim).
  verdict: null
  verdict_note: >-
    No terminal whole-report verdict is issued. Under a review_plan the Validator reports on its own
    joints only (agents/validator.md, "Working under a review plan"), and the card says "Give no
    whole-goal verdict". That overrides the tier's generic passed|failed|incomplete|invalid output line
    for this task. Per-joint verdicts: J1 CONCUR (holds); J2 DISSENT (breaks: O-1); J3 DISSENT (breaks
    as recorded: G-1, G-2); J4 DISSENT (breaks). This report's own computational artifacts are complete
    and reproducible (a re-run was byte-identical except wall-clock fields) and in scope. That statement
    is about the artifacts, not the claim.
  limitations:
    - PD-B. One reviewer owns every joint. This buys coverage, not cross-reviewer independence.
    - One model family. Independence is by session and role, not by model (DEC-20260930-3a0b7b R-2; composition C-10).
    - Reviewer derivations new to the record. The ordered-base (Z/2)^{m-2} monodromy, the forced symmetric-base S_4, the group orders and primitivity at m = 4..7, and the delta-rule at every m are derivation-tier and toy-scoped. They should be re-derived by an independent reviewer before any promotion.
    - Records outside my read scope may already state some of those structural facts, for example H-MONO-93bc4d, H-MONO-45183a and EXP-MONO-815525. I did not check.
    - The EXP-MONO-0e6e8f numbers and the CORR-20260904-33fbf3 chi-squares were taken as recorded.
    - Object 2 used a large factor base (#V of about p/10 to p/6) and excluded 2-torsion x-values. N(R) varied widely but never reached 0 in these runs, so no zero-count R was exhibited.
    - Toy primes only (101-1999). No claim at cryptographic scale; no security estimate moves.
  artifact_paths:
    - coordination/goals/GOAL-MONO-001/review/TASK-20260930-40470a/review_report.md
    - coordination/goals/GOAL-MONO-001/review/TASK-20260930-40470a/s4_construction/computations.json
```

### independent_recomputation

**Recomputed myself.** All code and outputs are in `computations.json`.

- S_3 and S_4, including their structure: 540 terms; degree 4 in each variable; full symmetry;
  LC = S_3^2.
- The m=3 product formula (symbolic).
- The root-set statement at m=3 and m=4: exhaustive on C1 and C2, random on C2, C3, C4 and C5, and m=5
  at random.
- The degree law deg f = 2^{m-2} - n_O on every tuple.
- All J1(c) degeneracies.
- The OBS-1 identity and the D-5 transport identity.
- The ordered-base delta-rule at m=3 and m=4.
- The factor-base counts N(R) at m=3 and m=4.
- The sign-class permutation groups for m = 3..7.

**Re-verified with a disjoint checker.** Each lineage is disjoint because my own code shares no source
with PARI, FLINT or sympy.

- **Group law.** My affine Python code was checked against PARI `elladd` on the full 96 x 96 table of C1,
  and on every random and degenerate tuple.
- **Factorization.** FLINT `nmod_poly.factor` was checked against PARI `factormod` on every random and
  degenerate tuple.
- **S_4.** sympy `resultant` against PARI `polresultant`: exact equality.
- **S_5.** A formal Sylvester determinant (PARI `matdet`) against sympy `resultant` on 3 tuples.
- **N(R).** The polynomial-root route against the group-law route, for every R.
- **#E(F_p).** My own enumeration against PARI `ellcard` on all five curves.
- **Semaev's Theorem 1.** Retrieved and read, so the citation is no longer recalled.

**Taken on the producer's word (not recomputed).**

- Every number in the EXP-MONO-0e6e8f execution report (the plan forbids a census recomputation).
- The red team's post hoc exact-null chi-squares, as quoted in CORR-20260904-33fbf3.
- The 193/193 and 1196/1196 counts. Their artifacts lie under blind_from, and my own exhaustive checks
  supersede them in coverage.
- The scope content of KN-FIND-edd62c, KN-FIND-19f5ea and DEC-20260905-021e6e. I read these for the
  staleness audit only; I did not re-derive them.
- The model identities recorded by earlier sessions.
- The archive and receipt status of earlier batches. I checked git reachability of five records only.

**What would make each claim false, and whether it was checked.**

- J1: a factor-base-locus fibre with a non-rational root, or with a root outside the sign set. Checked
  exhaustively on two curves and at random on four. None was found.
- J2: a sentence licensing the condemnation of D-4. Checked, and found (O-1).
- J3: a reading of (c) that the record fails. Checked, and found (G-1, G-2).
- J4: a reading of (a) that the result fails, or a committed statement it contradicts. Checked, and
  found (the ordered base; the withdrawn M3; N-2; the dd58c3 scope statement).

## Reading declaration (every path and commit read)

**Snapshot.** I read at HEAD `d771721ac052bce33dc302e6aa2d1d804a1c5db0` on branch
`claude/coordinate-mono-20260930`, with a clean tree. The file digests are in the table at the top.

**Read in full.**

- ledger/handoffs/TASK-20260930-40470a.yaml
- coordination/review/mono-20260930-44adf9/review-plan.yaml
- ledger/decisions/DEC-20260930-3a0b7b.yaml
- ledger/handoffs/TASK-20260904-50755f.yaml
- ledger/decisions/DEC-20260810-2f86db.yaml
- ledger/decisions/DEC-20260802-a51c82.yaml
- ledger/decisions/DEC-20260904-67cde4.yaml
- ledger/evidence/EV-MONO-a0a89c.yaml
- ledger/goals/GOAL-MONO-001/goal.yaml
- ledger/goals/GOAL-MONO-001/checkpoints/BATCH-003.yaml
- ledger/corrections/CORR-20260802-1d8384.yaml
- ledger/questions/RQ-MONO-001.yaml
- knowledge/open-problems/KN-OPEN-009.md
- ledger/decisions/DEC-20260904-dd58c3.yaml
- ledger/evidence/EV-MONO-e9dc3b.yaml
- ledger/hypotheses/H-MONO-ebd400.yaml
- ledger/corrections/CORR-20260904-33fbf3.yaml
- experiments/EXP-MONO-0e6e8f/specification.yaml
- experiments/EXP-MONO-0e6e8f/execution_report.yaml
- ledger/decisions/DEC-20260905-021e6e.yaml
- knowledge/findings/KN-FIND-edd62c.md
- knowledge/findings/KN-FIND-19f5ea.md
- AGENTS.md
- docs/inventor-protocol.md
- agents/validator.md
- .claude/agents/validator-breakthrough.md
- docs/claims-and-verification.md

**Read in part.**

- templates/research-records.md: lines 290-379 (Evidence schema and obstruction block) and 560-725
  (handoff, review plan, review attestation).
- coordination/goals/GOAL-MONO-001/batches/BATCH-44adf9/dispatch_queue.json: the top-level fields, the
  `notes`, the task-id list and the full card of TASK-20260930-40470a. The other three cards' contents
  were not printed.

**Directory listings (names only).**

- coordination/review/mono-20260930-44adf9/
- coordination/goals/GOAL-MONO-001/batches/BATCH-44adf9/ (including the name of its `claims/` subdirectory)
- my own write directory, which did not exist at start

**Git metadata only (log / merge-base).**

- The repository head: `git log -5`, `git status`.
- The history of these paths: DEC-20260810-2f86db, AGENTS.md, templates/research-records.md,
  DEC-20260904-dd58c3, EV-MONO-e9dc3b, H-MONO-ebd400, EV-MONO-a0a89c.
- `git rev-parse HEAD:<path>` for the digest table.

**Retrieved public source.** Semaev, IACR ePrint 2004/031 (details above).

**Network.** PyPI, through the agent proxy, for the scratch venv packages.

**Not read.**

- Any path under `experiments/EXP-MONO-4b50b6/` or `coordination/goals/GOAL-MONO-001/batches/BATCH-003/`
  (blind_from).
- Any other reviewer's report, including the m=4 reviewer task reports.
- DEC-20260810-2f86db's producing-session transcript.
- The handoffs TASK-20260930-a72623, -e74f4c and -f4f675.
- orchestration/model-bindings.yaml and tools/check_review_independence.py.
- H-MONO-93bc4d, H-MONO-45183a and EXP-MONO-815525.
- The files another session had left in the shared scratchpad. I saw their names in a directory listing
  and never opened them: e2/, ecc.txt, ecc_open.txt, fid.py, health.txt, indep.txt, mono.json, mono.md,
  now.txt, plan.json, plan.md, recent.txt, rt/, val2.txt, val_new.txt.
- No repository-wide search was run.

## review_attestation

```yaml
review_attestation:
  task_id: TASK-20260930-40470a
  card: TASK-20260930-40470a
  plan_id: REVIEW-MONO-20260930-40470a
  goal_id: GOAL-MONO-001
  batch_id: BATCH-44adf9
  claim_epoch: 1
  claim_owner: coordinator-portfolio-3811
  archived_by: TASK-20260930-a72623
  reviewer_role: validator
  role: validator-breakthrough          # binding (.claude/agents/validator-breakthrough.md, variant_of validator)
  joints_owned: [J1, J2, J3, J4, proves_too_much, blind_rederivation]
  verdict:                              # per joint only; CONCUR = holds, DISSENT = breaks
    J1: CONCUR                          # no-go derivationally sound; required scope corrections SC-1 (distinctness), SC-2 (degree drop on S_{m-1}=0)
    J2: DISSENT                         # O-1: D-5/N-2 (and the goal head's gating sentence) license condemning the D-4 swapped statistic at m=3
    J3: DISSENT                         # as recorded: G-1 (inherits O-1), G-2 (no obstruction block, AGENTS.md closure standard since 2026-08-14); curable in the composed decision
    J4: DISSENT                         # ordered-base reading (V_4 at m=4 for every curve), withdrawn M3 ("within stated error"), DEC-20260802-a51c82 N-2, DEC-20260904-dd58c3 scope
    proves_too_much: >-
      D-1 stops at the locus boundary on both objects: step (2) for generic tuples (delta-rule,
      967,678 generic fibres, 0 disagreements); "rational => in the factor base" for the D-4 count
      (N(R) varies; two routes agree). D-5, a separate provision, makes the transfer D-1 does not.
    blind_rederivation: >-
      Agrees with OBS-5 in substance at m=3 and m=4 (and m=5 at random). The correct wording is J1's
      corrected statement.
  whole_claim_verdict: none issued     # the plan asks for none; card constraint "Give no whole-goal verdict"
  independent_session: true
  requested_policy: review-breakthrough
  reasoning_effort_requested: max
  reasoning_effort_as_served: max       # evidence: binding frontmatter `effort: max`; CLAUDE_EFFORT=max in this session's tool-process environment; not otherwise observable from inside the session
  resolved_runtime: claude_code 2.1.42 (Claude Agent SDK subagent; CLAUDE_CODE_CHILD_SESSION=1; remote environment cloud_default)
  resolved_model_id: claude-opus-5-5    # as the runtime reports it to this session ("Opus 5.5"); not probe-verified
  model_verified: false                 # no `python3 -m orchestration.adapter doctor --probe` was run by this session
  fallback_used: true
  fallback_reason: >-
    Runtime inheritance under the Claude Code validator-breakthrough subagent binding
    (DEC-20260930-3a0b7b R-1, condition (d)). The served model identifier, claude-opus-5-5, is not the
    model DEC-20260930-3a0b7b R-1 records for review-breakthrough (claude-opus-5). This is a
    backend/model substitution only: the effort is not below max and nothing is degraded. The card has
    fallback_allowed: true.
  degraded_requirements: []
  amazon_bedrock: >-
    Not selected, configured, probed or contacted by this session. CLAUDE_CODE_USE_BEDROCK is unset,
    the ANTHROPIC_BASE_URL host is api.anthropic.com, and the resolved model identifier contains no
    "bedrock".
  network_used: [PyPI through the agent proxy (python-flint, cypari2, sympy into a scratch venv), eprint.iacr.org (Semaev 2004 PDF)]
  model_independence: >-
    None. Independence is by session and role, not by model (DEC-20260930-3a0b7b R-2; composition
    C-10). The records reviewed name claude-opus-5 for the BATCH-003 producer and reviews, and
    claude-sonnet-5 for DEC-20260904-dd58c3, DEC-20260905-021e6e and EXP-MONO-0e6e8f's design.
  read_sibling_reports: false
  sibling_or_composer_materials_read: >-
    None. No other reviewer report on this claim exists or was opened. The composer card
    TASK-20260930-e74f4c was not opened. Only the plan extraction's `composition` section, which the
    card's read_scope lists, was read.
  producer_transcripts_read: none
  blind_from: [experiments/EXP-MONO-4b50b6/, coordination/goals/GOAL-MONO-001/batches/BATCH-003/]
  blind_from_respected: true
  record_ids_reviewed:
    - DEC-20260810-2f86db
    - EV-MONO-a0a89c
    - DEC-20260802-a51c82
    - DEC-20260904-67cde4
    - DEC-20260930-3a0b7b
    - TASK-20260904-50755f
    - TASK-20260930-40470a
    - GOAL-MONO-001            # goal.yaml and checkpoints/BATCH-003.yaml
    - CORR-20260802-1d8384
    - RQ-MONO-001
    - KN-OPEN-009
    - DEC-20260904-dd58c3
    - EV-MONO-e9dc3b
    - H-MONO-ebd400
    - CORR-20260904-33fbf3
    - EXP-MONO-0e6e8f          # specification.yaml and execution_report.yaml
    - DEC-20260905-021e6e
    - KN-FIND-edd62c
    - KN-FIND-19f5ea
  sources_read: see "Reading declaration" above (complete; digests in the table at the top)
  retrieved_sources:
    - {citation: "Semaev, Summation polynomials and the discrete logarithm problem on elliptic curves, IACR ePrint 2004/031", provenance: retrieved, verified_by: TASK-20260930-40470a, sha256: 1cab0ae675996cdba6393b1e369a22113fd2e74bcf1223595743dc140631c7d6}
  zero_runs: true                       # no RUN-* directory; nothing under experiments/ written
  written_paths:                        # the only files this session wrote in the repository
    - coordination/goals/GOAL-MONO-001/review/TASK-20260930-40470a/review_report.md
    - coordination/goals/GOAL-MONO-001/review/TASK-20260930-40470a/s4_construction/computations.json
  scope_findings: none                  # no other file was written under the write scope
  commits_made: none                    # the Coordinator archives
  sessions_that_wrote_the_report: >-
    One: this validator-breakthrough subagent session, launched by the top-level session holding claim
    epoch 1 (owner coordinator-portfolio-3811). No other session wrote any part of this report or of
    computations.json.
  attested_at: '2026-09-30'
```
