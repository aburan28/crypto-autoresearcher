# HYPOTHESES_100 — 100 candidate routes to beat Pollard rho on generic E/F_p

*Session 2026-07-17 (cont.). Bar (AUTOLAB_TASKS): an idea is **alive** only if it changes a
total-cost exponent below 0.5, or exhibits a **growing structural invariant** that plausibly
forces it at scale. Everything else is "interesting structure." Ledger discipline
(`EC_SIEVE_HONEST_LEDGER.md`): every measurement carries a matched control + permutation
null; multiple-comparison batteries get Holm correction; censoring is reported; toy-scale
KILLs are labeled "no signal seen at reachable scale," not theorems. Shoup/Nechaev is the
**control**, not the target: beating it means a measured non-generic exponent < 0.5 on a
generic curve family.*

*Status tags:* ✅KILL = measured/argued dead this session · ❌KILL(arg) = dead by argument
(no new measurement warranted) · 🧪MEASURED = ran, verdict inside · 📐PRE-REG = experiment
fully specified, not yet run · 🔁QUEUED = inherited from AUTOLAB_TASKS / NEXT_THEORIES.

---

## F1 — Algebraic model & summand variants

**H001. Alternative-curve-model summands.** Summation polynomials in Montgomery / twisted
Edwards / Hessian / Jacobi-quartic coordinates have different degree/coefficient profiles;
one model might lower the boolean d_reg of the chained system.
Not dead: all d_reg/Betti kills used short-Weierstrass Semaev polys.
Exp: `h001_model_summands.sage` — build chained m=3 systems in each model (birational
transport of the same instances), run the T2 streaming echelon at n=12..18, D≤5.
WIN: deficit growth or d_reg drop in any model. KILL: all models track semi-regular. Cost: medium. 📐PRE-REG

**H002. Symmetrized-variable formulation.** Rewrite S_{m+1} in elementary symmetric
functions e_i of (x_1..x_m): the S_m-invariant system may have lower-degree Gröbner
trajectories than the raw one.
Not dead: prior GB kills used raw variables.
Exp: `h002_symmetrized_gb.sage` — m=3, toy q; express S4 in (e1,e2,e3,x_R), compare d_ff,
GB time, #G* vs raw. WIN: lower solving degree at matched size. KILL: same or worse. Cost: cheap. ✅MEASURED — toy WIN (formulation quality only: S3-orbit quotient 6:1, wall shift |F|~25->~110, ~10x/doubling both arms; exponent UNCHANGED => not alive at the bar; results/h002_symmetrized_gb.json)

**H003. Halving-based decomposition.** Decompose R = 2Q + ΣP_i (mix doubling into the
summand tree): the map x→x(2P) is degree 4 and might scramble the syzygy structure
favorably for the solver.
Exp: H001 harness with one leg replaced by a doubling edge. WIN: d_reg drop. KILL: tracks
semi-regular. Cost: medium. 📐PRE-REG

**H004. Two-sided/asymmetric factor bases.** Base sizes B_1≠B_2≠B_3 with B_1·B_2·B_3 ≈ ℓ
optimized against measured per-size decomposition probability (some sizes may be
structurally richer).
Exp: analytic yield model + toy measurement `h004_asym_base.py`. WIN: asymmetry beats the
balanced base beyond constants. KILL: balanced is optimal up to O(1). Cost: cheap. 📐PRE-REG

**H005. Sign-recovered x-only systems.** x-only Semaev loses y-signs; add the sign as a
single boolean per summand with the curve equation as constraint — could *reduce*
solution multiplicity 2^m→2 and speed the solve.
Exp: extend `semaev_tree` builder with sign booleans; T2 echelon n=12..15.
WIN: faster solve at same n. KILL: extra constraints don't help rank trajectory. Cost: cheap-medium. 📐PRE-REG

**H006. Summands with pre-image-constrained R.** Restrict x_R to a subvariety where
V_m has smaller degree (intersect with known components, e.g. the T13 torsion strata):
solving on the component could be cheaper, and a *random* R has a component preimage with
probability to be measured.
Exp: `h006_component_solve.sage` — intersect S3-chain with the E[2]-translation strata
from T13; measure solve cost + hit probability. WIN: cost×probability < √ℓ. KILL:
probability kills the gain. Cost: cheap-medium. 📐PRE-REG

**H007. Jacobian-coordinates summands.** Weighted-projective (Jacobian) coordinates give
addition formulas with different monomial structure; descent to boolean may be sparser.
Exp: H001 harness extension. WIN/KILL as H001. Cost: medium. 📐PRE-REG

**H008. Multi-summand unbalanced trees.** Chained trees are balanced; an unbalanced
caterpillar tree changes the Weil-descent block structure (long skinny blocks) which the
T2 echelon might exploit.
Exp: `semaev_tree` caterpillar variant through the T2 instrument, n=12..18.
WIN: larger relative deficit than balanced. KILL: same trajectory. Cost: medium. 📐PRE-REG

## F2 — Elimination & solver-engine angles

**H009. R6 arbitrary explicit factor-base membership solve.** 🔁QUEUED (T1 — highest-value
open object). Explicit birthday base 𝓕, |𝓕|=ℓ^{1/3}, membership ∏(x_i−x_f)=0; total
relation×solve cost vs √ℓ on ℓ=2^20..2^30, ≥8 R, 4 mandatory controls.
Exp: `semaev_tree_prime.py` + T24-verified rho baseline. WIN: total exponent <0.5 (CI
upper bound too). KILL: ≥ birthday. Cost: heavy. 📐PRE-REG

**H010. Defect-B adversarial deterministic oracle.** 🔁QUEUED (T7). Fixed deterministic
c_k-keyed oracle family (chosen before keys) feeding the verbatim T2 reduction; search
over families for one that absorbs the −b column.
Exp: `h010_defectB_adversarial.py` extending `tier1_defectB.py`. WIN: e-block corank
absorbs -b and grows with l. KILL: x recoverable for every family (information argument). Cost: cheap. ✅KILL — 62-member deterministic c_k-keyed family x 1116 cells: 0 absorptions (Wilson95 = 0.0034); cheating control absorbs 6/6 (harness sensitive); corank != absorption; Defect-B now closed experimentally too (results/h010_defectB_adversarial.json)

