# Independent draft mathematical check: Koblitz Jacobian-transfer dimension bounds

Date: 2026-09-30. Reviewed repository: `aburan28/crypto-autoresearcher`.
Reviewed branch: `docs/jacobian-transfer-assessment-20260930`.
Reviewed immutable commit: `6ee050827103049fb7bec95e61e315d95e7ccbbe`.
Reviewed theory path: `notes/jacobian-transfer-20260930/theory.md`.

This is an independent agent-session mathematical check of the specified draft, with requested policy `review-adversarial` and requested reasoning effort `xhigh`. It is not a harness-certified review or a claim-changing review round. No archived `TASK-*` handoff, predeclared `review_plan`, archival owner, or adapter/model-verification receipt was established before this session. Consequently this document does not attest compliance with those procedural requirements, does not certify a resolved model identifier, and must not be used by itself as a canonical promotion or closure receipt. The reviewer did not originate the draft and did not read another reviewer's report. The hyperelliptic refinement below was proposed by the parent/root agent during this review and is explicitly not represented as a blinded independent discovery.

Scope: mathematical validity, field of definition, subgroup location, homomorphism direction, and interpretation. No attack construction, key recovery, transfer implementation, DLP run, performance benchmark, canonical record edit, or research-state transition was performed.

## Assessment

The main necessity statement is mathematically sound for the two stated Koblitz families, the four stated prime extension degrees, and homomorphisms of abelian varieties **defined over F_2**. The draft needs clearer hypotheses for subgroup preservation, an explicit reverse-direction proof, and a quotient argument for isogenous replacement curves. These are proof and scope corrections; they do not invalidate the stated dimension obstruction.

For a smooth projective geometrically connected curve C/F_2 whose Jacobian participates in such a map, the reviewed necessary bounds are:

| n | General Jacobian, mu=-1 | General Jacobian, mu=+1 | Hyperelliptic Jacobian, either sign |
| --- | --- | --- | --- |
| 31 | g >= 30 | g >= 31 | g >= 31 |
| 53 | g >= 52 | g >= 53 | g >= 53 |
| 83 | g >= 82 | g >= 83 | g >= 83 |
| 131 | g >= 130 | g >= 131 | g >= 131 |

The last column uses the root-origin refinement reviewed below. All entries are necessary conditions, not existence results or estimates of DLP difficulty.

## Simplicity and Frobenius computation

Theorem 4 and Corollary 21 of Diem--Naumann apply: E is ordinary, its rational endomorphism field is Q(sqrt(-7)), its endomorphisms are defined over the finite base field, and the extension is cyclic. Their cyclic component criterion says the component for d is simple when that field has trivial intersection with Q(zeta_d); for prime n the non-base component has dimension n-1. For n=31,83,131 the unique quadratic cyclotomic subfield is Q(sqrt(-n)); for n=53 it is Q(sqrt(53)). None equals Q(sqrt(-7)). The n=7 exception and n=51 composite decomposition are consistent with their Corollary 21. [P1, retrieved, Theorem 4; Corollary 21; Section 3.5.]

The identification with the actual trace kernel is valid. After extending scalars to F_(2^n), W becomes E^n and trace becomes addition. Its kernel is isomorphic to E^(n-1), hence connected and smooth of dimension n-1. The diagonal embedding i:E -> W satisfies Tr composed with i = [n]. The addition map E x A -> W is an isogeny, so P_W=P_E P_A.

The proposed polynomials are correct:

    P_E(T)=T^2-mu*T+2,
    P_W(T)=T^(2n)-s_n*T^n+2^n,
    P_A(T)=P_W(T)/P_E(T),
    s_0=2, s_1=mu, s_j=mu*s_(j-1)-2*s_(j-2).

