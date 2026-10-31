# Separate full-RREF certificate exporter

The reference D4 producer completes closure before constructing its quotient
map. Its exporter reduces each pivot monomial by XORing the quotient images
of all later nonzero columns. The current n45 polynomial02 run is executing
that stage after reporting zero new low-degree relations. It is unchanged.

The candidate `lfdclose2_rref_export.c` changes only `export_cert`; closure
construction, column order, stopping condition, and certificate format are
copied from the pinned reference source. It applies the installed M4RI
full-row-reduction operation, checks that rank and the pivot-column set are
unchanged, and extracts coefficients at the original free columns.

For a fixed echelon matrix over F2 with pivot set P and free set Q, its full
RREF has rows e_p + sum(q in Q) a_pq e_q. Therefore the quotient image of e_p
is the coefficient vector a_p*, while each free monomial has its unit image.
The reference reverse substitution computes that same unique normal form
in the same ordered free basis. This gives the intended equality of the
certificate bytes. The independent checker remains required for actual
scientific outputs; the candidate producer is not a proof oracle.

Sources inspected: the reference `code/lfdclose2.c` in the original dossier,
SHA256 2413e3a3f34d0fdda8a53b0d62acff53aeaabc593b1c55fe42a3d7db8af3cc4f,
and the installed M4RI `brilliantrussian.h` documentation for the full flag
and top echelonization. The portable library hash is retained in
`runtime/rref-export-001/build.json`. This uses an existing row-reduction
operation and makes no algorithmic novelty or measured speed claim.

The prospective controls use seven fixed systems in two configurations:
rank zero, a multiword quotient with a partial final word, generic quadratic
relations, a constant-one rejection, and three retained Semaev fixtures.
Every completed candidate certificate must match the reference byte for
byte and pass the generic independent conditions; Semaev certificates also
pass the original standalone checker and retained hashes. Inputs, binaries,
checker and scripts are pinned in `rref-export-plan-001.json`. The protocol
must be frozen before execution. A 1 GiB child cap and 180-second stage
watchdog apply. No running instrument is replaced, and no scientific input
uses this candidate until the required controls and a separate freeze.

## Collection of the first panel result

The original n45 polynomial03 run uses a separately frozen protocol and bundle.
`collect_panel_result.py` accepts `--plan`, `--protocol`, and optional `--out`.
Without `--out` it only verifies existing terminal evidence. With `--out` it
writes a fresh collection directory and archives all closed files except the
main certificate, whose hash and original path remain recorded. Small control
certificates are included. It does not update the inventory or publish assets.

The collector requires a terminal wrapper receipt, the frozen request and
plan identity, matching worker metadata, hashed required evidence, the original
checker arguments and acceptance, fresh counter arguments/count, and passing
controls before recovering a bound. Other terminal outcomes retain no bound.
The validation record is `validation/panel-collector-001/result.json`: retained
polynomial02 passed47hashes; the live polynomial03 attempt and an omitted
count hash were rejected. No scientific trial was repeated for these checks.
