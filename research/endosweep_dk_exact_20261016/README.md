# Exact CM discriminants of 18 more standardized curves

**Question.**  For which standardized prime-field curves can `4q − t²` now be
factored completely, and what are their exact CM field discriminant `D_K`,
conductor `f` and least non-scalar endomorphism degree?  The NIST run
([`../endosweep_nist_20261006`](../endosweep_nist_20261006/README.md)) did
this for the NIST curves.  On most other curves `|D_K|` was only bounded,
because a 10-second factoring screen left a composite part of `4q − t²`
unsplit.  This directory takes every curve whose composite part the factoring
driver has since split completely and records the exact result.

## Method

1. **The 10 s screen** ([`provenance/survey.py`](provenance/survey.py), summary
   in [`provenance/SUMMARY.md`](provenance/SUMMARY.md)).
   * It loaded the corpus with `corpus.load_std_curves` from std-curves at
     `77fe6e3585ca2c2225b59d7df24b7c775437276f`, plus
     `research/endosweep_curves_20261006/arkworks/curves.json`.
   * Every prime-field curve was verified with `targets.verify` (`n` prime,
     `h·n` in the Hasse interval, a point killed by `h·n`), leaving 155
     distinct curves.
   * For each curve, `t = q + 1 − h·n` and `N = 4q − t²`. PARI `factorint(N)`
     ran with a 10 s wall-clock limit (`LIMIT=10`). On a timeout,
     `factor(N, 2^32)` kept the small primes and the composite cofactor `C`.
   * The records of the 18 curves below are in
     [`provenance/survey_selected.jsonl`](provenance/survey_selected.jsonl).
2. **The factoring driver** ([`provenance/driver.py`](provenance/driver.py),
   input [`provenance/jobs.json`](provenance/jobs.json)).
   * It took the 43 open cofactors and ran ECM tiers on all of them, four
     composites in parallel. The tiers used GMP-ECM 7.0.5:
     `nice -n 5 ecm -q -one -c CURVES B1`.

     | tier | B1 | curves |
     |--:|--:|--:|
     | 1 | 11 000 | 90 |
     | 2 | 50 000 | 240 |
     | 3 | 250 000 | 500 |
   * PARI `factorint` took the composites of at most 60 digits.
   * CADO-NFS took the rest, smallest first, up to 121 digits:
     `nice -n 5 python3 cado-nfs.py C -t 4 -w WORKDIR`. This is CADO-NFS
     3.0.0, git `692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b` (`git rev-parse
     HEAD` of the checkout used).
   * A fourth ECM tier (B1 = 10^6, 900 curves) was started at 20:55:46Z. The
     event log records no factor from it before the driver was restarted at
     22:22:21Z for the CADO stage.
   * The run used a **frozen snapshot** of the driver state,
     [`provenance/driver_state.snapshot.json`](provenance/driver_state.snapshot.json),
     taken at 22:24Z while CADO-NFS was still running. The event log up to
     the snapshot is
     [`provenance/driver_events.snapshot.log`](provenance/driver_events.snapshot.log).
