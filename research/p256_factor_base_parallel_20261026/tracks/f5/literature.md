# F5 source review before implementation

26 October 2026; worker `/root/pass2_geometry`, task TASK-20261026-26de77.
This note precedes all second-pass observation data. Native inherited model
binding is unprobed. No claim of novelty or canonical review admission is made.

- **Internal, read:** the prior F5 report, `exact.sage.py`,
  `composition.sage.py`, serialized kernel/map/dual records and `identities.json`
  under `research/p256_factor_base_parallel_20261025/tracks/f5/`; and the
  separate `reviews/maps_and_covers/independent_checks.py` and source records.
  These supply all four maps (degrees 3, 5, 11, 11), function-field composition
  certificates and exact endpoint identities. They do not supply a cheaper
  relation solver.
- **Internal, read:** the prior F1 generic depth-four signed domain and solver
  code. Eight canonical points will be selected by the frozen rule in the new
  protocol, without resampling endpoint bases or selecting for relation yield.
- **Retrieved and read:** [official Sage isogeny reference](https://doc.sagemath.org/html/en/reference/arithmetic_curves/sage/schemes/elliptic_curves/ell_curve_isogeny.html),
  `dual`, `rational_maps`, and `scaling_factor` entries (current documentation
  identifies version 10.8). The dual satisfies both multiplication-by-degree
  compositions. A normalized Vélu map has differential scale one; its dual
  generally has scale equal to the degree. The finite subgroup inverse used
  here is `[ell^-1 mod r] dual`, not a claim that the dual is normalized.

The primary API documentation is checked against the pinned prior Sage 10.6
output rather than assuming identical current behavior. The second pass uses
its own stdlib arithmetic and the serialized maps, not current Sage routines.
The prior parameter/order and global map certificates remain explicit inputs;
fresh bounded point tests do not replace those proofs. Kernel poles are
certified algebraically from numerator/denominator coprimality, not by claiming
nonidentity rational small torsion on the prime-order target.

No additional primary theorem about relation costs is asserted. Literature
supports map semantics only; a representation change alone supplies no ECDLP
advantage. S3 checkpoint rejection and pending disclosure approval prohibit
all experimental execution until root's exact Phase B release.
