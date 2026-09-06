# LOCKED BLIND DERIVATION -- written 2026-09-04T19:05Z
# Sources read so far, and ONLY these:
#   ledger/handoffs/TASK-20260904-b4b00c.yaml   (task card)
#   agents/validator.md, AGENTS.md (head)       (role contract)
#   experiments/EXP-MONO-64aaa4/implementation/run_experiment.py
#   experiments/EXP-MONO-cb905d/implementation/run_experiment_v2_part_a_corrected.py
# NOT read: any red-team report, any review, any ledger/knowledge record,
#           any raw-result.json, any specification/amendment.

## Notation
E/F_p : y^2 = x^3+Ax+B.  N = #E(F_p).
T  = E(F_p)[2]  (points P with 2P=O, INCLUDING O).   tau = |T| in {1,2,4}.
nu4 = #E(F_p)[4] (points with 4P=O, including O).    n4 = nu4 - tau = #{exact order 4}.
S  = affine points with y != 0  ("generic"), |S| = G = N - tau = 2*n1,
     n1 = |factor base| = #{x : f(x) nonzero square}.
key(P) = x(P) for affine P, "O" for the point at infinity.

## Step 1. The 4 sign-class sums
eps in {(+,+,+),(+,+,-),(+,-,+),(+,-,-)}, eps_1 fixed +1:
  S1=P1+P2+P3, S2=P1+P2-P3, S3=P1-P2+P3, S4=P1-P2-P3.

## Step 2. x-collision <=> S_i = +- S_j  (also correct for the "INF" sentinel:
   both infinite <=> S_i=S_j=O; one infinite one affine never matches).

## Step 3. The six pair conditions.  Differences/sums:
  (1,2): S1-S2=2P3          S1+S2=2(P1+P2)
  (1,3): S1-S3=2P2          S1+S3=2(P1+P3)
  (1,4): S1-S4=2(P2+P3)     S1+S4=2P1
  (2,3): S2-S3=2(P2-P3)     S2+S3=2P1
  (2,4): S2-S4=2P2          S2+S4=2(P1-P3)
  (3,4): S3-S4=2P3          S3+S4=2(P1-P2)
so, writing {a,b} = {1,2,3}\{k}, the six conditions are exactly

  COLLISION(k,eps)  <=>  P_k in T   OR   P_a + eps*P_b in T,    k=1,2,3, eps=+-1.