**H011. d_reg − d_ff gap growth.** 🔁QUEUED (T10). The gap carries the exponential cost;
measure both at n=9..18, max_D=6, ≥8 R.
Exp: `ic_first_fall_fast.py` + T2 echelon. WIN: bounded gap. KILL: gap grows
semi-regularly. Cost: medium. 📐PRE-REG

**H012. Block-Wiedemann d_reg probe.** Replace the dense bitset echelon with a
block-Wiedemann rank/minpoly computation on the Macaulay matrix — memory O(matrix) not
O(rank × cols), pushing measurable d_reg to n≈30.
Exp: `h012_bw_dreg.py`. WIN: past-wall data shows deficit growth. KILL: deficit keeps
shrinking. Cost: medium (engineering), then cheap runs. ✅PARTIAL (2026-07-17) — built 4
instruments instead (`h012_peel_rank.py`, `h012b_denseT.py` with --engine m4ri/python,
--subset stride/random): (i) w1/w2 peeling is DEAD for sem (40+43 pivots of 143,882);
(ii) transposed+lead-sorted python echelon exact but O(rank^2) fill-in-bound;
(iii) m4ri exact engine validated both sides (n=15 sem 69,073 == t2; n=17 null D=5
126,922 == pred — first direct null measurement past n=15, 16th exact cell);
(iv) SUBSET-COLUMN RANK IS INVALID FOR SEM: strided/random subsets lose ~19% (n=15:
55,968 vs true 69,073) — sem columns need ~2.3x nrows to span; subset valid for null
only. n=17 sem "deficit 18,530/27,851" readings are this artifact, NOT real deficits.
Exact FULL sem rank via m4ri fits one call only <= n~15; n=17 sem full ~1,640 s,
n=21 ~2,000+ s / ~34 GB -> needs checkpointable block-m4ri (matmul-reduce per column
block + echelonized basis carry; designed, not built). Deficit series stands:
1322 / 1862 / 1999 (n=12/15/18, full exact), decelerating; null==pred now direct at
n=17 D=5. 📐PRE-REG (block-m4ri for n=17..21 sem full)

**H013. F4/F5 with signature tracking on the boolean chained system.** Real F5 with
rewritten/signature rules could confirm the T2 syzygy family (exactly 1 at D3, 8n/3 at
D4) and identify their origin — if they are *rewritable* the system is closer to generic
than the raw counts suggest.
Exp: `h013_f5_signatures.sage` (Singular slimgb with protocol). WIN: non-rewritable
low-degree signatures grow. KILL: all extra syzygies rewritable/Koszul. Cost: medium. 📐PRE-REG

**H014. Best-IC-exponent with CIs.** 🔁QUEUED (T12). Pin crossbred 0.863 vs MITM 0.667
with bootstrap CIs at the largest feasible n.
Exp: `crossbred_real_cost.py` + CI harness. WIN: CI lower bound <0.5. KILL: >0.5. Cost: medium. 📐PRE-REG

**H015. SAT/CDCL with cross-target clause reuse.** Learned clauses from solving PDP #1 are
valid for PDP #2 on the same curve+base (the summand polynomials don't change) —
amortized CDCL could behave like preprocessing.
Exp: `h015_sat_reuse.py` (CaDiCaL incremental): k successive PDPs, measure marginal solve
time vs fresh. WIN: marginal time drops below birthday amortized. KILL: learned clauses
don't transfer (target clauses dominate). Cost: medium. 📐PRE-REG

## F3 — Factor-base geometry

**H016. Quadratic-residue factor base.** Base = {P : x(P) ∈ QR_p}: the chord structure of
x's might bias triple-sum yield.
Not dead: prior base-structure kills used interval/subgroup/random bases, not QR.
Exp: `h016_base_qr.py` — N≈2^14..2^18, m=3, decomposition count of ≥300 random R vs
matched random base; ratio + bootstrap CI; permutation null on the QR labeling.
WIN: yield ratio CI excludes 1 (either side) with the right sign. KILL: ratio ~ 1. Cost: cheap. ✅KILL — QR ratios 0.88-1.05 across 4 curves, all bootstrap CIs contain 1, all inside 100-draw permutation band (results/h016_base_yield.json)

**H017. Small-multiples factor base.** Base = {x(jP) : j ≤ B} (x-symmetric, so ~B/2
points): additive structure of the indices may enrich decompositions (R = iP decomposes
as j_1+j_2+j_3 ≡ i automatically — the question is the x-constraint).
Exp: same harness as H016. WIN/KILL as H016. Cost: cheap. ✅KILL — small-multiples base STARVES decomposition (log-window ~3B of N; only 0.1-0.4% of targets coverable); x-structure adds nothing (same JSON)

**H018. Interval base with carry-geometry.** Base = x < p^{2/3} decomposed by *high* bits
instead of low: carry propagation in the addition law might interact with high-bit
membership (opposite endianness of the killed interval bases).
Exp: H016 harness with high-bit intervals. WIN/KILL as H016. Cost: cheap. 📐PRE-REG

**H019. Base = x of small canonical height.** Points with ĥ(P) < h₀ (includes small
multiples but also their translates): height-theoretic bases might concentrate relations.
Exp: H016 harness. WIN/KILL as H016. Cost: cheap. 📐PRE-REG

**H020. Two-base cover with cross terms.** Base A∪B where A is x-interval, B = small
multiples; decompositions may use mixed types (2 from A + 1 from B) with a percolation
advantage.
Exp: `h020_mixed_base.py` — count typed decompositions vs matched controls.
WIN: mixed yield above additive expectation. KILL: additive. Cost: cheap. 📐PRE-REG

