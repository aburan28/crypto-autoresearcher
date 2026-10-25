# Proposed atlas row diffs (for the Coordinator; nothing here was applied)

Each diff names the record that would decide it. A diff that changes an
obstruction kind to `proof` lands only after the Lean target is
`machine_verified` through the repository gate (blocked on this host, see
`problems/formal-lean-external-volume-eintr.md`) and a separate session's
sheriff review signs off (then, and only then, kind `theorem`).

## 1. `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-generic-oracle-arity-cost-floor.yaml`

```diff
 obstruction:
-  kind: cost_model
+  kind: proof            # conditional on H1-H4; theorem after sheriff review
   statement: >-
-    For oracles of class ENUM, MITM and MITM_CAPPED on binary curves of prime degree n, the
-    replicated v2 cost model has zero in-domain sub-rho cells (EV-SEMBIN-b6d042); ...
+    Within the two-term cost model (H1 yield B^m/(m! r), H2 B relations, H3 sparse linear
+    algebra B^2, H4 oracle cost B^k per attempt), the index-calculus cost exponent is at
+    least 2/(m+1-k) for k <= 2 and k/(m-1) for 2 <= k <= m-1 (all-decompositions oracle;
+    one-decomposition oracles are never cheaper), so every oracle of order k >= (m-1)/2,
+    which includes exhaustive (k = m-1) and meet-in-the-middle (k = ceil(m/2)) oracles,
+    stays at or above the generic 1/2 at every arity and every group order
+    (formal/CryptoResearch/IC/ArityOracleThreshold.lean, TASK-20261024-9fbb0f).
+    Measured: for oracles of class ENUM, MITM and MITM_CAPPED on binary curves of prime
+    degree n, the replicated v2 cost model has zero in-domain sub-rho cells
+    (EV-SEMBIN-b6d042); ... [rest unchanged]
+    Scope: oracles whose per-attempt cost is a power B^k of the factor-base size with
+    k >= (m-1)/2; the FREE control (k = 0) does have sub-generic cells for m >= 4 in the
+    model, so the obstruction is the oracle order, not IC.
   revisit_when: >-
-    An oracle that reads coordinates with per-query cost polynomial in n at fixed degree (see
-    LEAD-ICE-descent-closure-degree-at-scale) is measured, or a non-generic yield exceeds
-    C(B+m-1,m)/N on average.
+    An implemented oracle has a fitted enumeration order k < (m-1)/2 (all-decompositions)
+    or k < m/2 - 1 (one-decomposition) with its 95% interval below the line over >= 6 sizes
+    (spec: docs/reports/ecdlp-lead-discovery-20261024/specs/EXP-SPEC-oracle-order-census.md),
+    or a non-generic yield exceeds C(B+m-1,m)/N on average (H1 fails).
 evidence:
+- repo: crypto-autoresearcher
+  path: formal/CryptoResearch/IC/ArityOracleThreshold.lean
+  note: closed-form threshold, both oracle semantics; compiles under lean, gate pending
 ledger_refs:
+- IDEA-20261024-a2b05d
+- RQ-ECDLP-361f3a
 forecloses:
+- oracle enumeration order below the threshold line
+- all-decompositions versus one-decomposition oracle semantics
 last_reviewed: '2026-10-24'
```
Deciding record: the `machine_verified` result for TASK-20261024-9fbb0f plus the sheriff review.

## 2. `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-charged-toy-ic-exponent-vs-rho.yaml`

```diff
 next_action:
   step: >-
-    Build the EXP-ICEX-153c34 backend (G1 membership, O5 oracle, S/G/X/V counters, admission-refusing
-    driver) and pass S0 gates G0-1..G0-6 on smoke curves, then fit the crossover order log
-    l* (IDEA-20260805-4d31bc) rather than a ratio exponent.
+    Before building the EXP-ICEX-153c34 backend, state the O5 oracle's return semantics and
+    predicted enumeration order k; build it only if k < (m-1)/2 (all-decompositions) or
+    k < m/2 - 1 (one-decomposition) at its arity, since the arity/oracle-order theorem
+    (formal/CryptoResearch/IC/ArityOracleThreshold.lean) shows no crossover l* exists in the
+    model otherwise. Then pass S0 gates G0-1..G0-6 on smoke curves and fit the crossover
+    order log l* (IDEA-20260805-4d31bc).
   discriminates: >-
-    A measured crossover with both arms on the same instances fixes the distance to rho in
-    one unit-invariant number; an empty crossover across the reachable range turns the lane
-    into an exhausted_at_scale record with the reached size.
+    k at or above the line: the lane closes as closed_obstructed (kind proof, via
+    LEAD-ICE-generic-oracle-arity-cost-floor) without a build; k below the line and a
+    measured crossover: open_next_step with best_measured; k below the line and no
+    crossover across the reachable range: exhausted_at_scale with the reached size and a
+    note that H1-H3 need re-examination for this pipeline.
```
Deciding record: the Coordinator's decision citing IDEA-20261024-a2b05d.

