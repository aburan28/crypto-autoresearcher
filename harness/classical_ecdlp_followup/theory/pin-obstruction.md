# Local basis obstructions and their exact limits

25 October 2026. This is an elementary derivation and an exact symbolic audit of a **specified local tensor representation**. It is not a new ECDLP algorithm, a literature novelty claim, a proof-assistant result, or a lower bound on arbitrary classical computation. Same-session mathematical checking does not constitute an independent scientific review.

## The object and convention

The Boolean AND tensor has two input legs and one output leg:

\[
T_{ijk}=1\quad\text{exactly when }k=i\mathbin{\mathrm{AND}}j.
\]

Its nonzero coefficients are at `000,100,010,111`, where the first two coordinates are inputs. Array mask bit 0 is the first input, bit 1 the second input, and bit 2 the output. A uniform change of basis uses an invertible matrix M on output legs and M^{-T} on input legs. This convention preserves a contracted wire because M^T M^{-T}=I.

An isolated output pin CONST0 or CONST1 is the one-leg vector e0 or e1, transformed to M e0 or M e1. No pin is absorbed into another tensor in the first proposition.

A single homogeneous weighted perfect-matching signature is **parity-pure**: its coefficients are supported on external subsets of one parity. Indeed, deleting an external subset leaves a perfect matching only if the number of remaining vertices is even. This necessary condition holds over any coefficient ring, regardless of planarity. It is not a sufficient tractability condition for a whole factor network. A sum of an even and an odd signature is a different representation.

## Proposition 1: the isolated two-pin common-basis model

Let K be a field and M=[[a,b],[c,d]] an invertible matrix over K. If both transformed pins are parity-pure, each nonzero column has at most one nonzero entry. Equivalently over a field, ac=bd=0. Invertibility forces the nonzero entries of the two columns into different rows, so M is diagonal or anti-diagonal. Its inverse transpose is also monomial.

A monomial transformation of each tensor leg only rescales coefficients by nonzero factors and optionally flips the leg bit. It cannot cancel any support coefficient. A pattern of leg flips shifts the parity of **every** supported index by the same amount. The AND tensor has both even and odd support, so it remains mixed-parity. Consequently no one common invertible basis over any field simultaneously makes the two isolated pins and this AND tensor homogeneous matchgate signatures.

This statement is parameter-uniform; the finite coefficient search below is a regression, not the proof for all matrices. It assumes both pins remain isolated and share the same M. Per-wire matrices, absorbed pins, larger-boundary block tensors and a different representation do not meet those hypotheses. Their success is neither asserted nor excluded by this proposition.

## The rational escape control is real

AND **alone** can satisfy the local matchgate conditions over Q. Take

\[
M=\begin{pmatrix}1&2\\1&0\end{pmatrix},\qquad
M^{-T}=\begin{pmatrix}0&1/2\\1&-1/2\end{pmatrix}.
\]

The transformed AND tensor has coefficient 1/2 exactly at `000,110,101,011` and zero elsewhere. It is even-parity and satisfies all checked Grassmann–Pluecker identities. But CONST0 transforms to (1,1), which is mixed-parity; CONST1 transforms to (2,0).

Thus the first pilot's observation that all 48 invertible matrices with entries in {-1,0,1} failed at AND was **not a universal AND-only obstruction over Q**. The enlarged grammar includes this escape and separates AND-only feasibility from the joint pin/AND condition. The example has determinant -2 and reduces to a singular matrix in characteristic two. Its division by two cannot be transported into the square-zero characteristic-two tag ring as an invertible basis change.

## Proposition 2: a characteristic-two local invariant

Let K be a **nonzero commutative ring with identity and 2=0**. For a three-leg tensor f, define

\[
B(f)=f_{000}f_{111}+f_{001}f_{110}
     +f_{010}f_{101}+f_{011}f_{100}.
\]

For any three 2-by-2 matrices A,C,D over K, without assuming invertibility,

\[
B((A\otimes C\otimes D)f)
  =\det(A)\det(C)\det(D)B(f). \tag{1}
\]

One direct derivation uses the two first-leg slices U,V. On 2-by-2 arrays put

\[
\langle U,V\rangle=U_{00}V_{11}+U_{01}V_{10}
                      +U_{10}V_{01}+U_{11}V_{00}.
\]

Then B(f)=<U,V>. The pairing is alternating in characteristic two: <U,U>=0, by commutativity and cancellation of each doubled product. Mixing U,V by A multiplies the pairing by det(A). For the other two legs, with J=[[0,1],[1,0]], the identity S^T J S=det(S)J follows by multiplying its four entries, using 2=0. Acting on rows and columns therefore multiplies the pairing by det(C)det(D). Combining the three actions proves (1). This calculation does not divide by any ring element.

