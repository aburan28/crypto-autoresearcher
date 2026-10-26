# F4 prospective derivations

These derivations were written before the second-pass observation panel.
Assume the published nonsingular P-256 curve has its published prime odd
order r greater than three and cofactor one. Thus every nonzero rational
point P generates E(F_p), and rational points with y=0 do not occur.

## Anchored exact pole-three sections

The exact pole-three part of L(3O) has nonzero y coefficient. Normalize it
to one. A section vanishing at fixed P=(x_P,y_P) is uniquely

    f_t = y - y_P + t(x-x_P),  t in F_p.

There are p such projective sections. Their norm is
`A_t(x)^2-(x^3-3x+b)`, of degree three; the known anchor is a linear factor.
A section has a completely rational zero divisor exactly when its residual
unordered pair Q,R is affine rational and Q+R=-P, with multiplicities allowed.

The involution Q -> -P-Q preserves E(F_p) minus {O,-P}. This set has r-2
points. It has exactly one fixed point, since multiplication by two is
bijective and the solution of 2Q=-P lies in that set. Its unordered-orbit
count is therefore `(r-2+1)/2=(r-1)/2`. Conversely each pair gives a unique
projective section in L(3O) vanishing at P. No vertical section can have exact
pole three. Hence exactly `(r-1)/2` of the p slopes are fully rational, and
the ideal uniform-slope probability is `(r-1)/(2p)`.

The pair Q=R is included, as is the tangent at P with divisor
`2[P]+[-2P]-3[O]`. They are different sections because 3P is nonzero. Triple
zeros would require a rational nonidentity point of order three and do not
occur under the assumptions. An opposite residual pair would force P=O and
is excluded. These are distribution identities, not observed sample rates.
The finite SHA-256-derived slopes are reproducible inputs; their realized
fraction is not a measured population probability or a proof of hash uniformity.

## The one-anchor incidence geometry

Write `n=(r-1)/2` and label inverse orbits by `[k]={kP,-kP}`, 1<=k<=n.
The rational sections give columns connecting `[k]` and `[k+1]` for
1<=k<n, plus the terminal section `P+2(nP)=O`. The terminal column has
one outside entry with magnitude two after equal endpoints aggregate.
This is a path of two-endpoint columns plus a terminal doubled one-endpoint
column. It is not an ordinary random graph. If displayed as a loop, that
loop counts twice in ordinary graph valence; no ambiguous degree bound is
being asserted. Removing base vertex `[1]` gives a one-outside column from
the tangent at P; removing additional base vertices splits the remaining
path into segments, with boundary one-outside columns.

The eight-anchor workload combines eight such geometries on the same fixed
base. It may branch or collide, but neither a random-graph model nor a
collision-frequency law is assumed. The anchors are inside the base. Forcing
an additional outside anchor would change the law and normally leave too
many outside columns; it is not hidden inside this sampling panel.

## Streaming weighted incidence reduction

Each accepted row supplies at most two nonzero outside entries over F_r.
Process rows in fixed order. Reduce its outside column by earlier normalized
pivots; each pivot has at most two entries. Eliminating a shared pivot from
a vector of support at most two preserves that support bound. The pivot
is its least remaining vertex, so a stored two-entry pivot points towards
a larger vertex and the implicit parent structure is acyclic. A closed
weighted walk can leave a nonzero one-entry pivot; it is not silently called
a cancellation. A later closure may combine with that pivot and emit a
kernel vector, including combinations of two unbalanced signed cycles.

Every arithmetic step also creates a node in a linear-combination DAG of
input rows. A zero outside vector emits its exact witness. A nonzero vector
adds an independent pivot. Distinct emitted witnesses have distinct latest
input indices with coefficient one, so they are independent. Their number
is L-rank(A); they therefore form the full right kernel of the outside
incidence A. This proves the algorithmic invariant, conditional on correct
field operations. The separate dense oracle and witness consumer check it
on every executed graph.

Let D be all input relation rows and let B be the fixed base columns. The
image of ker(A) in B has dimension `rank(D)-rank(A)`. Thus kernel count,
unsigned cycle count and useful base-row rank are different quantities.
Zero outputs and duplicates are retained. Witness coefficients are exact
integer representatives of F_r elements. For their centered integer lifts,
outside sums can be nonzero multiples of r; records include those quotients.
Cancellation is modulo r, appropriate to the r-torsion subgroup, and is not
misrepresented as equality of integer divisors.

The active pivot entries use at most twice rank(A) field elements, besides
vertex labels. Witness DAG storage is proportional to the recorded
reductions and normalizations; expansion and output storage are additionally
charged. This is a representation fact, not an end-to-end ECDLP bound or a
claim that all input orders have short paths.
