#set document(title: "Small-prime splitting of the NIST/ANSI prime-field curves", date: datetime(year: 2026, month: 10, day: 29))
#set page(paper: "a4", margin: (x: 2.2cm, y: 2.3cm), numbering: "1")
#set text(font: ("Libertinus Serif", "New Computer Modern"), size: 10.5pt)
#set par(justify: true, leading: 0.62em)
#set heading(numbering: "1.")
#set math.equation(numbering: "(1)")
#show figure.caption: set text(size: 9pt)
#show table: set text(size: 9pt)
#show link: set text(fill: rgb("#1b4f8a"))

#align(center)[
  #text(size: 16pt, weight: "bold")[Small-prime splitting of the NIST/ANSI prime-field curves:\ a prime-order null, a cutoff sweep, and a frozen held-out test]
  #v(0.4em)
  Isogeny Labs research program (crypto-autoresearcher) \
  29 October 2026 · study `research/nist_seed_split_null_20261029`
]

#v(0.6em)
#block(inset: (x: 1.2em))[
  *Abstract.* A retrospective observation says the published 1997--98 NIST/ANSI prime-field curves have fewer _split_ small primes, odd primes $ell <= 691$ at which $Delta = t^2 - 4p$ is a nonzero square, than the eleven named prime-order seed candidates passed over in the same generator streams. The most extreme case is prime239v1, with 42 splits against 61--71 for the five omitted 239-bit curves. We test three objections. (i) *Prime-order confound.* All nineteen curves have prime order, so no omitted curve gains forced splits from small factors of $n$. Under an exact Chebotarev null conditioned on prime order, the mean split count is 59.7--60.2 (s.d. 5.5) instead of 62. The correction is 0.5--1.4 splits, and small factors of the twist order contribute 0--4 forced splits per curve. Neither explains the gap. (ii) *Cutoff choice.* On the nineteen curves, the within-field pair score of 25/25 occurs only for $B in {691, 701, 709, 769}$, and is 19--23 elsewhere. Even so, a look-elsewhere correction over 655 prime cutoffs leaves $p approx 0.006$, both by random-curve Monte Carlo and by exact label permutation. (iii) *Replication.* We froze the statistic at $B = 691$ in a committed protocol and applied it to the 42 unpublished draft-eligible curves in the same streams that were _not_ among the named eleven. The association *does not replicate*: held-out curves exceed published ones in 0.574 of 102 within-field pairs (one-sided permutation $p = 0.29$). The held-out percentiles fit the null (KS $D = 0.153$, 5% critical value 0.210), and one unpublished 192-bit curve has 44 splits. What survives is one low outlier, prime239v1, at the 0.06th percentile. Among the 61 eligible curves examined, a minimum that extreme has null probability about 0.05. No known mechanism connects few small rational isogenies with discrete-logarithm hardness. We find no evidence of a split-count selection rule.
]

= The claim under test

The recovered `lrand48`/SHA-1 seed streams behind the X9.62/NIST prime-field curves contain prime-order candidates that were not published. Eleven of them, five 239-bit, three P-224, two 192-bit and one P-256, have been named as _omitted_ and compared with the eight published curves of the same fields: prime192v1--v3, secp224r1, prime239v1--v3 and prime256v1. The repository's open problem `problems/nist-seed-selection-rule-unexplained.md` records many earlier features tested on these nineteen curves.

The observation under test counts, for each curve, the odd primes $ell <= 691$ that _split_:
$ S(E) = \#{ ell "odd prime", 3 <= ell <= 691 : (Delta \/ ell) = +1 }, quad Delta = t^2 - 4p, $
where $t = p + 1 - n$. A split prime is an Elkies prime: Frobenius has eigenvalues in $FF_ell$, and $E$ has two rational $ell$-isogenies. The reported pattern is that published curves have smaller $S$ in every same-field comparison. A critique of that claim raised a prime-order confound, forking paths (the cutoff 691, the ramified convention, a 4-field sign test), and the absence of a mechanism. This paper tests each objection with exact arithmetic and then runs one frozen out-of-sample test.

= Data

*Nineteen named curves.* Exact $p, n$ and EC1 curve UIDs come from the archived record
#block(inset: (left: 1em))[`nist_seed_1997_selection_extension_20261023/sea_signature/runs/scan-20261023T1840Z/raw.json`] (SHA-256 `4a0df1de…48fe`), whose Legendre symbols were independently verified in Sage by that study. Every $n$ is prime (checked again here).