Every parity-pure three-leg tensor has B=0: complementation flips parity, so at least one coefficient in every complementary pair is zero. The AND tensor has B=1. If A,C,D are invertible, their determinants are units; the right side of (1) is a unit and hence nonzero in K. Therefore **no independent invertible 2-by-2 leg changes make this fixed AND tensor parity-pure in characteristic two**. The uniform contragredient model is a special case.

In particular this applies to the proposed tag ring

\[
R=\mathbb F_2[\varepsilon_0,\ldots,\varepsilon_{\ell-1}]
 /(\varepsilon_i\varepsilon_j:\text{ all }i,j).
\]

An alternative, weaker uniform-model check reduces an invertible R-matrix by the augmentation eps_j -> 0. It gives an invertible F2 matrix. Reduction commutes with tensor transformation, so a parity-pure R output would reduce to a parity-pure F2 output. All six uniform GL2(F2) cases have mixed-parity AND output. The direct invariant proof above is stronger because it covers independent leg matrices and does not rely on finite-field enumeration to establish the general ring statement.

## Exact ordinary-polynomial expansion certificate

The C++ audit additionally expands (1) in the ordinary polynomial ring

\[
\mathbb F_2[f_0,\ldots,f_7,A_{00},\ldots,A_{11},
 C_{00},\ldots,C_{11},D_{00},\ldots,D_{11}].
\]

There are twenty independent indeterminates. The implementation's variable labels use A/B/C for the three matrices. Monomials store full exponent vectors, and multiplication **adds exponents without the relation x²=x**. Equal monomials cancel only through coefficient addition modulo two. Both sides normalize to the same 32 degree-eight monomials; the difference is the empty polynomial. The output lists both monomial sets in lexicographic order of their full twenty-entry exponent vectors, using repeated variable indices to encode powers. A developer check explicitly requires x² != x, and an intentionally altered right side must produce a nonzero difference.

This is an ordinary symbolic polynomial identity, not interpolation on Boolean variable assignments. Its universal evaluation in commutative characteristic-two rings follows from the ring homomorphism substituting arbitrary elements for the indeterminates. It supplements the written calculation. No Lean build or independent proof-assistant verification is claimed.

## Finite domains and countercontrols

The exact rational grammar is all 625 integer quadruples in [-2,2]^4, with singular matrices removed. It has 496 invertible matrices; scalar multiples are deliberately retained as separate arms. Sixteen make AND alone pass parity and the checked identities. Thirty-two keep both isolated pins parity-pure, and none satisfies the joint condition. Every rational arm retains its exact transformed coefficients and its first mixed-parity tensor. The original 48 invertible coefficient-bound-one arms remain an explicit regression subset.

The binary regression covers all six GL2(F2) matrices uniformly and all 216 independent triples. The single-tag-ring regression covers all 96 invertible matrices over F2[e]/(e²) uniformly. These cases are finite correctness controls, not the basis of a leap to arbitrary coefficients or arbitrary tag dimension.

The XOR parity tensor has B=0 and is parity-pure, so it is a positive control against an argument that would reject every Boolean tensor. Also AND is the **sum of two** parity-pure three-leg signatures: its even and odd support parts. Each part passes the tested three-leg identities. Since B is quadratic, the sum can have B=1. This proves that the local invertible-gauge obstruction must not be misrepresented as an obstruction to sums of signatures. No bound on the growth of such sums under network composition is established here.

## What remains open

These arguments retain one fixed local three-leg AND relation and transform its legs invertibly. They do not rule out a larger block with a different boundary tensor, an alternative EC representation, a target-conditioned functional, a charged characteristic-zero computation followed by a justified integral reduction, noninvertible reductions with separately proved semantics, or sums of signatures. If a grouped block still presents exactly the same three-leg AND tensor, grouping by itself does not change Proposition 2; an escape must identify the changed object or hypothesis.

Neither proposition bounds arbitrary coordinate computations or ECDLP time/memory. Even ordinary efficient linear Boolean computation may use explicit COPY tensors outside this local matchgate class. A missing local basis construction is not a generic security theorem. Any new EC-specific cancellation rule still needs a public constructor, compositional soundness and complete costs.

The previous pilot's exact rational conventions and classical-matchgate context are documented in `harness/classical_ecdlp_pilot/src/circuit.cpp`, its `tests/circuit-notes.md`, and the original IDEA-050/source notes. Those are internal prior-work anchors; no external literature novelty audit was performed for this elementary calculation. The known weighted-perfect-matching parity condition and determinant algebra are not submitted as a new algorithm.
