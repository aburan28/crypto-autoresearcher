#set page(paper: "a4", margin: 1.6cm, flipped: true)
#set text(size: 9pt)
#let d = json("../dk_exact.json")

= Exact CM discriminants of 6 more standardized curves (batch 2)

research/endosweep_dk_exact_batch2_20261016 (2026-10-16). Data: `dk_exact.json`, `factorizations.jsonl`;
std-curves commit #raw(d.std_curves_commit). Every factor of $4q - t^2$ is proved prime by PARI `isprime`.
These are exact computations, not measurements; the README states method, scope and regeneration.
They are the six curves the factoring driver completed between the frozen snapshot of batch 1
(research/endosweep_dk_exact_20261016) and the second frozen snapshot, five of them by a CADO-NFS split.
std-curves records no `cm_disc` for any of the six, so none was checked against the literature.

#figure(image("dk_exact.svg", width: 100%),
  caption: [(a) $log_2 |D_K|$ against $p$ for the 4 curves with a large $D_K$, coloured by the
  conductor $f$. (b) The bits between $log_2 4q$ and $log_2 |D_K|$. Recorded values from `dk_exact.json`.
  Not drawn: $D_K = -3$ on bn606 and $D_K = -339$ on cp6_782.])

#pagebreak()
== Results

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

Excluded: P-256, P-384, P-521, Curve25519 (research/endosweep_nist_20261006) and the 18 curves of
research/endosweep_dk_exact_20261016.
Lean: `CryptoResearch.Endosweep.DkExactBatch2.exact_discriminants` (target `TASK-20261016-892515`) checks, per curve,
$q + 1 - t = h n$, $t^2 - 4q = D_K f^2$, the product of the factors, the squarefree part and the $D_K$ construction,
$D_K equiv 0, 1 thin (mod 4)$ and the degree bound, reusing `DkExact.DkCert`; fundamentality is conditional on
the primality of the factors above $10^8$ (PARI, not Lean).
