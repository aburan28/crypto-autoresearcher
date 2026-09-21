# Standalone blind rederivation for TASK-20260824-caf255

## Scope and notation

This is a derivation from `blind-statement.yaml` only, under the standalone
handoff for this task. It does not inspect an implementation, own any review
joint, compare with another artifact, or issue a claim-level verdict.

Write

- `lambda = (q,s,e,z)` for the immutable label tuple;
- `beta(lambda) = e AND NOT z` for the effective enable;
- `A_lambda = T_s(q)`;
- `t(q,s) = enc(T_s(q))` for the bit string loaded into `Q`;
- `mu(q,s,R) = m_s(q,R)` for the exceptional-mask string;
- `b_Q = |Q|`, `b_M = |M|`, and `b_W = |W|`.

All XORs below are bitwise. The frozen accumulator action is denoted
`R boxplus A`. No group-law formula is assumed here: the required primitive
must supply the exception-aware permutation on the complete frozen encoding
domain, including the explicit encoding `O`.

## Reversible maps and the primitive obligation

The effective-enable computation is the reversible toggle

```
C_f: f <- f XOR (e AND NOT z).
```

For a literal reading of the declared mask `m_s(q,R)`, define the coherent
XOR loader

```
L: Q <- Q XOR f*t(q,s)
   M <- M XOR f*mu(q,s,R).
```

The loader leaves `q,s,e,z,f,R` unchanged and is its own inverse for any
fixed value of its controls. Its truth tables can be synthesized from
X/CX/MCX target toggles, with every negative literal either retained as a
declared negative-control polarity or opened and closed by X gates.

The controlled exception-aware accumulator primitive `P` must satisfy all of
the following. These are assumptions on the supplied arithmetic primitive,
not consequences of the correction layer.

1. `P` is a computational-basis permutation on its full declared register
   domain, so that it has a unitary linear extension even away from the clean
   subspace.
2. `P` does not change `q,s,e,z,f` or `Q`.
3. For every frozen encoded accumulator value `R`, including the cases
   represented by `O`, `A`, `-A`, and `-2A`, on a legal loaded input it acts as

   ```
   P: (R, Q=f*t(q,s), M=f*mu(q,s,R), W=0)
      ->
      (R'=R boxplus f*T_s(q),
       Q=f*t(q,s),
       M=f*mu(q,s,R'),
       W=0).
   ```

4. In particular, `f=0` gives the identity accumulator block. For `f=1`,
   `R -> R boxplus T_s(q)` must be a bijection on the complete frozen encoded
   domain, with the prescribed exception behavior rather than a partial
   affine formula. Its inverse is the corresponding frozen subtraction map.

The post-map value of `M` in item 3 is necessary when `mu` really depends on
`R`. The arithmetic changes `R`, so preserving the pre-map mask would make the
second application of `L` toggle by `mu(q,s,R')` while `M` still contained
`mu(q,s,R)`; cleanup would then require the generally unjustified identity
`mu(q,s,R)=mu(q,s,R')`. Thus the exact cleanup alternatives are:

- transport `M` as stated above and apply the same self-inverse XOR loader at
  the post-map accumulator value; or
- define the loaded mask independently of `R`, in which case `P` may preserve
  it.

If "load from `q,s,f`" is intended to exclude `R` as even a read-only control,
then the declared `m_s(q,R)` cannot be the loaded Boolean function without an
additional specification. The mask must instead be independent of `R`, or be
computed and cleaned inside `P`. No silent choice among these formulations is
used here.

## Basis permutation, unitary extension, and blocks

The required sequence is the product

```
U = C_f ; L ; P ; L ; C_f,
```

where the semicolons show time order. Every X, CX, and polarity-declared MCX
gate is an involutive permutation of computational-basis strings. By
assumption `P` is also a basis permutation. Their composition is therefore a
basis permutation. The linear map that sends every basis ket to its permuted
basis ket preserves the orthonormal basis and is unitary. This argument applies
to the full circuit domain; it is not restricted to classical addresses.

On the subspace with `f=Q=M=W=0`, the cleanup proof below induces

```
U_clean = direct_sum over lambda=(q,s,e,z) of U_lambda,

U_lambda = I_R                         if e=0 or z=1,
U_lambda: |R> -> |R boxplus T_s(q)>   if e=1 and z=0.
```

Equivalently,

```
U_clean = sum_lambda |lambda><lambda| tensor V_lambda,
```

with `V_lambda` equal to the block shown above and all work registers returned
to zero. Because `q,s,e,z` are never targets, distinct label blocks never mix.
For any finite superposition

