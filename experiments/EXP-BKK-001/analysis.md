# EXP-BKK-001 analysis — Newton polytopes, mixed volume, sparse-vs-dense solve cost of the target-sectioned Semaev family (candidate B2, TASK-20260717-B2)

**Runs:** `RUN-BKK-001-a` (m=3,4; p∈{101,431,1009}; 3 seeds), `RUN-BKK-001-b/c/d` (m=5; p=101/431/1009; 3 seeds). All valid. 27 configs × 2 targets = 54 measured instances. No timeouts, no kills (run walls 16.2 s / 261.9 s / 249.4 s / 220.4 s, all < 600 s; total ≈ 748 s of 2400 s budget). Implementation: exact evaluation–interpolation construction of the Semaev recursion over F_p with instrumented F_p-op counting; exact Newton polytopes via pulling triangulation, cross-checked against Sage `Polyhedron.volume()` (agreement everywhere).

## Stage 0 — supports, Newton polytopes, MV vs Bézout (primary)

Bézout baseline (frozen in specification): multigraded dense count `B_m = n!·D^n`, `n = m−1`, `D = 2^(m−2)`. `MV = n!·Vol(Δ_m)` (BKK identity). `ρ_m = MV/B_m`.

| m | n | D | box (D+1)^n | support size (54-instance range) | fill range | polytope Δ_m (all 54 instances) | MV | Bézout n!·D^n | ρ_m |
|---|---|---|---|---|---|---|---|---|---|
| 3 | 2 | 2 | 9 | 9–9 | 1.000 | full box [0,2]² | 8 | 8 | **1 (exact)** |
| 4 | 3 | 4 | 125 | 119–125 | 0.952–1.000 | full box [0,4]³ (Vol 64; hull path, pulling = Sage volume) | 384 | 384 | **1 (exact)** |
| 5 | 4 | 8 | 6561 | 6417–6561 | 0.9781–1.000 | full box [0,8]⁴ (Vol 4096; 24-simplex pulling = Sage volume) | 98304 | 98304 | **1 (exact)** |