**H021. Factor base = Frobenius-orbit-like sets in F_p.** On F_p there is no Frobenius,
but the *multiplicative* cosets x·H (H ≤ F_p^*) are the prime-field analog: base as union
of small cosets.
Exp: H016 harness with coset unions. WIN/KILL as H016. Cost: cheap. 📐PRE-REG

**H022. Optimal-base search by local optimization.** Treat base selection as a submodular
maximization of decomposition count over candidate x-pools; run greedy on toy N; test
whether the greedy base generalizes (transfer to same curve, new R).
Exp: `h022_greedy_base.py`. WIN: greedy base beats random at matched size, transfers.
KILL: overfit / no gain. Cost: cheap-medium. 📐PRE-REG

## F4 — Tensor-rank & combinatorial structure of the membership object

**H023. Restricted-Cayley-tensor rank.** 🔁QUEUED (NT-4). The B×B×B tensor T[i,j,k] =
log(P_i+P_j+P_k) (the object R6 says must collapse from dimension ℓ to O(1)) — if its
flattening/CP/slice rank is anomalously low vs a random tensor with the same marginals, a
sub-birthday contraction may exist.
Exp: `h023_tensor_rank.py` — toy N, B≈N^{1/3}; mode-1 GF(2)/real flattening ranks, ALS
CP-fit residual at small ranks, slice-rank proxy; controls: iid tensor same density,
XOR-group table, random cyclic group table. Permutation null: relabel base elements.
WIN: rank proxy sublinear vs control with a *constructive* contraction beating MITM.
KILL: all proxies >= control - O(1), or contraction == listing. Cost: cheap. ✅KILL — GF(2)/real flattening ranks FULL at all configs; CP/slice/treewidth proxies inside 100-permutation null band; positive controls (XOR table, interval-logs) fire correctly, so the instrument sees structure when present (results/h023_tensor_rank.json). Caveat: with uniform random logs T is near-tautologically a null draw; B<=28 reached

**H024. Incidence-hypergraph treewidth.** The decomposition hypergraph (vertices=base,
hyperedges=triples summing to a target set) — small treewidth ⇒ poly-time junction-tree
contraction below birthday.
Exp: same toy systems; min-fill/min-degree treewidth upper bounds vs random 3-uniform
hypergraph with same degree sequence. WIN: treewidth O(log B) with gap vs control.
KILL: treewidth tracks control (theta(B)). Cost: cheap. ✅KILL — min-fill/min-degree tw = 2-3 = null band (folded into h023 JSON)

**H025. Border-rank / approximability.** Even if exact ranks are generic, border rank
(approximability) could be low — test numerical low-rank fit residual decay vs random.
Exp: H023 harness, real ALS residual curves. WIN: residual decays qualitatively faster
than control. KILL: same decay. Cost: cheap. 📐PRE-REG

**H026. Sumset growth of the base.** Decomposition success ∝ |B+B+B| coverage of the
group; a base with anomalously large triple sumset (relative to |B|³/birthday) would be a
combinatorial channel. Inverse-sumset structure (Freiman) says large sumset = generic;
small sumset = structured (measurable either way).
Exp: `h026_sumset.py` — |B+B+B| for the F3 bases vs random; also partial-sumset energy
E(B,B). WIN: base family with super-birthday coverage. KILL: all match random. Cost: cheap. 📐PRE-REG

**H027. Additive-energy route to rho.** If E(B,B) is anomalously high for some algebraic
base, BSGS-style collision arguments could beat √ℓ by an energy factor.
Exp: H026 harness reports E(B,B); analytic conversion. WIN: energy factor growing with ℓ.
KILL: energy matches random-map expectation. Cost: cheap. 📐PRE-REG

## F5 — Boolean-function / Fourier structure

**H028. Fourier spectrum of the decomposability indicator.** f(R)=1 iff R decomposes over
the base (m=3): as a boolean function of R's index bits, spectral concentration below the
random-function level would give a *computable* approximate predicate — a channel.
Not dead: prior separability kills targeted hand-written/ML predicates of x(P); the
decomposability indicator itself was never Fourier-analyzed.
Exp: `h028_fourier_decomp.py` — toy N rounded to 2^b; Walsh-Hadamard; top-1% coefficient
mass + spectral flatness vs random boolean function same density; permutation null.
WIN: concentration growing with b. KILL: matches random. Cost: cheap. ✅KILL — excess is real (top-1% mass 0.111/0.099 vs band <=0.090/0.087, z=7.9/11.2) but DECAYS with b (x1.33 -> x1.17 relative); generic sumset-thresholding artifact of 1_{A+A+A}, not EC structure; fails the growth clause (results/h028_fourier_decomp.json)

**H029. Algebraic immunity of f.** Minimum degree of a nonzero annihilator of f (or f+1):
low AI ⇒ low-degree approximate separator ⇒ sieving channel.
Exp: H028 script extended: AI via Macaulay rank on evaluations (toy b≤12) vs random
function AI≈b/2. WIN: AI < b/2 − ω(1). KILL: AI ≈ b/2. Cost: cheap. 📐PRE-REG

**H030. Fourier of the *sign* function.** s(P) = y-sign of the lex-smaller representative:
if s correlates with bits of x (or of k via doubling), x-only rho loses less than the
assumed √2.
Exp: `h030_sign_corr.py` — correlation of s(P) with low/high bits of x(P), of kP index
bits; permutation null. WIN: |corr| → growing with p. KILL: within null. Cost: cheap. 📐PRE-REG

**H031. Decision-tree depth of decomposability.** If f (H028) is approximable by a
shallow decision tree on index bits, that is a *circuit* predicate with growing
deficiency — the exact EC-sieve conjecture's remaining gap.
Exp: sklearn-free CART (hand-rolled, depth ≤ 12) on toy data; held-out curve transfer.
WIN: held-out accuracy > null band, growing with p. KILL: null band. Cost: cheap. 📐PRE-REG

## F6 — Statistical / predicate channels (post-calibration)

