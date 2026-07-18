# EXP-EQJ-001 analysis — B3 isotypic decomposition of the m=4 Semaev fiber-product relation space

Runs: RUN-EQJ-001-a (p=211), RUN-EQJ-001-b (p=1009), RUN-EQJ-001-c (p=4099). Seeds 20260717..20260719 everywhere.
Curves (deterministic rule): p=211: y²=x³+x+1, n=223; p=1009: y²=x³+x+14, n=1013; p=4099: y²=x³+x+34, n=4049 (all prime ⇒ ordinary; p ∤ 48).
G = B₃ = S₃ ⋉ (Z/2)³, |G| = 48, 10 irreps (dims 1,1,1,1,2,2,3,3,3,3). Ambient modules M = 13824, 13824, 32768; G-orbits: 364, 364, 816.
No deviations: no timeouts (max single-run wall 4.45 s ≪ 600 s), 3 seeds as frozen, no size reductions.

## 1. Controls

| control | result |
|---|---|
| POS-1 Parseval (Σ w_λ = N exact; Σ mult·dim = M) | PASS, 9/9 cells |
| POS-2 conservation (Σ B_λ ≡ A mod n, entrywise) | PASS, 9/9 cells |
| POS-3 spotcheck (5 relations/seed re-verified by fresh EC addition) | PASS, 9/9 cells |
| group construction (10 classes, 10 irreps, orthogonality Σ|cc|χ² = 48) | PASS |
| numpy rank vs Sage rank on every block (run a, --crosscheck) | PASS (all equal) |
| independent audit eqj1_verify.sage (ranks over GF(n) and QQ, 9/9 cells) | PASS (all ranks match) |
| NEG-1 null (8 random N-subsets per seed) | EC profile OUTSIDE null envelope in all 90 block-cells |

## 2. Per-cell measured numbers

