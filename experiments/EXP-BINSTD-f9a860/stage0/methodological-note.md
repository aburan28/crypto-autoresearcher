# Methodological note — EXP-BINSTD-f9a860 Stages 0–3

Experiment: `EXP-BINSTD-f9a860` · Hypothesis: `H-BINSTD-0514c3` ·
Task: `TASK-20261001-af8338` · Approval: `DEC-20261001-8570c3`

## What this experiment is

Tooling / transcription / synthetic-mutation battery only. It creates a
per-cell write-once reachability layout, seeds only independently re-derived
cells, implements validator live checks, and runs a six-case scratch-copy
battery. It does **not** claim a break, any curve's attack cost, or any
exponent movement.

## HOLD-F corrections absorbed

From `analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-6028ed.yaml`
(verdict `sound_with_corrections`):

1. **Per-cell shards** under
   `analysis/binstd-curve-audit/reachability/<curve>/<column>.yaml`,
   write-once with `superseded_by`. No shared mutable ~180-cell YAML.
2. **Extended schema**: `unit`, `m`, `floor_bits`, `budget_bits`,
   `rho_convention`, `provenance_tier`.
3. **ECC2K-130 hand-seed** from `KN-LIT-661e97` (absent from OpenSSL dump):
   field degree 131, cofactor `h=4`, prime-order subgroup on the 129-bit
   prime `l` recovered from the Weil recursion with `t=-1`.
4. **Seed only re-derived cells** at `provenance_tier: proposal_arithmetic`.
   Do **not** seed COMPUTED cells from unrepaired `IDEA-20260922-77bf31`
   g/B prose.

## Rho convention

`matched_rho` cells pin `rho_convention: CORR-20260922-81aeab`:
`0.886 sqrt(r)/sqrt(k) = sqrt(pi r / (4k))`. Negation is already inside the
`0.886` constant; the Frobenius class map of order `k` contributes `sqrt(k)`,
not `sqrt(2k)`.

## Generated view

Path: `analysis/binstd-curve-audit/reachability_table.generated.yaml`.
Gitignored; rebuilt by `tools/validate_reachability_table.py --emit-view`.
Committing it is a hard fail of H1.

## Certificate vocabulary (run manifests)

Per `docs/claims-and-verification.md`, run manifests for this experiment use
only `certificate.kind: none`. No discrete-log / decomposition / key-recovery
claim is made by any Stage 0–3 run.

## CI

Stage 4 CI wire-up is **out of scope** of this experiment's authorized stages.
No `.github/workflows` edits.

## Seed-grid choice

Prefer **ABSENT** (= not yet assessed) over inventing ~175 empty
`NOT_YET_ASSESSED` files. Only re-derived cells are written as shards.
Documented in `stage1/seed-policy.yaml`.

## No-break / no-attack-cost

No artifact of this experiment asserts a cryptanalytic break or a concrete
attack cost for any deployed curve. Seeded `floor_bits` / `matched_rho` bits
are transcribed re-derived arithmetic for schema/validator exercise only.
