# Independent normalization/domain/order review

Task: `TASK-20261026-391e68`  
Owned joint: `normalization-domain-order`  
Published implementation: `isogeny-labs/crypto@1d47988261c4d13f7a8549d70f53571163246c77` (PR 2642)  
Verdict on owned joint: **holds, bounded to published-source semantics**

## Finding

No source-level counterexample was found for the assigned joint. The pinned native source implements the independently sealed affine object, coordinate map, initial convex integral domain, weighted order, multiplicity normalization, and constant-pivot construction. This is a bounded interface-readiness finding. It is not an executed-equivalence finding and says nothing about numerical reach, reduction, extraction, group relations, DLP success, index-calculus gain, or global optimality.

The blind derivation was sealed before deliberate implementation access:

- `blind-derivation.md` SHA-256: `bc4175caa9751bb72e02051c446b040443eaa7033d53a66c3c70ba9a4ecbcf7f`
- `blind-seal.json` SHA-256: `fda03f96e31d85f50c934689c1309f0f57340ad7923019f984e23b9959f4fb8a`
- sealed at: `2026-10-26T19:19:50Z`
- producer/native access began only after the seal hash and time were sent to the Coordinator.

## Comparison to the sealed object

### Exact relations and six/seven-coordinate map

The hand-derived expansions in `blind-derivation.md` have child supports

\[
\{(i,j,k):0\le i,j,k\le2,\ i+j+k\le4\}
\]

and target support \(\{(i,j):0\le i,j\le2\}\); every displayed coefficient is nonzero. The native `S3` is term-for-term the supplied formula, and `cell` uses the exact centers `(11,13,17,19,23,29)` and target `5` (`src/model.hpp`, lines 17--49). This establishes equality by direct algebraic substitution, without executing a polynomial helper.

The lost-leading-coordinate attack fails against the implementation. `cell` constructs each deviation as variable `i+1` in an arity-7 polynomial, reserves coordinate 0 for the formal modulus `p`, and copies every active exponent into offset `i+1` (`model.hpp`, lines 43--78). For the joint arm the names are exactly

`(p,z1,z2,z3,z4,h1,h2)`.

`initial_vertices` additionally requires exponent 0 in the `p` coordinate before dilation (`model.hpp`, lines 93--104). Thus a six-tuple is never directly zipped against seven generators, and `h2` is not dropped or shifted.

The leading modulus contribution is also retained after monomial comparison. `strip` clears only exponent 0, `lt_no_p` returns the stripped unknown-variable monomial together with its `p`-power coefficient, and `coeff_no_p` accumulates the complete polynomial in `p` for a fixed stripped monomial (`src/exact.hpp`, lines 221--251). This agrees with Ryan's `monom_no_N`, `lt_no_N`, and `coeff_no_N` split.

### Weighted order

For the full joint, the native order weights are

- `r=2`: `(1000,50,50,50,50,100,100)`;
- `r=4`: `(1000,50,50,50,50,200,200)`.

These are exactly the integer-scaled weights from modulus weight 1 and bound guess `(1,1,1,1,r,r)/20` (`model.hpp`, lines 66--72). `Order::cmp` first compares the exact weighted sum and then the exponent vectors lexicographically (`exact.hpp`, lines 62--75). The Singular backend declares the same variables and `Wp(weights)` order. Sage 10.9 maps `wdeglex` to this `Wp` convention; no source-order mismatch was found.

The initial domain is sorted again by this order before FIFO closure (`exact.hpp`, line 331), so replacing Sage's integral-point iteration order by deterministic coordinate enumeration does not change the effective `M` order.

### Convex integral domain versus Minkowski substitution

The native initial vertices are exactly zero plus `mu` times every nonzero-support exponent (`model.hpp`, lines 93--104). The hull path passes those seven-coordinate points to cddlib using exact rational entries, receives the exact H-representation, enumerates the coordinate bounding box, and retains precisely the integer points satisfying every equality/inequality (`src/polytope.hpp`, lines 43--109). The pipeline passes those points, not raw supports or a bounding box, to the optimal closure (`src/pipeline.hpp`, lines 146--152).

Thus the initial domain is

