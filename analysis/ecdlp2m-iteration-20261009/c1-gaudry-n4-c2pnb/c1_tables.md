# C1 cost model: Gaudry/Diem n=4 with GTTD double large primes and a pi_16-orbit factor base, against rho/vOW on the five c2pnb rows

This is a derivation only. It uses scripted arithmetic and no experiment: nothing was run on any curve, and no record or repository file was written. All figures are log2. A positive **margin** means C1 is cheaper than the baseline. Everything below the "Verbatim output" heading is the unedited stdout of `python3 c1_model.py --verify-repo /home/user/crypto-autoresearcher`. The run is deterministic, takes about 11 s, and uses only the Python 3 standard library.

Forbidden paths were not read: `experiments/EXP-FROB-30006a/` and `experiments/EXP-QSP-70b731/runs/`.

## 1. Program conventions used (read in this session; reproduced in T0 by assertion to <= 0.05 bit)

| convention | source (file:line) | how used |
|---|---|---|
| Matched rho = log2 sqrt(pi r / (4k)) (negation + pi_16, classes of 2k) | `experiments/EXP-BINSTD-9d1b8e/specification.yaml:77-81,246-248`; `ledger/evidence/EV-BINSTD-f541ea.yaml:91-95` | time baseline; also W in every other metric. Recomputed from t: the Weil recursion gives #E(F_{2^{16k}}), r = #E / h, and r equals `r_from_dump` exactly (`experiments/EXP-BINSTD-9d1b8e/stage0/five-row-symmetry-certificate.yaml:17,52,87,122,157`). Bits 78.0976 / 93.9804 / 125.7848 / 141.7069 / 173.5656 vs frozen 78.10 / 93.98 / 125.78 / 141.71 / 173.57 |
| t, h = 2^16 + 1 - t (65390 / 65096 / 65286 / 65070 / 65392) | `analysis/binstd-curve-audit/audit-certificate.txt:1-15`, `audit-scan.txt:35-39` | exact r for each row (no approximation used) |
| HEUR-VOW-CURVE: T = W(1/M + 1/w), Mem = 3n max(w, M) bits, W = 0.886 * 2^{n/2}; coherent baseline = own-curve T x Mem minimum 6nW | `ledger/evidence/EV-SEMBIN-4125ec.yaml:80-87,103-112`; `ledger/hypotheses/H-SEMBIN-97ea23.yaml:40-41,183-184`; `experiments/EXP-SEMBIN-2c40bb/runs/RUN-SEMBIN-3ae91c/arm-b-coherent-baseline.json:1569-1600,2068` | Reproduced: own_curve_min_product_log2 at n = 163 ... 571, the +29.0 record-point excess, T_v = 204.33 and Mem_v = 40.26 at n = 409 (`EV-SEMBIN-4125ec.yaml:182`). For c2pnb this run uses **W = matched rho** and n = 16k field bits. That is an adaptation: no program record prints a c2pnb vOW figure |
| 0.886 = sqrt(pi/4) already includes negation; 3n bits/DP is an upper bound; vOW's own optimum has w/M ~ 2^3.9 | `knowledge/literature/KN-LIT-73f7e1.md:103-147` | baseline constant scope; DP-bit variant 3 log2 r is shown in T2 |
| SEMBIN parallel convention: IC time - p, memory log2add(store, ws + p), p in {0, 20, 40} | `experiments/EXP-SEMBIN-2c40bb/runs/RUN-SEMBIN-3ae91c/implementation.md:9`; `EV-SEMBIN-4125ec.yaml:42-50` (processors_log2 grid) | metric (ii) "p0" and "best" |
| Explicit metric; compare against vOW parallel rho including DP storage | `knowledge/open-problems/KN-OPEN-86e7e1.md:130-148` | why (ii) and (iii) are reported beside (i) |
| MM-1: FC = sum over phases of (P + mem/RHO_AREA) x wall; RHO_AREA = 2^16; P_REF = 2^20; rho iteration = 10 (16k)^2 bit ops; P*2^10 DPs at 3 log2 l bits; Wiedemann D^2 (3w log2 l + 7 (log2 l)^2); LA memory D(w(log2 D + 1) + 4 log2 l); P_LA_MAX = 2^10; sensitivity grid P in {2^10, 2^20, 2^30}, RHO_AREA in {2^10, 2^16, 2^22} | `experiments/EXP-BINSTD-f442a9/specification.yaml:579-605,621-623,359`; `ledger/hypotheses/H-BINSTD-0dd2ce.yaml:65-74,503-507` | metric (iii-a), the LA bit-op form, and the rho-step unit. MM-1 has no runs, so it has no printed numbers to reproduce. Its formulas were applied literally, including charging all P processors during the LA phase |
| HOLD-D product-law floors min_l m! 2^(N - (m-1)l) + m 2^(2l), N = 16(k-1); orbit variant relations/k, LA/k^2 | `analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-6cf862.yaml:56-69` | all 9 x 2 quoted floors reproduced to <= 0.036 bit (T0); m = 4 context in T6 |

## 2. Model C1: parameters and provenance

