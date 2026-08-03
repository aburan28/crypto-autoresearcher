# Pre-implementation theory review v1

## Handoff: generalized-root circuit paper preflight

### Claim or task

Audit the five-case EC addition cover, five-leaf equivalence, exceptional routes,
registry semantics, and zero-run proof gate.

### Status

`OPEN`: `REVISE`.

The typed five-case addition relation is correct. The original equivalence
statement was not literally true for the raw polynomial circuit because public
registry membership was applied afterward. No implementation or execution is
authorized.

### Assumptions

- `p>3`, the curve is nonsingular, and all points lie in an odd-order subgroup.
- `O` and affine points are distinct algebraic types.
- The registry may contain duplicate identifiers or multiple orientations over
  one source/x fiber.
- Repeated identifier use is allowed.

### Evidence so far

- The identity branches cover one or both identity inputs.
- The ordinary inverse witness enforces `x_P != x_R`.
- Odd subgroup order excludes finite `y=0`, so doubling and inverse cases are
  disjoint.
- Equal finite x-coordinates imply `R=P` or `R=-P`.
- Chaining four exact typed additions computes `P_1+...+P_5`, including
  doubling, inverse pairs, repeated leaves, identity intermediates, and `Q=O`.

### Required revisions

1. Define an exact decoration relation `Reg(b,t,x,y)` and state equality of the
   public-id projections, not a bijection of coordinate solutions.
2. Freeze branch enumeration as the primary semantics. Any one-hot encoding
   needs Boolean, exactly-one, and inactive-equation saturation rules.
3. Register unique integer lifts `0<=t_i<T_i<=p` and account for aliases.
4. Charge rejected algebraic roots, registry filtering, and duplicate
   identifier expansion.
5. Add a complete candidate-list bound, integer coefficient growth, and bit
   complexity to the zero-run gate.
6. Parameterize actual relation attempts by
   `A=ceil(B/(epsilon5*eta_rank))`.

### Narrowest valid theorem

`RESTRICTED THEOREM`: the five typed branches define the EC group-law graph on
the registered odd-order subgroup. After adjoining exact registry decorations,
the public-id projection of the four-gate circuit is exactly the ordered
five-leaf witness set.

`NEGATIVE RESULT`: constant graph width and `5^4` branch patterns alone give no
bounded-root advantage. At `T_1*...*T_5 approximately B^5 approximately p`, a
positive path needs an additional proved algebraic dependency.

### Failure modes

- External filtering can hide extraneous algebraic roots.
- Duplicate fibers can distort solution and witness counts.
- A lattice filter can leave a completion list too large to certify.
- Full-field intermediate variables can recreate a D2-sized eliminant.
- Constant support or rank yield can be silently assumed in batch exponents.

### Next concrete action

Independently replay the decorated projection identity over all typed branch
patterns and duplicate-id cases, then derive one explicit shift family. Do not
implement a solver.

### Artifact paths

- `contract.md`
- `theory.md`
- `object-dimension-ledger.md`
- `hypothesis.json`

## Coordinator response

The v1 `REVISE` decision is preserved. The theory and contract now define
`Reg`, projection equality, selector semantics, unique integer lifts,
candidate-list and registry costs, integer bit complexity, and the actual
`epsilon5,eta_rank` attempt count. Status remains `REVIEW_REQUIRED` because the
shift family, recovery inequality, slack, and completion dimensions remain
undefined.
