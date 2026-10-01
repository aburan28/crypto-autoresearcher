| fault (on the scratch copy) | which instruments reach it | result on 120 candidates |
|---|---|---|
| **baseline (unfaulted)** | — | `M2 = (0, 0, 0)`, 0 errors |
| **F-a** `square()`: drop the top spread mask | I1, I2, I3 | **module will not load** — `KField.__init__`'s `assert is_irreducible(self.mod)` fails |
| **F-b** `polymod()`: stop one degree early | I1, I2, I3 | **non-terminating** — `KField(7)` never returns (observed, 60 s, exit 124) |
| **F-c** `clmul()`: drop the top set bit of the sparser operand | I1, I2, I3 | **87 of 120 counts changed; `M2 = (75, 73, 43)` — AGREEMENT BREAKS** |
| **F-d** `gcd()`: "swap one step early" | I2, I3 (not I1) | 0 changed, `M2 = (0,0,0)` — **this is not a fault**: the rewrite is semantically identical to the original Euclid. Retained as the NEGATIVE CONTROL. |
| **F-e** `polymod_sparse_tail()`: corrupt the tail | **I2 only** | 92 changed; `M2 = (92, 0, 92)` — **I2 disagrees with both, I1 and I3 still agree: the matrix LOCALISES the fault** |
| **F-f** `frob_power_mod()`: seed `X+1` instead of `X` | **I3 only** | **non-terminating within 300 s** (`_edf`'s splitting loop never succeeds) |
| **F-g** `_frob_table()`: one Frobenius too few | **I1 only** | 17 changed; `M2 = (17, 17, 0)` — **I1 disagrees with both, I2 and I3 still agree** |
| **G-a** `square()`: corrupt only when `deg > 40` (invisible to the `n <= 13` field-polynomial check) | I1, I2, I3 | **crash** — `ddf_factor`'s `assert deg(rest) <= 0` fails: *"unfactored remainder of degree 2"* |
| **G-b** `polymod()`: corrupt only when `deg m > 40` | I1, I2, I3 | **crash** — same assert, same message |
| **G-d** `gcd()`: corrupt only when both operands have `deg > 60` | I2, I3 (not I1) | **crash** — same assert, same message |
