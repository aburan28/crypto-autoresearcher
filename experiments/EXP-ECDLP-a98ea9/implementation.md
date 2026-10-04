# EXP-ECDLP-a98ea9 implementation (Stage 0–1)

Authorized by `DEC-20260907-39d016` and
`amendments/v1_execution_authorized.yaml`. Stages 2–5 are not implemented.

## Layout

- `implementation/ec_jac.py` — Jacobian group law over `Z/p^r Z` with
  weighted p-content normalization, plus affine helpers.
- `implementation/kfree_transport.py` — k-free lift: Hensel, then `[p]`
  applied `r-1` times, then multiply by `(p^{r-1})^{-1} mod n`.
- `implementation/static_provenance.py` — AST gate: that module never
  takes a discrete-log scalar.
- `implementation/stage0.py` — writes the transport lemma (zero compute).
- `implementation/stage1.py` — agreement gate at `r ∈ {1,2,3,4}`.
- `implementation/run_stage01.py` — driver that writes run records.

## Construction note

Double-and-add of the integer `p^{r-1}` hits pairs that reduce to the
same `F_p` point and breaks the generic Jacobian adder. The equivalent
construction `[p]` applied `r-1` times keeps every intermediate reduction
equal to `[p^j]S ≠ O` because `gcd(n,p)=1`. That is the same group
element `[p^{r-1}]P̃` required by the contract.

## What is not computed

No `ADV`, no comparator table, no planted ladder, no multiplicative arm.
Certificate kind is `none`.