```
sum_(lambda,R) alpha_(lambda,R) |lambda,R,0_f,0_Q,0_M,0_W>,
```

linearity gives the same amplitudes on
`|lambda,V_lambda(R),0_f,0_Q,0_M,0_W>`. In particular, `e=0` and `z=1` are
identity blocks even when they occur coherently alongside enabled blocks.

## Cleanup and liveness in sequence order

Starting from a basis state with all clean targets zero:

1. **Compute `f`.** `C_f` changes `f` from zero to `beta=e AND NOT z`.
   It does not change any label.
2. **Load.** `L` produces
   `Q=beta*t(q,s)` and `M=beta*mu(q,s,R)`. The label tuple, `R`, and `W`
   are unchanged.
3. **Arithmetic use.** `P` consumes the live `Q` and `M`, maps
   `R` to `R'=R boxplus beta*T_s(q)`, preserves `Q`, transports an
   `R`-dependent mask to `M=beta*mu(q,s,R')`, and returns `W` to zero.
   Correctness is required on every exceptional encoding named in the
   primitive obligation.
4. **Unload.** Applying the identical XOR loader at the post-map state gives

   ```
   Q <- beta*t(q,s) XOR beta*t(q,s) = 0,
   M <- beta*mu(q,s,R') XOR beta*mu(q,s,R') = 0.
   ```

5. **Uncompute `f`.** The unchanged `e,z` controls make the final `C_f`
   toggle `f` from `beta` back to zero.

The liveness intervals are:

- `f`: defined by the first `C_f`; live throughout load, arithmetic use, and
  unload; dead only after the final `C_f`.
- `Q`: defined by load; live through the accumulator invocation; dead after
  unload.
- `M`: defined by load; its exceptional predicate must remain live through
  the accumulator invocation; if it depends on `R`, its representation is
  transported during that invocation; dead after unload.
- `W`: clean on entry to `P`, live only inside `P`, and clean again before
  unload.
- `q,s,e,z`: immutable for the whole circuit. They are live controls where
  used and retain their input values at every boundary.
- `R`: live from entry through the accumulator invocation and, when `M`
  depends on the post-map `R`, through mask unload; it is the only intended
  non-work output.

Unloading before arithmetic use removes the inputs on which the legal-input
contract for `P` depends, so it does not implement the stated enabled block.
Omitting unload leaves `Q` or `M` as a function of the coherent labels and
possibly `R`, so final work is nonzero and generally entangled. Clearing an
exceptional predicate before `P` likewise destroys information needed by a
reversible exception-aware branch; it is not cleanup of a dead value.

## Symbolic correction-layer counts

For each output bit `j` of the forward loader, let `F_j(x)` be its Boolean
truth table over its declared controls, and let

```
h_j = |{x : F_j(x)=1}|.
```

Let `T[p,n]` be the number of forward-load minterms, summed over all `Q` and
`M` output bits, having `p` positive and `n` negative control literals. Then

```
L_load   = sum_j h_j = sum_(p,n) T[p,n]
L_unload = L_load
L_qrom   = L_load + L_unload = 2*L_load.
```

Thus every output bit of Hamming weight `h` contributes exactly `h`
controlled target toggles to a forward load and another `h` to its inverse,
before elementary MCX decomposition.

With native negative-control polarities, the abstract gate inventory is

```
L_X  = 2*T[0,0]
L_CX = 2*sum_(p+n=1) T[p,n]
L_MCX[p,n] = 2*T[p,n] + 2*I[(p,n)=(1,1)]  for p+n >= 2.
```

The indicator term is the compute and uncompute of
`f ^= e AND NOT z`: each is one MCX with one positive and one negative
control. `L_X` includes the two appearances of every unconditional loader
target toggle. The single-control class is recorded as CX, including a
polarity-declared negative-control CX.

For an all-positive elementary convention, let `B_minus` be the total number
of negative-control wire intervals actually opened and closed across both
loader directions, after any valid sharing schedule. Each interval contributes
exactly two X gates. The two effective-enable invocations use two separate
opened-and-closed `z` intervals when labels remain physically unchanged
between sequence boundaries. Therefore

```
L_X = 2*T[0,0] + 2*B_minus + 4
L_CX = 2*sum_(p+n=1) T[p,n]
L_MCX[r,0] = 2*sum_(p+n=r) T[p,n] + 2*I[r=2]  for r >= 2.
```