3. **Certificates** ([`make_factorizations.py`](make_factorizations.py) →
   [`factorizations.jsonl`](factorizations.jsonl)).
   * The script takes every snapshot entry with `open == []`. It skips the
     four that `endosweep_nist_20261006` already certifies.
   * It joins the survey's small primes to the primes of `C`. On the `D = −3`
     curves the survey left `C²`, and the exponent is recovered by division.
   * `found_by` is a list, one entry per factor, in the NIST schema otherwise.
     It is reconstructed by replaying the snapshot's split log (`how:
     n-digit -> a x b`) against the order in which the driver appended the
     primes. Both parts of a split get that split's method.
4. **Results** ([`build_dk_exact.py`](build_dk_exact.py) →
   [`dk_exact.json`](dk_exact.json), [`dk_exact.md`](dk_exact.md)).
   * Everything is recomputed from the curve constants. Each curve is
     reloaded and re-verified, `t` and `N` are recomputed, and the factors
     must multiply back to `N` exactly.
   * Every factor is proved prime with PARI 2.15.4 `isprime`, a proof and not
     a pseudoprime test.
   * `D_K` and `f` come from `nist.exact_discriminant`. The odd-exponent
     primes give the squarefree part `s` of `4q − t²`. Then `D_K = −s` if
     `−s ≡ 1 (mod 4)`. Otherwise `D_K = −4s` and `f` is halved, which needs
     `4 | 4q − t²` with `f` even.
   * `D_K` is re-checked to be fundamental, and `t² − 4q = D_K·f²` is
     re-checked.
   * The least non-scalar degree is `quadorder.min_nonscalar_degree(D_K) =
     (|D_K| + (D_K mod 2))/4`.
   * Where std-curves records `cm_disc` and `conductor`, both are compared,
     and a disagreement stops the script.

## Results

| curve | p bits | 4q−t² digits | factorisation of 4q−t² | f | D_K | log2 \|D_K\| | least non-scalar degree | already public? |
|:--|--:|--:|:--|--:|:--|--:|--:|:--|
| x962/prime239v2 | 239 | 73 | 5² · 11 · 5830789 · p24 · p40 | 5 | −(71 digits) | 235.78 | 2^233.78 | std-curves `cm_disc`, `conductor` (agree) |
| nums/ed-255-mers | 255 | 78 | 2² · 443 · 647 · 40193 · p31 · p36 | 2 | −(77 digits) | 254.77 | 2^252.77 | (not checked against literature) |
| nums/w-255-mers | 255 | 78 | 13 · 17 · 739 · p27 · p46 | 1 | −(78 digits) | 256.83 | 2^254.83 | std-curves (agree) |
| nums/numsp256d1 | 256 | 78 | 984952349 · p23 · p47 | 1 | −(78 digits) | 258.00 | 2^256.00 | std-curves (agree) |
| other/BADA55-R-256 | 256 | 78 | 5² · p20 · p58 | 5 | −(77 digits) | 252.69 | 2^250.69 | std-curves (agree) |
| other/MDC201601 | 256 | 77 | 2² · 7 · 1423 · 75193 · p27 · p42 | 2 | −(77 digits) | 253.20 | 2^251.20 | (not checked against literature) |
| other/ssc-288 | 288 | 87 | 29 · 239 · 30092263963 · p26 · p47 | 1 | −(87 digits) | 288.16 | 2^286.16 | std-curves (agree) |
| arkworks/ed_on_bw6_761 (= ed_on_cp6_782) | 377 | 114 | 2⁵ · 83 · 139 · 179 · 383 · 7349 · p15 · p28 · p58 | 2 | −(114 digits), `−4s` | 376.51 | 2^374.51 | (not checked against literature) |
| nums/ed-383-mers | 383 | 116 | 2² · 2819 · 1322369 · 526459501063 · 828591709009 · p15 · p26 · p43 | 2 | −(116 digits) | 382.96 | 2^380.96 | (not checked against literature) |
| nums/ed-384-mont | 384 | 117 | 2² · 13 · p17 · p24 · p75 | 2 | −(116 digits) | 383.45 | 2^381.45 | (not checked against literature) |
| nums/w-384-mont | 384 | 117 | 13 · 128191201 · 152102048827 · p18 · p29 · p50 | 1 | −(117 digits) | 385.43 | 2^383.43 | (not checked against literature) |
| bn/bn510 | 510 | 154 | 3 · 1307² · p37² · p37′² | 77 digits | −3 | 1.58 | 1 | `D = −3` by construction; std-curves (agree) |
| nums/w-511-mers | 511 | 155 | 7 · 1721 · p30 · p122 | 1 | −(155 digits) | 512.85 | 2^510.85 | (not checked against literature) |
| gost/id-tc26-gost-3410-2012-512-paramSetC | 512 | 155 | 2² · 139 · 149 · 2702671 · p20 · p124 | 2 | −(155 digits) | 511.71 | 2^509.71 | (not checked against literature) |
| nums/w-512-mont | 512 | 155 | 241 · 2178797 · p15 · p27 · p106 | 1 | −(155 digits) | 513.85 | 2^511.85 | (not checked against literature) |
| other/ssc-512 | 512 | 155 | 7² · 19 · 23 · 47 · 149 · 10955913739 · p23 · p114 | 7 | −(153 digits) | 507.44 | 2^505.44 | (not checked against literature) |
| bls/BLS12-638 | 638 | 193 | 3 · 7² · 67⁴ · 79² · 5563² · 2099837² · 13273591² · p18² · p22² · p34² | 97 digits | −3 | 1.58 | 1 | `D = −3` by construction; std-curves (agree) |
| arkworks/bw6_767 | 767 | 232 | 2² · 3 · 7⁴ · 67² · 3607² · 2757659² · p16² · p22² · p65² | 116 digits | −3 | 1.58 | 1 | `D = −3` by construction (not checked against literature) |

* `pN` is an N-digit prime; [`dk_exact.json`](dk_exact.json) has every
  number in full, including `t`, `n`, `h`, the squarefree part `s` and `D_K`.
* Where the table shows no `−4s`, `D_K = −s`: there `s ≡ 3 (mod 4)` and `D_K`
  is minus the squarefree part.
* The "least non-scalar degree" column is `(|D_K| + (D_K mod 2))/4`, which is
  about `|D_K|/4`. It is a lower bound for the degree of every endomorphism
  outside `Z`, whichever order between `Z[π]` and `O_K` `End(E)` is.
* [`dk_exact.md`](dk_exact.md) gives the same table with the squarefree part
  and `t`, and names the method that found each factor.

**Already public?**  Seven of the `D_K` values agree with the `cm_disc` and
`conductor` that std-curves records: prime239v2, w-255-mers, numsp256d1,
BADA55-R-256, ssc-288, bn510 and BLS12-638. They are therefore not new as
numbers. What is new for them is the complete prime factorisation, with its
proofs. The other eleven were **not checked against literature**. Their
sources may already publish them, including FactorDB:

* the NUMS paper (ePrint 2014/130);
* the Million Dollar Curve;
* TC26;
* the arkworks/ZEXE papers.

On the three `D = −3` curves (bn510, BLS12-638, bw6_767), `D_K = −3` holds by
construction (`j = 0`). The only new item there is the factorisation of the
conductor.

## Findings

1. **Eighteen more curves have an exact `D_K`.**
   * On the fifteen curves without CM by construction, `|D_K|` lies between
     2^235.78 (x962/prime239v2) and 2^513.85 (nums/w-512-mont).
   * `log2 |D_K|` is within 6.3 bits of `log2(4q)` on every one of them. The
     largest gaps are ssc-512 (6.21), BADA55-R-256 (5.23) and prime239v2
     (5.22). These gaps are the conductors `f = 7, 5, 5`, which account for
     `log2 f²` = 5.61, 4.64 and 4.64 bits. The rest is the difference
     between `4q` and `4q − t²`.
   * So the least non-scalar endomorphism degree is at least 2^233.78 on
     every one of these curves, and none has a small-degree endomorphism
     beyond the integers.
   * Lean proves the arithmetic of `|D_K| ≥ 2^235` and degree `≥ 2^233` on
     them (below).
2. **The conductors are small.**
   * `f = 1` on w-255-mers, numsp256d1, ssc-288, w-384-mont, w-511-mers and
     w-512-mont. There `End(E) = Z[π]`.
   * `f = 2` on ed-255-mers, MDC201601, ed_on_bw6_761, ed-383-mers,
     ed-384-mont and the GOST paramSetC curve. All six are (twisted) Edwards
     curves, so `h·n` and `t` are even and `4 | 4q − t²`. That `f` is exactly
     2 is a property of these curves, not a consequence of the model.
   * `f = 5` on prime239v2 and BADA55-R-256, and `f = 7` on ssc-512.
   * On the `D = −3` curves, `f` has 77, 97 and 116 digits.
3. **Every factor was found by the methods named per factor.**
   * GMP-ECM tiers 1 to 3 found every large factor except those of three
     composites, which CADO-NFS split:
     * ed-255-mers' C67, into p31 · p36 in 37 s wall;
     * ed-383-mers' C69, into p26 · p43 in 33 s wall;
     * bn510's C74, into p37 · p37′ in 68 s wall.
   * The largest factor ECM itself returned is a p30, on w-511-mers.
   * The largest prime left as an ECM cofactor is a p124, on GOST
     paramSetC.
4. **Excluded:**
   * P-256, P-384, P-521 and Curve25519 are complete in the snapshot too.
     They are already certified, with the same `4q − t²`, in
     [`../endosweep_nist_20261006/factorizations.jsonl`](../endosweep_nist_20261006/factorizations.jsonl),
     and are not repeated here.
   * 21 snapshot entries still had an open composite, so they are not in
     this directory: SM2, bn606, numsp384t1, bw6_761, ed-382-mont, E-382,
     brainpoolP384r1, cp6_782, numsp384d1, Curve41417, numsp512t1,
     w-510-mont, ed-510-mont, ed-512-mont, brainpoolP512r1, numsp512d1,
     ed-511-mers, M-511, gost512, E-521 and ed_on_mnt4_753.
   * After the snapshot (22:26Z), the driver's live event log reports a
     CADO-NFS split of numsp512t1's last composite, C75. This directory uses
     only the frozen snapshot, so numsp512t1 stays excluded.

## Scope

* These are exact integer facts about `t² − 4q`, plus the standard theory
  that `End(E)` is an order of `Q(√D_K)` containing `Z[π]`, whose
  non-scalar elements have norm at least `(|D_K| + (D_K mod 2))/4`.
* No attack, speed-up or weakness is claimed. A large `|D_K|` rules out a
  small-degree endomorphism and nothing else.
* Primality is PARI `isprime`, which is a proof. Lean re-proves only the
  factors below 10^8 (below).
* The 10 s screen and the ECM tiers are effort levels. They are not
  measurements of how hard any number is.

## Files

| file | what |
|:--|:--|
| `factorizations.jsonl` | the 18 complete factorisation certificates of `4q − t²`. Same schema as the NIST file, with `found_by` a per-factor list and `seconds` null, because per-split times were not recorded for ECM |
| `dk_exact.json` | per curve: `p`, `n`, `h`, `t`, `4q − t²`, factorisation, `found_by`, squarefree part, `f`, `D_K`, log2, least non-scalar degree, source, std-curves check |
| `dk_exact.md` | the generated table, with who found each factor |
| `build_dk_exact.py` | recomputes `dk_exact.json` and `dk_exact.md` from the curve constants and `factorizations.jsonl` |
| `make_factorizations.py` | assembles `factorizations.jsonl` from the survey records and the driver snapshot |
| `provenance/` | `survey.py` (with its `SUMMARY.md` and the 18 records it wrote), `driver.py`, `jobs.json`, the frozen driver snapshot and its event log |
| `lean/gen_dk_exact_lean.py` | generates `formal/CryptoResearch/Endosweep/DkExact.lean` |
| `report/` | `report.typ`, the graph `dk_exact.svg` with its script `plot_dk.py`, and `report.pdf` |
| `SHA256SUMS` | hashes of the data files |

## Regenerating

```sh
# The 10 s screen (provenance; survey.py inserts /home/user/wt/native-export
# into sys.path: point it at a checkout of this repository):
LIMIT=10 nice -n 10 python3 research/endosweep_dk_exact_20261016/provenance/survey.py \
    STD_CURVES_CHECKOUT research/endosweep_curves_20261006 survey.jsonl
