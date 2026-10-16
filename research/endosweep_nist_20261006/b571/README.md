# B-571: how the last cofactor was split

B-571's `4q − t²` (173 digits) is

```
137 · 1502689 · 5608493523058319 · 3563521804312876303 · p38 · p93
p38 = 46393104672338327566438581332776443577
p93 = 110062885101747737373848971769992595641139506008946715206760528637300688225399301632484625559
```

all to exponent 1. The complete certificate is the B-571 line of
[`../factorizations.jsonl`](../factorizations.jsonl).

1. **Trial division** below 10^7 found 137 and 1 502 689.
2. **GMP-ECM 7.0.5** (B1 = 3·10^6, three workers) found 5 608 493 523 058 319
   and 3 563 521 804 312 876 303 within its first 2 350 curves. That left a
   130-digit composite cofactor
   `C130 = 5106158949064929458195825244013686251303650244512648497717558074254289649451324237901292834252800885477933556954015766654535584543`.
3. **CADO-NFS** split `C130 = p38 · p93` with the number field sieve:

   ```sh
   cado-nfs.py 5106158949064929458195825244013686251303650244512648497717558074254289649451324237901292834252800885477933556954015766654535584543 -t 4
   ```

   * CADO-NFS 3.0.0, built from source at git commit
     `692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b` (gitlab.inria.fr/cado-nfs,
     `master`, 2026-10-02), with the default `params.c130`.
   * The log's final summary line reports 214 591 CPU-seconds (about 59.6
     CPU-hours) for the whole factorisation. The run was 4 threads on one
     4-core machine. It ran in 14 sessions between 2026-10-07 and 2026-10-16,
     each resumed from CADO's parameter snapshot after a container restart, so
     the wall-clock span is not a meaningful timing.
   * Lattice sieving collected 33 564 919 relations (30 000 000 wanted).
   * [`c130.poly`](c130.poly) is the degree-5 polynomial pair CADO selected.
     The relation files, the matrix and the database are not kept: they run
     to gigabytes and the result does not depend on them, since it is checked
     by multiplying back.
4. **Primality.** PARI `isprime` returns 1 for both p38 and p93.
   [`primecert_43577.txt`](primecert_43577.txt) (p38) and
   [`primecert_25559.txt`](primecert_25559.txt) (p93) are PARI ECPP
   certificates (`primecert`), and `primecertisvalid` accepts both:

   ```sh
   python3 -c 'import cypari2; P = cypari2.Pari()
   for f in ("primecert_43577.txt", "primecert_25559.txt"):
       c = P(open(f).read()); print(c[0][0], P.primecertisvalid(c))'   # ... 1, twice
   ```

   The harness re-tests every factor when it reads the certificate
   (`nist.check_factorization`).

FactorDB lists this `4q − t²` as fully factored (status FF) as of 2026-10-16.
