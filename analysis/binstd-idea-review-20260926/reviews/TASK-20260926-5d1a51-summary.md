# Lane R2 (TASK-20260926-5d1a51) summary — the nine `design_after` BINSTD proposals

Adversarial re-read of the nine `design_after` proposals under `RQ-BINSTD-b6f698`,
against the ranking context of `DEC-20260924-99ce20`, the product-law floor table
(BRIEF §2), and independent arithmetic. Reviews are advisory input to the next
`/coordinate` selection point; they change no status and approve nothing.

## Verdict table

| idea | verdict | agrees with hold? | one-line concrete experiment | successor seam |
| --- | --- | --- | --- | --- |
| d11575 | sound_with_corrections | agrees (HOLD-H, T2) | 5×9 F_{2^16} GHS census + toy c\|d conorm-norm=0 check at dk'≤41; instruments gf2n/curve.py, cover builder new (missing: Sage) | separate "collapse vs low-filtration" small-m cells via conjugate period 16/gcd(c,16) |
| 0e3641 | sound | agrees (consolidate into d11575) | toy composite-k′ cell F_{2^36}, divisors c=3,c=9 same period, check genus agrees | none (subsumed by d11575) |
| f37254 | sound | agrees (HOLD-I, merge cdca3a) | trinomial vs pentanomial at n=17 via φ transport; Macaulay first-fall degree (macaulay.py); missing: WDSat for conflicts | sparsity as continuous term-count variable + basis-disclosure amendment |
| 9d12bd | sound_with_corrections | agrees (HOLD-I, merge cdca3a) | CNF-XOR c_leaf axis at F_{2^9} (x^9+x+1) with width-matched relabelling null; missing: WDSat | (shared with f37254); lift the relabelling-null pattern |
| 99294c | sound | agrees (HOLD-I, fold into ICPERF) | ECC2K-130 field poly vs type-2 normal basis at toy n; Macaulay solving degree; missing: WDSat | unify model/order/basis into one ICPERF boundary-table coordinate |
| 8ac1ea | sound | agrees (HOLD-J, file under NISTBIN) | K/B 2×2 factorial at F_{2^23}, Macaulay rank profile M3 (macaulay.py); missing: WDSat for M4 | transferability of a solving-degree bound across curves vs constant-vector weight |
| 8278db | sound | agrees (HOLD-L, T4) | reproduce (A)(B)(C) arithmetic + toy T_k per-trial cost at g≤8; missing: msolve/Magma for higher g | rho_reg=g/log₂q as a standing overclaim tripwire on every cover/decomposition cell |
| 2e2a58 | sound_with_corrections | agrees (HOLD-M) | reproduce KN-LIT-096 ECC2K-130 figures + rho overhead P/(2D) on toy cells + Krylov chain vs shape-matched null; missing: sparse-LA engine | search ECDLP binary relation matrices for exploitable spectral structure |
| 9e5383 | sound_with_corrections | agrees (HOLD-N) | WDSat conflict ratio on F_{4^17} stable subspace vs **primitive-prime** null (n=37, NOT n=31); missing: WDSat | primitive-prime (ord_n(2)=n−1) vs non-primitive prime as the clean stability null |

## Which of the lane's ideas are worth designing next, and why

1. **8278db (high)** — the most valuable record in the lane. It is a model of the
   inventor-protocol §4 closure standard: it computes a dramatic 27–73-bit
   "apparent break" *specifically to discredit it* (regime ratio ≥1 at 3/5 rows,
   per-trial cost at arity 10–22 unmeasured) and files the cell OPEN with the
   missing quantity named. Its `rho_reg = g/log₂q` tripwire generalises to guard
   the whole reachability table against misapplied asymptotics. Design after
   Gorla-Massierer is read at source; review-breakthrough on any move to DEFINED.
2. **8ac1ea (high)** — the best-designed experiment. The K-163/B-163 single-variable
   pair and the C-GK null (sparse S₃ without τ, which exists in no standard) are the
   missing control for every "Koblitz" claim in the corpus. M3 (Macaulay rank
   profile) is the decisive, solver-free, preprocessing-immune discriminator and
   runs on the existing pure-Python impl. Route the measured cost to RQ-NISTBIN.
3. **2e2a58 (high, cost-model correction)** — the only lane record that can *invert*
   a verdict: a time-axis "break" is defeatable on the memory axis by N^{1/(m+1)}.
   Its two instruments (parallel-rho counters, sparse-LA engine) are shared with
   b19793 and 6028ed, so build once. Pin the √2 unit ambiguity in the null-curve
   control first.
4. **d11575 (high, but literature-gated)** — highest information gain per compute,
   but its C1 closure hinges on the unread Hess theorem and the whole live-lane
   table is dominated by unread MMT. Design only after both are read at source.
5. **f37254 / 9d12bd / 99294c (medium)** — merge into one cdca3a basis-invariance
   design; constant-factor audits, no exponent. Their Step-0 arithmetic is free and
   either closes the axis or names a basis-disclosure debt.
6. **0e3641 (medium)** — a proof, not an experiment; a section of d11575's design.
7. **9e5383 (medium, needs re-selection)** — good instrument reuse but its
   null-object justification is arithmetically wrong (see below); re-select null
   arms to primitive primes before design.

## ECC2K-130 bearing, in one line each

