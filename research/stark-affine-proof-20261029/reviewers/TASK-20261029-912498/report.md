# Independent mathematical review of the affine ring statements

Task: `TASK-20261029-912498`  
Joint owned: `J1`  
Review policy: `review-adversarial`  
Verdict: **holds**, with statement 4 read in its stated existential sense, “can permit.”

The sole source read was
`/home/ec2-user/scratch/stark-affine-proof-20261029/TASK-20261029-912498/blind-math.md`.
Its SHA256 is
`854236e982008c70057d981a072ed8683756734db3d1e5d1e2e325b9b6ed20b4`,
matching the supplied expected value. All arguments below were derived manually
from that input. No producer implementation, formal proof, claim inventory,
repository history, sibling report, prior conversation history, or memory was
consulted. No build, native verification, experiment, network request, or package
installation was performed.

## Conventions and scope

Here a commutative ring has an identity element `1`, as required by the named
probes. The zero ring, in which `0 = 1`, is allowed. “Nontrivial” means `0 != 1`;
for a ring with identity this is equivalent to having more than one element.

For `a,b,c,x,y` in `R`, write

\[
E_{a,b,c}(x,y)=ax+by+c.
\]

Equality of functions means agreement for every pair in `R × R`. This report
reviews only the five mathematical statements in the input. It is not a
Lean-kernel verification, a review of any formal theorem's exact statement, or
scientific promotion. It establishes no serialization, security, execution,
performance, cost, or cryptanalytic claim. Checking the input's SHA256 identifies
the reviewed artifact; it is not a mathematical or security claim about a hash
construction.

## 1. Recovery of the coefficient triple

The ring identities give

\[
E_{a,b,c}(0,0)=c,\qquad
E_{a,b,c}(1,0)=a+c,\qquad
E_{a,b,c}(0,1)=b+c.
\]

Consequently,

\[
\begin{aligned}
E_{a,b,c}(1,0)-E_{a,b,c}(0,0)&=(a+c)-c=a,\\
E_{a,b,c}(0,1)-E_{a,b,c}(0,0)&=(b+c)-c=b,\\
E_{a,b,c}(0,0)&=c.
\end{aligned}
\]

Thus the ordered tuple in statement 1 is exactly `(a,b,c)`. Only additive
cancellation and multiplication by `0` and `1` have been used. There is no
division, multiplicative cancellation, assumption of characteristic different
from two, or assumption that the ring has no zero divisors. This calculation
also holds in the zero ring, where each entry is its unique element.

## 2. Three probes determine the affine function

Suppose triples `(a,b,c)` and `(a',b',c')` agree at each of `(0,0)`, `(1,0)`,
and `(0,1)`. The recovery formula from statement 1 applied to their shared three
values gives

