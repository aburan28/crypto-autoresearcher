# Witness-assisted interval factor recovery by commuting projectors

Status: preliminary derivation, unreviewed and unimplemented. Scientific acceptance: false. No trials or solver calls. Source input for IDEA-20261030-a62c58, not a replacement for complete signed-chart verification.

## Proposition and input contract

Let p be prime, U in F_p[X] monic of degree k>=1, and Q=F_p[X]/(U). Let s>=0, 2^s<p, t in F_p, and suppose supplied quotient elements e_0,...,e_(s-1) satisfy

    e_j^2=e_j,
    n^k=0, where n=X-t-sum_j 2^j e_j in Q.

The interval is the field set {t+a mod p : 0<=a<2^s}; it may wrap. No bound k<p is assumed. The intended elliptic-curve application additionally has p>3 and k<=5, but this algebraic statement does not need those restrictions.

Given these witnesses, a deterministic algorithm recovers distinct interval coordinates x_i and positive INTEGER multiplicities m_i with

    U(X)=product_i (X-x_i)^m_i,  sum_i m_i=k.

Using classical dense quotient arithmetic and Gaussian elimination, construction, recovery and the checks below take O((s+1)k^3) field operations, counting field inversions as operations rather than hiding them. The bound is conditional on already supplied witnesses. It is not a bound for finding the e_j, solving the chart, recovering signs, or a measured speed result.

## Construction

Use the basis 1,X,...,X^(k-1). Let M be multiplication by X and E_j multiplication by e_j. Quotient multiplication is faithful and commutative, so E_j^2=E_j and all E_j commute with one another and M.

Maintain a list of pairs (V,b), where columns of V are a basis of a nonzero subspace and b is a bit prefix. Initially V is the identity k by k matrix and b is empty. For each j, replace every pair by the nonzero column-space bases

    (basis((I-E_j)V), b appended with 0),
    (basis(E_j V),     b appended with 1).

Use Gaussian elimination to select independent columns. Never enumerate all 2^s labels. For a final bitword b, output x_b=t+sum_j 2^j b_j mod p and m_b=number of columns in V_b.

## Proof of the splitting invariant

Initially Q is M-invariant and invariant under every E_j. Inductively, commutation preserves those invariances on images of the processed projectors. For any projector E on an invariant space V, every v decomposes as Ev+(I-E)v. The two images intersect only at zero: E acts as identity on the first and zero on the second. Thus each split is a direct sum and dimensions are preserved.

After processing j bits, the surviving spaces form a direct sum of dimension k, and each previous E_i acts on its space as its recorded bit b_i. There are at most k nonzero spaces at every depth. This holds in every characteristic; dimensions are integers obtained from elimination, not traces modulo p.

## Proof of factor recovery

Multiplication by n has kth power zero because n^k=0 in Q. On a final space V_b, this operator is M-x_b I. Hence the restriction of M has the form x_b I plus a nilpotent operator and has characteristic polynomial (T-x_b)^m_b. The direct-sum invariant gives the product of these characteristic polynomials on Q.

The characteristic polynomial of multiplication by X on Q is U: its matrix is the companion matrix of U (equivalently, 1 is cyclic and its minimal polynomial is the degree-k polynomial U). Therefore the reported product equals U exactly. Distinct bitwords give distinct field coordinates because the integer labels lie in [0,2^s) with 2^s<p. Adding t preserves injectivity even when the interval wraps.

## Converse and uniqueness of the interval witnesses

Suppose U already splits into powers of distinct linear factors with coordinates in the interval. The Chinese remainder decomposition is

    Q = product_i F_p[X]/((X-x_i)^m_i).

On each local factor, define e_j to be the jth bit of the unique interval label of x_i. CRT supplies quotient elements with those components. They are idempotents. On each factor n is X-x_i, whose kth power vanishes since m_i<=k, giving existence.

Conversely, an idempotent in a local ring is zero or one: if its residue is zero then 1-e is a unit and e(1-e)=0 forces e=0; if its residue is one, e is a unit and e(e-1)=0 forces e=1. The nilpotence equation on the residue field forces x_i=t+sum_j 2^j b_j. Interval injectivity fixes every bit, so CRT fixes every e_j uniquely. This is uniqueness of interval-membership auxiliaries for fixed U,t,s, not uniqueness of signed divisors or A,B chart functions.

## Cost and certificate boundary

Build each E_j from k reduced products e_j X^i. The conservative classical bound is O(k^3) field operations per matrix. At one splitting depth the current dimensions d_i sum to k. Multiplying the k by k projector into all k by d_i bases costs O(k^3); column elimination costs sum_i O(k d_i^2)<=O(k^3). Streaming one projector uses O(k^2) workspace beyond O(sk) input field elements and at most k bit labels of length s. Fixed-input quotient checks e_j^2=e_j cost O(sk^2); binary powering for n^k costs O(k^2 log(k+1)). These fit the stated bound. Bit-operation costs of modular multiplication and inversion must be charged separately when instantiating a runtime claim.

An independent factor checker needs no trust in the reported ranks: check canonical labels, positive integer multiplicities, distinct coordinates, sum m_i=k, and multiply product_i (X-x_i)^m_i to compare coefficients with U. Sequential multiplication of k linear factors costs O(k^2) field operations. Original witness equations remain part of the chart verifier; this factor certificate does not replace them.

For k=0 use the separate U=1 empty-support case; no matrix split. For s=0 the interval has one element t and there are no idempotents; n^k=0 implies U=(X-t)^k.

## Characteristic-five example (hand derivation only)

Over F_5 let U=(X-1)^5, s=1, t=0, and e_0=1. Then (X-e_0)^5=0 in Q. The only nonzero space is the one-bit image of the identity projector. Its dimension is 5, although trace(I_5)=0 in F_5. The output is coordinate 1 with multiplicity 5. This is an algebraic example, not an executed fixture or an elliptic-curve chart instance.

## Remaining signed-chart obligations

This removes a generic polynomial-factorization step only for x-support recovery from supplied, checked interval witnesses. It does not construct those witnesses or yield certified pruning from partial assignments. Recovering the signed zeros of h=A+B*y still requires local orders, subtracting exactly -R for a finite target, all lower pole/identity charts, common A,B roots, inverse pairs, two-torsion, and identity padding. Square-root work for balanced pairs must still be accounted for. Do not infer that all signed recovery is now deterministic with the stated cost.

The older coefficients.py uses X^d-c coset/Graeffe membership; this proposition applies to the selected interval-idempotent construction. It does not silently identify their domains. No-wrap moment substitutions are optional stricter subcases and are unnecessary here.

## Sources and novelty boundary

Retrieved 2026-10-30: Stacks Project Example10.35.24, https://stacks.math.columbia.edu/tag/00GG, supports the standard classification of idempotent matrices and explains why their traces can lose rank information in positive characteristic. Section10.53, https://stacks.math.columbia.edu/tag/00J4, supports the finite-algebra/local-factor background. The recovery algorithm, cost accounting and application are the present unreviewed derivation. These reads do not establish novelty or constitute an independent proof review.
