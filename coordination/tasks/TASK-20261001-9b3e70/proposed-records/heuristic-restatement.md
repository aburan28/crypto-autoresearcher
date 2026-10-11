# D3: HEUR-HARVEST-FV, a restatement of HEUR-GENERIC-MSUM in relation-harvesting form, with the fill charged

- **Task and author:** TASK-20261001-9b3e70, idea-generator, 2026-10-01/02.
- **Status:** a draft for the Coordinator. It is **not adopted** (DEC-20261001-5c9e7a R6 says the restatement "is not adopted by this decision").
- **Runs and scope:** zero runs. No statement about any deployed curve.
- **Conditionality:** this draft is conditional on the Coordinator's ruling on DERIVATION.md §2.5 (the literal (C-yes) flag). It is written on the generic invariants of DERIVATION.md §2.3, which stand under either ruling.

## 1. What is being replaced, and why

HEUR-GENERIC-MSUM (H-SEMBIN-8e7ae3) is quoted here: "m-SUM over the group of points of a binary elliptic curve admits no better generic time-store tradeoff than partial meet-in-the-middle: with store |F|^s the time is |F|^(m-s)".

It is contradicted as worded (DEC-20261001-5c9e7a R6, via vOW §5.3). Three facts force the restatement to change form, not just its numbers:

1. **Wrong object.** It is a per-target statement. What the family consumes is K = |F| + O(1) relations, harvested by any means.
2. **No fill charge.** It charges no table construction, so a table larger than rho's work looked cheap.
3. **Wrong frontier.**
   - Its generic half is no heuristic: it is COR-GEN (DERIVATION.md §3), a theorem consequence.
   - The comparator it implicitly used, the shared-table line T·M = m!·N·|F|, is not a frontier. Generic batched collision harvesting already lies below it (DERIVATION.md §2.2).

So the replacement has two parts. One is a theorem-backed generic layer, cited and not claimed. The other is two numbered heuristics, and they carry exactly what the theorem does not: the non-generic object F_V and the membership test.

## 2. Shared definitions

- **Group.** E/F_{2^n} is a binary curve with n prime. ⟨P⟩ ≤ E(F_{2^n}) has prime order ℓ and cofactor h ∈ {2, 4}.
- **Factor base.** V ⊂ F_{2^n} is an F_2-subspace of dimension D. The factor base is F = F_V = {Q ∈ ⟨P⟩ : x(Q) ∈ V}, which is negation-closed, with |F| ≈ 2^D / h (heuristic count, not derived exactly here).
- **Koblitz case.** On a Koblitz curve with σ-stable V, F is also π-closed.
- **Relation.** A relation is Σ_j c_j·[F_j] = a·P + b·Q that is not a formal identity. K = |F| + 2 relations of full rank suffice (J1 weak_point_checks; DERIVATION.md cites it).
- **Cost unit (v1/v2 unit, declared optimistic for index calculus).** Each of these counts 1:
  - group operation;
  - F_{2^n} field operation;
  - table write;
  - probe;
  - membership test x(Q) ∈ V;
  - Frobenius application (Koblitz).

  **Fill charged:** every stored entry costs at least 1 at the time it is written. M is the peak number of stored group elements.
- **Classes.**
  - 𝒢 is the COR-GEN generic class (DERIVATION.md §3.2).
  - 𝒜_FV, the semi-generic class, is 𝒢 plus a unit-cost membership test x(Q) ∈ V, plus unit-cost π on Koblitz curves.
  - 𝒜_FV **excludes** coordinate algebra beyond the membership test: summation polynomials, Weil descent, Gröbner/SAT, approximate x-filters, and trace and halving tests. Those are OPEN-A and OPEN-B. This heuristic is silent on them, as R6's wording requires.

## 3. The generic layer (theorem-backed; cited, not claimed; sota_delta 0)

- **G-1 (COR-GEN).** Every H ∈ 𝒢 spends at least c·√ℓ calls before its first non-trivial relation, at any memory.
  - Basis: Wagner 2002 Cor. 1, retrieved by TASK-20260928-62ad14. Shoup 1997 via KN-LIT-011, whose primary text was unreadable here. Secondary: Hhan 2024 Thm 3.3, retrieved this session.
- **G-2 (multi-instance).** n DL instances cost Ω(√(nℓ)) in the GGM.
  - Basis: Yun 2015, abstract retrieved; Hhan 2024 Thm 3.4, retrieved; KR-RHO-46c2c6.
  - Transfer to "K relations" needs the **K-of-L missing step** (DERIVATION.md §2.3 and OPEN-C). Until that step is proved, G-2's harvesting form is itself conditional. That is why it also appears in clause 2 below.

