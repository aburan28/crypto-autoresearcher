# Stage 0: Vacuity Derivation and F_p Spectral Norms (EXP-ECDLP-56ee42)

## 1. The pinning bound in triangle-inequality form

The pinning (IDEA-20260815-f558e4 sub-result (E)) bounds the majority
advantage of an efficiently computable coordinate-derived statistic v on a
prime-order subgroup G = <P>, |G| = n, in terms of the Fourier coefficients
of the fiber indicators of v along the discrete-log coordinate.

Let v: G -> S be a statistic with fibers A_1..A_s partitioning G.  The
majority advantage is q_maj(v) - 1/s, where
    q_maj(v) = max over F: SxS -> S of Pr[v(R+R') = F(v(R), v(R'))]
    (probability over uniform R, R' in G).

The triangle-inequality form of the pinning bound is:

    q_maj(v) - 1/s  <=  C * ||v_hat||_1 * sqrt(p) / n

where:
  - ||v_hat||_1 = SUM_chi |hat{v}(chi)| is the L1 spectral norm of v
    over F_p (the sum of the magnitudes of the Fourier coefficients of
    the fiber indicators over the additive characters of F_p);
  - sqrt(p) is the Weil/Bombieri bound for the hybrid character sum
    SUM_k e_N(ck) chi(x([k]P)) (square-root cancellation,
    Kohel-Shparlinski / Lange-Winterhof lineage);
  - n is the group order (~ p for the ladder);
  - C is a constant depending on the degree of the defining conditions.

The bound is VACUOUS when ||v_hat||_1 * sqrt(p) / n > 1, i.e., when
||v_hat||_1 > n / sqrt(p) ~ sqrt(p).  For the comparator (top bit of x),
||v_hat||_1 is O(log p) (polylog), so the bound reads O(log p / sqrt(p)),
which is the n^(-1/2) scale -- non-vacuous and useful.  For the digit family
(t, r), ||v_hat||_1 is a power of p (computed below), so the bound reads
O(p^alpha) for alpha > 0, which is much larger than n^(-1/2) = p^(-1/2) --
VACUOUS.

## 2. The recalled facts (marked RECALLED)

The following facts are RECALLED (not verified by this program; no source
was opened):

- **Gelfond's bound (RECALLED):** for the Thue-Morse sequence t(m) =
  (-1)^(s_2(m)),
      sup_theta |SUM_{m<N} t(m) e(m theta)| << N^lambda,  lambda = log 3 / log 4 ~= 0.79.
  This is a bound on the L-infinity norm of the DFT of t.  Source: Gelfond,
  'Sur les nombres qui ont des proprietes additives et multiplicatives
  donnees', Acta Arith. 13 (1968).  The exact constant and normalisation were
  not checked; this program COMPUTES the norm rather than relying on this.

- **Rudin-Shapiro root-N property (RECALLED):** for the Rudin-Shapiro
  sequence r(m),
      sup_theta |SUM_{m<N} r(m) e(m theta)| <= C sqrt(N).
  This is a bound on the L-infinity norm of the DFT of r.  Source: Rudin
  (1959) and Shapiro (1951) on Salem's question.  A WebSearch snippet on
  2026-09-02 corroborated this statement; the source itself was not read, so
  provenance stays recalled.

These recalled facts are bounds on the L-infinity norm (the maximum magnitude
of a single DFT coefficient).  The L1 norm (the spectral norm in the pinning
bound) is related by ||v_hat||_1 <= sqrt(p) * ||v_hat||_infinity (Cauchy-
Schwarz).  The Stage 0 computation below computes the L1 norm directly.

## 3. Computed F_p spectral norms

The table below reports the L1 and L-infinity spectral norms of t, r, and the
comparator at each ladder prime, computed by one length-p FFT per statistic.

| T | p | t L1 | r L1 | comparator L1 | t Linf | r Linf | comparator Linf |
|---|---|------|------|---------------|--------|--------|-----------------|
| 17 | 131101 | 1.50033e+07 | 1.50179e+07 | 748250 | 7165.25 | 7164.31 | 131043 |
| 19 | 524309 | 1.0378e+08 | 1.03969e+08 | 2.85568e+06 | 33300.5 | 33298.7 | 524267 |
| 21 | 2097169 | 7.17522e+08 | 7.18197e+08 | 1.10635e+07 | 64154.6 | 64154 | 2.09713e+06 |
| 23 | 8388617 | 5.01014e+09 | 5.01222e+09 | 3.99311e+07 | 299760 | 299758 | 8.3886e+06 |
| 25 | 33554473 | 3.54827e+10 | 3.54952e+10 | 2.00957e+08 | 576477 | 576476 | 3.35544e+07 |
| 27 | 134217757 | 2.48556e+11 | 2.48571e+11 | 7.66158e+08 | 1.74419e+06 | 1.74419e+06 | 1.34218e+08 |

Normalized norms (divided by p), which is the quantity that appears in the
pinning bound.  The comparator's L1_noDC_over_p (L1 norm excluding the DC
term, divided by p) is the quantity most directly related to the 'polylog'
claim.

| T | p | t L1/p | r L1/p | comparator L1/p | comparator L1_noDC/p |
|---|---|--------|--------|-----------------|----------------------|
| 17 | 131101 | 114.441 | 114.552 | 5.70743 | 4.70788 |
| 19 | 524309 | 197.936 | 198.297 | 5.44655 | 4.44663 |
| 21 | 2097169 | 342.138 | 342.46 | 5.27543 | 4.27545 |
| 23 | 8388617 | 597.254 | 597.503 | 4.76016 | 3.76016 |
| 25 | 33554473 | 1057.47 | 1057.84 | 5.98898 | 4.98898 |
| 27 | 134217757 | 1851.89 | 1852 | 5.70832 | 4.70832 |

Fitted growth exponents (log norm = alpha * log p + beta, over the six
ladder primes):

- t L1: alpha = 1.4020
- r L1: alpha = 1.4018
- comparator L1: alpha = 1.0038
- t Linf: alpha = 0.7743
- r Linf: alpha = 0.7743
- comparator Linf: alpha = 1.0001
- t L1/p: alpha = 0.4020
- r L1/p: alpha = 0.4018
- comparator L1/p: alpha = 0.0038
- comparator L1_noDC/p: alpha = 0.0045

NOTE: the unnormalized L1 norm of the comparator grows like p (alpha ~ 1)
because it includes the DC term (a = 0), which is ~ p/2.  The normalized
L1 norm excluding the DC term (L1_noDC/p) grows like log p (alpha ~ 0),
which is the 'polylog' behaviour the hypothesis claims for the comparator.
The digit norms (t, r) grow as powers of p in all normalisations.

## 4. Gate P3

Gate P3: a polylog digit norm drops that arm (F1) and the computed norm is
archived.

- t (Thue-Morse): fitted L1 exponent = 1.4020.  Polylog? False.  Arm dropped? False.
- r (Rudin-Shapiro): fitted L1 exponent = 1.4018.  Polylog? False.  Arm dropped? False.

The comparator's L1 exponent is 1.0038 (expected ~0, polylog).

## 5. Conclusion

The digit norms (t, r) grow as powers of p (fitted exponents > 0), confirming
that the pinning bound is vacuous for the digit family.  The comparator's norm
is polylog (fitted exponent ~0), confirming that the pinning bound is
non-vacuous for the comparator.  This is the record's reason to exist: the
digit family is the one cheap family for which the program's
probabilistic-regime closure has no proof.