None of the nine is an attack on ECC2K-130 (n=131 prime, no subfield). d11575/0e3641
(GHS) and 8278db (trace-zero variety) are **structurally empty at n=131** and confirm
it as the prime-degree null. 8278db's implied arity m=k−1=10–22 is the m≥5 regime the
floor table flags as the only hope — but on the composite curves, with per-trial cost
unmeasured, not on ECC2K-130. f37254/9d12bd/99294c/8ac1ea are **constant-factor** at
best (basis/coefficient changes cannot move an exponent); ECC2K-130's own b=1 makes
8ac1ea's E2 (weight-1 constant vector) apply, but only as a constant. 2e2a58 is the
one that **directly reframes** the ECC2K-130 rho baseline: memory (N^{1/(m+1)}), not
parallel width, is the binding axis. 9e5383's intended null reasoning is correct *for*
ECC2K-130 (ord_131(2)=130 ⇒ no useful stable subspace) but false for its own n=31 arms.

## Arithmetic checks performed (all by short Python, no solver)

- **Multiplicative orders (load-bearing for 9e5383, 8ac1ea, HOLD-N/J/S/T):**
  ord_31(2)=**5** (⇒ n=31 hosts f=7 ⇒ 128 nontrivial Frobenius-stable subspaces —
  **9e5383's null reasoning is wrong, HOLD-N confirmed**); ord_37(2)=36=n−1 (f=2, the
  primary null arm is genuinely trivial); ord_29(2)=28 (f=2, confirms HOLD-J A10:
  n=29 hosts no stable subspace, harmless since 8ac1ea uses an arbitrary V);
  ord_41(2)=20 (f=3, so 9e5383's "poor-n" n=41 is not poor); ord_163(2)=162 (K-163
  hosts no stable subspace); ord_131(2)=130 (ECC2K-130 primitive, dims 0,1,130,131 —
  matches KN-OPEN-095df5); ord_17(4)=ord_4(17)=**4** ⇒ f=5 ⇒ 32 stable subspaces
  (9e5383 (C) correct).
- **d11575 rho and margins:** matched rho 0.886√l/√(2k), l=2^{s−0.5} reproduces
  77.85, 93.73, 125.53, 141.45, 173.31 (record 77.9…173.3); c=4k time q^{1.75}=2^{7k}
  = 77,91,119,133,161; advantages 0.8,2.7,6.5,8.5,12.3 (record 0.9…12.3); memory
  q^{7/8}=2^{3.5k}=38.5…80.5. All reproduce. log₂(8!)=15.30 (the GTTD wash constant).
- **The 0.5-bit gap (ranking A4):** the brief's canonical sqrt(π·r/(4k)) with k=prime
  gives 78.35, 94.23, 126.03, 141.95, 173.81 — exactly **0.50 bit** above d11575's
  sqrt(π·r/(8k)) column on every row. Confirms A4; changes no verdict.
- **8278db (T4 latent figure):** naive q^{2−2/g}(k−1)! = 50.6, 58.2, 74.3, 82.7,
  100.5 bits; margins below rho 27.3, 35.5, 51.3, 58.8, 72.8 (record identical, "27
  to 73 bits"); regime ratio (k−1)/16 = 0.625, 0.750, 1.000, 1.125, 1.375 (=1 at
  k=17). All reproduce; the figure is a certified-invalid artifact, correctly handled.
- **0e3641 divisor counts:** τ(16)=5; τ(176)=10, τ(144)=15, τ(240)=20, τ(336)=20;
  period formula n(c)=d/gcd(c,d) reproduces d11575's two families (c=2→8, c=22→8).
- **2e2a58 internal consistency:** 60.9−35.63=25.27 (the three KN-LIT-096 figures
  agree); 2^35.63·32 B = 2^40.63 B ≈ 1.55 TiB (record ~1.5 TiB); θ=2^−35 ⇒ D=2^25.9
  points·32 B ≈ 1 GiB (record ~1 GiB). All reproduce.
- **Irreducibility (f37254/9d12bd/8ac1ea):** x^163+x^7+x^6+x^3+1 irreducible over F_2
  (FIPS-163 pentanomial); x^233+x^74+1 irreducible (FIPS-233 trinomial); **no**
  irreducible trinomial x^163+x^k+1 exists (scanned k=1..162 — confirms NIST's
  Swan-theorem rationale, now checked not recalled); x^9+x+1 irreducible (9d12bd's
  Stage-0 cell).
- **8ac1ea deployed rho:** B-163 negation-only 0.886√r at r=2^162 = 80.83 (record
  80.83, exact); K-163 Koblitz sqrt(π r/(4n)) = 76.65 vs record 77.16 (0.5-bit
  convention gap, non-load-bearing). ECC2K-130 sqrt(π l/(4·131)), l=2^128.5 ≈ 2^60.6
  (brief quotes 2^60.8; order-of-magnitude consistent).

## Files written

- `analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-d11575.yaml`
- `analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-0e3641.yaml`
- `analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-f37254.yaml`
- `analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-9d12bd.yaml`
- `analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-99294c.yaml`
- `analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-8ac1ea.yaml`
- `analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-8278db.yaml`
- `analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-2e2a58.yaml`
- `analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-9e5383.yaml`
- `analysis/binstd-idea-review-20260926/reviews/TASK-20260926-5d1a51-summary.md`
