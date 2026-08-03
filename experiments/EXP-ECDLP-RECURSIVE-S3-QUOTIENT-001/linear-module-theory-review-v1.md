# Linear-module theory review v1

## Handoff: prime-cycle convolution and x-orbit rank

### Claim or task

Audit whether a nonempty proper subset of a prime cyclic group induces full-rank
oriented and x-orbit compatibility profiles.

### Status

`RESTRICTED THEOREM`, `MODEL-BOUND`, `GO` for the theorem and
`NO-GO` for an exact low-dimensional linear-profile module.

### Assumptions

- `G=C_q` with prime `q`; x-orbits additionally require odd `q`.
- The complement support `D` is nonempty and proper.
- The target domain is all of `G`, including identity.
- Profiles retain integer orientation multiplicity.
- The main rank statement is over `Q` or `C`.

### Evidence so far

For `F_D(X)=sum_{d in D} X^d`, every Fourier eigenvalue
`F_D(zeta^k)` is nonzero. At zero frequency this is `|D|`. At nonzero
frequency, a zero would make the prime cyclotomic polynomial `Phi_q` divide the
0/1 polynomial `F_D`, forcing `D` to be empty or all of `G`.

Convolution by `1_D` is therefore invertible over `C` and, because its matrix is
integral with nonzero determinant, over `Q`. It maps the point-mass basis to all
oriented target profiles, proving their linear independence. It also maps the
independent orbit vectors `delta_0` and `delta_R+delta_-R` to independent
x-orbit multiplicity profiles.

The orbit profiles form a basis of the image of the even subspace. They form a
basis of the even subspace itself only when `D=-D`; this symmetry holds for the
registered sign-complete complement supports but must remain explicit.

The identity orbit uses `delta_0`, not `2 delta_0`. This correction does not
change independence in characteristic zero.

### Failure modes

- Over a finite field `K`, rank is controlled by
  `gcd(F_D(X),X^q-1)` and can drop at exceptional characteristics.
- Restricting targets can reduce observed rank; sampled schedules cannot prove
  the all-target theorem empirically.
- Boolean OR support is nonlinear and is not covered by the multiplicity rank.
- Full rank is not a circuit lower bound. A full-rank transform may still have a
  succinct description or fast structured application.
- One-witness output may discard multiplicity, while all-signed-witness output
  retains it.

### Next concrete action

Reject exact partition and exact low-dimensional linear-profile successors.
Before implementing a nonlinear first-witness branch operator, list the size and
construction cost of every subtree predicate, cached node, target specialization,
fallback, and witness pointer.

### Artifact paths

- `theory.md`
- `contract.md`
- `decision.json`

## Coordinator response

The theorem and its corrections are accepted. The rejection is limited to the
registered complete all-target partition and linear-profile models. Full-rank
structured transforms, nonlinear branch predicates, and dedicated generalized
root-finding remain open.
