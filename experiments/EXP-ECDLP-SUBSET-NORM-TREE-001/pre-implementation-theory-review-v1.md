# Pre-implementation theory review v1

## Handoff: subset-norm tree paper preflight

### Claim or task

Audit the quadratic-extension encoding, resultant/gcd predicate, identity and
collision handling, witness self-reduction, and zero-run operator obligations.

### Status

`OPEN`: `REVISE`.

The finite-point intersection lemma and conditional tree self-reduction are
correct. The original records disagreed about oriented affine leaves versus
x-orbits, and identity and terminal-lift semantics were incomplete. No
implementation or execution is authorized.

### Assumptions

- `K/F_p` is a registered degree-two field extension with a canonical basis.
- D2 and D3 supports are deduplicated by oriented affine point while retaining
  at least one signed witness and audit multiplicity.
- Node polynomials are over `K`.
- Identity is represented by a separate sentinel.

### Evidence so far

The basis `(1,omega)` makes `enc(x,y)=x+omega*y` injective on affine points.
Translation `S -> Q-S` is injective. Therefore the node polynomial and the
finite translated-D3 polynomial share a root exactly when the node contains a
D2 point completing with a D3 point to `Q`. Gcd and resultant zero are exact
equivalent predicates.

Given an exact predicate oracle, left-first descent maintains a positive
invariant and reaches a compatible leaf in at most `ceil(log2(N2))` decisions.
This is an oracle-call theorem only; terminal D3 witness lift remains required.

### Required revisions

1. Use distinct oriented affine D2 points throughout; a single linear factor
   does not represent an x-orbit.
2. Register the irreducible quadratic, basis, serialization, and base-field cost
   of every extension operation.
3. Use the full identity formula

   ```text
   Hit(Q) = Hit_ff(Q)
            or (o_2 and Q in D3)
            or (o_3 and Q in D2).
   ```

4. Define the empty product and the target-dependent degree drop when `Q in D3`.
5. Separate one deterministic witness from audit multiplicity.
6. Make terminal D3 membership and three-id lift part of exactness and advice.
7. Require hereditary child-subset restriction and exact positive and negative
   certificates.

### Narrowest valid theorem

`RESTRICTED THEOREM`: for distinct oriented finite D2 and D3 supports in a
registered quadratic encoding, resultant/gcd zero is exactly finite
D2-translated-D3 intersection. An exact predicate oracle plus exact terminal
lift returns one five-leaf witness in logarithmically many oracle calls.

`NEGATIVE RESULT`: the subset tree alone provides no time or memory advantage.
Naive `C_Q`, all leaf predicates, and `C_Q mod M_root` require respectively
`Theta(B^3)`, `Theta(B^2)`, and `Theta(B^2)` target outputs or state.

### Failure modes

- One orientation cannot stand for an entire x-orbit.
- A compact root operator may not restrict compactly to child subsets.
- Exact node bits can hide a D2 vector or translated D3 polynomial.
- Tier B terminal lift can recreate explicit D3 advice.
- Streaming all leaves lowers resident state without lowering online work.
- Full ordinary rank does not rule out short displacement generators.

### Next concrete action

Independently replay the identity-complete intersection theorem, degree-drop
semantics, deterministic witness choice, and child-subset restriction before
deriving the root displacement equation.

### Artifact paths

- `contract.md`
- `theory.md`
- `object-dimension-ledger.md`
- `hypothesis.json`

## Coordinator response

The v1 `REVISE` decision is preserved. The records now use oriented affine
leaves, a registered quadratic extension, the full identity formula, empty and
degree-drop semantics, deterministic witness selection, hereditary restriction,
and exact negative certificates. Status remains `REVIEW_REQUIRED` because the
root operator, displacement equation, ranks, child restriction law, and
terminal Tier B lift remain undefined.
