#set page(paper: "a4", margin: 1.6cm, flipped: true)
#set text(size: 9pt)
#let d = json("../dk_exact.json")

= Exact CM discriminants of 18 standardized curves

research/endosweep_dk_exact_20261016 (2026-10-16). Data: `dk_exact.json`, `factorizations.jsonl`;
std-curves commit #raw(d.std_curves_commit). Every factor of $4q - t^2$ is proved prime by PARI `isprime`.
These are exact computations, not measurements; the README states method, scope and regeneration.
No $D_K$ here was checked against the literature; seven agree with the `cm_disc` std-curves records.

#figure(image("dk_exact.svg", width: 100%),
  caption: [(a) $log_2 |D_K|$ against $p$ for the 15 curves without CM by construction, coloured by the
  conductor $f$. (b) The bits between $log_2 4q$ and $log_2 |D_K|$. Recorded values from `dk_exact.json`.])

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

Excluded (already in research/endosweep_nist_20261006/factorizations.jsonl): P-256, P-384, P-521, Curve25519.
Lean: `CryptoResearch.Endosweep.DkExact.exact_discriminants` (target `TASK-20261016-f6a5e8`) checks, per curve,
$q + 1 - t = h n$, $t^2 - 4q = D_K f^2$, the product of the factors, the squarefree part and the $D_K$ construction,
$D_K equiv 0, 1 thin (mod 4)$ and the degree bound; fundamentality is conditional on the primality of the
factors above $10^8$ (PARI, not Lean).
