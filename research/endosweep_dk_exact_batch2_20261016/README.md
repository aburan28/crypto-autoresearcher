# Exact CM discriminants of 6 more standardized curves (batch 2)

**Question.**  Batch 1 ([`../endosweep_dk_exact_20261016`](../endosweep_dk_exact_20261016/README.md))
recorded the exact CM field discriminant `D_K`, the conductor `f` and the least
non-scalar endomorphism degree for the 18 curves whose `4q − t²` the factoring
driver had split completely by its frozen snapshot (22:24Z).  The driver kept
running.  Which further curves did it finish by a second frozen snapshot, and
what are their exact `D_K`, `f` and degree bound?

The answer is six curves: oscaa/SM2, bn/bn606, nums/ed-382-mont,
brainpool/brainpoolP384r1, arkworks/cp6_782 and nums/numsp512t1.  This
directory is batch 1's computation applied to them, by the same scripts.

## Method

Everything up to the factoring driver is batch 1's, unchanged: the 10 s
screen, its survey records, the driver and its job list.  Batch 1's README,
"Method" steps 1 and 2, describes them.  `survey.py`, `driver.py` and
`jobs.json` are not copied here.  They are byte-identical (`cmp`) to
[`../endosweep_dk_exact_20261016/provenance/`](../endosweep_dk_exact_20261016/provenance/).

1. **A second frozen snapshot** of the driver state,
   [`provenance/driver_state.snapshot2.json`](provenance/driver_state.snapshot2.json),
   was taken at 22:56Z.  CADO-NFS was then running on numsp384t1's C104.  The
   driver's event log up to that moment is
   [`provenance/driver_events.snapshot2.log`](provenance/driver_events.snapshot2.log).
   * Its first 54 lines are byte-identical to batch 1's
     `driver_events.snapshot.log`.
   * Every snapshot-1 entry that was complete is unchanged in snapshot 2.
   * Exactly six entries went from open to complete between the snapshots.
     Those six are this batch.
2. **The survey records** of the six curves are copied verbatim from the 10 s
   screen's output (`survey.jsonl`, 155 records) into
   [`provenance/survey_selected.jsonl`](provenance/survey_selected.jsonl).
