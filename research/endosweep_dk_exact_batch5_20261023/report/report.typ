#set page(paper: "a4", margin: 1.6cm, flipped: true)
#set text(size: 9pt)
#let d = json("../dk_exact.json")
#let o = json("../open_composites.json")

= Exact CM discriminant of gost512 (batch 5), and the four composites still open

research/endosweep_dk_exact_batch5_20261023 (2026-10-23). Data: `dk_exact.json`, `factorizations.jsonl`,
`open_composites.json`; std-curves commit #raw(d.std_curves_commit). Every factor of $4q - t^2$ is proved
prime by PARI `isprime`. These are exact computations, not measurements; the README states method, scope and
regeneration.

*Part A.* gost/gost512 is the one curve completed between the fourth frozen driver snapshot (batch 4) and the
fifth (2026-10-23). Its $4q - t^2$ (155 digits) is $19870558523 dot p_71 dot p_74$. The 11-digit factor was
found by GMP-ECM at B1 = 11000. *The split of the 144-digit cofactor into $p_71 dot p_74$ was not found by this
project:* it was fetched from FactorDB (number id 1100000009030548498, fetched 2026-10-22T23:04:32Z), after the
driver's ECM had run the complete B1 = 3·10^6 tier (2400 curves) and 1200 of 4480 curves at B1 = 11·10^6 on it
without a factor. FactorDB does not say who found the split. Both primes were re-proved here and the product
re-checked against $4q - t^2$ recomputed from the curve parameters. std-curves records no `cm_disc`, so $D_K$
was not checked against the literature.

#figure(image("dk_exact.svg", width: 85%),
  caption: [(a) $log_2 |D_K|$ against $p$ for gost512 ($f = 1$). (b) The bits between $log_2 4q$ and
  $log_2 |D_K|$. Recorded values from `dk_exact.json`.])

#let short(s, n) = if s.len() <= n { s } else { "(" + str(s.trim("-").len()) + " digits)" }
#table(
  columns: 9,
  align: (left, right, right, right, left, right, right, right, left),
  table.header[*curve*][*p bits*][*4q−t² digits*][*s digits*][*f*][*D_K*][*log2 |D_K|*][*min degree*][*std-curves*],
  ..d.curves.map(r => (
    r.curve, str(r.p_bits), str(r.N_digits), str(r.squarefree_part_digits), short(r.conductor_f, 6),
    short(r.D_K, 6), str(r.log2_abs_D_K),
    if r.min_nonscalar_degree.len() <= 6 { r.min_nonscalar_degree } else { "2^" + str(r.log2_min_nonscalar_degree) },
    r.std_curves_check.replace("std-curves records ", ""),
  )).flatten()
)

Lean: `CryptoResearch.Endosweep.DkExactBatch5.exact_discriminants` (target `TASK-20261023-6fca5a`), reusing
`DkExact.DkCert`; fundamentality is conditional on the primality of the factors above $10^8$ (PARI, not Lean).

#pagebreak()
== Part B: the four $4q - t^2$ still open at snapshot 5

No $D_K$ is stated for these. Curves per B1 are those the driver state records; the coverage columns divide
them by GMP-ECM 7.0.5's own expected-curve table (`ecm -v`) and give $exp(-sum)$, the approximate chance that
a factor of that size, if one exists, was missed (an idealised model). ed-511-mers' C133 has been on CADO-NFS
since 2026-10-22T23:05Z (in progress); the C146 to C152 are beyond practical NFS on this 4-core machine.

#table(
  columns: 11,
  align: (left, right, right, right, right, right, right, right, right, right, left),
  table.header[*curve*][*cofactor*][*11e3*][*5e4*][*2.5e5*][*1e6*][*3e6*][*11e6 (of 4480)*][*Σ/E 40 dig.*][*Σ/E 45 dig.*][*FactorDB*],
  ..o.curves.map(r => {
    let c(b) = {
      let t = r.ecm.filter(x => x.B1 == b)
      if t.len() == 0 { "0" } else if t.at(0).curves == none { "≤ 90 (n.r.)" } else { str(t.at(0).curves) }
    }
    (r.curve, "C" + str(r.cofactor_digits), c(11000), c(50000), c(250000), c(1000000), c(3000000), c(11000000),
     str(calc.round(r.ecm_coverage.at("40").sum_curves_over_expected, digits: 2)),
     str(calc.round(r.ecm_coverage.at("45").sum_curves_over_expected, digits: 2)),
     r.factordb.status)
  }).flatten()
)

#figure(image("ecm_effort.svg", width: 85%),
  caption: [(a) ECM curves per B1 tier on each open cofactor at snapshot 5. (b) The same effort in units of
  GMP-ECM's expected number of curves per factor size; 1 (dashed) is one expected find.])