*Held-out cohort.* `nist_seed_1997_acceptance_20261024` classifies 69 seed positions in the six streams that pass the November 1997 X9.62 draft's numerical checks with certified prime order. 10 are published and 59 unpublished, and the named eleven are a retrospective subset of the 59. The other 48 unpublished positions (labels `order_too_wide_only`, `opposite_root_only`) never entered the 691 observation. 42 lie in the four comparison fields and 6 in P-384. Their $p, n$ come from the 82 branch-level certificates in `nist_seed_selection_20261016/raw/full_prime_order_certificates.jsonl`. The two square-root branches at one seed give isomorphic curves or quadratic twists ($t -> plus.minus t$), so both have the same $Delta$ and the script asserts this. Each position therefore contributes one split count.

= A prime-order null model

== Forced splits

*Lemma.* Let $ell$ be an odd prime. If $ell | n = p + 1 - t$, then $t equiv p + 1$ and $Delta equiv (p-1)^2 space (mod ell)$. So $ell$ splits unless $p equiv 1 space (mod ell)$, in which case it ramifies. The same holds if $ell$ divides the twist order $p + 1 + t$.

This is the critique's mechanism. It cannot separate the groups here, because both groups have prime $n$. The twist does contribute: the twist orders have small odd factors $<= 691$ on 18 of 19 curves, 0--4 per curve, and the published curves have no fewer of them. Removing those primes from the count (variant `split-twist` below) leaves the picture unchanged.

== The Chebotarev null

For a random curve over $FF_p$ and a small prime $ell != p$, the Frobenius conjugacy class in $"GL"_2(FF_ell)$ is asymptotically distributed like a uniformly random matrix of determinant $p$. Castryck and Hubrechts make this precise for the number of points modulo an integer. Given $d = p mod ell$, the number of $2 times 2$ matrices over $FF_ell$ with trace $u$ and determinant $d$ is $ell^2 + ell chi(u^2 - 4d)$, where $chi$ is the Legendre symbol. Prime order excludes Frobenius with eigenvalue 1, which removes $u equiv 1 + d$. Hence
$ P_ell^"split" = (sum_(u != 1+d, space chi(u^2-4d) = 1) (ell^2 + ell)) / (sum_(u != 1+d) (ell^2 + ell chi(u^2 - 4d))). $
Treating the primes as independent gives an exact Poisson-binomial law for $S$ in each field. A curve's position is its mid-percentile $100 dot (P(X < S) + P(X = S) \/ 2)$.

#figure(
  table(columns: 5, align: (left, right, right, right, right), stroke: 0.4pt,
    table.header([Field], [Mean, all curves], [Mean, prime order], [Shift], [s.d., prime order]),
    [192-bit], [61.08], [59.70], [$-1.38$], [5.51],
    [224-bit], [60.62], [60.08], [$-0.53$], [5.53],
    [239-bit], [61.12], [59.72], [$-1.40$], [5.51],
    [256-bit], [60.69], [60.18], [$-0.51$], [5.54],
  ),
  caption: [Null split count over the 124 odd primes $3 <= ell <= 691$. Conditioning on prime order moves the mean by about one split. The shift is larger when many small $ell$ divide $p - 1$, where the excluded eigenvalue-1 class is all split. Source: `runs/results.json`.],
) <tab:null>

*Validation.* (a) Over two random 48-bit primes, 1,500 real prime-order curves $y^2 = x^3 - 3x + b$ per field, point-counted with PARI's SEA, matched the model: means 60.11 and 60.08 against 60.20 and 60.30, and KS distances 0.023 against a 5% critical value of 0.035 (`runs/validation48_stdout.log`). (b) The 42 held-out curves over the real fields fit the null as well (§5). We did not run 10,000 SEA counts per real field: without PARI's `seadata` modular-polynomial package, no prime-order count over these fields finished within 10 minutes on four cores. That run remains open.

= Exploratory analysis of the nineteen curves

#figure(image("fig_null.svg", width: 100%),
  caption: [Exact prime-order null for $S$ (grey) with the nineteen curves at $B = 691$. Orange triangles are omitted and blue circles published; markers with equal values are stacked. Source: `runs/results.json`, `figures.py`.]) <fig:null>

