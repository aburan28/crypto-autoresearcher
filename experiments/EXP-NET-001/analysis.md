# EXP-NET-001 analysis — elliptic-net (EDS) Somos-collision sieve vs BSGS

**Run:** `RUN-NET-001-a` (**valid**). Candidate B1 (`research_directions_20260717.md` line 243).
Protocol: `specification.yaml`. Raw data: `runs/RUN-NET-001-a/raw.json`.
Tables below are produced by `analyze_run.py` (canonical analysis script, kept in this directory).
Toy primes `p ∈ {101, 431, 1601}`, seeds `20260717..20260722` (18 main instances),
`B = ⌈√n⌉`, FB = net terms `{W_P(i), W_Q(i), i ≤ B}`, `Q = kP`, k seeded.
Op unit: 1 F_p multiplication (inversion = 10, comparison = 1), identical accounting for sieve and BSGS reference (specification `op_accounting_policy`).

## Controls

| control | outcome |
|---|---|
| PC1 pairing (Stange, net recomputation == Sage) | **PASS 3/3**: reduced Tate `[W(n+1,1)/W(n+1,0)]^((p−1)/n)` == `P.tate_pairing(Q,n,1)`; n = 5 (p=101), **43** (p=431), 5 (p=1601); all non-vacuous (τ ≠ 1). Rank-2 net built from executor-derived initial values `W(2,1) = x_P − x_{P+Q}`, `D(3) = 4y_P·y_{P+Q} − (x_Q−x_P)W(2,1)²`, closed rows-0/1 recurrence (verified against Sage; derivation in final report). |
| PC2 net exactness | **PASS 18/18**: x(mP) group identity (8 samples/instance), EDS translation identity `W_{kP}(i)·W_P(k)^{i²} = W_P(ik)` (all i ≤ B), Somos identity (8 samples/instance). |
| NC1 independent curve | **PASS**: cross-sieve products enrichment per instance 0.47–1.52, totals ≈ 1.1 — no systematic sieve artifact (counts are small; noisy). |
| NC2 permuted target | **behaves as designed** (see below): `|S|=1` false-yield relations appear at comparable rates without any k-structure. |
| NC3 random oracle | **PASS**: enrichment 1.043 / 0.976 / 1.057 per size — birthday denominator validated. |
| k ∈ S assertion | never failed on any analyzed collision (implementation self-check). |

