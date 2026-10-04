# Complete-admissible affine factor base: exact N19 result

A full affine 2-plane survives curve and subgroup admission and retains **99.4377% of the best exact-three coverage** in the frozen 37-orbit pool. This satisfies the preregistered finite geometry prediction. It establishes a concrete candidate for the next SAT test; no SAT, full-IC or rho speedup was measured here.

The curve is K1: y²+xy=x³+x²+1 over F2^19 with polynomial x^19+x^5+x^2+x+1 and prime subgroup order262543. Polynomial-coordinate integers describe

    F = 12009 + span_F2{257473, 353192}
      = {12009, 246568, 347457, 434304}.

Addition here is bitwise XOR. The factor base contains both rational signed points above every x in the19 Frobenius conjugates of F. All four seed x-values survive admission and lie in four different full orbits, so B has76x-values and152signed subgroup points, with four effective Frobenius columns. Its pool indices are[13,24,28,35].

| Fixed four-orbit base | Exactly three target orbits | At most three | Geometry |
|---|---:|---:|---|
| Best complete affine plane |6189/6909 (89.5788%)|6220/6909 (90.0275%)|Complete2plane|
| Unconstrained pool winner[6,9,22,28]|6224/6909 (90.0854%)|6257/6909 (90.5630%)|No required plane|
| Frozen null[0,1,2,3]|5950/6909|5985/6909|No complete plane|

The structured base loses35of6909 target orbits, or0.5066percentagepoints of exact coverage, relative to the unconstrained winner. It exceeds the frozen threshold5913. The search retained1752canonical planes across1726bases;1700bases haveoneplane and26havetwo. All66045four-orbit subsets were scored, so this is the best plane-compatible exact-three score in this fixed pool and under the frozen tie-breaks. It is not an optimum over arbitrary factor bases or all affine planes in the field.

The earlier N7 construction admitted only two of eight seed x-values and collapsed to an affine line. This N19 candidate retains a genuine plane, resolving that structural defect. Neither the improved structure nor high coverage proves useful SAT propagation.

## Evidence and independent review

EXP-KIC-3df18c / RUN-KIC-234d11 is frozen at4afb14f3757a342172711ba4165ba593b97bfc39 with74bound paths. The approved protocol and additive baseline amendment preceded every experiment process. The amendment corrected a historical interpretation before execution: the old global record optimized at-most-three coverage; its chosen base alone had a separately reported exact-three score. The new full enumeration now finds that the same base also uniquely maximizes exact-three coverage. That value was measured, not imposed as a global exact-three control.

One native-control process, one scientific geometry/frontier process and one independent coordinate checker completed validly. Native controls include4457fieldproducts,4096group-pair samples,20480batchedexception cases, field irreducibility and full orbit admission. The full target partition has6909disjoint signed Frobenius orbits covering all262542nonidentity subgroup points.

A source-aware independent reviewer verified all snapshot bindings, the complete plane enumeration, all66045frontier scores from the frozen support cache, the959-bin historical at-most-three histogram, selection ordering, seven directly regenerated support rows and570unanchored symmetry controls,20727per-target verdicts and18363recorded triple witnesses. A separate permanently blind reviewer rebuilt the geometry and the selected/prior/null coverage with independent coordinate MITM and independently anchored supports. The blind reviewer opened no producer or sibling output. Both owned joints hold; the canonical review-independence checker exits0 withPASS. Reviewer model metadata includes an older adapter probe and is not presented as a fresh serving-model probe.

The entire support-cache generation was not independently regenerated row-by-row. The complete score unions, independent selected/prior/null coverage, direct sampled support rows, source audit and full historical histogram provide the stated finite evidence. This limit remains visible.

## Actual cost scope

| Phase | Owned compute-child wall | Whole supervisor wall |
|---|---:|---:|
| Native correctness controls|0.7612s|0.9879s|
| Geometry, support cache, full frontier|5.8080s|7.9472s|
| Independent checker|39.7614s|41.9861s|

The three supervisor intervals sum to50.9211s and include source/input checks, child execution, result promotion, hashes and raw archives. Compilation and independent reviewer work are separate. Scientific child peakRSS is70,696,960bytes; checker peakRSS is317,980,672bytes. Child and supervisor CPU/RSS scopes overlap and are not added together. These are costs of discovering and checking per-curve advice, not cold target-decomposition or fullIC timings.

The first control command named symbolicHEAD. The immediate post-control readback, before the next commit, binds its actual commit988bcf406b04ae82769803a09e14ad20c80309fa and exact source/admission/binary bytes. Original argv, receipt and manifest remain unchanged. An additive manifest_execution_bound.yaml records the immutable binding. Science and checker admissions used full commit hashes. The source-aware reviewer checked this correction; it does not claim the original argument was already an immutable hash. Host executable/compiler/Python custody is recorded, with no portable environment claim.

## Next discriminating test

Compare a strong explicit one-hot encoding of the same76x-values with two complete-affine encodings: a factorized one-hot Frobenius selector sharing the two seed coordinates, and a binary cyclic-shift circuit. Give all arms identical constant-folded S3 arithmetic and native XOR handling, and retain a native coordinate MITM baseline. Freeze targets, ordering, caps and censor handling before solver output. A stratified SAT/UNSAT pilot measures encoding behavior; its weights do not estimate uniform relation-generation cost.

The prospective sparse cofactor-projection note is a separate unreviewed algebraic lead. It explicitly retains the automorphism equivalence to ordinary cofactor clearing, so it makes no coverage improvement claim. Neither it nor the SAT design notes changes the completed N19 geometry protocol.

All experiment and review citations have internal provenance. The Coordinator disposition is DEC-20260921-42cecf; no existing hypothesis or goal file is rewritten by this report.