## 4. The heuristic, numbered

### HEUR-HARVEST-FV-1 (distributional)

**Formal statement.** Fix (n, E, ⟨P⟩, V) as in §2, with ℓ prime, and let F = F_V. Let F* be a uniformly random negation-closed list of the same size, also π-closed on Koblitz curves with σ-stable V: a union of the same number of ±-orbits (or ⟨±π⟩-orbits) of uniformly random elements of ⟨P⟩. Two statistics must be indistinguishable between F and F*, up to the stated tolerance:

- **(a) Two-sum coincidences.** N_2(F) is the number of unordered pairs {{a, b}, {c, d}} ⊂ F with a + b = c + d, excluding formal identities:
  - excluded identities are {a, b} = {c, d}, and pairs where both sides are 0 (a = −b and c = −d);
  - on the Koblitz case, π-images are also excluded.

  N_2(F) is Poisson-distributed with the same mean λ_2 as N_2(F*). For a random list, λ_2 ≈ |F|^4/(8ℓ). The constant here is scratch and must be fixed by the null sample, not by this formula.
- **(b) Decomposition counts.** For a uniformly random target R ∈ ⟨P⟩, the number of unordered m-multisets in F summing to R (m ∈ {3, 4}) has the same distribution under F and F*. Both are approximately Poisson(|F|^m / (m!·ℓ)), up to the negation multiplicity.

**Random-model justification.** Two pieces support it:
- **Rigorous, with no x-structure:** for a list of uniformly random elements, the counts in (a) and (b) are sums of pairwise or m-wise weakly dependent indicators of probability 1/ℓ. Their Poisson limit is the classical Poisson-approximation regime for sparse random sums.
- **Literature (recalled, backs nothing):** the "decomposition probability ≈ |F|^m/(m!·#group)" heuristic is standard in the summation-polynomial literature (Diem; Petit–Quisquater).

The assumption is that the F_2-linear condition x ∈ V imposes no additive structure on ⟨P⟩ beyond the detectable symmetries (negation, π), so that F_V behaves like F*.

**Falsification condition.** At any tested cell, either of these, with the null F* passing its own calibration and the positive control detected:
- the empirical distribution of N_2 or of the decomposition count departs from the F* null at p < 10^-3 after Bonferroni correction over all cells;
- the largest-count cell exceeds the Poisson tail predicted by λ at p < 10^-3.

### HEUR-HARVEST-FV-2 (algorithmic, fill charged)

**Formal statement.** For every harvester H ∈ 𝒜_FV, every tested (n, D), and peak memory M:

    T(H) ≥ (1/8) · K · √(ℓ / min(M, K))

Here T(H) is the number of unit operations to output K = |F| + 2 full-rank relations, with every stored entry charged at write. In particular, T(H) ≥ (1/8)·√(Kℓ), and T(H)²·M ≥ (1/64)·K²·ℓ for M ≤ K.

**Random-model justification.** Three supports, the first two cited:
- **(i)** For list-only access (H ∈ 𝒢), the time clause is G-2 conditional on the K-of-L step. The time-memory clause is Dinur 2020's T²·S = Θ̃(C²·N) for C collisions (KR-RHO-7d93f6, abstract-read, random-function model). PCS batching meets it at about 4·K·√(ℓ/w) (J3 §2; AMD X-6). The constant 1/8 is set 5 bits below that best known harvester, **declared before any measurement**.
- **(ii)** The membership test adds only "decomposition events". Each test on a non-formal element succeeds with probability about |F|/ℓ (clause 1(b) at m = 1), giving relations ≲ T·|F|/ℓ + T²/ℓ. This is my sketch, unreviewed. At arity 1 it reproduces IDEA-20260807-070d03's N/(2√L) rho result (internal).
- **(iii)** Frobenius at unit cost buys at most the orbit factor 2n (DEC-20261001-5c9e7a R8; KR-RHO-037e22). That is absorbed in the constant only if c is read **per orbit class**. On Koblitz curves the statement is therefore made with ℓ replaced by ℓ/(2n), matching rho's √(2n).

