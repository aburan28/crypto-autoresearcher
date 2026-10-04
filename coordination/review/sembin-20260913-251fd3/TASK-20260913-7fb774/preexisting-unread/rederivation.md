# Blind re-derivation — TASK-20260913-7fb774 (attempt 2)

Review round: REVIEW-SEMBIN-20260913-251fd3. Joint owned: `blind_rederivation`.
Requested policy `review-adversarial` at `xhigh`; resolved model
`claude-fable-5-1-thinking-xhigh`, `model_verified: false`, `fallback_used: false`.

Everything below is this session's own arithmetic from the task card's statement
and the frozen Nagao text. No value was compared against any producer output;
none was available to this session by design. Every figure is a heuristic cost
estimate under stated conventions. No degree is measured or asserted, nothing is
executed against any curve, and nothing here is a statement about the security
of any curve.

## 0. What was read, and what was not

Read (the only paths opened, in this order):

1. `agents/validator.md`
2. `ledger/hypotheses/H-SEMBIN-4a80f3.yaml`
3. `experiments/EXP-SEMBIN-db9bc3/specification.yaml`
4. `experiments/EXP-SEMBIN-f4a17b/specification.yaml`
5. `ledger/evidence/EV-SEMBIN-71e5cd.yaml`
6. `ledger/corrections/CORR-20260913-53739b.yaml`
7. `inputs/NAGAO-2015-984/paper_fulltext.md`

`AGENTS.md` and `CLAUDE.md` were supplied to the session as always-applied
rules and were read in that form. NOT opened: `inputs/SEMAEV-2015-310/paper_fulltext.md`
(eq. (11) is quoted in CORR-20260913-53739b correction_1, which sufficed for the
Poisson form), `experiments/EXP-SEMBIN-f4a17b/runs/RUN-SEMBIN-121b59/COST-SEMBIN-8d123b.yaml`
(optional; the vOW conventions needed are stated in the task card and in
EV-SEMBIN-71e5cd O-6/O-10), and nothing in the blind set.

Disclosure: the session's initial `git status` snapshot (supplied by the runtime,
not requested) listed the *names* of untracked paths, among them
`experiments/EXP-SEMBIN-db9bc3/code/` and one `coordination/review/...` task
directory. No file under any of them was opened, listed, or grepped; only the
directory names were seen. No `git log` was run.

## 1. The statement being derived from

(Transcribed from the task card; nothing else is used as input.)

Nagao 2015/984 Theorem 1 costed per H-SEMBIN-4a80f3, cells

- A: p = 2, n = 571, omega = 2.807, C_0 = 8
- B: p = 2, n = 571, omega = 3.0,   C_0 = 3

binomial monomial-count reading: monomials = C(N + d_F, d_F), d_F = 4.

- T1 = log2(monomials), N = n(m - 1), m = n / C_0
- T2 = (omega - 1) T1   (so T1 + T2 = omega * log2 monomials = one solve)
- T3 = log2 #Fb, #Fb = m p^{C_0}
- T4 = log2(1 / Pr[decomposition succeeds]), Pr = 1 - exp(-lambda),
  lambda = prod_i #Fb_i / #E, #E ~ p^n, #Fb_i binomial with mean ~ p^{C_0}
- T5 = memory in field elements: log2(monomials) ("frozen width") or
  2 log2(monomials) ("dense width squared")
- time = log2( 2^{T1+T2+T3+T4} + 2^{omega T3} ); memory = T5
- vOW: W = 0.886 * 2^{n/2}; T = W(1/M + 1/w); Mem = 3n max(w, M);
  time_only at M = 1, w -> inf (log2 W); time_memory_product = min over
  (w, M) of T * Mem
- margins = Nagao - vOW under time_only and under the product (both T5
  readings). No F_2-operation <-> group-operation conversion.

