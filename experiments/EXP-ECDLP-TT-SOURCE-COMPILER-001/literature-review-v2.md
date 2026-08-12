# Literature review v2: exact source-TT compilation

Version 2 corrects the authorship and use of the 2025 ROABP closure paper and
restores the cut-rank lineage to Nisan, Forbes-Shpilka, and standard TT theory.

## Scope

This review asks whether the proposed operation has already been established:
compile the fixed coordinate outputs of a five-source elliptic-curve addition
circuit into exact finite-field TT cores, without enumerating the full input
tensor, with certificate-grade recompression and complete preprocessing cost.

Novelty is `UNVERIFIED`. The sources below justify primitives and identify
nearby numerical work; they do not establish a new cryptanalytic algorithm.

## Closest primary sources

### Tensor-train rank and rounding

I. V. Oseledets, "Tensor-Train Decomposition," SIAM Journal on Scientific
Computing 33(5), 2011, DOI
[`10.1137/090752286`](https://doi.org/10.1137/090752286).

Relevant result: TT bond ranks are governed by ranks of the corresponding
unfolding matrices, and sequential matrix factorizations construct TT cores.
The published algorithms use numerical SVD/QR over real or complex fields.
The present protocol uses only the algebraic rank-factorization identity over
`F_p`; it does not import numerical orthogonality, tolerance, or error bounds.

### Hadamard-product rank inflation

Z. Sun, J. Huang, C. Xiao, and C. Yang, "HaTT: Hadamard avoiding TT
recompression," 2024, [`arXiv:2410.04385`](https://arxiv.org/abs/2410.04385).

Relevant result: explicitly forming the raw TT Hadamard product can cause high
storage and recompression cost, motivating an algorithm that avoids a complete
raw product representation. This is the closest operation-level neighbor to
the streamed local-product proposal.

Boundary: HaTT is a numerical recompression method and its analysis uses the
real/complex linear-algebra setting. It is not an exact finite-field compiler,
does not bind an elliptic-coordinate circuit, and does not provide the
producer/verifier certificate or cryptanalytic accounting required here.

### Randomized Hadamard alternatives

Z. Meng, Y. Khoo, J. Li, and E. M. Stoudenmire, "Recursive Sketched
Interpolation: Efficient Hadamard Products of Tensor Trains," 2026,
[`arXiv:2602.17974`](https://arxiv.org/abs/2602.17974).

Relevant result: randomized sketching and interpolative decomposition can
reduce numerical Hadamard-product scaling in TT rank.

Boundary: sketching, approximate interpolation, sampled slices, and numerical
error are invalid substitutes for exact zero semantics over `F_p`. This work
is a comparator and a source of possible future ideas only; none of its
probabilistic approximation claims enters the experiment.

### Read-once oblivious algebraic branching programs

M. A. Forbes and A. Shpilka, "Quasipolynomial-Time Identity Testing of
Non-commutative and Read-Once Oblivious Algebraic Branching Programs," 2012,
[author manuscript](https://www.cs.tau.ac.il/~shpilka/publications/ForbesShpilka12.pdf).

Relevant result: an ROABP is a product of matrices whose entries are
univariate polynomials in successive variables. After interpolating each
finite registry mode, this is the polynomial analogue of a TT core product.
Set-multilinear ABPs and ROABPs are explicitly related in the paper, and
low-dimensional partial-derivative/evaluation spaces control the model.

J. Armand, P. Dwivedi, M. R. D. Hansen, N. Limaye, S. Srinivasan, and
S. Tavenas, "On Closure Properties of Read-Once Oblivious Algebraic Branching
Programs," 2025,
[`arXiv:2509.10725`](https://arxiv.org/abs/2509.10725).

Relevant result: ROABPs are not closed at polynomial width under several
operations, including superconstant powering. The paper uses the established
Nisan/coefficient-matrix width characterization; it is not the original source
of that theorem. The non-closure result is especially relevant here: a
low-width first norm does not justify assuming that `h^(p-1)` has a low-width
ROABP or TT.

The exact cut-rank lineage is Nisan's coefficient-matrix method for ordered
algebraic branching programs, the ROABP/evaluation-dimension development
described by Forbes-Shpilka, and Oseledets's unfolding-rank TT theorem above.

Boundary: direct-sum addition, product-width multiplication, cut-rank
characterization, and exact linear-algebra minimization are therefore standard
ordered-ABP/TT mechanisms. The present experiment cannot claim novelty for
those primitives. Its research content is the width and fully charged
construction behavior of the bound elliptic-coordinate circuit on finite
registries, including exact certificates and the fixed-curve target split.

### Complete elliptic-curve addition circuit

J. Renes, C. Costello, and L. Batina, "Complete addition formulas for prime
order elliptic curves," EUROCRYPT 2016,
[`IACR ePrint 2015/1060`](https://eprint.iacr.org/2015/1060).

Relevant result: the homogeneous short-Weierstrass addition law used by the
frozen experiment is complete for the stated prime-order setting and has an
explicit arithmetic schedule. The experiment binds the literal local gate
text and does not replace it with an affine exceptional-case oracle.

## Semantic deduplication

The mathematical operation is distinct from the closest repository records:

- `EXP-ECDLP-TT-ZERO-LOCATOR-001` formalized exact final TT ranks and exposed
  intermediate Hadamard construction as an open obstruction; it did not build
  source cores.
- `EXP-ECDLP-TT-NORM-RANK-001` enumerated `B^5` values to validate the first
  norm and source span; it explicitly deferred constructive advice.
- `EXP-ECDLP-FIXED-COMPILER-001` materialized four-term EC sum keys and source
  witnesses. It is a sumset index, not circuit-to-TT compilation.
- Generic Groebner, solver, and parameter changes do not implement the same
  operation and remain controls rather than substitutes.

## Gap statement

No reviewed source located in this pass establishes the exact combined claim:

1. finite-field TT arithmetic with deterministic exact recompression;
2. streamed Hadamard construction without a full raw TT product;
3. a bound complete EC coordinate circuit as the input program;
4. target-independent first-norm source advice;
5. independent exhaustive replay and full offline/online accounting.

This is a gap statement, not a novelty proof. A broader bibliography and
author-level search would be required before any novelty claim.

The sharper algebraic formulation is:

> Compile the frozen RCB arithmetic circuit into a minimal ordered finite-domain
> ABP/TT and determine whether its intermediate widths and exact construction
> work remain useful under fixed-curve preprocessing accounting.

This formulation prevents ordinary ABP closure operations from being mistaken
for the breakthrough. A positive result must come from unexpectedly favorable
coordinate-circuit width, a better exact contraction schedule, or reusable
target-independent structure.

## Handoff: literature boundary

### Claim or task

Identify the nearest exact and numerical TT work and state what may be reused.

### Status

`OBSERVATION`, `NOVELTY-UNVERIFIED`

### Assumptions

- Only primary papers or official publication records support technical
  claims.
- Numerical approximation guarantees do not transfer to exact `F_p` zero
  semantics.

### Evidence so far

- Unfolding-rank TT semantics, ordered-ABP width characterization, and
  sum/product closure are standard.
- Avoiding explicit raw Hadamard products is an active numerical research
  direction.
- ROABP non-closure under powering reinforces the firewall between a compiled
  first norm and the still-open Fermat locator.
- No exact EC-coordinate source compiler was found in this focused pass.

### Failure modes

- The streamed product may reproduce a known exact ordered-ABP contraction
  schedule.
- A literature gap must not be called algorithmic advantage.

### Next concrete action

Treat exact TT/ROABP closure and cut-rank minimization as prior art, and search
specifically for circuit-to-ROABP width reduction on elliptic-coordinate or
rational-map circuits before any novelty label is considered.

### Artifact paths

- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/literature-review-v2.md`
