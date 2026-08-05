# H-PSEUDO C(p) for Special Prime Classes
## TASK-20260804-140, BATCH-100

## Measurement: p ≡ 1 mod 4 vs p ≡ 3 mod 4 (bits~14)

| Class | p values | C values | mean C |
|-------|---------|----------|--------|
| p≡1 mod 4 | 14593,11273,14389,11257 | 3.58,3.96,3.71,3.62 | 3.719 |
| p≡3 mod 4 | 15427,8543,13967,10267 | 3.98,3.81,3.52,3.65 | 3.742 |

**No systematic difference** between p≡1 mod 4 and p≡3 mod 4. C values are
essentially the same across both classes (both ~3.7 at bits~14).

## Interpretation

The residue class of p mod 4 has no measurable effect on C(p). This is consistent
with H-PSEUDO being a property of the GROUP STRUCTURE (Z/N, prime cyclic) rather than
the specific arithmetic of p. The factor base small-x indicator has the same Fourier
flatness regardless of whether p≡1 or 3 mod 4.

## CM prime analysis (theoretical)

For CM primes p where p = (t²-D)/4 with |D| ≤ 20 and h(D)=1:
- The curve E/F_p has CM by O_K with discriminant D
- The CM endomorphism of E is available over F_p (or F_{p²})
- For |D| = 3 (j=0): the CM endomorphism is the cube root of unity (GLV)
- For |D| = 4 (j=1728): the CM is the square root of -1 (Frobenius twist)

For these CM curves: the H-PSEUDO character sum might be smaller because the DL
values {DL(P): P ∈ F} have structure related to the CM endomorphism.

However: BATCH-074 showed C≈3 even at p=1009 with random curves, and CM curves
(j=0, 1728 etc.) are excluded from cryptographic use. The CM case is the ONLY case
where H-PSEUDO might be easier to prove (via Hecke characters, as noted in BATCH-087).

## Conclusion

No special prime class shows systematically lower C(p) at bits~14. C≈3.7 uniformly
across p≡1 and p≡3 mod 4. The CM case (small discriminant) is theoretically special
but cryptographically excluded. No new avenue for H-PSEUDO proof identified here.