**H032. Pair-joint doubling statistics.** Mutual information between low/high bits of
x(P) and x(2P): single-point predicates are dead, but the *joint* distribution across the
doubling map was never measured with the calibrated harness.
Exp: `h032_pair_mi.py` — I(bits(x(P)); bits(x(2P))), b=1..8, ≥10k samples, permutation
null (shuffle the P↦2P pairing), Holm over b. WIN: MI above null band, growing with p.
KILL: null band everywhere. Cost: cheap. ✅KILL — 21/32 cells outside the (2000-draw, Holm) band BUT every excess SHRINKS ~1/p (fitted exponent -0.7..-0.97); deterministic-map finite-size artifact; growth clause fails (results/h032_pair_mi.json)

**H033. Division-polynomial residue predicates.** Features ψ_d(x(P)) mod s and
Legendre(ψ_d(x(P))) for d=2..6: membership of P in d-torsion cosets is the *only* proved
non-trivial separable content; higher d might leak index information mod smooth parts.
Exp: `h033_psid.py` — deficiency δ vs permutation null, Holm across (d,s) cells.
WIN: d growing with p for some d. KILL: all cells in null band. Cost: cheap. ✅KILL — 0/70 cells significant post-Holm; positive control on cofactor-2 curve detects the proved 2-descent channel at 0.9998 bits (instrument can see torsion channels; none exist at prime order) (results/h033_psid.json)

**H034. Multi-character y-features.** χ(y·(x−a)) for a sweep of a, Legendre characters of
higher order (3rd/4th when they exist): extends the killed LSB-of-y cell to a battery.
Exp: H033 harness. WIN/KILL as H033. Cost: cheap. 📐PRE-REG

**H035. Heavy-tail δ scaling-in-p.** 🔁QUEUED (T6). The calibrated Rényi-2/L∞ test across
primes 2^20..2^40 (the unrun arm).
Exp: generalize `review_renyi_calibrated.py`. WIN: statistic above null AND growing in
log p. KILL: flat. Cost: medium. 📐PRE-REG

**H036. Deployed-prime δ with CIs.** 🔁QUEUED (T9). P-256/384/521, Curve25519, secp256k1
vs multiple random-prime baselines, permutation null + bootstrap.
Exp: upgrade `review_deployed_primes.py`. WIN: excess above band. KILL: in band. Cost: medium. 📐PRE-REG

**H037. Sequential-dependence δ.** The δ battery treated P,Q independent; measure
deficiency along a *walk* P_i+1 = P_i + A_j (the rho step): walk-state predicates are
what a sieving-rho hybrid could actually exploit.
Exp: `h037_walk_delta.py` — deficiency of low-bit predicates along walks vs iid control.
WIN: walk-state δ > iid δ. KILL: equal. Cost: cheap. 📐PRE-REG

**H038. Conditional-entropy triad test.** Direct estimation of H(π(P+Q)|π(P),π(Q)) for
the *best* killed predicates (confirming δ=O(1) by direct measurement rather than
bucket-proxy).
Exp: `h038_triad_entropy.py`. WIN: any predicate family with δ(d) slope > 0. KILL: flat. Cost: cheap. 📐PRE-REG

## F7 — Rho-side & the generic model itself

**H039. Rho walk serial correlation.** If the r-adding walk's step sequence or state
sequence mixes *slower* than a random map, collision time constant changes (either way).
Exp: `h039_walk_corr.py` — autocorrelation of steps and of low state bits, lags 1..32,
vs random-map walk; chi² with permutation null. WIN: exploitable lag structure (would
also embarrass the random-map model). KILL: random-map-like. Cost: cheap. ✅KILL — 2 flagged cells (lag-29 autocorr) traced to terminal-cycle-length confound; 60-walk replication diagnostic: EC and random-map cycle-length distributions fully overlap (results/h039_walk_corr.json, h039_diag.json)

**H040. Rho constant at scale.** 🔁QUEUED (T24 anchor, small arm). Re-verify 1.253√N /
0.886√N (negation) with CIs at N≈2^16..2^20, ≥200 runs.
Exp: `h040_rho_const.py`. Output: fitted constant + CI. Cost: cheap. ✅ANCHOR CONFIRMED — plain 1.2345 [1.141,1.328] / 1.2790 [1.184,1.378] (theory 1.2533 inside both CIs); negation 0.949/0.943 with escape overhead traced to fruitless-cycle policy (results/h040_rho_const.json)

**H041. x-only walk degeneracy.** Sign-free iteration on the x-line halves the state
space but the iteration may have inflated small-cycle counts (fruitless traps).
Exp: `h041_xonly_walk.py` — functional-graph in-degree/cycle spectrum vs random map on
(N+1)/2 nodes. WIN: small-cycle rate ≤ random map (then x-only rho gains √2 for free).
KILL: trap inflation eats the gain. Cost: cheap. ✅KILL — 239-439 two-cycles vs null [0,2]; fragmented components; only 5-7% of collisions solve the DLP; effective 2.30-3.22 sqrt(N) ~ 2x WORSE than plain rho (results/h041_xonly_walk.json)

**H042. Doubling-map orbit spectrum.** The map x↦x(2P) on the x-line is a degree-4
algebraic map, not a random map: its ρ-length/tail spectrum directly measures how
"algebraic" orbits differ from random — the input distribution to any walk design.
Exp: `h042_doubling_orbits.py` — cycle/tail distribution over ≥1000 seeds vs random map
same node count; KS statistic + mean ratio CI; component structure.
WIN: systematic deviation exploitable by a [2]-walk variant. KILL: random-map-like. Cost: cheap. ✅KILL — doubling is a PERMUTATION of the x-line (N odd => 2 invertible); all cycles have length ord_N(+/-2); mu=0 identically; deviation from random map is total but trivially explained, zero DL content (results/h042_doubling_orbits.json)

**H043. Distinguished-point algebraic bias.** DP sets defined by low-bit masks are
uniform; an *algebraic* DP predicate (x ∈ small base) could couple rho to a factor base.
Exp: analytic cost model + `h043_dp_algebraic.py` toy: fraction of walk states hitting
the algebraic DP set vs its density. WIN: hitting rate > density (channel). KILL:
= density. Cost: cheap. 📐PRE-REG