- **Field and base.** F_{2^{16k}} = F_{Q^4} with Q = 2^{4k}. The factor base is the points with x in F_Q, about Q points. pi_16 : x -> x^{2^16} acts on F_Q with order 4k / gcd(16, 4k) = k, and its fixed field is F_{2^4}. Its orbits combined with negation have size 2k, so **N = Q / (2k)** orbits; the 16 exceptional x are ignored. On the orbit-quotient unknowns the coefficients are ±mu^j mod r, so each LA nonzero costs one Z/r multiplication (`coef = orbit`). The no-orbit "plain" variant uses N = Q/2 and ±1 coefficients.
- **H0**: decomposition probability p = 1/4! = 1/24 per trial. [heuristic]
- **2LP trial count**: kappa N^3 / (12 p s^2). It comes from P(exactly 2 of 4 large) = C(4,2) x^2 (1 - x)^2 ~ 6 x^2 with x = s/N, together with percolation of the large-prime graph at ~N/2 edges. The code uses the exact x and N - s large vertices; T2b shows the effect is <= 0.15 bit. **H2**: kappa = 1. [heuristic; recalled-unverified random-graph fact that the excess of the giant component grows like ~(2/3) eps^3 N at kappa = 1 + eps]
- **LA**: B s^2 w with B = 3 Wiedemann passes, w = 8 (**H3**), plus 7 (log2 r)^2 per row (MM-1). This is converted to rho steps through t_iter = 10 (16k)^2. The constant per s^2 comes to 2^1.36 ... 2^1.50 rho steps. Sensitivity runs from `small` (MM-1 literal, about 2^-2) to `pess` (3 rho steps per nonzero, 2^4.58).
- **Optimisation**: s is found analytically, s*^4 = kappa N^3 c / (12 p LAc), and numerically by golden section, which is checked against a 0.05-grid scan. For each metric, s is re-optimised under that metric. T5 checks the exponents: 2LP 1.5000 (Q^{2-2/4}), 1LP 1.5556 (= 14/9), basic 2.0000.
- **c_trial** (rho-step units): floor 2^15.5 = 2^21 F_Q ops / 45-54 F_Q mults per rho step. The band is [2^27, 2^32.5] with centre 2^30; its top equals dense FGLM n D^3 = 2^38 F_Q ops / 45-54. All of these are [brief] red-team estimates. The "247 s in Magma" figure attributed to Granger (Asiacrypt 2010) is **not verified**: `knowledge/literature/KN-LIT-41fe5c.md` covers the abstract only and does not contain it. c_gen = 1 rho step per trial is the target generation, and it is kept in the free-oracle columns.
- **Memory**: (a) relation store minimum, s rows of (w (log2 s + log2 2k) + 4 log2 r) bits (MM-1 LA-memory form); (b) graph store, kappa N/2 edges of 2 large + 2 small entries, peak with (a); (c) per-worker FGLM state, D^2 F_Q elements = 2^24 * 4k bits = 2^29.5 ... 2^30.5 bits. Model (c) is charged in (ii) as the SEMBIN working set and in (iii) as per-worker area.
- **(iii-b) mesh AT**: each relation-collection worker is 1 processor plus ws/RHO_AREA of memory area, about 2^13.5 ... 2^14.5 processor-equivalents. The store is amortised over up to 2^40 workers. LA runs on a mesh with one cell per nonzero, at area cells x cell_bits / RHO_AREA and time B s c_route sqrt(cells) Z/r-mults, with c_route = 1 [model; Bernstein-style routing constant recalled-unverified]. The rho AT is W(1 + a + 2 sqrt a) with a = 3 log2 r / RHO_AREA.

## 3. Heuristics and how each would be validated on a toy ladder

The toy ladder is E/F_{2^4} over F_{2^{4k}}, k in {5, 7, 9, 11, 13}. This is the exact analogue of the deployed rows: base field F_Q with Q = 2^k, and pi_4 : x -> x^16 has order k on F_Q (k odd) with fixed field F_2. The orbit count N = 2^k/(2k) is 3.2 / 9.1 / 28.4 / 93.1 / 315.1, the group orders are about 2^{4k}, and r is about 2^{4k-4}. That puts the full DLP at k <= 13 within reach of rho in about 2^24 steps, which serves as ground truth.

| id | statement | toy measurement | pass band | expected cost |
|---|---|---|---|---|
| **H0** | p = 1/24 per random target | Fraction of random R in E(F_{2^{4k}}) that decompose as a sum of 4 factor-base points, from the Weil-restricted S_5 system solved over F_{2^k} with roots in F_Q and sign-checked; reported per k | 99 % CI of p inside [1/48, 1/12], with no trend in k after finite-Q correction | ~2,300 trials per k gives ±10 % (1 sigma) relative error on p, so ~11,500 trials over 5 k. Per-trial cost is **unmeasured**; at the brief's 1-247 s per decomposition the run takes ~3 h to ~33 CPU-days, and it parallelises perfectly. The same trials feed H1-H3 |
| **H1** | N = Q/(2k) orbits are hit uniformly; orbit-quotient relations (coefficients ±mu^j) have full rank, giving gain k in relations and k^2 in LA | Chi-square of decomposition hits over orbits; rank of the orbit-quotient relation matrix against the raw matrix; one complete DL solved through the orbit quotient at k = 11 and k = 13, checked against rho | uniform at 1 %; rank = s; solved log equals the rho log | same trials as H0 (k = 11, 13), plus ~2^24 rho steps per check (seconds) |
| **H2** | kappa ~ 1: about kappa (N - s)/2 2LP edges yield >= s independent small-prime relations | (i) Synthetic random-graph simulation at N = 10^4 ... 10^7 for s/N in {1/2, 1/4, 1/8, 1/16}, which costs seconds and isolates the graph constant; (ii) the real toy edge stream at k = 11, 13 (N = 93, 315), compared with (i) | kappa(s/N) curve; toy kappa within ±25 % of synthetic | (i) negligible; (ii) ~3,000 (k = 11) and ~10,000 (k = 13) trials at s = N/4, the dominant toy cost, ~4 h to ~37 CPU-days at 1-247 s |
| **H3** | LA constant: B = 3, row weight w = 8 after path combination, one Z/r mult per nonzero; per-trial cost c_trial is constant in k when counted in F_Q ops; FGLM state = D^2, D = 4096 | Measured mean weight of combined rows; Wiedemann/Lanczos op counts per s^2; **instrumented F_Q-op count per decomposition** (F4 + FGLM / msolve) with the realised quotient dimension D and peak memory at each k; rho steps counted in the same library to give the F_Q-mults-per-rho-step ratio (45-54 assumed) | ops-per-trial flat in k within 2x; D <= 4096; LA constant within the small..pess range | comes free with H0's trials, plus minutes of LA |

## 4. Headline (read with T3, T7, T8, T9, T10 below)

