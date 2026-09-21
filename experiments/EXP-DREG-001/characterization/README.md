# EXP-DREG-001 — deficit characterization probes

Analysis-side probes for §10–§11 of `../analysis.md`. These are **not** the
instrument: they do not produce new run receipts and they change nothing in the
measurement path. They re-derive, by exact GF(2) linear algebra, *where* the rank
deficit lives and *what* the responsible syzygies are.

All four import the construction from the per-run archived code snapshot
`../runs/RUN-DREG-001-VALIDATE-N12-A/code/` (`semaev_tree.py`, `h012_peel_rank.py`,
`macaulay_export.py`, `ic_first_fall_fast.py`). That snapshot — not the workspace
`src/` — is authoritative after the 2026-07-20 workspace relocation; it is pinned by
sha256 in the run manifest.

## Running

The system volume runs near-full, so keep Sage's caches and temporaries on the
external volume:

```
cd <workspace root>
export DOT_SAGE=$PWD/experiments/EXP-DREG-001/runtime/sage
export TMPDIR=/Volumes/Volume/tmp
sage -python experiments/EXP-DREG-001/characterization/<probe>.py [--n-list ...]
```

All cells below are cheap (seconds to ~20 s). Nothing here needs the block-m4ri
instrument or a budget.

| probe | what it establishes | cost |
|---|---|---|
| `deficit_by_degree.py` | §10 table: graded deficit per degree; checks def3 = 1 and def4 = 8k−1 | <10 s to n=21 |
| `syzygy_degree3.py` | extracts the single degree-3 syzygy, proves it is an affine degeneration; null control | <5 s |
| `syzygy_degree4.py` | isolates generic (Frobenius+Koszul) vs extra syzygies; confirms deficit = 8·dim V | ~20 s at n=18 |
| `alpha_action_test.py` | **negative result**: the naive α-action is not the symmetry | ~30 s |

## Verified outputs (2026-07-20, seed 2026, t=3, ti=0)

`deficit_by_degree.py --n-list 9,12,15,17,18,21 --dmax 4`

| n | k | shape | def(D=3) | def(D=4) | 8k−1 |
|---|---|---|---|---|---|
| 9 | 3 | deficient (8 quadrics, not 9) | 0 | 23 | 23 |
| 12 | 4 | full | 1 | 31 | 31 |
| 15 | 5 | full | 1 | 39 | 39 |
| 17 | 6 | deficient (nb = 2n+1, 34 eqs) | 1 | 45 | — |
| 18 | 6 | full | 1 | 47 | 47 |
| 21 | 7 | full | 1 | 55 | 55 |

`syzygy_degree4.py --n-list 12,15,18` — rank(G) = nrows − pred[4] exactly
(78 / 120 / 171), G ⊆ left kernel, extra syzygies = 32 / 40 / 48 = 8k.

`syzygy_degree3.py --n-list 12,15,18` — null kernel 0 at every n; sem kernel 1;
shared multiplier set; **Q·L = 0 verified directly**; Q affine and L = 1 + Q at
every n, so the relation is the Boolean identity P(1+P) = 0 on a derived affine
form P (e.g. P = z18, the sum of 7 quadrics, at n=18).

## Scope and caveats

- The degree-4 generic/extra isolation is valid only for **full** systems
  (exactly n quadrics + n cubics in nb = 2n variables). n=9 and n=17 are deficient
  and are precisely the cells that break the closed forms; `--n-list` accepts them
  but the scripts label the shape and suppress the closed-form check.
- `def4 = 8k−1` holds at n=9 too, but `cumulative(D=4) = 8k` does **not** there,
  because n=9 has no degree-3 relation (def3 = 0). The cumulative identity assumes
  the full quadric count.
- Supports (which quadrics, which variables) are coordinate-dependent — they change
  with n and the random decomposable R. Only the **counts** are invariant. Do not
  read the specific index sets as structural.
- `alpha_action_test.py` records a refuted hypothesis and is kept deliberately: it
  rules out the simplest α-action and documents *why* (the operator fails even on
  the universal generic space, so it is incomplete rather than the symmetry being
  absent).