\[
(a,b,c)=(a',b',c').
\]

Equivalently, the first probe gives `c=c'`; the second then gives
`a+c=a'+c` and hence `a=a'`; the third gives `b=b'`. Substitution of these three
coefficient equalities gives

\[
E_{a,b,c}(x,y)=E_{a',b',c'}(x,y)
\quad\text{for every }x,y\in R.
\]

This establishes statement 2 in every ring under the conventions above.
In particular, the coefficient-to-function map for this specific affine family
is injective, even when the full polynomial-to-function map is not injective.
The conclusion in the zero ring is valid: there is only one coefficient triple
and only one function from `R × R` to `R`.

## 3. Multiplication cannot be affine in a nontrivial ring

Assume an affine representation of multiplication exists:

\[
ax+by+c=xy\quad\text{for all }x,y\in R.
\]

At `(0,0)` this forces `c=0`. At `(1,0)` it then forces `a=0`, and at `(0,1)`
it forces `b=0`. At `(1,1)`, the asserted representation consequently forces

\[
0=1.
\]

This contradicts nontriviality. Statement 3 therefore holds for every nontrivial
commutative ring with identity, regardless of its characteristic, size, or zero
divisors.

An equivalent certificate uses the four evaluations

\[
\Delta f=f(1,1)-f(1,0)-f(0,1)+f(0,0).
\]

For any affine `f=E_{a,b,c}`, direct cancellation gives `Δf=0`. For
`f(x,y)=xy`, it gives `Δf=1`. This is a functional obstruction: it uses actual
values and does not infer functional inequality merely from distinct formal
polynomial coefficients.

The phrase “for all x,y” is essential. Multiplication and the zero affine
function agree at all three designated probes. Their disagreement at `(1,1)`
in a nontrivial ring shows that the three probes determine a function only
within the asserted affine family; they do not certify that an arbitrary
function belongs to that family.

## 4. Omitting a designated probe

Taking “the third designated probe” in the order listed in statement 2 means
omitting `(0,1)` and retaining `(0,0)` and `(1,0)`. Consider

\[
f(x,y)=E_{0,0,0}(x,y)=0,\qquad
g(x,y)=E_{0,1,0}(x,y)=y.
\]

Both functions give zero at the two retained probes. At `(0,1)`, their values
are `0` and `1`, respectively. They are therefore distinct functions, arising
from distinct coefficient triples, in every nontrivial ring.

More generally, agreement at the two retained probes forces equality of `c`
and `a` but leaves `b` unrestricted. If two choices of `b` differ, evaluation
at `(0,1)` distinguishes the resulting functions. No zero-divisor issue can
hide that difference because the multiplier at this probe is `1`.

For completeness, any one of the three listed probes can be essential. These
examples also resolve any ambiguity about the ordering of “third”:

| Omitted probe | Retained probes | Two affine functions agreeing at the retained probes | Values at the omitted probe |
| --- | --- | --- | --- |
| `(0,1)` | `(0,0)`, `(1,0)` | `0` and `y` | `0`, `1` |
| `(1,0)` | `(0,0)`, `(0,1)` | `0` and `x` | `0`, `1` |
| `(0,0)` | `(1,0)`, `(0,1)` | `0` and `1-x-y` | `0`, `1` |

Every row gives distinct functions whenever the ring is nontrivial, including
in characteristic two. In the zero ring there cannot be distinct functions or
distinct coefficient triples. Thus the statement that removal **can permit**
distinct affine functions is true. A stronger assertion that it permits them
in **every** commutative ring would require nontriviality and would be false
without it.

## 5. Nontriviality is necessary for statement 3

In the zero ring, the sole element is both `0` and `1`. For the sole triple
`(0,0,0)` and every possible pair `(x,y)`,

\[
E_{0,0,0}(x,y)=0=xy.
\]

This is an explicit counterexample to statement 3 with its nontriviality
assumption removed. The converse is supplied by the four-probe proof above:
any affine representation of multiplication forces `1=0`. A ring with identity
satisfying that equality has only one element, since any `r` satisfies
`r=r·1=r·0=0`. Hence the exact characterization is

\[
\text{multiplication has an affine representation on }R\times R
\quad\Longleftrightarrow\quad
R\text{ is the zero ring}.
\]

Nontriviality is therefore both sufficient and necessary for the asserted
nonexistence of an affine representation.

## Exceptional cases and distinctions between representations

**Characteristic two.** All preceding deductions remain valid. For example,
over `F₂`, multiplication has values `0,0,0,1` at `(0,0)`, `(1,0)`, `(0,1)`,
and `(1,1)`. Matching its first three values forces all affine coefficients
to zero, which fails at the fourth point. Although subtraction equals addition
in this ring, additive cancellation still holds; no argument divides by `2`.
The missing-probe example `0` versus `y` works unchanged. The same reasoning
also covers nontrivial characteristic-two rings with zero divisors, such as
`F₂[ε]/(ε²)`, where the nonzero class of `ε` has square zero.

**Composite modulus and zero divisors.** In `Z/4Z`, the nonzero element `2`
satisfies `2·2=0`; in `Z/6Z`, the nonzero classes `2` and `3` satisfy `2·3=0`.
Nevertheless, `1 != 0` in both rings, and the same substitutions recover all
affine coefficients and prohibit an affine representation of multiplication.
Neither additive cancellation nor multiplication by `1` requires an integral
domain. All composite moduli greater than one satisfy the same conclusions.

**Zero ring.** All three designated points and `(1,1)` coincide. Statements
1 and 2 still hold because there is only one coefficient triple. Multiplication
is affine. There is no pair of distinct affine functions, so the witness for
statement 4 requires a nontrivial ring. This is the precise exception already
accounted for above.

**Expressions, polynomials, and functions.** These are distinct objects.
An expression is syntax, so `x+0` and `x` can be different expressions while
denoting the same formal polynomial and function. A polynomial in `R[X,Y]`
is determined by its coefficients. Its evaluation on `R × R` is a function;
different polynomials can induce the same function on a finite ring.

For example, `X²-X` is a nonzero formal polynomial over `F₂`, but its value is
zero at both elements of `F₂`. Over `Z/4Z`, the formal polynomial
`2X(X-1)=2X²-2X` has nonzero coefficients yet also induces the zero function:
for any integer representative `t`, `t(t-1)` is even, so `2t(t-1)` is divisible
by four. These are identities of functions, not identities of those formal
polynomials. They remain examples in two variables by ignoring `Y`.

In a nontrivial ring, the coefficient of `XY` in
`XY-(aX+bY+c)` is `1`, so this difference is a nonzero formal polynomial.
That coefficient observation alone would not prove that its evaluated
function is nonzero on a finite ring. The explicit four-probe argument does
prove it. Conversely, the recovery formulas establish that this particular
affine family has unique coefficients even as functions on a finite ring.
In the zero ring, all polynomial coefficients and all evaluated values are
zero, although one may still write different syntactic expressions.

## Review determination

Statements 1 and 2 hold without nontriviality. Statement 3 holds with its
stated nontriviality assumption. Statement 4 holds as an existential claim
and, more strongly, in every nontrivial ring; its universal version would fail
in the zero ring. Statement 5 has an affirmative answer: removing
nontriviality invalidates statement 3, with the zero ring as the exact
exception. This determination concerns only the manually derived mathematics
above and does not attest to any implementation or formal proof artifact.
