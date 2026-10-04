# Methodological note — EXP-BINSTD-f14cbb

## Scope

Structural-certificate / arithmetic measurement for the KN-OPEN-095df5 torus
row under H-BINSTD-41d8b2. **No curve ECDLP**, no GHS/decomposition attack at
n>=131, no factor-base construction, no rho competitiveness claim.

## Certificate vocabulary

Every run manifest sets `certificate.kind: none` (closed set:
`discrete_log | decomposition | key_recovery | none`). This experiment emits
structural cyclotomic and Lemma-L observations only.

## Stage 0 instrument

Moebius product for `Phi_k(2)` with `v_p(2^d-1)` via modular lifting. Does
**not** assume the recalled cyclotomic-divisor lemma
(`p|Phi_k(a) <=> k=p^j ord_p(a)`); that lemma is what the census tests on
`k<=20000`. Exact `Phi_130(2)` uses the integer Moebius product plus the
`(2^65+1)/(8193*11)` cross-check.

## Stage 1 / 2 instrument

Composite-field arithmetic `F_(2^{k n}) = F_(2^k)·F_(2^n)` (`composite_field.py`)
with CRT relative Frobenius. Self-contained `gf2n_local.py` (schoolbook);
optional conceptual kinship to `EXP-CERTBIN-e94b27/impl/gf2n.py` but **no import**.

## Claim guards

- Do **not** claim Couveignes–Lercier primary text was read.
- Do **not** claim a break, factor base, or rho competitiveness.
- Timeout / OOM / crash → `failed_infrastructure`, **never** outcome A/B/C.
- Measured columns (sets, valuations, dims, stability, null counts, wall_s,
  peak_rss) stay separate from modeled/analytic priors (HEUR-H1 2^-8 cap;
  17030 unknowns/slot).
- Amazon Bedrock prohibited.
- No AUXIN edits; no H/EXP/IDEA status edits by the executor.

## Outcomes

Outcomes A/B/C are recorded as comparisons against preregistered predictions
for the Coordinator/Reviewer; this packet reports observations only.