**Falsification condition.** An exhibited H ∈ 𝒜_FV whose fill-charged unit count to K full-rank relations is below the stated line at some tested (n, D, M). It must be measured over ≥ 30 independent (curve, V, Q) instances, with the 99% upper confidence bound of the mean below the line, and with the same harness's PCS-batch arm reproducing its predicted 4·K·√(ℓ/w) to within a factor of 2.

## 5. Validation plan

None of these samples is run by this task, and none is approved: designing it is a later task. Scale numbers are estimates.

- **V1: clause 1(a), toy scale, exhaustive.**
  - **Curves:** n ∈ {31, 37, 41, 43, 47}. For each n, 3 random ordinary binary curves with h ∈ {2, 4} and ℓ prime, plus a Koblitz curve wherever #E_a(F_{2^n})/h is prime (to be checked, not assumed).
  - **Subspaces:** V is a random F_2-subspace, with D chosen so that λ_2 ∈ {2^-2, 2^0, 2^2, 2^4, 2^6}. Ten subspaces per cell.
  - **Method:** count N_2 by hashing all |F|²/2 pairwise sums. That is about 2^24 group operations at |F| = 2^12, and needs no discrete logs.
  - **Null:** F* generated as ±(r_i·P) for random r_i, plus π-orbits on Koblitz. 100 null lists per cell.
  - **Positive control:** F_AP = ±{P, 2P, …, (|F|/2)·P}, with N_2 ≫ λ_2. It must be flagged by the same test.
  - **Comparison:** the empirical distribution of N_2 over subspaces against the null's empirical distribution (two-sample KS), and against Poisson(λ̂_null).
  - **Tail check:** the maximum standardised excess over all cells against the Bonferroni-corrected normal tail. P(N_2 ≥ k*) with k* the largest observed, against the Poisson tail.
- **V2: clause 1(b), toy scale.**
  - **Setup:** same curves. m ∈ {3, 4}. 10^4 uniformly random targets per (curve, V).
  - **Method:** count decompositions by MITM over unordered (m/2)-sums, tables kept in RAM. D is chosen so that |F|^m/(m!·ℓ) ∈ [2^-3, 2^3].
  - **Comparison and tail:** the same null and comparison as V1. Tail: P(count ≥ 3) against Poisson.
- **V3: clause 1(a) at cryptographic degree (weak, disclosed as weak).**
  - **Setup:** n ∈ {131, 163}, D = 16, so |F| ≈ 2^15. N_2 by hashing about 2^29 sums.
  - **Prediction:** λ_2 ≈ 2^60/(8·2^129) ≈ 2^-72 (scratch), so the prediction is N_2 = 0.
  - **What it tests.** Any non-trivial coincidence falsifies clause 1(a) at cryptographic scale. A zero cannot confirm the dense-regime rate.
  - **Shortcut and transfer.** No shortcut comparable to the Deuring correspondence is known that samples dense-regime statistics at n = 131. Transfer of V1 and V2 to n ≥ 97 is **by assumption**, stated as such.
- **V4: clause 2, toy scale.** This reuses IDEA-20260930-4b7d1e step 2's harness if that is ever carded (it is NOT in this task's scope).
  - **Arms, on the same op counter:** PCS batching over F_V; PCS batching over F*; ENUM via membership test; shared-table PMITM with fill charged; per-target vOW golden collision.
  - **Grid:** w ∈ {2^4, 2^6, 2^8, 2^10}.
  - **Samples:** at least 30 instances per cell.
  - **Comparison:** fill-charged unit count to K relations against (1/8)·K·√(ℓ/min(M, K)), and against each arm on F*.
  - **Tail check:** the minimum over instances against the 1% quantile of the F* arm.
- **Sampled parameters to record:** n, the curve coefficients, ℓ, h, D, a basis of V, the seeds, |F|, λ, and every op-counter definition.

## 6. What this heuristic does not do

- It does not bound algebraic oracles: summation polynomials, Weil descent, approximate filters (OPEN-A, OPEN-B).
- A pass of V1–V4 would not make the family's conclusion unconditional outside 𝒜_FV.
- It moves no exponent. Its value is that the family's numbers become validatable at all. The previous heuristic was not validatable by its own text.
- **dominated_by:** "n/a (no result claimed)". Its generic half is KR-RHO-46c2c6 / KN-LIT-011.
- **sota_delta:** 0 on time, memory and data/queries.
- **Novelty:** `unverified`. The Poisson decomposition heuristic is standard but `recalled` here. The membership-class clause and the closure-matched null were not searched for beyond the corpus Greps listed in DERIVATION.md §7.
