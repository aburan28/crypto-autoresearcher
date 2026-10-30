# Independent statement for normalization review

No implementation, derived bound, determinant, or observed joint result is supplied.
Work from this statement and primary sources, in a fresh session without parent
history. Seal a hashed derivation and source-read list before implementation access.

Use S(A,B,C)=(A-B)^2 C^2-2((A+B)(AB+a)+2b)C+(AB-a)^2-4b(A+B).
There are four leaf deviations z1,z2,z3,z4 and two internal deviations h1,h2.
Substitute leaves c_i+z_i and internals d_j+h_j into the three binary-tree
relations connecting leaves 1,2 to internal 1, leaves 3,4 to internal 2, and
internals 1,2 to fixed target q. Set a=2,b=3,q=5 and centers
(c1,c2,c3,c4,d1,d2)=(11,13,17,19,23,29). Common known modulus p; no integer
relations; all modular relation degrees and modulus-multiple degree 1; divisor
bound 1. The leaf/internal bound ratio vectors are (1,1,1,1,r,r).
Cells (r,mu)=(2,1),(2,2),(4,1),(4,2). Bounds guess is that vector divided by20;
precompute multiplicity mu. All t-shifts false; skip_reduce false.
Construct the monomial domain as all nonnegative integral points of the convex
hull of zero and mu times the exact nonzero exponent supports of the affine
relations. Map it to the formal-modulus polynomial ring. Independently derive
coordinate count/order, weighted order, mu normalization, and finite-domain
distinctions from source. No numerical bound optimization or scientific call.

Reference source: keeganryan/cuso at fb2747d2105a8e48499bf10a3a717cf80c14d079;
full Ryan eprint2024/1577 must be read before theorem certification.
After sealing the independent derivation, inspect the published native source
and compare it. Do not read the sibling reviewer report at any phase.
