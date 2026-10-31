# Signed Frobenius and exact two-predicate fits

This round finds a complete **retrospective separator** on all 21 curves.
At auxiliary prime 199, retain a curve when its known-degree eigenvalue
candidate-list size is at most 32 and the minimum predicted irreducible
factor degree of its 199-division polynomial is at most 2048. All ten
publications pass; all eleven reconstructed omissions fail.

Those constants and the mandatory 199 test have no established historical
source. The general resource-policy interpretation fails: uniform caps through
199 reject every publication, and unknown splitting-degree mode at 199 loses
four publications. The later measured counter stopped before 199 on all eleven
omissions. [Exact native log bindings](COUNTER-TRACE-BINDING.json) verify each
log hash, model, returned order and reported working-prime markers.

Read the [four-page report](report.pdf), [report source](report.md),
[all 21 observations at 199](ell199.csv), [every fitting pair and alias](ALL-FITS.json),
[source qualifications](SOURCE-QUALIFICATION.md) and [frozen plan](PLAN.md).
All 16 fitting pairs and 19 truth tables are retained; none is promoted to the
historical selector. The original problem and goal remain open.

Both independent methods agree on all 1,281 signed-action profiles and source
candidate-list metrics. The extended search covers 3,130,260 new signature
pairs and 50,084,160 Boolean-function cases. Old-old pairs reuse the prior
independently checked zero-fit census. Every nonfit collision witness is sealed.

The P-224 publication has Frobenius `-I` on 3-torsion, so its quadratic twist
has full rational 3-torsion. The three P-224 omissions have Jordan action.
This gives a concrete meaning of the earlier cube/splitting observation on this
cohort without establishing a universal equivalence or historical requirement.

With Python and `python-flint==0.9.0`, and GP at `/opt/homebrew/bin/gp`, replay
from a fresh extraction:

```sh
zstd -dc evidence.tar.zst | tar -xf -
python3 -B evidence/run.py
python3 -B evidence/policy-check-01/policy.py
```

For shorter relocation validation, run `verify_archive.py /fresh/output/path`.
It verifies every sealed file, replays both arithmetic methods, the entire
bitset search and the policy checks, then matches the original complete
rowwise results and witnesses. It does not repeat rowwise enumeration.
[PORTABLE-REPLAY.json](PORTABLE-REPLAY.json) records the exact scope.

The archive contains 54 sealed files, including both exports and their passing
file checks. Original third-party source-package/PDF bytes and binaries are
excluded; source references and hashes are retained. Canonical artifact delivery
returned HeadObject403. The exact archive remains in Git under PR2602's existing
`large-file-ok` exception. Existing immutable-record merge conflicts remain
separate from the arithmetic and classifier results.