\[
\{0\}\times\bigl((\mu\operatorname{conv}(\{0\}\cup E))\cap\mathbb Z_{\ge0}^6\bigr),
\]

as sealed. It does not replace the initial convex-integer domain by a discrete Minkowski sum. The later `convolution` stage uses pairwise sums of the already constructed augmented point set, exactly as Ryan's `AugPolyhedron.__add__` does; that later source behavior is distinct from the initial-domain construction attacked here.

### Multiplicity normalization

The source keeps three operations separate:

1. the raw bound guess sets the order weights;
2. `initial_vertices` dilates domain exponents by `mu` once;
3. `limit` divides the formal-modulus statistic `C` and every bound-ray weight by `mu` once (`exact.hpp`, lines 466--475).

This matches Ryan's `get_delta_star`, where `S_1` has a root modulo `p^k_pre`, so both `log_(p^mu) X_i` and `log_(p^mu) p` acquire one factor `1/mu`. I found no missing or double multiplicity divisor.

### Constant-pivot intersection

The native outside-domain intersection reverses rows and columns, performs the constant-pivot reduction, reverses back, and keeps exactly rows whose columns outside `M` vanish (`exact.hpp`, lines 368--391). Its reducer:

- selects the first nonzero entry that is constant in the polynomial variables;
- inverts only its rational scalar;
- rescales the pivot row from the pivot column;
- eliminates the pivot column from every other row using polynomial row addition;
- never inverts the formal modulus polynomial.

This is a literal source match to Sage 10.9 `Matrix_mpolynomial_dense._echelonize_row_reduction` (official Sage tag `10.9`, lines 309--422), which states that division is limited to constants and uses the base coefficient field only. The fraction-field attack therefore fails: constants are inverted in `QQ`, while `p` remains a nonunit polynomial variable.

## Explicit unresolved obligation

`UNRESOLVED-NDO-1`: no published artifact demonstrates the full fixed joint cell's exact domain list and constant-pivot intersection at commit `1d47988261c4d13f7a8549d70f53571163246c77`. The producer compatibility map says the full domain was not invoked and full intersection equivalence remains unverified. This review was expressly limited to source/hand derivation and performed zero scientific calls, bound calls, reductions, extractions, or parameter searches. Therefore the joint holds as a static source construction, while executed parity of the full cell remains unestablished. A future authorized conformance check would need to bind the full-domain point list and pre/post-intersection matrices to this pinned commit and compare them with an independent reference construction; it would not certify a numerical bound or scientific result.

The full Ryan ePrint source was retrieved and read before this finding. Lemma 7 remains conditional on Heuristics 1 and 2, sufficiently large `p`, proportional specialization values, and excludes final root recovery. Nothing in this review promotes those assumptions or supplies a numerical theorem result.

## Provenance and scope

The owner manifest identifies 77 published source blobs at the pinned commit. The seven source files material to this joint were independently streamed from that commit and their SHA-256 values matched the manifest: `model.hpp`, `exact.hpp`, `polytope.hpp`, `cdd_ipc.hpp`, `cdd_helper.cpp`, `backend.hpp`, and `pipeline.hpp`. The compatibility map's eight cited cuso file digests likewise matched `keeganryan/cuso@fb2747d2105a8e48499bf10a3a717cf80c14d079`.

Actual invocation provenance: reviewer; `review-adversarial`; explicitly configured `openai` binding; native `gpt-5.6-sol`; `xhigh`; fresh `fork:none`; no fallback; no degradation; no new API catalog probe; the repository binding's `2026-08-02` probe date is historical and is not presented as a current serving-session attestation.

## Procedure deviation

Before the seal, an initial filename-only `rg --files` search used an overly broad `*contract*` glob and enumerated many repository path names, including the already named prohibited `native-backend-contract.md` path. No content from that file, any queue or other task card, prior design/bound artifact, producer artifact, owner implementation, or sibling report was opened. The deviation exposed filenames only and did not change the derivation.

```yaml
review_attestation:
  task_id: TASK-20261026-391e68
  joints_owned:
    - normalization-domain-order
  sources_read: review-attestation.yaml
  read_sibling_reports: false
  blind_from_respected: true
  verdict: holds
```