If every qROM minterm opens every negative literal independently, then
`B_minus = 2*sum_(p,n) n*T[p,n]`; a grouped schedule must instead state its
smaller exact interval count. A negative-control sandwich may close only after
its last use. In particular, no accounting simplification may erase a live
exceptional predicate before the accumulator invocation.

At the abstract X/CX/MCX level, with `c_dec` and `d_dec` denoting the peak clean
and dirty ancillae of a chosen elementary MCX decomposition,

```
A_clean = 1 + b_Q + b_M + c_dec
A_dirty = d_dec.
```

For abstract MCX gates taken as primitives, `c_dec=d_dec=0`. The arithmetic
workspace is supplied separately: the composition has `b_W` additional clean
workspace bits for `P` (and any separately declared primitive ancillae).
The correction-layer gate inventory excludes the internal gates of `P` and
records exactly one controlled invocation of `P` per use.

No leading asymptotic coefficient for the full arithmetic construction follows
from these relations. Any expression of the form `3n+O(log n)` is admissible
here only as a conditional composition with independently supplied upstream
arithmetic bounds; it is not derived from this blind correction layer.

## Independent sparse exact-amplitude checking procedure

This is a procedure specification, not an executed experiment.

1. Represent a sparse state as a map `S: basis_tuple -> exact_amplitude`, where
   a key is `(q,s,e,z,R,f,Q,M,W)` and amplitudes are exact symbolic or algebraic
   values.
2. Initialize finitely many keys, including at least two distinct label blocks
   when checking coherence. Require each initialized work register to be zero.
3. For each X, CX, or MCX gate, compute its Boolean control predicate on every
   key and flip its target exactly when true. For `P`, apply an independently
   specified basis permutation satisfying the primitive obligation. Move the
   amplitude unchanged to the resulting key; combine amplitudes exactly if a
   malformed non-bijection ever creates a collision.
4. After every step, verify that `q,s,e,z` equal their initial values for the
   amplitude lineage, and that no output key occurs under a different label
   block. Verify exact amplitude transport, key multiplicity, and exact norm.
5. At the arithmetic boundary, verify per block that `f=0` leaves `R`
   unchanged and `f=1` maps `R` by the frozen exception-aware action. Include
   the explicit exceptional inputs `O`, `A`, `-A`, and `-2A` for the selected
   row.
6. At circuit end, require `f=Q=M=W=0` on every nonzero-amplitude key, require
   the expected block accumulator output, and require the exact input
   amplitude on that output key. Any cross-block key, residual work key,
   changed amplitude, lost key, or extra key is a failure of the specified
   check.

## Six known-false reasoning controls

These are reasoning controls to be applied to the procedure; none is reported
as an executed run.

1. **No-op Protocol.** Replace the enabled accumulator block by identity and
   choose an enabled row and accumulator for which the specified frozen
   translation is non-identity. The per-block accumulator check must reject
   the unchanged `R`; otherwise the checker proves too little.
2. **Classical address loop.** Replace the reversible address-controlled map by
   host-language iteration, measurement, or branch selection over `q`. Start
   with exact nonzero amplitudes on two addresses. The construction supplies no
   single amplitude-preserving basis permutation for that superposition, so
   the gate-by-gate coherent-permutation check must reject it.
3. **Missing unload.** Delete the inverse load. On any row with a nonzero
   loaded coordinate or mask, the final-work check finds `Q` or `M` nonzero
   and correlated with the block label.
4. **Pre-map flag cleanup.** Clear an exceptional predicate before `P` and use
   an accumulator in the exceptional set. The liveness check observes that the
   value is dead before its required use, and the exceptional per-block check
   has no reversible information path supporting the specified branch.
5. **Zero-digit omission.** Compute `f` without the negative `z` control and
   choose `e=1,z=1` with a non-identity row action. The required identity block
   changes `R`, so the block check rejects it.
6. **Partial arithmetic.** Substitute a primitive that implements only a
   generic affine formula. Check the named inputs `O`, `A`, `-A`, and `-2A`.
   By the control's definition, at least one differs from the frozen specified
   permutation, and the exact per-block check rejects that key.

## Review attestation

```yaml
review_attestation:
  task_id: TASK-20260824-caf255
  role: validator
  independent_session: true
  requested_policy: review-adversarial
  reasoning_effort: xhigh
  fallback_used: false
  degraded_requirements: []
  joints_owned: []
  sources_read:
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/blind-statement.yaml
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-COHERENT-QROM-PREADMISSION-20260824-aca034/handoffs/TASK-20260824-caf255.yaml
  read_sibling_reports: false
  blind_from_respected: true
  whole_claim_verdict: not_issued
  output_scope: standalone_derivation_only
```