# The driver (provenance; it reads jobs.json next to it and the NIST
# factorizations.jsonl, and expects a CADO-NFS checkout at ../cado-nfs):
nice -n 10 python3 research/endosweep_dk_exact_20261016/provenance/driver.py

# The certificates, from the copied survey records and the frozen snapshot:
nice -n 10 python3 research/endosweep_dk_exact_20261016/make_factorizations.py \
    STD_CURVES_CHECKOUT research/endosweep_curves_20261006
# The results:
nice -n 10 python3 research/endosweep_dk_exact_20261016/build_dk_exact.py \
    STD_CURVES_CHECKOUT research/endosweep_curves_20261006
# The Lean file:
python3 research/endosweep_dk_exact_20261016/lean/gen_dk_exact_lean.py .
# The graph and the PDF (matplotlib and the typst wheel):
python3 research/endosweep_dk_exact_20261016/report/plot_dk.py
python3 -c "import typst; typst.compile('research/endosweep_dk_exact_20261016/report/report.typ', \
    output='research/endosweep_dk_exact_20261016/report/report.pdf')"
# Checks:
(cd research/endosweep_dk_exact_20261016 && sha256sum -c SHA256SUMS)
python3 -m pytest -q tests/test_endosweep_dk_exact.py
```

`STD_CURVES_CHECKOUT` is J08nY/std-curves at commit
`77fe6e3585ca2c2225b59d7df24b7c775437276f`.

## Lean verification

`formal/CryptoResearch/Endosweep/DkExact.lean` is generated by
`lean/gen_dk_exact_lean.py`.

* **What it imports and reuses.** It imports `NistCertificates` and reuses its
  `FactoredCert`, its `noDivBelow` trial division and its 10^8 threshold.
  It is core Lean, with no Mathlib.
* **Its target.** The frozen target spec is
  `formal/targets/endosweep-dk-exact-discriminants.yaml`
  (`TASK-20261016-f6a5e8`).
* **How it is generated.** The generator re-derives every number from
  `dk_exact.json` and `factorizations.jsonl`, and refuses to write on any
  mismatch.

Per curve, `<curve>_holds` is closed arithmetic checked by `decide +kernel`.
`<curve>_certificate` (`DkCert.Statement`) states:

* `q + 1 − t = h·n`, and `t² − 4q = D_K·f²`;
* `4q − t²` is the product of the certificate's prime powers;
* the odd-exponent primes are `oddPrimes`, and their product is the
  squarefree part `s`;
* `D_K = −s` with `D_K ≡ 1 (mod 4)`, or `D_K = −4s` with `−s ≡ 2, 3 (mod 4)`;
* `IsDisc D_K`, that is `D_K < 0` and `D_K ≡ 0, 1 (mod 4)`;
* `minNonscalarDegree D_K` is the recorded degree;
* `2^L ≤ |D_K| < 2^(L+1)`, and the degree is at least `2^(L−2)`;
* if the listed factors above 10^8 are prime, `D_K` is fundamental.

**`DkExact.exact_discriminants`** collects all 18 certificates. It adds that
`D_K = −3` on bn510, BLS12-638 and bw6_767. On the other 15 curves it adds
`|D_K| ≥ 2^235` and `min_nonscalar_degree(D_K) ≥ 2^233`.

**The primality hypothesis.** As in `NistCertificates`, the factors above
10^8 are an explicit hypothesis: Lean does not prove them prime. PARI
`isprime` proved them. Factors below 10^8 are proved prime in Lean by trial
division.

**Not certified:**

* the primality of `p` and `n`;
* that `t` is the trace of Frobenius of the named curve;
* any elliptic-curve fact;
* the uniqueness of the fundamental discriminant in a square class.

**Checked locally** with Lean 4 (the `formal/lean-toolchain` toolchain),
using `lean -o` on `Discriminant.lean`, `NistCertificates.lean` and
`DkExact.lean` in order:

* all three compile;
* `#print axioms` on `exact_discriminants`, `DkCert.statement_of_holds` and
  the per-curve certificates gives `[propext, Classical.choice, Quot.sound]`;
* the file has no `sorry`, `admit`, `axiom`, `unsafe` or `native_decide`.

**Negative controls.** Two edited copies were compiled, and the kernel
rejected both, with `decide` proving the proposition false:

* one digit of prime239v2's p40 changed in its factor list;
* one digit of bn510's `n` changed.