#figure(
  table(columns: 3, align: (left, left, left), stroke: 0.4pt,
    table.header([Field], [Omitted: $S$ (percentile)], [Published: $S$ (percentile)]),
    [192-bit], [61 (59.3), 62 (66.1)], [v1 60 (52.2), v2 58 (38.0), v3 57 (31.3)],
    [224-bit], [53 (10.1), 56 (23.1), 59 (42.3)], [secp224r1 50 (3.4)],
    [239-bit], [71 (97.9), 67 (90.6), 66 (87.2), 63 (72.3), 61 (59.2)], [v1 *42 (0.06)*, v2 57 (31.2), v3 57 (31.2)],
    [256-bit], [58 (34.8)], [prime256v1 57 (28.4)],
  ),
  caption: [Split counts and mid-percentiles under the prime-order null at $B = 691$. P-256 (57 vs 58) and the 192-bit field are within noise. Source: `runs/results.json`.],
) <tab:pct>

== Cutoff sweep

#figure(image("fig_sweep.svg", width: 100%),
  caption: [Top: fraction of the 25 within-field pairs with the omitted curve's $S$ above the published curve's, against cutoff $B$, for all 655 prime cutoffs $53 <= B <= 5003$. The dashed line is the same score with prime239v1's 5 pairs removed. Dotted lines are null quantiles of the _maximum over the grid_. Bottom: mid-percentiles of the eight published curves. Sources: `runs/lookelsewhere.json`, `runs/permute.json`.]) <fig:sweep>

The score reaches 25/25 only on the narrow plateau $B in {691, 701, 709, 769}$ (@fig:sweep). It is 19--23 at the other cutoffs tabulated in `runs/results.json` (101, 251, 397, 997, 2003, 5003), with or without ramified primes counted as split and with or without twist-forced splits. prime239v1 is most extreme near $B = 571$ (percentile 0.009), stays below 1% for $359 <= B <= 1367$, and rises to 11% by $B = 5003$.

== Correcting for the choice of cutoff

We assessed the pair score at its best cutoff, maximised over the whole grid, in two ways:

- *Random-curve null.* We drew 20,000 synthetic sets of nineteen prime-order curves on the archived fields and labels (seed 20261029). The null 0.50, 0.90 and 0.99 quantiles of the grid maximum are 18, 22 and 24. $P("max" >= 25) = 0.0055$, and $P(S_691 "score" >= 25) < 5 times 10^(-5)$.
- *Exact label permutation.* Over all 4,480 within-field relabellings of the observed nineteen curves, $p = 0.0065$ for the grid maximum and $1\/4480$ at 691.
- *Without prime239v1.* The remaining 20 pairs are still 20/20 on the same plateau, and median 15/20 over the grid.

These corrections cover the choice of $B$, but not the choice of statistic. This statistic was formed after many other features had been examined on the same nineteen curves (Elkies-only CRT cutoff, Atkin residue density, conductor and genus ranks, twist embedding degrees, order sparsity and others; see the open problem). Its exploratory $p approx 0.006$ cannot be read as confirmatory. The test that can is a new sample.

= Frozen held-out test

`PROTOCOL.md` was committed (`bd5d146bb`) before any held-out curve was computed. It fixes the statistic ($S$ at $B = 691$, prime-order null), the population, a single confirmatory test, and the decision rule: within-field pairs (held-out, published) in the four fields, fraction with the held-out curve higher (ties count 1/2), a one-sided within-field label-permutation $p$ from 200,000 draws, and replication if $p <= 0.05$. `AMENDMENT.md` corrects a count typo in the protocol (48 for 42 in the four fields) and changes nothing else.

#figure(image("fig_heldout.svg", width: 100%),
  caption: [Split counts at $B = 691$ by field. Grey squares are the 42 + 6 held-out unpublished draft-eligible curves, orange the named eleven, blue the published curves including P-384. Source: `runs/heldout.json`.]) <fig:heldout>

*Primary result.* Held-out curves exceed published ones in *0.574* of 102 pairs (permutation $p = 0.29$). *The association does not replicate.*

*Secondary results* (descriptive):