What the frozen Nagao text contributes (Section 7, lines 746-826 of the
extraction): `k = C_0` fixed, `m ~ n/C_0`; `#Fb_i ~ p^k`, `#Fb ~ m p^k`;
`prod_i #Fb_i ~ (p^k)^m ~ p^n ~ #E`, "so the probability that decomposition
success, is O(1)"; the parenthesis that `k = 1` sometimes gives an empty
`#Fb_i`; "we must collect #Fb + 1 decompositions"; Lemma 2 charges a solve at
(monomials)^w; the linear-algebra step is (#Fb)^w. Definition 4 / Definition 8
give n(m - 1) variables. Algorithm 2 loops `while i <= #Fb`, i.e. #Fb + 1
relations.

## 2. Method

Script: `scratch/rederive.py` (raw output `scratch/rederive-output.json`,
stderr `scratch/rederive-stderr.txt`); cross-checks `scratch/check_inst_avg.py`,
`scratch/check_inst_avg2.py` with outputs beside them; reshaping to the
deliverable `rederived-values.json` by `scratch/make_values.py`. Python 3.12,
numpy 2.4.4 (used only for the FFT convolution and the Monte Carlo check).
Nothing was imported from any `experiments/` directory.

- log2 of a binomial at integer N: `math.log2(math.comb(N + 4, 4))` — exact
  integer, then one double-precision log.
- At non-integer N: `(lgamma(N+5) - lgamma(5) - lgamma(N+1)) / ln 2`.
- Log-addition: `max + log2(sum 2^{x - max})`.
- T4: `-log2(-expm1(-lambda))`, stable at both ends.

## 3. Step-by-step

### 3.1 m and its rounding (ambiguity R1)

m = n / C_0 is not an integer at either cell:

| cell | C_0 | n/C_0    | floor | ceil | nearest |
|------|-----|----------|-------|------|---------|
| A    | 8   | 71.375   | 71    | 72   | 71 (= floor) |
| B    | 3   | 190.333… | 190   | 191  | 190 (= floor) |

Three conventions are carried throughout: `floor`, `ceil`, and `exact`
(fractional m, in the style of Semaev's un-ceiled Table-3 parameter, with N and
#Fb fractional and C(N+4,4) via lgamma). Nearest coincides with floor at both
cells and is not carried separately. **Rounding m fixes the sign of km - n**:
floor gives km - n = -3 (A) / -1 (B); ceil gives +5 (A) / +2 (B); exact gives 0.
This is the one rounding decision with a material downstream effect (T4, §3.5).

### 3.2 N and T1 (ambiguities R2, R3 — both immaterial)

N = n(m - 1) per the statement. Alternative literal count from Definition 8,
N' = m k + (m - 2) n (k coordinates per X_i, n per U_i), coincides with n(m-1)
exactly when km = n and differs by |km - n| otherwise.

| cell | rounding | N          | N'        | T1 = log2 C(N+4,4) | T1 at N' | squarefree Σ_{d≤4} C(N,d) | 4 log2 N (Nagao loose, ref.) |
|------|----------|------------|-----------|--------------------|----------|---------------------------|------------------------------|
| A    | floor    | 39970      | 39967     | 56.561918 | 56.561485 | 56.561485 | 61.146520 |
| A    | ceil     | 40541      | 40546     | 56.643770 | 56.644481 | 56.643343 | 61.228376 |
| A    | exact    | 40184.125  | 40184.125 | 56.592749 | 56.592749 | —         | 61.177352 |
| B    | floor    | 107919     | 107918    | 62.293529 | 62.293475 | 62.293368 | 66.878357 |
| B    | ceil     | 108490     | 108492    | 62.323981 | 62.324087 | 62.323821 | 66.908810 |
| B    | exact    | 108109.333 | 108109.333| 62.303697 | 62.303697 | —         | 66.888526 |

R2 (N vs N') moves T1 by ≤ 0.0007 bits. R3 (C(N+4,4) vs the field-equation-
reduced squarefree count Σ_{d≤4} C(N,d), which is what a p = 2 Macaulay
block actually holds) moves it by ≤ 0.0005 bits. Rounding m moves T1 by 0.082
(A) / 0.030 (B) bits between floor and ceil. Nagao's loose N^4 is 4.585 bits
above the binomial count (log2 24 minus a negligible term); it is listed for
reference only, since the card fixes the binomial reading.

### 3.3 T2 and one solve

T2 = (omega - 1) T1; T1 + T2 = omega T1.

| cell | rounding | T2         | T1 + T2 (one solve) |
|------|----------|------------|---------------------|
| A    | floor    | 102.207386 | 158.769304 |
| A    | ceil     | 102.355292 | 158.999061 |
| A    | exact    | 102.263097 | 158.855846 |
| B    | floor    | 124.587057 | 186.880586 |
| B    | ceil     | 124.647961 | 186.971942 |
| B    | exact    | 124.607394 | 186.911091 |

### 3.4 T3 (ambiguity R4 — immaterial)

#Fb = m p^{C_0}. Algorithm 2 and Section 7 say #Fb + 1 relations are collected;
both log2 #Fb (the card's statement) and log2(#Fb + 1) are given. #Fb is taken
as its mean m p^k (it is itself a random sum of the #Fb_i).

| cell | rounding | #Fb      | T3 = log2 #Fb | log2(#Fb + 1) | omega T3 (linear algebra) |
|------|----------|----------|---------------|---------------|---------------------------|
| A    | floor    | 18176    | 14.149747 | 14.149826 | 39.718340 |
| A    | ceil     | 18432    | 14.169925 | 14.170003 | 39.774979 |
| A    | exact    | 18272    | 14.157347 | 14.157426 | 39.739673 |
| B    | floor    | 1520     | 10.569856 | 10.570804 | 31.709567 |
| B    | ceil     | 1528     | 10.577429 | 10.578373 | 31.732286 |
| B    | exact    | 1522.667 | 10.572384 | 10.573332 | 31.717153 |

R4 (+1) is ≤ 0.001 bits. The linear-algebra term omega T3 is 134-166 bits below
the decompose term at every cell, so the log-addition in (b) changes `time` by
less than 1e-30 bits; it is carried but is numerically invisible.

### 3.5 T4 — the term the statement does NOT pin down (ambiguities R1, R5, R6, R7)

lambda = prod_i #Fb_i / #E with #E = p^n (the +1 and the Hasse term are
< 2^{-280} relative; no cofactor is in the statement and none is applied).

**R5 — the binomial parametrisation of #Fb_i.** HEUR-1 says "a binomial count
with mean ~ p^k". Three parametrisations with that mean are carried:

- P1: #Fb_i = 2 · Bin(p^k, 1/2). Each of the p^k x-values in the coset is on
  the curve with probability 1/2 and then contributes the pair ±P. This is the
  model HEUR-1's own `random_model_justification` describes ("the x-coordinate
  map is 2-to-1 onto a set of density ~1/2"). Mean p^k, variance p^k,
  P[empty] = 2^{-p^k}. Taken as PRIMARY.
- P2: #Fb_i = Bin(2 p^k, 1/2). The literal "binomial with mean p^k". Variance
  p^k / 2, P[empty] = 2^{-2 p^k}.
- P3: #Fb_i = Poisson(p^k), the limit of Bin(#E, p^{k-n}) (each point lands in
  the coset independently). Variance p^k, P[empty] = e^{-p^k}.

Per-coset statistics (exact sums over the pmf; conditioning is on #Fb_i > 0):

| cell (p^k) | model | P[#Fb_i = 0] | E[log2 #Fb_i \| >0] | log2 p^k − E[log2 · \| >0] | Var[log2 · \| >0] | E[#Fb_i \| >0] |
|---|---|---|---|---|---|---|
| A (256) | P1 | 8.64e-78  | 7.997166 | 0.002834 | 0.008211 | 256.000000 |
| A (256) | P2 | 7.46e-155 | 7.998587 | 0.001413 | 0.004085 | 256.000000 |
| A (256) | P3 | 6.62e-112 | 7.997173 | 0.002827 | 0.008178 | 256.000000 |
| B (8)   | P1 | 3.906e-3  | 2.900485 | 0.099515 | 0.347923 | 8.031373 |
| B (8)   | P2 | 1.526e-5  | 2.949772 | 0.050228 | 0.156930 | 8.000122 |
| B (8)   | P3 | 3.355e-4  | 2.898708 | 0.101292 | 0.327820 | 8.002685 |

**R6 — which expectation.** Three defensible readings, plus the degenerate
one and a reference row:

- `arith` — expectation of the PRODUCT: lambda = E[prod #Fb_i] / p^n = (p^k)^m / p^n
  = 2^{km − n}. Independent of P1/P2/P3. This is the form HEUR-2 states
  ("prod_i #Fb_i ~ #E gives lambda ~ 1"), exact at fractional m.
- `arith_cond_*` — the same conditioned on every coset being nonempty:
  lambda = (E[#Fb_i | >0])^m / p^n.
- `geo_cond_*` — expectation of the LOGARITHM (typical instance):
  log2 lambda = m · E[log2 #Fb_i | >0] − n. Conditioning is forced: without it
  E[log2 #Fb_i] = −∞ because P[#Fb_i = 0] > 0, which makes the unconditioned
  geometric T4 = +∞ (`geo_uncond_*`; P[all m cosets nonempty] is reported in
  its place).
- `inst_avg_cond_*` — instance-averaged success probability,
  T4 = −log2 E[1 − exp(−lambda) | all nonempty], the quantity an attacker with
  one random (V, v_1..v_m) sees on average. Computed for integer m only, by an
  m-fold convolution of the exact per-coset distribution of log2 #Fb_i on a
  2^{-10}-bit grid (each atom split between its two neighbouring grid points so
  the mean is preserved exactly), via FFT. `inst_avg_uncond_*` multiplies by
  P[all nonempty] (an empty coset gives lambda = 0).
- `nagao_literal` — Pr = 1, T4 = 0. Nagao's "O(1)" read as 1. NOT a HEUR-2
  reading; it is ARM M's free-yield null and is carried for reference only.

**Cross-checks on the instance-averaged reading (cell A, floor, P1):** FFT at
grid 2^{-10} and 2^{-13} give E[Pr] = 0.1153915 and 0.1153912; a direct
shift-and-add convolution with no FFT gives 0.1153915 (mass sums to 1.0 to nine
digits). Monte Carlo gives 0.115160 ± 0.000059 (1e6 samples, seed 20260914) and
0.115351 ± 0.000029 (4e6 samples, seed 7); pooled, about 3σ below the
deterministic value, with the sampler's per-coset mean of log2 #Fb_i also 1.6σ
low (7.99715680 ± 5.4e-6 against the exact 7.99716555). The two deterministic
routes agree to seven digits and are grid-insensitive, so the deterministic
value is the one reported; the Monte Carlo gap is ≤ 0.003 bits in T4 and is
recorded rather than resolved. A Gaussian (CLT) approximation gives 0.1154244.

T4 in bits (P[all nonempty] in the last column is for the P1 model):

| cell | rounding | km−n | arith | arith_cond P1 | geo_cond P1 | geo_cond P2 | geo_cond P3 | inst_avg cond P1 | inst_avg uncond P1 | inst_avg cond P3 | P[all nonempty] P1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | floor | −3 | 3.089229 | 3.089229 | 3.278964 | 3.183619 | 3.278463 | 3.115391 | 3.115391 | 3.115384 | 1.000000 |
| A | ceil  | +5 | 0.000000 (1.8e-14) | 0.000000 | 0.000000 (1.2e-12) | 0.000000 | 0.000000 | 0.000039 | 0.000039 | 0.000038 | 1.000000 |
| A | exact | 0  | 0.661728 | 0.661728 | 0.784146 | 0.721602 | 0.783812 | — | — | — | 1.000000 |
| B | floor | −1 | 1.345677 | 0.619962 | 19.907860 | 10.543852 | 20.245521 | 6.660135 | 7.732982 | 7.057907 | 0.475380 |
| B | ceil  | +2 | 0.026669 | 0.000309 | 17.007380 | 7.597330 | 17.346817 | 5.334111 | 6.412605 | 5.659282 | 0.473523 |
| B | exact | 0  | 0.661728 | 0.187188 | 18.941032 | 9.561067 | 19.279286 | — | — | — | 0.474760 |

Instance-to-instance spread of log2 lambda (sd, P1): 0.76 bits at cell A, 8.1
bits at cell B.

Reading of this table (values only, no interpretation of the hypothesis):

- At cell A (C_0 = 8) every finite HEUR-2 reading at a given rounding lies
  within 0.2 bits of the arithmetic one; the rounding of m (R1) is the whole
  T4 story there, 0 → 3.09 bits between ceil and floor, because lambda_arith
  = 2^{km−n} jumps by a factor 2^{C_0} = 256 between the two integer choices.
- At cell B (C_0 = 3) the arithmetic and geometric expectations differ by
  18.3 bits at exact m (0.66 against 18.94, P1), because the per-coset
  deficit log2 p^k − E[log2 #Fb_i | >0] ≈ 0.10 bits is multiplied by m ≈ 190.
  The instance-averaged reading sits between them (6.66 bits at floor,
  conditioned). Under P1 about half of all random instances at C_0 = 3
  contain an empty coset (P[all nonempty] = 0.475), which is the degenerate
  case the unconditioned geometric reading records as +∞. P2 halves the
  geometric deficit and P3 matches P1 to within 0.35 bits. **The statement
  determines T4 at cell B only after both the rounding of m and the
  expectation are chosen; the card asked for values under each and they are
  above.**
- The hypothesis text (HEUR-2) states the inverse yield as "~0.663 bits".
  −log2(1 − e^{−1}) = 0.661728 bits. The 0.0013-bit difference is immaterial
  and is noted only because the card asks that every discrepancy be recorded.

**R7 — #E.** p^n exactly. p^n + 1 and the Hasse term are below 2^{-280}
relative and are ignored; a group-order cofactor is not part of the statement
and would enter as +log2 h in lambda's denominator if one were applied.

### 3.6 T5 (ambiguity R8 — units)

T5_frozen = T1; T5_dense = 2 T1, in field elements. EQS4 (Definition 8) is a
system over F_p = F_2, so one field element is one bit and T5 in bits equals
T5 in field elements; this is the reading used when T5 is added to `time` and
compared with vOW's memory in bits. If "field elements" were read as F_{2^n}
elements, every T5 and both product margins would rise by log2 571 = 9.157
bits; that reading is not adopted and is recorded only as the alternative.

| cell | rounding | T5_frozen | T5_dense |
|---|---|---|---|
| A | floor | 56.561918 | 113.123836 |
| A | ceil  | 56.643770 | 113.287539 |
| A | exact | 56.592749 | 113.185497 |
| B | floor | 62.293529 | 124.587057 |
| B | ceil  | 62.323981 | 124.647961 |
| B | exact | 62.303697 | 124.607394 |

The relation matrix ((#Fb + 1) × #Fb entries, ≈ 2 T3 ≈ 21-28 bits) is not part of
the stated T5 and would be invisible under log-addition to it.

### 3.7 Charged Nagao time (b)

time = log2(2^{T1+T2+T3+T4} + 2^{omega T3}). Since omega T3 is 134-166 bits below
the first term, time = T1 + T2 + T3 + T4 to all shown digits.

| cell | rounding | arith | arith_cond P1 | geo_cond P1 | geo_cond P2 | geo_cond P3 | inst_avg cond P1 | inst_avg uncond P1 | nagao_literal (ref.) |
|---|---|---|---|---|---|---|---|---|---|
| A | floor | 176.008281 | 176.008281 | 176.198015 | 176.102671 | 176.197515 | 176.034443 | 176.034443 | 172.919052 |
| A | ceil  | 173.168986 | 173.168986 | 173.168986 | 173.168986 | 173.168986 | 173.169026 | 173.169026 | 173.168986 |
| A | exact | 173.674921 | 173.674921 | 173.797338 | 173.734795 | 173.797005 | — | — | 173.013193 |
| B | floor | 198.796118 | 198.070403 | 217.358301 | 207.994293 | 217.695963 | 204.110576 | 205.183423 | 197.450441 |
| B | ceil  | 197.576040 | 197.549680 | 214.556750 | 205.146701 | 214.896188 | 202.883482 | 203.961975 | 197.549371 |
| B | exact | 198.145204 | 197.670664 | 216.424508 | 207.044543 | 216.762762 | — | — | 197.483476 |

With log2(#Fb + 1) in place of log2 #Fb every entry rises by ≤ 0.001 bits
(`time_with_T3_plus1` in the JSON).

### 3.8 vOW baseline (c), n = 571

W = 0.886 · 2^{285.5}: log2 W = 285.5 + log2 0.886 = **285.325379** bits.

- `time_only` at M = 1, w → ∞: T = W(1 + 1/w) → W, so **285.325379** bits.
- `time_memory_product`: T · Mem = W(1/M + 1/w) · 3n · max(w, M). Put
  a = max(w, M). If w ≥ M the product is 3nW(w/M + 1) ≥ 6nW; if M ≥ w it is
  3nW(1 + M/w) ≥ 6nW; equality in both cases exactly when w = M, for ANY
  common value. So the minimum is 6nW, attained along the whole line w = M
  (there is no distinguished point on it), and equals
  log2(6 · 571) + log2 W = 11.742309 + 285.325379 = **297.067688** bits.
  A grid over (log2 w, log2 M) ∈ {0..80}² returns the same 297.067688 at
  every diagonal point (argmin reported at (0, 0) only because it is the first
  visited). This agrees with the structural statement in EV-SEMBIN-71e5cd O-6
  (product ≥ 2 · 3n · W, invariant along the curve).

Memory unit: bits (3n bits per stored or held point, per O-6/O-10).

### 3.9 Margins (d), Nagao − vOW, bits, positive = Nagao worse

No conversion between F_2 operations and group operations is applied on the
time axis, and none between F_2 elements and bits on the memory axis (identity
for p = 2). Product margin = (time + T5) − 297.067688.

| cell | rounding | T4 reading | margin_time_only | margin_product_frozen | margin_product_dense |
|---|---|---|---|---|---|
| A | floor | arith        | −109.317098 | −64.497489 | −7.935571 |
| A | floor | geo_cond P1  | −109.127363 | −64.307754 | −7.745836 |
| A | floor | inst_avg P1  | −109.290936 | −64.471327 | −7.909409 |
| A | ceil  | arith        | −112.156392 | −67.254932 | −10.611163 |
| A | ceil  | geo_cond P1  | −112.156392 | −67.254932 | −10.611163 |
| A | exact | arith        | −111.650458 | −66.800018 | −10.207270 |
| A | exact | geo_cond P1  | −111.528040 | −66.677601 | −10.084853 |
| B | floor | arith        | −86.529260  | −35.978041 | +26.315488 |
| B | floor | geo_cond P1  | −67.967077  | −17.415858 | +44.877671 |
| B | floor | inst_avg P1  | −81.214802  | −30.663583 | +31.629946 |
| B | ceil  | arith        | −87.749339  | −37.167668 | +25.156313 |
| B | ceil  | geo_cond P1  | −70.768628  | −20.186957 | +42.137024 |
| B | exact | arith        | −87.180174  | −36.618787 | +25.684911 |
| B | exact | geo_cond P1  | −68.900870  | −18.339483 | +43.964214 |

The complete set (every rounding × every T4 reading × both memory readings,
with P2/P3 variants and the `nagao_literal` reference row) is in
`rederived-values.json` under `cells.<cell>.roundings.<rounding>.margin_*`.

### 3.10 The reading the hypothesis text implies (for the Coordinator's comparison)

HEUR-2's formal statement fixes the operating point at prod #Fb_i ~ #E, lambda
~ 1. That is the `exact` rounding with the `arith` expectation. It is recorded
in the JSON as `reading_implied_by_hypothesis_text` and is NOT privileged
over the others; it is flagged so the Coordinator can locate the producer's
convention. Under it: cell A — T1 56.592749, T2 102.263097, T3 14.157347,
T4 0.661728, T5 56.592749 / 113.185497, time 173.674921, margins
−111.650458 / −66.800018 / −10.207270; cell B — T1 62.303697, T2 124.607394,
T3 10.572384, T4 0.661728, T5 62.303697 / 124.607394, time 198.145204,
margins −87.180174 / −36.618787 / +25.684911.

## 4. Spreads that summarise the ambiguities (bits)

| quantity | cell A | cell B |
|---|---|---|
| T1, floor → ceil | 0.082 | 0.030 |
| T3, floor → ceil | 0.020 | 0.008 |
| T4 arith, floor − ceil | 3.089 | 1.319 |
| T4 geo_cond P1 − arith, at exact m | 0.122 | 18.279 |
| T4 inst_avg cond P1 − arith, at floor m | 0.026 | 5.314 |
| time (arith), floor − ceil | 2.839 | 1.220 |
| time, range over all finite HEUR-2 readings and roundings | 173.169 – 176.198 | 197.550 – 217.696 |
| N vs N' on T1 | ≤ 0.0007 | ≤ 0.0001 |
| C(N+4,4) vs squarefree count on T1 | ≤ 0.0005 | ≤ 0.0002 |
| log2 #Fb vs log2(#Fb + 1) on T3 | 0.0001 | 0.0009 |
| linear-algebra log-addition on time | < 1e-30 | < 1e-30 |
| "field elements" as F_{2^n} instead of F_2 on T5 (not adopted) | +9.157 | +9.157 |

## 5. Ambiguities found (consolidated)

- **R1 — rounding of m = n/C_0.** Not an integer at either cell. floor / ceil /
  exact carried. Material through T4 (3.09 bits at A, 1.32 at B under `arith`)
  because it fixes km − n; otherwise ≤ 0.08 bits.
- **R5 — binomial parametrisation of #Fb_i.** P1 (2·Bin(p^k, ½), HEUR-1's own
  justification), P2 (Bin(2p^k, ½)), P3 (Poisson). Immaterial under `arith`;
  under the geometric reading at C_0 = 3 it moves T4 by ~9 bits (P1 vs P2).
- **R6 — arithmetic vs geometric expectation, and conditioning.** ≤ 0.2 bits
  at C_0 = 8; ~18 bits at C_0 = 3. The unconditioned geometric reading is
  +∞ at both cells (P[empty coset] > 0); at C_0 = 3 the P1 probability that
  all cosets are nonempty is 0.475. The instance-averaged reading is a third,
  intermediate value (5.3-7.7 bits at C_0 = 3).
- **R2 — N = n(m−1) vs m k + (m−2) n.** ≤ 0.0007 bits.
- **R3 — C(N+4,4) vs squarefree Σ C(N,d).** ≤ 0.0005 bits.
- **R4 — #Fb vs #Fb + 1 relations.** ≤ 0.001 bits.
- **R7 — #E = p^n vs p^n + 1 ± 2p^{n/2}, and cofactor.** < 2^{-280} relative;
  cofactor not in the statement.
- **R8 — T5 "field elements".** Read as F_2 elements = bits (EQS4 is over
  F_p); F_{2^n} reading would add 9.157 bits and is not adopted.
- **Text discrepancy.** HEUR-2 quotes ~0.663 bits for the inverse yield at
  lambda = 1; the value is 0.661728.
- **Cross-check discrepancy.** Monte Carlo for the instance-averaged reading
  sits ~3σ below the two agreeing deterministic routes (≤ 0.003 bits in T4);
  recorded, deterministic value reported.

## 6. Verdict on the joint

`holds` — the quantity is derivable from the statement up to the recorded
ambiguities. T1, T2, T3, T5 and both vOW charges are determined to within
0.1 bits once a rounding of m is chosen, and the rounding options are
enumerated. T4 is determined only after two further choices (R1 and R6) that
the statement leaves open, and at C_0 = 3 those choices span ~19 bits; the
card anticipated exactly this and asked for values under each reading, which
are given. Had the card not asked for readings, the honest verdict at cell B
would have been that the statement does not determine T4.

This is a report on the `blind_rederivation` joint only. It is not a validation
of any run, supports no ECDLP claim, demonstrates no speedup, and says nothing
about any curve.
