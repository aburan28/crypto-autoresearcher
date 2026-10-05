# Idea-generator report: RQ-ECDLP-bc7a54 (the invertible half), 2026-10-03

Policy `research-deep`; runtime fallback: the subagent inherits the session
model (`fallback_used: true`). No Bedrock. No runs. No outputs, timings or
citations were fabricated. Every number in the proposals is either hand
arithmetic, labelled as such, or a forced value.

## IDs

| id | used | class | side of the duality | priority |
|---|---|---|---|---|
| IDEA-20261003-cd1903 | yes | mechanism | impossibility, in the algebraic-omega model M_deg | high |
| IDEA-20261003-76df35 | yes | mechanism | impossibility, in the spectral class K (uncertainty principle) | high |
| IDEA-20261003-0c5564 | yes | mechanism (building block) | re-poses the object: graded omega, price of recognition | medium |

All three pre-minted IDs were used and none was left unused. Files written:
`ledger/proposals/IDEA-20261003-{cd1903,76df35,0c5564}.yaml` and this report.
Each draft was rewritten once by this agent before handback, and none had been
committed. In cd1903, a plain YAML scalar contained ` #`, which would have
truncated it. In 0c5564, a transform name was wrong. No other file was touched.
The YAML was not machine-parsed (this agent has no shell), so the dispatcher
must run the strict parse and `tools/validate_ledger.py`. Every `prior_art`
KR row and KN ref was checked to exist on disk.

## What the three ideas are, in one line each

- **cd1903, Theorem W.** A degree-d polynomial F agrees with log_g Q on at most
  2 + K_d sqrt(p)(1 + ln pn) points. The proof is Kohel–Shparlinski plus
  completion; d = 1 is covered by the retrieved Lemma 1.
  - Regime (i), a total polylog-degree omega, is closed at exactly α = 1/2.
  - Regime (ii), a promised-input omega within the n^{1-α} budget, is closed
    only for α > 3/4.
  - The n^{1/3} point sits in the window (1/2, 3/4]. Only the sqrt(p) error
    term keeps that window open. A random-graph heuristic, H1, would close it,
    and the exact census A(1)/A(2) on toy curves tests H1.
  - The anomalous curve is the stated ceiling: its omega is cheap as a
    straight-line program, but the theorem forces it to have high degree.
- **76df35, Theorem U (uncertainty).** For every D, |D| ≤ 4(C sqrt(p) + 1) A_x(D) A_L(D),
  where A_x and A_L are Wiener norms of the x-profile and the log-profile.
  - Consequence: no interval-type chi and no kangaroo/structured-exponent omega
    share a dense set. This makes the duality a theorem over class K at
    exponent exactly 1/2.
  - The scope number is A_L(W(m,w)), the exponent-side Wiener norm of the
    low-weight set. It needs no curve and one FFT. It decides whether D_w falls
    inside the theorem.
- **0c5564, Lemma V and the exchange law.**
  - Lemma V: a total coordinate omega is its own chi, by verifying with one
    scalar multiplication. So "invertible but not recognizable" is empty for
    coordinate omegas, and D_w is invertible only by generation.
  - A partial omega that supplies a fraction β of the log's bits is priced by
    the 4-vector (α, β, γ, κ): density, bits, omega cost and native-chi cost
    exponents.
  - A chi-less claw beats rho iff α − γ > 1/2 and α + β − γ > 1.
  - A native chi is necessary exactly on the strip 0 < β ≤ 1 − α.
  - The note's D_x and D_w are the two boundary lines of this diagram.

These three axes are distinct from the 2026-09-20 axes and from each other:

- 2026-09-20: cubical representation, Freiman branching, query-bounded generic
  P·T, detector calibration.
- This session: function-class agreement (cd1903), a bilinear spectral set-size
  bound (76df35), and graded accounting (0c5564).

The nearest internal ancestors are IDEA-20260815-f558e4 (E)/(F) and
IDEA-20260902-c17bf6. Both pin one statistic linearly; the deltas are recorded
in each file.

## Recommended first test: IDEA-20261003-cd1903, Stage 1 (the A(1) census)

Why it comes first:

- **Cost.** It is exact integer incidence counting, O(n^2) per curve up to
  p = 2^16 (minutes per curve). It needs only a discrete-log table and an
  anchor-slope loop.