## 3. `knowledge/leads/ecdlp/ic-prime/LEAD-ICP-generic-table-decomposition.yaml`

```diff
   revisit_when: >-
-    A non-generic decomposition oracle exists with per-attempt cost T_dec << p^{1/4} at arity
-    m = 4 (an S_5 oracle at B ~ p^{1/5}), or a decomposition test sub-linear in |F|.
+    A non-generic decomposition oracle exists with fitted enumeration order k < (m-1)/2
+    (all-decompositions) or k < m/2 - 1 (one-decomposition) at its arity, e.g. a free
+    (k = 0) S_5 oracle at m = 4 or a linear (k = 1) S_6 oracle at m = 5; the two-term
+    remark "m = 3 only ties rho even with T_dec = O(1)" is theorem arity_three_free_ties of
+    formal/CryptoResearch/IC/ArityOracleThreshold.lean.
 ledger_refs:
+- IDEA-20261024-a2b05d
```
Deciding record: as in 1.

## 4. `knowledge/leads/ecdlp/ic-prime/LEAD-ICP-extension-field-embedding.yaml`

```diff
 obstruction:
-  kind: cost_model
+  kind: proof            # conditional on H6 (Gaudry's heuristic cost); theorem after review
   statement: >-
-    Gaudry's cost on E(F_{p^n}) is O~(p^{2-2/n}) against the original sqrt(p): p at n = 2 and
-    p^{4/3} at n = 3; the embedding enlarges the problem faster than the subfield helps. Scope: any fixed n.
+    Gaudry's cost on E(F_{p^n}) is O~(p^{2-2/n}) (H6, KR-IC-46d822) against the original
+    sqrt(p): p at n = 2 and p^{4/3} at n = 3; for every real n >= 2, 1/2 < 2 - 2/n and no
+    n >= 2 reaches 1/2 (formal/CryptoResearch/IC/ExtensionFieldEmbedding.lean,
+    TASK-20261024-551bd9), so the embedding enlarges the problem faster than the subfield
+    helps. Scope: any fixed n >= 2 with the subfield base {x in F_p}; other bases over
+    F_{p^n} are not covered.
 evidence:
+- repo: crypto-autoresearcher
+  path: formal/CryptoResearch/IC/ExtensionFieldEmbedding.lean
+  note: 1/2 < 2 - 2/n for all n >= 2; control at n = 1
```
Deciding record: the `machine_verified` result for TASK-20261024-551bd9 plus review.

## 5. `knowledge/leads/ecdlp/generic/LEAD-RHO-pool-class-quotient.yaml` (path drift, AUD-2 housekeeping)

```diff
 evidence:
-- {repo: ecc-challenges, path: verification/negation-walk-20261024/README.md, note: ...}
-- {repo: ecc-challenges, path: docs/negation-walk.md, note: ...}
+- {repo: ecc-challenges, path: verification/negation-walk-20261024/README.md, ref: claude/ecdlp-leads-analysis-l7f87y, note: ...}
+- {repo: ecc-challenges, path: docs/negation-walk.md, ref: claude/ecdlp-leads-analysis-l7f87y, note: ...}
```
Reason: both paths exist only at ecc-challenges commit `1f49962` on branch
`claude/ecdlp-leads-analysis-l7f87y`, not on `main` (`86f8a57`);
`lead_atlas.py --check --strict-paths` fails on them. Alternative: merge that branch.

## 6. `problems/README.md` (held by Conductor task T-5065; not edited)

Add the index line for `problems/formal-lean-external-volume-eintr.md`.

## 7-12. Disposition changes that survived three skeptics (audit workflow; wording as corrected by the skeptics, see `AUDIT.md` and the `votes` in the workflow result)

