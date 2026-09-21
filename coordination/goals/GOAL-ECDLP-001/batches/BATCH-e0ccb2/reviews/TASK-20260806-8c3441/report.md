# Independent Red Team Report — TASK-20260806-8c3441

**Task:** TASK-20260806-8c3441 (independent red-team), BATCH-e0ccb2, GOAL-ECDLP-001
**Role:** Red Team (independent session; this session did not contribute to the reviewed documents)
**Requested policy:** `review-adversarial`; resolved model id: opencode/deepseek-v4-flash-free

**Reviewed (committed, read-only):**
- coordination/goals/GOAL-ECDLP-001/batches/BATCH-121/tasks/TASK-20260805-004/oracle_hpseudo_analysis.md
- coordination/goals/GOAL-ECDLP-001/batches/BATCH-121/tasks/TASK-20260805-005/closure_and_multi_target.md
- ledger/decisions/DEC-20260805-364e9e.yaml
- ledger/decisions/DEC-20260805-70450a.yaml
- coordination/goals/GOAL-ECDLP-001/batches/BATCH-e0ccb2/batch.yaml
- Supporting context (read only): IDEA-20260805-62ef74, IDEA-20260805-58b638, IDEA-20260805-0cd03f (BATCH-120), KN-FIND-9d2f56, KN-FIND-c7d31e, H-PSEUDO-83817b, BATCH-060/TASK-20260804-051/ggm_analysis.md

**Mandate:** falsify the interpretation, cost model, and scope of the two BATCH-121 analyses and of DEC-20260805-364e9e. No experiment was run; all checks below are algebraic identities, arithmetic rewrites, or proposed run recipes.

---

## Summary

The BATCH-121 documents contain several correct isolated sub-claims (rational-function duplication formula; the ordinal table at p=1009; the arithmetic of the K* table). The interpretations attached to them are not defensible as written, and DEC-20260805-364e9e reproduces those interpretations as official findings. The strongest single falsification: the doubling-oracle closure is void because a **halving query** retrieves x(Q) directly, independent of any cycle of length `ord_N(2)` — so the "no sub-rho path, barrier confirmed → rejected" disposition for IDEA-58b638 rests on a false model of what the oracle does, and the "confirmed closure" in DEC-364e9e is unsupported. A second structural failure: the "unconditional sub-rho" finding (claim A in Task-20260805-004) is a heuristic cost estimate mislabeled as unconditional, and it *contradicts* the sibling closure's premise that the x-coordinate oracle yields no sub-rho. The corrected biconditional is not actually biconditional at the failure scales H-PSEUDO itself predicts. The multi-target crossover arithmetic is correct but the *cost model* feeding it omits linear algebra and memory.

---

## Objection 1 — "Unconditional sub-rho" (L[1/2, sqrt(2)] ≈ 2^61.7) is a heuristic-labeled claim

**Attacked claim (TASK-20260805-004 Q1; DEC-364e9e finding #1):** "Semaev IC is sub-rho (L[1/2, sqrt(2)] ≈ 2^61.7 << 2^128) in GGM+C_t UNCONDITIONALLY."

**Falsification route.**
- The arithmetic `L[1/2, sqrt(2)]` for N=2^256: exp(c·sqrt(log N · log log N)) with c=sqrt(2): log(e)N)=256·ln2=177.4; ln(ln N)=ln(177.4)=5.18; product=919; sqrt≈30.3; c·30.3≈42.9; exp(42.9)≈2^61.9. The figure 2^61.7 is consistent with that convention. But the *rate* L[1/2, sqrt(2)] is held only under a smoothness/yield heuristic for Semaev IC — it is not a theorem for any family. Paragraph Q1 itself uses "with heuristic yield"; the tag "unconditionally" elsewhere is unsupported. DEC-364e9e lifts "UNCONDITIONALLY" into a finding, which is scope dishonesty under AGENTS rule 5 and the cost-honesty profile.
- The cost number omits: linear-algebra term `B^omega`, memory for factor base + relation matrix, factor-base construction cost, and the per-attempt field arithmetic of the Semaev polynomial. L[1/2, sqrt(2)] is the *relation-collection-only* rate under a specific parameter balance; the documents do not show that balance is achievable with the /B chosen order for GGM.

