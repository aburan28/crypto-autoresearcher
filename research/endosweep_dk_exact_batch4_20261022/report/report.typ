#set page(paper: "a4", margin: 1.6cm, flipped: true)
#set text(size: 9pt)
#let d = json("../dk_exact.json")

= Exact CM discriminants of 7 more standardized curves (batch 4)

research/endosweep_dk_exact_batch4_20261022 (2026-10-22). Data: `dk_exact.json`, `factorizations.jsonl`;
std-curves commit #raw(d.std_curves_commit). Every factor of $4q - t^2$ is proved prime by PARI `isprime`.
These are exact computations, not measurements; the README states method, scope and regeneration.
They are the seven curves the factoring driver completed between the third frozen snapshot (batch 3,
research/endosweep_dk_exact_batch3_20261017) and the fourth (2026-10-22): three by a CADO-NFS split
(C112, C117, C121) and four by GMP-ECM (B1 = 10^6 or 3·10^6).
std-curves records no `cm_disc` for any of the seven, so none was checked against the literature.
On 2026-10-17 at about 11:36Z the driver crashed (a cypari2 segfault: `isprime` called from ECM worker threads);
its saved state then held numsp512d1 and ed_on_mnt4_753 as complete with the parts of their last split missing.
Both entries were restored from snapshot 3, the driver was fixed, and ECM found both factors again at
B1 = 10^6 (12:32Z and 12:38Z). Every factor here is re-proved prime and multiplied back to $4q - t^2$.

#figure(image("dk_exact.svg", width: 100%),
  caption: [(a) $log_2 |D_K|$ against $p$ for the 7 curves, all with a large $D_K$, coloured by the
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

Excluded: P-256, P-384, P-521, Curve25519 (research/endosweep_nist_20261006), the 18 curves of
research/endosweep_dk_exact_20261016, the 6 of research/endosweep_dk_exact_batch2_20261016 and the 3 of
research/endosweep_dk_exact_batch3_20261017.
Lean: `CryptoResearch.Endosweep.DkExactBatch4.exact_discriminants` (target `TASK-20261022-ff60b1`) checks, per curve,
$q + 1 - t = h n$, $t^2 - 4q = D_K f^2$, the product of the factors, the squarefree part and the $D_K$ construction,
$D_K equiv 0, 1 thin (mod 4)$ and the degree bound, reusing `DkExact.DkCert`; fundamentality is conditional on
the primality of the factors above $10^8$ (PARI, not Lean).