For prime n the listed roots alpha*zeta_n^i and beta*zeta_n^i, 1<=i<n, are correct. The alternative irreducibility proof is also valid: alpha/beta + beta/alpha = -3/2, so alpha/beta cannot be a root of unity, since a rational algebraic integer must be integral. Thus alpha^n is nonrational and generates Q(sqrt(-7)). For lambda=alpha*zeta_n, lambda^n=alpha^n implies Q(lambda) contains that quadratic field and then zeta_n. Trivial intersection gives degree 2(n-1), exactly the degree of P_A. A proper positive-dimensional F_2 abelian subvariety would yield a proper rational Frobenius-polynomial factor. Therefore A is F_2-simple.

This is **F_2-simplicity**, not absolute simplicity: A becomes E^(n-1) after the stated field extension. The lower bound must retain the field-of-definition hypothesis throughout.

## Forward and reverse maps

For G of odd prime order ell in E(F_(2^n))=W(F_2), trace maps G into E(F_2), whose order is 3-mu, namely 2 or 4. The image must be trivial, so G is contained in A(F_2). This step needs no rational-point surjectivity assertion.

For f:W -> J_C defined over F_2, state preservation precisely as `f|_G != 0`, equivalently injectivity on this prime-order group. Then f|_A is nonzero. The reduced identity component of its kernel is an F_2 abelian subvariety of the simple A, and cannot be A. It therefore has dimension zero, and the image has dimension n-1. Consequently g=dim(J_C)>=n-1. In characteristic 2 the scheme-theoretic kernel can be nonreduced; the dimension conclusion remains valid.

For h:J_C -> W, let B be its abelian-variety image. A clean proof is:

1. Require at least a nonzero point of G to lie in B(F_2). The stronger condition G contained in h(J_C(F_2)) is also sufficient.
2. The rational Tate-module exact sequence for B contained in W gives P_B dividing P_W=P_E P_A.
3. If dim(B)<n-1, irreducibility and degrees imply P_B=1 or P_B=P_E. Thus B is zero, or is an elliptic curve F_2-isogenous to E.
4. Accordingly #B(F_2) is 1, 2, or 4 and cannot contain an odd-prime-order point. This contradicts step 1.

Hence dim(B)>=n-1 and g>=n-1. If g=n-1 then P_B=P_A and h:J_C -> B is an isogeny, so J_C is F_2-isogenous to A. Thus the exact-dimension point-count obstruction applies in the reverse direction as well.

Replace the draft's informal sentence that the reverse image must contain the large component with this proof. It avoids treating the rational-point group as a direct product of isogeny factors.

Geometric surjectivity does **not** imply surjectivity on rational points. For example, multiplication by ell is an isogeny but is not surjective on a finite rational-point group containing a point of order ell. More generally, equality of Weil polynomials implies equality of point counts, not equality of group structures or preservation of a chosen subgroup. [P2, retrieved, Definition 7.1.2; Theorem 7.1.4.] Even a nonzero map on A may kill G. The genus bound is a necessary condition for a preserving map; it is not evidence that such a preserving map exists.

## Isogenous replacement over F_(2^n)