**Cheapest control:** rewrite the claim as "sub-rho (heuristic, if the yield and smoothness heuristics hold and if overheads are bounded by constant factors)" and strip "unconditional" from the DEC findings. No compute needed.

## Objection 2 — GGM+C_t accounting hides query volume and preprocessing

**Attested claim.** Membership = 1 × C query per point; full recovery O(log p); IC only needs the membership bit; total O(1) per relation.

**Falsification route.**
- `O(1)` is per candidate, not per relation. Generating relations enumerates ~B^(m-1) (or with BKK, (B/2)^(m-1)) candidate m-tuples; each candidate is charged one C_t query in their accounting, so a total oracle-query volume of that same magnitude is neither discussed nor bounded by L[1/2] — B is never pinned down at N=2^256.
- Factor base construction: a threshold-defined F (subset of x-values) still has to be *found* by oracle evaluation in the GGM; the analysis treats the factor base as frictionlessly given ("IC does not need the full coordinate, only the membership bit"); the construction is a hidden preprocessing term that rules out the "O(1) overhead" claim unless it is charged explicitly.
- x-recovery is O(log p) ≈ 256 adaptive C_t queries for P-256. The claim "IC needs only the membership bit" silently assumes the Semaev decomposition polynomial can be evaluated from the membership bit of the target R alone, without the concrete x-coordinate. Evaluating S_m at x_R is an algebraic requirement; substituting a one-bit predicate in its place is an assumption, not a consequence.

**Cheapest control:** on a toy field (16–24 bit) implement relation-collection literally counting C-t queried per candidate; compare to the "one per point" formula and record the actual constant/volume. Cheap; yields a number, false if the count is ≥ (candidate count)-log N.

## Objection 3 — The corrected biconditional is not a biconditional at the failure scale H-PSEUDO itself predicts

**Attested claim (TASK-20260805-004 §Corrected Claim B; DEC finding):** "∃F chain-C_R^F β_1<sqrt(N) iff ∃F H-PSEUDO fails for F."