- **Controls are built in.** A planted-line positive on the relabelled null, the
  j = 0 orbit count, and an anomalous ceiling arm. Each has a forced value, so
  a broken instrument shows itself.
- **It discriminates two explanations that change a conclusion.**
  - E-RANDOM (prior 0.95): A(1) stays in the null band of about 8–16. H1 then
    supports, at toy scale, closing the polynomial-omega route to n^{1/3}.
  - E-POWER / E-WEIL-TIGHT: some line captures p^θ or sqrt(p) points of the
    log-graph on real curves. That would be a non-genericity nobody has looked
    for, and a decision-target (b) lead.
- **Why not 76df35 first.** Its theorem needs no compute. Its Stage 1 certifies
  a constant, and its scope number A_L(W) is cheap but only sets reach.
- **Why not 0c5564 first.** Its Stage 1 validates bookkeeping on planted
  oracles.

## Ranking rationale (information gain against cost)

- **cd1903 ranks first.** Its minimal test is the cheapest, and it is the only
  one whose positive branch is a structural surprise about E(F_p). Its negative
  branch is also useful: it converts the (1/2, 3/4] window from a Weil gap into
  a toy-supported heuristic closure.
- **76df35 ranks next, at nearly the same value.** It delivers the most decisive
  zero-compute content: the duality proved over a named class at exactly the
  generic exponent. One cheap measurement (A_L(W)) fixes its reach toward D_w.
  Its expected information per CPU-hour is high, but most of it sits in Stage 0.
- **0c5564 is a building block.** It moves no exponent and its planted pipeline
  mostly confirms algebra, so it ranks lower. Its value is that it changes what
  the lane should look for: a few bits of the log on a recognizable dense set,
  not a full omega. It also supplies the pricing instrument that decision
  target (a) asks for. Its one genuine measurement is the shape arm M2: whether
  log-structured D are hit at rate |D|/n.

## Searches actually run

Corpus (Grep):

- knowledge/ for `Kohel|Shparlinski|Lange.Winterhof|Winterhof|Coppersmith.Shparlinski|interpolation` (47 files). None concerns interpolating the EC discrete log.
- ledger/, knowledge/ and docs/ for agreement or approximation of the discrete log (no matches).
- ledger/ for `uncertainty principle|Wiener norm|partial omega|graded duality` (one match, IDEA-20260902-c17bf6, read).
- IDEA-20260815-f558e4 sections (E) and (F).
- KN-LIT-043, -4155, -5602, -2167, -013 and -5230 headers.
- The three IDEA-20261003 files in other lanes (BINSTD; unrelated).
- `tools/validate_ledger.py` prior_art rules.
- Existence of all 15 KR rows cited.

Web, fetched and read:

- ar5iv.labs.arxiv.org/html/1302.4210 (Ahmadi–Shparlinski, JNT 2014). Lemma 1
  restates Kohel–Shparlinski Cor. 1: for ordinary E, any nonprincipal ψ and any
  group character χ, the sum over n ∈ Z_T of ψ(x(nG))χ(nG) is ≪ q^{1/2}.
  Reference [17] was read. This is cited with provenance `retrieved`, at
  secondary level.
- arxiv.org/abs/1302.4210 (abstract).
- hyperelliptic.org/tanja/publications.html (bibliographic data for
  Lange–Winterhof COCOON 2002 and AAECC 2003; no PDF).
- eprint.iacr.org/2004/031 (Semaev summation polynomials; not relevant).

Web, fetched but unreadable or blocked:

- Kohel's character.pdf: binary only, and pdftoppm is absent.
- Springer chapter 10.1007/10722028_24: auth redirect, not followed.
- unpaywall/oadoi redirect for the Lange–Winterhof paper: not followed.
- De Gruyter page for Kim–Tibouchi: HTTP 405.

Web searches, snippet level only (none used as `retrieved`):

- Lange–Winterhof interpolation (three queries).
- The Kohel–Shparlinski title.
- EC exponential sums with group characters.
- The joint distribution of x in an interval and log in an interval.
- Kim–Tibouchi equidistribution.

The crypto-kb index was not queried; no retrieval tool was exposed to this
agent.

**Novelty:** all three proposals are `unverified`.

