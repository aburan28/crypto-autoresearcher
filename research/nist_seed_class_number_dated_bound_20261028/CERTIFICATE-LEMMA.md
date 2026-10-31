# Split-prime subset certificate

Let K be an imaginary quadratic field with fundamental discriminant D<0. Let q_1,...,q_k be distinct rational primes splitting in K, and choose one prime ideal P_i of norm q_i above each. Put Q=product(q_i).

If 4Q<|D|, then h(K)>=2^k.

Proof. Consider the2^k ideal classes of products I_S=product(P_i:i in S), one for every subset S. Suppose two distinct subsets S,T give equal classes. Then I_S*conjugate(I_T) is principal. Cancel the rational ideals (q_i) from indices in their intersection. The remaining integral principal ideal has norm N=product(q_i:i in the symmetric difference). This N is squarefree and greater than1, with N<=Q.

Its generator alpha is an algebraic integer. If alpha is rational, it is an ordinary integer and its norm is a square, contradicting the squarefree N>1. If alpha is nonrational, write alpha=(a+b*sqrt(D))/2 with nonzero integer b (with the appropriate parity condition). Then Norm(alpha)=(a^2+|D|b^2)/4>=|D|/4>Q>=N, again a contradiction. Thus all subset classes differ.

This is a lower-bound certificate, not a computation of the full class group. For the fixed dated RFC bound, k=24 gives h(K)>=16,777,216>10,000,000. The ring class map Pic(O_f)->Pic(O_K) is surjective, so this also lower-bounds the class number of the actual CM order. The converse inference from a large Frobenius-order class number to the maximal-order class number is not valid.

No cohort witness has been evaluated in this planning record. An independent implementation check and the full fixed-identity comparison remain required.