Let E'/F_(2^n) be isogenous over that field to the base-changed E, and W'=Res(E'). Restriction of scalars carries the isogeny to an F_2-isogeny W -> W', so P_W'=P_W. [P1, retrieved, Section 1.3.] This remains valid when E' itself does not descend to F_2.

For the forward-map argument, choose the dimension-(n-1) simple isotypic abelian subvariety A' of W'. The quotient Q=W'/A' has P_Q=P_E, hence #Q(F_2)=2 or 4. Every odd-prime subgroup of W'(F_2) maps trivially to Q(F_2) and therefore lies in A'(F_2). The same simplicity argument gives the forward bound; the Frobenius-factor argument gives the reverse bound. No rational-point splitting of W' is assumed.

This quotient formulation should replace any suggestion that a canonical trace W' -> E' over F_2 exists when E' does not descend. The chosen isogeny may kill a subgroup if its degree contains ell; invariance of the isogeny class does not prove a usable subgroup map. Concealing the isogeny does not change these public invariants, but the derivation supplies neither a secrecy theorem nor an obstruction for maps over another field.

## Exact dimension and root-origin hyperelliptic refinement

For n>2, the first two power traces of W are zero. The corresponding traces for A are -mu and -s_2; here s_2=mu^2-4=-3. If J_C is isogenous to A, then

    #C(F_2)=3+mu,
    #C(F_4)=5+s_2=2.

For mu=+1 the required counts are 4 and 2, contradicting C(F_2) contained in C(F_4). Thus exact genus n-1 is impossible for a general smooth curve in this sign case. For mu=-1 both counts are 2, so this inclusion test alone supplies no exclusion or existence claim. Additional factors in a larger Jacobian alter its traces and require a separate assessment.

The root agent proposed the following refinement during this session, and the reviewer checked it:

For a geometrically hyperelliptic smooth projective curve C/F_2 of genus at least 2, the unique geometric hyperelliptic involution is Galois-invariant and therefore descends to F_2. Its quotient is a smooth genus-zero F_2 curve, hence P^1/F_2. This standard double-cover framework is stated in Howe's ANTS XVI slides, printed slide 2 (PDF page 2). [P3, retrieved.] The conic characterization and the projective-line criterion are also in Stacks, Lemma 53.10.3 and Proposition 53.10.4. [P4, retrieved.] Over F_2 a conic has a rational point; the elementary finite check recorded below verifies this for all homogeneous quadratic forms.

Pull back each of the three points of P^1(F_2). Each fiber is an effective divisor of degree 2, whose support consists of closed points of degree 1 or 2. Each fiber therefore contributes at least one F_4-rational point; distinct fibers have disjoint support. Thus #C(F_4)>=3. This contradicts the required count 2 for **both signs** if J_C is isogenous to A. Exact genus n-1 is consequently impossible for hyperelliptic destinations, including mu=-1.

Wild ramification in characteristic 2 changes fiber multiplicities, not this support argument. A hypothetical purely inseparable degree-2 map to P^1 also supplies no exception: purely inseparable maps from smooth proper geometrically connected curves preserve genus, by Stacks Lemma 53.13.5, and hence cannot map a positive-genus C to P^1. [P5, retrieved.] This refinement excludes the exact-dimension hyperelliptic case only; it does not exclude general mu=-1 Jacobians or larger hyperelliptic destinations.

## What the review does not establish

Neither an arbitrary high-genus Jacobian existence theorem nor the presence of A as an isogeny factor proves an easier DLP, a hidden advantage, efficient construction, efficient subgroup-preserving map evaluation, rational-point lifting, or a total-cost improvement. Existence and useful computation are distinct claims. Likewise high genus alone proves no lower bound on DLP cost. Explicit isogenies are not supplied by equality of Weil polynomials. [P2, retrieved, Remark 7.1.5.] No high-genus algorithm hypotheses or performance claims were verified in this review; the root agent retained that separate source-checking task.

The conclusions also do not cover arbitrary finite-group homomorphisms, F_(2^n)-defined maps without the stated F_2 descent, nonstandard binary elliptic families, composite extension degrees without component identification, or an exact ECC2K-130 curve UID/subgroup. No breakthrough or research-goal closure is asserted.

## Checks actually performed

- Retrieved the root AGENTS.md at the reviewed commit using the GitHub connector and read the relevant model-policy, provenance, independence, review-plan, archival, and authority rules. Directory reads found no additional AGENTS.md in `notes/` or `notes/jacobian-transfer-20260930/` at that commit.
- Retrieved the committed theory, diagnostic code, and arithmetic output. Independently computed Git blob SHA-1 values for all three local copies; each matched the connector's committed blob SHA below.
- Ran `python3 theory-work/check_tracezero.py > /tmp/independent-tracezero.json`. All assertions passed. Parsed both JSON documents and confirmed exact equality with `theory-work/arithmetic.json`, covering both signs at n=7,31,51,53,83,131 (12 cases). This rerun checks the diagnostic assertions, not an independent formal proof of the theorem.
- Independently enumerated the two Koblitz equations over F_2 and F_4, using F_4=F_2[u]/(u^2+u+1). Obtained #E(F_2)=4,2 for a=0,1 respectively and #E(F_4)=8 for both, confirming the sign convention and s_2=-3.
- Independently enumerated all 64 homogeneous quadratic forms in three variables over F_2 and all seven projective F_2 points. Every form had a nonzero zero. Also enumerated all four monic quadratic polynomials over F_2: all had an F_4 root, including the nonreduced fibers.
- Checked the mathematical field-degree and map-image arguments above directly. Did not factor the large polynomials computationally, construct a Jacobian or an isogeny, or execute any discrete logarithm.

| Committed artifact | Git blob SHA-1 |
| --- | --- |
| theory.md | 55faa1d04e783352fc24c589e7f916fdbda1e54d |
| check_tracezero.py | daed3bcb2982245314f14e57a514dca4b8baac94 |
| arithmetic.json | 07e7eca60ca47c35a6a0707dce0fb25c92257072 |

## Sources read and provenance

All supporting external sources below were retrieved and read in this session; no recalled-only reference is used as support. Some initial direct opens failed, but the subsequently retrieved source content was read. The inaccessible Equations of Hyperelliptic Curves PDF and Milne PDF are not supporting citations.

- R1: Repository contract, AGENTS.md, provenance `retrieved` through the GitHub connector: https://github.com/aburan28/crypto-autoresearcher/blob/6ee050827103049fb7bec95e61e315d95e7ccbbe/AGENTS.md . Read relevant policy and review/archival sections; no compliance attestation inferred.
- R2: Reviewed draft and associated diagnostics, provenance `retrieved` through the GitHub connector: https://github.com/aburan28/crypto-autoresearcher/tree/6ee050827103049fb7bec95e61e315d95e7ccbbe/notes/jacobian-transfer-20260930 . Source identities confirmed by the blob hashes above.
- P1: Claus Diem and Niko Naumann, *On the Structure of Weil Restrictions of Abelian Varieties*, arXiv:math/0504359v2, provenance `retrieved`: https://arxiv.org/html/math/0504359v2 . Read Section 1.3, the Frobenius/restriction framework, Section 3.5, Theorem 4 and Corollary 21. The latter exact theorem labels are the principal published structural input.
- P2: Kiran S. Kedlaya, *Weil cohomology in practice*, Chapter 7, *Inverse problems for zeta functions*, provenance `retrieved`: https://kskedlaya.org/weil-cohom/chapter-7.html . Read Definition 7.1.2, Theorems 7.1.3--7.1.4, Remark 7.1.5, and the curve point-count constraints in Remark 7.1.12. This is an author-hosted exposition of Tate's results, not a claim to have read Tate's original paper.
- P3: Everett W. Howe, *Enumerating hyperelliptic curves over finite fields in quasilinear time*, ANTS XVI, 15--19 July 2024, printed slide 2/PDF page 2, provenance `retrieved`: https://antsmath.org/ANTSXVI/slides/Howe.pdf . Read the hyperelliptic involution and finite-field genus-zero quotient statements. No enumeration algorithm claim is used.
- P4: The Stacks Project, Section 53.10, Lemma 53.10.3 and Proposition 53.10.4, provenance `retrieved`: https://stacks.math.columbia.edu/tag/0C6L . Read the conic and projective-line characterizations.
- P5: The Stacks Project, Lemma 53.13.5, Tag 0CD0, provenance `retrieved`: https://stacks.math.columbia.edu/tag/0CD0 . Read the smoothness and genus preservation statement for purely inseparable maps; also read its surrounding Section 53.13 search-returned context.

This draft records a limited mathematical assessment and specific correction needs. Official hypothesis and goal statuses remain unchanged.