Deviation (recorded in raw.json `deviations` and EV record): PC1 uses reduced **Tate** pairing instead of Weil — toy fields host no independent rational n-torsion pair (n² > #E at these p); both are Stange (Pairing 2007) net formulas. MAXC=600 deterministic stride sample for the k-consistency analysis (counts reported for the analyzed sample). Script placed at `experiments/EXP-NET-001/` per the handoff ID mapping (candidate text proposed `experiments/ecdlp_net/`).

## Main measurements (S2 = pairwise-product scope)

| p | obs collisions | birthday exp | enrichment | Q-involving | analyzed | universal | yielding (|S|=1) | permuted yielding |
|---|---|---|---|---|---|---|---|---|
| 101  | 1564 | 1407.4 | **1.111** | 1450 | 1450 | 228 | 204 (0.141/analyzed) | 154 (0.183/analyzed) |
| 431  | 1958 | 1631.9 | **1.200** | 1862 | 1202 | 161 | 218 (0.181/analyzed) | 204 (0.214/analyzed) |
| 1601 | 6186 | 5881.4 | **1.052** | 5804 | 2435 | 192 | 722 (0.297/analyzed) | 248 (0.121/analyzed) |

Per-family-pair enrichment (totals, 18 instances): PPPP 1.02, PPQQ 1.02, PPPQ 1.12, QQQQ 1.15, PQQQ 1.15, PQPQ 1.03.
Large-n subset (n ≥ 400, 5 instances): 7487 / 7010.4 = **1.068**.
Random-oracle control at identical sizes: 1.043 / 0.976 / 1.057. The mild excess in the QQ/PQ families is the measured **index-1 tautology class** (W(1) = 1 makes index-1 products equal to single terms — the 581 `universal` collisions, confirmed k-independent by the consistency analysis).

**Collision statistics therefore track the random-oracle birthday model across sizes** once the universal tautology class is accounted; no sub-birthday relation supply was measured.

## k-recovery vs BSGS at equal op budget

Charged per protocol policy. `ops_opt` = FB + enumeration + full-EDS verification precompute + **one** collision scan (optimistic fiction: first collision checked yields k); `ops_full` = scan of all analyzed Q-involving collisions. BSGS reference = `2⌈√n⌉·16 + ⌈√n⌉·⌈log₂⌈√n⌉⌉`.

| p | exp (optimistic) | exp (full scan) | BSGS exp (same accounting) | mean ops_opt / ops_BSGS |
|---|---|---|---|---|
| 101  | 2.025 | 2.802 | 1.317 | 24.2 |
| 431  | 2.025 | 2.595 | 1.311 | 38.6 |
| 1601 | 1.972 | 2.406 | 1.174 | 134.7 |

The sieve's cost disadvantage over BSGS **grows with size** (ops ratio ≈ 24 → 39 → 135 over the three sizes; per-instance up to 298 at n = 1607). Even the free-verification fiction (FB + enumeration only, 3B² products ≈ 3n mults) has exponent 1.70 / 1.71 / 1.59 per size. Note honestly: at toy sizes even BSGS's charged exponent is 1.0–1.5 because the constant 32 mults/point-op dominates log(ops)/log(n); the gate's 0.49 is an asymptotic statement and is not literally reachable by any method at these n — the comparable quantities are the sieve-vs-BSGS ratio at equal accounting and its trend, both measured above.

**Promotion-gate arithmetic (numbers only, no verdict):**
- Gate 1, "k-recovery charged exponent trend < 0.49": measured 1.97–2.03 (optimistic), 2.41–2.80 (full scan), and 1.59–1.71 (enumeration-only fiction). All ~4–6× above 0.49; sieve/BSGS ops ratio grows with n.
- Gate 2, "net-relation rank per field op ≥ 2× BSGS-equivalent": measured 0.045 / 0.046 / 0.024 per size — 40–80× **below** the threshold.

## Why yielding relations do not help (the obstruction, measured)

1. `|S| = 1` ("k-yielding") collisions are **birthday artifacts**: the permuted-target control produces them at comparable rates (0.121–0.214 vs main 0.141–0.297 per analyzed collision; at p = 101 and p = 431 the permuted rate is *higher*). The main-vs-permuted excess at p = 1601 is the expected conditioning artifact: main collisions are guaranteed ≥ 1 consistent k' (the true k) by construction, permuted ones are not (most have |S| = 0).
2. Consistency sets are **large**: mean |S| = 11–68 across instances (naive random model predicts ≈ 1 + n/p ≈ 2). EDS index periodicity plus the `W_P(k')^{Δ}` scale factor make value collisions systematically k-unspecific — a quantitative form of the candidate's "relations encode the group law, not k" obstruction, extending beyond the index-1 universal class.
3. Using any relation requires the Ω(n) candidate scan (`15(n−1)` ops per collision plus `6B(n−1)` precompute) — this verification floor alone gives exponent → 1.5, before enumeration.

## Unexpected observations (contract rule 8)

- **NC2 collision-count asymmetry**: permuted nets produce only 0.52–0.70× as many Q-involving collisions as true k-structured nets at equal multiset sizes (per-instance ratios in raw.json, e.g. 2023 vs 3388 at n = 1607). This is a genuine k-dependence of the product-value distribution (origin not resolved here: systematic product-level identities vs small-period effects); it does **not** convert into cheap recovery (points 1–3 above).
- Two small-n p = 1601 instances (n = 43, 47) show S2 enrichment 4.7–5.6: fully accounted by the index-1 tautology class at B = 7 (15 of 16–19 collisions universal), not by new structure.
- Two crashed invocations during development (RNG `TypeError` from Sage Integer seeds; `UnboundLocalError`/`ZeroDivisionError` from a variable shadowing `r4` and a Q = −P pairing-control sample) — infrastructure failures producing no data, fixed before RUN-NET-001-a; the intermediate raw.json had floor-corrupted float fields (Sage `round` semantics in `.sage` files) and was regenerated. Raw integer counts of the final run were bit-identical across the two complete runs (determinism check).

## Scope and limits (contract rules 6, 7)

Toy prime fields (p ≤ 1601, n ≤ 1607), 6 seeds, one BSGS-equivalent B per instance, EDS in division-polynomial normalization, stated op policy. Negative language per `docs/evidence-and-reproducibility.md`: **no improvement meeting the predefined threshold was observed over the tested instances, parameters, solver, and resource budget.** This closes only the tested scope: it does not address other net parameterizations, other B regimes, rank ≥ 2 nets as relation source, or any crypto-scale claim. The proof-track question (relation module of Somos identities restricted to k-fibers) remains open theory; the measured large-|S| degeneracy is consistent with it.