7. **`LEAD-TRF-padic-canonical-section`** (AUD-1 + two fold rows, all three survive). Split the row; no hypothesis or goal status moves.
   - Keep `LEAD-TRF-padic-canonical-section` `closed_obstructed` for the homomorphic-section / formal-logarithm clause only: `obstruction.kind: proof` (KN-FIND-7e2b94 has `proof_status: derivation`, so not `theorem` until machine-verified), statement narrowed to EV-CZLIFT-ad28f5 / H-CZLIFT-6d4ed1's scope ("for p not dividing n the prime-to-p torsion section is the only homomorphic section and the formal log kills it; the identity read-out channel is closed"), deciding records DEC-20261023-36b4f0 and EV-CZLIFT-ad28f5 (commit 87bdd8316f on origin/main). Delete the clause "any non-homomorphic section recovers d only at the random 1/p rate" (recorded false by DEC-20261024-23d64d).
   - New row `LEAD-TRF-torsion-section-digit-fourier` (`open_next_step`; the fold's new mechanism from KN-OPEN-d3a6f0): the p-adic digit characters i >= 1 of the torsion section against the n^(-1/4) Fourier-learning break-even; `next_action.step` = the DEC-20261023-2e7447 NA-4 successor queued as DEC-20261024-23d64d N-3(1); `discriminates`: Fourier mass above the break-even at two scales -> open_next_step with best_measured; at or below -> exhausted_at_scale for the reached n; `ledger_refs` DEC-20261023-2e7447, DEC-20261024-23d64d (cite only after its archive lands; `archived_by` is null today).
8. **`LEAD-TRF-small-genus-cover-general`** (AUD-5). Narrow the title to "Kummer/GHS covers of the x-line (degree-2 function x) over F_{q^3} and F_{p^k}, k = 6, 10, 14"; keep `closed_obstructed` with the statement as is. New row (open_next_step) for the non-x-line degree-2-function and Jacobian-existence routes over F_{q^3}, with the census of IDEA-20261018-* (the one named in the audit) as the first step and outcomes: a genus <= 3 cover found -> open_next_step with the map certified by `transfer`; none across the enumerated configurations -> closed_obstructed (kind proof, Riemann-Hurwitz) for that enumeration.
9. **`LEAD-EXO-augmented-oracle-ggm`** (AUD-2). Split: keep `closed_obstructed` (kind theorem, structured GGM per KN-FIND-002 / EV-GGM-001) only for oracles whose answers are group elements or equality bits computable by group operations (endomorphism image with public lambda, incidence, halving, net); move the coordinate-reading phrases (`x-coordinate oracle meet in the middle`, `y-coordinate oracle guided decomposition`, ...) to a new `open_unexamined` row whose first step is the simulation-overhead question of SO-GEN stated per oracle.
10. **`LEAD-EXO-miller-pairing-cocycle`** (AUD-4). Keep `open_next_step`; replace `next_action.step` with: (1) commit the T-KUMMER derivation (`AUDIT.md`, exotic X2: for gcd(N, p-1) = 1 and f = f_{N,P}, chi(U(R)) = chi^{...}) as a reviewable knowledge or ledger record, anchoring the Weil/Deligne input on a KN-LIT row; (2) only then run the K1/K2 identity check as the reduction check. `discriminates`: K2 exact on all k -> closed_obstructed (proof); K2 fails -> the correlation experiment as currently queued.
11. **`LEAD-RHO-non-automorphism-equivalence`** (AUD-5; the three skeptics agree the step is too weak and disagree on the remedy). Minimal version all three accept: keep one row, `open_unexamined -> open_next_step`, add the scope note "generic canonicaliser: Shoup/Nechaev plus the lemma |A|^2 - |A| + 1 >= |H| (Lean target in `AUDIT.md`) bounds the gain of any H-invariant computed by group operations; the open half is an encoding-specific canonicaliser", and make the first step the lemma's proof plus a measured canonicalisation cost for one encoding. The split into a closed generic half (kind theorem) is the alternative two skeptics prefer; both keep the id.
12. **`LEAD-ICE-chained-semaev-dreg-vs-semiregular`** (AUD-4). Keep `open_next_step`; rewrite `next_action.step`: build and run the block/topology-matched null (IDEA-20260805-f49efb, IDEA-20260808-11b8c7) on the frozen EV-DREG-008 cell (n = 12, t = 3, ti = 0, seed = 2026, D = 6) first, since KR-IC-fbdb61 already says the semi-regular prediction does not describe descended systems; `discriminates`: the null absorbs the deficit -> closed_obstructed (support artefact, toy, scoped to Frobenius-invariant chains); it does not -> the C1 re-run at n = 15 as queued.
