# Factorised one-hot selector: prospective SAT ablation

This is an unapproved design alternative to the binary barrel-shift selector in SAT_SUCCESSOR_DESIGN_NOTES.md. It has no measurements or scientific status claim. Freeze the choice or the full comparison family before any solver target is observed.

For the 19 Frobenius shifts introduce one-hot Boolean indicators J_0,...,J_18 and two shared plane coordinates u,v. Add U_j=J_j AND u and V_j=J_j AND v. With a,b,c expressed in a verified normal basis, the kth normal coordinate of x is the native XOR equation

    x_k = XOR_j (a_(k-j) J_j XOR b_(k-j) U_j XOR c_(k-j) V_j),

where subscripts are modulo19 and multiplication by a displayed basis bit either retains or removes the term. Exactly one J_j is true, so the expression equals the selected conjugate of a+u*b+v*c. Conversely every legal (j,u,v) satisfies the encoding. Four distinct full seed orbits ensure the resulting76xvalues are distinct.

This shares only38 nonlinear AND outputs across all19 coordinate equations, plus the exactly-one machinery and coordinate conversion. It may expose the common u,v structure more directly than a five-layer mux circuit, but native XOR length, one-hot propagation and clause interactions can dominate. Gate counts alone cannot select a winner.

The strong explicit control uses76one-hot point selectors with coordinate implications and reverse disjunctions for each coordinate bit. Both controls must receive the same cardinality implementation, arithmetic optimizations, target ordering, symmetry breaking and model replay. Comparing a carefully factorised candidate only against a weak binary lookup would not isolate the affine-plane mechanism.

The important ablation is shared versus independent seed choices across shift blocks. Replacing the shared u,v by unrelated u_j,v_j under exactly one active J_j preserves the allowed x-domain; any observed change in propagation comes from the auxiliary representation, not a larger or smaller factor base. Charge extra gates and keep all model/relation checks identical. This is a same-object encoding control and requires no null base selected on target timings.

A future fixed panel could compare both predeclared structured encodings, the strong explicit control, and a native coordinate MITM control. Report every arm and every censored case; selecting the faster structured encoding from those results requires a fresh holdout or explicit multiplicity treatment. No such run is authorized by this note.