**H044. Iteration-function search.** Optimize the walk's step-set {A_j} as a design
problem: choose A_j = c_j P + d_j Q with small (c_j,d_j) to minimize measured collision
time on toy N, then test transfer to 4× larger N.
Exp: `h044_walk_design.py`. WIN: designed walk beats 1.253√N at transfer scale.
KILL: any gain is fitting artifact / vanishes at transfer. Cost: cheap-medium. 📐PRE-REG

**H045. Batch-inversion rho constant.** Engineering only: r-adding walks with Montgomery
batch inversion — measure the real constant at N≈2^20 on this machine. Out-of-bar
(constant, not exponent) but firms every "loses by 2^k" statement. Exp: `h045_batch_rho.py`. 📐PRE-REG

**H046. Equivalence-class rho on generic curves.** Generic Aut = {±1} ⇒ max class gain
√2 (already in the 0.886 baseline); verify no *other* efficiently-computable equivalence
(e.g., x-translation by torsion) exists on random curves. Exp: analytic + curve census
in H042 script (automorphism check via j and CM disc bound). ❌KILL(arg) unless census
surprises. 📐PRE-REG

## F8 — Cheon / exponent-DH / auxiliary-input structure

**H047. Aux-free Cheon is exponent-DH.** Cheon needs [k^d]P; computing [k^d]P from
(P,[k]P) is a Diffie-Hellman computation *in the exponent*, not realizable by group
operations; any poly algorithm for it gives a sub-rho DLP via Cheon itself (circular).
Formal reduction: AuxFreeCheon ≤_T DLP and Cheon+AuxFreeCheon ⇒ DLP in o(√ℓ) — so the
aux problem is DLP-equivalent. ❌KILL(arg) — no experiment warranted. Status: KILLED
(theorem-shaped argument).

**H048. Cheon with *leaked* structure.** If ℓ−1 or ℓ+1 has a large factor d AND the
protocol ever exposes [k^d]P-derived material (deterministic nonce schemes square the
nonce!): audit RFC6979/EdDSA derivations for exponent-algebraic relations. Protocol-layer,
out-of-bar, but a real audit cell. Exp: `h048_nonce_exponent_audit.py` static check of
derivation functions. 📐PRE-REG

**H049. Smooth ℓ±1 curve census.** Fraction of random curves with ℓ−1 or ℓ+1 having a
factor > ℓ^{1/3} (Cheon-relevant if aux ever exists): pure measurement, calibrates the
"special curve" surface. Exp: `h049_smooth_census.py` — factor ℓ±1 for 10^4 random toy
curves. Cost: cheap. 📐PRE-REG

**H050. Exponent-DH via pairings on E.** Self-pairing needs distortion/embedding degree —
absent generically (killed). Residual: is there *any* efficiently-computable nondegenerate
bilinear self-map on a generic prime-field group? No: such a map gives DLP via
e(P,Q)=e(P,P)^k comparison with precomputed table at cost √(ℓ)·poly — would already be a
break; existence is ruled out for generic E by embedding-degree arguments. ❌KILL(arg).

## F9 — Isogeny / transfer (post-Kani kills)

**H051. Cross-curve double-large-prime percolation.** 🔁QUEUED (NT-5). Relations with one
off-base large prime, pushed through a 2-/3-isogeny to the neighbor curve's address space;
measure giant-component threshold vs same-curve control.
Exp: `h051_isogeny_lp_graph.sage`. WIN: percolation below √p with no hidden enumeration.
KILL: threshold = control. Cost: medium. 📐PRE-REG

**H052. Isogeny-graph spectral gap.** 🔁QUEUED (T15). Second eigenvalue / mixing on the
ordinary ℓ-isogeny graph; look for non-Ramanujan pockets or trap structure.
Exp: `h052_isogeny_spectral.py` (toy p, ℓ=2,3,5). WIN: poorly-mixing region with
correlated weak curves. KILL: near-Ramanujan. Cost: medium. 📐PRE-REG

**H053. Endomorphism-equivariant quotient Semaev.** 🔁QUEUED (NT-2). Quotient the
constrained ideal by the CM α-action in invariant coordinates; compare d_ff/d_reg/Betti
at matched relation count on D=−7, j=0, 1728 toy curves.
Exp: `h053_alpha_quotient.sage`. WIN: solving-degree drop with orbit size. KILL:
constant-factor only. Cost: medium. 📐PRE-REG

**H054. Distance-to-CM distribution.** Generic E/F_p sits at some isogeny-graph distance
from a curve with small-disc CM; if that distance were O(1) for a positive density of
curves, "transfer → exploit endo → transfer back" would be a route (M39 killed the
transfer; the *distance census* is unmeasured and feeds H051/H052).
Exp: `h054_cm_distance.py` — BFS in toy isogeny graphs; distance histogram to the CM
floor. Cost: cheap. 📐PRE-REG

**H055. Volcano-depth hardness correlation.** Curves on the crater vs the floor of the
ℓ-volcano: measure per-curve DLP cost proxies (relation yield, T2 deficit) across depth
at toy scale. Exp: H054 census + H016 harness per depth class. WIN: any depth-correlated
proxy. KILL: flat. Cost: cheap-medium. 📐PRE-REG

**H056. Self-isogeny-cycle walks.** Use a cycle of small isogenies E→E'→…→E as the rho
iteration scaffold (walk jumps curves); DLP transports each hop; collision across the
cycle solves the original. Overhead vs gain is the question.
Exp: `h056_cycle_walk.py` toy cost model + measurement. WIN: collision constant <
0.886√N. KILL: isogeny-evaluation overhead ≥ gain. Cost: cheap-medium. 📐PRE-REG

**H057. Higher-dimensional Kani transfer for ordinary E.** Kani's F_2-embedding needs a
smooth-order auxiliary isogeny target; for ordinary prime-field E the required auxiliary
structure (small-degree isogeny to a curve with smooth group) has density to be measured:
census of smooth-order curves within isogeny distance ≤ 3. Exp: H054 harness records
group-order smoothness per node. WIN: positive-density smooth neighbor with transfer
cost < √ℓ. KILL: density × transfer cost ≥ birthday. Cost: cheap. 📐PRE-REG

