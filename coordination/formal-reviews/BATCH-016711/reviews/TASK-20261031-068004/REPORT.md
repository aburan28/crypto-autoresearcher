# J3 blind finite Boolean re-derivation

## Input custody and method

I used only the isolated six-file bundle. `git bundle verify` reported a complete bundle with `main` and `HEAD` at `e0bd0ab45882cd65a3de481b45c15ad5447ea844`; its SHA-256 is `953d984272eb185b681b05361a50549adaa96c649f12a393411a785eb08eaf7e`. The cloned snapshot HEAD is the same commit. No producer source, prior output, PR, or sibling review was opened.

The checker evaluates the stated field formula for all 256 assignments, then applies the Boolean Möbius transform independently to each output bit. It verifies that every transformed ANF evaluates back to the original truth table. For each component and multiplier mask 0..255 it forms the squarefree product using union of masks and XOR, retains rows with maximum degree at most D, and uses binary Gaussian elimination on 256-bit coefficient vectors. The raw JSON contains every retained row, its support and coefficient-vector hex value.

## Derived ANFs

Each integer is an eight-bit squarefree monomial mask; bits 0..3 select the stated basis for `x1`, bits 4..7 for `x2`. The four lists are low field-coordinate bit first.

| Component | ANF monomial masks |
| --- | --- |
| 0 | 0, 1, 2, 8, 16, 17, 24, 32, 34, 36, 40, 66, 68, 128, 129, 130, 136 |
| 1 | 8, 17, 34, 68, 72, 128, 132 |
| 2 | 1, 2, 4, 8, 16, 18, 32, 33, 34, 64, 68, 128, 136 |
| 3 | 1, 8, 16, 128 |

## Compatible spaces and new class

| D | Compatible row counts by component | Total rows | Row-space rank |
| --- | --- | ---: | ---: |
| 2 | 1, 1, 1, 25 | 28 | 11 |
| 3 | 9, 9, 9, 53 | 80 | 53 |

For the D=3 rows, projection onto monomials of degree greater than two has rank 41. Its kernel within the D=3 row space therefore has dimension `53 - 41 = 12`. The D=2 span has dimension 11 and is contained in that kernel. Thus exactly one independent degree-at-most-two class occurs outside the D=2 span.

The following D=3 compatible rows, XORed together, give an explicit representative. Each pair is `(component, multiplier mask)`:

```
(0,2) (0,4) (0,8) (0,32) (0,64) (0,128)
(1,1) (1,2) (1,8) (1,16) (1,32) (1,128)
(2,1) (2,2) (2,16) (2,32)
(3,3) (3,10) (3,20) (3,33) (3,34) (3,40) (3,65)
```

Its coefficient-1 support is:

```
1, 2, 4, 8, 9, 10, 12, 16, 18, 20, 32, 40, 48, 64, 65, 128, 144, 192
```

All these monomials have degree at most two. The functional `L(v) = coefficient(v,80) XOR coefficient(v,192)` has raw value **0 on every one of the 28 D=2 rows** (the 28 values are in `raw.json`) and **1 on the witness**: witness coefficients at masks 80 and 192 are respectively 0 and 1. It therefore separates the class from the D=2 span.

## Controls

* Duplicate-monomial parity: multiply component 0 by mask 1. Its input ANF terms at masks 0 and 1 both produce output mask 1. The multiplicity is two, and XOR gives coefficient 0 at mask 1. The checker applies this same parity rule to all products.
* Mutation: toggle ANF monomial mask 1 in component 0. Its ANF becomes `0, 2, 8, 16, 17, 24, 32, 34, 36, 40, 66, 68, 128, 129, 130, 136`. The compatible D=2 row count changes from 28 to 57 (component 0: 1 to 30), and D=3 from 80 to 109 (component 0: 9 to 38). The 29 new multiplier keys at each degree are in `raw.json`. Ranks remain 11 and 53; this control detects a component change through the derived row sets without asserting that every mutation changes rank.

## Scope and reproduction

This is a finite F2 row-space result for the exact stated F16 basis, fixed `xR=1`, and `a6=1`. Reproduce with `python3 check.py > raw.json` from this directory. The checker performs no Lean or Cargo build and launches no cloud job.