- **(i) Time only.** C1 beats matched rho on **all five rows across the whole band 2^27 ... 2^32.5**. At c_trial = 2^30 the margins are +1.46 / +5.80 / +14.19 / +18.34 / +26.60 bits. c2pnb176v1 is marginal: its break-even c_trial is 2^32.69, so it holds only +0.11 bit at the band top 2^32.5, and the `pess` LA unit alone (x2^3.05) flips it. The break-even c_trial for the other rows is 2^41.1 / 2^57.6 / 2^65.9 / 2^82.2, far above the band. The orbit gain is 4.1 ... 5.7 bits. Without large primes (basic Gaudry) C1 loses on every row. The 1LP variant (q^{14/9}) also wins on all five rows, but by only +0.01 on 176v1.
- **(ii) Program T x Mem (SEMBIN convention, vOW at 6nW).** With p = 0, C1 **loses on every row at every c_trial, including a free oracle**, by 35 ... 56 bits at 2^30. With the processor dilution of the SEMBIN surface, best p in {0, 20, 40}, C1 still loses everywhere inside the band. It wins only at the c_trial floor 2^15.5, on 272w1/304w1/368w1 under memory (a) (+2.0 / +6.0 / +5.6) and on 272w1 alone under (b) (+1.1). The break-even under (a) is 2^2.6 / 2^19.5 / 2^26.0 / 2^22.9 for 208w1/272w1/304w1/368w1, all below the band; 176v1 loses even with a free oracle.
- **(iii) Area-time.** Under MM-1 literal (iii-a), C1 loses on all rows at every c_trial in the band and at the floor. It wins only with a free oracle. The break-even c_trial is 2^5.0 ... 2^13.4 with memory (a). With the graph store (b), 272w1/304w1/368w1 lose even with a free oracle, and 176v1/208w1 break even at 2^10.3 / 2^9.4. Under the mesh model (iii-b) with memory (a), C1 beats rho **only at the band's bottom edge 2^27, on c2pnb304w1 (+1.28) and c2pnb368w1 (+0.97)**. It loses at 2^30 and above. The break-even is 2^29.19 and 2^28.36, so it sits inside the band. With the graph store (b), C1 loses everywhere in the band. The dominant AT penalty is the per-worker FGLM state, D^2 F_Q elements ≈ 2^13.5 ... 2^14.5 processor-equivalents per worker.
- **Most sensitive parameters** (T9, by slope x plausible range):
  1. **c_trial**, together with its exact aliases kappa and 1/p, since the cost depends on c_trial x kappa / p. It is first or second in every metric.
  2. **The area or memory price of the per-worker decomposition state** (D^2 F_Q elements against RHO_AREA). It is first in (iii-b), at RHO_AREA swing 11 bits, and second or third in (ii)-best and (iii-a).
  3. **The LA constant per s^2** (H3: B, w, Z/r-mult coefficients). It is second in (i), the only metric where C1 wins inside the band.
  For (iii-a) the MM-1 processor count P is the largest swing (12-15 bits), but within the grid it flips no row.

## 5. Verbatim output

