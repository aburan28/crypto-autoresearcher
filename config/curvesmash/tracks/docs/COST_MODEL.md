# Computation accounting

The score is the submitted **log2(total computation in target-group-operation equivalents)**. Lower is better. Explain the complete calculation in `proof.md`; no cost-ledger file, integer-budget field or intermediate pricing engine is required.

This follows [HashSmash's reference normalization](https://github.com/Layr-Labs/hash-smash/blob/main/docs/RESCORING.md): one reference target operation costs 1, and other computation costs R/C. Here R is work in scalar AArch64 instruction equivalents, including arithmetic, loads/stores, addressing and control. Larger arithmetic must be accounted for through its implementation. Analytical instruction-equivalent bounds are sufficient; participants do not need to supply assembly or execute a full-size attack.

| Target | Reference operation | Fixed C |
| --- | --- | ---: |
| P-256 DLOG | Borrowed secp256k1 reference unit; actual P-256 arithmetic charged in instructions | **1,000** |
| BLS12-381 ordinary G1 DLOG | Existing BLS G1 addition reference | **2,000** |
| BLS12-381 fixed-G2 pairing inversion into G1 | Dense Fp12 multiplication in blst | **20,000** |
| secp256k1 DLOG | Batched incomplete affine addition, using the 6M convention below | **1,000** |
| BLS12-381 G1 DLOG | Batched incomplete affine G1 addition, using the 6M convention below | **2,000** |
| BLS12-381 fixed-G1 pairing inversion into G2 | Dense Fp12 multiplication in blst | **20,000** |

These are rounded normalization constants grounded in instruction counts, not CPU cycles or claims of the fastest possible attack. Count other work on the same scalar 64-bit instruction basis, not as arbitrary-width unit-cost arithmetic. The constants are fixed by the organizer and cannot be changed by a submission. Faster arithmetic and lookup algorithms are welcome; justify their actual work. Scores from different tracks are not directly comparable.

## Where C comes from

The measurements use GCC 14.2.0 on Linux/AArch64, with `-O3 -fno-tree-vectorize -mgeneral-regs-only`, and Valgrind Callgrind 3.24.0's instruction event `Ir`. blst uses its upstream AArch64 assembly; its C also uses `-fno-builtin -fPIC`. This counts executed instructions, including call and loop work, rather than measuring elapsed time.

- **secp256k1:** Bitcoin Core's [5x52 field multiplication](https://github.com/bitcoin-core/secp256k1/blob/e74a0187aac1cac734d5ad23ca5e40ceb6ddd4a8/src/field_5x52_int128_impl.h), commit `e74a0187aac1cac734d5ad23ca5e40ceb6ddd4a8`, measures **179 instructions per multiplication**. The batched incomplete affine reference uses **6M**: 3M for the addition formula and 3M for batch amortisation, with S=M and A=0. The measured six-multiplication calibration is **6 × 179 = 1,074**, rounded to **C = 1,000**. There is no standalone inversion charged per addition. This is a six-multiplication normalization, not a measurement of a complete point-addition routine. The A=0 convention is for this reference formula; unrelated computation in an attack still counts.
- **BLS12-381 GT:** [blst_fp12_mul](https://github.com/supranational/blst/blob/f7a88067ed98385ebc6cf41ccecf21ead706a5b7/src/fp12_tower.c), commit `f7a88067ed98385ebc6cf41ccecf21ead706a5b7`, measures **22,996 instructions per dense multiplication**, rounded to **C = 20,000**. It operates in the tower Fp2/Fp6/Fp12 representation, with reduction and its internal additions and memory work included. The benchmark multiplies actual GT elements; setup and subgroup checking are outside the counted region.

**BLS12-381 G1:** the same pinned blst build measures **383 instructions** per `blst_fp_mul`. Its 6M calibration is **2,298**, approximately one tenth of the dense Fp12 cost. The G1 price is therefore **C = 2,000**, consistent with the rounded Fp12 price of 20,000. The 6M convention again amortises the batch work and has no standalone per-addition inversion term.

Each kernel was counted at 4,096 and 8,192 iterations. Dividing the difference in instruction totals by 4,096 removes fixed profiling/setup overhead while retaining per-iteration work:

| Kernel | Ir at 4,096 iterations | Ir at 8,192 iterations | Difference / 4,096 |
| --- | ---: | ---: | ---: |
| secp256k1 field multiply | 733,204 | 1,466,388 | **179** |
| blst dense Fp12 multiply | 94,191,636 | 188,383,252 | **22,996** |
| blst base-field multiply | 1,568,788 | 3,137,556 | **383** |

The [measurement record](../../scripts/reference_costs/measurement.json) pins the source commits, toolchain, raw totals, harness hashes and measured binary hashes. The [harness](../../scripts/reference_costs/) contains the programs used. To read the derived prices, run `python3 scripts/reference_operation_costs.py`. To rebuild the pinned sources and repeat the counts with Docker, run `bash scripts/reference_costs/reproduce.sh`. The latter checks fresh totals against the record and retains raw profiles. A changed compiler can change instruction counts; the fixed published prices do not update automatically.

## Complete attack work

Charge total work across processors, including preprocessing, advice construction, random sampling, all trials and failures, sorting, lookup, memory transfers, verification, output and success amplification. A stored answer does not make its search free. Do not charge both a reference operation and its internal instructions. Public profile constants and algorithm design effort are excluded.

For H reference operations and R other reference-instruction equivalents, the cost is **H + R/C**, with all work included exactly once. Submit its base-2 logarithm and justify the calculation. Sieving, smoothness testing, linear algebra and descent count through their computation; they do not need to use field multiplication.

For each BLS track with auxiliary powers, express the complete cost as **W(n) = H(n) + R(n)/C** and submit **time_log2 = log2(W(2^20))**. State the range of n and any conditions under which the bound holds; it must apply at the scoring value n=2^20. The supplied powers are public challenge inputs, so their generation is excluded, while all accesses and processing by the attack count. The attack may use only a subset of the powers.

The required success probability is at least 0.39 over uniform production challenges and fresh algorithm coins. Peak memory includes code, advice, tables and scratch. Report memory, preprocessing and advice alongside the computation bound; memory has no scalar contribution or tie-break. Quantum algorithms are outside this classical benchmark.

A supported cost discrepancy must be considered by the reviewer together with the strongest evidence-based response. A surviving fatal discrepancy prevents acceptance. Material uncertainty remains visible in the review reason under the exploratory policy. There is no separate defense/adjudication stage. An accepted submission receives its submitted bound; ordinary judging does not silently optimize it. Changed rules or prices require a newly justified claim and [fresh review](RESCORING.md), not automatic reuse of an earlier score.

The fixed-argument track `bls12-381-fixed-g1-invert-g2` has no powers input or n parameter. Its score is log2(W), using the same dense Fp12 reference price C=20,000.

The ordinary BLS G1 DLOG and both fixed-argument pairing tracks have no n
parameter and reuse the existing G1 and Fp12 calibrations respectively.
P-256 borrows C=1,000 from the secp256k1 reference as a normalization unit,
not a measured P-256 kernel price. Its actual arithmetic, including point
additions, must be charged through justified instruction counts divided by C.
The measurement record remains unchanged; no new hardware measurements or
qualified attack scores are claimed. For these tracks the score is log2(W).