3. **Certificates.**  Batch 1's
   [`make_factorizations.py`](../endosweep_dk_exact_20261016/make_factorizations.py)
   writes [`factorizations.jsonl`](factorizations.jsonl), run with
   `--dir` (this directory), `--snapshot provenance/driver_state.snapshot2.json`
   and `--exclude-certified` (batch 1's `factorizations.jsonl`).
   * It takes every complete snapshot entry except the four NIST curves and
     the 18 of batch 1.
   * It joins the survey's small primes to the primes of the composite `C`.
     On bn606 and cp6_782 the survey left `C²`, and the exponent is recovered
     by division.
   * It reconstructs `found_by` per factor by replaying the snapshot's split
     log against the order in which the driver appended the primes.
   * Every factor is proved prime with PARI `isprime`, and the factors must
     multiply back to `4q − t²` exactly.
4. **Results.**  Batch 1's
   [`build_dk_exact.py`](../endosweep_dk_exact_20261016/build_dk_exact.py),
   run with `--dir` and `--exclude-certified`, writes
   [`dk_exact.json`](dk_exact.json) and [`dk_exact.md`](dk_exact.md).
   * Each curve is reloaded from the std-curves checkout and re-verified (`n`
     prime, `h·n` in the Hasse interval, a point killed by `h·n`).
   * `t = q + 1 − h·n` and `N = 4q − t²` are recomputed.
   * `D_K` and `f` come from `nist.exact_discriminant`.  Then `t² − 4q =
     D_K·f²`, `D_K ≡ 0, 1 (mod 4)` and fundamentality are re-checked.
   * The degree is `quadorder.min_nonscalar_degree(D_K) = (|D_K| + (D_K mod
     2))/4`.
   * Where std-curves records `cm_disc` or `conductor`, both are compared.  It
     records neither for any of the six.

**The batch-1 scripts were parameterised, not copied.**
`make_factorizations.py`, `build_dk_exact.py`, `lean/gen_dk_exact_lean.py`
and `report/plot_dk.py` gained optional arguments: an output directory, a
snapshot name, earlier certificate files to exclude, a Lean module name and
target, and a report directory.  Without the arguments they behave as before.
This was checked by regenerating batch 1 with the edited scripts:

* `factorizations.jsonl`, `dk_exact.json`, `dk_exact.md` and
  `formal/CryptoResearch/Endosweep/DkExact.lean` came out byte-identical
  (`git status` clean, and `sha256sum -c SHA256SUMS` passes in batch 1).
* `report/dk_exact.svg` came out identical except for two things. One is the
  `<dc:date>` line. The other is matplotlib's per-run random clip-path and
  marker ids, which were renamed one-to-one.
* Batch 1's `report.typ` and `report.pdf` were not touched.

## Results

| curve | p bits | 4q−t² digits | factorisation of 4q−t² | f | D_K | log2 \|D_K\| | least non-scalar degree | already public? |
|:--|--:|--:|:--|--:|:--|--:|--:|:--|
| oscaa/SM2 | 256 | 78 | 19 · p36 · p41 | 1 | −(78 digits) | 257.88 | 2^255.88 | (not checked against literature) |
| nums/ed-382-mont | 382 | 116 | 2² · 31 · 356399 · p28 · p29 · p52 | 2 | −(115 digits) | 381.02 | 2^379.02 | (not checked against literature) |
| brainpool/brainpoolP384r1 (= brainpoolP384t1) | 384 | 116 | 11² · 6857 · 379795560371 · p44 · p55 | 11 | −(114 digits) | 377.45 | 2^375.45 | (not checked against literature) |
| nums/numsp512t1 | 512 | 155 | 2² · 23227 · 480647 · 11602586981 · p15 · p18 · p29 · p37 · p38 | 2 | −(154 digits) | 511.07 | 2^509.07 | (not checked against literature) |
| bn/bn606 | 606 | 183 | 3³ · p14² · p34² · p44² | 92 digits | −3 | 1.58 | 1 | `D = −3` by construction (not checked against literature) |
| arkworks/cp6_782 | 782 | 236 | 2¹⁰ · 3³ · 113 · 2879² · p22² · p33² · p58² | 117 digits | −339 | 8.41 | 85 | (not checked against literature) |

* `pN` is an N-digit prime.  [`dk_exact.json`](dk_exact.json) has every number
  in full, including `t`, `n`, `h`, the squarefree part `s` and `D_K`.
* On all six, `s ≡ 3 (mod 4)` and `D_K = −s`.
* The degree column is `(|D_K| + (D_K mod 2))/4`.  It is a lower bound for the
  degree of every endomorphism outside `Z`, whichever order between `Z[π]`
  and `O_K` `End(E)` is.
* [`dk_exact.md`](dk_exact.md) gives the same table with `t` and `s`, and
  names the method that found each factor.

**Already public?**  std-curves records no `cm_disc` and no `conductor` for
any of the six, so none of these `D_K` values was checked against literature.
Their sources may publish them, as may FactorDB:

* SM2: GM/T 0003-2012;
* the NUMS paper (ePrint 2014/130);
* Brainpool: RFC 5639;
* the BN construction;
* the ZEXE paper, for CP6-782.

On bn606, `D_K = −3` holds by construction (BN curves have `j = 0`), and only
the factorisation of the conductor is new.  On cp6_782, `|D_K| = 339` is
small, which a CM construction gives.  That it is the discriminant the curve
was built with was not checked against the ZEXE paper.

## Findings

1. **Six more curves have an exact `D_K`.**
   * On the four curves with a large `D_K`, `|D_K|` lies between 2^257.88
     (SM2) and 2^511.07 (numsp512t1).
   * The gap `log2(4q) − log2 |D_K|` is 0.12 bits on SM2, 2.98 on ed-382-mont,
     2.93 on numsp512t1 and 7.69 on brainpoolP384r1.  On brainpoolP384r1,
     6.92 of those bits are `log2 f² = log2 121`.
   * So the least non-scalar endomorphism degree on these four is at least
     2^255.88, and none of them has a small-degree endomorphism beyond the
     integers.
   * Lean proves the arithmetic of `|D_K| ≥ 2^257` and degree `≥ 2^255` on
     them (below).
2. **The conductors.**
   * `f = 1` on SM2, so `End(E) = Z[π]` there.
   * `f = 2` on ed-382-mont and numsp512t1, both twisted Edwards curves with
     `h = 4`.
   * `f = 11` on brainpoolP384r1.  Its duplicate in the corpus,
     brainpoolP384t1, is the same curve up to isomorphism, with the same `t`.
   * On bn606 and cp6_782, `f` has 92 and 117 digits.
3. **cp6_782 has `D_K = −339`.**
   * Its least non-scalar degree bound is only 85.
   * This is a lower bound, not an endomorphism. `End(E)` lies between
     `Z[π]` and `O_K`, and its index in `O_K` divides the 117-digit `f`.
   * Which order it is was not determined. So nothing here shows that
     cp6_782 has an endomorphism of degree 85.
4. **Who found each factor.**  The per-factor list is in
   [`dk_exact.md`](dk_exact.md); it is reconstructed from the snapshot-2 split
   log.
   * CADO-NFS 3.0.0 (git `692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b`, run as
     `nice -n 5 python3 cado-nfs.py C -t 4 -w WORKDIR`) made the last split on
     every one of the six, each in wall-clock time:

     | curve | composite | split | wall |
     |:--|--:|:--|--:|
     | numsp512t1 | C75 | p37 · p38 | 124 s |
     | SM2 | C77 | p36 · p41 | 94 s |
     | bn606 | C78 | p34 · p44 | 90 s |
     | ed-382-mont | C80 | p28 · p52 | 113 s |
     | cp6_782 | C90 | p33 · p58 | 423 s |
     | brainpoolP384r1 | C99 | p44 · p55 | 1018 s |
   * GMP-ECM 7.0.5 found the factors before that:
     * tier 1 (B1 = 11 000): bn606's p14, brainpoolP384r1's 379795560371 and
       numsp512t1's 11602586981;
     * tier 2 (B1 = 50 000): cp6_782's p22 and numsp512t1's p15;
     * tier 3 (B1 = 250 000): ed-382-mont's p29.
   * On numsp512t1, tier 3 returned a **composite** 46-digit factor.
     * CADO-NFS failed on that C46 (rc = 1, 20:55:46Z).
     * After the driver restart (22:22:21Z), PARI `factorint` split it into
       p18 · p29 in under a second.  Those two carry `PARI factorint (0 s)`.
   * Every other factor came from the survey's `PARI factor(N, 2^32)`.
   * The wall times are those of one run on a shared 4-core machine. They
     are not measurements of how hard any number is.
5. **Excluded:**
   * P-256, P-384, P-521 and Curve25519, certified in
     `../endosweep_nist_20261006`, and the 18 curves of batch 1 are complete
     in snapshot 2 too.  They are not repeated.
   * 15 snapshot-2 entries still had an open composite, so they are not in
     this directory: numsp384t1 (CADO-NFS running on its C104), bw6_761,
     E-382, numsp384d1, Curve41417, w-510-mont, ed-510-mont, ed-512-mont,
     brainpoolP512r1, numsp512d1, ed-511-mers, M-511, gost512, E-521 and
     ed_on_mnt4_753.

## Scope

* These are exact integer facts about `t² − 4q`, plus the standard theory
  that `End(E)` is an order of `Q(√D_K)` containing `Z[π]`, whose
  non-scalar elements have norm at least `(|D_K| + (D_K mod 2))/4`.
* No attack, speed-up or weakness is claimed.  A large `|D_K|` rules out a
  small-degree endomorphism and nothing else.  The small `|D_K|` of cp6_782
  only allows one; whether `End(E)` contains one was not checked.
* Primality is PARI `isprime`, which is a proof.  Lean re-proves only the
  factors below 10^8 (below).

## Files

| file | what |
|:--|:--|
| `factorizations.jsonl` | the 6 complete factorisation certificates of `4q − t²`, in batch 1's schema (`found_by` a per-factor list, `seconds` null) |
| `dk_exact.json` | per curve: `p`, `n`, `h`, `t`, `4q − t²`, factorisation, `found_by`, squarefree part, `f`, `D_K`, log2, least non-scalar degree, source, std-curves check; and the 22 excluded curves with the file that certifies each |
| `dk_exact.md` | the generated table, with who found each factor |
| `provenance/` | the second frozen driver snapshot, its event log, and the six survey records |
| `report/` | `report.typ`, the graph `dk_exact.svg` (drawn by batch 1's `plot_dk.py`) and `report.pdf` |
| `SHA256SUMS` | hashes of the data files |

The scripts are batch 1's, in
[`../endosweep_dk_exact_20261016/`](../endosweep_dk_exact_20261016/).

## Regenerating

From the repository root, with `STD_CURVES_CHECKOUT` J08nY/std-curves at commit
`77fe6e3585ca2c2225b59d7df24b7c775437276f`:

```sh
B1=research/endosweep_dk_exact_20261016
B2=research/endosweep_dk_exact_batch2_20261016
# The certificates, from the copied survey records and the second frozen snapshot:
nice -n 10 python3 $B1/make_factorizations.py STD_CURVES_CHECKOUT research/endosweep_curves_20261006 \
    --dir $B2 --snapshot provenance/driver_state.snapshot2.json \
    --exclude-certified $B1/factorizations.jsonl
# The results:
nice -n 10 python3 $B1/build_dk_exact.py STD_CURVES_CHECKOUT research/endosweep_curves_20261006 \
    --dir $B2 --exclude-certified $B1/factorizations.jsonl
# The Lean file:
python3 $B1/lean/gen_dk_exact_lean.py . --dir $B2 --module DkExactBatch2 \
    --target formal/targets/endosweep-dk-exact-batch2-discriminants.yaml
# The graph and the PDF (matplotlib and the typst wheel):
python3 $B1/report/plot_dk.py $B2/report
python3 -c "import typst; typst.compile('$B2/report/report.typ', \
    output='$B2/report/report.pdf', root='$B2')"
# Checks:
(cd $B2 && sha256sum -c SHA256SUMS)
python3 -m pytest -q tests/test_endosweep_dk_exact_batch2.py
```

The same scripts with no options regenerate batch 1.  Its README's `typst`
line needs `root='research/endosweep_dk_exact_20261016'` as well, because its
`report.typ` reads `../dk_exact.json`.

## Lean verification

`formal/CryptoResearch/Endosweep/DkExactBatch2.lean` is generated by batch
1's `lean/gen_dk_exact_lean.py` with `--module DkExactBatch2`.

* **What it imports and reuses.** It imports `CryptoResearch.Endosweep.DkExact`
  and reuses its `DkCert`, `DkCert.Statement` and `DkCert.statement_of_holds`,
  and through them NistCertificates' `FactoredCert`, `noDivBelow` and its 10^8
  threshold.  It defines none of them again and has only data and proofs.
  It is core Lean, with no Mathlib.
* **Its target.** The frozen target spec is
  `formal/targets/endosweep-dk-exact-batch2-discriminants.yaml`
  (`TASK-20261016-892515`).  The id was checked for collisions in the whole
  tree at `HEAD`, and in `formal/targets` and `coordination` on every
  remote branch tip.
* **Its namespace** is `CryptoResearch.Endosweep.DkExactBatch2`.

Per curve, `<curve>_holds` is closed arithmetic checked by `decide +kernel`.
`<curve>_certificate : <curve>.Statement` states the same propositions as in
batch 1:

* `q + 1 − t = h·n`, and `t² − 4q = D_K·f²`;
* the factorisation multiplies back;
* the squarefree part and the construction of `D_K` from it;
* `IsDisc D_K`, and the recorded degree;
* `2^L ≤ |D_K| < 2^(L+1)`, and the degree is at least `2^(L−2)`;
* if the listed factors above 10^8 are prime, `D_K` is fundamental.

The theorems are `oscaa_SM2_certificate`, `nums_ed_382_mont_certificate`,
`brainpool_brainpoolP384r1_certificate`, `nums_numsp512t1_certificate`,
`bn_bn606_certificate` and `arkworks_cp6_782_certificate`.

**`DkExactBatch2.exact_discriminants`** collects all six certificates, plus:

* `D_K = −3` on bn606;
* `D_K = −339` on cp6_782;
* on the other four curves, `|D_K| ≥ 2^257` and
  `min_nonscalar_degree(D_K) ≥ 2^255`.

The generator's one functional change for this batch: curves with
`|D_K| < 2^20` are stated as equalities and kept out of the size bound.  In
batch 1 those were exactly the `D_K = −3` curves, and its output is unchanged.

**The primality hypothesis.** As in `DkExact`, the factors above 10^8 are an
explicit hypothesis: Lean does not prove them prime. PARI `isprime` proved
them.  Factors below 10^8 are proved prime in Lean by trial division.

**Not certified:**

* the primality of `p` and `n`;
* that `t` is the trace of Frobenius of the named curve;
* any elliptic-curve fact;
* which order `End(E)` is.

**Checked locally** with Lean 4 (`leanprover/lean4:v4.35.0-rc1`,
`formal/lean-toolchain`), using `lean -o` on `Discriminant.lean`,
`NistCertificates.lean`, `DkExact.lean` and `DkExactBatch2.lean` in order:

* all four compile;
* `#print axioms` gives `[propext, Classical.choice, Quot.sound]` on
  `exact_discriminants`, on the six certificates and on
  `DkExact.DkCert.statement_of_holds`;
* the file has no `sorry`, `admit`, `axiom`, `unsafe` or `native_decide`.

**Negative controls.** Two edited copies were compiled, and the kernel
rejected both: `decide` proved `oscaa_SM2.Holds` and `arkworks_cp6_782.Holds`
false.

* In the first, one digit of SM2's p41 was changed in its factor list.
* In the second, one digit of cp6_782's `n` was changed.