```text
verify-repo: embedded constants match the repository files

## T0. Reproduction of the program's numbers (assert |diff| <= 0.05 bit)

| quantity | this script | program record | |diff| | pass |
|---|---|---|---|---|
| rho c2pnb176v1 | 78.0976 | 78.10 | 0.0024 | True |
| rho c2pnb208w1 | 93.9804 | 93.98 | 0.0004 | True |
| rho c2pnb272w1 | 125.7848 | 125.78 | 0.0048 | True |
| rho c2pnb304w1 | 141.7069 | 141.71 | 0.0031 | True |
| rho c2pnb368w1 | 173.5656 | 173.57 | 0.0044 | True |
| vOW 6nW n=163 | 91.2591 | 91.2591 | 0.00003 | True |
| vOW record-pt n=163 | 120.2591 | 120.2591 | 0.00003 | True |
| vOW 6nW n=233 | 126.7745 | 126.7745 | 0.00003 | True |
| vOW record-pt n=233 | 155.7745 | 155.7745 | 0.00003 | True |
| vOW 6nW n=283 | 152.0550 | 152.0550 | 0.00000 | True |
| vOW record-pt n=283 | 181.0550 | 181.0550 | 0.00000 | True |
| vOW 6nW n=409 | 215.5863 | 215.5863 | 0.00000 | True |
| vOW record-pt n=409 | 244.5863 | 244.5863 | 0.00000 | True |
| vOW 6nW n=571 | 297.0677 | 297.0677 | 0.00001 | True |
| vOW record-pt n=571 | 326.0677 | 326.0677 | 0.00001 | True |
| vOW T_v n=409 | 204.3254 | 204.33 | 0.0046 | True |
| vOW Mem_v n=409 | 40.2609 | 40.26 | 0.0009 | True |
| HOLD-D floor N=160 m=3 | 83.08/77.90 | 83.1/77.9 | 0.015 | True |
| HOLD-D floor N=160 m=4 | 68.00/62.47 | 68.0/62.5 | 0.030 | True |
| HOLD-D floor N=160 m=5 | 58.10/52.34 | 58.1/52.3 | 0.036 | True |
| HOLD-D floor N=192 m=3 | 99.08/93.53 | 99.1/93.5 | 0.034 | True |
| HOLD-D floor N=192 m=4 | 80.80/74.88 | 80.8/74.9 | 0.016 | True |
| HOLD-D floor N=192 m=5 | 68.77/62.60 | 68.8/62.6 | 0.031 | True |
| HOLD-D floor N=192 m=6 | 60.28/53.94 | 60.3/53.9 | 0.035 | True |
| HOLD-D floor N=256 m=4 | 106.40/99.86 | 106.4/99.9 | 0.035 | True |
| HOLD-D floor N=256 m=5 | 90.10/83.29 | 90.1/83.3 | 0.011 | True |

ALL REPRODUCTION ASSERTIONS PASSED

## T1. c_trial band (rho-step units)

| source | log2 c_trial | provenance |
|---|---|---|
| root-extraction floor 2^21 F_Q ops / (45..54) | 15.25 .. 15.51 | brief; used as 'floor' = 2^15.5 |
| dense FGLM n D^3 = 2^38 F_Q ops / (45..54) | 32.25 .. 32.51 | brief; band top 2^32.5 |
| Granger Asiacrypt 2010, 247 s per char-2 n=4 decomposition (Magma) | 27 .. 32.5, central 30 | brief red-team estimate; NOT in KN-LIT-41fe5c (abstract only); unverified |

## T2. Per-row derived quantities (defaults)

| row | k | log2 Q | log2 N (orbit) | log2 N (plain) | log2 r | rho W | vOW 6nW (n=16k) | vOW 6LW (3 log2 r/DP) | MM-1 rho FC | mesh rho AT | log2 LA const/s^2 | log2 ws bits (c) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c2pnb176v1 | 11 | 44 | 39.54 | 43.00 | 160.00 | 78.10 | 88.14 | 88.00 | 81.19 | 78.33 | 1.36 | 29.46 |
| c2pnb208w1 | 13 | 52 | 47.30 | 51.00 | 192.01 | 93.98 | 104.27 | 104.15 | 97.30 | 94.24 | 1.40 | 29.70 |
| c2pnb272w1 | 17 | 68 | 62.91 | 67.00 | 256.01 | 125.78 | 136.46 | 136.37 | 129.49 | 126.08 | 1.46 | 30.09 |
| c2pnb304w1 | 19 | 76 | 70.75 | 75.00 | 288.01 | 141.71 | 152.54 | 152.46 | 145.57 | 142.02 | 1.48 | 30.25 |
| c2pnb368w1 | 23 | 92 | 86.48 | 91.00 | 352.00 | 173.57 | 184.67 | 184.61 | 177.70 | 173.91 | 1.50 | 30.52 |

## T2b. Optimal s, time only, c_trial = 2^30: analytic (s << N) vs numeric (exact 2LP rates)

| row | log2 s* analytic | log2 s* numeric | log2 (s*/N) | T* analytic | T* numeric | numeric - analytic |
|---|---|---|---|---|---|---|
| c2pnb176v1 | 37.07 | 37.10 | -2.44 | 76.49 | 76.64 | 0.15 |
| c2pnb208w1 | 42.87 | 42.88 | -4.42 | 88.15 | 88.18 | 0.03 |
| c2pnb272w1 | 54.57 | 54.57 | -8.34 | 111.60 | 111.60 | 0.00 |
| c2pnb304w1 | 60.44 | 60.45 | -10.31 | 123.37 | 123.37 | 0.00 |
| c2pnb368w1 | 72.23 | 72.23 | -14.25 | 146.97 | 146.97 | 0.00 |

Optimiser check: golden-section minus 0.05-grid minimum, worst case over rows x c_trial x metrics = 0.00e+00 bits (assert < 1e-3)

## T3[time]. (i) time only vs rho: C1 bits / baseline bits / margin (+ = C1 better)

| row | baseline | C1 @floor | margin @floor | C1 @2^27 | margin @2^27 | C1 @2^30 | margin @2^30 | C1 @2^32.5 | margin @2^32.5 | C1 free-oracle (c_trial=0) | margin free | log2 s* @2^30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c2pnb176v1 | 78.10 | 69.25 | 8.85 | 75.07 | 3.02 | 76.64 | 1.46 | 77.99 | 0.11 | 61.49 | 16.61 | 37.10 |
| c2pnb208w1 | 93.98 | 80.90 | 13.08 | 86.67 | 7.31 | 88.18 | 5.80 | 89.45 | 4.53 | 73.15 | 20.83 | 42.88 |
| c2pnb272w1 | 125.78 | 104.35 | 21.44 | 110.10 | 15.69 | 111.60 | 14.19 | 112.85 | 12.93 | 96.60 | 29.19 | 54.57 |
| c2pnb304w1 | 141.71 | 116.12 | 25.59 | 121.87 | 19.84 | 123.37 | 18.34 | 124.62 | 17.09 | 108.37 | 33.34 | 60.45 |
| c2pnb368w1 | 173.57 | 139.72 | 33.85 | 145.47 | 28.10 | 146.97 | 26.60 | 148.22 | 25.35 | 131.97 | 41.60 | 72.23 |

## T3[TxM-a-p0]. (ii) TxMem, mem (a), p=0 vs vOW 6nW: C1 bits / baseline bits / margin (+ = C1 better)

| row | baseline | C1 @floor | margin @floor | C1 @2^27 | margin @2^27 | C1 @2^30 | margin @2^30 | C1 @2^32.5 | margin @2^32.5 | C1 free-oracle (c_trial=0) | margin free | log2 s* @2^30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c2pnb176v1 | 88.14 | 112.38 | -24.24 | 121.12 | -32.98 | 123.45 | -35.31 | 125.43 | -37.29 | 100.70 | -12.56 | 36.65 |
| c2pnb208w1 | 104.27 | 130.09 | -25.82 | 138.76 | -34.50 | 141.04 | -36.77 | 142.94 | -38.67 | 118.42 | -14.15 | 42.47 |
| c2pnb272w1 | 136.46 | 165.62 | -29.17 | 174.27 | -37.82 | 176.53 | -40.07 | 178.41 | -41.95 | 153.97 | -17.51 | 54.17 |
| c2pnb304w1 | 152.54 | 183.43 | -30.89 | 192.08 | -39.54 | 194.33 | -41.79 | 196.21 | -43.67 | 171.78 | -19.24 | 60.05 |
| c2pnb368w1 | 184.67 | 219.10 | -34.42 | 227.74 | -43.07 | 229.99 | -45.32 | 231.87 | -47.20 | 207.45 | -22.78 | 71.83 |

## T3[TxM-b-p0]. (ii) TxMem, mem (b), p=0 vs vOW 6nW: C1 bits / baseline bits / margin (+ = C1 better)

| row | baseline | C1 @floor | margin @floor | C1 @2^27 | margin @2^27 | C1 @2^30 | margin @2^30 | C1 @2^32.5 | margin @2^32.5 | C1 free-oracle (c_trial=0) | margin free | log2 s* @2^30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c2pnb176v1 | 88.14 | 115.15 | -27.00 | 121.14 | -32.99 | 123.45 | -35.31 | 125.43 | -37.29 | 107.32 | -19.17 | 36.65 |
| c2pnb208w1 | 104.27 | 134.79 | -30.52 | 140.60 | -36.33 | 142.12 | -37.86 | 143.40 | -39.14 | 126.97 | -22.71 | 42.88 |
| c2pnb272w1 | 136.46 | 174.21 | -37.76 | 180.00 | -43.54 | 181.51 | -45.05 | 182.77 | -46.31 | 166.42 | -29.96 | 54.57 |
| c2pnb304w1 | 152.54 | 193.98 | -41.44 | 199.76 | -47.22 | 201.27 | -48.73 | 202.52 | -49.98 | 186.19 | -33.65 | 60.44 |
| c2pnb368w1 | 184.67 | 233.57 | -48.90 | 239.34 | -54.67 | 240.85 | -56.18 | 242.11 | -57.43 | 225.79 | -41.11 | 72.23 |

## T3[TxM-a-best]. (ii) TxMem, mem (a), best p in {0,20,40}: C1 bits / baseline bits / margin (+ = C1 better)

| row | baseline | C1 @floor | margin @floor | C1 @2^27 | margin @2^27 | C1 @2^30 | margin @2^30 | C1 @2^32.5 | margin @2^32.5 | C1 free-oracle (c_trial=0) | margin free | log2 s* @2^30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c2pnb176v1 | 88.14 | 98.71 | -10.57 | 104.53 | -16.39 | 106.10 | -17.96 | 107.45 | -19.31 | 90.95 | -2.81 | 37.10 |
| c2pnb208w1 | 104.27 | 110.60 | -6.34 | 116.37 | -12.11 | 117.89 | -13.62 | 119.16 | -14.89 | 102.85 | 1.42 | 42.88 |
| c2pnb272w1 | 136.46 | 134.44 | 2.02 | 140.21 | -3.76 | 141.73 | -5.28 | 143.01 | -6.55 | 126.69 | 9.77 | 54.56 |
| c2pnb304w1 | 152.54 | 146.56 | 5.98 | 153.15 | -0.61 | 155.07 | -2.53 | 156.73 | -4.19 | 138.63 | 13.91 | 60.21 |
| c2pnb368w1 | 184.67 | 179.10 | 5.57 | 187.74 | -3.07 | 189.99 | -5.32 | 191.87 | -7.20 | 167.50 | 17.17 | 71.83 |

## T3[TxM-b-best]. (ii) TxMem, mem (b), best p in {0,20,40}: C1 bits / baseline bits / margin (+ = C1 better)

| row | baseline | C1 @floor | margin @floor | C1 @2^27 | margin @2^27 | C1 @2^30 | margin @2^30 | C1 @2^32.5 | margin @2^32.5 | C1 free-oracle (c_trial=0) | margin free | log2 s* @2^30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c2pnb176v1 | 88.14 | 98.71 | -10.57 | 104.53 | -16.39 | 106.10 | -17.96 | 107.45 | -19.31 | 90.95 | -2.81 | 37.10 |
| c2pnb208w1 | 104.27 | 110.60 | -6.34 | 116.37 | -12.11 | 117.89 | -13.62 | 119.16 | -14.89 | 102.85 | 1.42 | 42.88 |
| c2pnb272w1 | 136.46 | 135.33 | 1.13 | 141.10 | -4.64 | 142.60 | -6.14 | 143.86 | -7.40 | 127.56 | 8.90 | 54.57 |
| c2pnb304w1 | 152.54 | 153.98 | -1.45 | 159.76 | -7.23 | 161.27 | -8.73 | 162.53 | -9.99 | 146.19 | 6.35 | 60.44 |
| c2pnb368w1 | 184.67 | 193.57 | -8.90 | 199.34 | -14.67 | 200.85 | -16.18 | 202.11 | -17.43 | 185.79 | -1.11 | 72.23 |

## T3[MM1-a]. (iii-a) MM-1 full cost, mem (a): C1 bits / baseline bits / margin (+ = C1 better)

| row | baseline | C1 @floor | margin @floor | C1 @2^27 | margin @2^27 | C1 @2^30 | margin @2^30 | C1 @2^32.5 | margin @2^32.5 | C1 free-oracle (c_trial=0) | margin free | log2 s* @2^30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c2pnb176v1 | 81.19 | 84.23 | -3.04 | 91.19 | -10.00 | 93.03 | -11.84 | 94.57 | -13.39 | 74.95 | 6.23 | 35.46 |
| c2pnb208w1 | 97.30 | 98.59 | -1.29 | 105.98 | -8.67 | 108.01 | -10.71 | 109.75 | -12.45 | 89.14 | 8.16 | 40.26 |
| c2pnb272w1 | 129.49 | 132.11 | -2.62 | 140.75 | -11.27 | 143.01 | -13.52 | 144.89 | -15.40 | 120.49 | 8.99 | 51.67 |
| c2pnb304w1 | 145.57 | 149.91 | -4.35 | 158.56 | -12.99 | 160.81 | -15.25 | 162.69 | -17.13 | 138.26 | 7.30 | 57.55 |
| c2pnb368w1 | 177.70 | 185.58 | -7.89 | 194.23 | -16.53 | 196.48 | -18.78 | 198.36 | -20.66 | 173.94 | 3.76 | 69.33 |

## T3[MM1-b]. (iii-a) MM-1 full cost, mem (b): C1 bits / baseline bits / margin (+ = C1 better)

| row | baseline | C1 @floor | margin @floor | C1 @2^27 | margin @2^27 | C1 @2^30 | margin @2^30 | C1 @2^32.5 | margin @2^32.5 | C1 free-oracle (c_trial=0) | margin free | log2 s* @2^30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c2pnb176v1 | 81.19 | 84.29 | -3.11 | 91.23 | -10.04 | 93.05 | -11.87 | 94.58 | -13.39 | 75.02 | 6.17 | 35.48 |
| c2pnb208w1 | 97.30 | 100.99 | -3.68 | 107.92 | -10.62 | 109.73 | -12.43 | 111.24 | -13.94 | 91.64 | 5.66 | 40.95 |
| c2pnb272w1 | 129.49 | 138.82 | -9.34 | 145.75 | -16.26 | 147.55 | -18.07 | 149.06 | -19.57 | 129.49 | -0.00 | 53.41 |
| c2pnb304w1 | 145.57 | 157.81 | -12.24 | 164.73 | -19.16 | 166.53 | -20.97 | 168.04 | -22.47 | 148.48 | -2.91 | 59.67 |
| c2pnb368w1 | 177.70 | 195.83 | -18.14 | 202.75 | -25.05 | 204.56 | -26.86 | 206.06 | -28.36 | 186.51 | -8.81 | 72.25 |

## T3[mesh-a]. (iii-b) mesh area-time, mem (a): C1 bits / baseline bits / margin (+ = C1 better)

| row | baseline | C1 @floor | margin @floor | C1 @2^27 | margin @2^27 | C1 @2^30 | margin @2^30 | C1 @2^32.5 | margin @2^32.5 | C1 free-oracle (c_trial=0) | margin free | log2 s* @2^30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c2pnb176v1 | 78.33 | 81.33 | -3.00 | 87.83 | -9.49 | 89.57 | -11.24 | 91.08 | -12.75 | 72.69 | 5.64 | 37.30 |
| c2pnb208w1 | 94.24 | 94.51 | -0.27 | 100.92 | -6.68 | 102.60 | -8.36 | 104.01 | -9.77 | 85.89 | 8.35 | 42.44 |
| c2pnb272w1 | 126.08 | 120.95 | 5.13 | 127.35 | -1.27 | 129.02 | -2.94 | 130.41 | -4.33 | 112.33 | 13.75 | 52.83 |
| c2pnb304w1 | 142.02 | 134.21 | 7.81 | 140.74 | 1.28 | 142.50 | -0.48 | 143.99 | -1.97 | 125.57 | 16.45 | 58.11 |
| c2pnb368w1 | 173.91 | 164.71 | 9.20 | 172.94 | 0.97 | 175.09 | -1.17 | 176.87 | -2.96 | 153.76 | 20.15 | 70.81 |

## T3[mesh-b]. (iii-b) mesh area-time, mem (b): C1 bits / baseline bits / margin (+ = C1 better)

| row | baseline | C1 @floor | margin @floor | C1 @2^27 | margin @2^27 | C1 @2^30 | margin @2^30 | C1 @2^32.5 | margin @2^32.5 | C1 free-oracle (c_trial=0) | margin free | log2 s* @2^30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c2pnb176v1 | 78.33 | 81.33 | -3.00 | 87.83 | -9.49 | 89.57 | -11.24 | 91.08 | -12.75 | 72.69 | 5.64 | 37.30 |
| c2pnb208w1 | 94.24 | 94.51 | -0.27 | 100.92 | -6.68 | 102.60 | -8.36 | 104.01 | -9.77 | 85.89 | 8.35 | 42.44 |
| c2pnb272w1 | 126.08 | 121.44 | 4.64 | 127.84 | -1.76 | 129.51 | -3.43 | 130.91 | -4.82 | 112.81 | 13.27 | 53.03 |
| c2pnb304w1 | 142.02 | 138.42 | 3.60 | 144.83 | -2.81 | 146.50 | -4.48 | 147.89 | -5.87 | 129.78 | 12.24 | 59.75 |
| c2pnb368w1 | 173.91 | 173.66 | 0.25 | 180.06 | -6.15 | 181.73 | -7.82 | 183.13 | -9.22 | 165.03 | 8.88 | 73.72 |

## T4. Degenerate floor with c_trial = c_gen = 0 (graph bookkeeping only)

| row | log2 (kappa N/2) edge insertions | rho | margin |
|---|---|---|---|
| c2pnb176v1 | 38.54 | 78.10 | 39.56 |
| c2pnb208w1 | 46.30 | 93.98 | 47.68 |
| c2pnb272w1 | 61.91 | 125.78 | 63.87 |
| c2pnb304w1 | 69.75 | 141.71 | 71.95 |
| c2pnb368w1 | 85.48 | 173.57 | 88.09 |

(With trials free AND target generation free, s -> 1 and the only cost left is touching ~N/2 edges; this is a degenerate bound, not an attack. The 'free-oracle' columns above keep c_gen = 1 rho step per trial.)

## T5. Cross-check variants, time only, c_trial = 2^30 (C1 bits; margin vs rho)

| row | 2LP orbit (default) | 1LP orbit (q^{14/9}) | no LP (basic Gaudry) | 2LP plain (no orbit, +-1 coeffs) | orbit gain (plain - default) | orbit gain, same coef model |
|---|---|---|---|---|---|---|
| c2pnb176v1 | 76.64 (1.46) | 78.08 (0.01) | 80.46 (-2.36) | 80.73 (-2.64) | 4.10 | 5.07 |
| c2pnb208w1 | 88.18 (5.80) | 90.08 (3.90) | 96.00 (-2.02) | 92.67 (1.31) | 4.48 | 5.53 |
| c2pnb272w1 | 111.60 (14.19) | 114.37 (11.41) | 127.28 (-1.50) | 116.67 (9.12) | 5.07 | 6.13 |
| c2pnb304w1 | 123.37 (18.34) | 126.58 (15.13) | 142.98 (-1.27) | 128.67 (13.03) | 5.31 | 6.37 |
| c2pnb368w1 | 146.97 (26.60) | 151.05 (22.52) | 174.46 (-0.89) | 152.69 (20.88) | 5.72 | 6.79 |

Exponent check (d log2 T / d log2 N, N 2^60 -> 2^120): 2LP = 1.4999 (theory 1.5 = Q^(2-2/4)); 1LP = 1.5555 (theory 14/9 = 1.5556); none = 2.0000 (theory 2, LA-dominated)

## T6. Context: HOLD-D product-law floor at m = 4 (free decomposition oracle, subspace base of free size 2^l, N = 16(k-1)) vs C1 free-oracle time (c_trial = 0, c_gen = 1)

| row | N | HOLD-D m=4 plain | HOLD-D m=4 orbit | C1 free-oracle time | rho |
|---|---|---|---|---|---|
| c2pnb176v1 | 160 | 68.00 | 62.47 | 61.49 | 78.10 |
| c2pnb208w1 | 192 | 80.80 | 74.88 | 73.15 | 93.98 |
| c2pnb272w1 | 256 | 106.40 | 99.86 | 96.60 | 125.78 |
| c2pnb304w1 | 288 | 119.20 | 112.41 | 108.37 | 141.71 |
| c2pnb368w1 | 352 | 144.80 | 137.57 | 131.97 | 173.57 |

(HOLD-D lets the base size float (2^l) and divides relations by k, LA by k^2; C1 fixes the base at the F_Q-rational x-coordinates, Q = 2^{4k}, and divides the orbit count by 2k.)

## T7. Break-even log2 c_trial (C1 = baseline); 'never' = loses even at c_trial = 0

| row | time | TxM-a-p0 | TxM-b-p0 | TxM-a-best | TxM-b-best | MM1-a | MM1-b | mesh-a | mesh-b |
|---|---|---|---|---|---|---|---|---|---|
| c2pnb176v1 | 32.69 | never | never | never | never | 10.43 | 10.32 | 10.13 | 10.13 |
| c2pnb208w1 | 41.06 | never | never | 2.61 | 2.61 | 13.42 | 9.39 | 15.01 | 15.01 |
| c2pnb272w1 | 57.63 | never | never | 19.53 | 17.75 | 12.01 | never | 24.73 | 23.84 |
| c2pnb304w1 | 65.87 | never | never | 26.02 | 12.62 | 9.71 | never | 29.19 | 21.96 |
| c2pnb368w1 | 82.24 | never | never | 22.92 | never | 4.96 | never | 28.36 | 15.95 |

## T8. Single-parameter sign flips at the central point (c_trial = 2^30)

Entry = log2 multiplier on that parameter (alone) that flips the sign of the margin; '-' = no flip within 2^+-80; [in] = flip lies inside the plausible range.

| metric | row | margin @2^30 | c_trial | p_dec | kappa | LA_unit | D_fglm | RHO_AREA | N_orbits | P_MM1 |
|---|---|---|---|---|---|---|---|---|---|---|
| time | c2pnb176v1 | 1.46 | +2.69 | -2.69 | +2.69 | +3.05 [in] | - | - | +0.99 [in] | - |
| time | c2pnb208w1 | 5.80 | +11.06 | -11.06 | +11.06 | +11.65 | - | - | +3.88 | - |
| time | c2pnb272w1 | 14.19 | +27.63 | -27.63 | +27.63 | +28.37 | - | - | +9.46 | - |
| time | c2pnb304w1 | 18.34 | +35.87 | -35.87 | +35.87 | +36.68 | - | - | +12.23 | - |
| time | c2pnb368w1 | 26.60 | +52.24 | -52.24 | +52.24 | +53.20 | - | - | +17.73 | - |
| TxM-a-p0 | c2pnb176v1 | -35.31 | - | +46.71 | -46.71 | - | - | - | -17.01 | - |
| TxM-a-p0 | c2pnb208w1 | -36.77 | - | +48.81 | -48.81 | - | - | - | -16.72 | - |
| TxM-a-p0 | c2pnb272w1 | -40.07 | - | +53.29 | -53.29 | - | - | - | -17.79 | - |
| TxM-a-p0 | c2pnb304w1 | -41.79 | - | +55.59 | -55.59 | - | - | - | -18.54 | - |
| TxM-a-p0 | c2pnb368w1 | -45.32 | - | +60.31 | -60.31 | - | - | - | -20.10 | - |
| TxM-b-p0 | c2pnb176v1 | -35.31 | - | +67.97 | -46.71 | - | - | - | -17.01 | - |
| TxM-b-p0 | c2pnb208w1 | -37.86 | - | +75.04 | -48.81 | - | - | - | -16.72 | - |
| TxM-b-p0 | c2pnb272w1 | -45.05 | - | - | -53.29 | - | - | - | -17.88 | - |
| TxM-b-p0 | c2pnb304w1 | -48.73 | - | - | -55.59 | - | - | - | -19.34 | - |
| TxM-b-p0 | c2pnb368w1 | -56.18 | - | - | -60.31 | - | - | - | -22.32 | - |
| TxM-a-best | c2pnb176v1 | -17.96 | - | +35.61 | -35.61 | - | -9.01 | - | -14.62 | - |
| TxM-a-best | c2pnb208w1 | -13.62 | -27.39 | +27.17 | -27.17 | - | -6.90 | - | -9.19 | - |
| TxM-a-best | c2pnb272w1 | -5.28 | -10.47 | +10.47 | -10.47 | -11.05 | - | - | -3.49 | - |
| TxM-a-best | c2pnb304w1 | -2.53 | -3.98 | +3.98 | -3.98 | -8.12 | - | - | -1.33 | - |
| TxM-a-best | c2pnb368w1 | -5.32 | -7.08 | +7.08 | -7.08 | -21.41 | - | - | -2.36 | - |
| TxM-b-best | c2pnb176v1 | -17.96 | - | +35.61 | -35.61 | - | -9.01 | - | -14.62 | - |
| TxM-b-best | c2pnb208w1 | -13.62 | -27.39 | +27.17 | -27.17 | - | -6.99 | - | -9.19 | - |
| TxM-b-best | c2pnb272w1 | -6.14 | -12.25 | +12.25 | -10.47 | -12.35 | - | - | -3.55 | - |
| TxM-b-best | c2pnb304w1 | -8.73 | -17.38 | +17.38 | -6.09 | -17.58 | - | - | -3.50 | - |
| TxM-b-best | c2pnb368w1 | -16.18 | - | +32.21 | -10.77 | -32.51 | - | - | -6.43 | - |
| MM1-a | c2pnb176v1 | -11.84 | -19.57 | +19.57 | -19.57 | - | - | - | -6.77 | - |
| MM1-a | c2pnb208w1 | -10.71 | -16.58 | +16.58 | -16.58 | - | - | +15.24 | -5.54 | - |
| MM1-a | c2pnb272w1 | -13.52 | -17.99 | +17.99 | -17.99 | - | - | +17.23 | -6.00 | - |
| MM1-a | c2pnb304w1 | -15.25 | -20.29 | +20.28 | -20.28 | - | - | +19.11 | -6.76 | - |
| MM1-a | c2pnb368w1 | -18.78 | -25.04 | +25.00 | -25.00 | - | - | +22.91 | -8.33 | - |
| MM1-b | c2pnb176v1 | -11.87 | -19.68 | +19.67 | -19.57 | - | - | - | -6.77 | - |
| MM1-b | c2pnb208w1 | -12.43 | -20.61 | +20.61 | -16.58 | - | - | +17.26 | -5.62 | - |
| MM1-b | c2pnb272w1 | -18.07 | - | +30.01 | -17.99 | - | - | +21.77 | -7.48 | - |
| MM1-b | c2pnb304w1 | -20.97 | - | +34.84 | -20.28 | - | - | +24.83 | -8.69 | - |
| MM1-b | c2pnb368w1 | -26.86 | - | +44.65 | -25.00 | - | - | +30.99 | -11.14 | - |
| mesh-a | c2pnb176v1 | -11.24 | -19.87 | +19.87 | -19.87 | - | - | +11.69 | -8.43 | - |
| mesh-a | c2pnb208w1 | -8.36 | -14.99 | +14.99 | -14.99 | - | - | +8.63 | -5.05 | - |
| mesh-a | c2pnb272w1 | -2.94 | -5.27 | +5.27 | -5.27 | -6.65 | -2.76 | +3.13 [in] | -1.76 | - |
| mesh-a | c2pnb304w1 | -0.48 | -0.81 [in] | +0.81 [in] | -0.81 | -1.18 [in] | -0.61 [in] | +0.53 [in] | -0.27 | - |
| mesh-a | c2pnb368w1 | -1.17 | -1.64 [in] | +1.64 | -1.64 | -4.13 | - | +1.29 [in] | -0.55 | - |
| mesh-b | c2pnb176v1 | -11.24 | -19.87 | +19.87 | -19.87 | - | - | +11.69 | -8.43 | - |
| mesh-b | c2pnb208w1 | -8.36 | -14.99 | +14.99 | -14.99 | - | - | +8.63 | -5.05 | - |
| mesh-b | c2pnb272w1 | -3.43 | -6.16 | +6.16 | -5.30 | -7.75 | - | +3.64 [in] | -1.86 | - |
| mesh-b | c2pnb304w1 | -4.48 | -8.04 | +8.04 | -4.07 | -10.12 | - | +4.73 [in] | -2.01 | - |
| mesh-b | c2pnb368w1 | -7.82 | -14.05 | +14.05 | -7.02 | -17.66 | - | +8.15 | -3.50 | - |

Plausible ranges (log2 multiplier): c_trial: [-3.0, +2.5] (brief band 2^27..2^32.5 (floor 2^15.5 separate)); p_dec: [-1.0, +1.0] (H0: 1/24 within x2 either way); kappa: [+0.0, +2.0] (H2: kappa in [1, 4]); LA_unit: row-specific H3: coef small .. pess (row-specific range) (H3: coef small .. pess (row-specific range)); D_fglm: [-2.0, +0.0] (H3: FGLM state D in [2^10, 2^12] (ws = D^2 F_Q elts)); RHO_AREA: [-6.0, +6.0] (MM-1 grid 2^10..2^22); N_orbits: [+0.0, +1.0] (H1: orbit count N x[1,2] (partial orbit gain)); P_MM1: [-10.0, +10.0] (MM-1 grid P in 2^10..2^30)

## T9. Sensitivity ranking: |d margin / d log2 param| x plausible log2 width (max over rows), top 3 per metric

| metric | 1st | 2nd | 3rd |
|---|---|---|---|
| time | c_trial (swing 2.91, slope -0.53) | LA_unit (swing 2.63, slope -0.50) | N_orbits (swing 1.50, slope -1.50) |
| TxM-a-p0 | c_trial (swing 4.31, slope -0.78) | N_orbits (swing 2.26, slope -2.26) | p_dec (swing 1.57, slope +0.78) |
| TxM-b-p0 | c_trial (swing 4.31, slope -0.78) | kappa (swing 3.02, slope -1.51) | LA_unit (swing 2.61, slope -0.50) |
| TxM-a-best | c_trial (swing 4.13, slope -0.75) | D_fglm (swing 4.00, slope -2.00) | LA_unit (swing 2.62, slope -0.49) |
| TxM-b-best | D_fglm (swing 4.00, slope -2.00) | kappa (swing 3.00, slope -1.50) | c_trial (swing 2.91, slope -0.53) |
| MM1-a | P_MM1 (swing 15.04, slope +0.75) | c_trial (swing 4.14, slope -0.75) | D_fglm (swing 2.32, slope -1.16) |
| MM1-b | P_MM1 (swing 12.04, slope +0.60) | c_trial (swing 3.35, slope -0.61) | N_orbits (swing 2.41, slope -2.41) |
| mesh-a | RHO_AREA (swing 11.05, slope +0.92) | c_trial (swing 3.94, slope -0.72) | D_fglm (swing 2.37, slope -1.18) |
| mesh-b | RHO_AREA (swing 11.05, slope +0.92) | c_trial (swing 3.25, slope -0.59) | D_fglm (swing 2.37, slope -1.18) |

## T10. Verdict per metric (rows with margin > 0 at each c_trial)

| metric | @floor | @2^27 | @2^30 | @2^32.5 | @free-oracle |
|---|---|---|---|---|---|
| time | 176v1, 208w1, 272w1, 304w1, 368w1 | 176v1, 208w1, 272w1, 304w1, 368w1 | 176v1, 208w1, 272w1, 304w1, 368w1 | 176v1, 208w1, 272w1, 304w1, 368w1 | 176v1, 208w1, 272w1, 304w1, 368w1 |
| TxM-a-p0 | none | none | none | none | none |
| TxM-b-p0 | none | none | none | none | none |
| TxM-a-best | 272w1, 304w1, 368w1 | none | none | none | 208w1, 272w1, 304w1, 368w1 |
| TxM-b-best | 272w1 | none | none | none | 208w1, 272w1, 304w1 |
| MM1-a | none | none | none | none | 176v1, 208w1, 272w1, 304w1, 368w1 |
| MM1-b | none | none | none | none | 176v1, 208w1 |
| mesh-a | 272w1, 304w1, 368w1 | 304w1, 368w1 | none | none | 176v1, 208w1, 272w1, 304w1, 368w1 |
| mesh-b | 272w1, 304w1, 368w1 | none | none | none | 176v1, 208w1, 272w1, 304w1, 368w1 |

## T11. Parameter values used (defaults)

| parameter | value |
|---|---|
| n | 4 |
| p_dec | 0.041666666666666664 |
| kappa | 1.0 |
| c_trial | 1073741824.0 |
| c_gen | 1.0 |
| B | 3.0 |
| w | 8.0 |
| coef | orbit |
| D | 4096 |
| fb_factor | 1.0 |
| orbit | True |
| RHO_AREA | 65536.0 |
| P_MM1 | 1048576.0 |
| P_LA_MAX | 1024.0 |
| DP_PER_PROC | 1024.0 |
| RHO_MULTS | 10.0 |
| c_route | 1.0 |
| P_MESH_MAX | 1099511627776.0 |
| lp | 2LP |
| LA_mult | 1.0 |
| vow_bits_mode | 3n |

Citations embedded in this script:
- t_h: analysis/binstd-curve-audit/audit-certificate.txt:1-15 (t, cofactor)
- r: experiments/EXP-BINSTD-9d1b8e/stage0/five-row-symmetry-certificate.yaml:17,52,87,122,157 (r_from_dump)
- rho_formula: experiments/EXP-BINSTD-9d1b8e/specification.yaml:77-81,246-248 (corrected_rho = log2 sqrt(pi r/(4k)))
- rho_frozen: ledger/evidence/EV-BINSTD-f541ea.yaml:91-95 (O-stage0: within +-0.01 of frozen [78.10,93.98,125.78,141.71,173.57])
- vow: ledger/evidence/EV-SEMBIN-4125ec.yaml:80-87 (HEUR-VOW-CURVE T=W(1/M+1/w), Mem=3n max(w,M), W=0.886 2^{n/2}; T x Mem = 6nW on w=M)
- vow_json: experiments/EXP-SEMBIN-2c40bb/runs/RUN-SEMBIN-3ae91c/arm-b-coherent-baseline.json:1569-1600 (own_curve_min_product_log2)
- vow_record_pt: ledger/evidence/EV-SEMBIN-4125ec.yaml:180-183 (T_v = 204.33, Mem_v = 40.26 at n=409 record point)
- vow_src: knowledge/literature/KN-LIT-73f7e1.md:103-114,133-147 (0.886 = sqrt(pi/4) includes negation; 3n bits/DP upper bound)
- mm1: experiments/EXP-BINSTD-f442a9/specification.yaml:579-605,621-623 (MM-1: FC=(P+mem/RHO_AREA)*wall per phase; RHO_AREA=2^16; P_REF=2^20; rho 10 N^2 bitops/iter, P*2^10 DPs at 3 log2 l bits; Wiedemann D^2(3w log2 l + 7 (log2 l)^2); LA memory D(w(log2 D+1)+4 log2 l); P_LA_MAX=2^10)
- mm1_grid: experiments/EXP-BINSTD-f442a9/specification.yaml:359 (P in {2^10,2^20,2^30}, RHO_AREA in {2^10,2^16,2^22})
- holdd: analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-6cf862.yaml:56-69 (product-law floor min_l m! 2^(N-(m-1)l) + m 2^(2l); orbit variant relations/k, LA/k^2)
- kn_open: knowledge/open-problems/KN-OPEN-86e7e1.md:130-148 (explicit metric; compare against vOW parallel rho incl. DP storage)
```

## 6. Integrity

- sha256(c1_model.py) = 10d2b729ef5233b035cb7985f4ca574eba3a352d1151e6eff0d41ea18bc0ce05
- sha256 of this file: see `SHA256SUMS` (a file cannot contain its own hash).