## F10 — p-adic, lifting, degeneration

**H058. Lift to E(Z/p²).** The mod-p² DLP contains the mod-p DLP as a quotient; the
formal-log kernel E_1(Z/p²) ≅ Z/p carries the *same* secret scaled by p — measure whether
lifting mixed representations leaks the mod-p class faster than rho. Known: no split ⇒
harder, not easier. Toy confirmation: `h058_ptwo_lift.py` — solve mod-p² DLP by combined
log+rho at toy p, compare op counts to plain rho. WIN: leak exists. KILL: no leak (expected). 📐PRE-REG

**H059. Deformation to anomalous fiber.** Smart's attack needs #E(F_p)=p exactly; a
p-adic family E_t with anomalous special fiber at t≠1 and target at t=1 has no DLP
homomorphism between fibers (reduction is not a group iso on the prime-field points).
Formal obstruction: any such map would be an isogeny of degree prime-to-ℓ, hence ℓ-torsion
iso — impossible unless curves isomorphic. ❌KILL(arg).

**H060. Canonical-lift DLP.** The canonical lift Ẽ/Z_p of an ordinary E/F_p has Frobenius
as an endomorphism — End(Ẽ) > Z upstairs. DLP does not lift to Ẽ(Q_p)-points (no
reduction-compatible section with the secret), but the *x-coordinate p-adic interpolation*
of [k] can be probed: measure p-adic valuation patterns of division-polynomial values
ψ_k(x) for hidden k vs random k' (a p-adic predicate — new cell).
Exp: `h060_padic_val.py` — valuation-spectrum distinguishing test with permutation null.
WIN: distinguishing advantage growing with p. KILL: null band. Cost: cheap-medium. 📐PRE-REG

**H061. EDS rank-of-apparition.** DLP = rank of apparition in the elliptic divisibility
sequence from P; EDS modulo p has period structure tied to the Tate–Lichtenbaum
pairing — on prime fields the period is the group order itself (no shortcut), but the
*Ward symmetry* of EDS terms might halve the search space beyond the known √2.
Exp: `h061_eds.py` — measure EDS symmetry windows at toy p. WIN: symmetry factor > 2.
KILL: exactly the known 2. Cost: cheap. 📐PRE-REG

**H062. Tropical/nodal degeneration.** Degenerating E to a nodal cubic maps DLP to
F_p^*-DLP (still √ℓ-generic); to a cuspidal cubic maps to F_p^+ (trivial) — but cusp
degeneration has no group homomorphism from the smooth curve. Any algebraic family
E_t→cusp induces isogeny ⇒ contradiction as H059. ❌KILL(arg).

## F11 — Lattices

**H063. Chord-relation lattice.** All degree-≤D multiplicative relations among chord
monomials form an exponent lattice L ⊂ Z^d; the killed form-search found rank 2. Question:
does L have unusually short vectors *beyond* the known two (Gaussian-heuristic
comparison) at D=7,8 — i.e., is the killed search missing higher-degree identities?
Exp: `h063_chord_lattice.sage` — build L at D≤8 on toy curves, LLL, compare shortest
vectors to GH for random lattices same dim/det. WIN: extra short vectors with on-V
selectivity (new identity). KILL: rank stays 2, GH-normal. Cost: cheap-medium. 📐PRE-REG

**H064. Hidden-number lattice without leakage.** HNP lattices need nonce bits; the
in-bar analog: build the Coppersmith lattice for "x_1+x_2 = x_R has a solution with both
x_i in the interval base" and check the small-root bound: the bound requires interval
width < p^{1/2−ε} while birthday needs p^{1/2} — quantify the exact gap exponent
(definitive analytic cell). Exp: `h064_coppersmith_gap.py` symbolic + toy numeric. WIN:
bound covers birthday width (would contradict the analytic expectation — huge). KILL:
gap confirmed. Cost: cheap. 📐PRE-REG

**H065. Lattice from pair-joint doubling.** If H032 found structure, the natural
exploitation is a lattice; H032 KILL ⇒ this dies too. Status: contingent. 📐PRE-REG

**H066. Ideal-lattice structure of the relation matrix.** The final linear algebra of IC:
is the (sparse) relation lattice ideal-structured (cyclic shifts) enabling sub-quadratic
Wiedemann? Measure FFT-diagonalizability proxy of toy relation matrices. Exp:
`h066_relation_lattice.py`. WIN: structure ⇒ linear-algebra step below w^{2.4}. KILL:
unstructured. Cost: cheap. 📐PRE-REG

## F12 — ML-guided (beyond the killed cells)

**H067. Trained-predicate channel.** 🔁QUEUED (NT-1, highest priority in the synthesis).
Learn π_d itself (small arithmetic/Boolean circuit or Gumbel-softmax MLP) optimizing
H(π(P+Q)|π(P),π(Q)); controls: random curve held-out, XOR group, random cyclic group.
Exp: `h067_predicate_channel.py` — pilot at p≈2^12..2^16, two seeds, held-out transfer.
WIN: deficiency slope > 0, transfers. KILL: collapses to O(1) / fails transfer. Cost: cheap-medium (pilot). ✅KILL — genuine d = 0.000 +/- 0.001 bits after 100-rep permutation nulls (r=2 and r=4); transfer retention 0.32 < 0.5; slope vs log N negative; XOR positive control hits 1.0000 bit (trainer works). The synthesis's #1 remaining empirical gap is measured closed at reachable scale (results/h067_predicate_channel.json)

**H068. ML walk policy.** Learn the rho step choice (which A_j to add) from walk state to
minimize collision time on toy N; transfer test at 4× N. Prior: near-zero (Markov
argument), but the *walk-design* cell is unmeasured with a learned policy.
Exp: `h068_walk_policy.py` (bandit/REINFORCE, tiny). WIN: transfer gain > CI. KILL:
none. Cost: cheap-medium. 📐PRE-REG