Hence  f(P1,P2,P3) = #colliding pairs
     = sum_{k=1..3} [ 2*1{P_k in T} + 1{P_k notin T} * #{eps : P_a+eps P_b in T} ].

COROLLARIES (structural, testable):
 (C1) f is invariant under P_k -> -P_k for each k  => the transversal arm's
      'fixed' and 'random' sign arms MUST give BIT-IDENTICAL counts, because
      measure_curve draws the same 3 fb indices (same label/counter prefix)
      in both arms and only then draws sign bits.
 (C2) f is a symmetric function of (P1,P2,P3) despite eps_1 being fixed.
 (C3) exactly one P_k in T (others generic) => f = 2 deterministically.
 (C4) two or three P_k in T => f = 6 deterministically.
 (C5) transversal arm (all P_k generic, y!=0) with tau=1 => f = 0 always.

## Step 4. Pair count D00
D00 := #{(P,Q) in S^2 : key(P)!=key(Q), P+Q in T}.
For each Q in S, W in T, put P=W-Q. Then P in S always. P=-Q <=> W=O;
P=Q <=> W=2Q (possible only if Q has exact order 4). The two exclusions are
disjoint. So
        D00 = G*(tau-1) - n4 = G*(tau-1) - (nu4 - tau).
Also D(1,1)=tau*(tau-1) (both in T), and D(1,0)=D(0,1)=0.

## Step 5. TRANSVERSAL ARM
3 distinct factor-base x's without replacement + any lift
  == uniform over ordered triples in S with pairwise distinct keys.
All P_k generic, so f = sum over the 6 (k,eps) of 1{P_a+eps P_b in T},
i.e. each unordered pair contributes both its sum and its difference:

  E_trans = 6 * D00 / ( G*(G-2) )
          = 6 * [ (N-tau)(tau-1) - (nu4-tau) ] / [ (N-tau)(N-tau-2) ].

(if nu4 = tau this is 6(tau-1)/(N-tau-2); the program's naive 6(tau-1)/N is
the large-N approximation.)

## Step 6. GROUP-UNIFORM ARM
Sampler: each accepted draw is uniform on all N points (per-iteration
acceptance 1/(2p+1) for O, for each 2-torsion point, and for each generic
point -- verified from the v2 code). Rejection is on KEY, so
  P1 ~ U(N); P2 ~ U(N - c1); P3 ~ U(N - c1 - c2),  c_k = |key class of P_k|
  = 1 if P_k in T, else 2.
Weight of an ordered triple: w = 1/( N (N-c1) (N-c1-c2) ). NOT exchangeable.

Let j = #{k : P_k in T}. Using (C3),(C4) and Step 5:
  E[f | j=0] = E_trans  (the j=0 conditional law IS the transversal law)
  E[f | j=1] = 2 ;  E[f | j=2] = 6 ;  E[f | j=3] = 6.
So

  E_gu = pi0 * E_trans + 2*pi1 + 6*pi2 + 6*pi3

with (C_j = # ordered distinct-key triples for one fixed pattern of weight j):
  C_0 = G(G-2)(G-4)          C_1 = tau*G(G-2)
  C_2 = tau(tau-1)*G         C_3 = tau(tau-1)(tau-2)
and W_j = sum over the C(3,j) patterns t of 1/(N (N-2+t1) (N-4+t1+t2)):
  W_0 = 1/(N(N-2)(N-4))
  W_1 = 1/(N(N-1)(N-3)) + 1/(N(N-2)(N-3)) + 1/(N(N-2)(N-4))
  W_2 = 1/(N(N-1)(N-2)) + 1/(N(N-1)(N-3)) + 1/(N(N-2)(N-3))
  W_3 = 1/(N(N-1)(N-2))
  pi_j = C_j * W_j    (sum_j pi_j = 1).

## CLAIM (locked): both E_trans and E_gu are EXACT rationals depending on the
## curve ONLY through (N, tau, nu4). No dependence on j-invariant, CM
## discriminant, or endomorphism ring beyond what those force on (N,tau,nu4).

## ============ VALIDATION COMPLETE, RESULTS LOCKED ============
## (timestamp below; NOTHING from any review/report has been read up to here)
## 1511 curves exhaustively brute-forced (12<=N<=26, 17 primes, 22 group
##     structures, 113 (p,j) pairs, all six (tau,nu4) profiles): 0 mismatches,
##     exact rational equality on BOTH arms.
## 2. 41 further curves (12<=N<=40) incl. matched (N,tau,nu4) cells whose
##     members differ in group structure ((2,18) vs (6,6); (1,25) vs (5,5);
##     (3,9) vs (1,27)) and in j (j=0, j=1728, ordinary): identical exact values.
## 3. Monte Carlo of the LITERAL sampler loop (2e6 tuples x 3 curves) matches
##     my sequential/non-exchangeable E_gu and REJECTS the exchangeable model.
## CHECK 1  p=617: ord(340,362) j=227 struct (2,290) N=580 tau=4 nu4=4
##                 cm1728(69,0)  j=494 struct (2,290) N=580 tau=4 nu4=4
##          N=580,tau=4 => UNIQUE structure Z/2 x Z/290 => nu4=4 forced.
##          E_trans = 9/287 = 0.031358885017421603 (both curves, exactly)
##          E_gu = 337753291/4666582705 = 0.0723770074058936 (both, exactly)
##          TRUE effect exactly 0 ; true P3 exactly 1.
## CHECK 2  p=3541: ord(577,1628) struct (6,600) nu4=8 ; cm j0 (0,2728)
##                  struct (60,60) nu4=16 ; both N=3600 tau=4.
##          MY P3_true = 4111818990624225/4113565673952074
##                     = 0.999575384601512661  (effect -0.0424615%)
##          Task card / Red Team claimed value: 0.99957533  -> DIFFERS at the
##          8th decimal (5.46e-8). Two model variants reproduce 0.99957533:
##            (a) group-uniform treated as UNIFORM over ordered distinct-key
##                triples (exchangeable) -> 0.999575334004326
##            (b) transversal denominator G(G-1) instead of G(G-2)
##                                       -> 0.999575334088307
##          MC of the literal loop rules (a) out; brute force rules (b) out.
## CHECK 3  calibration on RUN-MONO-cb905d-1 Part B (200 curve-measurements):
##          z vs MY exact formula: n=168 mean=-0.0335 sd=0.9255 (min -1.72 max +2.44)
##          z vs naive 6(tau-1)/N: n=168 mean=+0.1173 sd=0.9600
##          tau=1 exact-zero control: 32/32 observed exactly 0 collisions.
## COROLLARY C1 verified against RUN-MONO-64aaa4-1: fixed/random arms are
##          BIT-IDENTICAL (613/613, 681/681) as my derivation forces.
