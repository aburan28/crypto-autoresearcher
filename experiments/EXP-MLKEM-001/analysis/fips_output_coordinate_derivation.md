# FIPS output-coordinate derivation (EXP-MLKEM-001)

## Representatives

Work in \(\mathbb{Z}_q\) with \(q=3329\). Canonical representatives are
\([0,3328]\). Centered representatives are the unique integers in
\([-1664,1664]\), written \(\mathrm{ctr}_q\).

## Compression

FIPS 203 uses nearest-integer rounding with ties toward \(+\infty\):

\[
\mathrm{Compress}_d(x)=\Big\lfloor \tfrac{2^d}{q}x+\tfrac12\Big\rfloor \bmod 2^d,
\qquad
\mathrm{Decompress}_d(y)=\Big\lfloor \tfrac{q}{2^d}y+\tfrac12\Big\rfloor.
\]

The pinned pq-crystals estimator instead uses Python `round` (ties to even) in
`mod_switch`. These modes are compared exhaustively and never mixed silently.

## No-compression one-coordinate law

For independent CBD coefficients, each negacyclic product coordinate is a sum of
\(n\) independent CBD products (signs absorbed by symmetry). With module rank
\(k\),

\[
\nu_\ell = \sum_{j=1}^k\big((e_j y_j)_\ell - (s_j e_{1,j})_\ell\big) + (e_2)_\ell.
\]

Exact laws are obtained by generating-function convolution and independently by
successive product convolutions.

## Scalar compressed control

The \(n=1,k=1\) instance enumerates shared \(A,s,e,y,e_1,e_2\) with FIPS
compression on \(u,v\) and checks the ring identity

\[
\mathrm{ctr}_q(w-\mu_b)=\mathrm{ctr}_q(ey+e_2+c_v-s e_1-s c_u)
\]

up to an explicit multiple of \(q\). This is a toy discriminator, not a
standardized ring instance.
