# Symbol-collision audit statement

Required artifact per specification.yaml required_artifacts item 8 and
`controls` (SYMBOL-COLLISION CONTROL).

This run's code (`compute.py`), its raw output (`raw-result.json`), and every
prose artifact in this run directory use `k_simon` and `k_mlkem` as distinct,
never-conflated names:

- `k_simon`: Simon's own internal group/repetition parameter (his own stated
  condition `k_simon > c`; the `k` in `Q = k * n^(c+1)`, as HIS formula names
  it in `inputs/DCP-SIMON-2026/paper_extracted_text.txt` and
  `ledger/hypotheses/H-MLKEM-36f511.yaml`).
- `k_mlkem`: ML-KEM's module rank, `k_mlkem in {2, 3, 4}` for
  ML-KEM-512/768/1024 respectively (FIPS 203).

**One disclosed, contract-specified substitution, not a collision:**
specification.yaml's own `preregistered_prediction.formula` clause (i) writes
the Q formula as "Q = k_mlkem * (k_mlkem*256)^(c+1)" -- i.e. the frozen
contract itself substitutes the numeral `k_mlkem` into the `k` slot of
Simon's `Q = k_simon * n^(c+1)` formula (alongside substituting `n :=
k_mlkem*256`). This run reproduces that substitution exactly as the frozen
contract states it (see `compute.py`'s `q_table()` docstring, which flags the
substitution explicitly at the point it occurs) and does not introduce any
additional, undisclosed conflation. No value of `k_simon` is invented,
assumed, or solved for anywhere in this run; `k_simon` appears only in this
audit note and in `compute.py`'s comments identifying which formula slot
belongs to which paper's notation.

**Audit result: PASS.** No artifact in this run directory uses a bare `k` for
both quantities, and every place the contract's own `k_mlkem`-for-`k_simon`
substitution is used, it is named and cross-referenced to
specification.yaml's own text rather than presented as an independent
result.
