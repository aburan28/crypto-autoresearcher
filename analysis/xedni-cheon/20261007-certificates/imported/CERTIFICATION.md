# Exact certification of the two Cheon candidates

Date: 2026-10-07. This addendum supersedes the earlier unresolved primality, rank, and dependence assessment for these two candidates. It leaves the original bounded search and its raw results intact.

| Requested check | Result | Evidence |
| --- | --- | --- |
| Certify all six factor magnitudes | Complete: all six are prime | Recursive Lucas certificates in `candidate_certificates.json`, checked by a separate verifier |
| Certify rational rank | Complete: both ranks are exactly 2 | Two exact isogeny-descent images, each of size 4 |
| Check dependence of the supplied lifts | Complete: the two points are independent, including modulo torsion | Three independent classes P,Q,T in E(Q)/2E(Q) |
| Obtain a usable rational relation | Refuted for these pairs | Independence excludes every nonzero integer relation, even with a torsion term |
| Establish general lifting impossibility or a speedup | Not claimed | The conditional family obstruction below has explicit additional hypotheses |

## Inputs and results

The original source is [Cheon–Lee–Hahn–Chee, *Elliptic Curve Discrete Logarithms and Wieferich Primes*, §4](https://www.math.snu.ac.kr/~jhcheon/publications/2000/JWISC00_CLH.pdf), presented on 2000-01-25 according to the [IEICE record](https://www.ieice.org/publications/ken/summary.php?contribution_id=KJ00002127102&expandable=0&ken_id=ISEC&lang=en&presen_date=2000%2F1%2F25&schedule_id=AN10060811_99%28584%29&society_cd=ESSNLS&year=2000). A separate manuscript posting date remains unestablished.

Write E: y²=x(x²+Ax+B) and D=A²−4B. For both candidates, P has x=703²=494209 and Q has x=−439²=−192721.

| n | A | B | y(P) | y(Q) |
| --- | --- | --- | --- | --- |
| −1793 | 8697422826248745145 | −1793727297677166359919097 | 1112566596170849 | −817754998855289 |
| 181 | 8698021425756814477 | −1792472369211529197803773 | 1112910971874647 | −817620706622627 |

For n=−1793, the certified primes are

```
|B| = 1793727297677166359919097
f+  = 8697425991446308729
f−  = 8697419661053158397
```

For n=181, they are

```
|B| = 1792472369211529197803773
f+  = 8698024591934109793
f−  = 8698018259581495997
```

In each case D=f+ f−, with f+ and f− distinct. Exact checks confirm nonsingularity, point membership, coefficient reduction to A≡−1 and B≡16 mod 353, point reductions P→(9,63), Q→(17,183), and good reduction at 353. The finite-field modulus is checked by trial division through its square root.

## Unconditional primality certificates

The generator factors n−1 for each prime being proved and recursively certifies those factors. For every distinct prime q dividing n−1, it supplies a witness a_q satisfying

```
a_q^(n−1) ≡ 1 mod n
gcd(a_q^((n−1)/q) − 1, n) = 1.
```

The verifier checks the full factorization product, every recursive prime proof down to the literal base case 2, and every modular identity. This is the Lucas full-n−1 criterion, not a probable-prime acceptance rule. To see why it proves primality, take any prime divisor p of n. The witness for q forces its multiplicative order mod p to contain the full q-power dividing n−1. Therefore n−1 divides p−1. Since p≤n, this forces p=n.

The generation route uses Miller–Rabin only to decide where to attempt a certificate; the independent verifier does not import the generator, factor numbers, or call a probable-prime test. Its accepted certificate contains 70 prime nodes and 215 modular-witness checks, proving all six root values. The use of different witnesses for different q is valid by the argument above.

## Exact rank proof

Use the standard two-isogeny descent described in [Cremona, *Algorithms for Modular Elliptic Curves*, §3.6, pp. 84–85](https://johncremona.github.io/book/fulltext/chapter3.pdf). Its ingredients here are the isogenous curve

```
E′: v²=u(u²−2Au+D)
φ:E→E′, φ(x,y)=(y²/x², y(x²−B)/x²)
φ̂:E′→E, φ̂(u,v)=(v²/(4u²), v(u²−D)/(8u²)).
```

The maps have their standard extensions at O and the respective (0,0) kernel points; φ̂φ=[2]. Let α map a nonzero x coordinate to its squareclass in Q*/Q*², O to 1, and T=(0,0) to B. Define α′ similarly on E′, with α′(T′)=D. Their kernels are respectively φ̂(E′(Q)) and φ(E(Q)). Standard descent gives

```
rank E(Q) = log2 |im α| + log2 |im α′| − 2.
```

For each candidate B=−r, with r prime. Every α-image is represented by a signed squarefree divisor of B, so it belongs to {1,−1,r,−r}. The points Q and T provide α(Q)=−1 and α(T)=−r, so all four classes occur.

For E′, A>0 and D>0. A negative u would make u(u²−2Au+D)<0, so no real point has negative u. Its possible α′-images are therefore only {1,f+,f−,D}. These are all attained: T′ supplies D, and the following rational point supplies f−:

```
s=703
u=A+2s²−2y(P)/s=f−
v=−2s u
R=(u,v) on E′, with φ̂(R)=P.
```

The concrete R values are

```
n=−1793: R=(8697419661053158397, −12228572043440740706182)
n=181:   R=(8698018259581495997, −12229413672971583371782).
```

The independent verifier checks R's equation and φ̂(R)=P exactly, and checks φ̂φ=[2] on both supplied points using a separately implemented doubling law. Both descent images thus have exactly four elements, and both ranks equal 2. This uses actual rational witnesses and exhaustive squareclass support bounds; there is no BSD or analytic-rank assumption and no unresolved Selmer-to-rational-point step.

## Why P and Q are independent

Suppose ε_P P+ε_Q Q+ε_T T belongs to 2E(Q), with each ε in {0,1}. Applying α gives (−1)^ε_Q B^ε_T=1 in squareclasses. Because the classes of −1 and B=−r are independent, ε_Q=ε_T=0.

If ε_P=1, then P=2S for some rational S. Since P=φ̂(R) and 2S=φ̂φ(S), the point R−φ(S) must be O or T′. Applying α′ would force α′(R) to be 1 or D. But α′(R)=f−, and f− is neither class, because f+ and f− are distinct primes. This is a contradiction.

Thus P,Q,T are independent in E(Q)/2E(Q). D is nonsquare, so T is the only nonidentity rational 2-torsion point. These three classes, with rational rank exactly 2, certify that P and Q are independent in the free part. In particular, no nonzero integers m,n can make mP+nQ torsion. This is an exclusion of all coefficients, not a bounded relation search. It does not assert that P and Q form a saturated integral basis; an odd index is not computed or needed.

## Conditional family obstruction derived here

The independence argument applies beyond these two n values under the following explicit conditions: B=±r with r prime; P=(s²,y_P), Q=(−t²,y_Q) with nonzero rational s,t; and

```
f±=A+2s²±2y_P/s
D=f+ f−,
```

where f+ and f− are distinct positive primes. The same R=(f−,−2s f−) is a rational dual-isogeny preimage of P. The two descent-image lower bounds force rank at least 2, and the mod-2 argument proves P,Q independent. A>0 is needed for our simple exact rank upper bound on the two examples, not for this independence argument.

This is our derived conditional obstruction, not a theorem attributed to the original paper. In this distinct-prime branch of the paper's signed-square construction, achieving the prime screen cannot create a dependent pair. Other sign choices, nonprime factor patterns, or lifting families are outside the lemma. The result therefore closes these candidates and this conditional branch without ruling out Xedni lifts generally.

Compared with Xedni V2: its built-in doubling relation survived 68 synthetic checks but reached one residue per prime; its 1,944 fits from 24 finite pairs supplied zero rational relations within coefficient bound 8. Here, both published candidate lifts are verified, but all rational relation coefficients are excluded by a proof. Neither result demonstrates a general computational advantage.

## Reproduction, controls, and accounting

Run from the archive directory, or from the workspace with the paths below:

```bash
python research-watch/certify_candidates.py > research-watch/certificate_generation.log
python research-watch/verify_candidate_certificates.py > research-watch/certificate_verification.json
```

The scripts resolve input files relative to their own directory, so they also work after extraction under another path. Python 3.12.14, standard library only. Generation seed: 20261007; wall-time budget: 300 seconds; no unsuccessful certificate generations. The retained run took approximately 0.017 seconds to generate and 0.009 seconds to verify; exact elapsed values are in the logs. The 11 recorded Pollard–Brent attempts totaled 14,117 recorded batched inner iterations; these counters exclude the unrecorded outer advance loops, trial division, primality-routing tests, and modular-exponentiation work. They are not a complete arithmetic-operation count or a scaling claim.

Verification includes four deliberately corrupted inputs: a Lucas witness, a point ordinate, the sign of the dual preimage, and the discriminant. All four were rejected with the specific reason retained in the JSON. No assertion failures or timeouts occurred on the accepted input. Available-tool probes found no Sage, PARI/GP, Magma, SymPy, cypari2, FLINT, or gmpy2; these were environment observations, not mathematical failures. The exact certificate route did not require those packages.

Costs include the local factor searches, all recursive certificates, algebraic checks, source compatibility checks, and corruption controls. They exclude the already-reported 4,001-parameter original scan, source retrieval, code preparation, and the mathematical derivation written above. No recovery stage exists for these lifts because the required rational dependence is refuted. No production target was used and no repository was edited.
