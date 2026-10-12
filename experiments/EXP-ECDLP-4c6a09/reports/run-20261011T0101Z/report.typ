#set page(paper: "a4", margin: (x: 18mm, y: 16mm), numbering: "1")
#set text(font: "DejaVu Sans", size: 10pt)
#set par(justify: false, leading: .65em)
#set heading(numbering: none)
#set table(stroke: .4pt + luma(75%), inset: 5pt)
#show heading.where(level: 1): set text(size: 18pt, fill: rgb("176b87"))
#show heading.where(level: 2): set text(size: 12pt, fill: rgb("176b87"))
= Solinas number fields
Experiment observations and a worked explanation · 11 October 2026 UTC

*EXP-ECDLP-4c6a09* · H-ECDLP-4da36f · GOAL-ECDLP-001

== Recorded execution
The existing complete input set finished *1395 cells* in *768.0 s*.
A full three-seed replay finished in *823.4 s*. The raw results are
*byte-identical*. All recorded cells reached W=100,000.
These are observations; the scientific hypothesis has not been promoted.

#table(columns: (auto, auto, auto, auto, auto, auto),
  [Shape], [Solinas n], [Mean γ], [Random n], [Mean γ], [Difference],
  [P-192], [32/45], [0.057999], [217/300], [0.074362], [-0.016363],
[P-224], [4/15], [0.000000], [129/300], [0.077376], [-0.077376],
[P-256], [4/15], [0.076352], [93/300], [0.091570], [-0.015218],
[P-384], [1/15], [0.000000], [40/300], [0.045811], [-0.045811]
)

“n” gives fitted/total cells. There are *821 missing slopes* overall.
Means exclude missing values. Repeated fields and curves are retained;
the table does not assert independent sampling.

#figure(image("coverage.svg", width: 100%), caption: [
  Arithmetic mean coverage across all cells, including zero-point cells.
  Shading is observed min–max, not a confidence interval.])

#text(size: 8pt)[Primary RUN-ECDLP-24c35a; replay RUN-ECDLP-e09a9d.
The two single-threaded invocations overlap on a host with a four-CPU quota.]

#pagebreak()
= How the construction works
#image("construction.svg", width: 100%)

== 1. Turn the short prime formula into exact algebra
Write $p=f(m)$, with $m=2^k$, and introduce a symbolic root $alpha$ with
$f(alpha)=0$. If $f$ is irreducible, $K=QQ(alpha)$ is a number field.
For $f(t)=t^3-t-1$, this means $alpha^3=alpha+1$.

== 2. Reduce the algebra back to the finite field
Because $f(m)=p equiv 0$ modulo $p$, substitution $alpha mapsto m$ defines
a ring map $ZZ[alpha] -> FF_p$. Fractions with invertible denominators
can also be reduced. This is not a map from all of the characteristic-zero
field $K$ to $FF_p$. At good reduction, elliptic-curve reduction respects
point addition.

== 3. See an actual point identity
Choose $m=4$, $p=59$ and $E: y^2=x^3-x+3$. Then
$alpha^3-alpha+3=4$, so $(alpha,2)$ is an exact point over $K$.
It reduces to $(4,2)$ because $4^3-4+3=63 equiv 4$ modulo 59.
This is a derived example below the experiment's prime cutoff, not a
measured trial or a rank claim. The discriminant $-16 dot 239$ is nonzero
modulo 59, so this example has good reduction.

== 4. Ask whether this supplies points efficiently
The experiment tries small power-basis coordinates for $x$, searches for
an exact square root of $x^3+A x+B$ in $K$, then counts distinct reductions.
Accepted roots are verified exactly; bounded reconstruction can miss roots.
It compares the same search rule in Solinas and random comparison fields.

== Why the discriminant and rank matter
The algebraic integers form a lattice with covolume proportional to
$sqrt(abs(D_K))$, where $D_K$ is the field discriminant. The root discriminant $abs(D_K)^(1/d)$ normalizes
by degree. Smaller discriminants motivate smaller coordinates; they do not
force the curve equation to have a square root. PARI supplies field
discriminants, which can differ from the defining-polynomial discriminant.

