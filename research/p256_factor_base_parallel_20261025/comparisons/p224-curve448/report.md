# P-224 and Curve448: exact finite-domain observations

TASK-20261025-8c305c; 25 October 2026. These are local implementation observations on the actual published prime fields. They do not change a scientific status. Independent implementations agree on every complete domain and point decomposition set below.

## Measured observations

M denotes the number of accepted canonical points (x,min(y,p-y)); the signed base contains both signs. Every domain has S distinct roots. Zero-y exclusions were zero in all four cases.

| Curve | S | Canonical M | Signed points | Non-lifts | Cofactor rejections |
|---|---:|---:|---:|---:|---:|
| P-224 | 16 | 8 | 16 | 8 | 0 |
| P-224 | 32 | 18 | 36 | 14 | 0 |
| Curve448 | 16 | 2 | 4 | 6 | 8 |
| Curve448 | 32 | 4 | 8 | 14 | 14 |

All 12 control sets were completely enumerated. Entries below count unordered signed-point multisets of size three, allowing repetition. The last column counts solutions with repeated x coordinates across the controls.

| Curve | S | Constructed repeated positive | Base cancellation | Unrelated public generator | Repeated-x solutions |
|---|---:|---:|---:|---:|---:|
| P-224 | 16 | 1 | 8 | 0 | 9 |
| P-224 | 32 | 1 | 18 | 0 | 19 |
| Curve448 | 16 | 1 | 2 | 0 | 3 |
| Curve448 | 32 | 1 | 4 | 0 | 5 |

Each constructed target is 2P0+P1. Each cancellation target is the last canonical base point Q; all M solutions P+(-P)+Q are retained, including equal-coordinate cases. The unrelated controls use a public standard generator x coordinate, lifted to its canonical sign. Those zero counts concern these four targets and bases only. No secret scalar is supplied to the search.

## Exact domains, curve identities and subgroup checks

P-224 has p=2^224-2^96+1, a=-3, the input b and prime order r, cofactor 1. Its split multiplicative ambient order p-1 has 2-adicity 96. Curve448 has p=2^448-2^224-1 and Montgomery equation v^2=u^3+156326u^2+u. The invertible translation x=u+156326/3, y=v gives the exact short Weierstrass coefficients in each domain certificate. Its norm-one torus has order p+1 with 2-adicity 224; the elliptic curve has cofactor 4. The torus implementation uses F_(p^2)=F_p[i], i^2=-1; p=3 mod4 makes this extension irreducible.

For each S, zeta has exact order S. The deterministically chosen alpha satisfies c=alpha^S+alpha^(-S) != +/-2. Domain roots are x_k=alpha*zeta^k+(alpha*zeta^k)^(-1). In the torus this is the field trace. D_1(X)=X and D_(2n)=D_n(X)^2-2 give H(X)=D_S(X)-c. Every certificate retains alpha, zeta, c, all S roots, every linear factor with multiplicity, and all H coefficients. Explicit polynomial multiplication equals H, all FLINT roots equal the constructed roots, and gcd(H,H')=1. This proves the complete factorization over the actual field for each specified domain.

Both p and r pass FLINT's proven primality API. Nonsingularity and the nonidentity public generator relation [r]G=O are checked. The Hasse interval contains precisely the multiple h*r, proving the full elliptic curve order from that subgroup witness. The explicit integer bounds are in [group-orders.json](certificates/group-orders.json). Every candidate y is checked; non-lifts are retained. Every nonzero lift undergoes the exact [r]P=O test. Curve448's rejected residual points are retained, and cofactor multiplication is never substituted for membership. No y=0 occurred.

Each domain certificate contains the full metadata identity preimage, EC1 alias and full curve UID. These identify the exact short Weierstrass representation and chosen canonical generator sign. They are metadata identities, not claims of registry registration or a hash proof of isomorphism. Curve448's displayed Montgomery-to-short translation supplies its mathematical relationship.

## Complete decomposition controls and independence

The producer evaluates the supplied symmetric S4 polynomial on every unordered x triple in the entire domain, including non-lifts and cofactor exclusions. This checks 816 x multisets at S=16 and 5984 at S=32 per target. It retains every S4-zero candidate, the exclusion reasons, all accepted sign assignments and the full signed solution set. No division by differences of x coordinates is used. Repeated coordinates are included throughout.

The producer separately enumerates all signed-point triples with Jacobian sums. The independent checker imports no producer arithmetic: it uses affine secant/tangent sums and a left-to-right scalar ladder, computes S4 zeros from the resultant of the two original quadratic f3 polynomials, and independently multiplies polynomial coefficients and factors the full H. It scans every x multiset and every signed-point multiset. Both complete signed sets and complete S4-zero candidate sets agree for all twelve controls. The signed multiset counts per target are 816/8436 for P-224 and 20/120 for Curve448 at S=16/32 respectively.

This is implementation independence within the same executor session. It is not an independent scientific review. Producer certificates preserve their original pending-check field; [independent-result.json](independent-result.json) records the later successful replay without rewriting them.

## Artifacts, custody and scope

The complete canonical M values, exact full domain factorizations, rejected lifts and cofactor residuals are in the four *-domain.json files under [certificates](certificates). Every target's complete S4 and signed solutions has its own certificate. [result.json](result.json) indexes counts and scope; [producer-result.json](producer-result.json) records the original observation, source/input hashes, environment, base commit and dirty-tree state. [code/producer.py](code/producer.py), [code/independent.py](code/independent.py), [code/finalize.py](code/finalize.py), [commands.txt](commands.txt), stdout/stderr logs and [manifest-final.json](manifest-final.json) support replay. The final manifest supersedes the preliminary manifest, which was generated before its own stdout log closed; the original is retained. Each retained file is below 64 KiB before the coordinator's PDF rendering.

The baseline parameter and S4 inputs are internal supplied artifacts. Their use and code inspection provenance are listed in result.json. No source file from /workspace/dickson-inspection is imported; the local reference was read and the arithmetic paths were written self-contained here. Standard references are NIST SP 800-186 section3.2.1 and RFC7748 section4 (bibliographic pointers recalled from the internal source list; not independently fetched in this task).

Normal committed-and-pushed handoff compliance is **unmet**. Execution uses the explicitly recorded [local-custody exception](../../reviews/local-custody-exception.json); the new task card is local. This does not discharge an archive, review, promotion or publication gate. No upload, Git mutation or PR operation was performed. Explicit public-disclosure approval remains pending. The coordinator handles local snapshots and PDF rendering.

S=16 and32 were the fixed domain sizes. Both curves had nonempty accepted bases, so the conditional S=64 extension did not run. There were four completed cases, twelve completed controls, zero failed executions and zero timed-out executions. Runtime fields in the raw records describe these executions only and are not a performance comparison. No statistical uncertainty is attached to exact complete enumeration. No uniform-target yield, field-size scaling, asymptotic or attack-cost conclusion follows from these finite cases.

The quantitative [diagram.svg](diagram.svg) shows recorded coordinate counts for these four domains. Its editable source is code/finalize.py. Existing canonical scientific graphs were inspected only by scope: this local finite-domain record changes no canonical relationship, and no shared graph was edited. The next reviewable step is a separate reviewer replaying these certificates, followed by any specifically authorized expansion of domain sizes; the present observations already cover their full declared finite scope.