- The nearest outside works (Lange–Winterhof 2002, Coppersmith–Shparlinski
  2000, Shparlinski's monograph) are recalled only.
- Theorem W may be exactly the Lange–Winterhof degree bound. If so, cd1903's
  delta shrinks to the regime split, the window, and the census.
- 0c5564 had no web search of its own.

**Not written, by write-scope:** a KN-LIT note for Ahmadi–Shparlinski Lemma 1,
the first retrieved statement of the Kohel–Shparlinski bound in this program.
Two earlier records (f558e4, c17bf6) cite that bound as recalled. Curating the
note is recommended.

## Honest accounting (docs/inventor-protocol.md §5)

**Objects considered:**

1. The log-graph Γ_E with its polynomial incidences (cd1903).
2. The Wiener-norm pair (A_x, A_L) and the mixed spectrum S(a,t) (76df35).
3. The omega window J(Q), carried by the walk offset (0c5564).

**Rejected before writing (possibility side), with reasons:**

| candidate | reason rejected |
|---|---|
| Twist / x-only Kummer mixing (the twist side is invertible when its order is smooth) | The Kummer line's pseudo-law cannot combine points of E and E^t, and the Kummer paradigm is closed at model lever 1. |
| Target-dependent factor base populated by HINTWALK hits plus small-coefficient relations | Relation-finding among walk hits is generic multi-collision. With small-x structure it is the PDP of F2 / Route 1 (owned by ICPERF and related areas). |
| Elliptic-net / EDS values as a hint | W(k) depends on k, not on Q. That is the D_w side by generation, the same verdict and mechanism as cubical 376b00, so it is a repackaging. |
| Multiplicative-subgroup x-sets D_H | Recognizable only; A_x ~ sqrt(p) puts them outside 76df35's class (named there as M5). |
| Multipoint-evaluation chi for root sets of a stored polynomial | This is BSGS/BL with storage. |
| Smooth-x(Q) sets | Multiplication on x has no link to the group law; this is the xedni-type obstruction, already closed. |

Since no possibility-side candidate survived, every filed proposal sits on the
impossibility or accounting side. This is reported as a fact about this
session's search, not as a closure of the possibility side.

**dominated_by:** "n/a (no result claimed)" for all three. Each file lists the
KR rows it checked:

- cd1903: 12 rows.
- 76df35: 11 rows.
- 0c5564: 12 rows.

**sota_delta:** zero on time, memory and data/queries for all three. Model
deltas:

- cd1903: the regime split, the (1/2, 3/4] window, and the census.
- 76df35: the bilinear set-size bound and the scope number.
- 0c5564: Lemma V, the exchange law, and the strip.

**Closures proposed (scoped; none asserted before their Stage 0):**

- **Total polynomial omegas of polylog degree** cannot beat sqrt(n).
  - Obstruction: the mixed character sum bound via completion.
  - Scope: M_deg.
- **Interval-type chi combined with structured-exponent (kangaroo/BSGS) omega**
  cannot beat sqrt(n)/(4 C K1 K2).
  - Obstruction: Theorem U.
  - Scope: class K.
- **"Dense, coordinate-invertible, not recognizable" is empty** (Lemma V).
  - This is an exact argument: verification by one scalar multiplication.

**Open directions for the next session:**

1. Close or populate the (1/2, 3/4] window for promised-input polynomial
   omegas. This needs a beyond-square-root incidence bound, or a lead from the
   census.
2. Measure A_L(W(m,w)). If the result is E-SPREAD, an escape must use a set
   that is spectrally complex on one side.
3. Hunt partial omegas: a cheap coordinate function giving any Θ(log n) top
   bits of the log on a recognizable set with α > 1/2. Under 0c5564 this alone
   moves the exponent. Coordinate bias belongs to RQ-ECDLP-4fcbd3; the pricing
   belongs here.
4. Straight-line-program-cheap omegas of high degree are the class none of the
   three models touches. The anomalous Smart map is its only known member.
   Writing down what makes it cheap, as a property of a curve class rather than
   of p = n, is the next object to enumerate (KN-OPEN-019).
5. The G2–G3 van Oorschot–Wiener interpolation, and whether bit-security
   amplification exists for any sparse D. Translations leave D, so only
   automorphism-closed D are known to admit it.
