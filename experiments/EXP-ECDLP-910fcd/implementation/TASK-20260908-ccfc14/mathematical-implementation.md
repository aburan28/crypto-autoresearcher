# Mathematical and interface implementation notes

This note describes code-level deductions from the frozen
`EXP-ECDLP-910fcd/specification.yaml`, its approved implementation correction
decision `DEC-20260908-cfcacc`, and the explicitly hash-bound predecessor
`TASK-20260906-681152`. It contains no observed pairing, control, calibration,
or cost result.

For a monic polynomial

\[
f(X)=X^k+a_{k-1}X^{k-1}+\cdots+a_0 \in \mathbb F_p[X],\qquad a_0\ne0,
\]

the Rabin criterion tests

\[
X^{p^k}\equiv X\pmod f
\quad\text{and}\quad
\gcd(X^{p^{k/\ell}}-X,f)=1
\quad (\ell\mid k\text{ prime}).
\]

The comparison is between residues in the quotient. When `k=1`, `X mod f` is
the base-field constant `-a0`, so comparing a reduced Frobenius residue with
the unreduced coefficient vector `(0,1)` is wrong. The runner stores both
`reduced_x` and `frobenius_x`, while the higher-degree gcd witnesses stay
unchanged. `PolynomialField(p, modulus)` then represents the `k=1` branch as
Fp without inventing an extension construction.

For a selected public second argument `T` and shift `S`, the predecessor’s
binary Miller calculation evaluates the shifted divisor quotient

\[
f_{r,P}((T+S)-(S)),
\]

and `evaluate_shifted_tate` applies the explicit final exponent

\[
 (p^k-1)/r.
\]

Any zero denominator or exceptional divisor is an archived rejection. The
runner accepts `chi(G)` only if `chi(G)^r=1` and `chi(G) != 1`; the exact
control later compares `chi([a]G)` to `chi(G)^a` for every `a` in `0..r-1`.
Those statements are coded for a future authorized run; this task did not
execute them.

Both decoders use `m=ceil(sqrt(r))`, baby exponents `0..m-1`, giant steps
`0..m`, a candidate bound below `r`, and a final group equality check. The
character answer is additionally checked by `[a]G=Q`. Setup tables are built
once inside one public evaluator batch; query work is subsequently separated
into Tate evaluation, field giant steps, curve giant steps, and final curve
verification. The implementation reports operation counts as explicitly
unavailable because this Python arithmetic has not been instrumented at an
operation level; elapsed time is never converted into a fabricated operation
count.

The evaluator payload is a typed closed object. It contains only the public
fixture tuple, public context `(p,k,r,modulus,A,B,G,T,shift,chi_g)`, block and
order information, and `Q` points. The verifier-held random labels are not a
field in that schema. Both the parent serializing boundary and the evaluator
child parse exact keys recursively, reject duplicate JSON keys, require vector
width `k`, and reject arbitrary nested mappings. The known-false dishonest
control injects a top-level label then feeds that same bytestring into both
validators; it succeeds only if both reject it.

For a fixture/seed pair, the SHA-256 rejection stream first generates a fixed
list `(a_0,...,a_63)`. The q=1 workload is exactly `(a_0)`, and every repeat
and every one of the seven blocks reuses the same appropriate prefix. Blocks
have executable order: even blocks evaluate curve then character, odd blocks
evaluate character then curve. This is distinct from merely labelling records
with an alternating order.

The measured future total for one emitted row is reconstructed from retained
components. Shared deterministic selection is allocated one eighth to each
selected fixture in both arms. The character arm includes field construction,
all T/shift search rejects, accepted `chi(G)`, field table setup, Tate query
evaluation, field giant steps, reconstruction, and final verification. The
curve arm includes its own table, curve giant steps, reconstruction, final
verification, and the same allocated shared selection. The row also retains
wall time, table/output bytes, child/process-group RSS, and the unavailable
operation-count marker. Medians and the frozen q=64 decision predicates are
data; the runner does not make a scientific conclusion.

The frozen pairing definitions and source API provenance are already recorded
as `retrieved` in the experiment specification. This file makes no new
literature claim and relies on no recalled citation.
