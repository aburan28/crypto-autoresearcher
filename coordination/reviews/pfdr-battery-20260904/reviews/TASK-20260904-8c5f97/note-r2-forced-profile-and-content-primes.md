# R2 — derivation note: the entire (2, 2, 3) profile is forced, its content
# primes, and what the p-sweep could therefore have shown

Label: **derivation**. Red team, TASK-20260904-8c5f97, EXP-PFDR-fd901a.

## 1. The forced profile, derived over Z

Write A = F_p[a_0..a_5]/(a_i^2) for the top-form algebra and
B = F_p[a]/(a_i^2 - a_i) for the function ring. Two facts, each derived in
`note-r1-...` §1 and §5:

* **top half.** The degree-4 part of S~ is the parameter-free integer form
  T = 16 Q_1 Q_2 with Q_k = a_{k0}a_{k1} + 2a_{k0}a_{k2} + 4a_{k1}a_{k2}, i.e.
  the tensor product of the two per-block quadrics. Multiplication by Q_k on the
  3-variable block algebra has ranks r_k(0) = 1 (deg 0 -> 2) and r_k(1) = 1
  (deg 1 -> 3, since a_i Q_k = c_i a_0a_1a_2 with (c_0,c_1,c_2) = (4,2,1)), and
  ker(M_1 ⊗ M_2) = sum of block kernels, so

    top_rank(D) = sum_{j+k = D-4} r_1(j) r_2(k) = **1, 2, 1** at D = 4, 5, 6.

  Confirmed numerically at p = 3, 4099, 2^64 - 59 and P-256
  (`out/r1_derivation.json`, `tensor_top_rank_profile`).
* **full half.** full_rank(D) = rank of the degree-(D-4) monomial evaluation
  matrix on supp(S~), so full_rank = 1, 6, 15 (full row rank) unless S~ acquires
  >= 64, 32, 16 zeros respectively on the 64-point cube.

Hence, for **every** p with 2 != 0 and every (A, B, x_R) whose S~ has fewer than
16 zeros on the cube:

    (full_rank, top_rank) at D = 3..6 = [(0,0), (1,1), (6,2), (15,1)],
    fall_dim = [0, 0, 4, 14],  syzygy_dim = 0,  d_ff = 5,
    deficit_series against (1+z)^6(1-z^4) = [0, 0, 0, -14].

This is the entire recorded Semaev-arm invariant vector. **Content primes: {2}
and only {2}** — the invariant factors of the integer top blocks at D = 4, 5, 6
are (16), (16, 16), (16) (`out/proves_too_much.json`), so the top half is
characteristic-independent away from 2, and the full half is value-level, not
content-level.

## 2. The threshold p_0 is 3, not "somewhere below 4099"

The number of zeros of S~ on the cube is ~ 64/p for a uniform target, so the
drop threshold (>= 16 zeros) is crossed only for p <= 4. Measured
(`out/proves_too_much.json`, 24 uniform samples per prime, own code AND the
producer's meter, identical results):

| p | mean zeros on the cube | samples at the reference profile |
|---|---|---|
| 2 | 33.3 | 0 / 24 (four distinct profiles; top form ≡ 0 mod 2) |
| 3 | 26.0 | 23 / 24 (one draw with full_rank@6 = 13) |
| 5 | 12.8 | 24 / 24 |
| 7 | 8.4 | 24 / 24 |
| 11 | 5.7 | 24 / 24 |
| 4099 | 0.0 | 24 / 24 |

And the control the contract did **not** run — ONE integer instance reduced
modulo a prime ladder, which is literally what "specialization of one integer
matrix family" means (`out/r2_forced_profile.json`,
`one_integer_instance_across_primes`; the fixture triple (941, 428, 3690) taken
as integers): the profile equals the reference at **every prime from 3 to
2^256** in the ladder {3, 5, 7, ..., 199, 4099, 2^64-59, P-256}; the only
deviating prime is 2. Cost: under one second.

**Consequence.** The 12-bit / 64-bit / 256-bit ladder cannot separate any two
hypotheses about p once p >= 5. Criteria (3) and (5) could fail only by an
instrument fault, exactly as the Coordinator's prior anticipated; the 120
Semaev draws, 600 null draws and 120 non-curve draws re-measure one integer
vector whose value is fixed by T and by |Z(S~)| < 16.

## 3. The "pairing" is a seed pairing, not an instance pairing

`analysis.md` reports flatness "paired by curve seed, target seed, null seed".
But (A, B) are drawn *in F_p* from that seed, so curve seed 1101 is
(941, 428) at p = 4099, (3403988020299468145, 8510742384309064825) at
2^64 - 59, and a 76-digit pair at P-256 (`out/r2_forced_profile.json`,
`bookkeeping`). **No instance exists at two primes**, so "40 of 40 pairs
identical" carries exactly the same information as "all 80 draws hit the modal
profile" — the pairing adds nothing and cannot test the specialization claim,
which is a statement about *one* integer point read modulo different primes.
The null arm is further from a pairing still: its mixed seed contains p, so the
64-bit and 256-bit null polynomials are independent draws.

## 4. The "small-p artifact budget" is a bound restated, and it bounds an
##    event set that is empty at the prime it names

* Derived (Stage 0, single-minor): 30/4099 = 0.0073 at D = 6.
* Reported as measured: 0 of 40, exact 95% CI [0, 0.0881].
* Derived here (§5 of the R1 note): density <= 14/p = 0.0034, and the **actual**
  maximum over an exhaustive x_R search of 19 992 curves at p = 4099 is 6 zeros
  against a threshold of 16, i.e. **no rank-drop point exists on the searched
  axis at all**.

So the reported interval is an upper bound, at coarseness 0.088, on a quantity
that is 0 by derivation and 0 by exhaustive search. It is not a measurement of
the rank-drop rate; a measurement would need draws of order p (or a ladder at
p = 5..101 where the rate is nonzero). The two siblings that consumed it
(`EXP-PFDR-20ee58` execution-report `contract_1_reported`, analysis.md line
"within the fd901a budget"; `EXP-PFDR-cbdefb` execution-report input 1) used the
**number and its interval**, not the derived bound, and used it as a
pass-threshold — a threshold no plausible artifact rate could exceed, so it
discriminated nothing. Replacement available at zero cost: the per-draw
structural criterion "|Z(S~)| >= 16", 64 field evaluations per draw.

## 5. The one invariant in the table that is NOT forced

The support-matched null's top_rank at D = 5 is the rank of a 6 x 6 matrix
whose entries are the 9 random top coefficients — a genuine nonconstant
determinant, and the one place where Schwartz-Zippel is load-bearing. Measured
drop rate below 6 (2000 draws per prime, my own code,
`out/r2_forced_profile.json`):

| p | 5 | 7 | 11 | 13 | 101 | 4099 |
|---|---|---|---|---|---|---|
| rate | 0.2800 | 0.1835 | 0.1035 | 0.0935 | 0.0130 | 0.0005 |

That is the c/p law HEUR-001 asserts (c ≈ 2), and it is measurable — at
p = 5..101. The contract instead sampled 200 null draws at p = 4099, where the
expected event count is 0.1, and 0 of 200 followed. **This is what the reported
quantity should have done as p grows, and where it should have been measured.**

**Conclusion for R2.** The joint's breaking artifact was produced. The sweep's
information content is that of the Stage-0 derivation plus one instrument check;
its evidence strength is the derivation's, not 120 draws', and no reading that
calls the 256-bit cells a cryptographic-scale validation is supportable: they
are exact ranks of a 64-column matrix whose value was forced before the run.
None of this contradicts a single recorded integer.
