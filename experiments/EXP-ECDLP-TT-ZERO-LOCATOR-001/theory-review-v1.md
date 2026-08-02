# Direct five-source TT theory review v1

## Handoff: byte-bound preflight audit

### Claim or task

Audit frozen `preflight-v1.md` at SHA256
`5db581dae9305fe43190f766ac3a450bd17830adeaab0c1118859988cb52c720`,
emphasizing projective equality, final cut ranks, and lower-bound scope.

### Status

`REVISE`.

The projective-equality theorem, exact indicator, final cut-rank theorem, and
entry-oracle lower bound are correct. Two TT-accounting passages overstate what
follows from upper bounds or dense-core parameter counts.

### Assumptions

- The complete addition formula always returns a nonzero `F_p`-projective
  representative.
- TT bond ranks mean exact unfolding ranks over `K`.
- Dense TT-core allocation is distinguished from minimal structured or sparse
  storage.
- No implementation or experiment is authorized.

### Evidence so far

- For finite `Q`, `e_X=e_Y=0` forces `S=Q`; `Z=0` would otherwise produce the
  forbidden all-zero representative.
- For `Q=O=(0:1:0)`, `g_O=-omega*Z`. On
  `Y^2*Z=X^3+a*X*Z^2+b*Z^3`, `Z=0` forces `X=0`, leaving the unique projective
  point `(0:1:0)`. The identity case is exact.
- The final cut decomposition into disjoint all-ones blocks is correct. Each
  active partial sum contributes one rank-one block, and disjoint row and
  column supports imply `rho_k(Zcal_Q)=m_(k,Q)` over every field, regardless
  of ordered multiplicities.
- The generic sparse-spike query lower bound is valid and explicitly confined
  to the entry-oracle model.

### Failure modes

- From an upper bound `O(B*r^4)`, v1 cannot conclude that raw state is
  subquadratic only when `r=o(B^(1/4))`. With ranks merely bounded above by
  `r`, that condition is sufficient, not necessary. The standard dense
  Kronecker construction allocates exactly

  ```text
  sum_k B*(r^U_(k-1)*r^V_(k-1))*(r^U_k*r^V_k),
  ```

  which becomes `Theta(B*r^4)` only when the relevant actual ranks are all
  `Theta(r)`.
- Likewise, an `O(B*r^6)` exact reduction schedule is guaranteed
  subquadratic when `r=o(B^(1/6))`, but this is not a necessary condition
  without a matching lower bound.
- The displayed `S_TT` is the allocation for dense TT cores with those bond
  dimensions, not exact information-theoretic storage. For that dense
  representation, the complete storage gate requires

  ```text
  rho_1,
  rho_1*rho_2,
  rho_2*rho_3,
  rho_3*rho_4,
  rho_4 = o(B),
  ```

  rather than only the middle product. Structured or sparse cores remain
  outside this accounting negative.

### Next concrete action

Create a versioned preflight replacing the two necessary/exact-storage
passages with construction-conditional dense-TT statements and sufficient
gates, while preserving the equality, cut-rank, and entry-oracle theorems.

### Artifact paths

- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v1.md`
