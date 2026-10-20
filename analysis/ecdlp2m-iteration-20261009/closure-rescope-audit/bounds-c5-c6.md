# Bounds for the two items marked "stop": rho-constant polishing (C5) and the Couveignes–Lercier route (C6)

Derived; not a decision.

## C5: how much can polishing the rho constant buy on ECC2K-130?

The program's reference is 2^60.81 (KR-RHO-18cc42 reports 2^60.9 from the
2009 ECC2K-130 paper). With r = 680564733841876926932320129493409985129 the
prime subgroup order (log2 r = 129.000), the ideal expected rho cost with the
negation map and the order-131 Frobenius is

    sqrt(pi * r / (2 * 2 * 131))  =  2^60.809   (this audit's arithmetic)

So the reference ALREADY assumes the ideal collision constant sqrt(pi/2) and a
perfect 262-fold equivalence-class reduction. What remains to polish is only
implementation overhead against that ideal:

| item | size | source |
|---|---|---|
| published estimate vs ideal | 2^60.9 vs 2^60.809 = 0.09 bit | KR-RHO-18cc42; arithmetic above |
| sqrt(pi/2) itself (cannot be removed by a better walk; it is the birthday constant) | 0.33 bit | arithmetic |
| fruitless-cycle and DP overheads in the published design | folded into the 0.09 bit | KR-RHO-18cc42 |

Reading: the realistic headroom from "polishing rho" is about 0.1 bit, and the
0.5-bit figure used in `../NEXT-STEPS.md` was already a generous upper bound.
No experiment is designed for C5. Revisit only if an index-calculus row comes
within 1 bit of rho, where a 0.1-bit rho improvement would move the verdict.

## C6: Couveignes–Lercier route at n = 131

`analysis/couveignes-lercier-131/census.json` (earlier session) records that
the dimension-1 torus construction needs 131 | q + 1 (false over F_2), and the
census of written constructions at n = 131 over F_2 finds no admissible object
in the small-dimension classes it enumerated. The primary source has not been
read in full in this program, so by the inventor protocol this is NOT a
closure. No experiment is designed; the next step is a source read, which is a
`/deep-research` or `/curate-knowledge` act, not a contract.
