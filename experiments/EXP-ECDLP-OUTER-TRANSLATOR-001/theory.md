# Theory note: exact outer comparator and Semaev root-product translator

## Claim status

- `RESTRICTED THEOREM`: exact `D2 + D3` is a complete five-term lookup for the
  represented factor base.
- `RESTRICTED THEOREM`: the root-product/gcd construction identifies exactly the
  nonidentity D2 x-orbits satisfying the configured Semaev relation, assuming
  correct finite-field polynomial arithmetic.
- `HYPOTHESIS`: coordinate source sets make that construction cheaper than the
  exact outer-aware complete comparator.
- `TOY-EVIDENCE`, `MODEL-BOUND`: all experiments in this cycle.

## Exact 2+3 completeness

Let `D2={f_i+f_j}` and `D3={f_i+f_j+f_k}` with full point keys and one witness
per key. A point `Q` has a five-term decomposition over `F` if and only if there
is `A in D2` with `Q-A in D3`. Therefore scanning every D2 key is complete.
The heuristic random-set scale `|D2| about B^2`, `|D3| about B^3` gives space
`q^(3/5)` and online work `q^(2/5)` when `B about q^(1/5)`. This is a generic
meet-in-the-middle tradeoff, not a non-generic ECDLP algorithm or a proved
preprocessing lower bound.

## Semaev construction

For `E: y^2=x^3+a*x+b`, use

```text
f3(X1,X2,X3) =
  (X1-X2)^2 X3^2
  - 2((X1+X2)(X1 X2+a)+2b) X3
  + (X1 X2-a)^2 - 4b(X1+X2).
```

For quadratics `A(z)=a2*z^2+a1*z+a0` and
`B(z)=b2*z^2+b1*z+b0`,

```text
Res_z(A,B) =
  (a2*b0-a0*b2)^2
  - (a2*b1-a1*b2)(a1*b0-a0*b1).
```

Applying this to `f3(U,V,Z)` and `f3(W,X,Z)` produces `f4(U,V,W,X)`,
of degree at most four in each x-coordinate.

## Source substitution lemma

Let branch `b` have distinct accepted source roots `t_i`, rational map
`phi_b=N_b/D_b`, and `D_b(t_i) != 0`. After multiplying by `D_b(T)^4`,

```text
S_b(T,V,W) = D_b(T)^4 f4(phi_b(T),V,W,x(Q))
```

is polynomial. Hence

```text
product_i S_b(t_i,V,W)
 = product_i D_b(t_i)^4
   product_i f4(x(f_i),V,W,x(Q)).
```

The scalar is nonzero, so both products have identical zero sets and gcds after
the remaining elimination. This is an implementation invariant, not evidence
of compression.

## Root-product lemma

Let `R` be the set of distinct nonidentity D2 x-coordinates and
`M2(V)=product_{r in R}(V-r)`. The roots are distinct because `F_p` is a field.
For the combined factor product `G_Q(V,W)`, define

```text
H_Q(V) = product_{w in R} G_Q(V,w) mod M2(V).
```

For every `v in R`, reduction modulo `M2` preserves evaluation and

```text
H_Q(v)=0 iff some w in R and some factor x-root u satisfy
f4(u,v,w,x(Q))=0.
```

Therefore `gcd(H_Q,M2)` has exactly the compatible nonidentity D2 x-roots.
Because `F`, `D2`, and their negatives are sign complete, an `f4` root on
rational curve x-coordinates can be oriented to a full point equation with
right-hand side `Q`; the implementation must still recover and verify the exact
five factor leaves. D2 identity cases are outside x-coordinate Semaev equations
and require an explicit charged scan.

## S3 identity correction

The finite-root S3 product alone omits exact decompositions `Q=A+O`. For affine
`Q`, the exact control is

```text
C_Q(V) = (V-x(Q)) product_{w in R} f3(V,w,x(Q)) mod M2(V).
```

The added factor is inert unless `x(Q)` is a disclosed D2 root. Add an identity
sentinel iff `Q in D2`. For `Q=O`, every finite D2 orbit is compatible through
`A+(-A)` and the identity target requires a separate branch because `x(Q)` is
undefined. The emitted control uses the zero remainder modulo `M2`, recovers
one exact four-leaf witness for every finite orbit, and records `O+O` as an
identity sentinel.

For S4 first-witness semantics, an identity-side five-term witness can be
rerouted to finite D2 halves using sign completeness and repeated leaves. A
complete candidate API must still disclose the identity sentinel iff `Q in D3`.

## Symmetry-matched D3 codec

A fair full-D3 advice comparator stores one x key and one witness per
`{P,-P}` orbit, chooses the affine-minimum orientation canonically, and derives
the negative witness by toggling each adjacent sign-pair factor index. The
translator gate compares against this codec, not a table that stores both full
affine orientations independently.

## Proof track

1. Prove the dependency-free `f3/f4` implementation against the quadratic
   resultant identity and a tiny independent symbolic oracle.
2. Prove source substitution up to the exact denominator scalar for every
   accepted root.
3. Prove modular root-product evaluation and gcd roots equal direct enumeration.
4. Prove every compatibility root maps to a signed D2/factor witness and verify
   the five leaves by independent EC addition.
5. Derive a product-tree or modular-composition successor only from measured
   degree, density, and operation counts.

## Disproof track

1. Search for target/family instances where denominator clearing vanishes,
   source roots collide, or source and direct products differ.
2. Search for Semaev roots that do not lift to exact rational signed witnesses.
3. Measure whether `G_Q`, reduced `H_Q`, or gcd/root extraction becomes dense.
4. Compare all online coefficient operations with exact scalar and batched
   `D2 + D3`, not only with the failed source-tag scanner.
5. Charge the identity route, target-specific workspace, and witness backsolve.
6. Treat a random-x match as evidence against coordinate-specific structure.

## Matching and amortization boundary

Family-specific supported targets test correctness and exact witness recovery;
they are not used for coordinate/null ratios. Those ratios use identical
family-independent uniform points on each curve and report each factor base's
exact support count. Many-target totals are `preprocessing + K*mean_online` for
`K in {1,B,16B}`. Until target work is actually shared, these are independent-
target projections rather than batch complexity improvements. Preprocessing
crossover uses `max(0, P_translator-P_D3)`, not translator preprocessing in
isolation.

## Limitation

A negative result applies only to this exact root-product representation and
the configured source maps. It does not rule out asymptotically fast
resultants, multipoint evaluation shared across many targets, different
coordinates, all-witness relational states, or index calculus generally.