- Per-variable max degree = D and total degree = n·D in every instance (diagonal monomial present).
- Support symmetric under S_{m−1} in every instance.
- **Union (generic family) support = the full box at every (p, m).** Per-instance monomial losses (up to 144 at m=5, e.g. the three axis monomials at one m=4 instance) are instance-specific coefficient cancellations; 393 distinct monomials were ever missing at m=5-main, each in exactly one instance — they never touch box corners, so the hull is invariant.
- At p=1009 all six m=5 instances have full-box support (6561/6561).
- Unsectioned T₄ support is 439/625 (70.2%) — the *unsectioned* family polynomial is materially sparser; target-sectioning fills the support (recorded as an observation; the candidate's object is the sectioned system).
- `log MV / log Bézout` at m=5 = log(98304)/log(98304) = **1.0 exactly** (candidate's cost-model invariant; win requires < 1 strictly).

## Solve stage — sparse vs dense, counted F_p ops (means over main targets)

| m | C_dense construction | C_dense FB-eval | C_sparse construction | C_sparse FB-eval | C_sparse/C_dense total |
|---|---|---|---|---|---|
| 3 | 18 | 3,456 | 1,208 (measured) | 3,600 | **1.384** |
| 4 | 23,685 | 310,000 | 1,414,498 (measured) | 433,000 | **5.537** |
| 5 | 3,102,272 | 60,456,960 | fallback_analytic (K³/3 ≈ 9.4×10¹⁰ est., |supp| > 200, predeclared; charged = dense) | 121,789,554 (2.02× dense) | **1.000** (by fallback charge) |

- Sparse support-aware machinery is **strictly more expensive** than the dense tensor-structured route wherever measured (m=3: 1.38×; m=4: 5.54× total; evaluation alone up to 2.02× at m=5): at near-box fill, the generic |supp|-system solve costs K³/3 vs nested Newton's 2(D+1)^(n+1), and support-restricted evaluation loses to dense nested Horner.
- Solve-cost exponents (least squares of log C vs log(D^n) over m∈{3,4,5}): e_dense = 1.404, e_sparse = 1.328, ratio = 0.946 — **an artifact of the predeclared m=5 fallback charge (sparse ≡ dense), not a sparse win**; per-m ratios above show the sparse route never beats dense in any measured instance. Dense composed-resultant construction scales ×131 from m=4 to m=5 vs ×64 for D^n.
- Relation supply: algebraic solution sets are **identical** to the direct harvester in all 54 instances (POS-1), so relation probability is provably unchanged by the solver route.

## Controls

- **POS-1** (solution sets identical to ledger-style m-summation harvester): 54/54 pass (dense == harvest and sparse == harvest; m=3,4 also sparse-constructed polynomial).
- **POS-2** (sparse route reproduces dense polynomial coefficient-wise): 36/36 pass (m=3,4).
- **POS-3** (interpolation machinery recovers closed-form T₃): pass, every run (selftest).
- **POS-4** (witness target nonempty): 27/27 pass.
- **POS-5** (polytope machinery self-test on known volumes; ≥2 methods agree): pass, every run; pulling triangulation == Sage volume in all 36 hull-path computations.
- **NEG-1** (random same-support systems have the same MV): 54/54 pass — MV sees only the support hull, so any MV-based win would be generic sparse-system machinery, not EC structure.
- **NEG-2** (random same-support systems solve with identical op counts): 36/36 pass on op counts. **Deviation (minor):** in 2/36 cases (p=1009 m=3 seed 20260717 main; p=1009 m=4 seed 20260718 main) the "solution sets differ" sanity was vacuous because both sets were empty over the FB (expected at d^n ≪ p); post-run verification confirmed the random systems differ from the EC systems in **every** coefficient (9/9 and 125/125). Op-count equality held in both cases.

## Promotion-gate arithmetic (candidate's own thresholds; numbers, not a verdict)

- **G1:** ρ₅ = 98304/98304 = **1 (exact)** ≥ 0.95 ⇒ the candidate's **disproof-track arithmetic is triggered** (Newton saturation ⇒ MV = Bézout). Promotion would have required ρ₅ ≤ 0.85.
- **G2:** measured solve-exponent ratio e_sparse/e_dense = 0.946 under the predeclared fallback charge — not a sparse win (per-m op ratios 1.38×/5.54×/1.00× against sparse; at m=5 the sparse generic construction is infeasible and was charged equal to dense). The candidate's cost-model invariant log MV / log Bézout = 1.0 exactly at m=5, so the sparse cost driver MV^O(1) has the *same* exponential driver as the dense D^O(m) for any BKK-based algorithm, including unimplemented ones (polyhedral homotopy).
- **G3:** relation supply unchanged (POS-1) and solver cost ratio = 1 ⇒ charged-exponent change = 0 ⇒ no trend below 0.49; the dense composed-resultant driver (MX-1478 fit 1.979) is unchanged.

## Deviations and infrastructure notes

1. NEG-2 vacuous-set cases (2/36) — see Controls; op-count equality and coefficient-difference verified.
2. m=5 sparse construction used the predeclared `fallback_analytic` mode (|supp| ≈ 6.4–6.6k > 200); the K³/3 ≈ 9.4×10¹⁰ figure is an analytic estimate, labeled as such, not a measured run.
3. Development smoke runs: three single-config debugging runs (m=3/4/5, p=101, seed 20260717, output to /tmp, not retained as evidence) preceded the official runs; they exposed and fixed three implementation bugs (S₃ sign error, duplicated 2b term, interpolation basis overrun). The official evidence runs are RUN-BKK-001-a..d only (rule 5: development failures are not evidence either way).
4. git HEAD moved during the session (task-start 9cbe0049…, post-run 09ccb38b…, dirty tree both times; recorded in manifests). Runs are self-contained in the preserved script + Sage 10.9.
5. Toy instances have composite group orders (recorded per config in raw.json) — inherent to the candidate's own toy-prime protocol.

## Scope note (rule 7)

All primes are toy (p ≤ 1009, m ≤ 5, D ≤ 8). The measurement "Δ_m = [0,2^(m−2)]^(m−1) at m ∈ {3,4,5} over the tested instance distribution" closes exactly that scope; it is consistent with — but does not prove — the candidate's disproof-track Newton-saturation theorem for all m. It says nothing about crypto-scale fields.