N = |U_T| (fiber relations); w over the 10 isotypes in label order [trivial, sign_det, sign_prod, sign_perm, ir2#4, ir2#5, ir3#6, ir3#7, ir3#8, ir3#9].

| p | seed | N | w (10 blocks) | w_triv/N | r_full | r_blocks | orbits_hit |
|---|---|---|---|---|---|---|---|
| 211 | 20260717 | 1568 | [398.75, 0, 185.25, 0, 0, 0, 0, 479.25, 0, 504.75] | 0.254 | 12 | [12,0,12,0,0,0,0,12,0,12] | 206 |
| 211 | 20260718 | 2150 | [631.0, 0, 233.5, 0, 0, 0, 0, 660.0, 0, 625.5] | 0.294 | 12 | same pattern | 244 |
| 211 | 20260719 | 1184 | [235.75, 0, 133.75, 0, 0, 0, 0, 455.25, 0, 359.25] | 0.199 | 12 | same pattern | 177 |
| 1009 | 20260717 | 222 | [29.25, 0, 29.25, 0, 0, 0, 0, 81.75, 0, 81.75] | 0.132 | 12 | same pattern | 41 |
| 1009 | 20260718 | 472 | [99.5, 0, 63.5, 0, 0, 0, 0, 136.5, 0, 172.5] | 0.211 | 10 | same pattern | 70 |
| 1009 | 20260719 | 198 | [24.75, 0, 24.75, 0, 0, 0, 0, 74.25, 0, 74.25] | 0.125 | 10 | same pattern | 40 |
| 4099 | 20260717 | 228 | [31.5, 0, 31.5, 0, 0, 0, 0, 82.5, 0, 82.5] | 0.138 | 11 | same pattern | 39 |
| 4099 | 20260718 | 240 | [33.0, 0, 30.0, 0, 0, 0, 0, 87.0, 0, 90.0] | 0.138 | 11 | same pattern | 40 |
| 4099 | 20260719 | 300 | [39.0, 0, 39.0, 0, 0, 0, 0, 111.0, 0, 111.0] | 0.130 | 14 | same pattern | 54 |

Isotypic multiplicities (ambient module, per size): p=211/1009 (M=13824): mult = [364,220,364,220,572,572,792,936,792,936]; p=4099 (M=32768): [816,480,816,480,1248,1248,1728,2160,1728,2160]. Near |G|-symmetric (mult/dim ≈ M/48), small deviations from small orbits (histogram at p=211: {8:12, 24:132, 48:220}).

## 3. Negative control (random hypergraph / random action null)

Per spec, one null family covers both (conjugating the action by a random permutation σ gives w_λ^(σ) = ‖π_λ σ⁻¹f‖², distributionally identical to randomizing f). 8 seeded uniform N-subsets per seed. EC values are outside the null [min,max] range for **all 10 blocks at all 9 cells** (|z| from 7.5 to 152). The EC block distribution is decisively not that of a random hypergraph with a random action — the candidate's stated kill condition ("if they do, block structure is not EC-specific and any asymptotic hope dies") is **not triggered**.

## 4. Unexpected observations (rule 8)

1. **Exact zeros, structurally forced**: at every cell, exactly the same 6 of 10 isotypes carry w_λ = 0 (exactly). Mechanism identified during analysis: the relation indicator f is S₃-invariant (the sum Σt is permutation-invariant), so f lives in the S₃-fixed subspace; exactly 4 B₃-irreps have S₃-fixed vectors (trivial, sign_prod, and the two dim-3 irreps whose S₃-restriction contains a trivial isotype — measured: irrep_7_dim3, irrep_9_dim3). The zero pattern matches this representation-theoretic argument exactly at 9/9 cells.
2. **Distinct-row collapse**: the fiber's relations collapse to very few distinct coefficient rows (audit: 65/64/67 distinct rows at p=211; 12/12/12 at p=1009; 11/11/15 at p=4099, vs N up to 2150). rank_full ≈ #distinct rows in every cell. G-orbits of tuples map onto the same coefficient vector (slot permutations and sign patterns with equal column sums are indistinguishable in the matrix).
3. **Rank does not split**: every surviving block has r_λ = r_full exactly (all 9 cells), including the rank-deficient cells. The four blocks are not independent subsystems; each single-handedly spans the full column space.
4. **Integer kernel vectors** where distinct_rows > rank (p=1009 seeds …18/…19, p=4099 all seeds): e.g. p=1009/…18 kernel (mod 1013): [1,9,0,−4,2,7,5,−19,10,2,−9,−6], [0,0,1,−2,0,0,2,−4,2,−1,0,0] — small-integer relations, rank_QQ = rank_GF(n) confirms rational (not mod-n) phenomenon.
5. **EC orbit clustering**: EC relations hit far fewer G-orbits than the null (p=211: 177–244 vs null 333–362; p=4099: 39–54 vs null 193–262) — orbit-compressed storage is EC-specific (relations arrive in near-full orbit bundles).
6. Degenerate P₄ = O hits (T = Σt exactly): 54/42/33 (p=211), 12/33/12 (p=1009), 6/18/9 (p=4099) — excluded from relations, recorded.
7. orbit-scan DLP missed a decomposition for 1/20 targets at p=4099/…18 and 2/20 at …19 (baseline: 0 misses anywhere) — the orbit-rep candidate pool (816) is thinner per target; solve still succeeded.

## 5. Promotion-gate arithmetic (numbers only; no verdict)

Gate (candidate text): "Fully charged exponent trend < 0.49; or ≥ 4× LA+storage reduction at equal recovered targets sustained across three sizes."

**(a) Charged exponent trend** — proxy C = N·c_eval + LA + storage, c_eval = 1, LA(r) = r³.
Baseline C₀ = N + r_full³ + N; B3 C₁ = N + Σ r_λ³ + orbits_hit. Least-squares slope of log C vs log p over the three sizes:

| seed | C₀(211) | C₀(1009) | C₀(4099) | slope₀ | C₁(211) | C₁(1009) | C₁(4099) | slope₁ |
|---|---|---|---|---|---|---|---|---|
| 20260717 | 4864 | 2172 | 1787 | −0.341 | 8686 | 7175 | 5591 | −0.148 |
| 20260718 | 6028 | 1944 | 1811 | −0.412 | 9306 | 4542 | 5604 | −0.177 |
| 20260719 | 4096 | 1396 | 3344 | −0.080 | 8273 | 4238 | 11330 | +0.096 |
| mean | 4996 | 1837 | 2314 | −0.267 | 8755 | 5318 | 7508 | −0.057 |

Toy-proxy caveat (rule 7): with k fixed per size, N ∝ (2k)⁴/p falls with p (measured N-scaling slopes −0.66, −0.74, −0.48), so these slopes measure toy relation-density decay, not asymptotic LA scaling. No crypto-scale exponent claim is supported either way.

**(b) LA + storage reduction at equal recovered targets**
- LA factor (all-blocks accounting) = r_full³ / Σ r_λ³ = **0.25 exactly at all 9 cells** (Σ r_λ³ = 4·r_full³ because exactly 4 blocks survive, each with r_λ = r_full). Under this accounting, block LA is a 4× loss.
- LA factor (single-sufficient-block accounting) = **1.0** (any one surviving block spans the full column space when r_full = k; blind-descent full-column-rank flags: p=211 all seeds TRUE for the 4 surviving blocks; p=1009 seed …17 TRUE; other cells r_full < k, flags FALSE — rank limited by distinct-row collapse, not by block structure).
- Storage reduction (orbit compression) = N/orbits_hit: p=211: 7.61×, 8.81×, 6.69×; p=1009: 5.41×, 6.74×, 4.95×; p=4099: 5.85×, 6.00×, 5.56× — ≥ 4× at every cell. Null-model compression at matched N: 4.3–4.5× (p=211), 1.30–1.41× (p=1009/4099) — the EC compression beyond null is the S₃-collapse of observation 2 and is exactly what ordinary symmetrization already harvests.
- Combined (all-blocks) = LA factor × storage reduction = 1.24–2.20 (all cells < 4).
- Combined (single-block) = 1.0 × storage = 4.95–8.81 (all cells ≥ 4), but the LA component contributes no reduction and the storage component is the pre-existing symmetrization factor (candidate's own red-team line: "B3 ≡ FHJRV symmetrization with bookkeeping").
- **Equal recovered targets**: DLP baseline vs orbit-scan — 9/9 instances, both modes recovered the exact seeded secret every time (secrets 165, 152, 2 / 237, 920, 258 / 1261, 920, 1282). Equal: YES.

## 6. Scope and limitations

Toy primes ≤ 2^12, m = 4 only, single-target fibers per seed, prime-order curves chosen by deterministic rule, FB = smallest-x rule (k = 12, 12, 16), 3 seeds, 8 null draws/seed. The relation indicator is S₃-invariant by construction, so the 4-surviving-block pattern is expected to persist for m = 4; whether the pattern and the rank-equality persist at other m or crypto scale is untested. Negatives close only the tested scope (these primes, this FB rule, this group action, this operationalization of "relation space" as the fiber indicator inside the ambient permutation module — see specification.yaml operationalization_note).

## 7. Files

- specification.yaml (frozen protocol, Coordinator-staged)
- eqj1_isotypic.sage (experiment), eqj1_verify.sage (independent audit)
- runs/RUN-EQJ-001-{a,b,c}/{manifest.yaml, raw.json, stderr.txt}
- dev_test_p211.json, dev_test_p211.stderr.txt (pre-official validation run, kept for the record; identical code, p=211)