More discovered points do not certify greater rank: independent generators
must be proved independent. The number-field rank arm is explicitly skipped.

#pagebreak()
= What the measurements mean
#figure(image("gamma.svg", width: 92%), caption: [
  γ is a fitted log–log slope over up to the last three positive-coverage
  checkpoints. Dots are cell values; diamonds are arithmetic means.
  This is finite-search growth, not an asymptotic ECDLP exponent.])

#figure(image("discriminant.svg", width: 92%), caption: [
  Recorded field discriminants and fitted slopes. The interval is copied
  from the runner's cell bootstrap; it does not model shared-field or
  shared-curve dependence.])

Recorded regression: slope *-0.000221*, 99% interval
*[-0.024314, 0.022378]*, n=537.
Non-Q cells without a PARI field discriminant: 0.

#pagebreak()
= Reproduction and remaining gaps
== Exact scope
Seeds 1, 2, 3; 20 requested random fields per shape per seed; 5 curves per
field; candidate checkpoints 300, 1,000, 3,000, 10,000, 30,000, 100,000;
8 auxiliary primes. Curves are $y^2=x^3+A x+B$ with seeded integer
coefficients from −20 to 20 and good reduction at the selected toy prime.
The CSV and raw JSON contain every defining polynomial, modulus and curve.
No subgroup or unknown discrete-log challenge was selected.

The NIST names label polynomial shapes; this is not a deployed-size
curve experiment. Rank and point independence are unmeasured. Heights are
logarithmic coefficient-height proxies, not canonical point heights. Random fields match degree and
polynomial weight, but can repeat and have different prime sizes.

== The gap to a discrete-log algorithm
The multiplicative number field sieve factors small norms into prime
ideals to obtain useful log relations. Elliptic-curve points add; small
coordinates do not supply the same factorization automatically. A usable
method would still need affordable lifts or relations for arbitrary target
points, justified independence, and full recovery costs against a baseline.
This run measures a supply of points and their coverage, not that method.

== Execution identity
Code revision: #text(size: 8pt)[8e1cc6c5313fdab887d09b98a712ea05996d7b18]

Compiler: #text(size: 8pt)[rustc 1.99.0 (b940084d7 2026-09-28)]

PARI: #text(size: 8pt)[libpari GP/PARI CALCULATOR Version 2.17.2 (released) (FFI)]

The release binary used the complete documented argv. Each process had a
4 GiB address-space cap. Manifests preserve source hashes, command,
timestamps and per-cell timing; launch records preserve dirty-tree state.
Sources were unchanged. CTRL-SHAPE is True; literal raw-byte
CTRL-REPLAY is True. All rank-arm records retain the skipped label.

== Evidence and source files
All experiment sources have internal provenance and were inspected in this
session. Algebraic identities above are derived. The source implementation
is in #link("https://github.com/aburan28/crypto-autoresearcher/pull/2035")[PR #2035].
The complete commands, prime table, counts, required extreme-cell records,
resource receipts and caveats are in the accompanying #link("report.md")[Markdown report].

Primary: #text(size: 8pt)[RUN-ECDLP-24c35a]

Replay: #text(size: 8pt)[RUN-ECDLP-e09a9d]

SHA-256 of raw JSON:
#text(size: 7pt)[71ffe56253681626967a7b5abf8e9a81dfdc0601a18de3171e21654be8fec835]

#link("../../runs/RUN-ECDLP-24c35a/raw-result.json")[Primary raw JSON] ·
#link("../../runs/RUN-ECDLP-24c35a/manifest.yaml")[Manifest] ·
#link("replay-check.json")[Replay check] · #link("cells.csv")[Cell identities]

The PDF, Typst source and SVG graph sources are communication artifacts.
No scientific status, canonical frontier graph or ledger record was changed.