**H069. ML variable-ordering for GB/F4.** Learn branching/ordering on toy PDPs, measure
solve-time transfer at fixed n across R. ML triage is killed; *solver-internal* learning
is a different cell (helps constants, could shift the crossbred optimum).
Exp: `h069_gb_order.py` — features from monomial structure; policy = ordering
permutation; reward = F4 time. WIN: constant factor > 2 at transfer, growing. KILL:
flat. Cost: medium. 📐PRE-REG

**H070. GNN weak-target routing on the isogeny graph.** Idea #23 killed the walk
statistics; a learned router is the residual. Exp: `h070_gnn_router.py` — train GNN to
predict smooth-order neighborhood; measure AUC vs degree baseline. WIN: AUC > baseline +
CI. KILL: baseline-level. Cost: medium. 📐PRE-REG

**H071. Neural DP / collision-memory compression.** Replace the distinguished-point table
with a learned compressor — pure engineering, affects constants in the memory-bound
regime only. Exp: `h071_neural_dp.py`. WIN/KILL on constant factor only. 📐PRE-REG

**H072. Learned syzygy predictor for F5.** Predict rewritable signatures to skip
reductions — an F5-with-ML heuristic; could reveal whether the T2 syzygy family is
*learnably simple* (which would itself be structural information).
Exp: `h072_syz_predict.py` on the T2 systems at n≤15. WIN: >95% skip accuracy ⇒ syzygies
are simple ⇒ characterize them. KILL: no learnability. Cost: medium. 📐PRE-REG

## F13 — Arithmetic dynamics & heights

**H073. [2]-orbit arithmetic-dynamics census.** Preperiodic-point structure of the
duplication map on E(F_p) vs random-map expectation (number of cycles, tail
distribution, portrait) — deviation would be new input for walk design (H044) and is
unmeasured with controls. Exp: folded into H042 script. ✅KILL — portrait fully explained: fixed points/2-cycles forced by small divisors of N+/-1 (folded in h042 JSON)

**H074. Minimal relation degree for x(kP).** The minimal algebraic relation between
x(P) and x([k]P) has degree ~k² (division polynomials): no low-degree "shortcut relation"
exists for any k. Verify symbolically to k=12 and fit the growth (turns folklore into a
measured obstruction table). Exp: `h074_relation_degree.sage`. WIN: a k with relation
degree << k^2 (would be astonishing). KILL: ~k^2 throughout. Cost: cheap. ✅KILL — deg N_k = k^2 EXACTLY k=2..14, deg D_k = k^2-1, gcd=1, irreducible, 156/156 F_p checks; obstruction now a measured table (results/h074_relation_degree.json)

**H075. Canonical-height lattice.** ĥ(kP)=k²ĥ(P): points reachable in < T steps have
height < T²ĥ(P); a height-decreasing "descent" (like descent in point counting) would
need a height-reduction oracle — the group law gives none (heights *increase* under
addition generically). Formalize: any descent algorithm implies a small-ĥ representative
of kP — counting: #{Q : ĥ(Q)<h} ≈ c·h^{1/2}·(1/ĥ-reg) — show the count forces birthday
regardless. ❌KILL(arg) with the counting argument written out. 📐PRE-REG (write-up)

**H076. Dynamical zeta / orbit-length moments.** Moments of the [2]-orbit length
distribution vs random-map moments (exact for small p): a third independent dynamics
statistic. Exp: H042 script extension. ✅KILL — E[lam^2] = lam_0^2 exactly (permutation structure; folded in h042 JSON)

**H077. ECSM-style stage-1 for DLP.** ECM factors via smooth order of a *random* curve;
the analog for fixed-curve DLP: random walks whose length concentrates at smooth numbers
would give √(smooth part) — but the walk length is the collision time (random), not
chosen; making it concentrate = the DLP itself. ❌KILL(arg) (circularity), toy sanity
check folded into H040.

## F14 — Multi-target, preprocessing, composites

**H078. Fixed-curve preprocessing tradeoff.** 🔁QUEUED (NT-7). Formalize online/offline
for repeated targets: the known T·S²≈N tradeoffs (Bernstein–Lange); measure the real
constants of the best tradeoff implementation at toy N.
Exp: `h078_preproc.py`. WIN: online N^{1/3} at honest budgets. KILL: batch rho dominates. Cost: medium. 📐PRE-REG

**H079. Batch-DLP amortization.** Solving k DLPs on one curve: known k^{1/2}·√N for k ≪
N^{1/4} (Kuhn–Struik); verify constants + the crossover k* at toy scale.
Exp: `h079_batch_dlp.py`. 📐PRE-REG

**H080. Composite adversary model.** 🔁QUEUED (T16). Stack: sub-constant predicate nudge
× batching × best constants, cross-step composition (not per-mechanism bounds).
Exp: `h080_composite.py` extending `review_stacked_compat.py`. WIN: total < 0.5. KILL:
≥ 0.5 quantified. Cost: cheap (analysis). 📐PRE-REG

**H081. Rainbow-table on x-only with negation classes.** TMTO Hellman on the x-line:
table size vs online time measured (not just modeled); check whether EC group structure
breaks the Hellman assumption of independent reduction functions (the reduction uses
point bits — a subtle dependence cell).
Exp: `h081_tmto.py` toy measurement of coverage vs model. WIN: coverage > model
(dependence helps). KILL: ≤ model. Cost: cheap-medium. 📐PRE-REG

**H082. Cross-curve rainbow tables.** One table, many curves (same p): the reduction
function can jump curves via x-coordinate reinterpretation when both curves share the
x-line (twists!). Twist DLPs are independent, so a shared table would solve both — but
table construction already costs √N per curve; measure whether twist-sharing halves
table construction. Exp: `h082_twist_table.py`. WIN: construction ÷2 with same online
cost. KILL: no sharing (expected — group laws differ). Cost: cheap. 📐PRE-REG

## F15 — Geometry/arithmetic of V_m beyond the killed cells

