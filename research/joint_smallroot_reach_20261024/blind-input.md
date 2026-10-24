# Blind determinant derivation input

This is a software/mathematical instrument audit, not a scientific trial or a
hypothesis-state transition. Work only from the lattice definitions below.

Let p be prime, f an integer polynomial with leading coefficient 1 under a
fixed monomial order, and f(r) = 0 modulo p. At multiplicity t, a square
triangular coefficient lattice has one row per monomial a in a finite set M.
The row assigned power k is

    p^(t-k) * x^(a-k*LM(f)) * f^k,   0 <= k <= t.

All row supports lie in M and their leading monomials are distinct. Scale
column a by the product of X_i^a_i. Let N be the row count, q the sum of
the row modulus exponents t-k, and s_i the sum of a_i over columns.

1. Derive the determinant and the determinant-level Howgrave-Graham budget
   for a polynomial that vanishes as an integer at the root. Separate this
   necessary/sufficient lattice heuristic from algebraic independence and
   actual root extraction. Include LLL and norm factors when relevant.
2. Specialize to the full-box support [0,d]^n, with
   M_k = [kd,td]^n and rows from M_k minus M_(k+1). Derive the finite-t
   equal-bound exponent and its large-t limit. Evaluate n=1,d=2,t=1 and
   n=3,d=2,t=1. Do not use existing code or numerical conclusions.
3. Independently construct the t=1 lattice for

    f=(x-y)^2*z^2 - 2*((x+y)*(x*y+a)+2*b)*z
      + (x*y-a)^2 - 4*b*(x+y),

   at a=2,b=3,p=101,X_x=X_y=X_z=2. Use f once and p times each other
   support monomial. Compute its exact determinant and compare it with the
   expression from step 1. This is an arithmetic fixture, not a DLP solve.

For a joint-system follow-up, consider S3(x1,x2,u), S3(x3,x4,v), and
S3(u,v,xQ), with xQ fixed. State what a single-equation determinant bound
does and does not establish about a lattice built from products of all three.

Write the derivation and commands into independent-review.md. Read only this
file, AGENTS.md, agents/validator.md, and the assigned handoff. Do not read the
producer calculator, closure note, proposal, report, candidate implementation,
or other review outputs before delivering your independent derivation.
