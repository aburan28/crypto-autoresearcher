# Four-partition signed pair join

This is a derived correctness argument, not an executed result. Assume P-256's
published prime-order group, four disjoint index partitions of equal size n,
finite valid points and globally distinct x coordinates. A relation has one
point from each partition. Simultaneous negation permits its first sign to be
fixed positive.

For indices i,j,k,l in the four partitions and s,t in {+1,-1}, compute

    A = P_i + s P_j,   B = P_k + t P_l.

Neither sum is the identity because equal or inverse input points would share
an x coordinate. On a short Weierstrass curve, x(A)=x(B) implies A=B or A=-B.
If A=B, emit signs (1,s,-1,-t); if A=-B, emit (1,s,1,t). Every emitted row is
rechecked as a point sum. Conversely every signed four-partition relation,
with first sign positive, appears by setting s to its second sign and t to
its fourth sign divided by its third sign. Thus the join enumerates the same
relations as the complete 8*n^4 signed quadruple set, without treating a
summation-polynomial root as a rational signed relation automatically.

The join forms 2*n^2 left and 2*n^2 right pair sums. These are pair evaluations,
not total group-operation or ECDLP costs. Hash buckets retain every collision
and full output. The table has 2*n^2 entries; output memory is additional.
Construction, validation, signs, labels, inversions, failures and verification
remain charged separately in counters. An independent oracle uses Jacobian
arithmetic and exhaustive index/sign enumeration, with no coordinate hash
join and no import of producer arithmetic.

For R_i=a_i G+b_i Q, each checked relation yields

    A_label = sum c_i a_i mod r,  B_label = sum c_i b_i mod r.

If B_label is nonzero, d=-A_label/B_label is only accepted after dG=Q.
If B_label=0, a valid relation forces A_label=0 and supplies no target
information. The solver accepts points and partition indices only. It never
sees labels, Q or a fixture witness. Label assessment follows the search.

For ideal independent uniform label pairs conditioned on their point values,
the b_i remain uniform. A point-only selection of a coefficient vector nonzero
modulo r makes B_label uniform. Integer c=(r,0,...) is excluded from that
premise. Deliberately arranged labels and selection that reads labels are
outside the premise. SHA-derived deterministic test cases do not measure it.

The ideal independent uniform-point model has 8*n^4 signed choices and
expected raw dependency count 8*n^4/r before rejection. With uniform distinct-x
points, exposing the final representative gives a safe union bound
8*n^4/(r-7). This is a model-only bound; this pass neither samples that exact
law nor estimates a rare-event probability. Sparse fixed P-256 domains may
contain no dependency. Even if pair-join work is quadratic in n, the model
requires n on the order of r^(1/4) for constant raw relation count and therefore
square-root-scale pair work/storage. No generic attack advantage follows.
