# Operational corrections

2026-10-29 UTC: the frozen protocols and committed sources preceded the replay
and panel launch, but the repository's separate S3 resume-checkpoint gate was
missed. The sparse checkout did not contain `scripts/checkpoint.sh`. It was
materialized and a complete `.resume/RESUME.md` written while the original
processes remained active. The later checkpoint must not be described as a
pre-run checkpoint. Active owners and completed records were preserved.

The panel driver was invoked with source commit `fdd9cb0b73`. Its full object
identity is `fdd9cb0b730b3f18ab64d745bd32aa57e4cd1103`; this clarification does
not rewrite existing result records. The frozen instrument commit points to
the unchanged historical closure producer. Driver and native counter source
hashes are independently pinned in the panel protocol.

The generic unified-export validator expects a rectangular arm-by-instance
design. Here the reference is a correctness check within each pipeline, and
the panel has an extra degree-five request for only 50 inputs. Until a faithful
mapping is validated, progress snapshots use `semaev.data-progress/v1` and are
not advertised as validated `experiment.export/v1` bundles. No reference run
or pending result is fabricated to satisfy a validator.
