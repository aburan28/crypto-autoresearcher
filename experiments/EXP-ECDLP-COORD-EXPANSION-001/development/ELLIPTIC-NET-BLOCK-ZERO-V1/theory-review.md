# Independent Theory Review

## Handoff: Elliptic-net block-zero theory audit

### Claim or task

Determine what the observed Berlekamp-Massey and Somos-4 failures imply, and
identify the strongest nonlinear formulation still open.

### Status

`NEGATIVE RESULT`

The negative is restricted to constant-coefficient linear recurrences and
raw two-parameter Somos-4. The rank-two elliptic-net/function-field norm
route remains `OPEN`.

### Assumptions

- toy prime-order subgroups `q=953,3919,15583`;
- `B=5,8,10` and sequence length `L=8B`;
- the four recorded factor-base families, two `A` variants, and two targets;
- raw block products
  `G_C(i)=product_{t in C} h_Q(P0+iD+S_t)`;
- homogeneous constant-coefficient linear recurrences over `F_p`;
- raw Somos-4 with fixed coefficients, applied without gauge or denominator
  normalization.

### Evidence so far

- The deterministic verifier replayed all 12 rows exactly.
- An independent linear-system implementation checked all 48 root
  sequences: 16 each of lengths 40, 64, and 80 have minimal observed linear
  complexity 20, 32, and 40.
- Across 35,856 materialized node sequences and 17,792 sibling pairs, there
  are zero held-out-exact linear recurrences, zero exact raw Somos-4 fits,
  zero identical sibling annihilators, and zero sibling cross-annihilators.
- Every root trained on the first two-thirds fails held-out prediction.
- Explicit state is 5,720, 42,496, and 114,720 field elements, following
  `Theta(L B^4)=Theta(B^5)` construction.

For each tested root prefix, Berlekamp-Massey minimality proves that no
constant-coefficient recurrence below order `L/2=4B` annihilates the complete
observed prefix. This is a finite-prefix restricted theorem. `L/2` is a
random-like profile, not the maximum possible complexity, and it does not
prove asymptotic `Theta(B)` behavior.

For every tested node, exact elimination proves that no fixed raw Somos-4
coefficient pair satisfies all available equations. The source's
`violations` field is an inconsistency sentinel, not a best-fit residual.

The elliptic-divisibility positive control also has BM order `L/2` while
satisfying Ward and Somos-4 exactly. High linear complexity therefore does
not exclude low-state nonlinear recurrence.

### Failure modes

The experiment does not rule out:

- gauge-normalized or denominator-cleared sequences;
- higher-order Ward recurrences;
- rank-two elliptic nets coupling neighboring lattice slices;
- vector or matrix nonlinear state;
- index-dependent coefficients;
- function-field norms, resultants, or compact divisor representations;
- succinct high-degree arithmetic circuits;
- many-target amortization.

The code compares targets within each `A` variant, but does not implement the
contract's cross-variant sharing comparison. This omission does not affect
the failed gate because no candidate recurrence passes earlier conditions.

The claims are empirical for the toy schedule and algebraically exact only
for the two recurrence classes. No generic-group or structured-generic
theorem follows.

### Next concrete action

Implement `RANK2-NET-NORM-CIRCUIT-V1`.

For each tuple `t`, set `T_t=P0+S_t-Q` and verify that a denominator-free
rank-two net polynomial `Psi_(n,1)(D,T_t)` has the intended zero condition.
For a block, construct the norm over the coordinate algebra of the four-sum
divisor both enumeratively and through an iterated quotient-algebra or
resultant circuit.

Measure divisor degree, circuit DAG size, multiplication-operator dimension
and displacement rank, target specialization, and exact zero descent. Use an
additive-convolution divisor as a positive control and a matched random
divisor as a negative control. Falsify compression if reusable state remains
`Omega(B^4)`.

### Artifact paths

- `development/ELLIPTIC-NET-BLOCK-ZERO-V1/contract.md`
- `development/ELLIPTIC-NET-BLOCK-ZERO-V1/raw-result.json`
- `development/ELLIPTIC-NET-BLOCK-ZERO-V1/verification.json`
- `src/elliptic_net_block_zero.py`
