# Raw console outputs of the four computations (2026-10-24, this Mac)

Sage was run through the repository's inner binary
`/Volumes/SSD990/cryptanalysis/third_party/sage-binary/sage` with `TMPDIR`, `DOT_SAGE`
and `MPLCONFIGDIR` pointed at a writable directory; PARI/GP 2.17.3.

## newton.sage (p = next_prime(2^28), random a, b)

```
S4: nterms 439 degs [4, 4, 4, 4] total 12
S5: nterms 54777 degs [8, 8, 8, 8, 8] total 32
S3 with x3 fixed:
  free vars 2, deg/var 2, support 9 of box 9; discrete centroid sum 2.0000; hull centroid sum 2.0000; hull volume 4.00 vs box 4
  JM basic asymptotic reach delta_max = 1/((m+1) c_N) = 0.16667; box formula 2/(m(m+1)d) = 0.16667
S4 with x4 fixed:
  free vars 3, deg/var 4, support 125 of box 125; discrete centroid sum 6.0000; hull centroid sum 6.0000; hull volume 64.00 vs box 64
  JM basic asymptotic reach delta_max = 1/((m+1) c_N) = 0.04167; box formula 2/(m(m+1)d) = 0.04167
S5 with x5 fixed:
  free vars 4, deg/var 8, support 6561 of box 6561; discrete centroid sum 16.0000; hull centroid sum 16.0000; hull volume 4096.00 vs box 4096
  JM basic asymptotic reach delta_max = 1/((m+1) c_N) = 0.01250; box formula 2/(m(m+1)d) = 0.01250
```

## psi2.sage (p = 65537, B = 64)

```
j0 a=0 b=7     subgroup mu_64    : deg 8064, nonzero coeffs 8034 of 8065, roots in F_p 1987, roots in V 12, 1.1s
j0 a=0 b=7     interval [0,64)   : deg 8064, nonzero coeffs 8065 of 8065, roots in F_p 1966, roots in V 0, 0.6s
random a,b     subgroup mu_64    : deg 8064, nonzero coeffs 8064 of 8065, roots in F_p 1998, roots in V 3, 0.6s
random a,b     interval [0,64)   : deg 8064, nonzero coeffs 8065 of 8065, roots in F_p 1995, roots in V 0, 0.5s
```

## free2.sage (p = next_prime(2^20), B = 400 interval, mu_358 subgroup)

The script prints a random-model expectation of B(B-1)B/p (~61 / ~44); the correct
expectation after accounting for the two-fold ordered-pair and three-fold per-relation
detection is B^2(B-1)/(2p) ~ 30.5 (interval) and ~ 21.9 (subgroup); see report Appendix A.3.

```
j0 a=0 b=7     interval [0,400)    : roots in V 22, random-model expectation ~60.9, 4.0s
j0 a=0 b=7     subgroup mu_358     : roots in V 9, random-model expectation ~43.6, 2.3s
random a,b     interval [0,400)    : roots in V 27, random-model expectation ~60.9, 2.6s
random a,b     subgroup mu_358     : roots in V 38, random-model expectation ~43.6, 1.7s
```

## cyc.gp (p = 10009, B = 72, e = 139)

```
p=10009 B=72 e=139
a=6713  lhs==rhs: 1
a=5890  lhs==rhs: 1
a=9522  lhs==rhs: 1
a=8738  lhs==rhs: 1
a=8891  lhs==rhs: 1
a=9414  lhs==rhs: 1
all ok: 1
sum r_u = 71 (expect B-1 = 71); distinct cosets hit: 33 of e = 139
```