**Falsification route.**
- Quantifier mismatch: chain sub-rho is a global condition (β_1 < sqrt(N) for the complex over the factor base, i.e. about typical targets); the right side is an existence condition ("there exists an F" with a large Fourier coefficient). A large max_k |hat| at one frequency k* only inflates yield for targets whose DL is aligned with k* — the analysis itself says "a fraction 1/k* of all targets" (Q2). So the right-hand side does not imply chain-sub-rho for an arbitrary target R; the LHS and RHS quantify over different witness sets, and as stated the biconditional is incomplete.
- Scale issue: the yield lift is governed by the term Σ_{k≠0} |hat(k)|^m ≤ M^m (per the analysis's own S_m(R) formula). For a *moderate* failure — max coefficient M = C·sqrt(B) with C ≈ 3–6, exactly the magnitude H-PSEUDO-83817b's own predictions allow without being violated — M^m/N is dwarfed by B^m/N for B ≫ C^2, so no above-heuristic yield appears and the "failure ⇒ above-heuristic yield" direction fails to activate. The direction only fires when M is on the order of B itself (maximal failure), which the analysis elsewhere treats as the rare worst case.
- Net: "H-PSEUDO fails (moderately)" does not imply "chain-complex sub-rho"; the corrected biconditional is only defensible for maximal failures, and even then only for the aligned fraction of targets.

**Cheapest control:** with C-values from the H-PSEUDO predictions (C≈1.1 crossover, max 3.9–5.2), compute M^m/N vs B^m/N for B ≈ N^(1/3)−N^(1/2), record that relation fails to give above-heuristic yield ⇒ the feared "failure" must be quantified before any characterization. Pure arithmetic.

## Objection 4 — (CRITICAL) Halving query recovers x(Q) in ONE call; the ord_q(2) argument is void

**Instance (pure algebra, no compute).** In the prime-order subgroup of order q, the scalar (q+1)/2 is a public integer, so `[(q+1)/2]·Q` is computable by O(log q) doublings/adjustments of the handle Q — permitted in any GGM. Then a single query

```
O_D(P) with P = [(q+1)/2]·Q   =>   x([2]P) = x([q+1]·Q) = x(Q)
```

returns the x-coordinate of the target directly. The claimed mechanism in closure_and_multi_target.md §A.3 — "extract x(Q) via the doubling chain costs ord_q(2) ≈ sqrt(q) oracle calls … identical to Pollard rho; no speedup obtained" — is **false about what the oracle does structurally**: no 2-cycle (t = ord_q(2)) is needed at all, only one query on a publicly computable halved handle.

Consequences:
- The brief's halving scenario is realized: O_D([2^{-1}]Q) trivially reveals x(Q). This does not by itself exhibit a sub-rho *DLP* algorithm (x(Q) ≠ k), but it strips the closure down to the claim "x-coordinate oracle access does not enable sub-rho ECDLP" — which is a conjecture, not a theorem. BATCH-060 classified the x-coordinate (encoding) oracle as NON-SIMULABLE and stated only that recovering k from it "reduces to DLP"; it did not prove no acceleration.
- Cross-document tension: Task-20260805-004 (Claim A) asserts concrete-model (x-coordinate-equipped) Semaev IC is sub-rho "unconditionally" at L[1/2]; Task-20260805-005 asserts O_D ⊂ x-oracle power and that no sub-rho path exists. Since O_D gives x(Q) for arbitrary Q (by the halving identity), O_D has exactly the power of the x-oracle on arbitrary handles; if x-oracle-equipped IC is sub-rho (Task-004), then "no sub-rho path" (Task-005's disposition for IDEA-58b638) is contradicted at the level of interpretation. DEC-364e9e carries both findings without noting the conflict.
- "ord_q(2) = Ω(sqrt(q)) generically": this is a distributional heuristic for random primes (artin's-conjecture-type), not a lower bound valid for all large primes. There are explicit counterexample classes: if q = 2^r − 1 is prime (Mersenne prime), then 2^r ≡ 1 (mod q) and no smaller power works, so ord_q(2) = r = log2(q+1) ≪ sqrt(q). The 5-curve toy table (q ∈ {17,19,7,71,107,29} at p=1009) cannot certify a generic-primes claim, and the closure's (C) step leans on it without a bound for the exceptional class.

## Objection 5 — Multi-target BKK crossover: formula checks out; regime/model claims do not

**Attested claim:** `K*(BKK) = ⌈ s·β/(1−t·β) ⌉`, β = 2/(m+1); "BKK rescues t ∈ [1, (m+1)/2)"; example m=5, s=200, t=0.9 → "2001 → 96".

**Independent recompute.** For s=200, t=0.9, m=5 (β=1/3):
- K*(std) = ⌈200/(1−0.9)⌉ = ⌈200/0.1⌉ = ⌈2000⌉ = 2000. The doc prints 2001; that is the strict-inequality edge (needs k with k·(1−0.9) > 200, i.e. k > 2000, so minimal integer 2001). Off-by-one on an edge convention; worth pinning down but stable.
- K*(BKK) = ⌈200·(1/3)/(1 − 0.9·(1/3))⌉ = ⌈66.67/0.7⌉ = ⌈95.24⌉ = 96. ✓

**Falsification route.**
- Linear algebra omitted: a real IC cost is S_rel + k·T_desc + S_LA(relation matrix); the crossover model compares only S_rel + k·T_desc against k·sqrt(N) and drops the matrix term entirely (B^ω). Including LA changes the balance rows; the "rescue" is only about the descent term in the linear model.
- Memory is not dimensioned anywhere: factor base, relation matrix, and (for BKK) the sparse (B/2)^{m-1} candidate structure all require memory that is never tabulated; the crossover table has no memory column, so it cannot be checked against the target profile's "memory beside time" requirement.
- The "rescue" regime claims: "t∈[1,(m+1)/2)" gives a finite K* only as a mathematical restatement of "t·β < 1" in a labourless linear model. It does not assert that the whole multi-target instance (relations + LA + memory) beats rho; calling it "the principal new capability" is an over-scoped conclusion. And if t·β ≥ 1 the formula is unbounded again, so the "rescued" range is exactly a thin interval in the toy model.
- "Provable" labelling: the BKK theorem (KN-FIND-c7d31e) proves the per-attempt enumeration speedup; the crossover transfer "S·β and T·β" is an extra modelling assumption (that both channels scale by exactly β with no interference), not part of the theorem. The doc's claim "provably (not heuristic) reduction since BKK is proved" (§B.7) overstates what is provable.

**Cheapest control:** rerun the tables with LA term (B^ω at the balancing B) and a memory column, and state the strict vs non-strict inequality convention; then compare the same (s,t) rows. Cheap; changes conclusions at the "2000 vs 2001" edge and at the rescue boundary.

## Objection 6 — Pareto honesty: `dominated_by`/`sota_delta` labels are honest; headline findings are not

- DEC-20260805-364e9e `pareto_integrity`: dominated_by 'Pollard rho at exponent 1/2', sota_delta 'not_applicable'. That block is acceptable *as recorded* (constant-factor and theoretical only).
- The over-claims live in the derived findings/paraphrases: (i) "sub-rho UNCONDITIONALLY" (§Objection 1); (ii) "closure, barrier confirmed, no sub-rho path ⇒ rejected" for IDEA-58b638 (§Objection 4) contradicts the sibling analysis; (iii) "provable" in the BKK crossover summary (§Objection 5).
- Practical import: in the IDEA records, `dominated_by` is set to Pollard rho at exponent 1/2 and `sota_delta` N/A — consistent. But claiming "no sub-rho path (closure)" for a method whose sibling analysis itself claims sub-rho via the same x-coordinate access means the two deliverables disagree on whether the method is dominated; the closure's `dominated_by` field is thereby not fully checked against every row of the frontier (cf. Inventor-protocol Pareto honesty).

**Cheapest control:** text-only: make each anomalous conclusion conditional on the named heuristic and record the cross-document conflict (Task-004 vs Task-005) in the discipline-notes before any status transition that asserts "no sub-rho".

---

## Falsification routes consolidated per objection (cheapest control)

| # | Object being attacked | Cheapest discriminating control / counterexample |
|---|---|---|
| 1 | "Unconditional" sub-rho L[1/2] estimate | Restate as heuristic-conditional; reject "unconditional" in findings |
| 2 | GGM+C_t O(1)-per-candidate accounting | Toy count of actual C_t query volume in a 16–24-bit relation harvest (B^{m-1} loop) |
| 3 | Corrected biconditional | Boundary check M = C·sqrt(B), C≈3–6, fails to beat B^m/N, so "H-PSEUDO fails ⇒ chain-sub-rho" does not follow |
| 4 | Doubling closure / ord_N(2) | Algebraic: x(O_D([(q+1)/2]Q)) == x(Q) on the doc's own q=17 curve — one query recovers x(Q); the barrier argument collapses |
| 5 | BKK crossover model | Recompute tables with LA term + memory column + strict-inequality convention |
| 6 | Pareto/sota phrasing | Reword "unconditional"/"no sub-rho"/"provable" as conditional; record the Task-004 vs Task-005 conflict |

The single cheapest discriminator overall is Objection 4's halving test — it is an algebraic/oracle-interface contradiction independent of any benchmark.

---

## Scope note

- This report attacks interpretation, cost model, and scope only. It creates no evidence about ECDLP hardness in either direction and does not retract the BATCH-121 committed documents.
- No experiment was run; all checks above are algebraic identities, arithmetic rewrites, or future recipes. No fabricated runs, timings, statistics, or citations are introduced. Pointed references to committed records (TASK-20260805-004/-005, KN-FIND-9d2f56, KN-FIND-c7d31e, DEC-364e9e, H-PSEUDO-83817b, BATCH-060/TASK-20260804-051) cite existing files; the m=5/s=200/t=0.9 crossover rows were recomputed independently here.
- Recommendation to Coordinator: supersede the "rejected with barrier confirmed" disposition of IDEA-20260805-58b638 (Objection 4); reconcile the two documents' conflicting stances on the x-coordinate oracle (Task-004 sub-rho claim vs Task-005 no-sub-rho claim); re-tag "unconditional" as heuristic-conditional; and rephrase the corrected biconditional with the alignment-fraction quantifier before any dispatch that treats it as a theorem. The read-only experiment approvals (EV-SEMAEV-7f7d22) can proceed but their acceptance criteria must include the linear-algebra term and memory.