- The 42 held-out percentiles are consistent with uniform: KS $D = 0.153$ against a 5% critical value of 0.210.
- The named eleven exceed the held-out curves in 0.630 of 115 within-field pairs ($p = 0.13$). They sit somewhat high among unpublished curves, which is what a retrospectively picked subset of a noisy statistic would show.
- Published P-384 (54 splits, percentile 14.5) ranks lowest of 7 among its field's eligible curves, a rank probability of 1/7.
- The held-out-over-published fraction at the six other cutoffs is 0.66--0.71. This sensitivity table is reported, not tested. Choosing a cutoff from it would repeat the forking path the protocol exists to prevent.

= Discussion

*What the objections change.* The prime-order objection is correct in principle (Lemma) but negligible in size here. The omitted curves are prime-order too, and conditioning on prime order moves the mean by about one split. The forking-path objection is borne out. The perfect 25/25 belongs to a narrow cutoff plateau. Once the statistic is frozen and applied to curves it was not tuned on, the published-versus-unpublished difference is indistinguishable from chance. The high counts of the named eleven look like a property of that particular subset.

*What survives.* prime239v1 alone is a genuine low value: 42 splits, $P(X <= 42) = 8.3 times 10^(-4)$. Among the 8 published curves the minimum has null probability about $1 - (1 - 8.3 times 10^(-4))^8 approx 0.0066$. Among all 61 eligible curves examined in the four fields it is about $0.049$, before any correction for $B$. An unpublished 192-bit curve reaches 44. We regard this as an unremarkable extreme.

*Mechanism.* A split prime gives $E$ two rational $ell$-isogenies. Nothing in the generic, Pollard-rho, MOV/Frey--Rück, anomalous, Weil-descent or index-calculus analyses of prime-order curves makes the discrete logarithm easier on a curve with more or fewer rational small isogenies. The isogeny class's ECDLP difficulty is uniform up to polynomial-time isogeny walks (Jao--Miller--Venkatesan). The only historically plausible link runs through point-counting cost: Elkies primes make SEA _faster_ (Shparlinski--Sutherland). A designer avoiding slow counts would favour _more_ splits, the opposite of the observed direction, as the earlier `sea_signature` study already noted. So the observation has neither a security motive nor, after the held-out test, a statistical signal.

*Limitations.* The null treats primes as independent and Frobenius as exactly equidistributed. This was checked at 48 bits ($n = 3000$) and on 42 real-field curves, but not with 10,000 real-field SEA counts. The eight published curves are the same in exploration and test, so the held-out test replicates only the unpublished side. Monte Carlo $p$-values carry binomial error of about $sqrt(p(1-p)\/N)$.

= Reproduction

All commands run from the study directory with Python 3, `numpy` and, for validation only, `cypari2`. Wall times on this host are given.

#set text(size: 8.5pt)
```
RAW=../nist_seed_1997_selection_extension_20261023/sea_signature/runs/scan-20261023T1840Z/raw.json
python3 analysis.py      $RAW runs/results.json                    # 7 s
python3 lookelsewhere.py $RAW runs/lookelsewhere.json 20000 20261029  # 18 s
python3 permute.py       $RAW runs/permute.json                   # 1 s
python3 heldout.py $RAW ../nist_seed_1997_acceptance_20261024/analysis.json \
   ../nist_seed_selection_20261016/raw/full_prime_order_certificates.jsonl runs/heldout.json  # 1 s
python3 validate48.py    # ~25 min, PARI SEA at 48 bits
python3 figures.py $RAW  # matplotlib; then typst compile paper.typ
```
#set text(size: 10.5pt)

= References

#set text(size: 9pt)
#set par(justify: false)
- W. Castryck, H. Hubrechts. The distribution of the number of points modulo an integer on elliptic curves over finite fields. _Ramanujan J._ 30 (2013).
- R. Schoof. Counting points on elliptic curves over finite fields. _J. Théor. Nombres Bordeaux_ 7 (1995) 219--254.
- I. E. Shparlinski, A. V. Sutherland. On the distribution of Atkin and Elkies primes. _Found. Comput. Math._ (2014).
- D. Jao, S. D. Miller, R. Venkatesan. Expander graphs based on GRH with an application to elliptic curve cryptography. _J. Number Theory_ 129 (2009) 1491--1504.
- ANSI X9.62 working draft, 17 November 1997, §F.3.2 (archive.org `x962-11-17-97`).
- Internal: `research/nist_seed_1997_selection_extension_20261023/sea_signature/`, `research/nist_seed_1997_atkin_20261024/`, `research/nist_seed_1997_acceptance_20261024/`, `problems/nist-seed-selection-rule-unexplained.md`.
