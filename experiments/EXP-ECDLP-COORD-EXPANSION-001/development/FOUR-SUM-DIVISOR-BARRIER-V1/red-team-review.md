# Independent Red-Team Review

## Handoff: Four-Sum Divisor Barrier V1

### Claim or task

Audit whether the run establishes a reduced four-sum divisor barrier above the
rho frontier, including divisor semantics, point/x support, reconstruction,
controls, verification, and representation boundaries.

### Status

- divisor-degree lemma: `RESTRICTED THEOREM`;
- measured supports: `OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`;
- `Theta(B^4)` family claim: `OPEN`;
- preregistered all-row `B^2.5` barrier: false;
- overall: `REVISE INTERPRETATION`.

### Assumptions

- Three fixed toy prime-order curves, one seed, and `B in {5,8,10}`.
- Sign-canonical point factor bases, not full x-fibre factor bases.
- Reduced support discards multiplicities.
- The lower bound applies only when the reduced coordinate algebra or a fixed
  dense Riemann-Roch representation is explicitly materialized.
- A comparison to rho additionally requires a charged conversion from stored
  field elements to group-operation work; this artifact does not supply it.

### Evidence so far

- Source and artifact hashes match commit
  `5b2bb561607536355aac4451c0613c6ecf8b5fe9`.
- A separate affine implementation importing neither producer nor verifier
  reproduced all 15 reduced point supports, x-supports, and D2+D2
  reduced-support equalities.
- All tested point and x supports exceed `sqrt(q)`.
- Eleven of 12 coordinate point supports exceed `B^2.5`; the
  `q=953, source_prf_x` row has `55 < 55.90`.
- The scalar control is a sound reduced-support compression control. Its
  signed scalar support lies in `+-{1,...,B}`, giving
  `|4R| <= 8B+1`; observed point supports are 29, 55, and 75.
- For a reduced split divisor of `m` rational points,
  `dim_Fq(O_D)=m`, and a nonzero rational function regular and zero at those
  points has total pole degree at least `m`.

### Failure modes

1. D2+D2 establishes only equality of reduced supports. At
   `q=953, random_x`, direct canonical D4 has total multiplicity 70 while
   unique-D2 pairing has total 120; multiplicities differ at 45 of 70 points.
2. Reported multiplicity counts canonical multisets, not ordered four-draw
   convolution. These have different entropy, norm degree, and collision
   semantics even though reduced support agrees.
3. Three coupled `(q,B,curve,seed)` rows cannot establish
   `Theta(B^4)`. The appropriate random-like support model is
   regime-dependent, approximately
   `min(binomial(B+3,4),q)`.
4. The preregistered all-row gate failed. The finite observation
   `support > sqrt(q)` is not a substitute pass.
5. `dim(O_D)=m` is exact, but representation costs differ: a generic dense
   multiplication matrix uses `Theta(m^2)` entries, an evaluation-basis
   diagonal operator or dense vector uses `Theta(m)`, and structured or lazy
   operators may use less.
6. A pole-degree lower bound of `m` is not a universal coefficient count of
   `m+1`. On genus one, `dim L(E)=deg(E)` for positive degree. An x-only
   polynomial uses `s+1` coefficients for `s` x-values but has pole degree
   `2s`.
7. Point and x-image algebras need separate conclusions. Pulling back an
   x-image generally adds the negative points and changes divisor degree.
8. The verifier imports and reruns the producer. It is deterministic,
   hash-bound replay, not independent semantic verification.
9. Memory, traffic, build/query work, amortization, and conversion to rho or
   BSGS costs are absent.
10. The positive-control gate enforces only "smaller than every candidate,"
    not its predicted `O(B)` bound.
11. Nonreduced thickening cannot reduce scheme length below the length of its
    reduction. A succinct presentation may evade dense materialization;
    nonreducedness alone does not.
12. Equality-pair leaves still require independent factor certification
    before a resultant run can treat them as proven inputs.

### Strongest valid correction

> On three coupled toy instances, the four sign-canonical point sets have
> reduced D4 support close to the canonical multiset ceiling. All tested point
> and x supports exceed `sqrt(q)`; 11 of 12 point supports exceed `B^2.5`.
> No asymptotic family law or charged rho-cost lower bound is established.

The representation-specific quantities are:

- reduced point-algebra dimension: `m`;
- x-image algebra dimension: `s`;
- pole-degree lower bound for a function vanishing on all reduced points:
  `m`;
- generic dense operator entries: `m^2`;
- universal dense coefficient count: not established.

### Next concrete action

Run `ITERATED-DIVISOR-RESULTANT-V1-SCHEME-AWARE` after independent
equality-leaf certification. It must compare:

1. reduced D4 support;
2. canonical-multiset pushforward divisor;
3. ordered four-fold convolution divisor;
4. unique-D2-pair pushforward divisor;
5. point-based and x-eliminated resultant DAGs.

Charge multiplicity handling, squarefree reduction, DAG state, coefficient
growth, target work, memory traffic, and witness recovery. Add fixed-q B
sweeps, multiple seeds, matched random point/x controls, and separate rho and
BSGS baselines.

### Artifact paths

- `development/FOUR-SUM-DIVISOR-BARRIER-V1/contract.md`
- `development/FOUR-SUM-DIVISOR-BARRIER-V1/raw-result.json`
- `development/FOUR-SUM-DIVISOR-BARRIER-V1/verification.json`
- `src/four_sum_divisor_barrier.py`
- `src/verify_four_sum_divisor_barrier.py`