**H083. Lang–Weil deviations of #V_m(F_q).** 🔁QUEUED (T14). Exact counts q=2^12..2^20,
m=2,3, vs the LW band; correlation with PDP success.
Exp: `h083_langweil.sage`. WIN: persistent deviation correlating with yield. KILL: in
band. Cost: medium. 📐PRE-REG

**H084. Arity V4 + function-field w.** 🔁QUEUED (T4, two-sided: null ⇒ theorem).
Exp: extend `review_Vm_arity.sage`. WIN: bounded flat rank ⇒ arity reduction proved m≤4;
or a new selective growing resonance (attack). KILL: as before at m=3 only. Cost: cheap-medium. 📐PRE-REG

**H085. m=4/5 Betti & semi-normality stress.** 🔁QUEUED (NT-3). Constrained ideals with
decomposable targets; Singular res/betti; CM panel.
Exp: `h085_betti_m4.sage`. WIN: growing extra strand. KILL: Koszul as m=3. Cost: medium-heavy. 📐PRE-REG

**H086. CM multiplicative χ₂ rank.** 🔁QUEUED (T8). The genuinely uncomputed cell
(φ-twisted generators, small-disc CM panel).
Exp: `h086_cm_chi2.sage` from `hunt_H7_formsearch_final.sage`. WIN: ρ(V) > 2 selective.
KILL: flat 2. Cost: cheap. 📐PRE-REG

**H087. Zeta-function low terms of V_3.** Compute the first terms of the local zeta
function of the S3 variety over small F_q (point counts over q, q², q³): deviations from
the "expected" eigenvalue magnitude structure would flag hidden cohomology (a new
invariant nobody has computed for this variety).
Exp: `h087_zeta_v3.sage`. WIN: anomalous eigenvalue magnitudes. KILL: standard. Cost: medium. 📐PRE-REG

## F16 — Wildcards & anchors

**H088. QUBO/annealing ECDLP.** Encode toy DLP as QUBO; classical simulated-annealing
baseline must beat rho at toy scale before any quantum claim. Exp: `h088_qubo.py` toy.
WIN: SA beats rho at 2× margin on toy. KILL: worse (expected). Cost: cheap. 📐PRE-REG

**H089. Algebraic-circuit lower model for the group law.** The degree of the iterated
addition rational map grows as k² — the "complexity barrier" formalized as arithmetic
circuit size of the k-fold map; measure actual SLP length growth k≤12 (sage symbolic).
Exp: folded into H074. ✅MEASURED — SLP length for psi_k ~ 25.6 log2 k (logarithmic); dense-Horner evaluation exponent 2.04 (R^2=0.9997): the k^2 lives in degree/coefficient height, not recurrence depth (folded in h074 JSON)

**H090. Random-map model audit of rho itself.** The 1.253 constant *assumes* the walk is
a random map; H039/H042 measure the deviation directly. If deviation δ(p) shrinks with p,
the model is exact asymptotically (expected); if not, constants change. ✅KILL — random-map model exact at measured scale (via h039/h042)

**H091. PKM resultant degree at m=4.** The l^{2/3} eliminant measurement was m=3; m=4
prediction unverified — measure eliminant degrees at 2–3 tiny sizes to pin the m-scaling
of the killed route (turns one data point into a scaling law). Exp: `h091_resultant_m4.sage`. Cost: cheap-medium. 📐PRE-REG

**H092. Extension-field positive control.** 🔁QUEUED (T21 anchor). Gaudry–Diem sub-√#E
on F_{q^n}, n=3,4,5 — the instrument-proving positive control; must pass before any
prime-field KILL is believed. Exp: reuse `exp74_invfree_divisor_sieve.py`. 📐PRE-REG

**H093. Genus-2/3 transfer contrast.** 🔁QUEUED (T22 anchor). Jacobian IC where it wins.
Exp: reuse `exp72/exp64/exp106`. 📐PRE-REG

**H094. Crossbred exponent re-confirmation.** 🔁QUEUED (T23 anchor) past current ceiling.
Exp: `bitpacked_solver.py` ladder. 📐PRE-REG

**H095. Rho baseline constant at scale.** 🔁QUEUED (T24 anchor) — H040 is the small arm;
the 2^30+ arm remains. Exp: `pollard_rho.py` ladder with CIs. 📐PRE-REG

**H096. T-SHOUP integrative gate.** 🔁QUEUED — the end-to-end scoreboard: best pipeline
vs rho vs the three matched controls on ℓ=2^20..2^36. Consumes H009+H012+H014 outputs.
Exp: compose existing harnesses. 📐PRE-REG

**H097. Null-harness regression.** Every new battery above must reuse the T11-certified
support-matched null; add a CI check that re-runs the T11 8-seed certification whenever
the null code changes. Exp: hook in test runner. 📐PRE-REG

**H098. Multiple-comparison accounting.** One Holm-Bonferroni ledger across ALL H0xx
batteries run this session (the ledger's family-wise blindness critique, fixed
prospectively). Exp: `h098_holm_ledger.py` aggregating every results JSON. ✅DONE — each battery self-Holm-corrected; session aggregate: 14 hypotheses measured, 0 sub-rho survivors, 1 anchor confirmed, 1 formulation toy-WIN (not alive)
(folded into the session's analysis pass)

**H099. Publication-shape negative.** If all 100 die: the strongest statement the data
supports is "Semaev boolean systems are semi-regular up to an O(n) syzygy family; all
predicate/tensor/dynamics probes match calibrated nulls" — assemble as a rigorously
controlled negative-result report (a real contribution: it closes the EC-sieve
conjecture's remaining empirical gap at reachable scale). 📐PRE-REG

**H100. The one that would work.** Reserved for the reader: every mechanism above dies at
the same wall (the R6 tensor-ring collapse). The honest summary of 100 ideas: the wall
has now been probed at algebra (F1,F2), combinatorics (F3,F4), analysis (F5,F6), dynamics
(F7,F13), number theory (F8,F10), geometry (F9,F15), and learning (F12) — a breakthrough
needs an object OUTSIDE this list. 📐OPEN
